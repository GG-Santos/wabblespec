"""wabblespec-sync-skills.py — sync WabbleSpec skill modules to .claude/skills/

Reads wabblespec.yaml for the authoritative module list. For each module that
has a SKILL.md, copies the full module directory (minus __pycache__) to
.claude/skills/<name>/ using the SKILL.md frontmatter name: as the target dir.

Skips .claude/skills/ entries whose name does not appear in wabblespec.yaml —
external skills (naninovel, skill-creator, etc.) are left untouched.

Hash-checks all files before overwriting — idempotent.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

# Bootstrap repo root
_HERE = Path(__file__).resolve()
_REPO_ROOT_SENTINEL = ".wabblespec"
_probe = _HERE
while _probe != _probe.parent:
    if (_probe / _REPO_ROOT_SENTINEL).exists():
        break
    _probe = _probe.parent
if not (_probe / _REPO_ROOT_SENTINEL).exists():
    sys.exit("ERROR: cannot find WabbleSpec repo root")
ROOT = _probe

try:
    import yaml
except ImportError:
    sys.exit("ERROR: pyyaml not installed — run: pip install pyyaml")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _read_skill_name(skill_md: Path) -> str | None:
    content = skill_md.read_text(encoding="utf-8")
    m = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else None


def _copy_module(src_dir: Path, dst_dir: Path, quiet: bool) -> tuple[int, int]:
    """Copy src_dir to dst_dir, skipping __pycache__ and unchanged files.

    Returns (files_copied, files_skipped).
    """
    copied = skipped = 0
    for src_file in src_dir.rglob("*"):
        if src_file.is_dir():
            continue
        # Skip Python bytecode caches
        if "__pycache__" in src_file.parts:
            continue
        rel = src_file.relative_to(src_dir)
        dst_file = dst_dir / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        if dst_file.exists() and _md5(src_file) == _md5(dst_file):
            skipped += 1
            continue
        shutil.copy2(src_file, dst_file)
        copied += 1
        if not quiet:
            print(f"  copied {rel}")
    return copied, skipped


def _remove_stale(dst_dir: Path, valid_names: set[str], quiet: bool) -> int:
    """Remove .claude/skills/ subdirs that are WabbleSpec-managed but no longer in yaml."""
    removed = 0
    if not dst_dir.exists():
        return 0
    for child in dst_dir.iterdir():
        if not child.is_dir():
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.exists():
            continue
        name = _read_skill_name(skill_md)
        if name and name not in valid_names:
            shutil.rmtree(child)
            removed += 1
            if not quiet:
                print(f"  removed stale skill: {child.name}")
    return removed


# ── Main ──────────────────────────────────────────────────────────────────────

def _load_active_skills(recipe_path: Path) -> set[str] | None:
    """Return set of active skill names from recipe.json, or None if no filter applies."""
    if not recipe_path.exists():
        return None
    try:
        import json as _json
        data = _json.loads(recipe_path.read_text(encoding="utf-8"))
        skills = data.get("active_skills", [])
        if skills:
            return set(skills)
    except Exception:
        pass
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="suppress per-file output")
    parser.add_argument("--dry-run", action="store_true", help="report changes without writing")
    parser.add_argument(
        "--filter-recipe", metavar="PATH",
        help="Path to recipe.json. If it declares active_skills, only those skills are synced. "
             "Omit to sync all skills (default behavior).",
    )
    args = parser.parse_args()

    active_skills: set[str] | None = None
    if args.filter_recipe:
        active_skills = _load_active_skills(Path(args.filter_recipe))
        if active_skills is not None and not args.quiet:
            print(f"Skill filter active: {sorted(active_skills)}")

    yaml_path = ROOT / ".wabblespec" / "wabblespec.yaml"
    if not yaml_path.exists():
        sys.exit(f"ERROR: wabblespec.yaml not found at {yaml_path}")

    with yaml_path.open(encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    modules = registry.get("modules", [])
    skills_dir = ROOT / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    total_copied = total_skipped = total_removed = 0
    valid_skill_names: set[str] = set()
    synced = 0

    for mod in modules:
        mod_path = ROOT / mod.get("path", "").rstrip("/")
        skill_md = mod_path / "SKILL.md"
        if not skill_md.exists():
            continue

        name = _read_skill_name(skill_md)
        if not name:
            if not args.quiet:
                print(f"WARNING: no name: in {skill_md} — skipping")
            continue

        valid_skill_names.add(name)

        # Skip skills not in the active filter (leave existing copy untouched)
        if active_skills is not None and name not in active_skills:
            continue

        dst = skills_dir / name

        if args.dry_run:
            print(f"  would sync {name}")
            synced += 1
            continue

        if not args.quiet:
            print(f"syncing {name}...")

        copied, skipped = _copy_module(mod_path, dst, quiet=args.quiet)
        total_copied += copied
        total_skipped += skipped
        synced += 1

    # Stale removal: when a filter is active, only remove skills that are both
    # wabblespec-managed AND in the active filter but no longer in the registry.
    # Skills outside the filter are left untouched.
    stale_candidates = valid_skill_names if active_skills is None else (valid_skill_names & active_skills)
    if not args.dry_run:
        total_removed = _remove_stale(skills_dir, stale_candidates, quiet=args.quiet)

    print(
        f"\nSync complete: {synced} skills | "
        f"{total_copied} files copied | "
        f"{total_skipped} unchanged | "
        f"{total_removed} stale removed"
    )


if __name__ == "__main__":
    main()
