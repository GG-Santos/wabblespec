#!/usr/bin/env python3
"""Improve a skill description based on eval results.

Takes eval results (from run_eval.py) and generates an improved description
using the runtime adapter abstraction layer. Configure live adapters locally
with the --provider flag or SKILL_PROVIDER env var.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.observability import write_redacted_json_log
from scripts.providers import get_provider
from scripts.providers.base import LLMProvider
from scripts.prompt_builder import PromptBuilder
from scripts.repair import (
    append_repair_history,
    build_preserve_list,
    build_repair_guidance_section,
    build_target_sections,
    classify_repair_causes,
    make_repair_entry,
    within_growth_cap,
)
from scripts.utils import parse_skill_md
from scripts.validation import ValidationError, load_json_file, validate_eval_results


def _extract_description(text: str, provider_name: str = "generic") -> str:
    """Extract the description from provider response using appropriate delimiters."""
    match = re.search(r"\[DESCRIPTION\](.*?)\[/DESCRIPTION\]", text, re.DOTALL)
    if match:
        return match.group(1).strip().strip('"')

    # Fallback: return the whole text stripped
    return text.strip().strip('"')


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    model: str,
    provider: LLMProvider | None = None,
    provider_name: str | None = None,
    test_results: dict | None = None,
    log_dir: Path | None = None,
    iteration: int | None = None,
) -> str:
    """Call an LLM to improve the description based on eval results.

    Args:
        skill_name: Name of the skill.
        skill_content: Full SKILL.md content.
        current_description: Current description text.
        eval_results: Eval results from run_eval.
        history: Previous improvement attempts.
        model: Model identifier.
        provider: LLMProvider instance (auto-detected if None).
        provider_name: Provider name for auto-detection fallback.
        test_results: Optional test set results.
        log_dir: Directory for saving improvement logs.
        iteration: Current iteration number.

    Returns:
        The improved description text.
    """
    validate_eval_results(eval_results)

    if provider is None:
        provider = get_provider(provider_name)

    pname = provider.get_provider_name()
    builder = PromptBuilder(provider=pname)

    failed_triggers = [
        r for r in eval_results["results"]
        if r["should_trigger"] and not r["pass"]
    ]
    false_triggers = [
        r for r in eval_results["results"]
        if not r["should_trigger"] and not r["pass"]
    ]

    # Build scores summary
    train_score = f"{eval_results['summary']['passed']}/{eval_results['summary']['total']}"
    if test_results:
        test_score = f"{test_results['summary']['passed']}/{test_results['summary']['total']}"
        scores_summary = f"Train: {train_score}, Test: {test_score}"
    else:
        scores_summary = f"Train: {train_score}"

    repair_causes = classify_repair_causes(eval_results=eval_results)
    preserve = build_preserve_list(current_description, eval_results)
    targets = build_target_sections(repair_causes, eval_results)
    repair_guidance = build_repair_guidance_section(repair_causes, preserve, targets)

    # Build the prompt using the prompt builder
    prompt = builder.build_improve_prompt(
        skill_name=skill_name,
        current_description=current_description,
        skill_content=skill_content,
        scores_summary=scores_summary,
        failures_section=_build_failures_section(failed_triggers, false_triggers),
        history_section=_build_history_section(history, builder),
        repair_guidance_section=repair_guidance,
    )

    result = provider.complete(prompt, model=model, timeout=300)
    text = result.text
    description = _extract_description(text, pname)
    accepted_growth = within_growth_cap(current_description, description, repair_causes)
    fallback_used = False

    transcript: dict = {
        "iteration": iteration,
        "provider": pname,
        "model": result.model,
        "prompt": prompt,
        "response": text,
        "parsed_description": description,
        "char_count": len(description),
        "over_limit": len(description) > 1024,
        "repair_causes": repair_causes,
        "preserve": preserve,
        "targets": targets,
        "accepted_growth": accepted_growth,
        "tokens_used": result.tokens_used,
        "cost_estimate": result.cost_estimate,
        "duration_ms": result.duration_ms,
    }

    # Safety net: shorten if over 1024 characters
    if len(description) > 1024:
        shorten_prompt = (
            f"{prompt}\n\n"
            f"---\n\n"
            f"A previous attempt produced this description, which at "
            f"{len(description)} characters is over the 1024-character hard limit:\n\n"
            f'"{description}"\n\n'
            f"Rewrite it to be under 1024 characters while keeping the most "
            f"important trigger words and intent coverage. Respond with only "
            f"the new description in {builder.delimiters['description_tag_open']} "
            f"and {builder.delimiters['description_tag_close']} tags."
        )
        shorten_result = provider.complete(shorten_prompt, model=model, timeout=300)
        shortened = _extract_description(shorten_result.text, pname)

        transcript["rewrite_prompt"] = shorten_prompt
        transcript["rewrite_response"] = shorten_result.text
        transcript["rewrite_description"] = shortened
        transcript["rewrite_char_count"] = len(shortened)
        description = shortened
        accepted_growth = within_growth_cap(current_description, description, repair_causes)
        transcript["accepted_growth_after_rewrite"] = accepted_growth

    if not accepted_growth:
        compact_prompt = (
            f"{prompt}\n\n"
            f"---\n\n"
            f"The proposed description grew too much for a non-critical repair:\n\n"
            f'"{description}"\n\n'
            f"Rewrite it to preserve the target fixes while staying within 35% "
            f"growth of the current description. Respond with only the new "
            f"description in {builder.delimiters['description_tag_open']} and "
            f"{builder.delimiters['description_tag_close']} tags."
        )
        compact_result = provider.complete(compact_prompt, model=model, timeout=300)
        compacted = _extract_description(compact_result.text, pname)
        transcript["growth_cap_prompt"] = compact_prompt
        transcript["growth_cap_response"] = compact_result.text
        transcript["growth_cap_description"] = compacted
        transcript["growth_cap_char_count"] = len(compacted)
        description = compacted
        accepted_growth = within_growth_cap(current_description, description, repair_causes)

    if not accepted_growth:
        transcript["rejected_description"] = description
        description = current_description
        transcript["fallback_reason"] = "non-critical repair exceeded growth cap after compact rewrite"
        fallback_used = True
        accepted_growth = True

    transcript["final_description"] = description
    transcript["final_growth_accepted"] = accepted_growth
    transcript["repair_applied"] = not fallback_used and description != current_description

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"improve_iter_{iteration or 'unknown'}.json"
        write_redacted_json_log(log_dir, log_file.name, transcript)
        append_repair_history(
            log_dir,
            make_repair_entry(
                iteration=iteration,
                stage="description_improvement",
                causes=repair_causes,
                before=current_description,
                after=description,
                accepted=not fallback_used and accepted_growth,
                preserve=preserve,
                targets=targets,
                note=(
                    "repair rejected; current description preserved"
                    if fallback_used
                    else "provider-produced repair accepted"
                    if accepted_growth
                    else "growth cap still exceeded after compact rewrite"
                ),
            ),
        )

    return description


def _build_failures_section(failed_triggers: list, false_triggers: list) -> str:
    """Build the failures section of the prompt."""
    section = ""
    if failed_triggers:
        section += "FAILED TO TRIGGER (should have triggered but didn't):\n"
        for r in failed_triggers:
            section += f'  - "{r["query"]}" (triggered {r["triggers"]}/{r["runs"]} times)\n'
        section += "\n"

    if false_triggers:
        section += "FALSE TRIGGERS (triggered but shouldn't have):\n"
        for r in false_triggers:
            section += f'  - "{r["query"]}" (triggered {r["triggers"]}/{r["runs"]} times)\n'
        section += "\n"

    return section


def _build_history_section(history: list, builder: PromptBuilder) -> str:
    """Build the history section of the prompt."""
    if not history:
        return ""

    section = "PREVIOUS ATTEMPTS (do NOT repeat these - try something structurally different):\n\n"
    for h in history:
        train_s = f"{h.get('train_passed', h.get('passed', 0))}/{h.get('train_total', h.get('total', 0))}"
        test_s = f"{h.get('test_passed', '?')}/{h.get('test_total', '?')}" if h.get('test_passed') is not None else None
        score_str = f"train={train_s}" + (f", test={test_s}" if test_s else "")

        section += builder.wrap("attempt " + score_str, "")
        section += f'Description: "{h["description"]}"\n'
        if "results" in h:
            section += "Train results:\n"
            for r in h["results"]:
                status = "PASS" if r["pass"] else "FAIL"
                section += f'  [{status}] "{r["query"][:80]}" (triggered {r["triggers"]}/{r["runs"]})\n'
        if h.get("note"):
            section += f'Note: {h["note"]}\n'
        section += builder.wrap("/attempt", "") + "\n"

    return section


def main():
    parser = argparse.ArgumentParser(description="Improve a skill description based on eval results")
    parser.add_argument("--eval-results", required=True, help="Path to eval results JSON (from run_eval.py)")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--history", default=None, help="Path to history JSON (previous attempts)")
    parser.add_argument("--model", required=True, help="Model for improvement")
    parser.add_argument("--provider", default=None, help="Provider name (auto-detected if omitted)")
    parser.add_argument("--verbose", action="store_true", help="Print thinking to stderr")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    try:
        eval_results = validate_eval_results(load_json_file(args.eval_results))
    except ValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    history = []
    if args.history:
        try:
            history = load_json_file(args.history)
            if not isinstance(history, list):
                raise ValidationError("history must be an array")
        except ValidationError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    current_description = eval_results.get("description") or original_description

    provider = get_provider(args.provider)

    if args.verbose:
        print(f"Provider: {provider.get_provider_name()}", file=sys.stderr)
        print(f"Current: {current_description}", file=sys.stderr)
        print(f"Score: {eval_results['summary']['passed']}/{eval_results['summary']['total']}", file=sys.stderr)

    new_description = improve_description(
        skill_name=name,
        skill_content=content,
        current_description=current_description,
        eval_results=eval_results,
        history=history,
        model=args.model,
        provider=provider,
    )

    if args.verbose:
        print(f"Improved: {new_description}", file=sys.stderr)

    # Output as JSON with both the new description and updated history
    output = {
        "description": new_description,
        "history": history + [{
            "description": current_description,
            "passed": eval_results["summary"]["passed"],
            "failed": eval_results["summary"]["failed"],
            "total": eval_results["summary"]["total"],
            "results": eval_results["results"],
        }],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

