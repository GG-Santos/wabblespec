"""
session-conflict-check.py — Pre-archive parallel session conflict detector.

Reads the session registry and each session's wave receipts to extract the
files each session has written. Detects overlapping target files across
IN_PROGRESS sessions and emits a conflict report before archive.

Usage:
    python session-conflict-check.py [--session-id ID] [--json] [--strict]

    --session-id   Only check this session against others (default: check all active)
    --json         Output JSON instead of human-readable text
    --strict       Exit 1 if any conflicts found (useful as pre-archive gate)

Exit codes:
    0  no conflicts (or non-strict mode with conflicts found)
    1  error, or conflicts found in --strict mode
"""

import sys
import os
import json
import glob
import argparse


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


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_session_registry(ws):
    reg_path = os.path.join(ws, "state", "sessions", "registry.json")
    return read_json(reg_path) or {}


def extract_files_from_receipts(ws, session_id):
    """Extract all files_written from wave receipts for a session."""
    receipts_dir = os.path.join(ws, "state", "receipts")
    files = set()
    # Check both global receipts dir and per-session dirs
    patterns = [
        os.path.join(receipts_dir, f"wave-*{session_id}*.json"),
        os.path.join(receipts_dir, "wave-*.json"),
        os.path.join(ws, "state", "sessions", session_id, "receipts", "wave-*.json"),
    ]
    checked = set()
    for pattern in patterns:
        for path in glob.glob(pattern):
            if path in checked:
                continue
            checked.add(path)
            receipt = read_json(path)
            if not receipt:
                continue
            if receipt.get("session_id") != session_id and session_id not in path:
                continue
            written = receipt.get("files_written", [])
            if isinstance(written, list):
                files.update(written)
    return files


def find_conflicts(session_files):
    """
    session_files: dict of {session_id: set(file_paths)}
    Returns list of {file, sessions: [session_ids]} for overlapping files.
    """
    conflicts = []
    file_to_sessions = {}
    for sid, files in session_files.items():
        for f in files:
            file_to_sessions.setdefault(f, []).append(sid)
    for f, sessions in file_to_sessions.items():
        if len(sessions) > 1:
            conflicts.append({"file": f, "sessions": sorted(sessions)})
    return sorted(conflicts, key=lambda c: c["file"])


def main():
    parser = argparse.ArgumentParser(
        description="Pre-archive parallel session conflict detector.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--session-id", metavar="ID",
                        help="Check this session against others. Default: all active sessions.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if conflicts found.")
    parser.add_argument("--wabblespec-dir", metavar="PATH")
    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
        sys.exit(1)

    registry = load_session_registry(ws)
    sessions_to_check = registry.get("sessions", {})

    if not sessions_to_check:
        # Fallback: scan receipts in global receipts dir for session IDs
        receipts_dir = os.path.join(ws, "state", "receipts")
        session_ids = set()
        for path in glob.glob(os.path.join(receipts_dir, "wave-*.json")):
            r = read_json(path)
            if r and r.get("session_id"):
                session_ids.add(r["session_id"])
        sessions_to_check = {sid: {"status": "IN_PROGRESS"} for sid in session_ids}

    # Filter to active sessions only
    active_sessions = {
        sid: info for sid, info in sessions_to_check.items()
        if info.get("status", "IN_PROGRESS") == "IN_PROGRESS"
    }

    if args.session_id:
        # Focus on target session + all others
        target_sessions = {args.session_id: active_sessions.get(args.session_id, {"status": "IN_PROGRESS"})}
        target_sessions.update({sid: info for sid, info in active_sessions.items() if sid != args.session_id})
        active_sessions = target_sessions

    # Collect files per session
    session_files = {}
    for sid in active_sessions:
        session_files[sid] = extract_files_from_receipts(ws, sid)

    conflicts = find_conflicts(session_files)

    if args.json:
        print(json.dumps({
            "sessions_checked": sorted(active_sessions.keys()),
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
        }, indent=2))
    else:
        print(f"Sessions checked: {', '.join(sorted(active_sessions.keys())) or 'none'}")
        if conflicts:
            print(f"\nCONFLICTS FOUND ({len(conflicts)}):")
            for c in conflicts:
                print(f"  {c['file']}")
                print(f"    -> {', '.join(c['sessions'])}")
        else:
            print("No conflicts found.")

    if args.strict and conflicts:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
