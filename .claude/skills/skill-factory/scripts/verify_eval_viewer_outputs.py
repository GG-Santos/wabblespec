#!/usr/bin/env python3
"""Verify benchmark outputs are visible to eval-viewer-style scanners."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_MANIFEST_KEYS = {
    "agent",
    "category",
    "niche",
    "output_target",
    "created_at",
    "files",
    "entrypoint",
    "eval_viewer",
}

REQUIRED_SCORECARD_KEYS = {
    "output_quality",
    "token_usage",
    "structure_completeness",
    "domain_specificity",
    "safety_quality",
    "testability",
    "reuse_value",
}

REQUIRED_CHECK_KEYS = {
    "has_skill",
    "has_references",
    "has_templates",
    "has_scripts",
    "has_hooks",
    "has_agents",
    "has_mcp",
    "appears_in_eval_viewer",
}

SLUG_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def finding(severity: str, code: str, path: Path, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "path": str(path), "message": message}


def load_json(path: Path, findings: list[dict[str, str]]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append(finding("error", "invalid_json", path, str(exc)))
    except OSError as exc:
        findings.append(finding("error", "unreadable_json", path, str(exc)))
    return None


def validate_manifest(
    manifest_path: Path,
    root: Path,
    findings: list[dict[str, str]],
    require_visible_true: bool,
    strict_files: bool,
    require_readme: bool,
) -> None:
    data = load_json(manifest_path, findings)
    if not isinstance(data, dict):
        findings.append(finding("error", "manifest_not_object", manifest_path, "manifest.json must contain a JSON object."))
        return

    missing = sorted(REQUIRED_MANIFEST_KEYS - set(data))
    if missing:
        findings.append(finding("error", "manifest_missing_keys", manifest_path, f"Missing keys: {missing}"))

    for key in ("category", "niche", "output_target"):
        value = data.get(key)
        if not isinstance(value, str) or not SLUG_RE.fullmatch(value):
            findings.append(finding("error", "unstable_slug", manifest_path, f"{key} must be snake_case slug, got {value!r}."))

    relative_parts = manifest_path.relative_to(root).parts
    if len(relative_parts) >= 5:
        _, category, niche, output_target, filename = relative_parts[-5:]
        if filename == "manifest.json":
            expected = {"category": category, "niche": niche, "output_target": output_target}
            for key, path_value in expected.items():
                if data.get(key) != path_value:
                    findings.append(finding("error", "manifest_path_mismatch", manifest_path, f"{key}={data.get(key)!r} does not match path segment {path_value!r}."))

    files = data.get("files")
    if not isinstance(files, list) or not all(isinstance(item, str) and item for item in files):
        findings.append(finding("error", "manifest_files_invalid", manifest_path, "files must be a list of non-empty relative paths."))
        files = []

    entrypoint = data.get("entrypoint")
    if not isinstance(entrypoint, str) or not entrypoint:
        findings.append(finding("error", "manifest_entrypoint_invalid", manifest_path, "entrypoint must be a non-empty relative path."))
    elif not (manifest_path.parent / entrypoint).is_file():
        findings.append(finding("error", "entrypoint_missing", manifest_path, f"Entrypoint file does not exist: {entrypoint}"))

    if require_readme and not (manifest_path.parent / "README.md").is_file():
        findings.append(finding("error", "readme_missing", manifest_path, "README.md is required for viewer ingestion."))

    viewer = data.get("eval_viewer")
    if not isinstance(viewer, dict):
        findings.append(finding("error", "eval_viewer_invalid", manifest_path, "eval_viewer must be an object."))
    else:
        if require_visible_true and viewer.get("visible") is not True:
            findings.append(finding("error", "eval_viewer_not_visible", manifest_path, "eval_viewer.visible must be true."))
        if not isinstance(viewer.get("title"), str) or not viewer.get("title", "").strip():
            findings.append(finding("error", "eval_viewer_title_missing", manifest_path, "eval_viewer.title is required."))

    if strict_files:
        for item in files:
            candidate = manifest_path.parent / item
            try:
                candidate.resolve().relative_to(manifest_path.parent.resolve())
            except ValueError:
                findings.append(finding("error", "manifest_file_escapes_root", manifest_path, f"files entry escapes task root: {item}"))
                continue
            if not candidate.is_file():
                findings.append(finding("error", "manifest_file_missing", manifest_path, f"files entry missing: {item}"))


def validate_eval(eval_path: Path, findings: list[dict[str, str]]) -> None:
    data = load_json(eval_path, findings)
    if not isinstance(data, dict):
        findings.append(finding("error", "eval_not_object", eval_path, "eval.json must contain a JSON object."))
        return

    scorecard = data.get("scorecard")
    if not isinstance(scorecard, dict):
        findings.append(finding("error", "scorecard_missing", eval_path, "scorecard must be an object."))
    else:
        missing = sorted(REQUIRED_SCORECARD_KEYS - set(scorecard))
        if missing:
            findings.append(finding("error", "scorecard_missing_keys", eval_path, f"Missing scorecard keys: {missing}"))
        for key, value in scorecard.items():
            if key in REQUIRED_SCORECARD_KEYS and value is not None and not isinstance(value, (int, float)):
                findings.append(finding("error", "scorecard_value_invalid", eval_path, f"{key} must be null or numeric."))

    checks = data.get("checks")
    if not isinstance(checks, dict):
        findings.append(finding("error", "checks_missing", eval_path, "checks must be an object."))
    else:
        missing = sorted(REQUIRED_CHECK_KEYS - set(checks))
        if missing:
            findings.append(finding("error", "checks_missing_keys", eval_path, f"Missing check keys: {missing}"))
        for key, value in checks.items():
            if key in REQUIRED_CHECK_KEYS and not isinstance(value, bool):
                findings.append(finding("error", "check_value_invalid", eval_path, f"{key} must be boolean."))

    if not isinstance(data.get("notes"), list):
        findings.append(finding("error", "notes_invalid", eval_path, "notes must be a list."))


def verify_outputs(
    root: Path,
    require_manifest: bool = False,
    require_eval_json: bool = False,
    require_visible_true: bool = False,
    strict_files: bool = False,
    require_readme: bool = False,
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    root = root.resolve()

    if not root.exists():
        findings.append(finding("error", "root_missing", root, "Benchmark root does not exist."))
        manifests: list[Path] = []
    else:
        manifests = sorted(root.rglob("manifest.json"))

    if require_manifest and not manifests:
        findings.append(finding("error", "manifest_none_found", root, "No manifest.json files found."))

    eval_count = 0
    for manifest in manifests:
        validate_manifest(manifest, root, findings, require_visible_true, strict_files, require_readme)
        eval_path = manifest.parent / "eval.json"
        if eval_path.exists():
            eval_count += 1
            validate_eval(eval_path, findings)
        elif require_eval_json:
            findings.append(finding("error", "eval_json_missing", manifest.parent, "Missing eval.json next to manifest.json."))

    errors = sum(1 for item in findings if item["severity"] == "error")
    warnings = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "schema_version": "eval-viewer-output-verification-1.0",
        "valid": errors == 0,
        "root": str(root),
        "summary": {
            "manifests": len(manifests),
            "eval_json": eval_count,
            "errors": errors,
            "warnings": warnings,
        },
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify eval-viewer benchmark outputs.")
    parser.add_argument("--root", type=Path, required=True, help="Root containing benchmark output folders.")
    parser.add_argument("--require-manifest", action="store_true", help="Fail if no manifest.json files are found.")
    parser.add_argument("--require-eval-json", action="store_true", help="Require eval.json next to every manifest.json.")
    parser.add_argument("--require-visible-true", action="store_true", help="Require manifest eval_viewer.visible=true.")
    parser.add_argument("--strict-files", action="store_true", help="Require every manifest files[] entry to exist.")
    parser.add_argument("--require-readme", action="store_true", help="Require README.md next to every manifest.json.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable report.")
    args = parser.parse_args()

    report = verify_outputs(
        root=args.root,
        require_manifest=args.require_manifest,
        require_eval_json=args.require_eval_json,
        require_visible_true=args.require_visible_true,
        strict_files=args.strict_files,
        require_readme=args.require_readme,
    )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        status = "PASS" if report["valid"] else "FAIL"
        summary = report["summary"]
        print(
            f"verify_eval_viewer_outputs: {status} "
            f"manifests={summary['manifests']} eval_json={summary['eval_json']} "
            f"errors={summary['errors']} warnings={summary['warnings']}"
        )
        for item in report["findings"]:
            print(f"[{item['severity']}] {item['code']}: {item['path']}: {item['message']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
