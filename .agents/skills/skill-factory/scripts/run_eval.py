#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes an LLM to trigger (read the skill)
for a set of queries. Supports multiple providers via the provider abstraction
layer. Outputs results as JSON.
"""

import argparse
import json
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from scripts.observability import write_redacted_json_log
from scripts.providers import get_provider, get_provider_cached
from scripts.providers.base import LLMProvider
from scripts.utils import parse_skill_md, find_project_root
from scripts.validation import ValidationError, load_json_file, validate_eval_set


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    provider_name: str | None = None,
    model: str | None = None,
    project_root: str | None = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Uses the provider's check_skill_trigger method.
    """
    provider = get_provider_cached(provider_name)

    result = provider.check_skill_trigger(
        query=query,
        skill_name=skill_name,
        skill_description=skill_description,
        model=model,
        timeout=timeout,
    )

    return result.triggered


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    provider_name: str | None = None,
    log_dir: Path | None = None,
    run_id: str | None = None,
) -> dict:
    """Run the full eval set and return results.

    Args:
        eval_set: List of eval items with 'query' and 'should_trigger'.
        skill_name: Skill identifier.
        description: Description text to evaluate.
        num_workers: Number of parallel workers.
        timeout: Timeout per query.
        project_root: Project root for workspace-relative eval state.
        runs_per_query: Number of runs per query for confidence.
        trigger_threshold: Threshold for trigger rate.
        model: Model override.
        provider_name: Provider name (auto-detected if None).

    Returns:
        Dict with results and summary.
    """
    if num_workers < 1:
        raise ValueError("num_workers must be at least 1")
    if runs_per_query < 1:
        raise ValueError("runs_per_query must be at least 1")
    validate_eval_set(eval_set)

    start = time.time()
    run_id = run_id or uuid.uuid4().hex
    results = []

    provider = get_provider(provider_name)
    ExecutorClass = ThreadPoolExecutor
    total_jobs = len(eval_set) * runs_per_query

    if total_jobs == 0:
        return {
            "skill_name": skill_name,
            "description": description,
            "provider": provider.get_provider_name(),
            "results": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
            },
        }

    with ExecutorClass(max_workers=min(num_workers, total_jobs)) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    provider_name,
                    model,
                    str(project_root),
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    output = {
        "skill_name": skill_name,
        "description": description,
        "provider": provider.get_provider_name(),
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }
    write_redacted_json_log(log_dir, f"eval_{run_id}.json", {
        "kind": "trigger_eval",
        "run_id": run_id,
        "provider": provider.get_provider_name(),
        "model": model or provider.get_default_model(),
        "skill_description": description,
        "duration_ms": round((time.time() - start) * 1000, 2),
        "query_count": len(eval_set),
        "runs_per_query": runs_per_query,
        "trigger_threshold": trigger_threshold,
        "status": "success",
        "summary": output["summary"],
        "results": output["results"],
    })
    return output


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model to use (default: provider's default)")
    parser.add_argument("--provider", default=None, help="Provider name (auto-detected if omitted)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    try:
        eval_set = validate_eval_set(load_json_file(args.eval_set))
    except ValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        provider = get_provider(args.provider)
        print(f"Provider: {provider.get_provider_name()}", file=sys.stderr)
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        provider_name=args.provider,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
