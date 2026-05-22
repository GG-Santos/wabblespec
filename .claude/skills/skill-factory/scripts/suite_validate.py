#!/usr/bin/env python3
"""Validate a multi-skill suite manifest and member skills."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by environment setup
    raise SystemExit("PyYAML is required for suite validation") from exc

try:
    from scripts.check_schema_drift import check_schema_drift
    from scripts.lint_prompts import lint_directory
    from scripts.quick_validate import validate_skill_report
except ModuleNotFoundError:  # Allows `python scripts/suite_validate.py ...`.
    from check_schema_drift import check_schema_drift
    from lint_prompts import lint_directory
    from quick_validate import validate_skill_report


def load_suite(suite_root: Path) -> tuple[Path, dict[str, Any]]:
    suite_path = suite_root / "suite.yaml"
    if not suite_path.exists():
        raise ValueError(f"suite.yaml not found in {suite_root}")
    data = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("suite"), dict):
        raise ValueError("suite.yaml must contain a top-level 'suite' object")
    return suite_path, data["suite"]


def _safe_member_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    path.relative_to(root.resolve())
    return path


def _safe_surface_path(root: Path, value: str) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        raise ValueError(f"absolute plugin surface path: {value}")
    path = (root / raw).resolve()
    path.relative_to(root.resolve())
    return path


def _surface_paths(payload: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(payload, str):
        paths.append(payload)
    elif isinstance(payload, list):
        for item in payload:
            paths.extend(_surface_paths(item))
    elif isinstance(payload, dict):
        for value in payload.values():
            paths.extend(_surface_paths(value))
    return [path for path in paths if path and not path.startswith("python ")]


def _looks_like_surface_path(value: str) -> bool:
    suffixes = (
        ".css", ".csv", ".html", ".js", ".json", ".md", ".py", ".ts",
        ".txt", ".xml", ".yaml", ".yml",
    )
    return "/" in value or "\\" in value or value.endswith(suffixes)


def _write_disambiguation(root: Path, members: list[dict[str, Any]], overlaps: list[str]) -> None:
    lines = ["# Activation Disambiguation", ""]
    for member in members:
        tokens = member.get("activates_on") or []
        lines.append(f"## {member.get('id', '<missing-id>')}")
        lines.append("")
        lines.append(", ".join(str(token) for token in tokens) or "(no activation tokens)")
        lines.append("")
    if overlaps:
        lines.append("## Overlaps")
        lines.append("")
        lines.extend(f"- {item}" for item in overlaps)
        lines.append("")
    (root / "disambiguation.md").write_text("\n".join(lines), encoding="utf-8")


def validate_suite(suite_root: str | Path, strict: bool = True) -> dict[str, Any]:
    root = Path(suite_root).resolve()
    suite_path, suite = load_suite(root)

    errors: list[str] = []
    warnings: list[str] = []
    member_reports: dict[str, Any] = {}
    members = suite.get("members") or []
    if not isinstance(members, list) or not members:
        errors.append("suite.members must be a non-empty list")
        members = []

    member_ids: set[str] = set()
    member_paths: dict[str, Path] = {}
    activation_tokens: dict[str, set[str]] = {}

    for index, member in enumerate(members, start=1):
        if not isinstance(member, dict):
            errors.append(f"member {index} must be an object")
            continue
        member_id = str(member.get("id", "")).strip()
        if not member_id:
            errors.append(f"member {index} missing id")
            continue
        if member_id in member_ids:
            errors.append(f"duplicate member id: {member_id}")
            continue
        member_ids.add(member_id)

        try:
            member_path = _safe_member_path(root, str(member.get("path", "")))
        except Exception:
            errors.append(f"member {member_id} path escapes suite root")
            continue
        member_paths[member_id] = member_path
        if not (member_path / "SKILL.md").exists():
            errors.append(f"member {member_id} missing SKILL.md at {member_path}")
            continue

        report = validate_skill_report(member_path, strict=strict)
        member_reports[member_id] = report
        if not report["valid"]:
            errors.append(f"member {member_id} failed validation: {report['message']}")

        lint_errors = [item for item in lint_directory(member_path) if item.level == "ERROR"]
        if lint_errors:
            errors.append(f"member {member_id} has lint errors: {len(lint_errors)}")

        tokens = {
            str(token).strip().lower()
            for token in (member.get("activates_on") or [])
            if str(token).strip()
        }
        activation_tokens[member_id] = tokens

    handoffs = suite.get("handoffs") or []
    produced_or_existing = set()
    for member in members:
        if isinstance(member, dict):
            for key in ("consumes_schema", "produces_schema"):
                if isinstance(member.get(key), str):
                    produced_or_existing.add(member[key])

    for index, handoff in enumerate(handoffs, start=1):
        if not isinstance(handoff, dict):
            errors.append(f"handoff {index} must be an object")
            continue
        for key in ("from", "to"):
            if handoff.get(key) not in member_ids:
                errors.append(f"handoff {index} references unknown {key}: {handoff.get(key)}")
        via = handoff.get("via")
        if isinstance(via, str) and via not in produced_or_existing and not (root / via).exists():
            errors.append(f"handoff {index} via schema not found or produced: {via}")

    overlaps: list[str] = []
    ids = sorted(activation_tokens)
    for left_index, left in enumerate(ids):
        for right in ids[left_index + 1:]:
            shared = activation_tokens[left] & activation_tokens[right]
            if shared:
                overlaps.append(f"{left} <-> {right}: {', '.join(sorted(shared))}")
    if overlaps and not suite.get("activation_disambiguation"):
        warnings.append("activation overlap exists without activation_disambiguation")

    refusals = ((suite.get("safety") or {}).get("suite_wide_refusals") or [])
    if refusals:
        for member_id, member_path in member_paths.items():
            text = (member_path / "SKILL.md").read_text(encoding="utf-8")
            if "suite" not in text.lower() and "refusal" not in text.lower():
                warnings.append(f"member {member_id} does not visibly reference suite-wide refusals")

    plugin_dir = root / "plugin"
    if plugin_dir.exists():
        registry_path = plugin_dir / "surfaces.json"
        if not registry_path.exists():
            errors.append("plugin/surfaces.json missing")
        else:
            try:
                registry = json.loads(registry_path.read_text(encoding="utf-8"))
                for surface in _surface_paths(registry):
                    if _looks_like_surface_path(surface):
                        try:
                            surface_path = _safe_surface_path(root, surface)
                        except ValueError:
                            errors.append(f"plugin surface path escapes suite root: {surface}")
                            continue
                        if not surface_path.exists():
                            errors.append(f"plugin surface path missing: {surface}")
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"plugin/surfaces.json invalid: {exc}")

    drift = check_schema_drift(suite_path)
    errors.extend(drift["errors"])
    warnings.extend(drift["warnings"])
    _write_disambiguation(root, members, overlaps)

    return {
        "suite_root": str(root),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "members": member_reports,
        "schema_drift": drift,
        "disambiguation": str(root / "disambiguation.md"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a multi-skill suite")
    parser.add_argument("suite_root", type=Path, help="Directory containing suite.yaml")
    parser.add_argument("--no-strict", action="store_true", help="Skip member support-file checks")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    try:
        report = validate_suite(args.suite_root, strict=not args.no_strict)
    except Exception as exc:
        report = {
            "suite_root": str(args.suite_root),
            "valid": False,
            "errors": [str(exc)],
            "warnings": [],
            "members": {},
            "schema_drift": {},
            "disambiguation": None,
        }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "pass" if report["valid"] else "fail"
        print(f"suite validation: {status}")
        for warning in report["warnings"]:
            print(f"  warning: {warning}")
        for error in report["errors"]:
            print(f"  error: {error}")
        if report["disambiguation"]:
            print(f"  wrote: {report['disambiguation']}")

    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
