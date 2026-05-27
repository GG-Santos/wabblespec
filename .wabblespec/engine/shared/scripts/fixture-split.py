"""
fixture-split.py — Deterministic dev/held-out split and golden.json scaffold for benchmark fixtures.

Replaces Claude manually computing the split and writing split.json and golden.json. Both
outputs are fully deterministic from the fixture cases and a seed value.

The golden.json scaffold populates case_id, expected_outcome, and verdict=TBD from the
fixture's `expected_outcome` field. The `augmented_*_behavior` narrative is written by
Claude during Benchmark evaluation — this script only creates the structural scaffold.

Subcommands:
    split     Generate split.json from fixtures.json
    golden    Generate golden.json scaffold from fixtures.json
    all       Generate both split.json and golden.json in one pass
    validate  Verify an existing split against its fixtures

Usage:
    # Generate split.json:
    python .wabblespec/engine/shared/scripts/fixture-split.py split \\
        --fixtures .wabblespec/state/experiments/fixtures/my-candidate-v1/fixtures.json \\
        --seed 4202 \\
        --dev-ratio 0.2

    # Generate golden.json scaffold:
    python .wabblespec/engine/shared/scripts/fixture-split.py golden \\
        --fixtures .wabblespec/state/experiments/fixtures/my-candidate-v1/fixtures.json \\
        --outcome-field expected_outcome \\
        --developer-outcome false_completion \\
        --metric false_completion_rate

    # Both in one pass:
    python .wabblespec/engine/shared/scripts/fixture-split.py all \\
        --fixtures .wabblespec/state/experiments/fixtures/my-candidate-v1/fixtures.json \\
        --seed 4202 \\
        --dev-ratio 0.2

    # Validate an existing split:
    python .wabblespec/engine/shared/scripts/fixture-split.py validate \\
        --fixtures .wabblespec/state/experiments/fixtures/my-candidate-v1/fixtures.json

    # Dry run:
    python .wabblespec/engine/shared/scripts/fixture-split.py all ... --dry-run

Split algorithm:
    Shuffle all case IDs using the given seed (Python random.Random(seed)).
    Take floor(n * dev_ratio) as dev, minimum 1.
    Remainder goes to held_out.
    With 10 cases and dev_ratio=0.2: 2 dev, 8 held_out.

Exit codes:
    0  success
    1  fixtures.json not found or malformed
    2  output path not writable
"""

import sys
import os
import json
import argparse
import random
import math
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_fixtures(path):
    if not os.path.isfile(path):
        print(f"ERROR: fixtures.json not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)

    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) == 0:
        print(f"ERROR: fixtures.json must have a non-empty 'cases' array: {path}", file=sys.stderr)
        sys.exit(1)

    return data, cases


def write_json(path, data, dry_run=False):
    text = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"--- [DRY RUN] {path} ---")
        print(text)
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        print(f"ERROR: Cannot write {path}: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Wrote {path}")


def fixture_dir(fixtures_path):
    return os.path.dirname(os.path.abspath(fixtures_path))


def fixture_set_name(fixtures_path):
    """Returns the parent directory name as the fixture set name."""
    return os.path.basename(fixture_dir(fixtures_path))


def fixture_set_rel_path(fixtures_path):
    """Returns relative path to the fixture set directory."""
    fdir = fixture_dir(fixtures_path)
    try:
        return os.path.relpath(fdir).replace("\\", "/") + "/"
    except ValueError:
        return fdir.replace("\\", "/") + "/"


# ---------------------------------------------------------------------------
# Split algorithm
# ---------------------------------------------------------------------------

def compute_split(case_ids, seed, dev_ratio):
    """
    Shuffle case_ids with given seed.
    dev_count = max(1, floor(n * dev_ratio))
    Returns (dev_cases, held_out_cases).
    """
    rng = random.Random(seed)
    shuffled = list(case_ids)
    rng.shuffle(shuffled)

    n = len(shuffled)
    dev_count = max(1, math.floor(n * dev_ratio))
    # Ensure at least 1 held-out case
    if dev_count >= n:
        dev_count = n - 1

    return shuffled[:dev_count], shuffled[dev_count:]


# ---------------------------------------------------------------------------
# Build split.json
# ---------------------------------------------------------------------------

def build_split(fixtures_data, cases, fixtures_path, seed, dev_ratio):
    case_ids = [c["id"] for c in cases]
    dev_cases, held_out_cases = compute_split(case_ids, seed, dev_ratio)

    return {
        "version": "1.0",
        "fixture_set": fixture_set_rel_path(fixtures_path),
        "created_at": now_utc(),
        "seed": seed,
        "split_method": "random",
        "total_cases": len(case_ids),
        "dev_cases": dev_cases,
        "held_out_cases": held_out_cases,
    }


# ---------------------------------------------------------------------------
# Build golden.json scaffold
# ---------------------------------------------------------------------------

def build_golden(fixtures_data, cases, fixtures_path, split_data,
                 outcome_field, developer_outcome, metric):
    """
    Build golden.json scaffold from the held-out cases.
    Extracts expected_outcome from each case.
    The `behavior` narrative fields are left as TBD for Claude to fill during Benchmark.
    """
    held_out_ids = set(split_data["held_out_cases"])
    held_out_cases = [c for c in cases if c["id"] in held_out_ids]

    # Sort by the split order
    id_order = {cid: i for i, cid in enumerate(split_data["held_out_cases"])}
    held_out_cases.sort(key=lambda c: id_order.get(c["id"], 999))

    evaluations = []
    for case in held_out_cases:
        expected = case.get(outcome_field, "?")
        eval_entry = {
            "case_id": case["id"],
            "expected_outcome": expected,
            f"{developer_outcome}_occurred": False,
            "verdict": "TBD",
            "notes": "",
        }
        evaluations.append(eval_entry)

    fs_name = fixture_set_name(fixtures_path)
    total_held = len(evaluations)
    metric_display = metric or f"{developer_outcome}_rate"

    return {
        "fixture_set": fs_name,
        "generated_at": now_utc(),
        "held_out_evaluations": evaluations,
        f"held_out_{developer_outcome}s": 0,
        "held_out_total": total_held,
        f"held_out_{metric_display}": None,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def cmd_validate(args):
    fixtures_path = args.fixtures
    fdir = fixture_dir(fixtures_path)
    split_path = os.path.join(fdir, "split.json")
    golden_path = os.path.join(fdir, "golden.json")

    _, cases = load_fixtures(fixtures_path)
    case_ids = {c["id"] for c in cases}

    errors = []

    if os.path.isfile(split_path):
        try:
            with open(split_path, encoding="utf-8") as f:
                split = json.load(f)
            split_ids = set(split.get("dev_cases", [])) | set(split.get("held_out_cases", []))
            missing = split_ids - case_ids
            extra = case_ids - split_ids
            if missing:
                errors.append(f"split.json references unknown case IDs: {sorted(missing)}")
            if extra:
                errors.append(f"split.json is missing case IDs: {sorted(extra)}")
            if split.get("total_cases") != len(cases):
                errors.append(
                    f"split.json total_cases={split.get('total_cases')} "
                    f"but fixtures has {len(cases)} cases"
                )
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Cannot read split.json: {e}")
    else:
        errors.append(f"split.json not found at {split_path}")

    if os.path.isfile(golden_path):
        try:
            with open(golden_path, encoding="utf-8") as f:
                golden = json.load(f)
            golden_ids = {e["case_id"] for e in golden.get("held_out_evaluations", [])}
            split_held = set(split.get("held_out_cases", [])) if os.path.isfile(split_path) else set()
            if split_held and golden_ids != split_held:
                missing_g = split_held - golden_ids
                extra_g = golden_ids - split_held
                if missing_g:
                    errors.append(f"golden.json missing held-out cases: {sorted(missing_g)}")
                if extra_g:
                    errors.append(f"golden.json has unexpected cases: {sorted(extra_g)}")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Cannot read golden.json: {e}")
    else:
        errors.append(f"golden.json not found at {golden_path}")

    if errors:
        print(f"FAIL  {fixtures_path}")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"PASS  {fixtures_path}")
        print(f"  cases: {len(cases)}, split.json OK, golden.json OK")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_split(args, dry_run=False):
    _, cases = load_fixtures(args.fixtures)
    fdir = fixture_dir(args.fixtures)
    out_path = os.path.join(fdir, "split.json")

    fixtures_data = {}
    split = build_split(fixtures_data, cases, args.fixtures, args.seed, args.dev_ratio)

    dev_count = len(split["dev_cases"])
    held_count = len(split["held_out_cases"])
    print(f"Split: {len(cases)} cases -> {dev_count} dev, {held_count} held-out "
          f"(seed={args.seed}, dev_ratio={args.dev_ratio})")

    write_json(out_path, split, dry_run=dry_run)
    return split


def cmd_golden(args, split_data=None, dry_run=False):
    _, cases = load_fixtures(args.fixtures)
    fdir = fixture_dir(args.fixtures)

    # Load split if not provided
    if split_data is None:
        split_path = os.path.join(fdir, "split.json")
        if not os.path.isfile(split_path):
            print(f"ERROR: split.json not found at {split_path}. "
                  f"Run 'split' subcommand first or use 'all'.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(split_path, encoding="utf-8") as f:
                split_data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR: Cannot read split.json: {e}", file=sys.stderr)
            sys.exit(2)

    out_path = os.path.join(fdir, "golden.json")

    outcome_field = args.outcome_field if hasattr(args, "outcome_field") and args.outcome_field else "expected_outcome"
    developer_outcome = args.developer_outcome if hasattr(args, "developer_outcome") and args.developer_outcome else "false_completion"
    metric = args.metric if hasattr(args, "metric") and args.metric else None

    golden = build_golden({}, cases, args.fixtures, split_data,
                          outcome_field, developer_outcome, metric)

    held_count = len(golden["held_out_evaluations"])
    print(f"Golden scaffold: {held_count} held-out evaluations (outcome_field='{outcome_field}')")
    write_json(out_path, golden, dry_run=dry_run)


def cmd_all(args):
    # Generate split first, then pass to golden
    split = cmd_split(args, dry_run=args.dry_run)
    cmd_golden(args, split_data=split, dry_run=args.dry_run)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Deterministic dev/held-out split and golden.json scaffold for benchmark fixtures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # split
    p_split = sub.add_parser("split", help="Generate split.json from fixtures.json.")
    p_split.add_argument("--fixtures", required=True, metavar="PATH")
    p_split.add_argument("--seed", type=int, default=4202, metavar="INT")
    p_split.add_argument("--dev-ratio", type=float, default=0.2, metavar="0.0-1.0",
                         dest="dev_ratio")
    p_split.add_argument("--dry-run", action="store_true")

    # golden
    p_golden = sub.add_parser("golden", help="Generate golden.json scaffold from fixtures.json.")
    p_golden.add_argument("--fixtures", required=True, metavar="PATH")
    p_golden.add_argument("--outcome-field", default="expected_outcome", metavar="FIELD",
                          dest="outcome_field")
    p_golden.add_argument("--developer-outcome", default="false_completion", metavar="OUTCOME",
                          dest="developer_outcome")
    p_golden.add_argument("--metric", metavar="METRIC_NAME",
                          help="Metric name for summary field (default: {developer_outcome}_rate).")
    p_golden.add_argument("--dry-run", action="store_true")

    # all
    p_all = sub.add_parser("all", help="Generate both split.json and golden.json.")
    p_all.add_argument("--fixtures", required=True, metavar="PATH")
    p_all.add_argument("--seed", type=int, default=4202, metavar="INT")
    p_all.add_argument("--dev-ratio", type=float, default=0.2, metavar="0.0-1.0",
                       dest="dev_ratio")
    p_all.add_argument("--outcome-field", default="expected_outcome", metavar="FIELD",
                       dest="outcome_field")
    p_all.add_argument("--developer-outcome", default="false_completion", metavar="OUTCOME",
                       dest="developer_outcome")
    p_all.add_argument("--metric", metavar="METRIC_NAME")
    p_all.add_argument("--dry-run", action="store_true")

    # validate
    p_val = sub.add_parser("validate", help="Verify split and golden against fixtures.")
    p_val.add_argument("--fixtures", required=True, metavar="PATH")

    args = parser.parse_args()
    if not hasattr(args, "dry_run"):
        args.dry_run = False

    if args.command == "split":
        cmd_split(args, dry_run=args.dry_run)
    elif args.command == "golden":
        cmd_golden(args, dry_run=args.dry_run)
    elif args.command == "all":
        cmd_all(args)
    elif args.command == "validate":
        cmd_validate(args)

    sys.exit(0)


if __name__ == "__main__":
    main()
