"""
watzup-scan.py — Session handoff scanner.

Read-only repo state inspector that summarises the current WabbleSpec session,
active wave, pending receipts, and recent git commits into a handoff report.

Safety: read-only only — no writes, no branch switching, no receipt edits.
If state cannot be proved, emits a warning rather than guessing.

Usage:
    python watzup-scan.py [--json] [--no-git]

Output sections:
    ## Current Session
    ## Active Wave
    ## Pending Receipts
    ## Recent Commits

Exit codes:
    0  success
    1  error
"""

import sys
import os
import json
import subprocess
import glob
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


def run(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd or os.getcwd(), timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


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


def scan_session(ws):
    state_path = os.path.join(ws, "state", "session", "state.json")
    state = read_json(state_path) or {}
    return state


def scan_wave_plan(ws):
    plan_path = os.path.join(ws, "state", "plans", "current-wave-plan.md")
    content = read_text(plan_path)
    if not content:
        return None, None
    # Extract generated_at and task_card
    generated_at = None
    task_card = None
    for line in content.splitlines():
        if line.startswith("**generated_at:**"):
            generated_at = line.split("**generated_at:**")[-1].strip()
        if line.startswith("**task_card:**"):
            task_card = line.split("**task_card:**")[-1].strip()
    return generated_at, task_card


def scan_receipts(ws):
    receipts_dir = os.path.join(ws, "state", "receipts")
    if not os.path.isdir(receipts_dir):
        return []
    files = sorted(glob.glob(os.path.join(receipts_dir, "*.json")), key=os.path.getmtime, reverse=True)
    result = []
    for f in files[:10]:
        data = read_json(f)
        if data:
            result.append({
                "file": os.path.basename(f),
                "type": data.get("type") or data.get("module", "?"),
                "status": data.get("status", "?"),
                "timestamp": data.get("timestamp") or data.get("locked_at", "?"),
            })
    return result


def scan_checkpoints(ws):
    cp_dir = os.path.join(ws, "state", "session", "checkpoints")
    if not os.path.isdir(cp_dir):
        return []
    files = sorted(glob.glob(os.path.join(cp_dir, "*.json")), key=os.path.getmtime, reverse=True)
    result = []
    for f in files[:5]:
        data = read_json(f)
        if data:
            result.append({
                "file": os.path.basename(f),
                "wave_index": data.get("wave_index", "?"),
                "wave_label": data.get("wave_label", "?"),
                "timestamp": data.get("timestamp", "?"),
            })
    return result


def scan_git(repo_root):
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    status = run(["git", "status", "--short"], cwd=repo_root)
    log = run(["git", "log", "--oneline", "-8"], cwd=repo_root)
    return branch, status, log


def format_text(session, wave_generated, task_card, receipts, checkpoints, branch, status, log):
    lines = []

    lines.append("## Current Session")
    if session:
        sid = session.get("session_id", "unknown")
        module = session.get("active_module", "none")
        enf = session.get("enforcement_active", False)
        lines.append(f"  Session ID: {sid}")
        lines.append(f"  Active module: {module}")
        lines.append(f"  Enforcement active: {enf}")
        req = session.get("required_receipts", [])
        if req:
            lines.append(f"  Required receipts: {', '.join(req)}")
    else:
        lines.append("  WARNING: No session state found.")

    lines.append("")
    lines.append("## Active Wave")
    if wave_generated:
        lines.append(f"  Wave plan generated: {wave_generated}")
        lines.append(f"  Task card: {task_card or 'unknown'}")
    else:
        lines.append("  WARNING: No active wave plan found.")

    if checkpoints:
        lines.append("  Recent checkpoints:")
        for cp in checkpoints:
            lines.append(f"    Wave {cp['wave_index']} ({cp['wave_label']}) at {cp['timestamp']}")

    lines.append("")
    lines.append("## Pending Receipts")
    if receipts:
        for r in receipts:
            lines.append(f"  [{r['status']}] {r['type']} — {r['file']} ({r['timestamp']})")
    else:
        lines.append("  No receipts found.")

    lines.append("")
    lines.append("## Recent Commits")
    if log:
        for line in log.splitlines():
            lines.append(f"  {line}")
        if branch:
            lines.append(f"  (branch: {branch})")
        if status:
            lines.append(f"  Working tree: {len(status.splitlines())} modified file(s)")
    else:
        lines.append("  WARNING: Could not read git log (not a git repo or git unavailable).")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="WabbleSpec session handoff scanner.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of text.")
    parser.add_argument("--no-git", action="store_true", help="Skip git commands.")
    parser.add_argument("--wabblespec-dir", metavar="PATH")
    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
        sys.exit(1)

    repo_root = os.path.dirname(ws)
    session = scan_session(ws)
    wave_generated, task_card = scan_wave_plan(ws)
    receipts = scan_receipts(ws)
    checkpoints = scan_checkpoints(ws)

    branch, status, log = ("", "", "")
    if not args.no_git:
        branch, status, log = scan_git(repo_root)

    if args.json:
        out = {
            "session": session,
            "wave_plan": {"generated_at": wave_generated, "task_card": task_card},
            "recent_receipts": receipts,
            "recent_checkpoints": checkpoints,
            "git": {"branch": branch, "status_lines": len(status.splitlines()) if status else 0, "log": log},
            "scanned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        print(json.dumps(out, indent=2))
    else:
        print(format_text(session, wave_generated, task_card, receipts, checkpoints, branch, status, log))

    sys.exit(0)


if __name__ == "__main__":
    main()
