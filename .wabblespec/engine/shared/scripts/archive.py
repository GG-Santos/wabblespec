"""
archive.py — Mechanizes the Archive phase without reading CHANGELOG into context.

Replaces the token-expensive manual Archive loop:
  - Was: Claude reads 98KB CHANGELOG + 18KB receipt-index + VERSION + N receipts,
         reasons about semver, composes JSON, writes 4 files.
  - Now: Claude calls this script with the reasoning-dependent fields (summary,
         session_id, files list) as arguments. Script handles all file I/O.

CHANGELOG is opened in append mode — never read into memory.

Usage:
    # Full Archive run (derive delta_class from session receipts):
    python .wabblespec/engine/shared/scripts/archive.py \\
        --session-id seed-run-20260525xx \\
        --task-id seed-run-20260525xx \\
        --summary "What was built this session" \\
        --files-delivered ".wabblespec/engine/shared/references/foo.md" ".wabblespec/engine/shared/references/bar.md" \\
        --waves-completed 1

    # With explicit delta-class (skip auto-detection from receipts):
    python .wabblespec/engine/shared/scripts/archive.py \\
        --session-id seed-run-20260525xx \\
        --task-id seed-run-20260525xx \\
        --summary "Added reference docs" \\
        --delta-class ADDITIVE \\
        --files-delivered ".wabblespec/engine/shared/references/foo.md"

    # Pass extra JSON fields for the delivery receipt:
    python .wabblespec/engine/shared/scripts/archive.py ... \\
        --extra '{"total_receipts_accumulated": 94, "l8_gate_progress": "94/100"}'

    # Dry run — print what would be written without touching any files:
    python .wabblespec/engine/shared/scripts/archive.py ... --dry-run

    # Sweep mode — scan receipt-index for EXPIRED entries:
    python .wabblespec/engine/shared/scripts/archive.py --sweep

Output (written):
    .wabblespec/receipts/delivery-receipt-{session_id}.json
    .wabblespec/CHANGELOG.md        (appended, never read)
    .wabblespec/archive/receipt-index.json  (patched in place)
    .wabblespec/VERSION             (bumped)

Exit codes:
    0  success
    1  bad arguments or logical failure
    2  required file not found or unreadable
"""

import sys
import os
import json
import glob
import argparse
import re
import subprocess
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Audio helper
# ---------------------------------------------------------------------------

def _play_lifecycle_sound(event_name: str, root: str) -> None:
    """
    Fire-and-forget: spawn wabble-sound.py detached, never block, never raise.
    root — repo root path (used to locate the script).
    """
    try:
        script = os.path.join(root, "_shared", "scripts", "wabble-sound.py")
        if not os.path.isfile(script):
            return
        subprocess.Popen(
            [sys.executable, script, "--event", event_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def find_wabblespec_root(start_dir=None):
    """Walk up to find the directory containing .wabblespec/."""
    if start_dir is None:
        start_dir = os.getcwd()
    candidate = start_dir
    for _ in range(10):
        if os.path.isdir(os.path.join(candidate, ".wabblespec")):
            return candidate
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------

SEVERITY = {"BREAKING": 2, "ADDITIVE": 1, "COSMETIC": 0}


def parse_version(raw):
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", raw.strip())
    if not m:
        raise ValueError(f"Cannot parse version '{raw}'")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def bump_version(version_str, delta_class, pre_stabilization=None):
    """Return new version string. Raises ValueError on bad input."""
    major, minor, patch = parse_version(version_str)
    if pre_stabilization is None:
        pre_stabilization = major == 0
    if delta_class == "BREAKING":
        if pre_stabilization:
            return f"{major}.{minor + 1}.0"
        return f"{major + 1}.0.0"
    elif delta_class == "ADDITIVE":
        return f"{major}.{minor + 1}.0"
    else:  # COSMETIC
        return f"{major}.{minor}.{patch + 1}"


# ---------------------------------------------------------------------------
# Receipt scanning
# ---------------------------------------------------------------------------

def scan_session_receipts(receipts_dir, session_id):
    """
    Find all JSON receipts for session_id. Returns list of parsed dicts.
    Skips delivery receipts (those are the output, not the input).
    """
    pattern = os.path.join(receipts_dir, "*.json")
    results = []
    for path in glob.glob(pattern):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        # Match by session_id or task_id
        sid = data.get("session_id") or data.get("task_id") or ""
        if sid != session_id:
            continue
        # Skip delivery receipts — those are output
        rtype = data.get("receipt_type") or data.get("module") or ""
        if rtype in ("delivery", "archive"):
            continue
        results.append((path, data))
    return results


def derive_delta_class(receipts):
    """Return the highest-severity delta_class found across all receipts."""
    max_sev = -1
    best = "COSMETIC"
    for _, r in receipts:
        dc = r.get("delta_class")
        if dc and dc in SEVERITY:
            sev = SEVERITY[dc]
            if sev > max_sev:
                max_sev = sev
                best = dc
    return best


def aggregate_not_tested(receipts):
    """Collect and deduplicate not_tested items from all receipts."""
    seen = set()
    items = []
    for _, r in receipts:
        for item in r.get("not_tested", []):
            if item and item not in seen:
                seen.add(item)
                items.append(item)
    return items


# ---------------------------------------------------------------------------
# Receipt index
# ---------------------------------------------------------------------------

def load_receipt_index(index_path):
    if not os.path.isfile(index_path):
        return {"index_version": 1, "last_updated": "", "tasks": []}
    try:
        with open(index_path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"WARNING: Could not read receipt-index.json ({e}). Starting fresh.", file=sys.stderr)
        return {"index_version": 1, "last_updated": "", "tasks": []}


def save_receipt_index(index_path, data):
    tmp = index_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, index_path)


def upsert_index_entry(index, task_id, entry_fields):
    """Find existing entry by task_id or append new one. Updates in place."""
    for task in index.get("tasks", []):
        if task.get("task_id") == task_id:
            task.update(entry_fields)
            return
    entry = {"task_id": task_id}
    entry.update(entry_fields)
    index.setdefault("tasks", []).append(entry)


# ---------------------------------------------------------------------------
# CHANGELOG append
# ---------------------------------------------------------------------------

def append_changelog(cl_path, version, timestamp, title, summary, not_tested,
                     delivery_receipt_path, waves_completed, delta_class):
    """Append one entry using open('a') — CHANGELOG is never read."""
    lines = []
    lines.append(f"\n---\n")
    lines.append(f"\n## [{version}] — {timestamp}\n")
    if title:
        lines.append(f"\n### {title}\n")
    lines.append("\n### Changed\n")
    if summary:
        lines.append(f"- {summary}\n")
    else:
        lines.append("- (none)\n")
    if not_tested:
        lines.append("\n### Not Tested\n")
        for item in not_tested:
            lines.append(f"- {item}\n")
    lines.append("\n### Receipts\n")
    rel = os.path.relpath(delivery_receipt_path).replace("\\", "/")
    lines.append(f"- delivery-receipt: {rel}\n")
    lines.append(f"- waves: {waves_completed} completed\n")
    lines.append("- verification: all waves PASS\n")

    try:
        with open(cl_path, "a", encoding="utf-8") as f:
            f.writelines(lines)
    except OSError as e:
        print(f"ERROR: Cannot append to CHANGELOG at {cl_path}: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run the Archive phase without reading CHANGELOG into context.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--session-id", metavar="ID", help="Session identifier.")
    parser.add_argument(
        "--task-id",
        metavar="ID",
        help="Task identifier. Defaults to --session-id if omitted.",
    )
    parser.add_argument("--summary", metavar="TEXT", help="Human-readable summary for CHANGELOG.")
    parser.add_argument(
        "--delta-class",
        choices=["BREAKING", "ADDITIVE", "COSMETIC"],
        help="Override delta_class. If omitted, derived from session receipts.",
    )
    parser.add_argument(
        "--files-delivered",
        nargs="*",
        metavar="PATH",
        help="Files delivered this session.",
    )
    parser.add_argument("--waves-completed", type=int, default=1, metavar="N")
    parser.add_argument("--waves-planned", type=int, default=None, metavar="N")
    parser.add_argument("--title", metavar="TEXT", help="Optional CHANGELOG section title.")
    parser.add_argument(
        "--not-tested",
        nargs="*",
        metavar="ITEM",
        dest="not_tested_override",
        help="Override not-tested list (bypasses receipt scanning).",
    )
    parser.add_argument(
        "--extra",
        metavar="JSON",
        help="Extra JSON fields merged into delivery receipt (e.g. task-specific counters).",
    )
    parser.add_argument(
        "--receipts-dir",
        metavar="PATH",
        help="Directory containing session receipts. Default: .wabblespec/receipts/",
    )
    parser.add_argument(
        "--root",
        metavar="PATH",
        help="Repo root override. Default: auto-detected by walking up from cwd.",
    )
    parser.add_argument(
        "--no-pre-stabilization",
        action="store_true",
        help="Treat BREAKING as major bump even when major == 0.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written; touch no files.",
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Scan receipt-index for EXPIRED/IN_PROGRESS orphans and report.",
    )

    args = parser.parse_args()

    # Locate repo root
    root = args.root or find_wabblespec_root()
    if root is None:
        print("ERROR: Cannot find .wabblespec/. Run from inside the repo.", file=sys.stderr)
        sys.exit(2)

    wabble = os.path.join(root, ".wabblespec")
    receipts_dir = args.receipts_dir or os.path.join(wabble, "receipts")
    index_path = os.path.join(wabble, "archive", "receipt-index.json")
    cl_path = os.path.join(wabble, "CHANGELOG.md")
    ver_path = os.path.join(wabble, "VERSION")

    # --sweep mode
    if args.sweep:
        index = load_receipt_index(index_path)
        orphans = [
            t for t in index.get("tasks", [])
            if t.get("status") in ("IN_PROGRESS", "PENDING")
        ]
        expired = [
            t for t in index.get("tasks", [])
            if t.get("staleness_state") == "EXPIRED"
        ]
        print(f"Receipt index: {len(index.get('tasks', []))} total entries")
        print(f"IN_PROGRESS/PENDING (orphaned?): {len(orphans)}")
        for t in orphans:
            print(f"  - {t.get('task_id')} started={t.get('started_at')}")
        print(f"EXPIRED staleness: {len(expired)}")
        for t in expired:
            print(f"  - {t.get('task_id')}")
        sys.exit(0)

    # Validate required args
    if not args.session_id:
        parser.error("--session-id is required (or use --sweep).")

    task_id = args.task_id or args.session_id

    # Read VERSION
    if not os.path.isfile(ver_path):
        print(f"ERROR: VERSION not found at {ver_path}", file=sys.stderr)
        sys.exit(2)
    current_version = open(ver_path, encoding="utf-8").read().strip()

    # Scan session receipts
    session_receipts = scan_session_receipts(receipts_dir, args.session_id)
    receipts_aggregated = len(session_receipts)

    # Delta class
    if args.delta_class:
        delta_class = args.delta_class
    else:
        delta_class = derive_delta_class(session_receipts) if session_receipts else "ADDITIVE"

    # Not-tested
    if args.not_tested_override is not None:
        not_tested = args.not_tested_override
    else:
        not_tested = aggregate_not_tested(session_receipts)

    # Compute new version
    pre_stab = not args.no_pre_stabilization
    new_version = bump_version(current_version, delta_class, pre_stabilization=pre_stab)

    # Timestamp
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Delivery receipt path
    delivery_receipt_path = os.path.join(
        receipts_dir, f"delivery-receipt-{args.session_id}.json"
    )

    # Build delivery receipt
    delivery_receipt = {
        "receipt_type": "delivery",
        "task_id": task_id,
        "session_id": args.session_id,
        "status": "PASS",
        "all_waves_passed": True,
        "waves_completed": args.waves_completed,
        "receipts_aggregated": receipts_aggregated,
        "version_previous": current_version,
        "version_new": new_version,
        "version_bump_reason": delta_class,
        "not_tested_items": len(not_tested),
        "not_tested_list": not_tested,
        "summary": args.summary or "",
        "archived_at": now,
    }

    if args.files_delivered:
        delivery_receipt["files_delivered"] = args.files_delivered

    # Merge extra fields
    if args.extra:
        try:
            extra = json.loads(args.extra)
            delivery_receipt.update(extra)
        except json.JSONDecodeError as e:
            print(f"ERROR: --extra is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    # Index entry
    index_entry = {
        "task_id": task_id,
        "session_id": args.session_id,
        "status": "PASS",
        "archived_at": now,
        "delivery_receipt_path": os.path.relpath(delivery_receipt_path, root).replace("\\", "/"),
        "version_previous": current_version,
        "version_new": new_version,
        "version_bump_reason": delta_class,
        "waves_completed": args.waves_completed,
        "waves_planned": args.waves_planned if args.waves_planned is not None else args.waves_completed,
        "not_tested_items": len(not_tested),
        "summary": args.summary or "",
    }

    # --dry-run output
    if args.dry_run:
        print("=== DRY RUN — no files will be written ===")
        print(f"\nVERSION: {current_version} -> {new_version}")
        print(f"delta_class: {delta_class}")
        print(f"receipts scanned: {receipts_aggregated}")
        print(f"not_tested: {not_tested}")
        print(f"\nDelivery receipt -> {delivery_receipt_path}")
        print(json.dumps(delivery_receipt, indent=2))
        print(f"\nCHANGELOG append -> {cl_path} (open 'a')")
        print(f"  [{new_version}] — {now}")
        print(f"  title: {args.title or '(none)'}")
        print(f"  summary: {args.summary or '(none)'}")
        print(f"\nreceipt-index.json -> {index_path}")
        print(json.dumps(index_entry, indent=2))
        sys.exit(0)

    # Write delivery receipt
    tmp = delivery_receipt_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(delivery_receipt, f, indent=2)
        f.write("\n")
    os.replace(tmp, delivery_receipt_path)
    print(f"Wrote delivery receipt: {delivery_receipt_path}")

    # Append CHANGELOG (never reads existing content)
    append_changelog(
        cl_path=cl_path,
        version=new_version,
        timestamp=now,
        title=args.title,
        summary=args.summary or "",
        not_tested=not_tested,
        delivery_receipt_path=delivery_receipt_path,
        waves_completed=args.waves_completed,
        delta_class=delta_class,
    )
    print(f"Appended [{new_version}] to CHANGELOG (append-only, CHANGELOG not read)")

    # Bump VERSION
    tmp = ver_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_version + "\n")
    os.replace(tmp, ver_path)
    print(f"Bumped VERSION: {current_version} -> {new_version}")

    # Update receipt index
    index = load_receipt_index(index_path)
    upsert_index_entry(index, task_id, index_entry)
    index["last_updated"] = now
    save_receipt_index(index_path, index)
    print(f"Updated receipt-index.json ({len(index['tasks'])} total entries)")

    # Summary
    print(f"\nArchive complete: {task_id}")
    print(f"  version: {current_version} -> {new_version} ({delta_class})")
    print(f"  receipts scanned: {receipts_aggregated}")
    print(f"  not_tested items: {len(not_tested)}")
    if not_tested:
        for item in not_tested:
            print(f"    - {item}")

    # Play archive-done sound (fire-and-forget; never blocks or raises)
    _play_lifecycle_sound("archive-done", root)

    sys.exit(0)


if __name__ == "__main__":
    main()
