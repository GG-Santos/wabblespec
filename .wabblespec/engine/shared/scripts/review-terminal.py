#!/usr/bin/env python3
"""review-terminal.py — Launch a visible terminal running an interactive Claude
Code session to process a pending wave review job.

Uses `claude "task"` (interactive, subscription-billed) NOT `claude --print`
(headless, API-billed). The new terminal window is visible; the user can see
the review happening. The session uses WabbleSpec's /wave-review skill which
itself spawns parallel Agent subagents for multi-type review.

Called by review-daemon.py for each pending job. Returns immediately; the
terminal session runs independently and writes its own receipt.

Usage:
    python review-terminal.py <pending-job.json>
    python review-terminal.py <pending-job.json> --no-wait
    python review-terminal.py --check <ref>        Check if a ref is reviewed

Platform support:
    Windows : Windows Terminal (wt) > cmd.exe > PowerShell
    macOS   : Terminal.app via osascript
    Linux   : gnome-terminal > xterm > x-terminal-emulator
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError("Not a git repository")
    return Path(r.stdout.strip())


def _build_task_message(job: dict, root: Path) -> str:
    """Build the initial Claude message for the review session.

    The message tells Claude exactly what to do: run /wave-review on the
    specific pending job. The /wave-review skill handles multi-agent parallel
    review via Agent subagents and writes the receipt.
    """
    ref         = job.get("resolved_ref", "HEAD")
    review_type = job.get("review_type", "standard")
    pending     = job.get("_pending_path", "")
    diff_lines  = job.get("diff_lines", "?")

    return (
        f"WabbleSpec wave review task: process the pending review for commit {ref}. "
        f"The pending review file is at: {pending} "
        f"({diff_lines} diff lines, type={review_type}). "
        f"Run /wave-review to perform the review inline using the diff and prompt "
        f"template already in that file. Use parallel Agent subagents for each review "
        f"type (standard, security, design). Write the consolidated receipt via "
        f"receipt-writer.py --type wave-review and mark the job complete via "
        f"wave-review.py --complete {ref} --verdict <PASS|FAIL>. "
        f"Do not stop until the receipt is written and the job is marked complete."
    )


def _write_task_file(task: str, root: Path) -> Path:
    """Write the task to a file so the terminal command doesn't have to escape it."""
    task_dir = root / ".wabblespec" / "state" / "reviews" / "daemon"
    task_dir.mkdir(parents=True, exist_ok=True)
    task_file = task_dir / f"pending-task-{os.getpid()}.txt"
    task_file.write_text(task, encoding="utf-8")
    return task_file


# ---------------------------------------------------------------------------
# Terminal launchers per platform
# ---------------------------------------------------------------------------

def _launch_windows(cmd_args: list[str], title: str) -> subprocess.Popen | None:
    """Open a new visible terminal window on Windows."""
    # Try Windows Terminal first (modern, tabbed)
    if shutil.which("wt"):
        try:
            return subprocess.Popen(
                ["wt", "--title", title, "--"] + cmd_args,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        except Exception:
            pass

    # Fall back to cmd.exe with a new console window
    try:
        return subprocess.Popen(
            ["cmd", "/c", "start", f'"{title}"', "cmd", "/k"] + cmd_args,
            shell=False,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    except Exception:
        pass

    # PowerShell fallback
    ps_cmd = " ".join(f'"{a}"' if " " in str(a) else str(a) for a in cmd_args)
    try:
        return subprocess.Popen(
            ["powershell", "-Command",
             f"Start-Process powershell -ArgumentList '-NoExit -Command {ps_cmd}'"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    except Exception:
        return None


def _launch_macos(cmd_args: list[str], title: str) -> subprocess.Popen | None:
    cmd_str = " ".join(f'"{a}"' if " " in str(a) else str(a) for a in cmd_args)
    script  = f'tell app "Terminal" to do script "{cmd_str}"'
    try:
        return subprocess.Popen(["osascript", "-e", script])
    except Exception:
        return None


def _launch_linux(cmd_args: list[str], title: str) -> subprocess.Popen | None:
    for term in ("gnome-terminal", "xterm", "x-terminal-emulator", "konsole"):
        if not shutil.which(term):
            continue
        try:
            if term == "gnome-terminal":
                return subprocess.Popen(
                    ["gnome-terminal", "--title", title, "--"] + cmd_args
                )
            elif term in ("xterm", "x-terminal-emulator"):
                return subprocess.Popen(
                    [term, "-title", title, "-e"] + cmd_args
                )
            elif term == "konsole":
                return subprocess.Popen(
                    ["konsole", "--title", title, "-e"] + cmd_args
                )
        except Exception:
            continue
    return None


def _launch_terminal(root: Path, task_message: str, title: str) -> bool:
    """Open a new terminal window running claude with the given task message.

    The command is: claude "task message" --add-dir <root>
    This starts an interactive Claude Code session (subscription-billed, not API)
    with the task as the first user message.
    """
    if not shutil.which("claude"):
        print("ERROR: claude CLI not found in PATH", file=sys.stderr)
        return False

    # claude "task" --add-dir <root>  — interactive session, not headless
    claude_args = [
        "claude",
        task_message,
        "--add-dir", str(root),
    ]

    platform = sys.platform
    if platform == "win32":
        proc = _launch_windows(claude_args, title)
    elif platform == "darwin":
        proc = _launch_macos(claude_args, title)
    else:
        proc = _launch_linux(claude_args, title)

    if proc is None:
        # Last resort: same terminal in background (still interactive if TTY attached)
        try:
            proc = subprocess.Popen(claude_args, cwd=str(root),
                                    start_new_session=True)
        except Exception as exc:
            print(f"ERROR: could not launch terminal: {exc}", file=sys.stderr)
            return False

    print(f"Launched review session (pid={proc.pid}): {title}", flush=True)
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch a visible Claude Code terminal for wave review"
    )
    parser.add_argument("job_path", nargs="?", type=Path,
                        help="Path to pending review JSON")
    parser.add_argument("--check", metavar="REF",
                        help="Check if a ref has been reviewed (exit 0=yes, 1=no)")
    parser.add_argument("--no-wait", action="store_true",
                        help="Return immediately without polling for completion")
    parser.add_argument("--poll-timeout", type=int, default=600,
                        help="Seconds to poll for completion (default: 600)")
    args = parser.parse_args()

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # --check mode: look in DB for a reviewed entry
    if args.check:
        try:
            sys.path.insert(0, str(root / ".wabblespec" / "engine" / "shared" / "scripts"))
            import review_daemon as rd  # noqa: F401
            rows = rd._db_recent(root, 50)
            found = any(r["ref"] == args.check and r["status"] == "reviewed"
                        for r in rows)
            print("reviewed" if found else "pending")
            return 0 if found else 1
        except Exception:
            return 1

    if not args.job_path:
        parser.print_help()
        return 1

    # Load pending job
    try:
        job = json.loads(args.job_path.read_text(encoding="utf-8"))
        job["_pending_path"] = str(args.job_path)
    except Exception as exc:
        print(f"ERROR reading job file: {exc}", file=sys.stderr)
        return 2

    ref   = job.get("resolved_ref", "?")
    rtype = job.get("review_type", "standard")
    title = f"WabbleSpec Review: {ref} ({rtype})"

    task = _build_task_message(job, root)

    print(f"Opening review terminal for {ref}...", flush=True)
    ok = _launch_terminal(root, task, title)
    if not ok:
        return 2

    if args.no_wait:
        return 0

    # Poll for completion
    print(f"Waiting for review to complete (timeout={args.poll_timeout}s)...", flush=True)
    start  = time.monotonic()
    db_path = root / ".wabblespec" / "state" / "reviews" / "reviews.db"

    while time.monotonic() - start < args.poll_timeout:
        # Check if pending file has moved to completed/
        completed = root / ".wabblespec" / "state" / "reviews" / "completed" / args.job_path.name
        if completed.exists():
            print(f"Review complete: {ref}", flush=True)
            return 0
        # Also check DB if available
        if db_path.exists():
            try:
                import sqlite3
                con = sqlite3.connect(str(db_path), timeout=5)
                row = con.execute(
                    "SELECT verdict FROM reviews WHERE ref=? AND status='reviewed'",
                    (ref,)
                ).fetchone()
                con.close()
                if row:
                    print(f"Review complete: {ref} → {row[0]}", flush=True)
                    return 0 if row[0] == "PASS" else 1
            except Exception:
                pass
        time.sleep(10)

    print(f"Timeout waiting for {ref} — check the terminal window", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
