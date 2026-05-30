#!/usr/bin/env python3
"""review-daemon.py — WabbleSpec autonomous background code reviewer.

A long-running daemon that watches the pending review queue and processes
each job by spawning a headless Claude Code session (`claude --print`).
Equivalent to roborev's worker pool, implemented in Python with no external
binary dependency beyond the claude CLI already present in the environment.

The daemon is a separate OS process — it has no relationship to any running
Claude Code interactive session. It is started once and runs continuously.

Usage:
    python review-daemon.py start        Start daemon in background (writes PID file)
    python review-daemon.py run          Run in foreground (blocking)
    python review-daemon.py stop         Stop running daemon
    python review-daemon.py status       Show daemon status and queue stats
    python review-daemon.py install-hook Install git post-commit hook in current repo

Architecture:
    post-commit hook
        → wave-review.py --enqueue HEAD   (pure Python, no AI, <10ms)
        ↓
    review-daemon.py (always running)
        watches .wabblespec/state/reviews/pending/
        → for each pending job:
            → reads diff + template from pending JSON
            → spawns: claude --print "<review prompt>"
            → parses PASS/FAIL + findings (HIGH→MEDIUM→LOW)
            → writes wave-review receipt via receipt-writer.py
            → marks job complete via wave-review.py --complete
            → retry up to 3× on failure
        → sleeps POLL_INTERVAL seconds, loops

Configuration (environment variables):
    WABBLESPEC_REVIEW_POLL=15        Seconds between queue polls (default: 15)
    WABBLESPEC_REVIEW_RETRY=3        Max retries per job (default: 3)
    WABBLESPEC_REVIEW_TIMEOUT=180    Seconds before claude --print times out (default: 180)
    WABBLESPEC_REVIEW_MAX_JOBS=4     Max concurrent review jobs (default: 1, serial)

Exit codes:
    0  clean stop
    1  startup error
    2  fatal error during run
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants (overridable via env)
# ---------------------------------------------------------------------------

POLL_INTERVAL = int(os.environ.get("WABBLESPEC_REVIEW_POLL", "15"))
MAX_RETRY = int(os.environ.get("WABBLESPEC_REVIEW_RETRY", "3"))
AGENT_TIMEOUT = int(os.environ.get("WABBLESPEC_REVIEW_TIMEOUT", "180"))
DAEMON_LABEL = "wabblespec-wave-reviewer"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _short() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


# ---------------------------------------------------------------------------
# Repo / path resolution
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    import subprocess as sp
    r = sp.run(["git", "rev-parse", "--show-toplevel"],
               capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError("Not a git repository")
    return Path(r.stdout.strip())


def _daemon_dir(root: Path) -> Path:
    p = root / ".wabblespec" / "state" / "reviews" / "daemon"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _pid_path(root: Path) -> Path:
    return _daemon_dir(root) / "daemon.pid"


def _log_path(root: Path) -> Path:
    return _daemon_dir(root) / "daemon.log"


def _pending_dir(root: Path) -> Path:
    return root / ".wabblespec" / "state" / "reviews" / "pending"


def _scripts_dir(root: Path) -> Path:
    return root / ".wabblespec" / "engine" / "shared" / "scripts"


# ---------------------------------------------------------------------------
# Logging (append to daemon.log, also stdout when in foreground)
# ---------------------------------------------------------------------------

_foreground = False
_log_file = None


def _log(msg: str) -> None:
    line = f"[{_now()}] {msg}"
    if _foreground:
        print(line, flush=True)
    if _log_file:
        try:
            _log_file.write(line + "\n")
            _log_file.flush()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Agent invocation (the core: claude --print)
# ---------------------------------------------------------------------------

def _build_review_prompt(job: dict) -> str:
    """Build the full review prompt from a pending job JSON."""
    template = job.get("review_prompt_template", "Review the following code changes.")
    commit_info = job.get("commit_info", "")
    diff = job.get("diff", "")
    goal = job.get("task_goal", "")
    guidelines = job.get("review_guidelines_excerpt", "")

    parts = [template]
    if guidelines:
        parts.append(f"\n---\n## Project review guidelines\n{guidelines}")
    if goal:
        parts.append(f"\n---\n## Active task context\n{goal}")
    if commit_info:
        parts.append(f"\n---\n## Commit\n{commit_info}")
    parts.append(f"\n---\n## Diff\n```diff\n{diff}\n```")
    parts.append(
        "\n---\nRespond with:\n"
        "**VERDICT:** PASS or FAIL\n"
        "**FINDINGS:** Each finding on its own line: "
        "[HIGH|MEDIUM|LOW] file:line — description — suggested fix\n"
        "**NO FINDINGS:** (if nothing found)"
    )
    return "\n".join(parts)


def _call_claude(prompt: str, timeout: int) -> tuple[int, str]:
    """Spawn claude --print as a subprocess. Returns (exit_code, output)."""
    if not shutil.which("claude"):
        return 2, "claude CLI not found in PATH"

    # Write prompt to temp file to avoid shell metacharacter injection
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        result = subprocess.run(
            ["claude", "--print", f"$(cat '{prompt_file}')"],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        # Try direct stdin if shell substitution fails
        if result.returncode != 0 or not result.stdout:
            result = subprocess.run(
                ["claude", "--print"],
                input=prompt.encode("utf-8"),
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
        stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
        return result.returncode, (stdout + stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, f"[timeout after {timeout}s]"
    except Exception as exc:
        return 2, str(exc)
    finally:
        try:
            os.unlink(prompt_file)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Verdict parsing (identical to wave-review.py logic)
# ---------------------------------------------------------------------------

def _parse_verdict(output: str) -> tuple[str, list[dict]]:
    upper = output.upper()
    verdict = "FAIL"
    if "VERDICT: PASS" in upper or "**VERDICT:** PASS" in upper:
        verdict = "PASS"
    elif "NO FINDINGS" in upper and "VERDICT" not in upper:
        verdict = "PASS"
    elif "VERDICT: FAIL" in upper or "**VERDICT:** FAIL" in upper:
        verdict = "FAIL"

    findings = []
    for line in output.splitlines():
        s = line.strip()
        for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            if (s.upper().startswith(f"[{sev}]") or
                    s.upper().startswith(f"- {sev}") or
                    f"**{sev}**" in s.upper()):
                findings.append({
                    "severity": sev,
                    "description": s[:300],
                    "location": "",
                })
                break

    # Sort HIGH → MEDIUM → LOW
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings.sort(key=lambda f: order.get(f["severity"], 3))
    return verdict, findings


# ---------------------------------------------------------------------------
# Receipt write
# ---------------------------------------------------------------------------

def _write_receipt(root: Path, job: dict, verdict: str,
                   findings: list[dict], output_excerpt: str) -> Path | None:
    rw = _scripts_dir(root) / "receipt-writer.py"
    if not rw.exists():
        return None

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        counts[f.get("severity", "LOW")] += 1

    ref = job.get("resolved_ref", "unknown")
    review_type = job.get("review_type", "standard")
    ts = _short()
    out_path = (
        root / ".wabblespec" / "state" / "receipts" /
        f"wave-review-{ref}-{review_type}-{ts}.json"
    )

    result = subprocess.run(
        [
            sys.executable, str(rw),
            "--type", "wave-review",
            "--task-id", job.get("task_id") or f"wave-review-{ref}",
            "--session-id", job.get("session_id") or f"daemon-{ts}",
            "--status", "PASS" if verdict == "PASS" else "FAIL",
            "--target", ref,
            "--summary", f"{verdict}: {len(findings)} findings ({counts['HIGH']} HIGH, {counts['MEDIUM']} MEDIUM, {counts['LOW']} LOW)",
            "--confidence", "0.85",
            "--out", str(out_path),
        ],
        capture_output=True, check=False, timeout=30,
        cwd=str(root),
    )
    if result.returncode == 0:
        return out_path
    _log(f"  receipt-writer error: {result.stderr.decode('utf-8', errors='replace')[:200]}")
    return None


# ---------------------------------------------------------------------------
# Single job processor
# ---------------------------------------------------------------------------

def _process_job(root: Path, pending_path: Path) -> bool:
    """Process one pending review job. Returns True on success."""
    try:
        job = json.loads(pending_path.read_text(encoding="utf-8"))
    except Exception as exc:
        _log(f"  ERROR reading {pending_path.name}: {exc}")
        return False

    ref = job.get("resolved_ref", pending_path.stem)
    review_type = job.get("review_type", "standard")
    _log(f"reviewing {ref} ({review_type}, {job.get('diff_lines', '?')} diff lines)")

    prompt = _build_review_prompt(job)

    for attempt in range(1, MAX_RETRY + 1):
        if attempt > 1:
            _log(f"  retry {attempt}/{MAX_RETRY}")
            time.sleep(5 * attempt)

        rc, output = _call_claude(prompt, AGENT_TIMEOUT)

        if rc == 2:
            _log(f"  ERROR: agent unavailable: {output[:100]}")
            return False  # non-retryable

        if not output.strip():
            _log(f"  WARNING: empty output (attempt {attempt})")
            continue

        verdict, findings = _parse_verdict(output)
        _log(f"  verdict={verdict} findings={len(findings)}")

        receipt_path = _write_receipt(root, job, verdict, findings, output[:500])

        # Mark complete via wave-review.py --complete
        wrev = _scripts_dir(root) / "wave-review.py"
        if wrev.exists():
            subprocess.run(
                [sys.executable, str(wrev),
                 "--complete", ref,
                 "--verdict", verdict,
                 "--receipt", str(receipt_path or "")],
                capture_output=True, check=False, timeout=15,
                cwd=str(root),
            )

        # Move pending file to completed
        completed = root / ".wabblespec" / "state" / "reviews" / "completed"
        completed.mkdir(parents=True, exist_ok=True)
        try:
            pending_path.rename(completed / pending_path.name)
        except Exception:
            pass

        _log(f"  done: {ref} → {verdict}")
        return True

    _log(f"  FAILED after {MAX_RETRY} attempts: {ref}")
    return False


# ---------------------------------------------------------------------------
# Main daemon loop
# ---------------------------------------------------------------------------

def _daemon_loop(root: Path) -> None:
    pending_dir = _pending_dir(root)
    pending_dir.mkdir(parents=True, exist_ok=True)

    _log(f"daemon started (pid={os.getpid()}, poll={POLL_INTERVAL}s, retry={MAX_RETRY}x, timeout={AGENT_TIMEOUT}s)")
    _log(f"watching {pending_dir}")

    while True:
        try:
            jobs = sorted(pending_dir.glob("*.json"),
                          key=lambda p: p.stat().st_mtime)
            for job_path in jobs:
                _process_job(root, job_path)
        except Exception as exc:
            _log(f"loop error: {exc}")

        time.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# Daemon lifecycle commands
# ---------------------------------------------------------------------------

def cmd_run(root: Path, foreground: bool) -> int:
    global _foreground, _log_file

    if not shutil.which("claude"):
        print("ERROR: claude CLI not found in PATH — daemon cannot review without it", file=sys.stderr)
        return 1

    if not foreground:
        # Daemonise: fork and write PID
        pid = os.getpid()
        pid_path = _pid_path(root)
        pid_path.write_text(str(pid), encoding="utf-8")
        _foreground = False
        _log_file = open(_log_path(root), "a", encoding="utf-8")
    else:
        _foreground = True
        _log_file = open(_log_path(root), "a", encoding="utf-8")
        _pid_path(root).write_text(str(os.getpid()), encoding="utf-8")

    def _handle_stop(signum, frame):
        _log("received stop signal — shutting down")
        _pid_path(root).unlink(missing_ok=True)
        if _log_file:
            _log_file.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    try:
        _daemon_loop(root)
    except KeyboardInterrupt:
        _log("interrupted")
    finally:
        _pid_path(root).unlink(missing_ok=True)
        if _log_file:
            _log_file.close()
    return 0


def cmd_start(root: Path) -> int:
    """Start daemon in background using subprocess."""
    pid_path = _pid_path(root)
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            os.kill(pid, 0)
            print(f"Daemon already running (pid={pid})")
            return 0
        except (OSError, ValueError):
            pid_path.unlink(missing_ok=True)

    log = open(_log_path(root), "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, __file__, "run", "--root", str(root)],
        stdout=log, stderr=log,
        start_new_session=True,
        cwd=str(root),
    )
    time.sleep(1)  # Give daemon a moment to write PID file
    pid_path = _pid_path(root)
    if pid_path.exists():
        pid = int(pid_path.read_text().strip())
        print(f"Daemon started (pid={pid})")
        print(f"Log: {_log_path(root)}")
    else:
        print(f"Daemon process spawned (pid={proc.pid}) — check log for status")
        print(f"Log: {_log_path(root)}")
    return 0


def cmd_stop(root: Path) -> int:
    pid_path = _pid_path(root)
    if not pid_path.exists():
        print("Daemon not running (no PID file)")
        return 0
    try:
        pid = int(pid_path.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        pid_path.unlink(missing_ok=True)
        print(f"Daemon stopped (pid={pid})")
        return 0
    except ProcessLookupError:
        pid_path.unlink(missing_ok=True)
        print("Daemon was not running (stale PID file removed)")
        return 0
    except Exception as exc:
        print(f"ERROR stopping daemon: {exc}")
        return 1


def cmd_status(root: Path) -> int:
    pid_path = _pid_path(root)
    running = False
    pid = None

    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            os.kill(pid, 0)
            running = True
        except (OSError, ValueError):
            pass

    print(f"Daemon: {'RUNNING' if running else 'STOPPED'}" +
          (f" (pid={pid})" if running else ""))
    if not running and pid:
        print("  (stale PID file — daemon may have crashed; check log)")

    # Queue stats
    wrev = _scripts_dir(root) / "wave-review.py"
    if wrev.exists():
        result = subprocess.run(
            [sys.executable, str(wrev), "stats"],
            capture_output=True, text=True, check=False, timeout=10,
            cwd=str(root),
        )
        if result.stdout:
            print(f"Queue: {result.stdout.strip()}")

    # Pending jobs
    pending = list(_pending_dir(root).glob("*.json")) if _pending_dir(root).exists() else []
    print(f"Pending reviews: {len(pending)}")
    for p in pending[:5]:
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            print(f"  {j.get('resolved_ref','?'):12s}  {j.get('review_type','?'):10s}  {j.get('queued_at','')}")
        except Exception:
            print(f"  {p.name}")

    # Last log lines
    log = _log_path(root)
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()
        if lines:
            print(f"\nLast log entries ({log}):")
            for line in lines[-8:]:
                print(f"  {line}")

    return 0 if running else 1


# ---------------------------------------------------------------------------
# Git post-commit hook installer
# ---------------------------------------------------------------------------

def cmd_install_hook(root: Path) -> int:
    hook_path = root / ".git" / "hooks" / "post-commit"
    wave_review = _scripts_dir(root) / "wave-review.py"

    hook_content = f"""#!/bin/sh
# WabbleSpec wave review — enqueue HEAD for background review
# Installed by review-daemon.py --install-hook
python "{wave_review}" --enqueue HEAD --type standard 2>/dev/null &
"""

    marker = "# WabbleSpec wave review"
    if hook_path.exists():
        existing = hook_path.read_text(encoding="utf-8")
        if marker in existing:
            print(f"Hook already installed at {hook_path}")
            return 0
        # Append to existing hook
        hook_path.write_text(
            existing.rstrip() + "\n\n" + hook_content,
            encoding="utf-8"
        )
    else:
        hook_path.write_text(hook_content, encoding="utf-8")

    # Make executable (Unix)
    try:
        hook_path.chmod(0o755)
    except Exception:
        pass

    print(f"Post-commit hook installed: {hook_path}")
    print("Every git commit will now enqueue HEAD for background review.")
    print(f"Start the daemon: python {__file__} start")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="WabbleSpec autonomous background code reviewer"
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("start", help="Start daemon in background")
    sub.add_parser("stop", help="Stop running daemon")
    sub.add_parser("status", help="Show daemon status and queue stats")

    p_run = sub.add_parser("run", help="Run in foreground (blocking)")
    p_run.add_argument("--root", type=Path, default=None,
                       help="Repo root (auto-detected if omitted)")

    sub.add_parser("install-hook", help="Install git post-commit hook")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return 1

    if args.cmd == "run" and args.root:
        root = args.root
    else:
        try:
            root = _repo_root()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    if args.cmd == "start":
        return cmd_start(root)
    elif args.cmd == "run":
        return cmd_run(root, foreground=True)
    elif args.cmd == "stop":
        return cmd_stop(root)
    elif args.cmd == "status":
        return cmd_status(root)
    elif args.cmd == "install-hook":
        return cmd_install_hook(root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
