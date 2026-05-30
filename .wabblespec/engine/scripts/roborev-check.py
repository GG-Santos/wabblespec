#!/usr/bin/env python3
"""roborev-check.py — Post-archive code review trigger.

Runs as an on_archive daemon. Checks whether roborev is installed, ensures
the daemon is running, then triggers a review of the most recent commit (HEAD).

Silent-fail contract: this script NEVER exits non-zero. A missing roborev binary,
a failed review, or a daemon start failure are all logged and swallowed. The
WabbleSpec stop-hook must not be interrupted by review infrastructure.

Usage:
    python roborev-check.py [--wait] [--output <path>]

    --wait     Block until the review completes and print the verdict (default: fire-and-forget)
    --output   Write verdict JSON to this path (default: .wabblespec/state/daemons/roborev-last.json)
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            return parent
    raise RuntimeError(f"Cannot find WabbleSpec repo root above {here}")


def _roborev_available() -> bool:
    return shutil.which("roborev") is not None


def _run(args: list[str], *, timeout: int = 60, cwd: Path | None = None) -> tuple[int, str]:
    """Run a command. Returns (exit_code, stdout+stderr combined)."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode, output.strip()
    except subprocess.TimeoutExpired:
        return 1, f"[roborev-check] timed out after {timeout}s"
    except Exception as exc:  # noqa: BLE001
        return 1, f"[roborev-check] failed to launch: {exc}"


def _daemon_running(root: Path) -> bool:
    """Check if the roborev daemon is running via `roborev status`."""
    rc, output = _run(["roborev", "status"], timeout=5, cwd=root)
    return rc == 0 and "running" in output.lower()


def _ensure_daemon(root: Path) -> bool:
    """Start the daemon in the background if not already running. Returns True if running."""
    if _daemon_running(root):
        return True
    print("[roborev-check] daemon not running — starting in background", flush=True)
    try:
        subprocess.Popen(
            ["roborev", "daemon", "run"],
            cwd=str(root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        # Give the daemon a moment to bind its port
        time.sleep(2)
        return _daemon_running(root)
    except Exception as exc:  # noqa: BLE001
        print(f"[roborev-check] could not start daemon: {exc}", flush=True)
        return False


def _head_sha(root: Path) -> str | None:
    rc, output = _run(["git", "rev-parse", "HEAD"], timeout=10, cwd=root)
    return output.strip() if rc == 0 and output.strip() else None


def main() -> int:  # always returns 0 — silent-fail contract
    parser = argparse.ArgumentParser(description="roborev post-archive review trigger")
    parser.add_argument("--wait", action="store_true", default=True,
                        help="Block until review completes (default: True for archive trigger)")
    parser.add_argument("--no-wait", action="store_true",
                        help="Fire-and-forget mode (overrides --wait)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Write verdict JSON to this path")
    args = parser.parse_args()
    wait = args.wait and not args.no_wait

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"[roborev-check] {exc} — skipping", flush=True)
        return 0

    output_path = args.output or (
        root / ".wabblespec" / "state" / "daemons" / "roborev-last.json"
    )

    if not _roborev_available():
        print(
            "[roborev-check] roborev not found in PATH — skipping.\n"
            "  Install: powershell -ExecutionPolicy ByPass -c "
            "\"irm https://roborev.io/install.ps1 | iex\"\n"
            "  Then run: roborev init",
            flush=True,
        )
        _write_result(output_path, {
            "status": "skipped",
            "reason": "roborev not installed",
            "install_hint": "powershell -ExecutionPolicy ByPass -c \"irm https://roborev.io/install.ps1 | iex\"",
        })
        return 0

    # Ensure the daemon is running before queuing a review
    if not _ensure_daemon(root):
        print("[roborev-check] daemon could not be started — skipping review", flush=True)
        _write_result(output_path, {"status": "skipped", "reason": "daemon failed to start"})
        return 0

    sha = _head_sha(root)
    if not sha:
        print("[roborev-check] could not resolve HEAD SHA — skipping", flush=True)
        _write_result(output_path, {"status": "skipped", "reason": "HEAD SHA unavailable"})
        return 0

    print(f"[roborev-check] queuing review for HEAD ({sha[:8]})", flush=True)

    cmd = ["roborev", "review", "HEAD"]
    if wait:
        cmd.append("--wait")

    rc, output = _run(cmd, timeout=300, cwd=root)

    verdict = "pass" if rc == 0 else "fail"
    print(f"[roborev-check] review {verdict} (exit {rc})", flush=True)
    if output:
        # Print first 20 lines of review output so it surfaces in stop-hook logs
        lines = output.splitlines()
        for line in lines[:20]:
            print(f"  {line}", flush=True)
        if len(lines) > 20:
            print(f"  ... ({len(lines) - 20} more lines)", flush=True)

    _write_result(output_path, {
        "status": verdict,
        "sha": sha,
        "exit_code": rc,
        "output_lines": len(output.splitlines()),
        "waited": wait,
    })

    return 0  # always 0 — silent-fail contract


def _write_result(path: Path, data: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"[roborev-check] could not write output: {exc}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
