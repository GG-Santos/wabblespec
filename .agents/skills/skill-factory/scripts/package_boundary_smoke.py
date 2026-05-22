#!/usr/bin/env python3
"""Smoke-test package boundaries and archive safety."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

try:
    from scripts.install_smoke_test import safe_extract_archive, smoke_test
    from scripts.package_skill import build_package_manifest, package_skill
    from scripts.utils import redact_secrets
except ModuleNotFoundError:  # Allows `python scripts/package_boundary_smoke.py`.
    from install_smoke_test import safe_extract_archive, smoke_test
    from package_skill import build_package_manifest, package_skill
    from utils import redact_secrets


def finding(severity: str, code: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def write_fixture(root: Path) -> Path:
    """Create a valid skill plus local artifacts that should not ship."""
    skill = root / "boundary-skill"
    (skill / "references").mkdir(parents=True)
    (skill / "scripts").mkdir()
    (skill / ".planning").mkdir()
    (skill / "__pycache__").mkdir()
    (skill / "reports").mkdir()
    (skill / "logs").mkdir()
    (skill / "htmlcov").mkdir()

    (skill / "SKILL.md").write_text(
        """---
name: boundary-skill
description: Create, review, validate, package, audit, benchmark, and optimize skill package archives, manifests, release boundaries, install smoke tests, and bundle safety.
---

# Boundary Skill

## Workflow

1. Inspect the package root and release boundary.
2. Build a package manifest from runtime files.
3. Validate archive contents, install smoke results, and bundle safety.

## Output Contract

Return `package_manifest`, `archive_entries`, `install_smoke`, `excluded_files`,
`verification`, and `remaining_risks`.

Worked example:

> **package_manifest.** SKILL.md, runtime references, and helper scripts.
> **archive_entries.** No planning docs, caches, reports, or prior archives.
> **install_smoke.** PASS.

## Examples And Edge Cases

- Normal: package runtime files only.
- Ambiguous: name which path is outside the package root.

## Failure Modes

- Shipping planning docs, cache files, reports, or prior archives.
- Extracting archive traversal paths outside the release boundary.
- Trusting an archive before package manifest inspection.

## Safety Boundary

- Allowed help: inspect package manifests, archive entries, release boundaries,
  and install smoke evidence.
- Disallowed help: bypass archive safety checks or hide rejected package files.
- Safe redirect: explain the rejected member path and rerun with a safe archive.
- Refusal shape: boundary -> reason -> safe packaging command.

## Source And Recency Gate

Use local package files and command output as sources. If a package path,
archive hash, or release status changes, report the current checked path and
time of verification instead of inventing current claims.

## Error Handling

If packaging fails, report the rejected file and stop.

Do not use this skill for unrelated release automation.
""",
        encoding="utf-8",
    )
    (skill / "references" / "README.md").write_text("# Runtime reference\n", encoding="utf-8")
    (skill / "scripts" / "helper.py").write_text("print('helper')\n", encoding="utf-8")

    (skill / ".planning" / "PLAN.md").write_text("project-only\n", encoding="utf-8")
    (skill / "__pycache__" / "helper.pyc").write_bytes(b"cache")
    (skill / "old.skill").write_bytes(b"old archive")
    (skill / ".token-savior-cache.json").write_text("{}\n", encoding="utf-8")
    (skill / "coverage.xml").write_text("<coverage />\n", encoding="utf-8")
    (skill / "reports" / "report.json").write_text("{}\n", encoding="utf-8")
    (skill / "logs" / "run.log").write_text("log\n", encoding="utf-8")
    (skill / "feedback.json").write_text("{}\n", encoding="utf-8")
    (skill / "validation_report.json").write_text("{}\n", encoding="utf-8")
    (skill / "htmlcov" / "index.html").write_text("<html></html>\n", encoding="utf-8")
    return skill


def check_manifest(skill: Path) -> dict[str, Any]:
    manifest = build_package_manifest(skill)
    entries = sorted(str(arcname).replace("\\", "/") for _, arcname in manifest)
    prefix = f"{skill.name}/"
    required = {
        f"{prefix}SKILL.md",
        f"{prefix}references/README.md",
        f"{prefix}scripts/helper.py",
    }
    forbidden_fragments = [
        ".planning",
        "__pycache__",
        ".skill",
        ".token-savior-cache.json",
        "coverage.xml",
        "feedback.json",
        "validation_report.json",
        "reports/",
        "logs/",
        "htmlcov/",
    ]
    missing_required = sorted(required - set(entries))
    forbidden_entries = [
        entry for entry in entries
        if any(fragment in entry for fragment in forbidden_fragments)
    ]
    return {
        "entries": entries,
        "missing_required": missing_required,
        "forbidden_entries": forbidden_entries,
        "passed": not missing_required and not forbidden_entries,
    }


def check_secret_rejection(root: Path) -> dict[str, Any]:
    skill = write_fixture(root / "secret-fixture")
    marker = "api" + "_key = " + ("A" * 32)
    secret_file = skill / "references" / "credential-note.md"
    secret_file.write_text(marker + "\n", encoding="utf-8")
    try:
        build_package_manifest(skill)
    except ValueError as exc:
        return {
            "passed": "likely secret" in str(exc),
            "error": str(exc),
            "redaction_preserves_safe_text": redact_secrets("plain package note") == "plain package note",
        }
    return {
        "passed": False,
        "error": "Secret-like fixture was not rejected.",
        "redaction_preserves_safe_text": redact_secrets("plain package note") == "plain package note",
    }


def check_archive_rejection(root: Path) -> dict[str, Any]:
    unsafe_members = [
        "../escape.txt",
        "/absolute.txt",
        "C:/drive.txt",
        "safe/../../escape.txt",
        "safe\\..\\escape.txt",
    ]
    results: list[dict[str, Any]] = []
    for index, member in enumerate(unsafe_members, start=1):
        archive = root / f"unsafe-{index}.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr(member, "nope")
        try:
            with zipfile.ZipFile(archive, "r") as zf:
                safe_extract_archive(zf, root / f"extract-{index}")
        except ValueError as exc:
            results.append({"member": member, "rejected": True, "error": str(exc)})
        else:
            results.append({"member": member, "rejected": False, "error": ""})
    return {
        "passed": all(item["rejected"] for item in results),
        "cases": results,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_archive_roundtrip(skill: Path, root: Path) -> dict[str, Any]:
    output_dir = root / "archives"
    archive = package_skill(skill, output_dir=output_dir, verbose=False)
    if archive is None:
        return {"passed": False, "error": "package_skill returned None"}

    smoke = smoke_test(archive)
    with zipfile.ZipFile(archive, "r") as zf:
        entries = sorted(zf.namelist())
    forbidden_entries = [
        entry for entry in entries
        if any(fragment in entry for fragment in [".planning", "__pycache__", "coverage.xml", ".skill"])
    ]
    return {
        "passed": bool(smoke["passed"]) and not forbidden_entries,
        "archive": str(archive),
        "sha256": sha256_file(archive),
        "entry_count": len(entries),
        "forbidden_entries": forbidden_entries,
        "install_smoke_passed": bool(smoke["passed"]),
    }


def run_smoke(skill_root: Path) -> dict[str, Any]:
    _ = skill_root
    findings: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="skill_factory_package_boundary_") as tmp:
        root = Path(tmp)
        skill = write_fixture(root)
        manifest = check_manifest(skill)
        secret = check_secret_rejection(root)
        archive_rejection = check_archive_rejection(root)
        archive_roundtrip = check_archive_roundtrip(skill, root)

    checks = {
        "manifest": manifest,
        "secret_rejection": secret,
        "archive_rejection": archive_rejection,
        "archive_roundtrip": archive_roundtrip,
    }
    for name, check in checks.items():
        if not check.get("passed"):
            findings.append(finding("error", name, f"{name} failed"))
    errors = sum(1 for item in findings if item["severity"] == "error")
    return {
        "schema_version": "package-boundary-smoke-1.0",
        "valid": errors == 0,
        "summary": {"errors": errors, "warnings": 0},
        "checks": checks,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test package boundaries.")
    parser.add_argument("skill_path", nargs="?", default=".", help="Skill root, kept for CLI symmetry.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    report = run_smoke(Path(args.skill_path).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        status = "pass" if report["valid"] else "fail"
        print(f"package_boundary_smoke: {status}")
        print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
