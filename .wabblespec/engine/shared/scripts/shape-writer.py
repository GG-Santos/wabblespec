"""
shape-writer.py — Write state/plans/shape.md from locked scope and task card.

shape.md captures the non-obvious decisions made during task scoping:
what was considered, what was rejected, what constraints forced the choices.
It is a planning reference artifact, not a receipt.

Usage:
    python shape-writer.py [--session-id ID] [--scope-file PATH] [--task-card PATH]
                           [--decision TEXT] [--standard TEXT] [--dry-run]

    # Typical invocation after Specify locks scope:
    python shape-writer.py --session-id my-session-20260530

    # Add a decision note:
    python shape-writer.py --session-id my-session-20260530 \
        --decision "Chose additive over rewrite: avoids breaking receipt chain"

Exit codes:
    0  success
    1  error
"""

import sys
import os
import json
import argparse
import re
from datetime import datetime, timezone


def find_wabblespec(start=None):
    cwd = start or os.getcwd()
    for _ in range(10):
        ws = os.path.join(cwd, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return None


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def extract_section(content, heading):
    """Extract bullet items under a markdown ## heading."""
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    items = [line.lstrip("- ").strip() for line in block.splitlines() if line.strip().startswith("-")]
    return items


def extract_field(content, field):
    """Extract a frontmatter-style **field:** value."""
    match = re.search(rf"^\*\*{re.escape(field)}:\*\*\s*(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def main():
    parser = argparse.ArgumentParser(
        description="Write state/plans/shape.md from locked scope and task card.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--session-id", metavar="ID", default="unknown")
    parser.add_argument("--scope-file", metavar="PATH",
                        help="Path to scope.md (auto-discovered if omitted).")
    parser.add_argument("--task-card", metavar="PATH",
                        help="Path to task-card.md (auto-discovered if omitted).")
    parser.add_argument("--decision", action="append", default=[], metavar="TEXT",
                        help="Add a decision note (repeatable).")
    parser.add_argument("--standard", action="append", default=[], metavar="TEXT",
                        help="Add a standard applied note (repeatable).")
    parser.add_argument("--out", metavar="PATH",
                        help="Output path (default: state/plans/shape.md).")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wabblespec-dir", metavar="PATH")
    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
        sys.exit(1)

    scope_path = args.scope_file or os.path.join(ws, "state", "scope.md")
    task_path = args.task_card or os.path.join(ws, "state", "plans", "task-card.md")
    out_path = args.out or os.path.join(ws, "state", "plans", "shape.md")

    scope_content = read_text(scope_path) or ""
    task_content = read_text(task_path) or ""

    # Extract scope summary from scope.md
    goal = extract_field(task_content, "goal") or "Goal not found in task card."
    target = extract_field(scope_content, "target") or extract_field(task_content, "target") or "unknown"
    complexity = extract_field(scope_content, "complexity") or extract_field(task_content, "complexity") or "unknown"

    in_scope_items = extract_section(scope_content, "In Scope")
    out_of_scope_items = extract_section(scope_content, "Out of Scope")
    assumption_items = extract_section(scope_content, "Assumptions")

    # Decisions: from --decision flags + non-goal reasoning
    decisions = list(args.decision)
    # Add non-goals as implied decisions
    non_goals = extract_section(task_content, "Non-Goals")
    for ng in non_goals:
        decisions.append(f"Excluded: {ng}")

    # Standards applied: from --standard flags + assumption lines with 'Standard' keyword
    standards = list(args.standard)
    for a in assumption_items:
        if "standard" in a.lower() or "convention" in a.lower() or "invariant" in a.lower():
            standards.append(a)

    # Build shape.md content
    lines = [
        "# Shape",
        "",
        f"**session_id:** {args.session_id}",
        f"**locked_at:** {now_iso()}",
        "",
        "## Scope",
        "",
        f"**Goal:** {goal}",
        f"**Target:** {target}  **Complexity:** {complexity}",
        "",
        "**In scope:**",
    ]
    for item in in_scope_items:
        lines.append(f"- {item}")
    if not in_scope_items:
        lines.append("- (see scope.md)")

    lines += ["", "**Out of scope:**"]
    for item in out_of_scope_items:
        lines.append(f"- {item}")
    if not out_of_scope_items:
        lines.append("- (see scope.md)")

    lines += ["", "## Decisions", ""]
    if decisions:
        for d in decisions:
            lines.append(f"- {d}")
    else:
        lines.append("- No explicit decision notes recorded. Decisions implicit in scope.md non-goals.")

    lines += ["", "## Standards Applied", ""]
    if standards:
        for s in standards:
            lines.append(f"- {s}")
    else:
        lines.append("- No explicit standards cited. See scope.md Assumptions for discovered constraints.")

    content = "\n".join(lines) + "\n"

    if args.dry_run:
        print(f"[dry-run] would write {out_path}")
        print(content)
        sys.exit(0)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, out_path)
    print(f"Wrote {out_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
