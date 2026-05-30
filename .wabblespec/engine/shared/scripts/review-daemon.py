#!/usr/bin/env python3
"""review-daemon.py — WabbleSpec autonomous background code reviewer.

Watches the pending review queue and for each job opens a new terminal window
running an interactive Claude Code session (`claude "task"` — subscription-
billed, not API-billed). Inside that session the /wave-review skill runs
parallel Agent subagents (standard + security + design), synthesizes findings,
and writes the wave-review receipt.

This is WabbleSpec's equivalent of roborev's multi-agent worker pool.

Usage:
    python review-daemon.py start           Start daemon in background
    python review-daemon.py run             Run in foreground (blocking)
    python review-daemon.py stop            Stop running daemon
    python review-daemon.py status          Status + queue stats
    python review-daemon.py dashboard       Live-refreshing terminal dashboard
    python review-daemon.py install-hook    Install git post-commit hook
    python review-daemon.py post-pr <ref>   Post findings to open GitHub PR

Environment:
    WABBLESPEC_REVIEW_POLL=15      Queue poll interval in seconds (default: 15)
    WABBLESPEC_REVIEW_TIMEOUT=600  Seconds to wait for a terminal session (default: 600)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

POLL_INTERVAL = int(os.environ.get("WABBLESPEC_REVIEW_POLL",    "15"))
SESSION_TIMEOUT = int(os.environ.get("WABBLESPEC_REVIEW_TIMEOUT", "600"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _short() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError("Not a git repository")
    return Path(r.stdout.strip())

def _review_dir(root: Path) -> Path:
    p = root / ".wabblespec" / "state" / "reviews"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _pending_dir(root: Path) -> Path:
    p = _review_dir(root) / "pending"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _completed_dir(root: Path) -> Path:
    p = _review_dir(root) / "completed"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _daemon_dir(root: Path) -> Path:
    p = _review_dir(root) / "daemon"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _scripts_dir(root: Path) -> Path:
    return root / ".wabblespec" / "engine" / "shared" / "scripts"

def _pid_path(root: Path) -> Path:
    return _daemon_dir(root) / "daemon.pid"

def _log_path(root: Path) -> Path:
    return _daemon_dir(root) / "daemon.log"


# ---------------------------------------------------------------------------
# SQLite queue — concurrent-safe, queryable
# ---------------------------------------------------------------------------

def _db_path(root: Path) -> Path:
    return _review_dir(root) / "reviews.db"

def _db_connect(root: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(_db_path(root)), timeout=10,
                          check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            ref            TEXT NOT NULL,
            review_type    TEXT NOT NULL DEFAULT 'multi',
            status         TEXT NOT NULL DEFAULT 'pending',
            verdict        TEXT,
            queued_at      TEXT NOT NULL,
            reviewed_at    TEXT,
            receipt_path   TEXT,
            pending_path   TEXT,
            finding_high   INTEGER DEFAULT 0,
            finding_medium INTEGER DEFAULT 0,
            finding_low    INTEGER DEFAULT 0,
            agent_verdicts TEXT
        )
    """)
    con.commit()
    return con

def _db_enqueue(root: Path, ref: str, pending_path: str) -> int:
    con = _db_connect(root)
    if con.execute("SELECT id FROM reviews WHERE ref=? AND status='pending'",
                   (ref,)).fetchone():
        con.close()
        return -1
    cur = con.execute(
        "INSERT INTO reviews (ref, queued_at, pending_path) VALUES (?,?,?)",
        (ref, _now(), pending_path)
    )
    con.commit()
    row_id = cur.lastrowid
    con.close()
    return row_id

def _db_claim_pending(root: Path) -> sqlite3.Row | None:
    con = _db_connect(root)
    row = con.execute(
        "SELECT * FROM reviews WHERE status='pending' ORDER BY id LIMIT 1"
    ).fetchone()
    if row:
        con.execute("UPDATE reviews SET status='running' WHERE id=?", (row["id"],))
        con.commit()
    con.close()
    return row

def _db_complete(root: Path, ref: str, verdict: str, receipt_path: str,
                 h: int = 0, m: int = 0, l: int = 0,
                 agent_verdicts: str = "{}") -> None:
    con = _db_connect(root)
    con.execute(
        """UPDATE reviews SET status='reviewed', verdict=?, reviewed_at=?,
           receipt_path=?, finding_high=?, finding_medium=?, finding_low=?,
           agent_verdicts=? WHERE ref=? AND status IN ('pending','running')""",
        (verdict, _now(), receipt_path, h, m, l, agent_verdicts, ref)
    )
    con.commit()
    con.close()

def _db_stats(root: Path) -> dict:
    if not _db_path(root).exists():
        return {}
    con = _db_connect(root)
    row = con.execute("""
        SELECT COUNT(*) as total,
            SUM(CASE WHEN status='pending'  THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status='running'  THEN 1 ELSE 0 END) as running,
            SUM(CASE WHEN status='reviewed' THEN 1 ELSE 0 END) as reviewed,
            SUM(CASE WHEN verdict='PASS'    THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN verdict='FAIL'    THEN 1 ELSE 0 END) as failed
        FROM reviews
    """).fetchone()
    con.close()
    return dict(row) if row else {}

def _db_recent(root: Path, n: int = 10) -> list[sqlite3.Row]:
    if not _db_path(root).exists():
        return []
    con = _db_connect(root)
    rows = con.execute(
        "SELECT * FROM reviews ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    con.close()
    return rows


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_foreground = False
_log_file   = None

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
# Job processor — delegates to review-terminal.py
# ---------------------------------------------------------------------------

def _process_job(root: Path, row: sqlite3.Row) -> None:
    ref          = row["ref"]
    pending_path = row["pending_path"] or ""

    if not pending_path or not Path(pending_path).exists():
        _log(f"pending file missing for {ref} — skipping")
        _db_complete(root, ref, "ERROR", "")
        return

    _log(f"dispatching review terminal for {ref}")

    launcher = _scripts_dir(root) / "review-terminal.py"
    if not launcher.exists():
        _log("ERROR: review-terminal.py not found")
        _db_complete(root, ref, "ERROR", "")
        return

    result = subprocess.run(
        [sys.executable, str(launcher), pending_path,
         "--poll-timeout", str(SESSION_TIMEOUT)],
        capture_output=True, text=True,
        timeout=SESSION_TIMEOUT + 30,
        cwd=str(root),
    )

    # The terminal session writes the DB entry directly via wave-review.py --complete.
    # If it completed correctly the DB entry is already updated.
    # If it timed out or errored, mark as error so the queue doesn't stall.
    if result.returncode == 2:
        _log(f"  terminal launch failed for {ref}: {result.stderr[:100]}")
        _db_complete(root, ref, "ERROR", "")
    else:
        # Verify DB was updated by the terminal session
        stats = _db_recent(root, 20)
        if not any(r["ref"] == ref and r["status"] == "reviewed" for r in stats):
            _log(f"  terminal session did not mark {ref} complete — marking ERROR")
            _db_complete(root, ref, "ERROR", "")
        else:
            _log(f"  {ref} reviewed by terminal session")


# ---------------------------------------------------------------------------
# Daemon loop
# ---------------------------------------------------------------------------

def _daemon_loop(root: Path) -> None:
    _log(f"daemon started pid={os.getpid()} poll={POLL_INTERVAL}s timeout={SESSION_TIMEOUT}s")

    while True:
        try:
            row = _db_claim_pending(root)
            if row:
                _process_job(root, row)
            else:
                time.sleep(POLL_INTERVAL)
        except Exception as exc:
            _log(f"loop error: {exc}")
            time.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# Daemon lifecycle
# ---------------------------------------------------------------------------

def cmd_run(root: Path) -> int:
    global _foreground, _log_file
    _foreground = True
    _log_file   = open(_log_path(root), "a", encoding="utf-8")
    _pid_path(root).write_text(str(os.getpid()), encoding="utf-8")

    def _stop(sig, frame):
        _log("stopping")
        _pid_path(root).unlink(missing_ok=True)
        _log_file.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    try:
        _daemon_loop(root)
    finally:
        _pid_path(root).unlink(missing_ok=True)
    return 0


def cmd_start(root: Path) -> int:
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
        stdout=log, stderr=log, start_new_session=True, cwd=str(root),
    )
    time.sleep(1)
    if pid_path.exists():
        print(f"Daemon started (pid={int(pid_path.read_text().strip())})"
              f"  log={_log_path(root)}")
    else:
        print(f"Spawned pid={proc.pid}  log={_log_path(root)}")
    return 0


def cmd_stop(root: Path) -> int:
    pid_path = _pid_path(root)
    if not pid_path.exists():
        print("Daemon not running")
        return 0
    try:
        pid = int(pid_path.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        pid_path.unlink(missing_ok=True)
        print(f"Stopped (pid={pid})")
    except ProcessLookupError:
        pid_path.unlink(missing_ok=True)
        print("Not running (stale PID removed)")
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


def cmd_status(root: Path) -> int:
    pid_path = _pid_path(root)
    running, pid = False, None
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            os.kill(pid, 0)
            running = True
        except (OSError, ValueError):
            pass

    print(f"Daemon : {'RUNNING' if running else 'STOPPED'}" +
          (f" (pid={pid})" if pid else ""))

    stats = _db_stats(root)
    if stats:
        print(f"Queue  : total={stats.get('total',0)}  "
              f"pending={stats.get('pending',0)}  "
              f"running={stats.get('running',0)}  "
              f"reviewed={stats.get('reviewed',0)}  "
              f"pass={stats.get('passed',0)}  "
              f"fail={stats.get('failed',0)}")

    recent = _db_recent(root, 5)
    if recent:
        print("\nRecent:")
        for r in recent:
            print(f"  {r['ref']:12s}  {r['status']:9s}  "
                  f"verdict={r['verdict'] or '-':5s}  "
                  f"H={r['finding_high']} M={r['finding_medium']} L={r['finding_low']}")

    log = _log_path(root)
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()
        if lines:
            print(f"\nLog:")
            for line in lines[-5:]:
                print(f"  {line}")

    return 0 if running else 1


def cmd_dashboard(root: Path) -> int:
    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print("=== WabbleSpec Wave Reviewer Dashboard ===\n")
            cmd_status(root)
            print("\nPending jobs:")
            for p in sorted(_pending_dir(root).glob("*.json"),
                            key=lambda f: f.stat().st_mtime):
                try:
                    j = json.loads(p.read_text(encoding="utf-8"))
                    print(f"  {j.get('resolved_ref','?'):12s}  "
                          f"{j.get('review_type','?'):10s}  "
                          f"{j.get('diff_lines','?')} lines")
                except Exception:
                    print(f"  {p.name}")
            print("\n[Ctrl-C to exit — refreshes every 5s]")
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    return 0


# ---------------------------------------------------------------------------
# GitHub PR posting
# ---------------------------------------------------------------------------

def cmd_post_pr(root: Path, ref: str) -> int:
    if not shutil.which("gh"):
        print("gh CLI not found — install GitHub CLI to use post-pr")
        return 1

    rows   = _db_recent(root, 50)
    row    = next((r for r in rows if r["ref"] == ref), None)
    if not row:
        print(f"No review found for {ref}")
        return 1

    verdict = row["verdict"] or "UNKNOWN"
    av      = json.loads(row["agent_verdicts"] or "{}")
    av_str  = ", ".join(f"{k}: {v}" for k, v in av.items())
    h, m, l = row["finding_high"] or 0, row["finding_medium"] or 0, row["finding_low"] or 0

    if verdict == "PASS" and h == 0 and m == 0 and l == 0:
        body = f"Wave review **PASS** for `{ref}` — no findings. [{av_str}]"
    else:
        body = (
            f"## Wave Review — {verdict}\n"
            f"**Agents:** {av_str}\n\n"
            f"| Severity | Count |\n|---|---|\n"
            f"| HIGH | {h} |\n| MEDIUM | {m} |\n| LOW | {l} |\n\n"
            f"Run `/wave-review` in your session to see full findings."
        )

    result = subprocess.run(
        ["gh", "pr", "comment", "--body", body],
        capture_output=True, text=True, check=False,
        timeout=30, cwd=str(root),
    )
    if result.returncode == 0:
        print(f"Posted review findings to open PR")
        return 0
    print(f"gh error: {result.stderr[:200]}")
    return 1


# ---------------------------------------------------------------------------
# Git hook installer
# ---------------------------------------------------------------------------

def cmd_install_hook(root: Path) -> int:
    hook   = root / ".git" / "hooks" / "post-commit"
    wrev   = _scripts_dir(root) / "wave-review.py"
    marker = "# WabbleSpec wave review"
    snippet = (
        f"\n{marker}\n"
        f'python "{wrev}" --enqueue HEAD 2>/dev/null &\n'
    )
    if hook.exists():
        existing = hook.read_text(encoding="utf-8")
        if marker in existing:
            print(f"Hook already installed: {hook}")
            return 0
        hook.write_text(existing.rstrip() + "\n" + snippet, encoding="utf-8")
    else:
        hook.write_text("#!/bin/sh" + snippet, encoding="utf-8")
    try:
        hook.chmod(0o755)
    except Exception:
        pass
    print(f"Post-commit hook installed: {hook}")
    print(f"Start daemon: python {Path(__file__).name} start")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="WabbleSpec autonomous review daemon"
    )
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("start",        help="Start daemon in background")
    sub.add_parser("stop",         help="Stop running daemon")
    sub.add_parser("status",       help="Show status and queue stats")
    sub.add_parser("dashboard",    help="Live-refreshing terminal dashboard")
    sub.add_parser("install-hook", help="Install git post-commit hook")

    p_run = sub.add_parser("run", help="Run in foreground (blocking)")
    p_run.add_argument("--root", type=Path, default=None)

    p_pr = sub.add_parser("post-pr", help="Post review to open GitHub PR")
    p_pr.add_argument("ref")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 1

    if args.cmd == "run" and getattr(args, "root", None):
        root = args.root
    else:
        try:
            root = _repo_root()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    dispatch = {
        "start":        lambda: cmd_start(root),
        "run":          lambda: cmd_run(root),
        "stop":         lambda: cmd_stop(root),
        "status":       lambda: cmd_status(root),
        "dashboard":    lambda: cmd_dashboard(root),
        "install-hook": lambda: cmd_install_hook(root),
        "post-pr":      lambda: cmd_post_pr(root, args.ref),
    }
    return dispatch[args.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
