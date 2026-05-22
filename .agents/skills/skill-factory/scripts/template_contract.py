#!/usr/bin/env python3
"""Validate root template placeholder contracts.

The root ``templates/*.j2`` files are source templates until the generator
renderer is wired in. This module keeps their required context explicit enough
to test without adding a template engine dependency.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PLACEHOLDER_RE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")
UNRESOLVED_RE = re.compile(r"{{.*?}}")


def _finding(
    severity: str,
    code: str,
    template: str,
    message: str,
    field: str | None = None,
) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "severity": severity,
        "code": code,
        "template": template,
        "message": message,
    }
    if field:
        finding["field"] = field
    return finding


def template_dir(skill_root: Path) -> Path:
    """Return the root template catalog directory for a skill package."""
    return skill_root / "templates"


def iter_root_templates(skill_root: Path) -> list[Path]:
    """Return root ``*.j2`` templates in deterministic order."""
    root = template_dir(skill_root)
    if not root.exists():
        return []
    return sorted(path for path in root.glob("*.j2") if path.is_file())


def extract_placeholders(template_text: str) -> list[str]:
    """Extract simple identifier placeholders from template text."""
    return sorted(set(PLACEHOLDER_RE.findall(template_text)))


def template_inventory(skill_root: Path) -> dict[str, list[str]]:
    """Map each root template filename to sorted required context fields."""
    inventory: dict[str, list[str]] = {}
    for template_path in iter_root_templates(skill_root):
        text = template_path.read_text(encoding="utf-8")
        inventory[template_path.name] = extract_placeholders(text)
    return inventory


def _sample_value(field: str) -> Any:
    """Return a stable sample value for smoke-rendering a placeholder."""
    json_list_fields = {
        "agents_json",
        "assertions_json",
        "capabilities_json",
        "commands_json",
        "evaluations_json",
        "hook_scripts_json",
        "required_capabilities_json",
        "required_fields_json",
        "schemas_json",
        "templates_json",
        "trigger_evals_json",
    }
    json_object_fields = {
        "properties_json",
        "response_json",
    }
    boolean_fields = {
        "additional_properties",
        "destructive_hint",
        "idempotent_hint",
        "open_world_hint",
        "read_only_hint",
    }
    markdown_fields = {
        "changed_files",
        "fields_table",
        "findings",
        "operators_table",
        "remaining_risks",
        "summary",
        "verification",
    }

    if field in json_list_fields:
        return []
    if field in json_object_fields:
        return {}
    if field in boolean_fields:
        return False
    if field == "generated_at":
        return "2026-05-19T00:00:00Z"
    if field == "function_name":
        return "run_sample_tool"
    if field == "input_model":
        return "SampleInput"
    if field.endswith("_version"):
        return "0.1.0"
    if field in markdown_fields:
        return f"- sample {field.replace('_', ' ')}"
    return f"sample-{field.replace('_', '-')}"


def sample_context(fields: list[str]) -> dict[str, Any]:
    """Build a valid context fixture for the provided fields."""
    return {field: _sample_value(field) for field in fields}


def _render_value(value: Any) -> str:
    """Convert context values into template substitution text."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=True, sort_keys=True)
    return str(value)


def validate_context(
    template_name: str,
    required_fields: list[str],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compare supplied context keys with required template fields."""
    required = set(required_fields)
    provided = set(context)
    findings: list[dict[str, Any]] = []

    for field in sorted(required - provided):
        findings.append(_finding(
            "error",
            "missing_context_field",
            template_name,
            f"Template {template_name} requires context field {field}.",
            field,
        ))

    for field in sorted(provided - required):
        findings.append(_finding(
            "warning",
            "unused_context_field",
            template_name,
            f"Context field {field} is not used by template {template_name}.",
            field,
        ))

    return findings


def render_template_text(
    template_name: str,
    template_text: str,
    context: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    """Render simple placeholders and report unresolved template syntax."""
    findings: list[dict[str, Any]] = []

    def replace(match: re.Match[str]) -> str:
        field = match.group(1)
        if field not in context:
            return match.group(0)
        return _render_value(context[field])

    rendered = PLACEHOLDER_RE.sub(replace, template_text)
    unresolved = sorted(set(UNRESOLVED_RE.findall(rendered)))
    for token in unresolved:
        findings.append(_finding(
            "error",
            "unresolved_placeholder",
            template_name,
            f"Unresolved placeholder remains after dry render: {token}.",
        ))

    return rendered, findings


def check_template(
    template_path: Path,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate and dry-render one template."""
    text = template_path.read_text(encoding="utf-8")
    fields = extract_placeholders(text)
    active_context = sample_context(fields) if context is None else context
    findings = validate_context(template_path.name, fields, active_context)

    if not any(item["severity"] == "error" for item in findings):
        _, render_findings = render_template_text(template_path.name, text, active_context)
        findings.extend(render_findings)

    error_count = sum(1 for item in findings if item["severity"] == "error")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "template": template_path.name,
        "fields": fields,
        "field_count": len(fields),
        "valid": error_count == 0,
        "summary": {
            "errors": error_count,
            "warnings": warning_count,
        },
        "findings": findings,
    }


def check_skill_templates(
    skill_root: Path,
    template_name: str | None = None,
    context: dict[str, Any] | None = None,
    inventory_only: bool = False,
) -> dict[str, Any]:
    """Validate the root template catalog for a skill package."""
    templates = iter_root_templates(skill_root)
    if template_name:
        templates = [path for path in templates if path.name == template_name]

    findings: list[dict[str, Any]] = []
    if not templates:
        message = (
            f"Root template {template_name} was not found."
            if template_name
            else "No root templates/*.j2 files were found."
        )
        findings.append(_finding("error", "missing_template", template_name or "*", message))

    template_results: dict[str, Any] = {}
    for template_path in templates:
        if inventory_only:
            fields = extract_placeholders(template_path.read_text(encoding="utf-8"))
            result = {
                "template": template_path.name,
                "fields": fields,
                "field_count": len(fields),
                "valid": True,
                "summary": {"errors": 0, "warnings": 0},
                "findings": [],
            }
        else:
            result = check_template(template_path, context=context)
        template_results[template_path.name] = result
        findings.extend(result["findings"])

    errors = sum(1 for item in findings if item["severity"] == "error")
    warnings = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "schema_version": "template-contract-1.0",
        "skill_path": str(skill_root),
        "valid": errors == 0,
        "summary": {
            "templates": len(template_results),
            "fields": sum(result["field_count"] for result in template_results.values()),
            "errors": errors,
            "warnings": warnings,
        },
        "templates": template_results,
        "findings": findings,
    }


def _load_context(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Context file must contain a JSON object.")
    return data


def _format_text_report(report: dict[str, Any]) -> str:
    status = "valid" if report["valid"] else "invalid"
    lines = [
        f"Template contract: {status}",
        (
            f"Templates: {report['summary']['templates']} | "
            f"Fields: {report['summary']['fields']} | "
            f"Errors: {report['summary']['errors']} | "
            f"Warnings: {report['summary']['warnings']}"
        ),
    ]
    for finding in report["findings"]:
        field = f" ({finding['field']})" if "field" in finding else ""
        lines.append(
            f"[{finding['severity']}] {finding['template']}{field}: "
            f"{finding['message']}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate root templates/*.j2 placeholder contracts.",
    )
    parser.add_argument(
        "skill_path",
        nargs="?",
        default=".",
        help="Skill package root containing templates/*.j2.",
    )
    parser.add_argument(
        "--template",
        help="Validate one root template filename, for example agent.md.j2.",
    )
    parser.add_argument(
        "--context",
        type=Path,
        help="JSON object used as the template context. Defaults to generated sample context.",
    )
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="Only report required fields; skip context validation and dry render.",
    )
    parser.add_argument("--json", action="store_true", help="Write machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    skill_root = Path(args.skill_path).resolve()
    try:
        context = _load_context(args.context) if args.context else None
        report = check_skill_templates(
            skill_root,
            template_name=args.template,
            context=context,
            inventory_only=args.inventory_only,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "schema_version": "template-contract-1.0",
            "skill_path": str(skill_root),
            "valid": False,
            "summary": {"templates": 0, "fields": 0, "errors": 1, "warnings": 0},
            "templates": {},
            "findings": [
                _finding("error", "template_contract_error", args.template or "*", str(exc)),
            ],
        }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_format_text_report(report))

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
