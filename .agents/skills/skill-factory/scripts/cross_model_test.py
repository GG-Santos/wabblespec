#!/usr/bin/env python3
"""Cross-model testing utility.

Tests prompts across multiple providers/models simultaneously and
compares results. Useful for validating that skill descriptions
and prompts work consistently across providers.
"""

import argparse
import json
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from scripts.observability import write_redacted_json_log

__test__ = False


def test_prompt_across_providers(
    prompt: str,
    providers: list[str] | None = None,
    models: dict[str, str] | None = None,
    timeout: int = 120,
    log_dir: Path | None = None,
    run_id: str | None = None,
) -> dict:
    """Test a prompt across multiple providers and compare results.

    Args:
        prompt: The prompt text to test.
        providers: List of provider names to test (auto-detects if None).
        models: Optional dict of provider_name → model override.
        timeout: Timeout per provider call.

    Returns:
        Dict with results per provider and comparison metrics.
    """
    from scripts.providers import get_provider, list_available_providers

    if providers is None:
        available = list_available_providers()
        providers = [p["name"] for p in available if p.get("available")]

    models = models or {}
    run_id = run_id or uuid.uuid4().hex
    results = {}

    if not providers:
        return {
            "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "providers_tested": [],
            "results": {},
            "comparison": {"note": "No available providers to test"},
        }

    with ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = {}
        for provider_name in providers:
            model = models.get(provider_name)
            try:
                provider = get_provider(provider_name)
            except Exception as e:
                results[provider_name] = {
                    "status": "error",
                    "error": f"Failed to initialize: {e}",
                }
                continue

            futures[executor.submit(
                _call_provider, provider, provider_name, prompt, model, timeout, log_dir, run_id
            )] = provider_name

        for future in as_completed(futures):
            provider_name = futures[future]
            try:
                results[provider_name] = future.result()
            except Exception as e:
                results[provider_name] = {
                    "status": "error",
                    "error": str(e),
                }

    # Compare results
    comparison = _compare_results(results)

    return {
        "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
        "providers_tested": providers,
        "results": results,
        "comparison": comparison,
    }


def _call_provider(
    provider,
    provider_name: str,
    prompt: str,
    model: str | None,
    timeout: int,
    log_dir: Path | None = None,
    run_id: str | None = None,
) -> dict:
    """Call a single provider and return structured results."""
    start = time.time()
    try:
        result = provider.complete(prompt, model=model, timeout=timeout)
        duration = time.time() - start
        output = {
            "status": "success",
            "text": result.text,
            "model": result.model,
            "tokens_used": result.tokens_used,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "duration_ms": result.duration_ms,
            "cost_estimate": result.cost_estimate,
            "latency_s": round(duration, 2),
        }
        _write_cross_model_log(log_dir, run_id, provider_name, prompt, output, model)
        return output
    except Exception as e:
        output = {
            "status": "error",
            "error": str(e),
            "error_class": type(e).__name__,
            "latency_s": round(time.time() - start, 2),
        }
        _write_cross_model_log(log_dir, run_id, provider_name, prompt, output, model)
        return output


def _write_cross_model_log(
    log_dir: Path | None,
    run_id: str | None,
    provider_name: str,
    prompt: str,
    output: dict,
    model: str | None,
) -> None:
    if log_dir is None:
        return
    write_redacted_json_log(log_dir, f"cross_model_{run_id}_{provider_name}.json", {
        "kind": "cross_model_prompt",
        "run_id": run_id,
        "provider": provider_name,
        "model": model or output.get("model"),
        "prompt": prompt,
        **output,
    })


def _compare_results(results: dict) -> dict:
    """Compare results across providers."""
    successful = {k: v for k, v in results.items() if v.get("status") == "success"}

    if len(successful) < 2:
        return {"note": "Not enough successful results to compare"}

    # Basic metrics
    response_lengths = {k: len(v["text"]) for k, v in successful.items()}
    latencies = {k: v.get("latency_s", 0) for k, v in successful.items()}
    costs = {k: v.get("cost_estimate", 0) for k, v in successful.items()}
    tokens = {k: v.get("tokens_used", 0) for k, v in successful.items()}

    return {
        "response_length": response_lengths,
        "latency_seconds": latencies,
        "cost_estimate_usd": costs,
        "tokens_used": tokens,
        "fastest": min(latencies, key=latencies.get) if latencies else None,
        "cheapest": min(costs, key=costs.get) if costs else None,
        "most_verbose": max(response_lengths, key=response_lengths.get) if response_lengths else None,
    }


def test_trigger_across_providers(
    query: str,
    skill_name: str,
    skill_description: str,
    providers: list[str] | None = None,
    timeout: int = 30,
    log_dir: Path | None = None,
    run_id: str | None = None,
) -> dict:
    """Test skill triggering across providers.

    Args:
        query: User query to test.
        skill_name: Name of the skill.
        skill_description: Skill description.
        providers: List of provider names (auto-detects if None).
        timeout: Timeout per call.

    Returns:
        Dict with trigger results per provider and agreement metrics.
    """
    from scripts.providers import get_provider, list_available_providers

    if providers is None:
        available = list_available_providers()
        providers = [p["name"] for p in available if p.get("available")]

    results = {}
    run_id = run_id or uuid.uuid4().hex

    for provider_name in providers:
        try:
            provider = get_provider(provider_name)
            trigger_result = provider.check_skill_trigger(
                query, skill_name, skill_description, timeout=timeout
            )
            results[provider_name] = {
                "triggered": trigger_result.triggered,
                "confidence": trigger_result.confidence,
                "reasoning": trigger_result.reasoning,
            }
            write_redacted_json_log(log_dir, f"cross_model_trigger_{run_id}_{provider_name}.json", {
                "kind": "cross_model_trigger",
                "run_id": run_id,
                "provider": provider_name,
                "query": query,
                "skill_name": skill_name,
                "skill_description": skill_description,
                "status": "success",
                **results[provider_name],
            })
        except Exception as e:
            results[provider_name] = {
                "triggered": None,
                "error": str(e),
                "error_class": type(e).__name__,
            }
            write_redacted_json_log(log_dir, f"cross_model_trigger_{run_id}_{provider_name}.json", {
                "kind": "cross_model_trigger",
                "run_id": run_id,
                "provider": provider_name,
                "query": query,
                "skill_name": skill_name,
                "skill_description": skill_description,
                "status": "error",
                **results[provider_name],
            })

    # Calculate agreement
    decisions = [v["triggered"] for v in results.values() if v.get("triggered") is not None]
    if decisions:
        agreement = decisions.count(decisions[0]) / len(decisions)
        unanimous = len(set(decisions)) == 1
    else:
        agreement = 0
        unanimous = False

    return {
        "query": query,
        "skill_name": skill_name,
        "results": results,
        "agreement": round(agreement, 2),
        "unanimous": unanimous,
        "majority_triggered": sum(1 for d in decisions if d) > len(decisions) / 2 if decisions else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Test prompts across multiple providers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Prompt testing
    prompt_parser = subparsers.add_parser("prompt", help="Test a prompt across providers")
    prompt_parser.add_argument("--prompt", required=True, help="Prompt text or @file path")
    prompt_parser.add_argument("--providers", nargs="+", help="Provider names (default: auto-detect)")
    prompt_parser.add_argument("--timeout", type=int, default=120)
    prompt_parser.add_argument("--log-dir", type=Path, default=None, help="Optional directory for redacted provider logs")

    # Trigger testing
    trigger_parser = subparsers.add_parser("trigger", help="Test skill triggering across providers")
    trigger_parser.add_argument("--query", required=True, help="User query to test")
    trigger_parser.add_argument("--skill-name", required=True)
    trigger_parser.add_argument("--skill-description", required=True)
    trigger_parser.add_argument("--providers", nargs="+", help="Provider names (default: auto-detect)")
    trigger_parser.add_argument("--timeout", type=int, default=30)
    trigger_parser.add_argument("--log-dir", type=Path, default=None, help="Optional directory for redacted provider logs")

    # Status
    subparsers.add_parser("status", help="Show provider availability")

    args = parser.parse_args()

    if args.command == "status":
        from scripts.providers import print_provider_status
        print_provider_status()
        return

    if args.command == "prompt":
        prompt = args.prompt
        if prompt.startswith("@"):
            prompt = Path(prompt[1:]).read_text()
        result = test_prompt_across_providers(prompt, args.providers, timeout=args.timeout, log_dir=args.log_dir)
        print(json.dumps(result, indent=2))

    elif args.command == "trigger":
        result = test_trigger_across_providers(
            args.query, args.skill_name, args.skill_description,
            args.providers, args.timeout, log_dir=args.log_dir,
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
