#!/usr/bin/env python3
"""Run the skill benchmark matrix generation, scoring, reporting, and checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

try:
    from scripts.materialize_benchmark_outputs import materialize_task
    from scripts.exhaustive_benchmark_review import review_dirs
    from scripts.render_benchmark_matrix_html import render_report
    from scripts.report_benchmark_matrix import write_report
    from scripts.score_benchmark_outputs import score_dirs
    from scripts.qualitative_benchmark_audit import audit_dirs
    from scripts.skill_benchmark_matrix import generate_matrix, parse_filter, select_tasks, slugify
    from scripts.verify_eval_viewer_outputs import verify_outputs
except ModuleNotFoundError:  # Allows `python scripts/run_benchmark_pipeline.py`.
    from materialize_benchmark_outputs import materialize_task
    from exhaustive_benchmark_review import review_dirs
    from render_benchmark_matrix_html import render_report
    from report_benchmark_matrix import write_report
    from score_benchmark_outputs import score_dirs
    from qualitative_benchmark_audit import audit_dirs
    from skill_benchmark_matrix import generate_matrix, parse_filter, select_tasks, slugify
    from verify_eval_viewer_outputs import verify_outputs


def split_values(values: Iterable[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        result.extend(part.strip() for part in value.split(",") if part.strip())
    return result


def step(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, **payload}


def task_dirs(root: Path) -> list[Path]:
    return sorted(path.parent for path in root.rglob("task.json"))


def is_materialized(task_dir: Path) -> bool:
    manifest_path = task_dir / "manifest.json"
    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(manifest.get("benchmark", {}).get("materialized"))


def expected_task_dirs(
    root: Path,
    agent_names: list[str],
    stage: str,
    category_filters: set[str],
    niche_filters: set[str],
    target_filters: set[str],
    limit: int | None,
) -> list[Path]:
    selected = select_tasks(stage, category_filters, niche_filters, target_filters, limit)
    return [
        root / slugify(agent) / category.slug / niche.slug / target.slug
        for agent in agent_names
        for category, niche, target in selected
    ]


def validate_coverage(
    root: Path,
    agent_names: list[str],
    stage: str,
    category_filters: set[str],
    niche_filters: set[str],
    target_filters: set[str],
    limit: int | None = None,
) -> dict[str, Any]:
    expected = expected_task_dirs(root, agent_names, stage, category_filters, niche_filters, target_filters, limit)
    required_files = ["README.md", "task.json", "manifest.json", "eval.json"]
    missing: list[dict[str, str]] = []
    for task_dir in expected:
        for relative in required_files:
            path = task_dir / relative
            if not path.is_file():
                missing.append({
                    "path": str(path),
                    "error": f"missing required matrix file: {relative}",
                })
    return {
        "schema_version": "benchmark-pipeline-coverage-1.0",
        "root": str(root),
        "expected_tasks": len(expected),
        "present_tasks": sum(1 for task_dir in expected if (task_dir / "task.json").is_file()),
        "missing_files": len(missing),
        "missing": missing[:25],
        "missing_truncated": max(0, len(missing) - 25),
        "valid": not missing,
    }


def materialize_pending(root: Path, candidates: list[Path], overwrite: bool = False) -> dict[str, Any]:
    candidates = sorted(candidates)
    expected_count = len(candidates)
    if not overwrite:
        candidates = [path for path in candidates if not is_materialized(path)]

    completed = 0
    errors: list[dict[str, str]] = []
    for task_dir in candidates:
        try:
            materialize_task(task_dir, overwrite=overwrite)
            completed += 1
        except Exception as exc:
            errors.append({"path": str(task_dir), "error": str(exc)})

    return {
        "schema_version": "benchmark-pipeline-materialization-1.0",
        "root": str(root),
        "tasks_seen": len(candidates),
        "completed": completed,
        "skipped_existing": 0 if overwrite else expected_count - len(candidates),
        "errors": errors,
        "valid": not errors,
    }


def run_pipeline(
    root: Path,
    agent_names: list[str],
    stage: str,
    category_filters: set[str],
    niche_filters: set[str],
    target_filters: set[str],
    limit: int | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    execute_review_python: bool = True,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for agent_name in agent_names:
        generated = generate_matrix(
            root=root,
            agent_name=agent_name,
            stage=stage,
            category_filters=category_filters,
            niche_filters=niche_filters,
            target_filters=target_filters,
            limit=limit,
            dry_run=dry_run,
            overwrite=overwrite,
        )
        steps.append(step("generate", generated))

    if dry_run:
        return {
            "schema_version": "benchmark-pipeline-1.0",
            "root": str(root),
            "agents": agent_names,
            "stage": stage,
            "dry_run": True,
            "valid": True,
            "errors": [],
            "steps": steps,
        }

    selected_dirs = expected_task_dirs(root, agent_names, stage, category_filters, niche_filters, target_filters, limit)

    coverage = validate_coverage(root, agent_names, stage, category_filters, niche_filters, target_filters, limit)
    steps.append(step("coverage", coverage))
    if not coverage["valid"]:
        errors.extend(coverage["missing"])

    materialized = materialize_pending(root, selected_dirs, overwrite=overwrite)
    steps.append(step("materialize", materialized))
    if not materialized["valid"]:
        errors.extend(materialized["errors"])

    scored = score_dirs(root, selected_dirs, overwrite=True, write_summary=limit is None)
    steps.append(step("score", scored))
    if not scored["valid"]:
        errors.extend(scored["errors"])

    qualitative = audit_dirs(
        root,
        selected_dirs,
        write_report=limit is None,
    )
    steps.append(step("qualitative_audit", qualitative))
    if not qualitative["valid"]:
        errors.extend(qualitative["findings"])

    exhaustive = review_dirs(
        root,
        selected_dirs,
        write_report=limit is None,
        execute_python=execute_review_python,
    )
    steps.append(step("exhaustive_review", exhaustive))
    if not exhaustive["valid"]:
        errors.extend(exhaustive["findings"])

    report = write_report(root)
    steps.append(step("report", {"valid": report["valid"], "totals": report["totals"], "errors": report["errors"]}))
    if not report["valid"]:
        errors.extend(report["errors"])

    rendered = render_report(root)
    steps.append(step("html", rendered))

    verified = verify_outputs(
        root=root,
        require_manifest=True,
        require_eval_json=True,
        require_visible_true=True,
        strict_files=True,
        require_readme=True,
    )
    steps.append(step("verify", verified))
    if not verified["valid"]:
        errors.extend(verified["findings"])

    summary = {
        "schema_version": "benchmark-pipeline-1.0",
        "root": str(root),
        "agents": agent_names,
        "stage": stage,
        "dry_run": False,
        "valid": not errors,
        "errors": errors,
        "steps": steps,
    }
    (root / "benchmark_pipeline_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the benchmark matrix pipeline end to end.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--agent-name", action="append", default=[], help="Agent lane. Repeat or comma-separate.")
    parser.add_argument("--stage", choices=["1", "2", "3", "4", "5", "6", "all"], default="6")
    parser.add_argument("--category", action="append", help="Category slug/name filter. Repeat or comma-separate.")
    parser.add_argument("--niche", action="append", help="Niche slug/name filter. Repeat or comma-separate.")
    parser.add_argument("--target", action="append", help="Output target slug/name filter. Repeat or comma-separate.")
    parser.add_argument("--limit", type=int, help="Limit selected generation tasks and downstream checks.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-exhaustive-execution", action="store_true", help="Skip executing generated validators and hooks during exhaustive review.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")

    agent_names = split_values(args.agent_name) or ["skill_factory"]
    summary = run_pipeline(
        root=args.root,
        agent_names=agent_names,
        stage=args.stage,
        category_filters=parse_filter(args.category),
        niche_filters=parse_filter(args.niche),
        target_filters=parse_filter(args.target),
        limit=args.limit,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        execute_review_python=not args.skip_exhaustive_execution,
    )
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        status = "PASS" if summary["valid"] else "FAIL"
        print(f"run_benchmark_pipeline: {status} agents={len(agent_names)} stage={args.stage} root={args.root}")
        for item in summary["errors"]:
            print(f"error: {item}")
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
