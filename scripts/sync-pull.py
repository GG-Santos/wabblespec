#!/usr/bin/env python3
"""sync-pull.py — SessionStart cross-device state pull.

Fetches the latest .wabblespec/ state from the git remote so work
accumulated on another device is available at session open.

Silent-fail contract: exits 0 in all cases. Failures are logged to
_shared/logs/sync.log but never surface as hook errors.

Called by: .claude/settings.json  SessionStart hook (runs before
           wabblespec-session-start.js so session state is current).
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
    log_dir = ROOT / "_shared" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "sync.log"
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    host = socket.gethostname()
    entry = f"[{ts}] [{host}] [pull] {msg}\n"
    try:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError:
        pass  # log failure is never fatal


# ── Git helpers ────────────────────────────────────────────────────────────────

def _git(*args: str, cwd: Path, timeout: int = 20) -> tuple[int, str, str]:
    """Run a git command. Returns (returncode, stdout, stderr)."""
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


def _conflicted_files(root: Path) -> list[Path]:
    """Return paths of files with unresolved conflict markers."""
    rc, out, _ = _git("diff", "--name-only", "--diff-filter=U", cwd=root)
    if rc != 0 or not out:
        return []
    return [root / p for p in out.splitlines() if p]


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    if ROOT is None:
        return 0

    if not _has_remote(ROOT):
        _log("no remote configured — skipping pull")
        return 0

    branch = _current_branch(ROOT)

    # Fetch
    rc, _, err = _git("fetch", "origin", branch, cwd=ROOT, timeout=25)
    if rc != 0:
        _log(f"fetch failed: {err}")
        return 0  # network unavailable or no remote — not fatal

    # Check if remote has anything new
    rc, ahead_behind, _ = _git(
        "rev-list", "--left-right", "--count",
        f"HEAD...origin/{branch}",
        cwd=ROOT,
    )
    if rc == 0 and ahead_behind:
        parts = ahead_behind.split()
        if len(parts) == 2 and parts[1] == "0":
            _log("already up to date")
            return 0

    # Rebase with autostash so local working-tree dirt is preserved
    rc, out, err = _git(
        "rebase", "--autostash", f"origin/{branch}",
        cwd=ROOT, timeout=30,
    )

    if rc == 0:
        _log(f"rebase ok: {out[:120] if out else 'clean'}")
        return 0

    # Rebase left conflicts — resolve them then continue
    conflicts = _conflicted_files(ROOT)
    if not conflicts:
        # Something else went wrong; abort the rebase cleanly
        _git("rebase", "--abort", cwd=ROOT)
        _log(f"rebase failed (no conflicts found): {err[:200]}")
        return 0

    _log(f"conflicts in {len(conflicts)} file(s); running sync-merge")

    merge_script = ROOT / "scripts" / "sync-merge.py"
    all_resolved = True

    for cf in conflicts:
        try:
            result = subprocess.run(
                [sys.executable, str(merge_script), str(cf)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                _log(f"sync-merge failed for {cf.name}: {result.stderr[:120]}")
                all_resolved = False
            else:
                _log(f"resolved: {cf.name}")
        except Exception as exc:  # noqa: BLE001
            _log(f"sync-merge error for {cf.name}: {exc}")
            all_resolved = False

    if all_resolved:
        rc, out, err = _git("rebase", "--continue", cwd=ROOT, timeout=20)
        if rc != 0:
            _log(f"rebase --continue failed: {err[:200]}")
            _git("rebase", "--abort", cwd=ROOT)
    else:
        _log("not all conflicts resolved — aborting rebase")
        _git("rebase", "--abort", cwd=ROOT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
