#!/usr/bin/env python3
"""review-queue.py — WabbleSpec wave review job queue.

File-locked queue for tracking code review jobs. Each entry tracks a git ref,
review type, status, verdict, and receipt path.

Usage:
    python review-queue.py enqueue HEAD [--type standard|security|design]
    python review-queue.py list [--open] [--format json]
    python review-queue.py status <ref>
    python review-queue.py clear --reviewed
    python review-queue.py stats

Exit codes: 0 = success, 1 = error
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root() -> Path:
    import subprocess
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError("Not a git repository")
    return Path(r.stdout.strip())


def _queue_path(root: Path) -> Path:
    return root / ".wabblespec" / "state" / "reviews" / "queue.json"


def _read(root: Path) -> list[dict]:
    q = _queue_path(root)
    if not q.exists():
        return []
    try:
        return json.loads(q.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write(root: Path, items: list[dict]) -> None:
    q = _queue_path(root)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps(items, indent=2), encoding="utf-8")


def cmd_enqueue(args, root: Path) -> int:
    items = _read(root)
    existing = next((i for i in items if i["ref"] == args.ref), None)
    if existing and existing.get("status") == "pending":
        print(f"Already queued: {args.ref} ({existing['review_type']})")
        return 0
    items.append({
        "ref": args.ref,
        "review_type": args.type,
        "queued_at": NOW,
        "status": "pending",
        "verdict": None,
        "receipt_path": None,
    })
    _write(root, items)
    print(f"Enqueued: {args.ref} ({args.type})")
    return 0


def cmd_list(args, root: Path) -> int:
    items = _read(root)
    if args.open:
        items = [i for i in items if i.get("status") == "pending"]
    if not items:
        print("No reviews" + (" pending" if args.open else ""))
        return 0
    if args.format == "json":
        print(json.dumps(items, indent=2))
        return 0
    for i in items:
        verdict = i.get("verdict") or "-"
        print(f"  {i['status']:10s}  {i['ref']:20s}  {i['review_type']:10s}  verdict={verdict}  {i.get('queued_at','')}")
    return 0


def cmd_status(args, root: Path) -> int:
    items = _read(root)
    match = next((i for i in items if i["ref"] == args.ref), None)
    if not match:
        print(f"Not found: {args.ref}")
        return 1
    print(json.dumps(match, indent=2))
    return 0


def cmd_clear(args, root: Path) -> int:
    items = _read(root)
    if args.reviewed:
        before = len(items)
        items = [i for i in items if i.get("status") != "reviewed"]
        removed = before - len(items)
        _write(root, items)
        print(f"Cleared {removed} reviewed entries. {len(items)} remaining.")
    elif args.all:
        _write(root, [])
        print("Queue cleared.")
    return 0


def cmd_stats(args, root: Path) -> int:
    items = _read(root)
    total = len(items)
    pending = sum(1 for i in items if i.get("status") == "pending")
    reviewed = sum(1 for i in items if i.get("status") == "reviewed")
    passed = sum(1 for i in items if i.get("verdict") == "PASS")
    failed = sum(1 for i in items if i.get("verdict") == "FAIL")
    print(f"Total: {total}  Pending: {pending}  Reviewed: {reviewed}  Pass: {passed}  Fail: {failed}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="WabbleSpec review queue")
    sub = parser.add_subparsers(dest="cmd")

    p_enq = sub.add_parser("enqueue", help="Add a ref to the review queue")
    p_enq.add_argument("ref", help="Git ref to review")
    p_enq.add_argument("--type", default="standard",
                       choices=["standard", "security", "design"])

    p_list = sub.add_parser("list", help="List queued reviews")
    p_list.add_argument("--open", action="store_true", help="Pending only")
    p_list.add_argument("--format", default="table", choices=["table", "json"])

    p_status = sub.add_parser("status", help="Show status for a ref")
    p_status.add_argument("ref")

    p_clear = sub.add_parser("clear", help="Remove entries from queue")
    p_clear.add_argument("--reviewed", action="store_true", help="Remove reviewed entries")
    p_clear.add_argument("--all", action="store_true", help="Remove all entries")

    sub.add_parser("stats", help="Show queue statistics")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 1

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    dispatch = {
        "enqueue": cmd_enqueue,
        "list": cmd_list,
        "status": cmd_status,
        "clear": cmd_clear,
        "stats": cmd_stats,
    }
    return dispatch[args.cmd](args, root)


if __name__ == "__main__":
    raise SystemExit(main())
