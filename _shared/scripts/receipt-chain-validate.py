"""
receipt-chain-validate.py — Verify a session's receipt chain before Archive.

Scans .wabblespec/receipts/ for all receipts matching a session_id, checks
that required receipt types are present and all have status=PASS. Replaces
the manual read-each-receipt-and-check cycle that costs 2-5K tokens before
every Archive run.

Usage:
    # Validate a session chain (safe to archive = exit 0):
    python _shared/scripts/receipt-chain-validate.py --session-id seed-run-20260526xx

    # Check specific required types (override defaults):
    python _shared/scripts/receipt-chain-validate.py \\
        --session-id seed-run-20260526xx \\
        --require executor verifier

    # Emit JSON report:
    python _shared/scripts/receipt-chain-validate.py \\
        --session-id seed-run-20260526xx --json

    # Scan ALL sessions and report any with gaps or FAILs:
    python _shared/scripts/receipt-chain-validate.py --all

    # List receipts for a session without validating:
    python _shared/scripts/receipt-chain-validate.py --session-id xxx --list

Default required types for a standard seed run:
    executor, verifier
    (delivery is the Archive output — not checked here)

Full pipeline required types:
    recipe, specify, decompose, executor, verifier
    (use --require to override)

Exit codes:
    0  chain complete, all PASS — safe to run archive.py
    1  chain incomplete or has FAIL receipts — do not archive
    2  receipts directory not found
"""

import sys
import os
import json
import glob
import argparse
from datetime import datetime, timezone


# Default types checked for a seed-pipeline session.
# Override with --require for full-pipeline sessions.
DEFAULT_REQUIRED = ["executor", "verifier"]

FULL_PIPELINE_REQUIRED = ["recipe", "specify", "decompose", "executor", "verifier"]


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def find_receipts_dir(start_dir=None):
    if start_dir is None:
        start_dir = os.getcwd()
    candidate = start_dir
    for _ in range(10):
        path = os.path.join(candidate, ".wabblespec", "receipts")
        if os.path.isdir(path):
            return path
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def load_receipts(receipts_dir):
    """Load all JSON receipts. Returns list of (path, data) tuples."""
    results = []
    for path in sorted(glob.glob(os.path.join(receipts_dir, "*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            results.append((path, data))
        except (OSError, json.JSONDecodeError):
            continue
    return results


def get_session_ids(data):
    """Return set of all identifiers for this receipt (session_id + task_id)."""
    ids = set()
    for field in ("session_id", "task_id"):
        val = data.get(field)
        if val:
            ids.add(val)
    return ids


def get_session_id(data):
    """Primary display identifier — prefer session_id, fall back to task_id."""
    return data.get("session_id") or data.get("task_id") or ""


def get_receipt_type(data):
    rtype = data.get("receipt_type") or data.get("module") or ""
    # Normalize: "executor" / "verifier" / "recipe" / etc.
    return rtype.lower()


def receipts_for_session(all_receipts, session_id):
    """Match on session_id OR task_id — both are valid identifiers."""
    return [
        (path, data) for path, data in all_receipts
        if session_id in get_session_ids(data)
    ]


def all_session_ids(all_receipts):
    """Return unique identifiers across all receipts (prefer session_id)."""
    seen = set()
    ids = []
    for _, data in all_receipts:
        for sid in get_session_ids(data):
            if sid and sid not in seen:
                seen.add(sid)
                ids.append(sid)
    return ids


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def validate_session(session_id, receipts, required_types):
    """
    Returns a report dict:
    {
        session_id: str,
        receipts_found: [{type, path, status, timestamp}],
        required: [str],
        present: [str],
        missing: [str],
        failing: [{type, path, status, failure_reason}],
        chain_complete: bool,
        all_pass: bool,
        safe_to_archive: bool,
    }
    """
    found_by_type = {}
    found_list = []

    for path, data in receipts:
        rtype = get_receipt_type(data)
        status = data.get("status", "UNKNOWN")
        ts = (data.get("timestamp") or data.get("verified_at") or
              data.get("executed_at") or data.get("archived_at") or "")
        entry = {
            "type": rtype,
            "path": os.path.relpath(path).replace("\\", "/"),
            "status": status,
            "timestamp": ts,
        }
        if status in ("FAIL", "PARTIAL"):
            entry["failure_reason"] = data.get("failure_reason", "")
        found_list.append(entry)

        # For presence check, prefer PASS over FAIL when multiple exist
        if rtype not in found_by_type or status == "PASS":
            found_by_type[rtype] = entry

    present = [t for t in required_types if t in found_by_type]
    missing = [t for t in required_types if t not in found_by_type]
    failing = [
        entry for rtype, entry in found_by_type.items()
        if entry["status"] in ("FAIL", "PARTIAL")
    ]

    chain_complete = len(missing) == 0
    all_pass = len(failing) == 0
    safe = chain_complete and all_pass

    return {
        "session_id": session_id,
        "receipts_found": sorted(found_list, key=lambda x: x.get("timestamp", "")),
        "required": required_types,
        "present": present,
        "missing": missing,
        "failing": failing,
        "chain_complete": chain_complete,
        "all_pass": all_pass,
        "safe_to_archive": safe,
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

STATUS_ICON = {"PASS": "PASS", "FAIL": "FAIL", "PARTIAL": "PART", "UNKNOWN": "????"}


def print_report(report, verbose=False):
    sid = report["session_id"]
    safe = report["safe_to_archive"]
    verdict = "SAFE TO ARCHIVE" if safe else "NOT SAFE — fix before archive"
    print(f"\nSession: {sid}")
    print(f"Verdict: {verdict}")
    print()

    # Required chain status
    print("  Required types:")
    for rtype in report["required"]:
        found = next((e for e in report["receipts_found"] if e["type"] == rtype), None)
        if found:
            icon = STATUS_ICON.get(found["status"], "????")
            print(f"    {icon}  {rtype:<25} {found['path']}")
        else:
            print(f"    MISS  {rtype}")

    # Extra receipts found
    extra = [e for e in report["receipts_found"] if e["type"] not in report["required"]]
    if extra and verbose:
        print("\n  Additional receipts:")
        for e in extra:
            icon = STATUS_ICON.get(e["status"], "????")
            print(f"    {icon}  {e['type']:<25} {e['path']}")

    if report["missing"]:
        print(f"\n  Missing: {report['missing']}")

    if report["failing"]:
        print("\n  Failing receipts:")
        for e in report["failing"]:
            print(f"    FAIL  {e['type']} — {e.get('failure_reason', '(no reason)')}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate a session's receipt chain before running archive.py.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--session-id", metavar="ID",
                        help="Session to validate.")
    parser.add_argument("--require", nargs="+", metavar="TYPE",
                        help=f"Required receipt types. Default: {DEFAULT_REQUIRED}")
    parser.add_argument("--full-pipeline", action="store_true",
                        help=f"Require full pipeline types: {FULL_PIPELINE_REQUIRED}")
    parser.add_argument("--all", action="store_true",
                        help="Validate all sessions found in receipts dir.")
    parser.add_argument("--list", action="store_true",
                        help="List receipts for the session without validating.")
    parser.add_argument("--json", action="store_true", dest="emit_json",
                        help="Emit JSON report instead of human-readable output.")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--receipts-dir", metavar="PATH",
                        help="Explicit path to receipts directory.")

    args = parser.parse_args()

    if not args.session_id and not args.all:
        parser.error("--session-id or --all is required.")

    # Locate receipts dir
    rd = args.receipts_dir or find_receipts_dir()
    if rd is None or not os.path.isdir(rd):
        print("ERROR: Cannot find .wabblespec/receipts/. Run from inside the repo.",
              file=sys.stderr)
        sys.exit(2)

    all_receipts = load_receipts(rd)

    # Required types
    if args.require:
        required = args.require
    elif args.full_pipeline:
        required = FULL_PIPELINE_REQUIRED
    else:
        required = DEFAULT_REQUIRED

    # --list mode
    if args.list and args.session_id:
        session_receipts = receipts_for_session(all_receipts, args.session_id)
        if not session_receipts:
            print(f"No receipts found for session '{args.session_id}'")
            sys.exit(1)
        print(f"Receipts for session '{args.session_id}':")
        for path, data in session_receipts:
            rtype = get_receipt_type(data)
            status = data.get("status", "?")
            print(f"  {status:<5}  {rtype:<25} {os.path.basename(path)}")
        sys.exit(0)

    # --all mode
    if args.all:
        session_ids = all_session_ids(all_receipts)
        if not session_ids:
            print("No sessions found in receipts directory.")
            sys.exit(0)

        reports = []
        for sid in session_ids:
            receipts = receipts_for_session(all_receipts, sid)
            # Skip delivery-only sessions (Archive itself)
            non_delivery = [(p, d) for p, d in receipts
                           if get_receipt_type(d) not in ("delivery", "archive")]
            if not non_delivery:
                continue
            report = validate_session(sid, non_delivery, required)
            reports.append(report)

        if args.emit_json:
            print(json.dumps(reports, indent=2))
            sys.exit(0)

        unsafe = [r for r in reports if not r["safe_to_archive"]]
        safe_count = len(reports) - len(unsafe)
        print(f"Sessions scanned: {len(reports)}")
        print(f"Safe to archive:  {safe_count}")
        print(f"Need attention:   {len(unsafe)}")
        for r in unsafe:
            print_report(r, verbose=args.verbose)
        sys.exit(0 if not unsafe else 1)

    # Single session
    session_receipts = receipts_for_session(all_receipts, args.session_id)
    if not session_receipts:
        print(f"No receipts found for session '{args.session_id}'")
        print(f"Sessions with receipts: {all_session_ids(all_receipts)[:10]}")
        sys.exit(1)

    # Exclude delivery receipts from chain validation (they're the output)
    chain_receipts = [(p, d) for p, d in session_receipts
                      if get_receipt_type(d) not in ("delivery", "archive")]

    report = validate_session(args.session_id, chain_receipts, required)

    if args.emit_json:
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["safe_to_archive"] else 1)

    print_report(report, verbose=args.verbose)
    sys.exit(0 if report["safe_to_archive"] else 1)


if __name__ == "__main__":
    main()
