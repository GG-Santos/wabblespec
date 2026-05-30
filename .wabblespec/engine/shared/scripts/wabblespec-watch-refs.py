"""
wabblespec-watch-refs.py — Reference drawer staleness watcher.

Scans .wabblespec/state/memory/wings/references/ for drawers with evidence_path
fields. Tracks their last-seen state via a watermark file. On first encounter
per drawer, establishes a baseline (no NEEDS_REVERIFICATION). On subsequent
runs, marks drawers NEEDS_REVERIFICATION when their evidence file is missing or
the drawer itself has been modified.

Watermark file: .wabblespec/state/memory/wings/references/watch-watermarks.json

Usage:
    python wabblespec-watch-refs.py [--dry-run] [--verbose] [--max-watermarks N]

Exit codes:
    0  success (including no-change first-run baseline)
    1  error
"""

import sys
import os
import json
import glob
import argparse
from datetime import datetime, timezone

MAX_WATERMARKS = 500


def find_wabblespec(start=None):
    cwd = start or os.getcwd()
    for _ in range(10):
        ws = os.path.join(cwd, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return None


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_watermarks(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"schema_version": "1.0", "watermarks": {}, "last_run": None, "first_run_complete": False}


def save_watermarks(path, data, dry_run):
    if dry_run:
        print(f"[dry-run] would write {path}")
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def read_drawer(path):
    """Try to read a drawer file as JSON or YAML-frontmatter JSON."""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if path.endswith(".json"):
            return json.loads(content)
        # Markdown with YAML frontmatter -- extract first JSON-like block
        return None
    except Exception:
        return None


def update_staleness(drawer_path, field="staleness_state", value="NEEDS_REVERIFICATION", dry_run=False):
    """Patch staleness_state in a JSON drawer file."""
    if dry_run:
        print(f"[dry-run] would mark {drawer_path} -> {value}")
        return
    try:
        with open(drawer_path, encoding="utf-8") as f:
            data = json.load(f)
        data[field] = value
        tmp = drawer_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp, drawer_path)
    except Exception as e:
        print(f"  warning: could not update staleness in {drawer_path}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Reference drawer staleness watcher.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing.")
    parser.add_argument("--verbose", action="store_true", help="Print per-drawer status.")
    parser.add_argument("--max-watermarks", type=int, default=MAX_WATERMARKS,
                        help=f"Max watermark entries (oldest pruned). Default: {MAX_WATERMARKS}.")
    parser.add_argument("--wabblespec-dir", metavar="PATH")
    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
        sys.exit(1)

    refs_dir = os.path.join(ws, "state", "memory", "wings", "references")
    watermarks_path = os.path.join(refs_dir, "watch-watermarks.json")

    data = load_watermarks(watermarks_path)
    watermarks = data.get("watermarks", {})

    # Collect all JSON drawers in rooms/
    rooms_dir = os.path.join(refs_dir, "rooms")
    drawer_files = glob.glob(os.path.join(rooms_dir, "**", "*.json"), recursive=True)
    drawer_files = [f for f in drawer_files if not f.endswith("watch-watermarks.json")]

    marked = 0
    baselined = 0
    unchanged = 0

    for drawer_path in drawer_files:
        drawer = read_drawer(drawer_path)
        if drawer is None:
            continue

        drawer_id = drawer.get("drawer_id") or drawer.get("id") or os.path.basename(drawer_path)
        evidence_path = drawer.get("evidence_path", "")
        current_staleness = drawer.get("staleness_state", "UNKNOWN")
        try:
            drawer_mtime = os.path.getmtime(drawer_path)
        except OSError:
            drawer_mtime = 0.0

        entry = watermarks.get(drawer_id)

        if entry is None:
            # First run for this drawer: establish baseline
            watermarks[drawer_id] = {
                "drawer_path": drawer_path.replace("\\", "/"),
                "evidence_path": evidence_path,
                "last_seen_mtime": drawer_mtime,
                "last_seen_staleness": current_staleness,
                "watermark_updated": now_iso(),
                "first_run": True,
            }
            baselined += 1
            if args.verbose:
                print(f"  [baseline] {drawer_id}")
            continue

        # Subsequent run: check for changes
        last_mtime = entry.get("last_seen_mtime", 0.0)
        needs_mark = False
        reason = ""

        # Check if evidence_path no longer exists (local file)
        if evidence_path and os.path.isabs(evidence_path) and not os.path.exists(evidence_path):
            needs_mark = True
            reason = "evidence_path missing"

        # Check if drawer file was modified since last watermark
        if not needs_mark and drawer_mtime > last_mtime + 1.0:
            needs_mark = True
            reason = "drawer modified since last watermark"

        if needs_mark and current_staleness not in ("NEEDS_REVERIFICATION", "EXPIRED"):
            update_staleness(drawer_path, value="NEEDS_REVERIFICATION", dry_run=args.dry_run)
            watermarks[drawer_id].update({
                "last_seen_mtime": drawer_mtime,
                "last_seen_staleness": "NEEDS_REVERIFICATION",
                "watermark_updated": now_iso(),
                "first_run": False,
                "marked_reason": reason,
            })
            marked += 1
            if args.verbose:
                print(f"  [marked] {drawer_id}: {reason}")
        else:
            watermarks[drawer_id].update({
                "last_seen_mtime": drawer_mtime,
                "last_seen_staleness": current_staleness,
                "watermark_updated": now_iso(),
                "first_run": False,
            })
            unchanged += 1
            if args.verbose:
                print(f"  [ok] {drawer_id}")

    # Prune if over max
    if len(watermarks) > args.max_watermarks:
        sorted_keys = sorted(watermarks, key=lambda k: watermarks[k].get("watermark_updated", ""))
        for old_key in sorted_keys[:len(watermarks) - args.max_watermarks]:
            del watermarks[old_key]

    data["watermarks"] = watermarks
    data["last_run"] = now_iso()
    data["first_run_complete"] = True

    save_watermarks(watermarks_path, data, args.dry_run)

    print(f"Watch complete: {baselined} baselined, {marked} marked NEEDS_REVERIFICATION, {unchanged} unchanged.")
    sys.exit(0)


if __name__ == "__main__":
    main()
