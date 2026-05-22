#!/usr/bin/env python3
"""Create compact reports for a skill benchmark matrix corpus."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def score_average(scorecard: dict[str, Any]) -> float:
    values = [
        float(scorecard[key])
        for key in SCORECARD_KEYS
        if isinstance(scorecard.get(key), (int, float))
    ]
    return round(mean(values), 3) if values else 0.0


def average_scores(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {key: 0.0 for key in SCORECARD_KEYS}
    return {
        key: round(mean(float(row["scorecard"].get(key, 0.0) or 0.0) for row in rows), 3)
        for key in SCORECARD_KEYS
    }


def average_checks(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {key: 0.0 for key in CHECK_KEYS}
    return {
        key: round(mean(1.0 if row["checks"].get(key) else 0.0 for row in rows), 3)
        for key in CHECK_KEYS
    }


def load_rows(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for task_path in sorted(root.rglob("task.json")):
        task_dir = task_path.parent
        try:
            task = read_json(task_path)
            manifest = read_json(task_dir / "manifest.json")
            evaluation = read_json(task_dir / "eval.json")
            scorecard = evaluation.get("scorecard", {})
            checks = evaluation.get("checks", {})
            rows.append({
                "path": str(task_dir),
                "agent": manifest.get("agent_slug") or manifest.get("agent"),
                "category": manifest.get("category"),
                "niche": manifest.get("niche"),
                "output_target": manifest.get("output_target"),
                "category_name": task.get("category", {}).get("name", manifest.get("category")),
                "niche_name": task.get("niche", {}).get("name", manifest.get("niche")),
                "output_target_name": task.get("output_target", {}).get("name", manifest.get("output_target")),
                "scorecard": scorecard,
                "score_average": score_average(scorecard),
                "checks": checks,
            })
        except Exception as exc:
            errors.append({"path": str(task_dir), "error": str(exc)})
    return rows, errors


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, ""))].append(row)
    return dict(sorted(grouped.items()))


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "tasks": len(rows),
        "score_average": round(mean(row["score_average"] for row in rows), 3) if rows else 0.0,
        "score_means": average_scores(rows),
        "check_pass_rates": average_checks(rows),
    }


def build_report(root: Path) -> dict[str, Any]:
    rows, errors = load_rows(root)
    qualitative_path = root / "qualitative_audit.json"
    qualitative = read_json(qualitative_path) if qualitative_path.exists() else None
    exhaustive_path = root / "exhaustive_review.json"
    exhaustive = read_json(exhaustive_path) if exhaustive_path.exists() else None
    audit_errors: list[dict[str, str]] = []
    for name, path, payload in [
        ("qualitative_audit", qualitative_path, qualitative),
        ("exhaustive_review", exhaustive_path, exhaustive),
    ]:
        if payload and not payload.get("valid"):
            summary = payload.get("summary") or {}
            audit_errors.append({
                "path": str(path),
                "error": (
                    f"{name} invalid: "
                    f"errors={summary.get('errors', 0)} "
                    f"warnings={summary.get('warnings', 0)}"
                ),
            })
    by_agent = {
        key: summarize_group(value)
        for key, value in group_rows(rows, "agent").items()
    }
    by_output_target = {
        key: summarize_group(value)
        for key, value in group_rows(rows, "output_target").items()
    }
    by_category = {
        key: summarize_group(value)
        for key, value in group_rows(rows, "category").items()
    }
    leaderboard = sorted(
        (
            {
                "agent": agent,
                "tasks": summary["tasks"],
                "score_average": summary["score_average"],
            }
            for agent, summary in by_agent.items()
        ),
        key=lambda item: (-item["score_average"], item["agent"]),
    )
    return {
        "schema_version": "benchmark-matrix-report-1.0",
        "root": str(root),
        "valid": not errors and not audit_errors,
        "errors": errors + audit_errors,
        "totals": {
            "tasks": len(rows),
            "agents": len(by_agent),
            "categories": len(by_category),
            "output_targets": len(by_output_target),
            "niches": len({(row["category"], row["niche"]) for row in rows}),
        },
        "leaderboard": leaderboard,
        "by_agent": by_agent,
        "by_output_target": by_output_target,
        "by_category": by_category,
        "qualitative_audit": qualitative,
        "exhaustive_review": exhaustive,
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    totals = report["totals"]
    leaderboard_rows = [
        [item["agent"], item["tasks"], item["score_average"]]
        for item in report["leaderboard"]
    ]
    target_rows = [
        [target, summary["tasks"], summary["score_average"], summary["score_means"]["testability"], summary["score_means"]["token_usage"]]
        for target, summary in report["by_output_target"].items()
    ]
    agent_rows = [
        [agent, summary["tasks"], summary["score_average"], summary["score_means"]["structure_completeness"], summary["check_pass_rates"]["appears_in_eval_viewer"]]
        for agent, summary in report["by_agent"].items()
    ]
    return f"""# Benchmark Matrix Report

Root: `{report['root']}`

## Totals

- Tasks: `{totals['tasks']}`
- Agents: `{totals['agents']}`
- Categories: `{totals['categories']}`
- Category/niche pairs: `{totals['niches']}`
- Output targets: `{totals['output_targets']}`
- Valid: `{report['valid']}`

## Leaderboard

{markdown_table(["Agent", "Tasks", "Average Score"], leaderboard_rows)}

## Agents

{markdown_table(["Agent", "Tasks", "Avg", "Structure", "Viewer"], agent_rows)}

## Output Targets

{markdown_table(["Output Target", "Tasks", "Avg", "Testability", "Token Usage"], target_rows)}

## Qualitative Audit

- Valid: `{(report.get('qualitative_audit') or {}).get('valid')}`
- Errors: `{((report.get('qualitative_audit') or {}).get('summary') or {}).get('errors')}`
- Warnings: `{((report.get('qualitative_audit') or {}).get('summary') or {}).get('warnings')}`

## Exhaustive Review

- Valid: `{(report.get('exhaustive_review') or {}).get('valid')}`
- Errors: `{((report.get('exhaustive_review') or {}).get('summary') or {}).get('errors')}`
- Warnings: `{((report.get('exhaustive_review') or {}).get('summary') or {}).get('warnings')}`
- JSON parsed: `{((report.get('exhaustive_review') or {}).get('summary') or {}).get('json_files_parsed')}`
- Python parsed: `{((report.get('exhaustive_review') or {}).get('summary') or {}).get('python_files_parsed')}`
- Generated scripts executed: `{((report.get('exhaustive_review') or {}).get('summary') or {}).get('generated_scripts_executed')}`
- Generated hooks executed: `{((report.get('exhaustive_review') or {}).get('summary') or {}).get('generated_hooks_executed')}`

## Notes

Scores are deterministic structural heuristics from `eval.json`. Qualitative
and exhaustive gates are machine-checkable review signals; matching averages
across agents means the lanes share scaffolded outputs, not that separate live
agents performed equally.
"""


def write_report(root: Path) -> dict[str, Any]:
    report = build_report(root)
    write_json(root / "benchmark_report.json", report)
    (root / "benchmark_report.md").write_text(render_markdown(report).rstrip() + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Report on a skill benchmark matrix corpus.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = write_report(args.root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        totals = report["totals"]
        print(f"report_benchmark_matrix: tasks={totals['tasks']} agents={totals['agents']} valid={report['valid']}")
        for error in report["errors"]:
            print(f"error: {error['path']}: {error['error']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
