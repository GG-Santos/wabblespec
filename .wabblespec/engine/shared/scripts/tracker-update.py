"""
tracker-update.py — CRUD for .wabblespec/experiments/tracker.json.

Replaces Claude reading tracker.json (~13K tokens in a mature tracker), finding an
entry by blueprint_id, patching fields, and rewriting. Pure JSON CRUD — no reasoning
required. All writes are atomic (temp + os.replace).

Subcommands:
    show    Print one entry as JSON
    list    List all entries with status summary
    add     Create a new tracker entry (after Benchmark setup)
    set     Update fields on an existing entry (after Benchmark result)
    forge   Record forge promotion result
    delete  Remove an entry from the tracker

Usage:
    # Show one entry:
    python .wabblespec/engine/shared/scripts/tracker-update.py show \\
        --blueprint-id acceptance-test-executor-enforcement-v1

    # List all entries:
    python .wabblespec/engine/shared/scripts/tracker-update.py list

    # List only entries with a specific forge status:
    python .wabblespec/engine/shared/scripts/tracker-update.py list --forge-status pending

    # Create new tracker entry:
    python .wabblespec/engine/shared/scripts/tracker-update.py add \\
        --blueprint-id my-new-candidate-v1 \\
        --metric-name false_completion_rate \\
        --metric-type rate \\
        --developer-outcome false_completion \\
        --threshold 0.0 \\
        --direction lower_is_better \\
        --fixture-set .wabblespec/experiments/fixtures/my-new-candidate-v1/ \\
        --golden-ref .wabblespec/experiments/fixtures/my-new-candidate-v1/golden.json

    # Record benchmark result:
    python .wabblespec/engine/shared/scripts/tracker-update.py set \\
        --blueprint-id my-new-candidate-v1 \\
        --held-out-cases 8 \\
        --held-out-value 0.0 \\
        --verdict PASS \\
        --notes "All 8 held-out cases passed..."

    # Record forge promotion:
    python .wabblespec/engine/shared/scripts/tracker-update.py forge \\
        --blueprint-id my-new-candidate-v1 \\
        --forge-status PROMOTED \\
        --forge-receipt .wabblespec/receipts/forge-my-new-candidate-v1-receipt.json

    # Dry run (add or set):
    python .wabblespec/engine/shared/scripts/tracker-update.py add ... --dry-run
    python .wabblespec/engine/shared/scripts/tracker-update.py set ... --dry-run

Exit codes:
    0  success
    1  entry not found, duplicate on add, or bad arguments
    2  tracker file not readable or directory not writable
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def find_tracker(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        path = os.path.join(candidate, ".wabblespec", "state", "experiments", "tracker.json")
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    # Return default path even if file doesn't exist yet
    ws_candidate = start or os.getcwd()
    for _ in range(12):
        ws = os.path.join(ws_candidate, ".wabblespec")
        if os.path.isdir(ws):
            return os.path.join(ws, "state", "experiments", "tracker.json")
        parent = os.path.dirname(ws_candidate)
        if parent == ws_candidate:
            break
        ws_candidate = parent
    return None


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def load_tracker(path):
    if not os.path.isfile(path):
        return {"entries": []}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if "entries" not in data:
            data["entries"] = []
        return data
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)


def save_tracker(path, data, dry_run=False):
    text = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"--- [DRY RUN] {path} ({len(data['entries'])} entries) ---")
        print(text[:2000])
        if len(text) > 2000:
            print(f"... ({len(text) - 2000} chars truncated)")
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


def find_entry(data, blueprint_id):
    for entry in data.get("entries", []):
        if entry.get("blueprint_id") == blueprint_id:
            return entry
    return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_show(args, tracker_path):
    data = load_tracker(tracker_path)
    entry = find_entry(data, args.blueprint_id)
    if entry is None:
        print(f"ERROR: No entry for blueprint_id '{args.blueprint_id}'", file=sys.stderr)
        ids = [e.get("blueprint_id") for e in data["entries"]]
        print(f"Known IDs: {ids}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(entry, indent=2))


def cmd_list(args, tracker_path):
    data = load_tracker(tracker_path)
    entries = data.get("entries", [])

    if args.forge_status:
        entries = [e for e in entries
                   if (e.get("forge_status") or "pending").lower() == args.forge_status.lower()]

    if not entries:
        print("No entries found.")
        return

    # Table header
    print(f"  {'blueprint_id':<50} {'verdict':<7} {'forge':<12} {'held_out'}")
    print(f"  {'-'*50} {'-'*7} {'-'*12} {'-'*8}")
    for e in entries:
        bid = e.get("blueprint_id", "?")[:50]
        verdict = e.get("verdict") or "pending"
        forge = e.get("forge_status") or "pending"
        held_out = e.get("held_out_cases", "?")
        print(f"  {bid:<50} {verdict:<7} {forge:<12} {held_out}")
    print(f"\nTotal: {len(entries)}")


def cmd_add(args, tracker_path):
    data = load_tracker(tracker_path)

    if find_entry(data, args.blueprint_id):
        print(f"ERROR: Entry '{args.blueprint_id}' already exists. Use 'set' to update it.",
              file=sys.stderr)
        sys.exit(1)

    entry = {
        "blueprint_id": args.blueprint_id,
        "run_at": now_utc(),
        "metric_name": args.metric_name,
        "metric_type": args.metric_type,
        "developer_outcome": args.developer_outcome,
        "held_out_cases": None,
        "held_out_value": None,
        "threshold": args.threshold,
        "direction": args.direction,
        "verdict": None,
        "failure_note": None,
        "requeue_decision": None,
        "fixture_set": args.fixture_set,
        "golden_ref": args.golden_ref,
        "notes": args.notes,
        "forge_status": "pending",
        "forge_at": None,
        "forge_receipt": None,
    }

    data["entries"].append(entry)
    save_tracker(tracker_path, data, dry_run=args.dry_run)

    if not args.dry_run:
        print(f"Added tracker entry: {args.blueprint_id}")
        print(f"  metric: {args.metric_name} ({args.direction}), threshold: {args.threshold}")


def cmd_set(args, tracker_path):
    data = load_tracker(tracker_path)
    entry = find_entry(data, args.blueprint_id)
    if entry is None:
        print(f"ERROR: No entry for '{args.blueprint_id}'. Use 'add' to create it.",
              file=sys.stderr)
        sys.exit(1)

    changed = []

    if args.held_out_cases is not None:
        entry["held_out_cases"] = args.held_out_cases
        changed.append(f"held_out_cases={args.held_out_cases}")

    if args.held_out_value is not None:
        entry["held_out_value"] = args.held_out_value
        changed.append(f"held_out_value={args.held_out_value}")

    if args.verdict:
        entry["verdict"] = args.verdict
        changed.append(f"verdict={args.verdict}")

    if args.failure_note:
        entry["failure_note"] = args.failure_note
        changed.append("failure_note set")

    if args.requeue_decision:
        entry["requeue_decision"] = args.requeue_decision
        changed.append(f"requeue_decision={args.requeue_decision}")

    if args.notes:
        entry["notes"] = args.notes
        changed.append("notes updated")

    if args.fixture_set:
        entry["fixture_set"] = args.fixture_set
        changed.append(f"fixture_set={args.fixture_set}")

    if args.golden_ref:
        entry["golden_ref"] = args.golden_ref
        changed.append(f"golden_ref={args.golden_ref}")

    if not changed:
        print("WARNING: No fields to update.")
        sys.exit(1)

    save_tracker(tracker_path, data, dry_run=args.dry_run)

    if not args.dry_run:
        print(f"Updated '{args.blueprint_id}': {', '.join(changed)}")


def cmd_forge(args, tracker_path):
    data = load_tracker(tracker_path)
    entry = find_entry(data, args.blueprint_id)
    if entry is None:
        print(f"ERROR: No entry for '{args.blueprint_id}'.", file=sys.stderr)
        sys.exit(1)

    ts = now_utc()
    entry["forge_status"] = args.forge_status
    entry["forge_at"] = ts

    if args.forge_receipt:
        entry["forge_receipt"] = args.forge_receipt

    save_tracker(tracker_path, data, dry_run=args.dry_run)

    if not args.dry_run:
        print(f"Recorded forge for '{args.blueprint_id}': {args.forge_status} at {ts}")


def cmd_delete(args, tracker_path):
    data = load_tracker(tracker_path)
    before = len(data["entries"])
    data["entries"] = [e for e in data["entries"]
                       if e.get("blueprint_id") != args.blueprint_id]
    after = len(data["entries"])

    if before == after:
        print(f"ERROR: No entry for '{args.blueprint_id}'.", file=sys.stderr)
        sys.exit(1)

    save_tracker(tracker_path, data, dry_run=args.dry_run)

    if not args.dry_run:
        print(f"Deleted entry: {args.blueprint_id}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CRUD for .wabblespec/experiments/tracker.json.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--tracker", metavar="PATH",
                        help="Explicit path to tracker.json (auto-discovered if omitted).")

    sub = parser.add_subparsers(dest="command", required=True)

    # show
    p_sh = sub.add_parser("show", help="Print one entry as JSON.")
    p_sh.add_argument("--blueprint-id", required=True, dest="blueprint_id")

    # list
    p_ls = sub.add_parser("list", help="List all entries with status.")
    p_ls.add_argument("--forge-status", metavar="STATUS", dest="forge_status",
                      help="Filter by forge status (pending, PROMOTED, REJECTED, etc.).")

    # add
    p_add = sub.add_parser("add", help="Create a new tracker entry.")
    p_add.add_argument("--blueprint-id", required=True, dest="blueprint_id")
    p_add.add_argument("--metric-name", required=True, dest="metric_name")
    p_add.add_argument("--metric-type", default="rate", dest="metric_type")
    p_add.add_argument("--developer-outcome", required=True, dest="developer_outcome")
    p_add.add_argument("--threshold", required=True, type=float)
    p_add.add_argument("--direction", required=True,
                       choices=["lower_is_better", "higher_is_better"])
    p_add.add_argument("--fixture-set", metavar="PATH", dest="fixture_set")
    p_add.add_argument("--golden-ref", metavar="PATH", dest="golden_ref")
    p_add.add_argument("--notes", metavar="TEXT")
    p_add.add_argument("--dry-run", action="store_true")

    # set
    p_set = sub.add_parser("set", help="Update fields on an existing entry.")
    p_set.add_argument("--blueprint-id", required=True, dest="blueprint_id")
    p_set.add_argument("--held-out-cases", type=int, dest="held_out_cases")
    p_set.add_argument("--held-out-value", type=float, dest="held_out_value")
    p_set.add_argument("--verdict", choices=["PASS", "FAIL"])
    p_set.add_argument("--failure-note", metavar="TEXT", dest="failure_note")
    p_set.add_argument("--requeue-decision", metavar="TEXT", dest="requeue_decision")
    p_set.add_argument("--notes", metavar="TEXT")
    p_set.add_argument("--fixture-set", metavar="PATH", dest="fixture_set")
    p_set.add_argument("--golden-ref", metavar="PATH", dest="golden_ref")
    p_set.add_argument("--dry-run", action="store_true")

    # forge
    p_forge = sub.add_parser("forge", help="Record forge promotion result.")
    p_forge.add_argument("--blueprint-id", required=True, dest="blueprint_id")
    p_forge.add_argument("--forge-status", required=True,
                         choices=["PROMOTED", "REJECTED", "DEFERRED", "pending"],
                         dest="forge_status")
    p_forge.add_argument("--forge-receipt", metavar="PATH", dest="forge_receipt")
    p_forge.add_argument("--dry-run", action="store_true")

    # delete
    p_del = sub.add_parser("delete", help="Remove an entry from the tracker.")
    p_del.add_argument("--blueprint-id", required=True, dest="blueprint_id")
    p_del.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if not hasattr(args, "dry_run"):
        args.dry_run = False

    tracker_path = args.tracker or find_tracker()
    if tracker_path is None:
        print("ERROR: Cannot find .wabblespec/experiments/tracker.json and no .wabblespec/ "
              "directory found. Run from inside the repo.", file=sys.stderr)
        sys.exit(2)

    dispatch = {
        "show": cmd_show,
        "list": cmd_list,
        "add": cmd_add,
        "set": cmd_set,
        "forge": cmd_forge,
        "delete": cmd_delete,
    }
    dispatch[args.command](args, tracker_path)
    sys.exit(0)


if __name__ == "__main__":
    main()
