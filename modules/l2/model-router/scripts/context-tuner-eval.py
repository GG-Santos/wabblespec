#!/usr/bin/env python3
"""
ContextTuner fixture evaluator for model-router.
Imports _shared/scripts/context-tuner.py and runs the labeled fixture set.

Usage:
    python context-tuner-eval.py
    python context-tuner-eval.py --fixture-dir ../fixtures
    python context-tuner-eval.py --held-out-only
    python context-tuner-eval.py --verbose
"""

import argparse
import json
import os
import sys

# Resolve _shared/scripts from this module path:
# modules/l2/model-router/scripts/ -> up 4 levels -> project root -> _shared/scripts/
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, "..", "..", "..", ".."))
_shared_scripts = os.path.join(_root, "_shared", "scripts")
sys.path.insert(0, _shared_scripts)

try:
    import context_tuner  # context-tuner.py exposed as context_tuner module
except ImportError:
    # Fallback: try importing from context-tuner.py directly via importlib
    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        "context_tuner",
        os.path.join(_shared_scripts, "context-tuner.py")
    )
    context_tuner = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(context_tuner)


def load_fixtures(fixture_dir: str, held_out_only: bool = False) -> list[dict]:
    split_path = os.path.join(fixture_dir, "split.json")
    if not os.path.exists(split_path):
        print(f"ERROR: split.json not found at {split_path}", file=sys.stderr)
        sys.exit(1)

    with open(split_path) as f:
        split = json.load(f)

    if held_out_only:
        fixture_files = split.get("held_out", [])
    else:
        fixture_files = split.get("held_out", [])  # Always eval on held-out only

    fixtures = []
    for fname in fixture_files:
        fpath = os.path.join(fixture_dir, fname)
        if not os.path.exists(fpath):
            print(f"WARNING: fixture file not found: {fpath}", file=sys.stderr)
            continue
        with open(fpath) as f:
            fixtures.append(json.load(f))

    return fixtures


def evaluate(fixtures: list[dict], verbose: bool = False) -> dict:
    correct = 0
    total = len(fixtures)
    per_type: dict[str, dict] = {}

    for case in fixtures:
        label = case["label"]
        message = case["message"]
        history = case.get("history", [])

        result = context_tuner.classify(message=message, history=history)
        detected = result["detected_type"]
        hit = detected == label

        if label not in per_type:
            per_type[label] = {"correct": 0, "total": 0}
        per_type[label]["total"] += 1

        if hit:
            correct += 1
            per_type[label]["correct"] += 1

        if verbose:
            status = "OK" if hit else "FAIL"
            print(f"  [{status}] label={label} detected={detected} confidence={result['confidence']:.2f}")
            if not hit:
                print(f"         message={message[:80]!r}")

    accuracy = correct / total if total > 0 else 0.0

    per_type_acc = {}
    for t, counts in per_type.items():
        per_type_acc[t] = round(counts["correct"] / counts["total"], 4) if counts["total"] > 0 else 0.0

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "threshold": 0.80,
        "verdict": "PASS" if accuracy >= 0.80 else "FAIL",
        "per_type": per_type_acc
    }


def main():
    parser = argparse.ArgumentParser(description="ContextTuner benchmark evaluator")
    parser.add_argument("--fixture-dir", default=os.path.join(_here, "..", "fixtures"),
                        help="Path to fixtures directory (default: ../fixtures)")
    parser.add_argument("--held-out-only", action="store_true",
                        help="Evaluate on held-out split only (default behavior)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show per-case results")
    args = parser.parse_args()

    fixture_dir = os.path.abspath(args.fixture_dir)
    print(f"Fixture dir: {fixture_dir}")

    fixtures = load_fixtures(fixture_dir, held_out_only=args.held_out_only)
    print(f"Loaded {len(fixtures)} held-out cases")

    results = evaluate(fixtures, verbose=args.verbose)

    print(f"\nAccuracy: {results['accuracy']:.1%} ({results['correct']}/{results['total']})")
    print(f"Threshold: {results['threshold']:.0%}")
    print(f"Verdict: {results['verdict']}")
    print("\nPer-type accuracy:")
    for t, acc in sorted(results["per_type"].items()):
        print(f"  {t:<20} {acc:.1%}")

    sys.exit(0 if results["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
