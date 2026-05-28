"""
scope-writer.py — Write a conforming scope.md from CLI arguments.

Eliminates manual Markdown construction for ScopeFrame. Claude provides the
reasoning-dependent content (scope item text, assumptions); this script handles
structure, required fields, and Markdown serialization.

Usage:
    python .wabblespec/engine/shared/scripts/scope-writer.py \\
        --session-id phase3-new-scripts-20260528 \\
        --target Library-Package \\
        --complexity Medium \\
        --locked-at 2026-05-28T13:00:00Z \\
        --in-scope "Build task-card-writer.py" \\
        --in-scope "Build wave-plan-writer.py" \\
        --out-of-scope "SKILL.md updates to call new scripts" \\
        --assumption "Phase 2 complete — script-delegation-contract.md exists" \\
        --out .wabblespec/state/scope.md

    # Dry run:
    python .wabblespec/engine/shared/scripts/scope-writer.py ... --dry-run

Exit codes:
    0  success
    1  validation failure (missing required items)
    2  output path not writable
"""

import sys
import os
import argparse
from datetime import datetime, timezone


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
VALID_COMPLEXITY = {"Low", "Medium", "High"}


def render(args):
    lines = [
        "# Session Scope",
        "",
        f"**target:** {args.target}",
        f"**complexity:** {args.complexity}",
        f"**locked_at:** {args.locked_at}",
        f"**session_id:** {args.session_id}",
        "",
        "## In Scope",
        "",
    ]
    for item in args.in_scope:
        lines.append(f"- {item}")
    lines += ["", "## Out of Scope", ""]
    for item in args.out_of_scope:
        lines.append(f"- {item}")
    lines += ["", "## Assumptions", ""]
    for item in args.assumption:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Scope Change Log",
        "",
        "| timestamp | change | triggered_by |",
        "|---|---|---|",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--complexity", required=True, choices=list(VALID_COMPLEXITY))
    parser.add_argument("--locked-at", default=NOW, dest="locked_at")
    parser.add_argument("--in-scope", action="append", default=[], metavar="TEXT",
                        dest="in_scope", help="Repeatable. At least one required.")
    parser.add_argument("--out-of-scope", action="append", default=[], metavar="TEXT",
                        dest="out_of_scope", help="Repeatable. At least one required.")
    parser.add_argument("--assumption", action="append", default=[], metavar="TEXT",
                        help="Repeatable. At least one required.")
    parser.add_argument("--out", required=True, metavar="PATH")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    errors = []
    if not args.in_scope:
        errors.append("At least one --in-scope is required.")
    if not args.out_of_scope:
        errors.append("At least one --out-of-scope is required.")
    if not args.assumption:
        errors.append("At least one --assumption is required.")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    content = render(args)

    if args.dry_run or args.out == "-":
        print(content, end="")
        return

    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"Wrote {args.out}")
    except OSError as e:
        print(f"ERROR: Cannot write to {args.out}: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
