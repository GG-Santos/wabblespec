"""
memo-writer.py — Write a compaction-resistant session memo.

Writes critical in-flight state to state/session/memo.md so it survives
context compaction. The SessionStart hook injects memo.md contents on
next startup when the file is present.

Usage:
    # Auto-populate from session state (called by PreCompact hook):
    python memo-writer.py --auto

    # Add a specific note:
    python memo-writer.py --note "Blocked on: waiting for attestation before Wave 3"

    # Clear the memo (call after archive or session close):
    python memo-writer.py --clear

    # Show current memo:
    python memo-writer.py --show

Exit codes:
    0  success
    1  error
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


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


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def write_file(path, content, dry_run):
    if dry_run:
        print(f"[dry-run] would write {path}")
        print(content)
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)


def build_auto_memo(ws):
    """Build memo content from current session state."""
    state_path = os.path.join(ws, "state", "session", "state.json")
    state = read_json(state_path) or {}

    wave_plan_path = os.path.join(ws, "state", "plans", "current-wave-plan.md")
    wave_plan_content = read_text(wave_plan_path) or ""

    task_card_path = os.path.join(ws, "state", "plans", "task-card.md")
    task_card_content = read_text(task_card_path) or ""

    lines = [f"## Session Memo [{now_iso()}]", ""]

    session_id = state.get("session_id") or "unknown"
    active_module = state.get("active_module") or "none"
    required_receipts = state.get("required_receipts") or []

    lines.append(f"- Session: {session_id}")
    lines.append(f"- Active module: {active_module}")
    if required_receipts:
        lines.append(f"- Required receipts: {', '.join(required_receipts)}")

    # Extract goal from task card
    for line in task_card_content.splitlines():
        if line.startswith("**goal:**"):
            goal = line.replace("**goal:**", "").strip()
            lines.append(f"- Goal: {goal[:120]}")
            break

    # Extract current wave from wave plan (look for IN_PROGRESS marker)
    for line in wave_plan_content.splitlines():
        if "IN_PROGRESS" in line or "→" in line:
            lines.append(f"- In-progress: {line.strip()[:100]}")
            break

    lines.append("")
    lines.append("_Injected by memo-writer.py on PreCompact. Re-injected by SessionStart._")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Write a compaction-resistant session memo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--auto", action="store_true",
                        help="Auto-populate from current session state (called by PreCompact).")
    parser.add_argument("--note", action="append", default=[], metavar="TEXT",
                        help="Add a specific note line to the memo (repeatable).")
    parser.add_argument("--clear", action="store_true",
                        help="Delete the memo file.")
    parser.add_argument("--show", action="store_true",
                        help="Print current memo and exit.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wabblespec-dir", metavar="PATH")
    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
        sys.exit(1)

    memo_path = os.path.join(ws, "state", "session", "memo.md")

    if args.show:
        content = read_text(memo_path)
        if content:
            print(content)
        else:
            print("(no memo file)")
        sys.exit(0)

    if args.clear:
        if os.path.exists(memo_path):
            if not args.dry_run:
                os.remove(memo_path)
            print("Cleared memo.")
        else:
            print("No memo to clear.")
        sys.exit(0)

    # Build memo content
    if args.auto:
        content = build_auto_memo(ws)
    else:
        content = f"## Session Memo [{now_iso()}]\n\n"

    # Append manual notes
    for note in args.note:
        content += f"- {note}\n"

    if not args.auto and not args.note:
        print("ERROR: specify --auto, --note, --show, or --clear.", file=sys.stderr)
        sys.exit(1)

    write_file(memo_path, content, args.dry_run)
    print(f"Wrote {memo_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
