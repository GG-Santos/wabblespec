"""
WabbleSpec Quality Judge — LLM semantic evaluation for SKILL.md files.

Complements quality-score.py (static Layer 1) with semantic evaluation of
dimensions that require understanding: triggering_accuracy (F1 via synthetic
prompts), orchestration_fitness (worker vs orchestrator rubric), output_quality
(simulated task evaluation), and scope_calibration (fit assessment).

Two operation modes:

  GENERATE mode (default):
    Generates structured eval fixture files for skill-tdd. No API calls.
    Produces a .yaml fixture file with positive and negative prompts that
    can be run through /skill-tdd for triggering accuracy F1 measurement.

  JUDGE mode (--judge, requires ANTHROPIC_API_KEY):
    Calls the Claude API to evaluate orchestration_fitness and scope_calibration
    dimensions using 5-point anchored rubrics. Produces a judge report.

Usage:
  python quality-judge.py <skill_dir>
      Generate eval fixtures (GENERATE mode)

  python quality-judge.py <skill_dir> --judge
      Generate fixtures + call API for semantic dimensions (JUDGE mode)

  python quality-judge.py <skill_dir> --output json
      Output eval fixture as JSON

  python quality-judge.py <skill_dir> --fixture-out PATH
      Write fixture file to PATH (default: <skill_dir>/eval-fixture.yaml)

Exit codes:
  0 = success
  1 = judge mode: score below 70 (Silver threshold)
  2 = input error

Source: plugin-eval Layer 2 (judge.py) methodology via agents-main ref-adopt 2026-05-31.
Rubric anchors: docs/plugin-eval.md Layer 2 section.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ─── Rubric definitions ───────────────────────────────────────────────────────
# Source: plugin-eval docs/plugin-eval.md Layer 2: LLM Judge anchored rubrics

ORCHESTRATION_FITNESS_RUBRIC = """
5-point rubric for orchestration_fitness (worker vs orchestrator role):

  5 — Pure worker: takes a single well-defined input, produces a well-defined output,
      no sub-agent spawning, no multi-step orchestration described in body.
  4 — Mostly worker: orchestrates internally but does not spawn external agents.
      Has clear input/output contract.
  3 — Mixed: sometimes worker, sometimes orchestrator depending on context.
      Scope is ambiguous.
  2 — Mostly orchestrator: primarily spawns or coordinates other agents.
      Output depends heavily on sub-agent results.
  1 — Pure orchestrator: entire body describes multi-agent coordination.
      No standalone worker capability.

A well-calibrated skill should score 4 or 5. Score 1-2 indicates the skill
is doing orchestration that should belong to Executor or Autopilot.
"""

SCOPE_CALIBRATION_RUBRIC = """
5-point rubric for scope_calibration (is scope appropriate for domain?):

  5 — Perfectly sized: skill covers exactly one domain concept with appropriate
      depth. Neither too narrow (trivially simple) nor too broad (should be split).
  4 — Well-sized with minor overlap: one clear domain, slight boundary blur.
  3 — Acceptable but could be split or merged: scope includes 2 loosely related
      concepts that could reasonably be separate skills.
  2 — Oversized or undersized: clearly covers multiple distinct domains
      (should split) or is trivially simple (should merge into parent).
  1 — Wrong scope entirely: the skill's declared domain does not match its content.
      Content addresses a different problem than the name/description implies.
"""

OUTPUT_QUALITY_RUBRIC = """
5-point rubric for output_quality (would this skill produce correct, useful output?):

  5 — Output would be production-ready: instructions are specific enough that
      an agent following them would produce correct, complete results without
      further clarification.
  4 — Output would be correct with minor gaps: most cases covered; edge cases
      might require inference.
  3 — Output would be partially correct: instructions cover the happy path but
      miss important failure modes or edge cases.
  2 — Output would be inconsistent: ambiguous instructions would produce different
      results on repeated runs.
  1 — Output would be incorrect: instructions are wrong, contradictory, or
      underspecified to the point of being useless.
"""


# ─── Synthetic prompt generation ──────────────────────────────────────────────

def _extract_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm = {}
    for line in parts[1].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"\'')
    return fm, parts[2]


def generate_trigger_prompts(skill_name, description, body):
    """Generate 10 synthetic prompts: 5 should-trigger, 5 should-not.

    Strategy: extract key concepts from description and body to construct
    realistic trigger prompts. Generate contrasting prompts for negatives.
    """
    # Extract key phrases from description (after "Use when" clause)
    trigger_clause = re.search(
        r"(?:use when|use proactively when|activates when)\s+(.+?)(?:\.|$)",
        description, re.IGNORECASE
    )
    trigger_hint = trigger_clause.group(1).strip() if trigger_clause else description[:80]

    # Extract ## When to use section content
    when_match = re.search(
        r"## When to use\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL
    )
    when_content = when_match.group(1).strip() if when_match else ""

    # Extract ## When NOT to use section content
    when_not_match = re.search(
        r"## When NOT to use\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL
    )
    when_not_content = when_not_match.group(1).strip() if when_not_match else ""

    # Build fixture entries
    should_trigger = [
        {
            "id": "positive-001",
            "prompt": f"I need to {trigger_hint.lower().rstrip('.')}.",
            "should_trigger": True,
            "notes": f"Direct match to trigger clause in description of {skill_name}",
        },
        {
            "id": "positive-002",
            "prompt": f"Can you run /{skill_name} for this task?",
            "should_trigger": True,
            "notes": f"Explicit skill invocation — must trigger {skill_name}",
        },
        {
            "id": "positive-003",
            "prompt": f"Please activate {skill_name} on the current module.",
            "should_trigger": True,
            "notes": f"Direct activation request for {skill_name}",
        },
    ]

    # Extract up to 2 more positive cases from ## When to use bullets
    when_bullets = re.findall(r"^[-*]\s+(.+)$", when_content, re.MULTILINE)
    for i, bullet in enumerate(when_bullets[:2]):
        should_trigger.append({
            "id": f"positive-00{4 + i}",
            "prompt": bullet.strip().rstrip("."),
            "should_trigger": True,
            "notes": f"From '## When to use' section of {skill_name}",
        })

    # Pad to 5 if needed
    while len(should_trigger) < 5:
        n = len(should_trigger) + 1
        should_trigger.append({
            "id": f"positive-00{n}",
            "prompt": f"This scenario requires {skill_name} capabilities.",
            "should_trigger": True,
            "notes": f"Generic positive case {n} for {skill_name}",
        })

    should_not_trigger = [
        {
            "id": "negative-001",
            "prompt": f"This is the output from {skill_name} that you just ran — please review it.",
            "expected_skill": "wave-review",
            "should_trigger": False,
            "notes": f"Contains output-shaped content from {skill_name} but is a review request, not a re-run",
        },
        {
            "id": "negative-002",
            "prompt": "Please commit all current changes to git with a descriptive message.",
            "expected_skill": "commit",
            "should_trigger": False,
            "notes": "Commit request — unrelated to skill domain",
        },
        {
            "id": "negative-003",
            "prompt": "Show me the wave plan for the current task.",
            "expected_skill": "watzup",
            "should_trigger": False,
            "notes": "Session status request — should not trigger domain-specific skill",
        },
    ]

    # Extract up to 2 more negative cases from ## When NOT to use
    when_not_bullets = re.findall(r"^[-*]\s+(.+)$", when_not_content, re.MULTILINE)
    for i, bullet in enumerate(when_not_bullets[:2]):
        should_not_trigger.append({
            "id": f"negative-00{4 + i}",
            "prompt": bullet.strip().rstrip("."),
            "expected_skill": "other",
            "should_trigger": False,
            "notes": f"From '## When NOT to use' section of {skill_name}",
        })

    while len(should_not_trigger) < 5:
        n = len(should_not_trigger) + 1
        should_not_trigger.append({
            "id": f"negative-00{n}",
            "prompt": f"I'd like to review the {skill_name} output from last session.",
            "expected_skill": "wave-review",
            "should_trigger": False,
            "notes": f"Reviewing prior output — not a new {skill_name} invocation",
        })

    return should_trigger[:5] + should_not_trigger[:5]


# ─── Fixture generation ───────────────────────────────────────────────────────

def generate_fixture(skill_dir, content):
    """Generate a skill-tdd eval fixture for the given skill."""
    fm, body = _extract_frontmatter(content)
    name = fm.get("name") or os.path.basename(os.path.normpath(skill_dir))
    description = fm.get("description") or ""

    prompts = generate_trigger_prompts(name, description, body)

    fixture = {
        "skill": name,
        "skill_path": str(skill_dir),
        "generated_by": "quality-judge.py",
        "description": description,
        "eval_entries": prompts,
        "rubrics": {
            "orchestration_fitness": ORCHESTRATION_FITNESS_RUBRIC.strip(),
            "scope_calibration": SCOPE_CALIBRATION_RUBRIC.strip(),
            "output_quality": OUTPUT_QUALITY_RUBRIC.strip(),
        },
        "f1_target": 0.80,
        "instructions": (
            f"Run skill-tdd with this fixture to compute F1 triggering accuracy. "
            f"Use the should_trigger field to split positive/negative cases. "
            f"Use the rubrics section for LLM judge evaluation of semantic dimensions. "
            f"Target: F1 >= {0.80} for triggering_accuracy."
        ),
    }
    return fixture


# ─── Judge mode (API) ─────────────────────────────────────────────────────────

def judge_with_api(skill_dir, content, fixture):
    """Call Claude API to evaluate semantic dimensions. Returns judge_result dict.

    Requires ANTHROPIC_API_KEY in environment. Uses the fastest available
    capability for rubric scoring (haiku-tier equivalent for quick eval).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. JUDGE mode requires API access.", file=sys.stderr)
        return None

    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
        return None

    fm, body = _extract_frontmatter(content)
    name = fm.get("name") or os.path.basename(os.path.normpath(skill_dir))
    description = fm.get("description") or ""

    client = anthropic.Anthropic(api_key=api_key)

    judge_scores = {}
    rubric_pairs = [
        ("orchestration_fitness", ORCHESTRATION_FITNESS_RUBRIC),
        ("scope_calibration", SCOPE_CALIBRATION_RUBRIC),
        ("output_quality", OUTPUT_QUALITY_RUBRIC),
    ]

    for dim, rubric in rubric_pairs:
        prompt = f"""You are evaluating a Claude Code skill file for quality.

Skill name: {name}
Skill description: {description}

Skill body (first 2000 chars):
{body[:2000]}

RUBRIC for {dim}:
{rubric}

Score this skill on the {dim} dimension using the 5-point rubric above.
Respond with ONLY: a JSON object with keys "score" (1-5 integer) and "rationale" (one sentence).
"""
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                judge_scores[dim] = {
                    "score_1_to_5": data.get("score"),
                    "score_normalized": round((data.get("score", 3) - 1) / 4.0, 3),
                    "rationale": data.get("rationale", ""),
                }
            else:
                judge_scores[dim] = {"raw_response": raw, "parse_error": True}
        except Exception as e:
            judge_scores[dim] = {"error": str(e)}

    return {
        "skill": name,
        "judge_dimensions": judge_scores,
        "note": "LLM judge scores for semantic dimensions (Layer 2 analog). Combine with quality-score.py Layer 1 output for composite.",
    }


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WabbleSpec LLM semantic quality evaluator for SKILL.md files"
    )
    parser.add_argument("skill_dir", help="Path to skill directory containing SKILL.md")
    parser.add_argument("--judge", action="store_true",
                        help="Call API for semantic dimension scoring (requires ANTHROPIC_API_KEY)")
    parser.add_argument("--output", choices=["yaml", "json", "markdown"], default="yaml",
                        help="Output format (default: yaml)")
    parser.add_argument("--fixture-out", metavar="PATH",
                        help="Write fixture file to PATH (default: <skill_dir>/eval-fixture.yaml)")
    parser.add_argument("--threshold", type=float, default=0,
                        help="Exit 1 if judge avg score below threshold (0-10 scale)")
    args = parser.parse_args()

    skill_dir = args.skill_dir
    if not os.path.isdir(skill_dir):
        print(f"ERROR: skill directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(2)

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        print(f"ERROR: no SKILL.md found in {skill_dir}", file=sys.stderr)
        sys.exit(2)

    with open(skill_md, encoding="utf-8-sig") as f:
        content = f.read()

    fixture = generate_fixture(skill_dir, content)

    # Write fixture file
    fixture_path = args.fixture_out or os.path.join(skill_dir, "eval-fixture.yaml")
    if args.output in ("yaml",) or args.fixture_out:
        if HAS_YAML:
            with open(fixture_path, "w", encoding="utf-8") as f:
                yaml.dump(fixture, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            print(f"Eval fixture written: {fixture_path}")
        else:
            # Fallback: write JSON
            fixture_path = fixture_path.replace(".yaml", ".json")
            with open(fixture_path, "w", encoding="utf-8") as f:
                json.dump(fixture, f, indent=2)
            print(f"Eval fixture written (JSON fallback, pyyaml not installed): {fixture_path}")

    # Output fixture summary
    if args.output == "json":
        print(json.dumps(fixture, indent=2))
    elif args.output == "markdown":
        fm, body = _extract_frontmatter(content)
        name = fm.get("name") or os.path.basename(os.path.normpath(skill_dir))
        print(f"# Quality Judge: {name}")
        print()
        print(f"**Fixture written:** `{fixture_path}`")
        print(f"**Eval entries:** {len(fixture['eval_entries'])} ({sum(1 for e in fixture['eval_entries'] if e['should_trigger'])} positive, {sum(1 for e in fixture['eval_entries'] if not e['should_trigger'])} negative)")
        print(f"**F1 target:** >= {fixture['f1_target']}")
        print()
        print("## Eval Entries")
        for entry in fixture["eval_entries"]:
            mark = "+" if entry["should_trigger"] else "-"
            print(f"  [{mark}] {entry['id']}: {entry['prompt'][:80]}")
    else:
        # yaml mode: summary to stdout only
        print(f"Skill: {fixture['skill']}")
        print(f"Entries: {len(fixture['eval_entries'])} ({sum(1 for e in fixture['eval_entries'] if e['should_trigger'])} positive, {sum(1 for e in fixture['eval_entries'] if not e['should_trigger'])} negative)")
        print(f"Fixture: {fixture_path}")

    # Judge mode
    if args.judge:
        print("\nRunning LLM judge evaluation...")
        judge_result = judge_with_api(skill_dir, content, fixture)
        if judge_result:
            print(json.dumps(judge_result, indent=2))
            # Check threshold
            if args.threshold > 0:
                scores = [
                    d.get("score_normalized", 0.5) * 10
                    for d in judge_result.get("judge_dimensions", {}).values()
                    if "score_normalized" in d
                ]
                if scores:
                    avg = sum(scores) / len(scores)
                    if avg < args.threshold:
                        print(f"\nFAIL: avg judge score {avg:.1f} below threshold {args.threshold}", file=sys.stderr)
                        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
