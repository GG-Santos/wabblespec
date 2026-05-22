#!/usr/bin/env python3
"""Exhaustively review benchmark outputs for machine-checkable quality risks."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from scripts.materialize_benchmark_outputs import category_profile, text_value
except ModuleNotFoundError:  # Allows `python scripts/exhaustive_benchmark_review.py`.
    from materialize_benchmark_outputs import category_profile, text_value


SCORECARD_KEYS = [
    "output_quality",
    "token_usage",
    "structure_completeness",
    "domain_specificity",
    "safety_quality",
    "testability",
    "reuse_value",
]

CHECK_KEYS = [
    "has_skill",
    "has_references",
    "has_templates",
    "has_scripts",
    "has_hooks",
    "has_agents",
    "has_mcp",
    "appears_in_eval_viewer",
]

SKILL_SECTIONS = [
    "## Purpose",
    "## Domain Lens",
    "## Activation Conditions",
    "## Workflow",
    "## Output Contract",
    "## Safety Boundaries",
    "## Failure Modes",
    "## Evaluation Checklist",
    "## Example",
]

SYSTEM_SHARED_FILES = [
    "shared-interface.md",
    "shared-safety.md",
    "shared-evaluation.md",
    "routing.md",
]

STOPWORDS = {
    "that",
    "this",
    "with",
    "from",
    "into",
    "while",
    "using",
    "skill",
    "help",
    "safe",
    "offer",
    "tasks",
    "task",
    "output",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def finding(severity: str, code: str, path: Path, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "path": str(path), "message": message}


def text_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.split(r"[^a-z0-9]+", value.lower())
        if len(token) >= 4 and token not in STOPWORDS
    }


def token_coverage(source: str, expected: str, minimum: int = 2) -> bool:
    tokens = text_tokens(expected)
    if not tokens:
        return True
    source_tokens = text_tokens(source)
    required = min(len(tokens), max(1, minimum))
    return len(tokens & source_tokens) >= required


def expected_checks(task: dict[str, Any]) -> dict[str, bool]:
    folders = set(task.get("output_target", {}).get("folders", []))
    return {
        "has_skill": True,
        "has_references": "references" in folders,
        "has_templates": "templates" in folders,
        "has_scripts": "scripts" in folders,
        "has_hooks": "hooks" in folders,
        "has_agents": "agents" in folders,
        "has_mcp": "mcp" in folders,
        "appears_in_eval_viewer": True,
    }


def expected_files(task: dict[str, Any]) -> list[str]:
    target = task.get("output_target", {})
    folders = set(target.get("folders", []))
    skill_count = int(target.get("skill_count", 1))
    files = ["README.md", "prompt.txt", "task.json", "manifest.json", "eval.json"]
    if skill_count > 1:
        files.extend(SYSTEM_SHARED_FILES)
        files.extend(f"skills/skill-{index:02d}/SKILL.md" for index in range(1, skill_count + 1))
        if "evaluation" in folders:
            files.append("evaluation-plan.md")
        if "dependency_map" in folders:
            files.append("dependency-map.md")
    else:
        files.append("skill/SKILL.md")
        if "references" in folders:
            files.append("references/source-notes.md")
        if "templates" in folders:
            files.append("templates/output-template.md")
        if "scripts" in folders:
            files.append("scripts/validate_artifact.py")
        if "hooks" in folders:
            files.extend(["hooks/preflight.py", "hooks/post_generation.py"])
        if "agents" in folders:
            files.append("agents/reviewer.md")
        if "mcp" in folders:
            files.append("mcp/integration.md")
    return files


def run_python(path: Path, args: list[str], stdin: str = "", cwd: Path | None = None, timeout: int = 10) -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, "-B", str(path), *args],
        input=stdin,
        text=True,
        capture_output=True,
        cwd=str(cwd or path.parent),
        timeout=timeout,
        check=False,
    )
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output[:500]


def audit_json_files(task_dir: Path, findings: list[dict[str, str]], counters: Counter[str]) -> None:
    for path in sorted(task_dir.rglob("*.json")):
        counters["json_files_parsed"] += 1
        try:
            read_json(path)
        except Exception as exc:
            findings.append(finding("error", "json_parse_failed", path, str(exc)))


def audit_python_files(task_dir: Path, findings: list[dict[str, str]], counters: Counter[str]) -> None:
    for path in sorted(task_dir.rglob("*.py")):
        counters["python_files_parsed"] += 1
        try:
            ast.parse(read_text(path), filename=str(path))
        except Exception as exc:
            findings.append(finding("error", "python_parse_failed", path, str(exc)))


def audit_prompt_traceability(task_dir: Path, task: dict[str, Any], findings: list[dict[str, str]]) -> None:
    prompt_text = read_text(task_dir / "prompt.txt") if (task_dir / "prompt.txt").is_file() else ""
    readme_text = read_text(task_dir / "README.md") if (task_dir / "README.md").is_file() else ""
    category = task.get("category", {}).get("name", "")
    niche = task.get("niche", {}).get("name", "")
    output_target = task.get("output_target", {}).get("name", "")
    packet = task.get("niche", {}).get("tiny_prompt_packet", "")
    for label, value in {
        "category": category,
        "niche": niche,
        "output_target": output_target,
        "tiny_prompt_packet": packet,
    }.items():
        if value and value not in prompt_text:
            findings.append(finding("error", "prompt_trace_missing", task_dir / "prompt.txt", f"Missing {label}: {value}"))
        if value and value not in readme_text:
            findings.append(finding("error", "readme_trace_missing", task_dir / "README.md", f"Missing {label}: {value}"))


def audit_manifest(task_dir: Path, task: dict[str, Any], manifest: dict[str, Any], findings: list[dict[str, str]]) -> None:
    task_category = task.get("category", {}).get("slug")
    task_niche = task.get("niche", {}).get("slug")
    task_target = task.get("output_target", {}).get("slug")
    for key, expected in {
        "category": task_category,
        "niche": task_niche,
        "output_target": task_target,
        "entrypoint": "README.md",
    }.items():
        if manifest.get(key) != expected:
            findings.append(finding("error", "manifest_field_mismatch", task_dir / "manifest.json", f"{key}={manifest.get(key)!r}, expected {expected!r}"))
    eval_viewer = manifest.get("eval_viewer", {})
    if eval_viewer.get("visible") is not True:
        findings.append(finding("error", "manifest_not_visible", task_dir / "manifest.json", "eval_viewer.visible must be true"))
    manifest_files = set(str(item).replace("\\", "/") for item in manifest.get("files", []))
    for relative in expected_files(task):
        if relative not in manifest_files:
            findings.append(finding("error", "manifest_missing_file_entry", task_dir / "manifest.json", f"Missing files[] entry: {relative}"))
        if not (task_dir / relative).is_file():
            findings.append(finding("error", "required_file_missing", task_dir / relative, "Required target file missing"))
    for relative in manifest_files:
        if not (task_dir / relative).is_file():
            findings.append(finding("error", "manifest_file_missing_on_disk", task_dir / relative, "Manifest file entry not found on disk"))


def audit_eval(task_dir: Path, task: dict[str, Any], evaluation: dict[str, Any], findings: list[dict[str, str]]) -> None:
    checks = evaluation.get("checks", {})
    for key, expected in expected_checks(task).items():
        if checks.get(key) is not expected:
            findings.append(finding("error", "eval_check_mismatch", task_dir / "eval.json", f"{key}={checks.get(key)!r}, expected {expected!r}"))
    scorecard = evaluation.get("scorecard", {})
    for key in SCORECARD_KEYS:
        value = scorecard.get(key)
        if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
            findings.append(finding("error", "scorecard_invalid", task_dir / "eval.json", f"{key}={value!r} is not a 0..1 score"))


def audit_domain_lens(task_dir: Path, task: dict[str, Any], combined: str, findings: list[dict[str, str]]) -> None:
    category = task.get("category", {}).get("name", "")
    profile = category_profile(category)
    if not profile:
        findings.append(finding("error", "category_profile_missing", task_dir, f"No category module for {category!r}"))
        return
    for marker in ["Category risk tags:", "Allowed help:", "Disallowed help:", "Ambiguity trigger:", "Safe redirect:"]:
        if marker not in combined:
            findings.append(finding("error", "domain_lens_marker_missing", task_dir, f"Missing marker: {marker}"))
    for key in ["allowed_help", "disallowed_help", "ambiguity_trigger", "safe_redirect"]:
        expected = text_value(profile.get(key))
        if expected and not token_coverage(combined, expected, minimum=3):
            findings.append(finding("error", "category_profile_trace_missing", task_dir, f"Missing category profile terms for {key}"))
    risk_tags = text_value(profile.get("risk_tags")) or "none"
    if risk_tags not in combined:
        findings.append(finding("error", "risk_tags_missing", task_dir, f"Missing risk tags line value: {risk_tags}"))


def audit_single_skill(task_dir: Path, task: dict[str, Any], findings: list[dict[str, str]]) -> None:
    skill_path = task_dir / "skill" / "SKILL.md"
    skill_text = read_text(skill_path) if skill_path.is_file() else ""
    for marker in SKILL_SECTIONS:
        if marker not in skill_text:
            findings.append(finding("error", "skill_section_missing", skill_path, f"Missing section: {marker}"))
    if not re.search(r"^---\s+name: .+?\s+description: ", skill_text, flags=re.DOTALL | re.MULTILINE):
        findings.append(finding("error", "skill_frontmatter_missing", skill_path, "Missing name/description frontmatter"))
    folders = set(task.get("output_target", {}).get("folders", []))
    if "references" in folders:
        reference_text = read_text(task_dir / "references" / "source-notes.md")
        for marker in ["## Domain Assumptions", "## Citation Placeholders", "## Boundary Notes"]:
            if marker not in reference_text:
                findings.append(finding("error", "reference_section_missing", task_dir / "references" / "source-notes.md", f"Missing section: {marker}"))
    if "templates" in folders:
        template_text = read_text(task_dir / "templates" / "output-template.md")
        for marker in ["## Assumptions", "## Limits", "## Next Steps"]:
            if marker not in template_text:
                findings.append(finding("error", "template_section_missing", task_dir / "templates" / "output-template.md", f"Missing section: {marker}"))
    if "agents" in folders:
        agent_text = read_text(task_dir / "agents" / "reviewer.md")
        for marker in ["## Responsibilities", "## Handoff", "domain lens", "disallowed-help"]:
            if marker not in agent_text:
                findings.append(finding("error", "agent_contract_missing", task_dir / "agents" / "reviewer.md", f"Missing marker: {marker}"))
    if "mcp" in folders:
        mcp_text = read_text(task_dir / "mcp" / "integration.md")
        for marker in ["## Tools", "## Schemas", "## Expected Calls", "## Fallback", "audit_domain_lens", "safe_fallback"]:
            if marker not in mcp_text:
                findings.append(finding("error", "mcp_contract_missing", task_dir / "mcp" / "integration.md", f"Missing marker: {marker}"))


def audit_skill_system(task_dir: Path, task: dict[str, Any], findings: list[dict[str, str]]) -> None:
    skill_count = int(task.get("output_target", {}).get("skill_count", 1))
    for relative in SYSTEM_SHARED_FILES:
        text = read_text(task_dir / relative)
        if relative == "shared-interface.md":
            for marker in ["## Purpose", "## Domain Lens", "## Activation Conditions", "## Input Contract", "## Output Contract", "## Workflow", "## Example"]:
                if marker not in text:
                    findings.append(finding("error", "shared_interface_marker_missing", task_dir / relative, f"Missing marker: {marker}"))
        elif relative == "shared-safety.md":
            for marker in ["## Safety Boundaries", "Allowed help:", "Disallowed help:", "Refusal pattern:", "Safe redirect:"]:
                if marker not in text:
                    findings.append(finding("error", "shared_safety_marker_missing", task_dir / relative, f"Missing marker: {marker}"))
        elif relative == "shared-evaluation.md":
            if "## Evaluation Checklist" not in text:
                findings.append(finding("error", "shared_evaluation_marker_missing", task_dir / relative, "Missing evaluation checklist"))
    role_paths = sorted((task_dir / "skills").glob("skill-*/SKILL.md"))
    if len(role_paths) != skill_count:
        findings.append(finding("error", "system_role_count_mismatch", task_dir / "skills", f"Found {len(role_paths)}, expected {skill_count}"))
    role_names: list[str] = []
    for role_path in role_paths:
        text = read_text(role_path)
        for marker in ["## Role Responsibility", "## Workflow", "## Handoff Contract", "## Failure Modes"]:
            if marker not in text:
                findings.append(finding("error", "system_skill_marker_missing", role_path, f"Missing marker: {marker}"))
        match = re.search(r"- `role`: `([^`]+)`", text)
        if match:
            role_names.append(match.group(1))
        else:
            findings.append(finding("error", "system_role_name_missing", role_path, "Missing role handoff name"))
    duplicates = [role for role, count in Counter(role_names).items() if count > 1]
    if duplicates:
        findings.append(finding("error", "system_role_duplicate", task_dir / "skills", f"Duplicate roles: {', '.join(duplicates)}"))


def audit_execution(task_dir: Path, task: dict[str, Any], findings: list[dict[str, str]], counters: Counter[str]) -> None:
    folders = set(task.get("output_target", {}).get("folders", []))
    if "scripts" in folders:
        script = task_dir / "scripts" / "validate_artifact.py"
        counters["generated_scripts_executed"] += 1
        ok, output = run_python(script.resolve(), [str(task_dir.resolve())], cwd=task_dir.resolve())
        if not ok or "artifact=ok" not in output:
            findings.append(finding("error", "generated_validator_failed", script, output or "no output"))
    if "hooks" in folders:
        for hook in [task_dir / "hooks" / "preflight.py", task_dir / "hooks" / "post_generation.py"]:
            counters["generated_hooks_executed"] += 1
            ok, output = run_python(hook.resolve(), [], stdin=json.dumps({"root": str(task_dir.resolve())}), cwd=task_dir.resolve())
            if not ok:
                findings.append(finding("error", "generated_hook_failed", hook, output or "no output"))
                continue
            try:
                payload = json.loads(output)
            except json.JSONDecodeError as exc:
                findings.append(finding("error", "generated_hook_invalid_json", hook, str(exc)))
                continue
            if payload.get("decision") != "allow":
                findings.append(finding("error", "generated_hook_denied", hook, output))


def audit_task(task_dir: Path, execute_python: bool = False) -> tuple[list[dict[str, str]], Counter[str]]:
    findings: list[dict[str, str]] = []
    counters: Counter[str] = Counter()
    try:
        task = read_json(task_dir / "task.json")
        manifest = read_json(task_dir / "manifest.json")
        evaluation = read_json(task_dir / "eval.json")
    except Exception as exc:
        return [finding("error", "task_core_parse_failed", task_dir, str(exc))], counters

    audit_json_files(task_dir, findings, counters)
    audit_python_files(task_dir, findings, counters)
    audit_prompt_traceability(task_dir, task, findings)
    audit_manifest(task_dir, task, manifest, findings)
    audit_eval(task_dir, task, evaluation, findings)

    text_files = [path for path in task_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"}]
    combined = "\n\n".join(read_text(path) for path in text_files)
    audit_domain_lens(task_dir, task, combined, findings)

    if int(task.get("output_target", {}).get("skill_count", 1)) > 1:
        audit_skill_system(task_dir, task, findings)
    else:
        audit_single_skill(task_dir, task, findings)

    if execute_python:
        audit_execution(task_dir, task, findings, counters)

    return findings, counters


def review_dirs(root: Path, task_dirs: list[Path], write_report: bool = False, execute_python: bool = False) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    counters: Counter[str] = Counter()
    for task_dir in sorted(task_dirs):
        try:
            task_findings, task_counters = audit_task(task_dir, execute_python=execute_python)
            findings.extend(task_findings)
            counters.update(task_counters)
        except Exception as exc:
            findings.append(finding("error", "review_exception", task_dir, str(exc)))
    severity_counts = Counter(item["severity"] for item in findings)
    code_counts = Counter(item["code"] for item in findings)
    report = {
        "schema_version": "benchmark-exhaustive-review-1.0",
        "root": str(root),
        "tasks": len(task_dirs),
        "valid": severity_counts["error"] == 0,
        "executed_python": execute_python,
        "summary": {
            "errors": severity_counts["error"],
            "warnings": severity_counts["warning"],
            "codes": dict(sorted(code_counts.items())),
            "json_files_parsed": counters["json_files_parsed"],
            "python_files_parsed": counters["python_files_parsed"],
            "generated_scripts_executed": counters["generated_scripts_executed"],
            "generated_hooks_executed": counters["generated_hooks_executed"],
        },
        "findings": findings[:200],
        "findings_truncated": max(0, len(findings) - 200),
    }
    if write_report:
        (root / "exhaustive_review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def review_root(root: Path, limit: int | None = None, execute_python: bool = False) -> dict[str, Any]:
    task_dirs = sorted(path.parent for path in root.rglob("task.json"))
    if limit is not None:
        task_dirs = task_dirs[:limit]
    return review_dirs(root, task_dirs, write_report=limit is None, execute_python=execute_python)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run exhaustive benchmark output review.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--execute-python", action="store_true", help="Execute generated validators and hooks.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = review_root(args.root, limit=args.limit, execute_python=args.execute_python)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        status = "PASS" if report["valid"] else "FAIL"
        print(
            "exhaustive_benchmark_review: "
            f"{status} tasks={report['tasks']} errors={summary['errors']} warnings={summary['warnings']} "
            f"json={summary['json_files_parsed']} py={summary['python_files_parsed']} "
            f"scripts={summary['generated_scripts_executed']} hooks={summary['generated_hooks_executed']}"
        )
        for item in report["findings"]:
            print(f"[{item['severity']}] {item['code']}: {item['path']}: {item['message']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
