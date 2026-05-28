"""
session-registry.py — Multi-session registry for WabbleSpec.

Manages state/sessions/registry.json and per-session state directories,
enabling two concurrent Claude Code terminals to run isolated sessions
without corrupting each other's scope.md, recipe.json, or state.json.

Each session gets its own directory under state/sessions/<session-id>/
containing its own scope.md, recipe.json, state.json, and checkpoints/.

Usage:
    # Create a new session (registers it and creates its directory):
    python .wabblespec/engine/shared/scripts/session-registry.py create \\
        --session-id phase4-session-isolation-20260528 \\
        --task-id phase4-session-isolation-20260528

    # List all sessions:
    python .wabblespec/engine/shared/scripts/session-registry.py list

    # Show active (IN_PROGRESS) sessions only:
    python .wabblespec/engine/shared/scripts/session-registry.py list --active

    # Close a session (mark COMPLETE):
    python .wabblespec/engine/shared/scripts/session-registry.py close \\
        --session-id phase4-session-isolation-20260528

    # Show the state directory for a session:
    python .wabblespec/engine/shared/scripts/session-registry.py path \\
        --session-id phase4-session-isolation-20260528

    # Purge COMPLETE sessions older than N days:
    python .wabblespec/engine/shared/scripts/session-registry.py purge --days 30

    # JSON output for any command:
    python .wabblespec/engine/shared/scripts/session-registry.py list --json

Exit codes:
    0  success
    1  session not found, already exists, or bad args
    2  registry file not readable / directory not writable
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone, timedelta


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
REGISTRY_SCHEMA_VERSION = 1


def find_wabblespec(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        if os.path.isdir(os.path.join(candidate, ".wabblespec")):
            return os.path.join(candidate, ".wabblespec")
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def registry_path(ws_dir):
    return os.path.join(ws_dir, "state", "sessions", "registry.json")


def sessions_root(ws_dir):
    return os.path.join(ws_dir, "state", "sessions")


def load_registry(reg_path):
    if not os.path.isfile(reg_path):
        return {"registry_version": REGISTRY_SCHEMA_VERSION, "sessions": []}
    with open(reg_path, encoding="utf-8") as fh:
        return json.load(fh)


def save_registry(reg_path, data):
    os.makedirs(os.path.dirname(reg_path), exist_ok=True)
    tmp = reg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, reg_path)


def find_session(registry, session_id):
    for s in registry["sessions"]:
        if s["session_id"] == session_id:
            return s
    return None


def cmd_create(args, ws_dir):
    reg_path = registry_path(ws_dir)
    registry = load_registry(reg_path)

    if find_session(registry, args.session_id):
        print(f"ERROR: Session '{args.session_id}' already exists in registry.", file=sys.stderr)
        sys.exit(1)

    session_dir = os.path.join(sessions_root(ws_dir), args.session_id)
    try:
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(os.path.join(session_dir, "checkpoints"), exist_ok=True)
    except OSError as e:
        print(f"ERROR: Cannot create session directory {session_dir}: {e}", file=sys.stderr)
        sys.exit(2)

    entry = {
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": "IN_PROGRESS",
        "created_at": NOW,
        "completed_at": None,
        "session_dir": os.path.relpath(session_dir,
                                       os.path.dirname(os.path.dirname(ws_dir))),
    }
    registry["sessions"].append(entry)
    try:
        save_registry(reg_path, registry)
    except OSError as e:
        print(f"ERROR: Cannot write registry: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"Created session: {args.session_id}")
    print(f"  directory: {session_dir}")


def cmd_list(args, ws_dir):
    reg_path = registry_path(ws_dir)
    registry = load_registry(reg_path)

    sessions = registry["sessions"]
    if args.active:
        sessions = [s for s in sessions if s["status"] == "IN_PROGRESS"]

    if args.json:
        print(json.dumps({"sessions": sessions}, indent=2))
        return

    if not sessions:
        print("No sessions found.")
        return

    print(f"{'SESSION ID':<45} {'STATUS':<12} {'CREATED'}")
    print("-" * 80)
    for s in sessions:
        print(f"{s['session_id']:<45} {s['status']:<12} {s['created_at']}")


def cmd_close(args, ws_dir):
    reg_path = registry_path(ws_dir)
    registry = load_registry(reg_path)

    entry = find_session(registry, args.session_id)
    if not entry:
        print(f"ERROR: Session '{args.session_id}' not found.", file=sys.stderr)
        sys.exit(1)

    entry["status"] = "COMPLETE"
    entry["completed_at"] = NOW
    try:
        save_registry(reg_path, registry)
    except OSError as e:
        print(f"ERROR: Cannot write registry: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Closed session: {args.session_id}")


def cmd_path(args, ws_dir):
    reg_path = registry_path(ws_dir)
    registry = load_registry(reg_path)
    entry = find_session(registry, args.session_id)
    if not entry:
        print(f"ERROR: Session '{args.session_id}' not found.", file=sys.stderr)
        sys.exit(1)
    print(entry["session_dir"])


def cmd_purge(args, ws_dir):
    reg_path = registry_path(ws_dir)
    registry = load_registry(reg_path)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    before = len(registry["sessions"])
    registry["sessions"] = [
        s for s in registry["sessions"]
        if not (
            s["status"] == "COMPLETE"
            and s.get("completed_at")
            and datetime.fromisoformat(s["completed_at"].replace("Z", "+00:00")) < cutoff
        )
    ]
    purged = before - len(registry["sessions"])
    try:
        save_registry(reg_path, registry)
    except OSError as e:
        print(f"ERROR: Cannot write registry: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Purged {purged} session(s) older than {args.days} days.")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--wabblespec-dir", metavar="PATH",
                        help="Explicit .wabblespec directory path.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Register a new session.")
    p_create.add_argument("--session-id", required=True)
    p_create.add_argument("--task-id", required=True)

    p_list = sub.add_parser("list", help="List sessions.")
    p_list.add_argument("--active", action="store_true",
                        help="Show IN_PROGRESS sessions only.")
    p_list.add_argument("--json", action="store_true", dest="json")

    p_close = sub.add_parser("close", help="Mark a session COMPLETE.")
    p_close.add_argument("--session-id", required=True)

    p_path = sub.add_parser("path", help="Print the session_dir for a session.")
    p_path.add_argument("--session-id", required=True)

    p_purge = sub.add_parser("purge", help="Remove old COMPLETE sessions from registry.")
    p_purge.add_argument("--days", type=int, default=30,
                         help="Purge sessions completed more than N days ago (default: 30).")

    args = parser.parse_args()

    ws_dir = args.wabblespec_dir or find_wabblespec()
    if not ws_dir:
        print("ERROR: Cannot find .wabblespec directory.", file=sys.stderr)
        sys.exit(2)

    dispatch = {
        "create": cmd_create,
        "list": cmd_list,
        "close": cmd_close,
        "path": cmd_path,
        "purge": cmd_purge,
    }
    dispatch[args.command](args, ws_dir)


if __name__ == "__main__":
    main()
