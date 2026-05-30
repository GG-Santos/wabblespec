"""
notebook-writer.py — Per-session plan knowledge notebook.

Creates and manages per-session notepads at state/notepads/<session-id>/.
Each notepad contains timestamped entries in four categories:
learnings, decisions, issues, problems.

Usage:
    # Write a learning:
    python notebook-writer.py --session-id my-session --write learnings \\
        "Executor SKILL.md Step 3b is at line 130 -- verified by grep"

    # Write a decision:
    python notebook-writer.py --session-id my-session --write decisions \\
        "Chose additive over rewrite to avoid breaking receipt chain"

    # List all entries for a session:
    python notebook-writer.py --session-id my-session --list

    # List a specific category:
    python notebook-writer.py --session-id my-session --list learnings

Exit codes:
    0  success
    1  error
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone

CATEGORIES = ["learnings", "decisions", "issues", "problems"]


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


def notebook_dir(ws, session_id):
    return os.path.join(ws, "state", "notepads", session_id)


def category_path(ws, session_id, category):
    return os.path.join(notebook_dir(ws, session_id), f"{category}.json")


def load_category(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"entries": []}


def save_category(path, data, dry_run):
    if dry_run:
        print(f"[dry-run] would write {path}")
        print(json.dumps(data, indent=2))
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(
        description="Per-session plan knowledge notebook.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--session-id", required=True, metavar="ID")
    parser.add_argument("--write", nargs=2, metavar=("CATEGORY", "TEXT"),
                        help=f"Write an entry. Category: {', '.join(CATEGORIES)}.")
    parser.add_argument("--list", nargs="?", const="all", metavar="CATEGORY",
                        help="List entries. Omit CATEGORY to list all.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wabblespec-dir", metavar="PATH")
    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
        sys.exit(1)

    if args.write:
        category, text = args.write
        if category not in CATEGORIES:
            print(f"ERROR: category must be one of: {', '.join(CATEGORIES)}", file=sys.stderr)
            sys.exit(1)
        path = category_path(ws, args.session_id, category)
        data = load_category(path)
        data["entries"].append({
            "text": text,
            "timestamp": now_iso(),
        })
        save_category(path, data, args.dry_run)
        print(f"Wrote {category} entry ({len(data['entries'])} total).")

    elif args.list:
        if args.list == "all":
            cats = CATEGORIES
        else:
            if args.list not in CATEGORIES:
                print(f"ERROR: category must be one of: {', '.join(CATEGORIES)}", file=sys.stderr)
                sys.exit(1)
            cats = [args.list]

        for cat in cats:
            path = category_path(ws, args.session_id, cat)
            data = load_category(path)
            entries = data.get("entries", [])
            if entries:
                print(f"\n## {cat.capitalize()} ({len(entries)})")
                for e in entries:
                    print(f"  [{e.get('timestamp', '?')}] {e.get('text', '')}")
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
