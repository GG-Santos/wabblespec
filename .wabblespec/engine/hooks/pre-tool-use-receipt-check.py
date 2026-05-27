#!/usr/bin/env python3
"""
WabbleSpec pre-tool-use receipt enforcement hook.

Reads .wabblespec/state/session/state.json. Blocks tool execution when:
  1. Required upstream receipts are absent from .wabblespec/state/receipts/
  2. Any evidence drawer listed in evidence_drawers has staleness_state == EXPIRED
     (emits STALENESS_VIOLATION per I9)

Exit 0 = allow. Exit 1 = block (message to stderr).

Configured in .claude/settings.json PreToolUse hook.

session/state.json fields used:
  enforcement_active  : bool
  required_receipts   : list[str]  — receipt filename stems (no .json)
  active_module       : str
  evidence_drawers    : list[str]  — paths relative to .wabblespec root
"""
import json
import os
import sys
from pathlib import Path


ENFORCEMENT_TOOLS = {"Edit", "Write", "Bash", "MultiEdit"}


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


def check_expired_drawers(ws_root: Path, drawer_paths: list) -> list[str]:
    """Return list of drawer path strings whose staleness_state is EXPIRED."""
    expired = []
    for rel_path in drawer_paths:
        drawer_file = ws_root / rel_path.lstrip("/\\")
        data = load_json_safe(drawer_file)
        if isinstance(data, dict) and data.get("staleness_state") == "EXPIRED":
            expired.append(rel_path)
    return expired


def main() -> None:
    hook_input = load_json_safe(Path("/dev/stdin")) if sys.stdin.isatty() is False else None
    if hook_input is None:
        try:
            raw = sys.stdin.read()
            hook_input = json.loads(raw) if raw.strip() else {}
        except (json.JSONDecodeError, OSError):
            hook_input = {}

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in ENFORCEMENT_TOOLS:
        sys.exit(0)

    ws_root = find_wabblespec_root()
    if ws_root is None:
        sys.exit(0)

    state = load_json_safe(ws_root / "state" / "session" / "state.json")
    if state is None or not state.get("enforcement_active", False):
        sys.exit(0)

    required = state.get("required_receipts", [])
    receipts_dir = ws_root / "state" / "receipts"
    missing = [m for m in required if not (receipts_dir / f"{m}.json").exists()]

    if missing:
        active = state.get("active_module", "unknown")
        print(
            f"[WabbleSpec] BLOCKED — {tool_name} denied.\n"
            f"  Active module : {active}\n"
            f"  Missing receipts: {', '.join(missing)}\n"
            f"  Run upstream modules first, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Staleness enforcement (I9) ---
    evidence_drawers = state.get("evidence_drawers", [])
    if evidence_drawers:
        expired = check_expired_drawers(ws_root, evidence_drawers)
        if expired:
            active = state.get("active_module", "unknown")
            print(
                f"[WabbleSpec] STALENESS_VIOLATION — {tool_name} denied.\n"
                f"  Active module : {active}\n"
                f"  Expired drawers: {', '.join(expired)}\n"
                f"  Re-verify evidence before proceeding. See .wabblespec/engine/shared/references/staleness-states.md.",
                file=sys.stderr,
            )
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
