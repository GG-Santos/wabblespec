#!/usr/bin/env python3
"""Score materialized benchmark outputs with deterministic structural checks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is part of packaged requirements.
    yaml = None


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

SECTION_MARKERS = [
    "## Purpose",
    "## Activation Conditions",
    "## Workflow",
    "## Output Contract",
    "## Safety Boundaries",
    "## Failure Modes",
    "## Evaluation Checklist",
    "## Example",
]

SAFETY_TERMS = [
    "safety",
    "assumptions",
    "limits",
    "do not invent",
    "unsafe",
    "missing context",
]

REUSE_TERMS = [
    "activation",
    "workflow",
    "output contract",
    "template",
    "routing",
    "next steps",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def category_key(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def category_modules() -> dict[str, dict[str, Any]]:
    path = Path(__file__).resolve().parents[1] / "config" / "category_modules.yaml"
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    categories = data.get("categories", {})
    return categories if isinstance(categories, dict) else {}


CATEGORY_MODULES = category_modules()


def category_profile(category: str) -> dict[str, Any]:
    return CATEGORY_MODULES.get(category_key(category), {})


def text_value(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value or "")


def slug_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.split(r"[^a-z0-9]+", value.lower())
        if len(token) >= 4 and token not in {"skill", "create", "using", "with", "that", "this"}
    }


def file_texts(task_dir: Path, files: list[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for relative in files:
        path = task_dir / relative
        if path.suffix.lower() in {".md", ".txt", ".json", ".py"} and path.is_file():
            texts[relative] = read_text(path)
    return texts


def expected_component_checks(task: dict[str, Any], task_dir: Path) -> dict[str, bool]:
    checks = {key: False for key in CHECK_KEYS}
    checks["has_skill"] = (task_dir / "skill" / "SKILL.md").is_file() or any((task_dir / "skills").glob("skill-*/SKILL.md"))
    checks["has_references"] = (task_dir / "references").is_dir()
    checks["has_templates"] = (task_dir / "templates").is_dir()
    checks["has_scripts"] = any((task_dir / "scripts").glob("*.py"))
    checks["has_hooks"] = any((task_dir / "hooks").glob("*.py"))
    checks["has_agents"] = any((task_dir / "agents").glob("*.md"))
    checks["has_mcp"] = (task_dir / "mcp" / "integration.md").is_file()
    checks["appears_in_eval_viewer"] = (task_dir / "manifest.json").is_file() and (task_dir / "eval.json").is_file()
    return checks


def score_output_quality(combined: str) -> float:
    section_score = sum(marker in combined for marker in SECTION_MARKERS) / len(SECTION_MARKERS)
    contract_score = 1.0 if "`assumptions`" in combined and "`limits`" in combined and "`next_steps`" in combined else 0.5
    return clamp((section_score * 0.7) + (contract_score * 0.3))


def score_token_usage(texts: dict[str, str]) -> float:
    total_chars = sum(len(text) for text in texts.values())
    if total_chars <= 12000:
        return 1.0
    if total_chars >= 60000:
        return 0.4
    return clamp(1.0 - ((total_chars - 12000) / 48000) * 0.6)


def score_structure(task_dir: Path, manifest: dict[str, Any]) -> float:
    files = manifest.get("files", [])
    if not files:
        return 0.0
    present = sum(1 for relative in files if (task_dir / relative).is_file())
    return clamp(present / len(files))


def score_domain_specificity(task: dict[str, Any], combined: str) -> float:
    category = task["category"]["name"]
    niche = task["niche"]["name"]
    prompt = task["niche"]["tiny_prompt_packet"]
    tokens = slug_tokens(f"{category} {niche} {prompt}")
    if not tokens:
        return 0.0
    seen = sum(1 for token in tokens if token in combined.lower())
    return clamp(seen / min(len(tokens), 12))


def score_safety(task: dict[str, Any], combined: str) -> float:
    lowered = combined.lower()
    profile = category_profile(task["category"]["name"])
    profile_terms = slug_tokens(
        " ".join(
            text_value(profile.get(key))
            for key in ["risk_tags", "allowed_help", "disallowed_help", "ambiguity_trigger", "refusal_pattern", "safe_redirect"]
        )
    )
    generic = sum(1 for term in SAFETY_TERMS if term in lowered) / len(SAFETY_TERMS)
    if not profile_terms:
        return clamp(generic)
    seen = sum(1 for token in profile_terms if token in lowered)
    profile_score = seen / min(len(profile_terms), 10)
    return clamp((generic * 0.45) + (profile_score * 0.55))


def score_testability(task: dict[str, Any], task_dir: Path, combined: str, checks: dict[str, bool]) -> float:
    folders = set(task.get("output_target", {}).get("folders", []))
    target = task.get("output_target", {})
    pieces = [
        "## Evaluation Checklist" in combined,
        "## Failure Modes" in combined,
        "## Example" in combined,
        "manifest.json" in combined,
        "eval.json" in combined,
    ]
    if "scripts" in folders:
        pieces.append((task_dir / "scripts" / "validate_artifact.py").is_file())
    if "hooks" in folders:
        pieces.append(checks["has_hooks"])
    if "mcp" in folders:
        pieces.append(checks["has_mcp"] and "## Expected Calls" in combined)
    if int(target.get("skill_count", 1)) > 1:
        pieces.extend([
            (task_dir / "routing.md").is_file(),
            (task_dir / "shared-interface.md").is_file(),
            (task_dir / "shared-evaluation.md").is_file() or (task_dir / "evaluation-plan.md").is_file(),
        ])
    return clamp(sum(pieces) / len(pieces))


def score_reuse(combined: str) -> float:
    lowered = combined.lower()
    seen = sum(1 for term in REUSE_TERMS if term in lowered)
    return clamp(seen / len(REUSE_TERMS))


def score_task(task_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    task = read_json(task_dir / "task.json")
    manifest = read_json(task_dir / "manifest.json")
    eval_path = task_dir / "eval.json"
    eval_payload = read_json(eval_path)
    files = [str(item) for item in manifest.get("files", []) if isinstance(item, str)]
    texts = file_texts(task_dir, files)
    combined = "\n\n".join(texts.values())
    checks = expected_component_checks(task, task_dir)
    scorecard = {
        "output_quality": score_output_quality(combined),
        "token_usage": score_token_usage(texts),
        "structure_completeness": score_structure(task_dir, manifest),
        "domain_specificity": score_domain_specificity(task, combined),
        "safety_quality": score_safety(task, combined),
        "testability": score_testability(task, task_dir, combined, checks),
        "reuse_value": score_reuse(combined),
    }
    eval_payload["scorecard"] = scorecard
    eval_payload["checks"] = checks
    notes = [
        "Auto-scored by deterministic structural heuristics; not a human or model quality grade.",
        "Scores reflect observable file presence, required sections, target-aware testability, category safety markers, domain tokens, and reuse markers.",
    ]
    eval_payload["notes"] = notes
    if overwrite or any(eval_payload.get("scorecard", {}).get(key) is None for key in SCORECARD_KEYS):
        write_json(eval_path, eval_payload)
    return {"path": str(task_dir), "scorecard": scorecard, "checks": checks}


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"tasks": 0, "score_means": {}, "check_pass_rates": {}}
    score_means = {
        key: round(mean(row["scorecard"][key] for row in rows), 3)
        for key in SCORECARD_KEYS
    }
    check_pass_rates = {
        key: round(mean(1.0 if row["checks"][key] else 0.0 for row in rows), 3)
        for key in CHECK_KEYS
    }
    return {
        "tasks": len(rows),
        "score_means": score_means,
        "check_pass_rates": check_pass_rates,
    }


def score_dirs(root: Path, task_dirs: list[Path], overwrite: bool = False, write_summary: bool = False) -> dict[str, Any]:
    task_dirs = sorted(task_dirs)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for task_dir in task_dirs:
        try:
            rows.append(score_task(task_dir, overwrite=overwrite))
        except Exception as exc:
            errors.append({"path": str(task_dir), "error": str(exc)})
    summary = aggregate(rows)
    report = {
        "schema_version": "benchmark-score-summary-1.0",
        "root": str(root),
        "valid": not errors,
        "errors": errors,
        **summary,
    }
    if write_summary:
        write_json(root / "score_summary.json", report)
    return report


def score_root(root: Path, limit: int | None = None, overwrite: bool = False) -> dict[str, Any]:
    task_dirs = sorted(path.parent for path in root.rglob("task.json"))
    if limit is not None:
        task_dirs = task_dirs[:limit]
    return score_dirs(root, task_dirs, overwrite=overwrite, write_summary=limit is None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Score materialized benchmark outputs.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = score_root(args.root, limit=args.limit, overwrite=args.overwrite)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"score_benchmark_outputs: scored {report['tasks']} tasks")
        for error in report["errors"]:
            print(f"error: {error['path']}: {error['error']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
