"""wabblespec-init.py — install or re-configure WabbleSpec in a project.

Modes:
  --full          Copy engine bundle, create empty state/, write settings.json,
                  run skill sync, write install receipt. (New project install.)
  --sync-only     Re-sync .claude/skills/ from engine/modules/. (Used by SessionStart.)
  --configure-only  Write settings.json + run skill sync. (Clone-from-template installs.)

Usage (from the WabbleSpec repo or a target project):
  python .wabblespec/engine/scripts/wabblespec-init.py --full [--target /path/to/project]
  python .wabblespec/engine/scripts/wabblespec-init.py --sync-only
  python .wabblespec/engine/scripts/wabblespec-init.py --configure-only

When --target is omitted, the current working directory is used.

For --full, the script copies the entire .wabblespec/engine/ bundle from the SOURCE
(the WabbleSpec repo identified by this script's location) into TARGET/.wabblespec/engine/.
For --sync-only and --configure-only, the source and target are the same directory.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ── Bootstrap ─────────────────────────────────────────────────────────────────

_HERE = Path(__file__).resolve()
# This script lives at .wabblespec/engine/scripts/wabblespec-init.py
# Walk up to find the WabbleSpec SOURCE repo (the one containing this script)
_SOURCE_ROOT = _HERE.parent.parent.parent.parent  # 4 levels up from scripts/

_WABBLESPEC_DIR = ".wabblespec"
_ENGINE_DIR = ".wabblespec/engine"
_STATE_SUBDIRS = [
    "receipts", "archive", "memory", "experiments", "plans",
    "session", "health", "runtime", "checkpoints", "logs",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _copy_tree(src: Path, dst: Path, quiet: bool) -> tuple[int, int]:
    """Copy src tree to dst, skipping __pycache__ and unchanged files."""
    copied = skipped = 0
    for src_file in src.rglob("*"):
        if src_file.is_dir():
            continue
        if "__pycache__" in src_file.parts:
            continue
        rel = src_file.relative_to(src)
        dst_file = dst / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        if dst_file.exists() and _md5(src_file) == _md5(dst_file):
            skipped += 1
            continue
        shutil.copy2(src_file, dst_file)
        copied += 1
        if not quiet:
            print(f"  copy  {rel}")
    return copied, skipped


def _write_settings(target: Path, quiet: bool) -> None:
    """Write .claude/settings.json with correct absolute hook paths for target."""
    engine = target / ".wabblespec" / "engine"
    shared = engine / "shared"

    def _q(p: Path) -> str:
        # JSON-safe escaped Windows path string
        return str(p).replace("\\", "\\\\")

    hooks_path = engine / "hooks"
    scripts_path = engine / "scripts"

    settings = {
        "hooks": {
            "SessionStart": [
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(scripts_path / "sync-pull.py")}"',
                            "timeout": 30}]},
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(scripts_path / "wabblespec-sync-skills.py")}" --quiet',
                            "timeout": 30}]},
                {"hooks": [{"type": "command",
                            "command": f'node "{_q(hooks_path / "wabblespec-session-start.js")}"'}]},
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(shared / "scripts" / "wabble-sound.py")}" --hook'}]},
            ],
            "UserPromptSubmit": [
                {"hooks": [{"type": "command",
                            "command": f'node "{_q(hooks_path / "wabblespec-prompt-guard.js")}"'}]},
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(shared / "scripts" / "wabble-sound.py")}" --hook'}]},
            ],
            "PreToolUse": [
                {"matcher": "Edit|Write|Bash|MultiEdit",
                 "hooks": [{"type": "command",
                            "command": f'python "{_q(hooks_path / "pre-tool-use-receipt-check.py")}"'}]},
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(shared / "scripts" / "wabble-sound.py")}" --hook'}]},
            ],
            "PostToolUse": [
                {"matcher": "Edit|Write|Bash|MultiEdit",
                 "hooks": [{"type": "command",
                            "command": f'python "{_q(engine / "modules" / "l2" / "executor" / "hooks" / "post-wave-receipt-check.py")}"'}]},
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(shared / "scripts" / "wabble-sound.py")}" --hook'}]},
            ],
            "Stop": [
                {"matcher": "",
                 "hooks": [{"type": "command",
                            "command": f'python "{_q(scripts_path / "stop-hook.py")}"',
                            "timeout": 150}]},
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(shared / "scripts" / "wabble-sound.py")}" --hook'}]},
            ],
            "PreCompact": [
                {"matcher": "",
                 "hooks": [{"type": "command",
                            "command": f'python "{_q(scripts_path / "run-convo-miner.py")}" --urgent',
                            "timeout": 90}]},
                {"hooks": [{"type": "command",
                            "command": f'node "{_q(hooks_path / "wabblespec-precompact.js")}"'}]},
                {"hooks": [{"type": "command",
                            "command": f'python "{_q(shared / "scripts" / "wabble-sound.py")}" --hook'}]},
            ],
        },
        "statusLine": {
            "type": "command",
            "command": f'powershell -ExecutionPolicy Bypass -File "{_q(hooks_path / "wabblespec-statusline.ps1")}"',
        },
    }

    claude_dir = target / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_path = claude_dir / "settings.json"
    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    if not quiet:
        print(f"  wrote {settings_path.relative_to(target)}")


def _run_skill_sync(target: Path, quiet: bool) -> None:
    sync_script = target / ".wabblespec" / "engine" / "scripts" / "wabblespec-sync-skills.py"
    if not sync_script.exists():
        print(f"WARNING: sync script not found: {sync_script}", file=sys.stderr)
        return
    cmd = [sys.executable, str(sync_script)]
    if quiet:
        cmd.append("--quiet")
    result = subprocess.run(cmd, cwd=str(target))
    if result.returncode != 0:
        print("WARNING: skill sync exited non-zero", file=sys.stderr)


def _write_gitignore(target: Path, quiet: bool) -> None:
    """Add .wabblespec/state/ to .gitignore if not already present."""
    gitignore = target / ".gitignore"
    marker = ".wabblespec/state/"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if marker in content:
            return
        gitignore.write_text(content.rstrip() + f"\n{marker}\n", encoding="utf-8")
    else:
        gitignore.write_text(f"# WabbleSpec runtime state\n{marker}\n", encoding="utf-8")
    if not quiet:
        print(f"  updated .gitignore: added {marker}")


def _write_install_receipt(target: Path) -> None:
    receipt = {
        "installed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "installed_by": "wabblespec-init.py --full",
        "target": str(target),
        "platform": platform.system(),
        "python": sys.version,
    }
    receipt_path = target / ".wabblespec" / "state" / "receipts" / "install-receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--full", action="store_true", help="Full install to target project")
    group.add_argument("--sync-only", action="store_true", help="Re-sync .claude/skills/ only")
    group.add_argument("--configure-only", action="store_true", help="Write settings.json + sync skills")
    parser.add_argument("--target", help="Target project root (default: cwd)")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-file output")
    args = parser.parse_args()

    target = Path(args.target).resolve() if args.target else Path.cwd().resolve()

    if args.sync_only:
        print(f"wabblespec-init --sync-only: {target}")
        _run_skill_sync(target, quiet=args.quiet)
        return

    if args.configure_only:
        print(f"wabblespec-init --configure-only: {target}")
        _write_settings(target, quiet=args.quiet)
        _run_skill_sync(target, quiet=args.quiet)
        return

    # --full
    print(f"wabblespec-init --full: {target}")
    source_engine = _SOURCE_ROOT / ".wabblespec" / "engine"
    if not source_engine.exists():
        sys.exit(f"ERROR: source engine not found: {source_engine}")

    # 1. Copy engine bundle
    dst_engine = target / ".wabblespec" / "engine"
    print(f"\nCopying engine bundle...")
    copied, skipped = _copy_tree(source_engine, dst_engine, quiet=args.quiet)
    print(f"  {copied} files copied, {skipped} unchanged")

    # 2. Copy wabblespec.yaml
    src_yaml = _SOURCE_ROOT / ".wabblespec" / "wabblespec.yaml"
    if src_yaml.exists():
        dst_yaml = target / ".wabblespec" / "wabblespec.yaml"
        dst_yaml.parent.mkdir(parents=True, exist_ok=True)
        if not dst_yaml.exists() or _md5(src_yaml) != _md5(dst_yaml):
            shutil.copy2(src_yaml, dst_yaml)
            if not args.quiet:
                print("  copy  .wabblespec/wabblespec.yaml")

    # 3. Copy VERSION
    src_ver = _SOURCE_ROOT / ".wabblespec" / "VERSION"
    if src_ver.exists():
        dst_ver = target / ".wabblespec" / "VERSION"
        shutil.copy2(src_ver, dst_ver)

    # 4. Create empty state/ subdirs
    print("\nCreating state/ directories...")
    for sub in _STATE_SUBDIRS:
        (target / ".wabblespec" / "state" / sub).mkdir(parents=True, exist_ok=True)

    # 5. Write settings.json
    print("\nWriting .claude/settings.json...")
    _write_settings(target, quiet=args.quiet)

    # 6. Sync skills
    print("\nSyncing .claude/skills/...")
    _run_skill_sync(target, quiet=args.quiet)

    # 7. .gitignore
    _write_gitignore(target, quiet=args.quiet)

    # 8. Install receipt
    _write_install_receipt(target)
    if not args.quiet:
        print("  wrote .wabblespec/state/receipts/install-receipt.json")

    print(f"\nInstall complete. Open Claude Code in {target} to start a session.")


if __name__ == "__main__":
    main()
