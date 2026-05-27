"""
session-state.py — CRUD for .wabblespec/session/state.json.

Replaces manual reads and writes of the session state file. The file is
small (~200 bytes) so the token saving per operation is modest (~200 tokens),
but making the lifecycle explicit reduces accidental drift and makes session
transitions auditable.

Usage:
    # Initialize a new session:
    python .wabblespec/engine/shared/scripts/session-state.py init --session-id seed-run-20260526xx

    # Show current state:
    python .wabblespec/engine/shared/scripts/session-state.py show

    # Activate enforcement for a module:
    python .wabblespec/engine/shared/scripts/session-state.py set \\
        --enforcement-active true \\
        --active-module guard

    # Add required receipts:
    python .wabblespec/engine/shared/scripts/session-state.py set \\
        --required-receipts executor-receipt verifier-receipt

    # Record completed task and clear enforcement:
    python .wabblespec/engine/shared/scripts/session-state.py complete \\
        --task "Build foo.md — ARCHIVE PASS"

    # Clear session (enforcement off, no active module):
    python .wabblespec/engine/shared/scripts/session-state.py clear

    # Check if enforcement is currently active (exit 0 = yes, 1 = no):
    python .wabblespec/engine/shared/scripts/session-state.py check --enforcement-active

Exit codes:
    0  success (or condition met for --check)
    1  condition not met (--check), bad args, or no state file for show/set
    2  state file not readable / directory not writable
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


def find_wabblespec(start_dir=None):
    if start_dir is None:
        start_dir = os.getcwd()
    candidate = start_dir
    for _ in range(10):
        ws = os.path.join(candidate, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def state_path(ws):
    return os.path.join(ws, "state", "session", "state.json")


def load_state(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read state file at {path}: {e}", file=sys.stderr)
        sys.exit(2)


def save_state(path, data, dry_run=False):
    text = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"--- [DRY RUN] {path} ---")
        print(text)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def empty_state(session_id):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "enforcement_active": False,
        "required_receipts": [],
        "active_module": None,
        "evidence_drawers": [],
        "session_id": session_id,
        "started_at": now,
        "completed_at": None,
        "last_task": None,
    }


def cmd_init(args, sp, ws):
    existing = load_state(sp)
    if existing and not args.force:
        print(f"State already exists for session '{existing.get('session_id')}'.")
        print("Use --force to reinitialize.")
        sys.exit(1)
    state = empty_state(args.session_id)
    save_state(sp, state, dry_run=args.dry_run)
    print(f"Initialized session state: {args.session_id}")


def cmd_show(args, sp, ws):
    state = load_state(sp)
    if state is None:
        print("No state file found. Run: session-state.py init --session-id <id>")
        sys.exit(1)
    print(json.dumps(state, indent=2))


def cmd_set(args, sp, ws):
    state = load_state(sp)
    if state is None:
        print("No state file found. Run: session-state.py init --session-id <id>", file=sys.stderr)
        sys.exit(1)

    changed = []
    if args.enforcement_active is not None:
        val = args.enforcement_active.lower() in ("true", "1", "yes")
        state["enforcement_active"] = val
        changed.append(f"enforcement_active={val}")

    if args.active_module is not None:
        state["active_module"] = args.active_module or None
        changed.append(f"active_module={state['active_module']}")

    if args.required_receipts is not None:
        state["required_receipts"] = args.required_receipts
        changed.append(f"required_receipts={args.required_receipts}")

    if args.evidence_drawers is not None:
        state["evidence_drawers"] = args.evidence_drawers
        changed.append(f"evidence_drawers={args.evidence_drawers}")

    if not changed:
        print("WARNING: Nothing to set. Pass at least one field flag.")
        sys.exit(1)

    save_state(sp, state, dry_run=args.dry_run)
    print(f"Updated state: {', '.join(changed)}")


def cmd_complete(args, sp, ws):
    state = load_state(sp)
    if state is None:
        print("No state file. Run init first.", file=sys.stderr)
        sys.exit(1)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["enforcement_active"] = False
    state["active_module"] = None
    state["required_receipts"] = []
    state["completed_at"] = now
    if args.task:
        state["last_task"] = args.task
    save_state(sp, state, dry_run=args.dry_run)
    print(f"Session completed: {state.get('session_id')} at {now}")
    if args.task:
        print(f"  last_task: {args.task}")


def cmd_clear(args, sp, ws):
    state = load_state(sp)
    if state is None:
        state = empty_state("unknown")
    state["enforcement_active"] = False
    state["active_module"] = None
    state["required_receipts"] = []
    save_state(sp, state, dry_run=args.dry_run)
    print("Cleared enforcement state.")


def cmd_check(args, sp, ws):
    state = load_state(sp)
    if state is None:
        print("No state file.")
        sys.exit(1)

    if args.enforcement_active:
        val = state.get("enforcement_active", False)
        print(f"enforcement_active: {val}")
        sys.exit(0 if val else 1)


def main():
    parser = argparse.ArgumentParser(
        description="CRUD for .wabblespec/session/state.json.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--wabblespec-dir", metavar="PATH")

    sub = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = sub.add_parser("init", help="Initialize a new session state.")
    p_init.add_argument("--session-id", required=True)
    p_init.add_argument("--force", action="store_true", help="Reinitialize even if state exists.")
    p_init.add_argument("--dry-run", action="store_true")

    # show
    sub.add_parser("show", help="Print current state as JSON.")

    # set
    p_set = sub.add_parser("set", help="Update state fields.")
    p_set.add_argument("--enforcement-active", metavar="true|false")
    p_set.add_argument("--active-module", metavar="MODULE_ID")
    p_set.add_argument("--required-receipts", nargs="*", metavar="TYPE")
    p_set.add_argument("--evidence-drawers", nargs="*", metavar="DRAWER_ID")
    p_set.add_argument("--dry-run", action="store_true")

    # complete
    p_comp = sub.add_parser("complete", help="Mark session complete, clear enforcement.")
    p_comp.add_argument("--task", metavar="TEXT", help="Description of completed task.")
    p_comp.add_argument("--dry-run", action="store_true")

    # clear
    p_clr = sub.add_parser("clear", help="Clear enforcement flags without ending session.")
    p_clr.add_argument("--dry-run", action="store_true")

    # check
    p_chk = sub.add_parser("check", help="Test a state condition (exit 0 = true).")
    p_chk.add_argument("--enforcement-active", action="store_true")

    args = parser.parse_args()
    if not hasattr(args, "dry_run"):
        args.dry_run = False

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/. Run from inside the repo.", file=sys.stderr)
        sys.exit(2)

    sp = state_path(ws)

    dispatch = {
        "init": cmd_init,
        "show": cmd_show,
        "set": cmd_set,
        "complete": cmd_complete,
        "clear": cmd_clear,
        "check": cmd_check,
    }
    dispatch[args.command](args, sp, ws)
    sys.exit(0)


if __name__ == "__main__":
    main()
