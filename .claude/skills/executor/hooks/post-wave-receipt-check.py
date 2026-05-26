#!/usr/bin/env python3
"""
Executor post-tool-use hook: wave completion receipt check.

Fires after every tool call. When session state indicates a wave has just
completed (wave_just_completed: true), verifies that a verifier receipt
exists for the completed wave number.

Exit 0 = allow. Exit 1 = block (message to stderr).

session/state.json fields read:
  enforcement_active     : bool
  active_module          : str   — must be "executor" to fire
  current_wave           : int   — wave number just completed
  wave_just_completed    : bool  — set by executor after each wave
  waves_planned          : int   — total planned waves
  task_id                : str   — current task identifier
"""

import json
import os
import sys
from pathlib import Path


def find_wabblespec_root() -> Path | None:
    current = Path(os.getcwd())
    for path in [current, *current.parents]:
        candidate = path / ".wabblespec"
        if candidate.is_dir():
            return candidate
    return None


def load_json_safe(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


def receipt_exists_for_wave(ws_root: Path, task_id: str, wave: int) -> bool:
    """Check .wabblespec/receipts/ for a verifier receipt matching task+wave."""
    receipts_dir = ws_root / "receipts"
    if not receipts_dir.exists():
        return False

    for receipt_file in receipts_dir.glob("*.json"):
        data = load_json_safe(receipt_file)
        if not isinstance(data, dict):
            continue
        module = data.get("module", data.get("skill", ""))
        receipt_task = data.get("task_id", "")
        receipt_wave = data.get("wave", data.get("wave_number", None))
        if (module in ("verifier", "verify")
                and receipt_task == task_id
                and receipt_wave == wave):
            return True

    # Fallback: check for a verifier receipt file with wave number in name
    stem_patterns = [
        f"verifier-receipt-wave{wave}",
        f"verifier-wave{wave}-receipt",
        f"verify-receipt-wave{wave}",
    ]
    for receipt_file in receipts_dir.glob("*.json"):
        name_lower = receipt_file.stem.lower()
        if any(p in name_lower for p in stem_patterns):
            return True

    return False


def main() -> None:
    # Read hook input from stdin (Claude Code passes tool call context as JSON)
    hook_input: dict = {}
    if not sys.stdin.isatty():
        try:
            hook_input = json.load(sys.stdin)
        except (json.JSONDecodeError, OSError):
            pass

    ws_root = find_wabblespec_root()
    if ws_root is None:
        sys.exit(0)  # not in a WabbleSpec workspace — pass through

    state_path = ws_root / "session" / "state.json"
    state = load_json_safe(state_path)
    if not isinstance(state, dict):
        sys.exit(0)

    if not state.get("enforcement_active", False):
        sys.exit(0)

    if state.get("active_module", "") != "executor":
        sys.exit(0)

    if not state.get("wave_just_completed", False):
        sys.exit(0)

    wave = state.get("current_wave")
    task_id = state.get("task_id", "")
    waves_planned = state.get("waves_planned", 0)

    if wave is None:
        sys.exit(0)

    if receipt_exists_for_wave(ws_root, task_id, wave):
        sys.exit(0)

    # No verifier receipt found — block
    print(
        f"\n[EXECUTOR WAVE GATE] Wave {wave}/{waves_planned} complete "
        f"but no Verifier receipt found for task '{task_id}' wave {wave}.\n"
        f"  Required: a Verifier receipt with task_id='{task_id}' and wave={wave}\n"
        f"  in .wabblespec/receipts/\n"
        f"  Run /verify before proceeding to wave {wave + 1}.",
        file=sys.stderr
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
