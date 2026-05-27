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


def _run(script: Path, *, timeout: int, label: str) -> int:
    """Run a Python script in a subprocess. Returns the exit code."""
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            timeout=timeout,
            check=False,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        print(f"[stop-hook] WARNING: {label} timed out after {timeout}s", flush=True)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"[stop-hook] ERROR: {label} failed to launch: {exc}", flush=True)
        return 1


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
        # Do not return yet — sync push should still fire

    # Step 3: sync push — commit + push .wabblespec/ changes to remote
    # Non-blocking: push failure never fails the Stop hook (silent-fail contract)
    sync_push_script = engine / "scripts" / "sync-push.py"
    if sync_push_script.exists():
        _run(sync_push_script, timeout=30, label="sync-push")

    if rc2 != 0:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
