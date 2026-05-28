#!/usr/bin/env python3
"""Stop hook: bootstrap memory then run Dream.

Replaces the shell && chain in .claude/settings.json so that:
  - Each step has independent error handling (Dream still runs even if
    memory-bootstrap emits a warning).
  - No shell-specific && syntax is needed (works on cmd.exe, PowerShell,
    and bash without any assumption about the invoking shell).
  - A single process timeout covers both steps with room for ChromaDB
    model initialization on first run.

Exit codes:
  0  both steps succeeded (or Dream was skipped due to missing backend)
  1  memory bootstrap failed hard (Dream is still attempted)
  2  Dream failed
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            return parent
    raise RuntimeError(f"Cannot find WabbleSpec repo root above {here}")


def _run(script: Path, *, timeout: int, label: str, extra_args: list = None) -> int:
    """Run a Python script in a subprocess. Returns the exit code."""
    cmd = [sys.executable, str(script)] + (extra_args or [])
    try:
        result = subprocess.run(cmd, timeout=timeout, check=False)
        return result.returncode
    except subprocess.TimeoutExpired:
        print(f"[stop-hook] WARNING: {label} timed out after {timeout}s", flush=True)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"[stop-hook] ERROR: {label} failed to launch: {exc}", flush=True)
        return 1


def _archived_this_session(root: Path) -> bool:
    """Return True if a delivery receipt was written during this session."""
    import json as _json
    receipts_dir = root / ".wabblespec" / "state" / "receipts"
    state_file = root / ".wabblespec" / "state" / "session" / "state.json"
    if not state_file.exists():
        return False
    try:
        state = _json.loads(state_file.read_text(encoding="utf-8"))
        session_id = state.get("session_id", "")
        if not session_id:
            return False
        receipt = receipts_dir / f"delivery-receipt-{session_id}.json"
        return receipt.exists()
    except Exception:
        return False


def _run_daemons(root: Path, trigger: str) -> None:
    """Read daemon-config.json and run all enabled daemons for the given trigger. Silent-fail."""
    import json as _json
    config_path = root / ".wabblespec" / "state" / "daemons" / "daemon-config.json"
    if not config_path.exists():
        return
    try:
        config = _json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return
    for daemon in config.get("daemons", []):
        if not daemon.get("enabled", False):
            continue
        if daemon.get("trigger") != trigger:
            continue
        script_rel = daemon.get("script", "")
        # skip dream — already handled in main()
        if "dream" in script_rel:
            continue
        script = root / script_rel
        if not script.exists():
            print(f"[stop-hook] daemon '{daemon['id']}': script not found — skipping", flush=True)
            continue
        timeout = daemon.get("timeout_seconds", 60)
        extra_args = daemon.get("args", [])
        _run(script, timeout=timeout, label=f"daemon:{daemon['id']}", extra_args=extra_args)


def main() -> int:
    root = _repo_root()

    engine = root / ".wabblespec" / "engine"

    # Step 1: memory bootstrap (sets WABBLESPEC_MEMORY_PATH for Dream)
    bootstrap_script = engine / "scripts" / "memory-bootstrap.py"
    rc1 = _run(bootstrap_script, timeout=60, label="memory-bootstrap")
    if rc1 != 0:
        print(
            f"[stop-hook] WARNING: memory-bootstrap exited {rc1}; "
            "Dream will still run but memory env vars may be missing.",
            flush=True,
        )

    # Step 2: Dream (EMA decay + gap-map + staleness-map)
    dream_script = engine / "modules" / "l5" / "dream" / "scripts" / "dream.py"
    if not dream_script.exists():
        print(f"[stop-hook] WARNING: Dream script not found at {dream_script}", flush=True)
        return rc1

    rc2 = _run(dream_script, timeout=60, label="dream")
    if rc2 != 0:
        print(f"[stop-hook] ERROR: dream exited {rc2}", flush=True)

    # Step 3: daemon-driven background tasks
    # on_stop daemons run every session end
    _run_daemons(root, "on_stop")
    # on_archive daemons run only when a delivery receipt was written this session
    if _archived_this_session(root):
        _run_daemons(root, "on_archive")

    # Step 4: sync push — commit + push .wabblespec/ changes to remote
    # Non-blocking: push failure never fails the Stop hook (silent-fail contract)
    sync_push_script = engine / "scripts" / "sync-push.py"
    if sync_push_script.exists():
        _run(sync_push_script, timeout=30, label="sync-push")

    if rc2 != 0:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
