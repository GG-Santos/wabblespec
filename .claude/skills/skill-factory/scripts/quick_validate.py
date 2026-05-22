#!/usr/bin/env python3
"""Quick validation script for skills."""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from scripts.validation import (
        domain_fit_analysis,
        skill_quality_metrics,
        validate_phase1_skill_content,
        validate_phase2_skill_content,
        validate_phase3_skill_content,
    )
except ModuleNotFoundError:  # Allows `python scripts/quick_validate.py ...`.
    from validation import (
        domain_fit_analysis,
        skill_quality_metrics,
        validate_phase1_skill_content,
        validate_phase2_skill_content,
        validate_phase3_skill_content,
    )

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


ALLOWED_PROPERTIES = {
    "name",
    "description",
    "license",
    "metadata",
    "compatibility",
    "required-capabilities",
    "required_capabilities",
}


def finding(severity: str, code: str, message: str, repair: str = "") -> dict:
    return {"severity": severity, "code": code, "message": message, "repair": repair}


def base_report(skill_path: Path) -> dict:
    return {
        "schema_version": "validation-report-1.0",
        "skill_path": str(skill_path),
        "valid": False,
        "message": "",
        "summary": {},
        "frontmatter_keys": [],
        "metrics": {},
        "domain_fit": {},
        "findings": [],
    }


def finalize_report(report: dict) -> dict:
    findings = report["findings"]
    counts = {
        "errors": sum(1 for item in findings if item["severity"] == "error"),
        "warnings": sum(1 for item in findings if item["severity"] == "warning"),
        "info": sum(1 for item in findings if item["severity"] == "info"),
    }
    report["valid"] = counts["errors"] == 0
    report["summary"] = {
        **counts,
        "score": max(0.0, round(1.0 - counts["errors"] * 0.25 - counts["warnings"] * 0.05, 3)),
        "domain_fit_score": report.get("domain_fit", {}).get("score"),
    }
    first_error = next((item for item in findings if item["severity"] == "error"), None)
    if first_error:
        report["message"] = f"{first_error['code']}: {first_error['message']} Repair: {first_error['repair']}"
    else:
        report["message"] = "Skill is valid!"
    return report


def parse_frontmatter(frontmatter_text: str) -> dict:
    if HAS_YAML:
        data = yaml.safe_load(frontmatter_text)
        if not isinstance(data, dict):
            raise TypeError("Frontmatter must be a YAML dictionary")
        return data

    data = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip("\"").strip("'")
    return data


def extract_frontmatter(content: str) -> str:
    """Return frontmatter text when delimiters are exact standalone lines."""
    lines = content.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with a line containing only ---")
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return "\n".join(lines[1:index])
    raise ValueError("Close the frontmatter with a line containing only ---")


def _artifact_check_findings(skill_path: Path) -> tuple[list[dict], dict]:
    """Run optional support-file checks beyond SKILL.md."""
    findings: list[dict] = []
    checks: dict = {}

    try:
        from scripts.syntax_check import check_python_syntax
    except ModuleNotFoundError:
        from syntax_check import check_python_syntax

    syntax = check_python_syntax([skill_path])
    checks["syntax_check"] = syntax
    for failure in syntax.get("failures", []):
        findings.append(finding(
            "error",
            "python_syntax_error",
            f"{failure['path']}: {failure['error']}",
            "Fix generated Python support files before packaging.",
        ))

    try:
        from scripts.lint_prompts import lint_directory
    except ModuleNotFoundError:
        from lint_prompts import lint_directory

    lint_results = lint_directory(skill_path)
    lint_payload = [
        {
            "level": item.level,
            "rule": item.rule,
            "message": item.message,
            "file": item.file,
            "line": item.line,
        }
        for item in lint_results
        if item.level in {"ERROR", "WARNING"}
    ]
    checks["lint_prompts"] = lint_payload
    for item in lint_results:
        if item.level == "ERROR":
            findings.append(finding(
                "error",
                f"lint_{item.rule}",
                f"{item.file}:{item.line}: {item.message}",
                "Fix the lint error or move fixture text into a skipped test fixture.",
            ))
        elif item.level == "WARNING":
            findings.append(finding(
                "warning",
                f"lint_{item.rule}",
                f"{item.file}:{item.line}: {item.message}",
                "Review the lint warning before release.",
            ))

    return findings, checks


def validate_skill_report(skill_path, strict: bool = False):
    """Return machine-readable validation_report.json-style data."""
    skill_path = Path(skill_path)
    report = base_report(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        report["findings"].append(finding("error", "missing_skill_md", "SKILL.md not found", "Create SKILL.md at the skill root."))
        return finalize_report(report)

    try:
        content = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report["findings"].append(finding("error", "invalid_utf8", "SKILL.md is not valid UTF-8", "Rewrite the file as UTF-8."))
        return finalize_report(report)

    report["metrics"] = skill_quality_metrics(content)
    if not content.splitlines() or content.splitlines()[0] != "---":
        report["findings"].append(finding("error", "missing_frontmatter", "No YAML frontmatter found", "Start SKILL.md with YAML frontmatter."))
        return finalize_report(report)

    try:
        frontmatter_text = extract_frontmatter(content)
    except ValueError as exc:
        report["findings"].append(finding("error", "invalid_frontmatter_format", "Invalid frontmatter format", "Close the frontmatter with a line containing only ---."))
        return finalize_report(report)
    try:
        frontmatter = parse_frontmatter(frontmatter_text)
    except Exception as exc:
        report["findings"].append(finding("error", "invalid_frontmatter", f"Invalid frontmatter: {exc}", "Fix YAML frontmatter."))
        return finalize_report(report)

    report["frontmatter_keys"] = sorted(frontmatter.keys())

    unexpected = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected:
        report["findings"].append(finding("error", "unexpected_frontmatter_keys", f"Unexpected frontmatter fields: {', '.join(sorted(unexpected))}.", "Remove unsupported frontmatter fields."))

    if "name" not in frontmatter:
        report["findings"].append(finding("error", "missing_name", "Missing 'name' in frontmatter", "Add name: <kebab-case-name>."))
    if "description" not in frontmatter:
        report["findings"].append(finding("error", "missing_description", "Missing 'description' in frontmatter", "Add description: <trigger and purpose>."))

    name = frontmatter.get("name", "") or ""
    if not isinstance(name, str):
        report["findings"].append(finding("error", "name_not_string", f"Name must be a string, got {type(name).__name__}", "Use a string name."))
        name = ""
    name = name.strip()
    if not name:
        report["findings"].append(finding("error", "empty_name", "Name cannot be empty", "Add a kebab-case name."))
    elif not re.match(r"^[a-z0-9-]+$", name):
        report["findings"].append(finding("error", "invalid_name", f"Name '{name}' should be kebab-case.", "Use lowercase letters, digits, and single hyphens."))
    if name.startswith("-") or name.endswith("-") or "--" in name:
        report["findings"].append(finding("error", "invalid_name_hyphen", f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens", "Remove leading/trailing/consecutive hyphens."))
    if len(name) > 64:
        report["findings"].append(finding("error", "name_too_long", f"Name is too long ({len(name)} characters). Maximum is 64 characters.", "Shorten name to <=64 characters."))

    description = frontmatter.get("description", "") or ""
    if not isinstance(description, str):
        report["findings"].append(finding("error", "description_not_string", f"Description must be a string, got {type(description).__name__}", "Use a string description."))
        description = ""
    description = description.strip()
    if not description:
        report["findings"].append(finding("error", "empty_description", "Description cannot be empty", "Add a trigger-focused description."))
    if "<" in description or ">" in description:
        report["findings"].append(finding("error", "description_angle_brackets", "Description cannot contain angle brackets (< or >)", "Remove angle brackets from description."))
    if len(description) > 1024:
        report["findings"].append(finding("error", "description_too_long", f"Description is too long ({len(description)} characters). Maximum is 1024 characters.", "Shorten description to <=1024 characters."))

    compatibility = frontmatter.get("compatibility", "")
    if compatibility:
        if not isinstance(compatibility, str):
            report["findings"].append(finding("error", "compatibility_not_string", f"Compatibility must be a string, got {type(compatibility).__name__}", "Use a string compatibility field."))
        elif len(compatibility) > 500:
            report["findings"].append(finding("error", "compatibility_too_long", f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters.", "Shorten compatibility to <=500 characters."))

    report["domain_fit"] = domain_fit_analysis(content, description)
    report["findings"].extend(validate_phase1_skill_content(content, description))
    report["findings"].extend(validate_phase2_skill_content(content, description))
    report["findings"].extend(validate_phase3_skill_content(content, description))
    report["metrics"] = skill_quality_metrics(content)
    if strict:
        artifact_findings, artifact_checks = _artifact_check_findings(skill_path)
        report["artifact_checks"] = artifact_checks
        report["findings"].extend(artifact_findings)

    return finalize_report(report)


def validate_skill(skill_path, strict: bool = False):
    """Backward-compatible `(valid, message)` API."""
    report = validate_skill_report(skill_path, strict=strict)
    return report["valid"], report["message"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a skill directory")
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--strict", action="store_true", help="Also check support files, lint, and Python syntax")
    parser.add_argument("--json", action="store_true", help="Print validation_report.json to stdout")
    parser.add_argument("--report", type=Path, help="Write validation_report.json to this path")
    args = parser.parse_args()

    report = validate_skill_report(args.skill_directory, strict=args.strict)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(report["message"])
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
