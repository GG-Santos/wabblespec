#!/usr/bin/env python3
"""
Initialize .wabblespec/ directory structure in a project directory.

Usage: python scripts/init-wabblespec.py [target-dir]
Default target: current working directory.

Creates:
  .wabblespec/
    receipts/     -- module receipts (I10 receipt chain)
    plans/        -- planning artifacts per session
    memory/       -- evidence drawers with staleness metadata
    checkpoints/  -- rollback isolation points
    archive/      -- permanent receipt history (never deleted)
    session/      -- current session state (transient)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


STRUCTURE = {
    "receipts": "Module receipts. One JSON file per module execution. Never deleted.",
    "plans": "Planning artifacts. Spec docs, wave plans, proposal records for current session.",
    "memory": "Evidence drawers. Subdirs: wings/{wing}/rooms/{room}/drawers/{id}.json",
    "checkpoints": "Rollback isolation points. Named by wave or session.",
    "archive": "Permanent receipt history. Receipts moved here after session. Append-only.",
    "session": "Current session state. Transient. Cleared between sessions.",
}

DEFAULT_SESSION_STATE = {
    "active_module": None,
    "enforcement_active": False,
    "required_receipts": [],
    "session_id": None,
    "started_at": None,
}


def init(target: Path) -> None:
    ws = target / ".wabblespec"

    if ws.exists():
        print(f"[init] .wabblespec/ already exists at {ws}. Skipping directory creation.")
        print("[init] Run with --force to reinitialize (does not delete existing receipts).")
        return

    created = []
    for subdir, description in STRUCTURE.items():
        d = ws / subdir
        d.mkdir(parents=True, exist_ok=True)
        readme = d / "README.md"
        readme.write_text(f"# .wabblespec/{subdir}/\n\n{description}\n", encoding="utf-8")
        created.append(str(d.relative_to(target)))

    # Default session state (enforcement off until a module activates)
    state_path = ws / "session" / "state.json"
    state_path.write_text(
        json.dumps(DEFAULT_SESSION_STATE, indent=2) + "\n",
        encoding="utf-8",
    )

    # INDEX.md
    index = ws / "INDEX.md"
    index.write_text(
        f"# WabbleSpec Index\n\nInitialized: {datetime.now(timezone.utc).isoformat()}\n\n"
        "Module registry and session index.\n\n"
        "## Active Modules\n\n_None yet._\n",
        encoding="utf-8",
    )

    print(f"[init] .wabblespec/ initialized at {ws}")
    for d in created:
        print(f"  created: {d}/")
    print(f"  created: .wabblespec/INDEX.md")
    print(f"  created: .wabblespec/session/state.json (enforcement_active: false)")


def main() -> None:
    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = Path(args[0]).resolve() if args else Path.cwd()

    if not target.exists():
        print(f"ERROR: target directory does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if force:
        ws = target / ".wabblespec"
        if ws.exists():
            import shutil
            # Preserve receipts and archive — only reset session and plans
            for subdir in ["session", "plans"]:
                d = ws / subdir
                if d.exists():
                    shutil.rmtree(d)
            print(f"[init --force] Cleared session/ and plans/ at {ws}")

    init(target)


if __name__ == "__main__":
    main()
