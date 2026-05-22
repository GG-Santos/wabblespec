#!/usr/bin/env python3
"""Smoke-test generated skill/plugin artifacts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import py_compile
import re
import subprocess
import sys
import tempfile
import threading
import urllib.request
from functools import partial
from http.server import HTTPServer
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:  # Allows `python scripts/generated_artifact_smoke.py ...`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.component_generator import generate_skill_structure
from scripts.quick_validate import validate_skill_report


PLACEHOLDER_RE = re.compile(r"{{\s*[A-Za-z_][A-Za-z0-9_]*\s*}}")
FULL_RUNTIME_MAX_APPROX_TOKENS = 8200
FULL_RUNTIME_MAX_FILES = 31


def finding(severity: str, code: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def add_error(findings: list[dict[str, str]], code: str, message: str) -> None:
    findings.append(finding("error", code, message))


def run_python(
    args: list[str],
    input_data: dict[str, Any] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", *args],
        input=json.dumps(input_data) if input_data is not None else None,
        capture_output=True,
        text=True,
        check=check,
    )


def unresolved_placeholder_paths(files: dict[str, str]) -> list[str]:
    paths: list[str] = []
    for path, content in files.items():
        if path.startswith("templates/"):
            continue
        if PLACEHOLDER_RE.search(content):
            paths.append(path)
    return paths


def approx_tokens(files: dict[str, str]) -> int:
    return sum(len(content) // 4 for content in files.values())


def root_authoring_templates(files: dict[str, str]) -> list[str]:
    return sorted(
        path for path in files
        if path.startswith("templates/") and path.endswith(".j2")
    )


def expected_surface_paths(registry: dict[str, Any]) -> list[str]:
    hooks = registry.get("hooks", {})
    mcp = registry.get("mcp", {})
    values: list[Any] = [
        registry.get("skill"),
        registry.get("activation"),
        registry.get("commands", []),
        hooks.get("manifest"),
        hooks.get("scripts", []),
        hooks.get("rules"),
        mcp.get("server"),
        mcp.get("evaluation"),
        registry.get("agents", []),
        registry.get("schemas", []),
        registry.get("evaluations", []),
        registry.get("templates", []),
    ]
    paths: list[str] = []
    for value in values:
        if isinstance(value, str) and value:
            paths.append(value)
        elif isinstance(value, list):
            paths.extend(item for item in value if isinstance(item, str) and item)
    return sorted(set(paths))


def check_generated_matrix(root: Path, findings: list[dict[str, str]]) -> dict[str, Any]:
    tier_cases = {
        "simple": ("plain-helper", "Summarize user notes into a reusable checklist."),
        "standard": ("data-helper", "Validate structured JSON data with schema examples and eval cases."),
        "advanced": ("technical-helper", "Technical code workflow with agents commands hooks scripts and verification."),
        "full": ("full-helper", "Full plugin with hooks MCP agent command template schema eval rule matcher surfaces."),
    }
    results: list[dict[str, Any]] = []
    full_manifest: dict[str, Any] | None = None
    full_output: Path | None = None

    for tier, (name, description) in tier_cases.items():
        output_dir = root / tier / name
        manifest = generate_skill_structure(
            name,
            description,
            tier=tier,
            output_dir=output_dir,
            dry_run=False,
        )
        report = validate_skill_report(output_dir, strict=True)
        unresolved = unresolved_placeholder_paths(manifest["files"])
        skill_text = manifest["files"].get("SKILL.md", "")
        missing_quality_markers = [
            marker for marker in [
                "## Output Contract",
                "Worked example:",
                "## Output Quality Contract",
                "**Good:**",
                "**Bad:**",
                "**Discriminator:**",
                "## Failure Modes",
            ]
            if marker not in skill_text
        ]
        result = {
            "tier": tier,
            "files": len(manifest["files"]),
            "approx_tokens": approx_tokens(manifest["files"]),
            "valid": report["valid"],
            "errors": report["summary"]["errors"],
            "warnings": report["summary"]["warnings"],
            "unresolved_placeholders": unresolved,
            "missing_quality_markers": missing_quality_markers,
        }
        if not report["valid"] or report["summary"]["errors"] or report["summary"]["warnings"]:
            add_error(findings, "generated_skill_invalid", f"{tier} generated skill did not validate cleanly.")
        if unresolved:
            add_error(findings, "unresolved_generated_placeholder", f"{tier} unresolved placeholders: {unresolved}")
        if missing_quality_markers:
            add_error(findings, "generated_quality_contract_missing", f"{tier} missing quality markers: {missing_quality_markers}")
        if tier == "full":
            full_manifest = manifest
            full_output = output_dir
            authoring_templates = root_authoring_templates(manifest["files"])
            result["root_authoring_templates"] = authoring_templates
            if authoring_templates:
                add_error(
                    findings,
                    "full_runtime_authoring_templates_present",
                    f"Full runtime output includes root authoring templates: {authoring_templates}",
                )
            if result["files"] > FULL_RUNTIME_MAX_FILES:
                add_error(
                    findings,
                    "full_runtime_file_budget_exceeded",
                    f"Full runtime output has {result['files']} files; budget is {FULL_RUNTIME_MAX_FILES}.",
                )
            if result["approx_tokens"] > FULL_RUNTIME_MAX_APPROX_TOKENS:
                add_error(
                    findings,
                    "full_runtime_token_budget_exceeded",
                    "Full runtime output has "
                    f"{result['approx_tokens']} approximate tokens; budget is {FULL_RUNTIME_MAX_APPROX_TOKENS}.",
                )
        results.append(result)

    if full_manifest is None or full_output is None:
        add_error(findings, "missing_full_fixture", "Full generated fixture was not created.")
        return {"tiers": results}

    registry_path = full_output / "plugin" / "surfaces.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    missing_paths = [
        path for path in expected_surface_paths(registry)
        if path not in full_manifest["files"]
    ]
    if missing_paths:
        add_error(findings, "surface_path_missing", f"Surface registry paths missing: {missing_paths}")

    results[-1]["surface_paths"] = len(expected_surface_paths(registry))
    results[-1]["missing_surface_paths"] = missing_paths
    return {"tiers": results, "full_output": str(full_output)}


def check_overlay_cases(findings: list[dict[str, str]]) -> list[dict[str, Any]]:
    cases = {
        "technical": ("technical-skill", "technical code security workflow with files logs verification", "### Technical Domain"),
        "creative": ("creative-skill", "creative fiction design writing voice tone story", "### Creative Domain"),
        "current": ("current-skill", "latest current prices laws sports schedule release trends", "### Current Events Trends"),
        "safety": ("safety-skill", "safety high stakes emergency dangerous dual use risk", "### Safety Sensitive"),
    }
    results: list[dict[str, Any]] = []
    for case, (name, description, needle) in cases.items():
        content = generate_skill_structure(name, description, tier="simple", dry_run=True)["files"]["SKILL.md"]
        present = needle in content
        if not present:
            add_error(findings, "overlay_missing", f"{case} overlay marker missing: {needle}")
        results.append({"case": case, "needle": needle, "present": present})
    return results


def check_hook_and_mcp(full_output: Path, findings: list[dict[str, str]]) -> dict[str, Any]:
    hook_path = full_output / "hooks" / "hook.py"
    py_compile.compile(str(hook_path), doraise=True)

    denied = run_python(
        [str(hook_path)],
        {"event": "bash", "command": "rm -rf ~"},
    )
    denied_payload = json.loads(denied.stdout)
    safe = run_python(
        [str(hook_path)],
        {"event": "bash", "command": "python -m scripts.quick_validate . --strict"},
    )
    safe_payload = json.loads(safe.stdout)
    if denied_payload.get("decision") not in {"deny", "block"}:
        add_error(findings, "hook_did_not_block", f"Destructive hook fixture was not denied: {denied_payload}")
    if safe_payload.get("decision") in {"deny", "block"}:
        add_error(findings, "hook_blocked_safe_command", f"Safe hook fixture was blocked: {safe_payload}")

    server_path = full_output / "mcp" / "server.py"
    py_compile.compile(str(server_path), doraise=True)
    self_test = run_python([str(server_path), "--self-test"])
    self_test_payload = json.loads(self_test.stdout)
    if self_test_payload.get("status") != "scaffold":
        add_error(findings, "mcp_self_test_failed", f"MCP self-test payload: {self_test_payload}")

    return {
        "hook_denied_decision": denied_payload.get("decision"),
        "hook_safe_payload": safe_payload,
        "mcp_self_test_status": self_test_payload.get("status"),
    }


def write_eval_workspace(workspace: Path) -> Path:
    run_dir = workspace / "eval-1" / "with_skill" / "run-1"
    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True)
    (run_dir / "eval_metadata.json").write_text(
        json.dumps({"eval_id": 1, "prompt": "Smoke prompt"}, indent=2),
        encoding="utf-8",
    )
    (outputs_dir / "result.md").write_text("# Smoke Output\n\nReady.\n", encoding="utf-8")
    (run_dir / "grading.json").write_text(
        json.dumps({
            "expectations": [{"text": "Output exists", "passed": True, "evidence": "result.md"}],
            "summary": {"passed": 1, "failed": 0, "total": 1, "pass_rate": 1.0},
        }, indent=2),
        encoding="utf-8",
    )
    benchmark = workspace / "benchmark.json"
    benchmark.write_text(
        json.dumps({
            "skill_name": "smoke",
            "summary": {"total_runs": 1},
            "runs": [],
        }, indent=2),
        encoding="utf-8",
    )
    return benchmark


def check_eval_viewer(skill_root: Path, root: Path, findings: list[dict[str, str]]) -> dict[str, Any]:
    workspace = root / "eval-workspace"
    benchmark = write_eval_workspace(workspace)
    static_path = root / "static-viewer" / "review.html"
    run_python([
        str(skill_root / "eval-viewer" / "generate_review.py"),
        str(workspace),
        "--skill-name",
        "smoke",
        "--benchmark",
        str(benchmark),
        "--static",
        str(static_path),
        "--no-open",
    ])

    html = static_path.read_text(encoding="utf-8")
    expected_assets = [
        static_path.parent / "assets" / "skill-factory-small.svg",
        static_path.parent / "assets" / "skill-factory.png",
    ]
    missing_assets = [str(path) for path in expected_assets if not path.exists()]
    if missing_assets:
        add_error(findings, "viewer_asset_missing", f"Static viewer assets missing: {missing_assets}")
    legacy_name = "skill-" + "creator"
    if legacy_name in html:
        add_error(findings, "viewer_legacy_asset_reference", "Static viewer HTML references legacy asset names.")
    if "assets/skill-factory-small.svg" not in html or "assets/skill-factory.png" not in html:
        add_error(findings, "viewer_asset_reference_missing", "Static viewer HTML does not reference skill-factory assets.")

    live = check_eval_viewer_live(skill_root, workspace, benchmark, findings)
    return {
        "static_html": str(static_path),
        "assets_present": not missing_assets,
        "legacy_reference": legacy_name in html,
        "live": live,
    }


def check_eval_viewer_live(
    skill_root: Path,
    workspace: Path,
    benchmark: Path,
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    module_path = skill_root / "eval-viewer" / "generate_review.py"
    spec = importlib.util.spec_from_file_location("skill_factory_eval_viewer", module_path)
    if spec is None or spec.loader is None:
        add_error(findings, "viewer_live_import_failed", "Could not import eval viewer module.")
        return {"ok": False}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    feedback_path = workspace / "feedback.json"
    handler = partial(
        module.ReviewHandler,
        workspace,
        "smoke",
        feedback_path,
        {},
        benchmark,
    )
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    paths = [
        "/",
        "/assets/skill-factory-small.svg",
        "/assets/skill-factory.png",
        "/favicon.ico",
    ]
    statuses: dict[str, int] = {}
    try:
        for path in paths:
            with urllib.request.urlopen(base_url + path, timeout=5) as response:
                statuses[path] = response.status
    except Exception as exc:
        add_error(findings, "viewer_live_route_failed", f"Live viewer route failed: {exc}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    ok = all(statuses.get(path) == 200 for path in paths)
    if not ok:
        add_error(findings, "viewer_live_asset_missing", f"Live viewer route statuses: {statuses}")
    return {"ok": ok, "statuses": statuses}


def check_agent_contract_docs(skill_root: Path, findings: list[dict[str, str]]) -> dict[str, bool]:
    checks = {
        "grader": (
            skill_root / "agents" / "grader.md",
            ["## Inputs", "## Output format", "grading.json"],
        ),
        "comparator": (
            skill_root / "agents" / "comparator.md",
            ["## Inputs", "## Output format", "comparison.json"],
        ),
        "analyzer": (
            skill_root / "agents" / "analyzer.md",
            ["## Inputs", "## Output format", "analysis.json"],
        ),
        "schemas": (
            skill_root / "references" / "schemas.md",
            ["## grading.json", "## comparison.json", "## analysis.json"],
        ),
    }
    results: dict[str, bool] = {}
    for name, (path, needles) in checks.items():
        text = path.read_text(encoding="utf-8")
        ok = all(needle in text for needle in needles)
        results[name] = ok
        if not ok:
            add_error(findings, "agent_contract_doc_missing", f"{name} missing one of: {needles}")
    return results


def check_output_of_output_fixtures(root: Path, findings: list[dict[str, str]]) -> dict[str, Any]:
    fixtures = {
        "generated_simple": {
            "expectations": [
                {"text": "Generated skill has a concrete output contract", "passed": True, "evidence": "Output Contract section present"}
            ],
            "summary": {"passed": 1, "failed": 0, "total": 1, "pass_rate": 1.0},
            "eval_feedback": {"suggestions": [], "overall": "Fixture checks output-of-output shape."},
        },
        "generated_full_plugin": {
            "expectations": [
                {"text": "Generated plugin surfaces resolve", "passed": True, "evidence": "surfaces.json paths exist"},
                {"text": "Generated MCP self-test passes", "passed": True, "evidence": "status=scaffold"},
            ],
            "summary": {"passed": 2, "failed": 0, "total": 2, "pass_rate": 1.0},
            "eval_feedback": {"suggestions": [], "overall": "Fixture checks full scaffold output-of-output gates."},
        },
    }
    fixture_dir = root / "output-of-output-fixtures"
    fixture_dir.mkdir()
    results: dict[str, str] = {}
    for name, payload in fixtures.items():
        path = fixture_dir / f"{name}_grading.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not loaded.get("expectations") or loaded.get("summary", {}).get("failed") != 0:
            add_error(findings, "output_fixture_invalid", f"Invalid output-of-output fixture: {path}")
        results[name] = str(path)
    return results


def check_report_audit_validity(skill_root: Path, root: Path, findings: list[dict[str, str]]) -> dict[str, Any]:
    matrix_root = root / "invalid-audit-report"
    task_dir = matrix_root / "agent" / "science" / "experimental_replication" / "skill_only"
    task_dir.mkdir(parents=True)
    (task_dir / "task.json").write_text(json.dumps({
        "category": {"slug": "science", "name": "Science"},
        "niche": {"slug": "experimental_replication", "name": "Experimental Replication Skill"},
        "output_target": {"slug": "skill_only", "name": "Skill Only"},
    }, indent=2), encoding="utf-8")
    (task_dir / "manifest.json").write_text(json.dumps({
        "agent": "agent",
        "agent_slug": "agent",
        "category": "science",
        "niche": "experimental_replication",
        "output_target": "skill_only",
    }, indent=2), encoding="utf-8")
    (task_dir / "eval.json").write_text(json.dumps({
        "scorecard": {
            "output_quality": 1.0,
            "token_usage": 1.0,
            "structure_completeness": 1.0,
            "domain_specificity": 1.0,
            "safety_quality": 1.0,
            "testability": 1.0,
            "reuse_value": 1.0,
        },
        "checks": {
            "has_skill": True,
            "has_references": False,
            "has_templates": False,
            "has_scripts": False,
            "has_hooks": False,
            "has_agents": False,
            "has_mcp": False,
            "appears_in_eval_viewer": True,
        },
    }, indent=2), encoding="utf-8")
    (matrix_root / "exhaustive_review.json").write_text(json.dumps({
        "valid": False,
        "summary": {"errors": 1, "warnings": 0},
        "findings": [{"severity": "error", "code": "fixture", "path": str(task_dir), "message": "fixture"}],
    }, indent=2), encoding="utf-8")

    report_process = run_python([
        str(skill_root / "scripts" / "report_benchmark_matrix.py"),
        "--root",
        str(matrix_root),
        "--json",
    ], check=False)
    if report_process.returncode != 1:
        add_error(findings, "report_audit_exit_code_unexpected", f"Exit code: {report_process.returncode}")
    report = json.loads(report_process.stdout)
    if report.get("valid") is not False:
        add_error(findings, "report_audit_invalid_not_propagated", f"Report payload: {report}")
    if not any("exhaustive_review invalid" in item.get("error", "") for item in report.get("errors", [])):
        add_error(findings, "report_audit_error_missing", f"Report errors: {report.get('errors')}")
    return {
        "report_valid": report.get("valid"),
        "errors": report.get("errors", []),
    }


def check_benchmark_matrix(skill_root: Path, root: Path, findings: list[dict[str, str]]) -> dict[str, Any]:
    matrix_root = root / "skill_benchmarks"
    pipeline = run_python([
        str(skill_root / "scripts" / "run_benchmark_pipeline.py"),
        "--root",
        str(matrix_root),
        "--agent-name",
        "smoke-agent",
        "--stage",
        "1",
        "--limit",
        "3",
        "--json",
    ])
    pipeline_payload = json.loads(pipeline.stdout)
    if not pipeline_payload.get("valid"):
        add_error(findings, "benchmark_pipeline_failed", f"Pipeline payload: {pipeline_payload}")

    step_by_name = {step["name"]: step for step in pipeline_payload.get("steps", [])}
    generated_payload = step_by_name.get("generate", {})
    if generated_payload.get("written") != 3:
        add_error(findings, "benchmark_matrix_generation_failed", f"Matrix generation payload: {generated_payload}")

    coverage_payload = step_by_name.get("coverage", {})
    if coverage_payload.get("expected_tasks") != 3 or not coverage_payload.get("valid"):
        add_error(findings, "benchmark_matrix_coverage_failed", f"Coverage payload: {coverage_payload}")

    qualitative_payload = step_by_name.get("qualitative_audit", {})
    if not qualitative_payload.get("valid"):
        add_error(findings, "benchmark_qualitative_audit_failed", f"Qualitative audit payload: {qualitative_payload}")

    exhaustive_payload = step_by_name.get("exhaustive_review", {})
    if not exhaustive_payload.get("valid"):
        add_error(findings, "benchmark_exhaustive_review_failed", f"Exhaustive review payload: {exhaustive_payload}")

    verified_payload = step_by_name.get("verify", {})
    if not verified_payload.get("valid"):
        add_error(findings, "benchmark_matrix_verification_failed", f"Verification payload: {verified_payload}")

    rendered_payload = step_by_name.get("html", {})
    html_path = Path(rendered_payload.get("output", ""))
    if not rendered_payload.get("valid") or not html_path.exists():
        add_error(findings, "benchmark_matrix_html_missing", f"HTML payload: {rendered_payload}")
    elif "Benchmark Matrix Report" not in html_path.read_text(encoding="utf-8"):
        add_error(findings, "benchmark_matrix_html_invalid", f"HTML report missing title: {html_path}")

    reported_payload = json.loads(Path(rendered_payload.get("source", "")).read_text(encoding="utf-8"))
    if not reported_payload.get("valid"):
        add_error(findings, "benchmark_matrix_report_failed", f"Report payload: {reported_payload}")

    executable_root = root / "skill_benchmarks_executable"
    executable_pipeline = run_python([
        str(skill_root / "scripts" / "run_benchmark_pipeline.py"),
        "--root",
        str(executable_root),
        "--agent-name",
        "smoke-agent",
        "--stage",
        "6",
        "--target",
        "skill_references_template_scripts_hooks_agents_mcp",
        "--limit",
        "1",
        "--json",
    ])
    executable_payload = json.loads(executable_pipeline.stdout)
    if not executable_payload.get("valid"):
        add_error(findings, "benchmark_executable_pipeline_failed", f"Executable pipeline payload: {executable_payload}")
    executable_steps = {step["name"]: step for step in executable_payload.get("steps", [])}
    executable_review = executable_steps.get("exhaustive_review", {})
    executable_summary = executable_review.get("summary", {})
    if not executable_review.get("valid"):
        add_error(findings, "benchmark_executable_review_failed", f"Executable review payload: {executable_review}")
    if executable_summary.get("generated_scripts_executed") != 1 or executable_summary.get("generated_hooks_executed") != 2:
        add_error(findings, "benchmark_executable_review_uncovered", f"Executable review summary: {executable_summary}")

    return {
        "pipeline_valid": pipeline_payload.get("valid"),
        "generated": generated_payload,
        "coverage": coverage_payload,
        "qualitative_audit": qualitative_payload.get("summary", {}),
        "exhaustive_review": exhaustive_payload.get("summary", {}),
        "executable_pipeline_valid": executable_payload.get("valid"),
        "executable_exhaustive_review": executable_summary,
        "verified": verified_payload.get("summary", {}),
        "reported": reported_payload.get("totals", {}),
        "html": rendered_payload,
    }


def run_smoke(skill_root: Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="skill-factory-artifacts-") as tmp:
        root = Path(tmp)
        matrix = check_generated_matrix(root, findings)
        full_output = Path(matrix.get("full_output", ""))
        hook_mcp = check_hook_and_mcp(full_output, findings) if full_output.exists() else {}
        overlays = check_overlay_cases(findings)
        viewer = check_eval_viewer(skill_root, root, findings)
        contracts = check_agent_contract_docs(skill_root, findings)
        output_fixtures = check_output_of_output_fixtures(root, findings)
        report_audit_validity = check_report_audit_validity(skill_root, root, findings)
        benchmark_matrix = check_benchmark_matrix(skill_root, root, findings)

    errors = sum(1 for item in findings if item["severity"] == "error")
    return {
        "schema_version": "generated-artifact-smoke-1.0",
        "valid": errors == 0,
        "summary": {"errors": errors, "warnings": 0},
        "matrix": matrix,
        "hook_mcp": hook_mcp,
        "overlays": overlays,
        "viewer": viewer,
        "agent_contract_docs": contracts,
        "output_of_output_fixtures": output_fixtures,
        "report_audit_validity": report_audit_validity,
        "benchmark_matrix": benchmark_matrix,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test generated skill-factory artifacts.")
    parser.add_argument("skill_path", nargs="?", default=".", help="Skill factory package root.")
    parser.add_argument("--json", action="store_true", help="Write JSON report.")
    args = parser.parse_args()

    report = run_smoke(Path(args.skill_path).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"generated_artifact_smoke: {'PASS' if report['valid'] else 'FAIL'}")
        for item in report["findings"]:
            print(f"[{item['severity']}] {item['code']}: {item['message']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
