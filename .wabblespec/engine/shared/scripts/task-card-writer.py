"""
task-card-writer.py — Write a conforming task-card.md from CLI arguments.

Eliminates manual Markdown construction for Specify. Claude provides the
reasoning-dependent content (goal text, criteria prose); this script handles
structure, required fields, and Markdown serialization.

Usage:
    python .wabblespec/engine/shared/scripts/task-card-writer.py \\
        --session-id phase3-new-scripts-20260528 \\
        --goal "Three automation scripts and a guard chain check exist at engine/shared/scripts/." \\
        --target Library-Package \\
        --complexity Medium \\
        --delta-class ADDITIVE \\
        --locked-at 2026-05-28T13:00:00Z \\
        --non-goal "SKILL.md updates to call new scripts" \\
        --non-goal "DuckDB receipt store" \\
        --assumption "Phase 2 complete — script-delegation-contract.md exists" \\
        --assumption "Python 3.8+ stdlib only" \\
        --criterion "AC1|task-card-writer.py exists|task-card-writer.py is present|python .wabblespec/engine/shared/scripts/task-card-writer.py is invoked with --dry-run|command exits 0 and prints valid Markdown without writing files" \\
        --out .wabblespec/state/plans/task-card.md

    # Dry run — print without writing:
    python .wabblespec/engine/shared/scripts/task-card-writer.py ... --dry-run

Criterion format: "name|short_name|Given|When|Then" (pipe-delimited, 5 fields)
  name       = short label used as the ## heading (e.g., "AC1")
  short_name = human description (e.g., "task-card-writer.py exists")
  given      = precondition text
  when       = action text
  then       = expected observable outcome

Exit codes:
    0  success
    1  validation failure (missing required args, bad criterion format)
    2  output path not writable
"""

import sys
import os
import argparse
from datetime import datetime, timezone


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

REQUIRED_FIELDS = ("goal", "target", "complexity", "change_class", "locked_at")
VALID_COMPLEXITY = {"Low", "Medium", "High"}
VALID_CHANGE_CLASS = {"BREAKING", "ADDITIVE", "COSMETIC"}


def parse_criterion(raw):
    """Parse 'name|short_name|Given|When|Then' into dict. Raises ValueError on bad format."""
    parts = raw.split("|")
    if len(parts) != 5:
        raise ValueError(
            f"Criterion must have exactly 5 pipe-delimited fields "
            f"(name|short_name|Given|When|Then), got {len(parts)}: {raw!r}"
        )
    return {
        "name": parts[0].strip(),
        "short_name": parts[1].strip(),
        "given": parts[2].strip(),
        "when": parts[3].strip(),
        "then": parts[4].strip(),
    }


def render(args, criteria):
    """Render task-card.md content from parsed args and criteria list."""
    lines = [
        "# Task Card",
        "",
        f"**goal:** {args.goal}",
        f"**target:** {args.target}",
        f"**complexity:** {args.complexity}",
        f"**change_class:** {args.change_class}",
        f"**locked_at:** {args.locked_at}",
        f"**session_id:** {args.session_id}",
        "",
        "## Non-Goals",
        "",
    ]
    for ng in args.non_goal:
        lines.append(f"- {ng}")
    lines += ["", "## Assumptions", ""]
    for asm in args.assumption:
        lines.append(f"- {asm}")
    lines += ["", "## Acceptance Criteria", ""]
    for c in criteria:
        lines += [
            f"### {c['name']} — {c['short_name']}",
            "",
            f"Given {c['given']}",
            f"When {c['when']}",
            f"Then {c['then']}",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--goal", required=True, help="One sentence, falsifiable.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--complexity", required=True, choices=list(VALID_COMPLEXITY))
    parser.add_argument("--delta-class", required=True, choices=list(VALID_CHANGE_CLASS),
                        dest="change_class",
                        help="Delta/change classification (BREAKING/ADDITIVE/COSMETIC).")
    parser.add_argument("--locked-at", default=NOW, dest="locked_at")
    parser.add_argument("--non-goal", action="append", default=[], metavar="TEXT",
                        dest="non_goal", help="Repeatable. At least one required.")
    parser.add_argument("--assumption", action="append", default=[], metavar="TEXT",
                        help="Repeatable. At least one required.")
    parser.add_argument("--criterion", action="append", default=[], metavar="PIPE_FIELDS",
                        help="Repeatable. Format: name|short_name|Given|When|Then")
    parser.add_argument("--out", required=True, metavar="PATH",
                        help="Output path for task-card.md. Use '-' for stdout.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print output without writing.")
    args = parser.parse_args()

    errors = []
    if not args.non_goal:
        errors.append("At least one --non-goal is required.")
    if not args.assumption:
        errors.append("At least one --assumption is required.")
    if not args.criterion:
        errors.append("At least one --criterion is required.")

    criteria = []
    for raw in args.criterion:
        try:
            criteria.append(parse_criterion(raw))
        except ValueError as e:
            errors.append(str(e))

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    content = render(args, criteria)

    if args.dry_run or args.out == "-":
        print(content, end="")
        return

    out_path = args.out
    try:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"Wrote {out_path}")
    except OSError as e:
        print(f"ERROR: Cannot write to {out_path}: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
