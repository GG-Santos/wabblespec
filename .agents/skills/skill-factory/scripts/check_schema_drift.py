#!/usr/bin/env python3
"""Validate suite schema references and catch duplicate-name drift."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by environment setup
    raise SystemExit("PyYAML is required for suite schema validation") from exc


def load_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("suite"), dict):
        raise ValueError("suite.yaml must contain a top-level 'suite' object")
    return data["suite"]


def schema_refs(suite: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for member in suite.get("members", []) or []:
        if not isinstance(member, dict):
            continue
        for key in ("consumes_schema", "produces_schema"):
            value = member.get(key)
            if isinstance(value, str) and value:
                refs.append(value)
    for handoff in suite.get("handoffs", []) or []:
        if isinstance(handoff, dict) and isinstance(handoff.get("via"), str):
            refs.append(handoff["via"])
    return refs


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_schema_drift(suite_path: str | Path) -> dict[str, Any]:
    suite_path = Path(suite_path).resolve()
    suite_root = suite_path.parent
    suite = load_suite(suite_path)

    errors: list[str] = []
    warnings: list[str] = []
    refs = sorted(set(schema_refs(suite)))

    resolved: dict[str, Path] = {}
    for ref in refs:
        path = (suite_root / ref).resolve()
        try:
            path.relative_to(suite_root)
        except ValueError:
            errors.append(f"Schema reference escapes suite root: {ref}")
            continue
        if not path.exists():
            errors.append(f"Schema reference not found: {ref}")
            continue
        if not path.is_file():
            errors.append(f"Schema reference is not a file: {ref}")
            continue
        resolved[ref] = path

    by_name: dict[str, list[tuple[str, str]]] = {}
    for ref, path in resolved.items():
        by_name.setdefault(path.name, []).append((ref, file_digest(path)))
    for name, entries in by_name.items():
        digests = {digest for _, digest in entries}
        if len(entries) > 1 and len(digests) > 1:
            refs_text = ", ".join(ref for ref, _ in entries)
            errors.append(f"Schema basename drift for {name}: {refs_text}")
        elif len(entries) > 1:
            refs_text = ", ".join(ref for ref, _ in entries)
            warnings.append(f"Duplicate schema basename with identical content for {name}: {refs_text}")

    return {
        "suite_path": str(suite_path),
        "schema_refs": refs,
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check schema references in a skill suite")
    parser.add_argument("suite_yaml", type=Path, help="Path to suite.yaml")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    try:
        report = check_schema_drift(args.suite_yaml)
    except Exception as exc:
        report = {
            "suite_path": str(args.suite_yaml),
            "schema_refs": [],
            "errors": [str(exc)],
            "warnings": [],
            "valid": False,
        }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "pass" if report["valid"] else "fail"
        print(f"schema drift check: {status}")
        for warning in report["warnings"]:
            print(f"  warning: {warning}")
        for error in report["errors"]:
            print(f"  error: {error}")

    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
