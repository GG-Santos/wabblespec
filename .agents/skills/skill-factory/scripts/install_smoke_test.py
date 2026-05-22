#!/usr/bin/env python3
"""Install smoke test: unpack a .skill bundle in a clean tmpdir,
parse it, run quick_validate and review_skill inside, exercise any hooks with a
neutral payload, and report.

This is the v4 `install_smoke_test` gate from SKILL.md. It does NOT
require the host runtime - it just confirms the bundle is installable
and basic checks pass in isolation.

Usage:
    python -m scripts.install_smoke_test <path-to-skill-or-bundle> [--json]

The argument can be either:
  - A directory (treated as already-unpacked skill)
  - A .skill or .zip file (unpacked into a tmpdir before checks)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


DRIVE_QUALIFIED_RE = re.compile(r"^[A-Za-z]:")


def _safe_archive_parts(member_name: str) -> tuple[str, ...]:
    """Return safe archive path parts or raise for traversal/absolute paths."""
    normalized = member_name.replace("\\", "/")
    if normalized.startswith(("/", "//")) or DRIVE_QUALIFIED_RE.match(normalized):
        raise ValueError(f"unsafe archive member path: {member_name}")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"unsafe archive member path: {member_name}")
    return tuple(parts)


def safe_extract_archive(zf: zipfile.ZipFile, target_dir: Path) -> None:
    """Extract zip members after rejecting absolute and traversal paths."""
    target_root = target_dir.resolve()
    for info in zf.infolist():
        parts = _safe_archive_parts(info.filename)
        target = (target_root.joinpath(*parts)).resolve()
        try:
            target.relative_to(target_root)
        except ValueError as exc:
            raise ValueError(f"unsafe archive member path: {info.filename}") from exc

        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(info, "r") as source, target.open("wb") as dest:
            shutil.copyfileobj(source, dest)


def _resolve_skill_dir(input_path: Path, tmpdir: Path) -> Path:
    """Unpack a bundle into tmpdir or return input_path if already a directory."""
    if input_path.is_dir():
        return input_path
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if input_path.suffix not in (".skill", ".zip"):
        raise ValueError(f"unsupported bundle type: {input_path.suffix}")
    with zipfile.ZipFile(input_path, "r") as zf:
        safe_extract_archive(zf, tmpdir)
    # If the zip contains a single top-level directory, descend into it
    entries = [p for p in tmpdir.iterdir() if not p.name.startswith("_")]
    if len(entries) == 1 and entries[0].is_dir() and (entries[0] / "SKILL.md").exists():
        return entries[0]
    return tmpdir


def _check_skill_md(skill_dir: Path) -> dict[str, Any]:
    """Confirm SKILL.md exists and has valid frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    result: dict[str, Any] = {"check": "skill_md", "passed": False, "issues": []}
    if not skill_md.exists():
        result["issues"].append("SKILL.md not found at bundle root")
        return result
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    if not content.startswith("---"):
        result["issues"].append("SKILL.md does not start with YAML frontmatter")
        return result
    # Find closing ---
    end = content.find("\n---", 4)
    if end < 0:
        result["issues"].append("SKILL.md frontmatter not terminated")
        return result
    frontmatter = content[4:end]
    if "name:" not in frontmatter:
        result["issues"].append("frontmatter missing 'name'")
    if "description:" not in frontmatter:
        result["issues"].append("frontmatter missing 'description'")
    result["passed"] = not result["issues"]
    return result


def _run_quick_validate(skill_dir: Path) -> dict[str, Any]:
    """Run scripts.quick_validate against the unpacked skill, if available."""
    result: dict[str, Any] = {"check": "quick_validate", "passed": False, "issues": []}
    # quick_validate may live in the bundle's scripts/ or in the host package
    qv_in_bundle = skill_dir / "scripts" / "quick_validate.py"
    if qv_in_bundle.exists():
        cmd = [sys.executable, str(qv_in_bundle), str(skill_dir)]
    else:
        # Fall back to host module
        cmd = [sys.executable, "-m", "scripts.quick_validate", str(skill_dir)]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result["stdout_tail"] = proc.stdout.splitlines()[-5:]
        result["stderr_tail"] = proc.stderr.splitlines()[-5:]
        result["returncode"] = proc.returncode
        result["passed"] = proc.returncode == 0
        if proc.returncode != 0:
            result["issues"].append(f"quick_validate returncode={proc.returncode}")
    except FileNotFoundError as exc:
        result["issues"].append(f"quick_validate not runnable: {exc}")
    except subprocess.TimeoutExpired:
        result["issues"].append("quick_validate timed out (60s)")
    return result


def _run_review_skill(skill_dir: Path) -> dict[str, Any]:
    """Run scripts.review_skill against the unpacked skill, if available."""
    result: dict[str, Any] = {"check": "review_skill", "passed": False, "issues": []}
    review_in_bundle = skill_dir / "scripts" / "review_skill.py"
    if review_in_bundle.exists():
        cmd = [sys.executable, str(review_in_bundle), str(skill_dir), "--json"]
    else:
        cmd = [sys.executable, "-m", "scripts.review_skill", str(skill_dir), "--json"]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result["stdout_tail"] = proc.stdout.splitlines()[-5:]
        result["stderr_tail"] = proc.stderr.splitlines()[-5:]
        result["returncode"] = proc.returncode
        result["passed"] = proc.returncode == 0
        if proc.returncode != 0:
            result["issues"].append(f"review_skill returncode={proc.returncode}")
    except FileNotFoundError as exc:
        result["issues"].append(f"review_skill not runnable: {exc}")
    except subprocess.TimeoutExpired:
        result["issues"].append("review_skill timed out (60s)")
    return result


def _exercise_hooks(skill_dir: Path) -> dict[str, Any]:
    """Run each hook with a neutral payload to ensure none crash."""
    result: dict[str, Any] = {"check": "hooks_no_crash", "passed": True, "hooks_run": [], "issues": []}
    hooks_dir = skill_dir / "hooks"
    if not hooks_dir.exists():
        result["skipped"] = "no hooks/ directory"
        return result

    neutral_payload = json.dumps({
        "hook_event_name": "before_tool",
        "tool_name": "read_files",
        "tool_input": {"file_path": "/tmp/example.txt"},
    })

    for hook_file in sorted(hooks_dir.glob("*.py")):
        try:
            proc = subprocess.run(
                [sys.executable, str(hook_file)],
                input=neutral_payload,
                capture_output=True,
                text=True,
                timeout=10,
            )
            entry = {
                "hook": hook_file.name,
                "returncode": proc.returncode,
                "stdout_first_line": (proc.stdout.splitlines() or [""])[0],
            }
            if proc.returncode != 0:
                result["passed"] = False
                result["issues"].append(f"{hook_file.name}: nonzero return ({proc.returncode})")
            result["hooks_run"].append(entry)
        except subprocess.TimeoutExpired:
            result["passed"] = False
            result["issues"].append(f"{hook_file.name}: timed out (10s)")
        except Exception as exc:
            result["passed"] = False
            result["issues"].append(f"{hook_file.name}: {exc}")

    return result


def smoke_test(input_path: Path) -> dict[str, Any]:
    tmpdir = Path(tempfile.mkdtemp(prefix="skill_smoke_"))
    try:
        skill_dir = _resolve_skill_dir(input_path, tmpdir)
        checks = [
            _check_skill_md(skill_dir),
            _run_quick_validate(skill_dir),
            _run_review_skill(skill_dir),
            _exercise_hooks(skill_dir),
        ]
        passed = all(c.get("passed", False) or "skipped" in c for c in checks)
        return {
            "input": str(input_path),
            "unpacked_to": str(skill_dir),
            "checks": checks,
            "passed": passed,
        }
    finally:
        # Only clean up tmpdir if we actually unpacked into it
        if input_path.is_file():
            shutil.rmtree(tmpdir, ignore_errors=True)


def render_text(report: dict[str, Any]) -> str:
    lines = [f"install_smoke_test: {report['input']}"]
    lines.append("=" * 60)
    for c in report["checks"]:
        name = c["check"]
        status = "SKIP" if c.get("skipped") else ("PASS" if c.get("passed") else "FAIL")
        lines.append(f"  [{status}] {name}")
        if c.get("skipped"):
            lines.append(f"          reason: {c['skipped']}")
        for issue in c.get("issues", []):
            lines.append(f"          - {issue}")
    lines.append("")
    lines.append(f"Overall: {'PASS' if report['passed'] else 'FAIL'}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Smoke-test a skill bundle in a clean environment")
    p.add_argument("path", type=Path, help="Path to skill directory or .skill/.zip bundle")
    p.add_argument("--json", action="store_true", help="Emit JSON")
    args = p.parse_args()

    report = smoke_test(args.path)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
