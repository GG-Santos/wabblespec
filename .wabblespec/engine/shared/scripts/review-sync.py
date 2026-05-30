#!/usr/bin/env python3
"""review-sync.py — Cross-machine review queue reconciliation.

Runs at session start (after git pull). Reads the shared wave-queue entries
for wave-review jobs and for any pending entry that lacks a local pending file,
re-extracts the diff locally and prepares the review job.

Git is the transport — same channel as memories, receipts, and VERSION.
No separate SQLite. No separate sync mechanism.

What syncs via git (text, committed by sync-push.py):
    .wabblespec/state/queue/wave-queue.json     (shared job queue)
    .wabblespec/state/reviews/completed/        (completed review summaries)
    .wabblespec/state/receipts/wave-review-*    (receipts, in main chain)

What stays local (excluded by sync-push.py):
    .wabblespec/state/reviews/pending/          (machine-specific diff extractions)

Usage:
    python review-sync.py [--no-pull] [--verbose]

Exit codes: 0 success, 1 nothing to sync
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError("Not a git repository")
    return Path(r.stdout.strip())


def _pull(root: Path, verbose: bool) -> bool:
    r = subprocess.run(
        ["git", "pull", "--rebase", "--autostash"],
        capture_output=True, text=True, check=False,
        cwd=str(root), timeout=30,
    )
    if verbose:
        print(f"[review-sync] pull: {(r.stdout + r.stderr).strip()[:120]}")
    return r.returncode == 0


def _read_queue(root: Path) -> list[dict]:
    q = root / ".wabblespec" / "state" / "queue" / "wave-queue.json"
    if not q.exists():
        return []
    try:
        data = json.loads(q.read_text(encoding="utf-8"))
        return [t for t in data.get("tasks", [])
                if t.get("label", "").startswith("wave-review")]
    except Exception:
        return []


def _pending_refs(root: Path) -> set[str]:
    d = root / ".wabblespec" / "state" / "reviews" / "pending"
    if not d.exists():
        return set()
    refs: set[str] = set()
    for p in d.glob("*.json"):
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            r = j.get("resolved_ref") or j.get("ref")
            if r:
                refs.add(r)
        except Exception:
            pass
    return refs


def _ref_exists(ref: str, root: Path) -> bool:
    r = subprocess.run(["git", "cat-file", "-t", ref],
                       capture_output=True, text=True, check=False,
                       cwd=str(root), timeout=10)
    return r.returncode == 0


def _prep(root: Path, ref: str, review_type: str, verbose: bool, dry_run: bool) -> bool:
    wrev = root / ".wabblespec" / "engine" / "shared" / "scripts" / "wave-review.py"
    if not wrev.exists():
        return False
    if dry_run:
        print(f"[review-sync] DRY RUN: would prep {ref} ({review_type})")
        return True
    r = subprocess.run(
        [sys.executable, str(wrev), "--ref", ref, "--type", review_type],
        capture_output=True, text=True, check=False,
        cwd=str(root), timeout=60,
    )
    if verbose or r.returncode not in (0, 1):
        print(f"[review-sync] prep {ref}: {(r.stdout + r.stderr).strip()[:120]}")
    return r.returncode in (0, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-machine review queue reconciliation")
    parser.add_argument("--no-pull",  action="store_true")
    parser.add_argument("--verbose",  action="store_true")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"[review-sync] {exc}", file=sys.stderr)
        return 2

    if not args.no_pull:
        _pull(root, args.verbose)

    tasks   = _read_queue(root)
    pending = _pending_refs(root)

    new_preps = skipped = already = 0

    for t in tasks:
        ref   = t.get("label", "").replace("wave-review:", "")
        rtype = "standard"
        pp    = t.get("pending_path", "")

        if t.get("status") in ("PASS", "FAIL"):
            already += 1
            if args.verbose:
                print(f"[review-sync] {ref}: already reviewed ({t['status']})")
            continue

        if ref in pending:
            if args.verbose:
                print(f"[review-sync] {ref}: local pending file exists")
            continue

        if not _ref_exists(ref, root):
            print(f"[review-sync] {ref}: not in local git — fetch first")
            skipped += 1
            continue

        if args.verbose:
            print(f"[review-sync] {ref}: prepping from remote queue")
        if _prep(root, ref, rtype, args.verbose, args.dry_run):
            new_preps += 1
        else:
            skipped += 1

    if new_preps or skipped:
        print(f"[review-sync] {new_preps} new preps, {already} already done, {skipped} skipped")
    return 0 if new_preps > 0 or already > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
