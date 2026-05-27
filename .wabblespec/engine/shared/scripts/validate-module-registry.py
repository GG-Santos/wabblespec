#!/usr/bin/env python3
"""
WabbleSpec module registry consistency checker.

Secondary audit tool — NOT an authority replacement for wabblespec.yaml.
Validates that every path declared in wabblespec.yaml exists on disk,
and optionally reports skill files present on disk but not declared.

Exit codes:
  0 = all declared paths exist; no errors
  1 = one or more declared paths are missing
  2 = input error (wabblespec.yaml not found or malformed)

Usage:
  python validate-module-registry.py
  python validate-module-registry.py --verbose
  python validate-module-registry.py --undeclared   # also report undeclared skill dirs
  python validate-module-registry.py --framework path/to/.wabblespec/wabblespec.yaml
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ── Repo root resolution ──────────────────────────────────────────────────────

def find_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / ".wabblespec").is_dir():
            return parent
    raise FileNotFoundError(f"No .wabblespec/ found from {start}")


# ── Shared artifact checks ────────────────────────────────────────────────────

_SHARED_SECTIONS = [
    "schemas",
    "references",
    "infrastructure",
    "scripts",
    "templates",
    "dev_frameworks",
    "dev_infrastructure",
    "gateway_rules",
]


def check_shared(fw: dict, root: Path, verbose: bool) -> list[str]:
    errors = []
    shared = fw.get("shared", {})
    for section in _SHARED_SECTIONS:
        for entry in shared.get(section, []):
            path_str = entry.get("path", "")
            if not path_str:
                continue
            full = root / path_str
            if not full.exists():
                errors.append(f"MISSING shared.{section}: {path_str}")
            elif verbose:
                print(f"  OK  shared.{section}: {path_str}")
    return errors


# ── Module checks ─────────────────────────────────────────────────────────────

def check_modules(fw: dict, root: Path, verbose: bool) -> list[str]:
    errors = []
    for mod in fw.get("modules", []):
        mod_id = mod.get("id", "<unknown>")
        path_str = mod.get("path", "")
        if not path_str:
            errors.append(f"MISSING path field: module id={mod_id}")
            continue
        full = root / path_str
        if not full.exists():
            errors.append(f"MISSING module path: {path_str}  (id={mod_id})")
            continue

        # Container directories (path ends with /) hold sub-reference files only.
        # SKILL.md is not expected there — skip the check.
        is_container = path_str.endswith("/")
        if is_container:
            if verbose:
                print(f"  OK  container: {mod_id}  ({path_str})")
            continue

        skill_md = full / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"MISSING SKILL.md: {path_str}/SKILL.md  (id={mod_id})")
        elif verbose:
            print(f"  OK  module: {mod_id}  ({path_str})")
    return errors


# ── Undeclared skill dirs (optional) ─────────────────────────────────────────

def find_undeclared(fw: dict, root: Path) -> list[str]:
    declared_paths = {
        (root / m["path"]).resolve()
        for m in fw.get("modules", [])
        if m.get("path")
    }
    undeclared = []
    modules_root = root / ".wabblespec" / "engine" / "modules"
    if not modules_root.exists():
        return undeclared
    for skill_md in modules_root.rglob("SKILL.md"):
        skill_dir = skill_md.parent.resolve()
        if skill_dir not in declared_paths:
            rel = skill_dir.relative_to(root)
            undeclared.append(str(rel))
    return undeclared


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec registry consistency checker")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--undeclared", action="store_true",
                        help="Report skill dirs present on disk but not in wabblespec.yaml")
    parser.add_argument("--framework", default=None,
                        help="Path to wabblespec.yaml (default: auto-detect)")
    args = parser.parse_args()

    # Locate wabblespec.yaml
    try:
        repo_root = find_repo_root(Path.cwd())
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    yaml_path = Path(args.framework) if args.framework else repo_root / ".wabblespec" / "wabblespec.yaml"
    if not yaml_path.exists():
        print(f"ERROR: wabblespec.yaml not found at {yaml_path}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(yaml_path, encoding="utf-8") as f:
            fw = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: failed to parse {yaml_path}: {e}", file=sys.stderr)
        sys.exit(2)

    if args.verbose:
        print(f"Registry: {yaml_path}")
        print(f"Repo root: {repo_root}\n")

    all_errors: list[str] = []

    # Check shared artifacts
    all_errors.extend(check_shared(fw, repo_root, args.verbose))

    # Check module paths + SKILL.md presence
    all_errors.extend(check_modules(fw, repo_root, args.verbose))

    # Optional: undeclared skill dirs
    if args.undeclared:
        undeclared = find_undeclared(fw, repo_root)
        if undeclared:
            print("\nUNDECLARED skill directories (present on disk, not in wabblespec.yaml):")
            for p in sorted(undeclared):
                print(f"  ? {p}")
        elif args.verbose:
            print("\nNo undeclared skill directories found.")

    # Report
    if all_errors:
        print(f"\n{len(all_errors)} error(s) found:\n")
        for err in all_errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        module_count = len(fw.get("modules", []))
        print(f"OK — {module_count} modules, all declared paths present.")
        sys.exit(0)


if __name__ == "__main__":
    main()
