#!/usr/bin/env python3
"""Package a skill folder into a distributable .skill archive."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import zipfile
from pathlib import Path

try:
    from scripts.quick_validate import validate_skill
    from scripts.review_skill import review_skill
    from scripts.utils import redact_secrets
except ModuleNotFoundError:  # Allows `python scripts/package_skill.py ...`.
    from quick_validate import validate_skill
    from review_skill import review_skill
    from utils import redact_secrets


EXCLUDE_DIRS = {
    ".claude",
    ".git",
    ".hg",
    ".omc",
    ".omx",
    ".planning",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".svn",
    ".vscode",
    ".venv",
    "live_provider_raw",
    "live_provider_raw_dry",
    "live_provider_repair_prompts",
    "skill_benchmarks",
    "venv",
}
EXCLUDE_GLOBS = {
    "*.skill",
    "*.pyc",
    "*.pyo",
    "*.tmp",
    "*.log",
    "benchmark*.json",
    "comparison*.json",
    "coverage.xml",
    "feedback*.json",
    "grading*.json",
    "metrics*.json",
    "phase*_regression.py",
    "repair_history.json",
    "stress_live_artifact_*.json",
    "stress_live_eval_*.json",
    "stress_provider_*.json",
    "validation_report*.json",
}
EXCLUDE_FILES = {
    ".DS_Store",
    ".coverage",
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".token-savior-cache.json",
}
ROOT_EXCLUDE_DIRS = {"evals", "benchmarks", "logs", "dist", "htmlcov", "coverage", "test-results", "reports"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def should_exclude(rel_path: Path) -> bool:
    """Check if a path should be excluded from packaging."""
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    if rel_path.name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(rel_path.name, pattern) for pattern in EXCLUDE_GLOBS)


def build_package_manifest(skill_path: Path) -> list[tuple[Path, Path]]:
    """Return sorted package files as (source, archive-name), rejecting unsafe paths."""
    skill_path = Path(skill_path).resolve()
    skill_parent = skill_path.parent.resolve()
    manifest: list[tuple[Path, Path]] = []

    for file_path in sorted(skill_path.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.is_symlink():
            raise ValueError(f"Refusing to package symlink: {file_path}")

        resolved = file_path.resolve()
        try:
            resolved.relative_to(skill_path)
        except ValueError as exc:
            raise ValueError(f"Refusing to package file outside skill root: {file_path}") from exc

        if resolved.stat().st_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Refusing to package oversized file: {file_path}")

        arcname = resolved.relative_to(skill_parent)
        if should_exclude(arcname):
            continue
        scan_file_for_secrets(resolved, arcname)
        manifest.append((resolved, arcname))

    return manifest


def scan_file_for_secrets(file_path: Path, arcname: Path) -> None:
    """Reject packaged source/doc files containing likely API keys."""
    if len(arcname.parts) > 1 and arcname.parts[1] == "tests":
        return
    if file_path.suffix.lower() not in {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".toml", ".env"}:
        return
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    redacted = redact_secrets(text)
    if redacted != text:
        raise ValueError(f"Refusing to package file with likely secret: {arcname}")


def package_skill(
    skill_path: str | Path,
    output_dir: str | Path | None = None,
    dry_run: bool = False,
    strict: bool = True,
    verbose: bool = True,
) -> Path | None:
    """Package a skill folder into a .skill file."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"Error: Skill folder not found: {skill_path}")
        return None
    if not skill_path.is_dir():
        print(f"Error: Path is not a directory: {skill_path}")
        return None
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return None

    if verbose:
        print("Validating skill...")
    valid, message = validate_skill(skill_path, strict=strict)
    if not valid:
        print(f"Validation failed: {message}")
        print("Please fix validation errors before packaging.")
        return None
    if verbose:
        print(f"{message}\n")

    review = review_skill(skill_path)
    if not review["valid"]:
        print("Definition review failed:")
        for entry in review["items"]:
            if entry["status"] == "fail":
                print(f"  {entry['id']} {entry['title']}: {entry['note']}")
        print("Please fix review failures before packaging.")
        return None
    if verbose:
        summary = review["summary"]
        print(
            "Definition review passed: "
            f"{summary['pass']} pass, {summary['warning']} warn, {summary['fail']} fail\n"
        )

    output_path = Path(output_dir).resolve() if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    skill_filename = output_path / f"{skill_path.name}.skill"

    try:
        manifest = build_package_manifest(skill_path)
        if dry_run:
            if verbose:
                print(f"Dry run: would package {len(manifest)} files to {skill_filename}")
                for _, arcname in manifest:
                    print(f"  Would add: {arcname}")
            return skill_filename

        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for source, arcname in manifest:
                zipf.write(source, arcname)
                if verbose:
                    print(f"  Added: {arcname}")

        if verbose:
            print(f"\nSuccessfully packaged skill to: {skill_filename}")
        return skill_filename
    except Exception as exc:
        print(f"Error creating .skill file: {exc}")
        return None


def package_suite_members(
    suite_root: str | Path,
    output_dir: str | Path | None = None,
    dry_run: bool = False,
    strict: bool = True,
    verbose: bool = True,
) -> list[Path]:
    """Package each member declared in suite.yaml."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required for --per-member suite packaging") from exc

    suite_root = Path(suite_root).resolve()
    suite_path = suite_root / "suite.yaml"
    if not suite_path.exists():
        raise ValueError(f"suite.yaml not found in {suite_root}")
    data = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    suite = data.get("suite") if isinstance(data, dict) else None
    members = suite.get("members") if isinstance(suite, dict) else None
    if not isinstance(members, list) or not members:
        raise ValueError("suite.yaml must contain suite.members")

    output_path = Path(output_dir).resolve() if output_dir else Path.cwd()
    archive_names: dict[Path, str] = {}
    member_paths: list[tuple[dict, Path]] = []
    for member in members:
        if not isinstance(member, dict) or not member.get("path"):
            raise ValueError(f"Invalid suite member: {json.dumps(member)}")
        member_path = (suite_root / str(member["path"])).resolve()
        member_path.relative_to(suite_root)
        archive_path = output_path / f"{member_path.name}.skill"
        member_id = str(member.get("id", member_path.name))
        if archive_path in archive_names:
            raise ValueError(
                "Suite member package name collision: "
                f"{archive_path.name} for {archive_names[archive_path]} and {member_id}"
            )
        archive_names[archive_path] = member_id
        member_paths.append((member, member_path))

    packaged: list[Path] = []
    for member, member_path in member_paths:
        result = package_skill(
            member_path,
            output_dir=output_dir,
            dry_run=dry_run,
            strict=strict,
            verbose=verbose,
        )
        if result is None:
            raise ValueError(f"Failed to package suite member: {member.get('id', member_path.name)}")
        packaged.append(result)
    return packaged


def main() -> None:
    parser = argparse.ArgumentParser(description="Package a skill folder into a .skill archive")
    parser.add_argument("skill_path", help="Path to skill folder")
    parser.add_argument("output_dir", nargs="?", default=None, help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview package contents without writing archive")
    parser.add_argument("--skip-strict", action="store_true", help="Only validate SKILL.md; skip support-file lint/syntax checks")
    parser.add_argument("--per-member", action="store_true", help="For suite roots, package each suite member individually")
    args = parser.parse_args()

    print(f"Packaging skill: {args.skill_path}")
    if args.output_dir:
        print(f"Output directory: {args.output_dir}")
    print()

    try:
        if args.per_member:
            results = package_suite_members(
                args.skill_path,
                args.output_dir,
                dry_run=args.dry_run,
                strict=not args.skip_strict,
            )
            sys.exit(0 if results else 1)
        result = package_skill(args.skill_path, args.output_dir, dry_run=args.dry_run, strict=not args.skip_strict)
        sys.exit(0 if result else 1)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
