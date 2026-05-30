"""
research-artifact-writer.py — Per-wave internal reference capture.

Records which existing code files were studied during a wave's research phase:
file path, why it is relevant, and what patterns were extracted. Future waves
on the same task can load this artifact instead of re-exploring the codebase.

Usage:
    python research-artifact-writer.py \\
        --wave 1 --session-id my-session \\
        --file src/foo.py --relevance "contains the auth flow" --patterns "JWT decode, expiry check" \\
        --file src/bar.py --relevance "shared config model" --patterns "BaseSettings, env prefix"

    # Append to existing artifact:
    python research-artifact-writer.py --wave 1 --session-id my-session --append \\
        --file src/baz.py --relevance "rate limit middleware" --patterns "sliding window counter"

    # List recorded entries for a wave:
    python research-artifact-writer.py --wave 1 --session-id my-session --list

Exit codes:
    0  success
    1  error
"""

import sys
import os
import json
import argparse
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


def artifact_path(ws, session_id, wave):
    return os.path.join(ws, "state", "plans", f"references-wave-{wave}-{session_id}.json")


def load_artifact(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"entries": [], "created": now_iso(), "last_updated": now_iso()}


def save_artifact(path, data, dry_run):
    data["last_updated"] = now_iso()
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
    print(f"Wrote {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Record codebase files studied during a wave's research phase.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--wave", required=True, metavar="N", help="Wave number (e.g. 1).")
    parser.add_argument("--session-id", required=True, metavar="ID")
    parser.add_argument("--file", action="append", default=[], dest="files", metavar="PATH",
                        help="Path to a studied file (repeatable, paired with --relevance and --patterns).")
    parser.add_argument("--relevance", action="append", default=[], metavar="TEXT",
                        help="Why this file is relevant (one per --file).")
    parser.add_argument("--patterns", action="append", default=[], metavar="TEXT",
                        help="Key patterns extracted (one per --file).")
    parser.add_argument("--append", action="store_true",
                        help="Append to existing artifact rather than replacing.")
    parser.add_argument("--list", action="store_true",
                        help="Print existing entries and exit.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wabblespec-dir", metavar="PATH")
    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
        sys.exit(1)

    path = artifact_path(ws, args.session_id, args.wave)
    data = load_artifact(path) if (args.append or args.list) else {"entries": [], "created": now_iso()}

    if args.list:
        print(json.dumps(data, indent=2))
        sys.exit(0)

    if not args.files:
        print("ERROR: at least one --file is required (unless --list).", file=sys.stderr)
        sys.exit(1)

    # Pair files with relevance and patterns (allow shorter lists -- pad with empty strings)
    new_entries = []
    for i, filepath in enumerate(args.files):
        relevance = args.relevance[i] if i < len(args.relevance) else ""
        patterns = args.patterns[i] if i < len(args.patterns) else ""
        new_entries.append({
            "file": filepath,
            "relevance": relevance,
            "key_patterns": patterns,
            "recorded_at": now_iso(),
        })

    data.setdefault("entries", [])
    data["entries"].extend(new_entries)
    data["session_id"] = args.session_id
    data["wave"] = args.wave

    save_artifact(path, data, args.dry_run)
    print(f"Recorded {len(new_entries)} reference(s). Total: {len(data['entries'])}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
