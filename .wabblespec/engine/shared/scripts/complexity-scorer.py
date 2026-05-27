#!/usr/bin/env python3
"""
complexity-scorer.py

Deterministic complexity scorer for Decompose tasks.
5-factor scoring: file_scope, dependency_count, breaking_delta, test_coverage_gap, cross_layer.
Same input always produces same score.

Usage:
    python complexity-scorer.py --task-card <path> [--wave-plan <path>] [--json]

Output: score 0.0-1.0, scale level L0-L4
Exit: 0 always (scorer never blocks)
"""

import re
import sys
import json
import argparse
from pathlib import Path


SCALE_THRESHOLDS = [
    (0.0, 0.2, "L0", "Trivial"),
    (0.2, 0.4, "L1", "Routine"),
    (0.4, 0.65, "L2", "Complex"),
    (0.65, 0.85, "L3", "Critical"),
    (0.85, 1.01, "L4", "Cross-system"),
]


def score_file_scope(task_text: str, wave_text: str) -> tuple[float, str]:
    """Factor 1: Number of files declared in wave plan."""
    all_text = task_text + "\n" + wave_text
    file_refs = re.findall(r"(?:src/|lib/|app/|tests/)[^\s`\"']+", all_text)
    unique_files = len(set(file_refs))
    if unique_files == 0:
        score = 0.1
    elif unique_files <= 2:
        score = 0.2
    elif unique_files <= 5:
        score = 0.4
    elif unique_files <= 10:
        score = 0.7
    else:
        score = 1.0
    return score, f"{unique_files} file references"


def score_dependency_count(task_text: str, wave_text: str) -> tuple[float, str]:
    """Factor 2: External dependencies introduced or changed."""
    all_text = task_text + "\n" + wave_text
    dep_signals = re.findall(
        r"(import|require|from|install|package\.json|requirements\.txt|go\.mod|Cargo\.toml)",
        all_text, re.IGNORECASE
    )
    count = len(dep_signals)
    if count == 0:
        score = 0.0
    elif count <= 2:
        score = 0.2
    elif count <= 5:
        score = 0.4
    else:
        score = 0.7
    return score, f"{count} dependency signals"


def score_breaking_delta(task_text: str) -> tuple[float, str]:
    """Factor 3: BREAKING change classification."""
    if re.search(r"change_class:\s*BREAKING|delta_class:\s*BREAKING", task_text, re.IGNORECASE):
        return 1.0, "BREAKING delta class"
    if re.search(r"change_class:\s*ADDITIVE|delta_class:\s*ADDITIVE", task_text, re.IGNORECASE):
        return 0.3, "ADDITIVE delta class"
    if re.search(r"change_class:\s*COSMETIC|delta_class:\s*COSMETIC", task_text, re.IGNORECASE):
        return 0.0, "COSMETIC delta class"
    return 0.2, "delta class undeclared"


def score_test_coverage_gap(task_text: str, wave_text: str) -> tuple[float, str]:
    """Factor 4: Test coverage signals."""
    all_text = task_text + "\n" + wave_text
    has_tests = bool(re.search(r"test[s]?/|\.test\.|\.spec\.|pytest|unittest|testing", all_text, re.IGNORECASE))
    has_not_tested = bool(re.search(r"not[_-]tested|not tested|no test", all_text, re.IGNORECASE))
    if has_tests and not has_not_tested:
        return 0.1, "tests declared"
    if has_not_tested:
        return 0.7, "not-tested items present"
    return 0.4, "no test declarations found"


def score_cross_layer(task_text: str, wave_text: str) -> tuple[float, str]:
    """Factor 5: Cross-layer or cross-system coordination."""
    all_text = task_text + "\n" + wave_text
    layer_refs = re.findall(r"\b[Ll][0-9]\b", all_text)
    unique_layers = len(set(layer_refs))
    module_refs = re.findall(r"\b(autopilot|ensemble|team.?plan|gateway|platform)\b", all_text, re.IGNORECASE)
    cross_signals = unique_layers + len(set(m.lower() for m in module_refs))
    if cross_signals == 0:
        score = 0.0
    elif cross_signals <= 2:
        score = 0.2
    elif cross_signals <= 4:
        score = 0.5
    else:
        score = 0.9
    return score, f"{cross_signals} cross-layer signals"


def compute_scale(score: float) -> tuple[str, str]:
    for lo, hi, level, label in SCALE_THRESHOLDS:
        if lo <= score < hi:
            return level, label
    return "L4", "Cross-system"


def main():
    parser = argparse.ArgumentParser(description="Deterministic complexity scorer for Decompose tasks.")
    parser.add_argument("--task-card", required=True, help="Path to task-card.md")
    parser.add_argument("--wave-plan", help="Path to wave-plan.md (optional)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    task_path = Path(args.task_card)
    if not task_path.exists():
        print(f"ERROR: task-card not found: {task_path}", file=sys.stderr)
        sys.exit(2)

    task_text = task_path.read_text(encoding="utf-8", errors="replace")
    wave_text = ""
    if args.wave_plan:
        wave_path = Path(args.wave_plan)
        if wave_path.exists():
            wave_text = wave_path.read_text(encoding="utf-8", errors="replace")

    factors = {
        "file_scope": score_file_scope(task_text, wave_text),
        "dependency_count": score_dependency_count(task_text, wave_text),
        "breaking_delta": score_breaking_delta(task_text),
        "test_coverage_gap": score_test_coverage_gap(task_text, wave_text),
        "cross_layer": score_cross_layer(task_text, wave_text),
    }

    weights = {
        "file_scope": 0.25,
        "dependency_count": 0.15,
        "breaking_delta": 0.30,
        "test_coverage_gap": 0.15,
        "cross_layer": 0.15,
    }

    total_score = sum(factors[f][0] * weights[f] for f in factors)
    total_score = round(min(max(total_score, 0.0), 1.0), 3)
    scale_level, scale_label = compute_scale(total_score)

    result = {
        "score": total_score,
        "scale_level": scale_level,
        "scale_label": scale_label,
        "factors": {
            name: {"score": round(val[0], 3), "evidence": val[1], "weight": weights[name]}
            for name, val in factors.items()
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"complexity-scorer: {total_score:.3f} → {scale_level} ({scale_label})")
        for name, data in result["factors"].items():
            print(f"  {name}: {data['score']:.2f} (weight {data['weight']}) — {data['evidence']}")

    sys.exit(0)


if __name__ == "__main__":
    main()
