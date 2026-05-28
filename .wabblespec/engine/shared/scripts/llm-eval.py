#!/usr/bin/env python3
"""
llm-eval.py — WabbleSpec skill-section quality scorer.

Scores a SKILL.md section on three dimensions (1-5 each):
  clarity       — can an agent understand each step?
  completeness  — are commands, arguments, and expected behavior documented?
  actionability — can an agent execute without follow-up questions?

Minimum gate: all three dimensions >= 4.
Exits 0 on pass, 1 on fail or error.

Model resolution (in priority order):
  1. --model flag
  2. WS_ANALYSIS_MODEL environment variable
  Exits with an error if neither is set.

Usage:
  llm-eval.py --skill-path <SKILL.md> --section <heading> [--model <id>]
  llm-eval.py --content-file <path> --section <label> [--model <id>]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_STATE_PATH = Path(__file__).parents[4] / "state" / "runtime" / "runtime-state.json"
EVAL_LOG_PATH = Path(__file__).parents[4] / "state" / "evals" / "eval-log.json"
MIN_SCORE = 4

JUDGE_PROMPT_TEMPLATE = """\
You are evaluating instructions for a WabbleSpec AI agent skill module.

The agent reads these instructions to know what steps to take, what tools to call, \
and what outputs to produce. It must not need to guess or ask follow-up questions.

Rate the following {section} on three dimensions (1-5):

- **clarity** (1-5): Can an agent understand what each step does from the description alone?
- **completeness** (1-5): Are commands, arguments, file paths, and expected behavior documented? \
Would an agent need to guess anything?
- **actionability** (1-5): Can an agent execute this section correctly without asking \
follow-up questions?

Scoring guide:
- 5: Excellent — no ambiguity, all information present
- 4: Good — minor gaps an experienced agent can infer
- 3: Adequate — some guessing required
- 2: Poor — significant information missing
- 1: Unusable — agent would fail without external help

Respond with ONLY valid JSON (no markdown fences):
{{"clarity": N, "completeness": N, "actionability": N, "reasoning": "brief explanation"}}

Content to evaluate:

{content}"""


def check_analysis_capability():
    if not RUNTIME_STATE_PATH.exists():
        print(f"ERROR: runtime-state.json not found at {RUNTIME_STATE_PATH}", file=sys.stderr)
        print("Run runtime-probe first to generate it.", file=sys.stderr)
        sys.exit(1)
    with open(RUNTIME_STATE_PATH) as f:
        state = json.load(f)
    cap = state.get("capabilities", {}).get("analysis", {})
    if not cap.get("available"):
        print("ERROR: 'analysis' capability not available per runtime-state.json", file=sys.stderr)
        sys.exit(1)


def resolve_model(args_model):
    model = args_model or os.environ.get("WS_ANALYSIS_MODEL")
    if not model:
        print(
            "ERROR: No model specified. Set WS_ANALYSIS_MODEL env var or pass --model <id>.",
            file=sys.stderr,
        )
        sys.exit(1)
    return model


def extract_section(skill_path: Path, heading: str) -> str:
    text = skill_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^#{1,3}\s+" + re.escape(heading) + r"\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        print(f"ERROR: Section '{heading}' not found in {skill_path}", file=sys.stderr)
        sys.exit(1)
    start = match.end()
    next_heading = re.search(r"^#{1,3}\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def call_judge(model: str, section_label: str, content: str) -> dict:
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic SDK not installed. Run: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    prompt = JUDGE_PROMPT_TEMPLATE.format(section=section_label, content=content[:6000])
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Judge returned non-JSON: {raw[:200]}", file=sys.stderr)
        raise SystemExit(1) from e


def append_eval_log(entry: dict):
    EVAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if EVAL_LOG_PATH.exists():
        with open(EVAL_LOG_PATH) as f:
            log = json.load(f)
    else:
        log = []
    log.append(entry)
    with open(EVAL_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="WabbleSpec skill-section quality scorer")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--skill-path", type=Path, help="Path to SKILL.md")
    input_group.add_argument("--content-file", type=Path, help="Path to raw content file")
    parser.add_argument("--section", required=True, help="Section heading or label to evaluate")
    parser.add_argument("--model", help="Model ID (overrides WS_ANALYSIS_MODEL env var)")
    args = parser.parse_args()

    check_analysis_capability()
    model = resolve_model(args.model)

    if args.skill_path:
        if not args.skill_path.exists():
            print(f"ERROR: {args.skill_path} not found", file=sys.stderr)
            sys.exit(1)
        content = extract_section(args.skill_path, args.section)
        skill_path_str = str(args.skill_path)
    else:
        if not args.content_file.exists():
            print(f"ERROR: {args.content_file} not found", file=sys.stderr)
            sys.exit(1)
        content = args.content_file.read_text(encoding="utf-8").strip()
        skill_path_str = str(args.content_file)

    if len(content) < 50:
        print(f"ERROR: Section content too short ({len(content)} chars) — section may be empty or not found", file=sys.stderr)
        sys.exit(1)

    result = call_judge(model, args.section, content)

    clarity = int(result["clarity"])
    completeness = int(result["completeness"])
    actionability = int(result["actionability"])
    reasoning = result.get("reasoning", "")
    passed = all(s >= MIN_SCORE for s in (clarity, completeness, actionability))

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill_path": skill_path_str,
        "section": args.section,
        "scores": {
            "clarity": clarity,
            "completeness": completeness,
            "actionability": actionability,
        },
        "reasoning": reasoning,
        "passed": passed,
    }
    append_eval_log(entry)

    output = {
        "clarity": clarity,
        "completeness": completeness,
        "actionability": actionability,
        "reasoning": reasoning,
        "passed": passed,
    }
    print(json.dumps(output, indent=2))

    if not passed:
        failing = [
            dim for dim, score in [("clarity", clarity), ("completeness", completeness), ("actionability", actionability)]
            if score < MIN_SCORE
        ]
        print(f"\nFAIL: {', '.join(failing)} scored below {MIN_SCORE}/5", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
