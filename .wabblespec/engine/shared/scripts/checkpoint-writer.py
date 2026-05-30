"""
checkpoint-writer.py — Schema-enforced writer for WabbleSpec wave checkpoints.

Replaces inline JSON construction of checkpoint-wave-N.json in Executor step 5b.
Validates against wave-checkpoint.schema.json. Supports create, validate, show, list.

Usage:
    # Create — auto-derives checkpoint_id and output path:
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py \\
        --session-id abc12345 \\
        --task-id my-task-20260531 \\
        --wave-index 1 \\
        --wave-label "Wave 2 — Implementation" \\
        --receipt .wabblespec/state/receipts/wave-2-receipt.json \\
        --file src/foo.py:created \\
        --file src/bar.py:modified:abc123sha \\
        --ac-met "AC-01: schema file exists" \\
        --ac-pending "AC-02: tests pass"

    # Explicit checkpoint ID and output path:
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py \\
        --session-id abc12345 --task-id my-task --wave-index 1 \\
        --wave-label "Wave 2" \\
        --checkpoint-id wave-2-abc12345 \\
        --out .wabblespec/state/session/checkpoints/checkpoint-wave-2.json

    # With rollback blocker:
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py \\
        ... --rollback-blocker "External API call made to payment service"

    # Dry run:
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py ... --dry-run

    # Validate existing checkpoint:
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py \\
        --validate .wabblespec/state/session/checkpoints/checkpoint-wave-1.json

    # Show human-readable summary:
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py \\
        --show .wabblespec/state/session/checkpoints/checkpoint-wave-1.json

    # List checkpoints in session directory:
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py --list
    python .wabblespec/engine/shared/scripts/checkpoint-writer.py --list abc12345

--file format: path:action  or  path:action:prior_hash
  action must be: created | modified | deleted
  prior_hash (optional): SHA-256 of file content before this wave

Output path (when --out omitted):
    .wabblespec/state/session/checkpoints/checkpoint-wave-{wave_index}-{session_id[:8]}.json

Exit codes:
    0  success
    1  validation failure or bad arguments
    2  file not writable / directory missing
"""

from __future__ import annotations

import sys
import os
import json
import argparse
from datetime import datetime, timezone

VALID_ACTIONS = ["created", "modified", "deleted"]

REQUIRED_FIELDS = [
    "checkpoint_id", "session_id", "task_id", "wave_index",
    "wave_label", "timestamp", "receipts_written", "files_modified", "state_snapshot",
]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_wabblespec(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        ws = os.path.join(candidate, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def derive_checkpoint_id(wave_index, session_id):
    sid = session_id[:8] if session_id else "unknown"
    return f"wave-{wave_index}-{sid}"


def derive_output_path(ws, wave_index, session_id):
    sid = session_id[:8] if session_id else "unknown"
    fname = f"checkpoint-wave-{wave_index}-{sid}.json"
    return os.path.join(ws, "state", "session", "checkpoints", fname)


def parse_file_entry(raw):
    parts = raw.split(":", 2)
    if len(parts) < 2:
        raise ValueError(f"--file must be path:action or path:action:hash, got: {raw!r}")
    path, action = parts[0], parts[1]
    if action not in VALID_ACTIONS:
        raise ValueError(f"action must be one of {VALID_ACTIONS}, got: {action!r}")
    entry = {"path": path, "action": action}
    if len(parts) == 3 and parts[2]:
        entry["prior_hash"] = parts[2]
    return entry


def write_json(path, data, dry_run=False):
    text = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"--- [DRY RUN] {path} ---")
        print(text)
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        print(f"ERROR: Cannot write {path}: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Wrote {path}")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_checkpoint(data, path=None):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    wi = data.get("wave_index")
    if wi is not None and (not isinstance(wi, int) or wi < 0):
        errors.append(f"wave_index must be a non-negative integer, got: {wi!r}")

    for i, fm in enumerate(data.get("files_modified") or []):
        if "path" not in fm:
            errors.append(f"files_modified[{i}] missing 'path'")
        if "action" not in fm:
            errors.append(f"files_modified[{i}] missing 'action'")
        elif fm["action"] not in VALID_ACTIONS:
            errors.append(f"files_modified[{i}].action must be one of {VALID_ACTIONS}")

    if not isinstance(data.get("receipts_written", []), list):
        errors.append("receipts_written must be an array")

    if not isinstance(data.get("state_snapshot", {}), dict):
        errors.append("state_snapshot must be an object")

    rb = data.get("rollback_safe")
    if rb is not None and not isinstance(rb, bool):
        errors.append(f"rollback_safe must be boolean, got: {rb!r}")

    return errors


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_checkpoint(args):
    ts = now_utc()

    checkpoint_id = args.checkpoint_id or derive_checkpoint_id(args.wave_index, args.session_id)

    ws = find_wabblespec()
    default_wave_plan = os.path.join(ws, "state", "plans", "current-wave-plan.md") if ws else None
    default_task_card = os.path.join(ws, "state", "plans", "task-card.md") if ws else None

    files_modified = []
    for raw in (args.file or []):
        try:
            files_modified.append(parse_file_entry(raw))
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    state_snapshot = {
        "wave_plan_path": default_wave_plan or ".wabblespec/state/plans/current-wave-plan.md",
        "task_card_path": default_task_card or ".wabblespec/state/plans/task-card.md",
        "acceptance_criteria_met": list(args.ac_met or []),
        "acceptance_criteria_pending": list(args.ac_pending or []),
    }

    rollback_blockers = list(args.rollback_blocker or [])

    checkpoint = {
        "checkpoint_id": checkpoint_id,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "wave_index": args.wave_index,
        "wave_label": args.wave_label,
        "timestamp": ts,
        "receipts_written": list(args.receipt or []),
        "files_modified": files_modified,
        "state_snapshot": state_snapshot,
        "rollback_safe": len(rollback_blockers) == 0,
        "rollback_blockers": rollback_blockers,
    }

    return checkpoint, checkpoint_id


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_create(args):
    missing = []
    for field in ("session_id", "task_id", "wave_label"):
        if not getattr(args, field, None):
            missing.append(f"--{field.replace('_', '-')}")
    if args.wave_index is None:
        missing.append("--wave-index")
    if missing:
        print(f"ERROR: Missing required arguments: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    checkpoint, checkpoint_id = build_checkpoint(args)

    errors = validate_checkpoint(checkpoint)
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    if args.out:
        out_path = args.out
    else:
        ws = find_wabblespec()
        if ws is None:
            print("ERROR: Cannot find .wabblespec/. Use --out to specify explicit path.", file=sys.stderr)
            sys.exit(2)
        out_path = derive_output_path(ws, args.wave_index, args.session_id)

    if not args.checkpoint_id:
        print(f"Auto-derived checkpoint_id: {checkpoint_id}")

    write_json(out_path, checkpoint, dry_run=args.dry_run)


def cmd_validate(args):
    data = load_json(args.validate)
    errors = validate_checkpoint(data, path=args.validate)
    if errors:
        print(f"FAIL  {args.validate}")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"PASS  {args.validate}")
        print(f"  id: {data.get('checkpoint_id')}, wave: {data.get('wave_index')}, "
              f"label: {data.get('wave_label')}, "
              f"rollback_safe: {data.get('rollback_safe', True)}")


def cmd_show(args):
    data = load_json(args.show)
    print(f"checkpoint_id:    {data.get('checkpoint_id')}")
    print(f"session_id:       {data.get('session_id')}")
    print(f"task_id:          {data.get('task_id')}")
    print(f"wave_index:       {data.get('wave_index')}")
    print(f"wave_label:       {data.get('wave_label')}")
    print(f"timestamp:        {data.get('timestamp')}")
    print(f"rollback_safe:    {data.get('rollback_safe', True)}")

    blockers = data.get("rollback_blockers") or []
    if blockers:
        print(f"rollback_blockers:")
        for b in blockers:
            print(f"  - {b}")

    receipts = data.get("receipts_written") or []
    print(f"receipts_written: {len(receipts)}")
    for r in receipts:
        print(f"  {r}")

    files = data.get("files_modified") or []
    print(f"files_modified:   {len(files)}")
    for f in files:
        h = f"  hash:{f['prior_hash'][:12]}" if f.get("prior_hash") else ""
        print(f"  {f['action']:<10}  {f['path']}{h}")

    snap = data.get("state_snapshot") or {}
    print(f"state_snapshot:")
    print(f"  wave_plan_path:   {snap.get('wave_plan_path', '(not set)')}")
    print(f"  task_card_path:   {snap.get('task_card_path', '(not set)')}")
    met = snap.get("acceptance_criteria_met") or []
    pend = snap.get("acceptance_criteria_pending") or []
    print(f"  ac_met:           {len(met)}   ac_pending: {len(pend)}")


def cmd_list(args):
    ws = find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/.", file=sys.stderr)
        sys.exit(2)

    checkpoints_dir = os.path.join(ws, "state", "session", "checkpoints")
    if not os.path.isdir(checkpoints_dir):
        print("No checkpoints directory found.")
        return

    session_filter = args.list  # '' = all, 'abc12345' = filter by session prefix

    files = sorted(
        f for f in os.listdir(checkpoints_dir) if f.endswith(".json")
    )
    if not files:
        print("No checkpoints found.")
        return

    shown = 0
    for fn in files:
        path = os.path.join(checkpoints_dir, fn)
        try:
            data = json.loads(open(path, encoding="utf-8").read())
        except Exception:
            print(f"  {fn}  (unreadable)")
            shown += 1
            continue

        sid = data.get("session_id", "")
        if session_filter and not sid.startswith(session_filter):
            continue

        wi = data.get("wave_index", "?")
        label = data.get("wave_label", "")
        rs = "safe" if data.get("rollback_safe", True) else "UNSAFE"
        files_count = len(data.get("files_modified") or [])
        receipts_count = len(data.get("receipts_written") or [])
        print(f"  wave:{wi:<3}  {rs:<6}  files:{files_count}  receipts:{receipts_count}  {label[:50]}  [{sid[:8]}]")
        shown += 1

    if shown == 0:
        print(f"No checkpoints found for session prefix: {session_filter!r}")
    else:
        print(f"\n{shown} checkpoint(s) found in {checkpoints_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Schema-enforced writer for WabbleSpec wave checkpoints.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Operations
    parser.add_argument("--validate", metavar="PATH",
                        help="Validate an existing checkpoint.")
    parser.add_argument("--show", metavar="PATH",
                        help="Show human-readable summary.")
    parser.add_argument("--list", metavar="SESSION_PREFIX", nargs="?", const="",
                        help="List checkpoints (optional: filter by session ID prefix).")

    # Create-time fields
    parser.add_argument("--session-id", metavar="ID", dest="session_id")
    parser.add_argument("--task-id", metavar="ID", dest="task_id")
    parser.add_argument("--wave-index", metavar="N", type=int, dest="wave_index",
                        help="Zero-based wave index.")
    parser.add_argument("--wave-label", metavar="TEXT", dest="wave_label",
                        help="Human-readable wave name.")
    parser.add_argument("--checkpoint-id", metavar="ID", dest="checkpoint_id",
                        help="Explicit checkpoint ID (auto-derived if omitted).")
    parser.add_argument("--receipt", metavar="PATH", action="append",
                        help="Path to a receipt written in this wave (repeatable).")
    parser.add_argument("--file", metavar="PATH:ACTION[:HASH]", action="append",
                        help="File modified this wave. Format: path:action or path:action:sha256. "
                             "action: created|modified|deleted (repeatable).")
    parser.add_argument("--ac-met", metavar="CRITERION", action="append", dest="ac_met",
                        help="Acceptance criterion met this wave (repeatable).")
    parser.add_argument("--ac-pending", metavar="CRITERION", action="append", dest="ac_pending",
                        help="Acceptance criterion still pending (repeatable).")
    parser.add_argument("--rollback-blocker", metavar="REASON", action="append", dest="rollback_blocker",
                        help="Reason rollback may be unsafe (repeatable). Sets rollback_safe=false.")

    # Output / mode
    parser.add_argument("--out", metavar="PATH",
                        help="Explicit output path (auto-derived if omitted).")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    ops = [x for x in ("validate", "show") if getattr(args, x)]
    if args.list is not None:
        ops.append("list")
    if len(ops) > 1:
        print(f"ERROR: Conflicting operations: {ops}. Use only one.", file=sys.stderr)
        sys.exit(1)

    if args.validate:
        cmd_validate(args)
    elif args.show:
        cmd_show(args)
    elif args.list is not None:
        cmd_list(args)
    else:
        cmd_create(args)

    sys.exit(0)


if __name__ == "__main__":
    main()
