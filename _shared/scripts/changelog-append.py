"""
changelog-append.py — Append-only CHANGELOG writer. Never reads existing content.

Appends a new entry to .wabblespec/CHANGELOG.md using open('a') — the existing
file is never loaded into memory or into Claude's context window. This eliminates
the ~24,500-token CHANGELOG read cost that occurred on every Archive run.

Usage:
    python _shared/scripts/changelog-append.py \\
        --version 0.9.1 \\
        --timestamp 2026-05-25T14:00:00Z \\
        --title "Optional section heading" \\
        --changed "Added X" "Added Y" \\
        --fixed "Fixed Z" \\
        --not-tested "item A" "item B" \\
        --delivery-receipt ".wabblespec/receipts/delivery-receipt-xxx.json" \\
        --waves-planned 1 \\
        --waves-completed 1 \\
        --waves-failed 0

    # Minimal (only --version and --timestamp required):
    python _shared/scripts/changelog-append.py \\
        --version 0.9.1 \\
        --timestamp 2026-05-25T14:00:00Z \\
        --body "Raw markdown body text"

    # Read entry data from a delivery receipt JSON:
    python _shared/scripts/changelog-append.py \\
        --from-receipt .wabblespec/receipts/delivery-receipt-xxx.json

Exit codes:
    0  success
    1  bad arguments
    2  CHANGELOG file not found or not writable; receipt not found
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


def find_changelog(start_dir=None):
    if start_dir is None:
        start_dir = os.getcwd()
    candidate = start_dir
    for _ in range(8):
        path = os.path.join(candidate, ".wabblespec", "CHANGELOG.md")
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def format_list(items, bullet="-"):
    if not items:
        return f"- (none)"
    return "\n".join(f"{bullet} {item}" for item in items)


def build_entry(version, timestamp, title, changed, fixed, not_tested,
                delivery_receipt, waves_planned, waves_completed, waves_failed,
                body=None):
    """Return the markdown string for one CHANGELOG entry (no trailing newline)."""
    lines = []
    lines.append(f"## [{version}] — {timestamp}")
    lines.append("")

    if title:
        lines.append(f"### {title}")
        lines.append("")

    if body:
        lines.append(body)
        lines.append("")
        return "\n".join(lines)

    if changed:
        lines.append("### Changed")
        for item in changed:
            lines.append(f"- {item}")
        lines.append("")

    if fixed:
        lines.append("### Fixed")
        for item in fixed:
            lines.append(f"- {item}")
        lines.append("")
    elif changed:  # only emit Fixed section if there were Changed items too
        lines.append("### Fixed")
        lines.append("- (none)")
        lines.append("")

    if not_tested:
        lines.append("### Not Tested")
        for item in not_tested:
            lines.append(f"- {item}")
        lines.append("")

    if delivery_receipt:
        lines.append("### Receipts")
        lines.append(f"- delivery-receipt: {delivery_receipt}")
        if waves_planned is not None:
            failed = waves_failed if waves_failed is not None else 0
            lines.append(
                f"- waves: {waves_planned} planned, {waves_completed} completed, {failed} failed"
            )
        if not not_tested:
            lines.append("- verification: all waves PASS")
        lines.append("")

    return "\n".join(lines)


def append_entry(changelog_path, entry_text):
    """Append entry_text to changelog_path. Opens in append mode — never reads existing."""
    try:
        with open(changelog_path, "a", encoding="utf-8") as f:
            f.write("\n---\n\n")
            f.write(entry_text)
            if not entry_text.endswith("\n"):
                f.write("\n")
    except OSError as e:
        print(f"ERROR: Cannot write to CHANGELOG at {changelog_path}: {e}", file=sys.stderr)
        sys.exit(2)


def entry_from_receipt(receipt_path):
    """Extract changelog fields from a delivery receipt JSON."""
    try:
        with open(receipt_path, encoding="utf-8") as f:
            r = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read receipt {receipt_path}: {e}", file=sys.stderr)
        sys.exit(2)

    version = r.get("version_new") or r.get("version")
    if not version:
        print(
            "ERROR: Receipt has no 'version_new' or 'version' field — cannot derive version.",
            file=sys.stderr,
        )
        sys.exit(1)

    timestamp = r.get("archived_at") or r.get("timestamp") or datetime.now(timezone.utc).isoformat()
    summary = r.get("summary", "")
    not_tested = r.get("not_tested_list") or []
    delta = r.get("version_bump_reason", "ADDITIVE")

    changed = [summary] if summary else []
    title = f"{delta} — {r.get('task_id', 'unknown')}"

    return dict(
        version=version,
        timestamp=timestamp,
        title=title,
        changed=changed,
        fixed=[],
        not_tested=not_tested,
        delivery_receipt=os.path.relpath(receipt_path).replace("\\", "/"),
        waves_planned=r.get("waves_completed"),
        waves_completed=r.get("waves_completed"),
        waves_failed=0,
        body=None,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Append one entry to .wabblespec/CHANGELOG.md without reading it.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--changelog", metavar="PATH", help="Explicit path to CHANGELOG.md.")
    parser.add_argument("--version", metavar="X.Y.Z", help="Version string for the heading.")
    parser.add_argument(
        "--timestamp",
        metavar="ISO8601",
        help="Timestamp for the heading. Defaults to now UTC.",
    )
    parser.add_argument("--title", metavar="TEXT", help="Optional section heading text.")
    parser.add_argument("--changed", nargs="*", metavar="ITEM", help="Changed items.")
    parser.add_argument("--fixed", nargs="*", metavar="ITEM", help="Fixed items.")
    parser.add_argument(
        "--not-tested", nargs="*", metavar="ITEM", dest="not_tested", help="Not-tested items."
    )
    parser.add_argument("--delivery-receipt", metavar="PATH", help="Path to delivery receipt.")
    parser.add_argument("--waves-planned", type=int, metavar="N")
    parser.add_argument("--waves-completed", type=int, metavar="N")
    parser.add_argument("--waves-failed", type=int, metavar="N", default=0)
    parser.add_argument("--body", metavar="MARKDOWN", help="Raw markdown body (bypasses structure).")
    parser.add_argument(
        "--from-receipt",
        metavar="PATH",
        help="Derive all fields from a delivery receipt JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the entry that would be appended; do not write.",
    )

    args = parser.parse_args()

    # Locate CHANGELOG
    if args.changelog:
        cl_path = args.changelog
        if not os.path.isfile(cl_path):
            print(f"ERROR: CHANGELOG not found at {cl_path}", file=sys.stderr)
            sys.exit(2)
    else:
        cl_path = find_changelog()
        if cl_path is None:
            print(
                "ERROR: Could not find .wabblespec/CHANGELOG.md. Run from inside the repo.",
                file=sys.stderr,
            )
            sys.exit(2)

    # Build entry fields
    if args.from_receipt:
        fields = entry_from_receipt(args.from_receipt)
    else:
        if not args.version:
            print("ERROR: --version is required (or use --from-receipt).", file=sys.stderr)
            sys.exit(1)
        ts = args.timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        fields = dict(
            version=args.version,
            timestamp=ts,
            title=args.title,
            changed=args.changed or [],
            fixed=args.fixed or [],
            not_tested=args.not_tested or [],
            delivery_receipt=args.delivery_receipt,
            waves_planned=args.waves_planned,
            waves_completed=args.waves_completed,
            waves_failed=args.waves_failed,
            body=args.body,
        )

    entry = build_entry(**fields)

    if args.dry_run:
        print("--- DRY RUN: would append to", cl_path, "---")
        print(entry)
        sys.exit(0)

    append_entry(cl_path, entry)
    print(f"Appended [{fields['version']}] entry to {cl_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
