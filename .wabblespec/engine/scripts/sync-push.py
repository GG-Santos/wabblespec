#!/usr/bin/env python3
"""sync-push.py — Stop-time cross-device state push.

Commits any changed .wabblespec/ files (excluding session/) and pushes
to the git remote so other devices can pull the latest receipts, memory,
VERSION, and CHANGELOG.

Silent-fail contract: exits 0 in all cases. Failures are logged to
.wabblespec/engine/shared/logs/sync.log but never surface as Stop hook errors.

Called by: scripts/stop-hook.py  Step 3 (after Dream).
"""
from __future__ import annotations

import datetime
import socket
import subprocess
import sys
from pathlib import Path


# ── Repo detection ─────────────────────────────────────────────────────────────

def _repo_root() -> Path | None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            return parent
    return None


ROOT = _repo_root()


# ── Logging ────────────────────────────────────────────────────────────────────

def _log(msg: str) -> None:
    if ROOT is None:
        return
    log_dir = ROOT / ".wabblespec" / "state" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "sync.log"
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    host = socket.gethostname()
    entry = f"[{ts}] [{host}] [push] {msg}\n"
    try:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError:
        pass


# ── Git helpers ────────────────────────────────────────────────────────────────

def _git(*args: str, cwd: Path, timeout: int = 20) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"
    except FileNotFoundError:
        return 1, "", "git not found"
    except Exception as exc:  # noqa: BLE001
        return 1, "", str(exc)


def _has_remote(root: Path) -> bool:
    rc, out, _ = _git("remote", cwd=root)
    return rc == 0 and bool(out.strip())


def _current_branch(root: Path) -> str:
    rc, out, _ = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    if rc == 0 and out:
        return out
    return "main"


def _changed_wabblespec_files(root: Path) -> list[str]:
    """Return list of .wabblespec/ files that differ from HEAD."""
    rc, out, _ = _git(
        "diff", "--name-only", "HEAD", "--", ".wabblespec/",
        cwd=root,
    )
    if rc != 0 or not out:
        return []
    return [p for p in out.splitlines() if p]


def _untracked_wabblespec_files(root: Path) -> list[str]:
    """Return untracked .wabblespec/ files (new receipts, new drawers, etc.)."""
    rc, out, _ = _git(
        "ls-files", "--others", "--exclude-standard", ".wabblespec/",
        cwd=root,
    )
    if rc != 0 or not out:
        return []
    return [p for p in out.splitlines() if p]


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    if ROOT is None:
        return 0

    if not _has_remote(ROOT):
        _log("no remote configured — skipping push")
        return 0

    # Collect changed + untracked .wabblespec/ files
    changed = _changed_wabblespec_files(ROOT)
    untracked = _untracked_wabblespec_files(ROOT)
    all_changed = changed + untracked

    if not all_changed:
        _log("no .wabblespec/ changes — nothing to push")
        return 0

    _log(f"{len(all_changed)} file(s) changed: {', '.join(all_changed[:5])}"
         + (" ..." if len(all_changed) > 5 else ""))

    # Stage all .wabblespec/ changes
    rc, _, err = _git("add", ".wabblespec/", cwd=ROOT)
    if rc != 0:
        _log(f"git add failed: {err}")
        return 0

    # Unstage session/ — machine-specific state must not propagate
    _git("restore", "--staged", ".wabblespec/session/", cwd=ROOT)

    # Check if anything remains staged
    rc, staged, _ = _git("diff", "--cached", "--name-only", "--", ".wabblespec/", cwd=ROOT)
    if rc != 0 or not staged.strip():
        _log("nothing staged after excluding session/ — skipping commit")
        return 0

    # Build commit message
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    host = socket.gethostname()
    commit_msg = f"wabblespec: sync {host} {ts}"

    rc, _, err = _git("commit", "-m", commit_msg, cwd=ROOT)
    if rc != 0:
        _log(f"commit failed: {err[:200]}")
        # Unstage so we don't leave the index dirty
        _git("reset", "HEAD", ".wabblespec/", cwd=ROOT)
        return 0

    _log(f"committed: {commit_msg}")

    # Push
    branch = _current_branch(ROOT)
    rc, out, err = _git("push", "origin", branch, cwd=ROOT, timeout=30)
    if rc != 0:
        _log(f"push failed (will retry next session): {err[:200]}")
        # Leave the commit in place — it will be pushed next time
    else:
        _log(f"pushed to origin/{branch}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
