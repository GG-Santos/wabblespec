"""
pattern-inference.py — Classify a task description into an orchestration pattern.

Reads the task goal text and complexity score, outputs a JSON object with:
  pattern        — named orchestration pattern
  confidence     — 0.0-1.0 float
  signals        — list of signal strings that drove the classification
  needs_clarification — bool (true if multiple patterns are equally likely)
  work_breakdown — string (how the work maps to the pattern)

Usage:
    python pattern-inference.py --goal "Build a REST API for user auth" --complexity 3

    # From task card file:
    python pattern-inference.py --task-card .wabblespec/state/plans/task-card.md

Output: JSON to stdout. Exit 0 on success, 1 on error.

Patterns:
    hierarchical      — one orchestrator delegates to specialized subagents
    pipeline          — sequential transform stages, each stage consumes prior output
    swarm             — parallel independent agents, results merged at the end
    generator-critic  — one agent proposes, another critiques, iterates
    adversarial       — attack/defend structure, stress-test outputs
    jury              — multiple independent evaluators, consensus determines verdict

Complexity scale: 1 (trivial) to 10 (highly complex).
"""

import sys
import os
import json
import argparse
import re

PATTERNS = {
    "hierarchical": {
        "keywords": ["orchestrate", "delegate", "coordinate", "manage", "workflow",
                     "multi-step", "multi-stage", "pipeline orchestration", "executor",
                     "phases", "waves", "decompose"],
        "signals": ["multi-wave task", "phase-gated execution", "module delegation"],
        "work_breakdown": "Orchestrator manages phase transitions; specialized modules execute each phase.",
        "base_confidence": 0.55,
    },
    "pipeline": {
        "keywords": ["transform", "process", "ingest", "extract", "parse", "convert",
                     "ETL", "data pipeline", "sequential", "chain", "stage"],
        "signals": ["sequential data transforms", "each stage consumes prior output"],
        "work_breakdown": "Each stage transforms the output of the prior stage; no stage can skip ahead.",
        "base_confidence": 0.5,
    },
    "swarm": {
        "keywords": ["parallel", "independent", "concurrent", "fan-out", "distributed",
                     "multiple agents", "batch", "enumerate", "scan", "survey"],
        "signals": ["independent parallel subtasks", "results merged at end"],
        "work_breakdown": "Multiple agents run concurrently on independent chunks; outputs merged.",
        "base_confidence": 0.5,
    },
    "generator-critic": {
        "keywords": ["draft", "review", "iterate", "refine", "improve", "critique",
                     "feedback loop", "red-green", "revise", "verify output"],
        "signals": ["proposal-critique loop", "iterative refinement"],
        "work_breakdown": "Generator proposes; Critic evaluates; loop until acceptance threshold.",
        "base_confidence": 0.45,
    },
    "adversarial": {
        "keywords": ["attack", "stress", "security", "adversarial", "fuzzing",
                     "pressure", "exploit", "bypass", "harden", "guard"],
        "signals": ["attack/defend structure", "stress-testing outputs"],
        "work_breakdown": "Adversary attempts to break or bypass; Defender hardens against findings.",
        "base_confidence": 0.45,
    },
    "jury": {
        "keywords": ["evaluate", "grade", "score", "rank", "compare", "select best",
                     "consensus", "multiple reviewers", "judge", "verdict"],
        "signals": ["multiple independent evaluators", "consensus verdict"],
        "work_breakdown": "N independent reviewers each evaluate the artifact; consensus or majority determines verdict.",
        "base_confidence": 0.45,
    },
}

# Complexity modifiers: high complexity tasks tend toward hierarchical/pipeline
COMPLEXITY_BOOSTS = {
    "hierarchical": [(7, +0.1), (9, +0.05)],
    "pipeline": [(5, +0.05)],
    "swarm": [(6, +0.05)],
}


def classify(goal_text, complexity):
    goal_lower = goal_text.lower()
    scores = {}

    for pattern, config in PATTERNS.items():
        score = config["base_confidence"]
        matched_signals = []

        for kw in config["keywords"]:
            if kw.lower() in goal_lower:
                score += 0.06
                matched_signals.append(f"keyword: {kw}")

        # Complexity boosts
        for threshold, boost in COMPLEXITY_BOOSTS.get(pattern, []):
            if complexity >= threshold:
                score += boost

        scores[pattern] = {
            "confidence": min(score, 0.98),
            "signals": matched_signals or config["signals"][:1],
            "work_breakdown": config["work_breakdown"],
        }

    # Sort by confidence
    ranked = sorted(scores.items(), key=lambda x: x[1]["confidence"], reverse=True)
    best_pattern, best_data = ranked[0]
    second_pattern, second_data = ranked[1]

    # needs_clarification if top two are within 0.08 of each other AND both > 0.55
    needs_clarification = (
        abs(best_data["confidence"] - second_data["confidence"]) < 0.08
        and best_data["confidence"] > 0.55
        and second_data["confidence"] > 0.55
    )

    return {
        "pattern": best_pattern,
        "confidence": round(best_data["confidence"], 3),
        "signals": best_data["signals"],
        "needs_clarification": needs_clarification,
        "work_breakdown": best_data["work_breakdown"],
        "alternatives": [
            {"pattern": p, "confidence": round(d["confidence"], 3)}
            for p, d in ranked[1:3]
        ],
    }


def extract_goal_from_task_card(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("**goal:**"):
                    return line.replace("**goal:**", "").strip()
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Classify a task into an orchestration pattern.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--goal", metavar="TEXT", help="Task goal text (one sentence).")
    parser.add_argument("--complexity", type=float, default=5.0, metavar="N",
                        help="Complexity score 1-10 (default: 5).")
    parser.add_argument("--task-card", metavar="PATH",
                        help="Read goal from task-card.md instead of --goal.")
    args = parser.parse_args()

    goal = args.goal
    if args.task_card:
        goal = extract_goal_from_task_card(args.task_card)
        if not goal:
            print("ERROR: could not extract goal from task card.", file=sys.stderr)
            sys.exit(1)

    if not goal:
        print("ERROR: provide --goal or --task-card.", file=sys.stderr)
        sys.exit(1)

    result = classify(goal, args.complexity)
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
