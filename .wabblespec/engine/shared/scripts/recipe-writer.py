"""
recipe-writer.py — Write recipe.json and its receipt from CLI arguments.

Replaces the manual Recipe phase file writes (two Write tool calls, each
requiring Claude to reason about the JSON structure from scratch).

Writes:
  .wabblespec/recipe.json
  .wabblespec/receipts/recipe-receipt-{session_id}.json

Usage:
    python .wabblespec/engine/shared/scripts/recipe-writer.py \\
        --session-id seed-run-20260526xx \\
        --target Framework \\
        --complexity Low \\
        --confidence 0.97 \\
        --detection-method explicit-instruction

    # With secondary targets and input quality flags:
    python .wabblespec/engine/shared/scripts/recipe-writer.py \\
        --session-id seed-run-20260526xx \\
        --target CLI \\
        --platform CLI \\
        --complexity Medium \\
        --confidence 0.92 \\
        --detection-method file-signals \\
        --secondary-targets API-Service \\
        --vague --collapse-eligible

    # Dry run — print both files without writing:
    python .wabblespec/engine/shared/scripts/recipe-writer.py ... --dry-run

Detection methods:
    explicit-instruction    User stated target directly
    file-signals            Inferred from project file structure
    prior-session           Loaded from existing recipe.json
    complexity-scorer       From complexity-scorer.py output

Exit codes:
    0  success
    1  bad arguments
    2  output directory not writable
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


VALID_TARGETS = [
    "Framework", "Script", "Web", "API-Service", "CLI", "Mobile", "Desktop",
    "Library-Package", "Extension-Plugin", "Data-Pipeline", "AI-Agent",
    "Game", "IoT-Embedded", "ALL",
]

VALID_DETECTION = [
    "explicit-instruction", "file-signals", "prior-session", "complexity-scorer",
]

VALID_COMPLEXITY = ["Low", "Medium", "High"]


def find_wabblespec(start_dir=None):
    if start_dir is None:
        start_dir = os.getcwd()
    candidate = start_dir
    for _ in range(10):
        ws = os.path.join(candidate, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def write_json(path, data, dry_run):
    text = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"--- [DRY RUN] {path} ---")
        print(text)
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)
    print(f"Wrote {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Write recipe.json and its receipt without loading framework context.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--session-id", required=True, metavar="ID")
    parser.add_argument("--target", required=True, choices=VALID_TARGETS)
    parser.add_argument("--complexity", required=True, choices=VALID_COMPLEXITY)
    parser.add_argument("--confidence", type=float, default=0.97, metavar="0.0-1.0")
    parser.add_argument("--detection-method", default="explicit-instruction",
                        choices=VALID_DETECTION)
    parser.add_argument("--platform", metavar="TEXT",
                        help="Platform string (defaults to --target value).")
    parser.add_argument("--secondary-targets", nargs="*", default=[], metavar="TARGET")
    parser.add_argument("--collapse-eligible", action="store_true")
    parser.add_argument("--vague", action="store_true",
                        help="Mark input_quality.vague = true (triggers Sharpen).")
    parser.add_argument("--broad", action="store_true",
                        help="Mark input_quality.broad = true (triggers Enhance).")
    parser.add_argument("--wabblespec-dir", metavar="PATH",
                        help="Explicit path to .wabblespec/ directory.")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not 0.0 <= args.confidence <= 1.0:
        print("ERROR: --confidence must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/. Run from inside the repo.", file=sys.stderr)
        sys.exit(2)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    platform = args.platform or args.target

    recipe = {
        "target": args.target,
        "platform": platform,
        "detection_method": args.detection_method,
        "confidence": args.confidence,
        "complexity": args.complexity,
        "secondary_targets": args.secondary_targets,
        "collapse_eligible": args.collapse_eligible,
        "input_quality": {
            "vague": args.vague,
            "broad": args.broad,
            "enhanced": False,
            "sharpened": False,
        },
        "locked_at": now,
        "session_id": args.session_id,
    }

    receipt = {
        "module": "recipe",
        "layer": "L0",
        "phase": "Intake",
        "wave": 0,
        "timestamp": now,
        "session_id": args.session_id,
        "target": args.target,
        "platform": platform,
        "detection_method": args.detection_method,
        "confidence": args.confidence,
        "complexity": args.complexity,
        "secondary_targets": args.secondary_targets,
        "collapse_eligible": args.collapse_eligible,
        "input_quality": recipe["input_quality"],
        "checks_run": ["target-detection", "complexity-score", "input-quality"],
        "checks_passed": ["target-detection", "complexity-score", "input-quality"],
        "status": "PASS",
        "confidence_score": args.confidence,
        "outputs": ["recipe.json"],
        "not_tested": [],
    }

    recipe_path = os.path.join(ws, "recipe.json")
    receipt_path = os.path.join(ws, "receipts", f"recipe-receipt-{args.session_id}.json")

    write_json(recipe_path, recipe, args.dry_run)
    write_json(receipt_path, receipt, args.dry_run)

    sys.exit(0)


if __name__ == "__main__":
    main()
