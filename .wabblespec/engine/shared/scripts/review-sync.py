#!/usr/bin/env python3
"""review-sync.py — Cross-machine review queue reconciliation.

Runs at session start. Reads the shared queue.json (which arrives via git
pull from other machines) and for any pending entry that lacks a local
pending file, re-extracts the diff locally and writes the prep file so the
daemon can process it.

The git transport is the same channel that syncs memories, receipts, and
VERSION across machines — no extra infrastructure needed.

Sync design:
    Synced via git (text):   state/reviews/queue.json
                             state/reviews/completed/
    Local-only (excluded):   state/reviews/pending/       (machine-specific diffs)
                             state/reviews/daemon/         (PID, log)
                             state/reviews/reviews.db      (SQLite binary)

Flow:
    Machine A commits → git push (sync-push.py, on stop)
    Machine B git pull → gets queue.json with entries from A
    Machine B session start → review-sync.py reconciles
        → any pending entry without a local pending file:
            → wave-review.py --ref <ref> (re-extracts diff locally)
        → any pending entry already reviewed on A (via completed/):
            → mark as reviewed in local DB so daemon skips it

Usage:
    python review-sync.py [--dry-run] [--verbose]

Exit codes: 0 success, 1 nothing to sync, 2 error
"""
from __future__ import annotations

import argparse
import json
import sqlite3
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
    """git pull --rebase (silent-fail). Returns True if pull succeeded."""
    r = subprocess.run(
        ["git", "pull", "--rebase", "--autostash"],
        capture_output=True, text=True, check=False,
        cwd=str(root), timeout=30,
    )
    if verbose:
        print(f"[review-sync] pull: {r.stdout.strip() or r.stderr.strip()}")
    return r.returncode == 0


def _read_queue(root: Path) -> list[dict]:
    q = root / ".wabblespec" / "state" / "reviews" / "queue.json"
    if not q.exists():
        return []
    try:
        return json.loads(q.read_text(encoding="utf-8"))
    except Exception:
        return []


def _completed_refs(root: Path) -> set[str]:
    """Set of refs that have a completed review on this machine (local DB or completed/)."""
    refs: set[str] = set()

    # From completed/ directory (synced text receipts from other machines)
    completed_dir = root / ".wabblespec" / "state" / "reviews" / "completed"
    if completed_dir.exists():
        for p in completed_dir.glob("*.json"):
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
                ref = j.get("resolved_ref") or j.get("ref")
                if ref:
                    refs.add(ref)
            except Exception:
                pass

    # From local SQLite DB
    db = root / ".wabblespec" / "state" / "reviews" / "reviews.db"
    if db.exists():
        try:
            con = sqlite3.connect(str(db), timeout=5)
            rows = con.execute(
                "SELECT ref FROM reviews WHERE status='reviewed'"
            ).fetchall()
            con.close()
            refs.update(r[0] for r in rows)
        except Exception:
            pass

    return refs


def _pending_refs(root: Path) -> set[str]:
    """Set of refs that already have a local pending file."""
    pending_dir = root / ".wabblespec" / "state" / "reviews" / "pending"
    if not pending_dir.exists():
        return set()
    refs: set[str] = set()
    for p in pending_dir.glob("*.json"):
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            ref = j.get("resolved_ref") or j.get("ref")
            if ref:
                refs.add(ref)
        except Exception:
            pass
    return refs


def _ref_exists_locally(ref: str, root: Path) -> bool:
    """Check if this git ref exists in the local repo (may need to fetch first)."""
    r = subprocess.run(
        ["git", "cat-file", "-t", ref],
        capture_output=True, text=True, check=False,
        cwd=str(root), timeout=10,
    )
    return r.returncode == 0


def _prep_review(root: Path, ref: str, review_type: str,
                 dry_run: bool, verbose: bool) -> bool:
    """Run wave-review.py --ref <ref> to create a local pending file."""
    wrev = root / ".wabblespec" / "engine" / "shared" / "scripts" / "wave-review.py"
    if not wrev.exists():
        print(f"[review-sync] wave-review.py not found", file=sys.stderr)
        return False

    if dry_run:
        print(f"[review-sync] DRY RUN: would prep review for {ref} ({review_type})")
        return True

    r = subprocess.run(
        [sys.executable, str(wrev),
         "--ref", ref,
         "--type", review_type],
        capture_output=True, text=True, check=False,
        cwd=str(root), timeout=60,
    )
    if verbose or r.returncode != 0:
        print(f"[review-sync] prep {ref}: {r.stdout.strip() or r.stderr.strip()}")
    return r.returncode in (0, 1)  # 1 = no diff (OK — nothing to review)


def _mark_db_reviewed(root: Path, ref: str, verdict: str) -> None:
    """Mark a ref as reviewed in the local DB (imported from another machine)."""
    db = root / ".wabblespec" / "state" / "reviews" / "reviews.db"
    if not db.exists():
        return
    try:
        con = sqlite3.connect(str(db), timeout=5)
        con.execute("PRAGMA journal_mode=WAL")
        existing = con.execute("SELECT id FROM reviews WHERE ref=?", (ref,)).fetchone()
        if existing:
            con.execute(
                "UPDATE reviews SET status='reviewed', verdict=? WHERE ref=?",
                (verdict, ref)
            )
        else:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            con.execute(
                """INSERT INTO reviews (ref, queued_at, status, verdict)
                   VALUES (?,?,?,?)""",
                (ref, now, "reviewed", verdict)
            )
        con.commit()
        con.close()
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile review queue across machines via git"
    )
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--verbose",  action="store_true")
    parser.add_argument("--no-pull",  action="store_true",
                        help="Skip git pull (use when pull already happened)")
    args = parser.parse_args()

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"[review-sync] ERROR: {exc}", file=sys.stderr)
        return 2

    # Step 1: pull latest from remote
    if not args.no_pull:
        ok = _pull(root, args.verbose)
        if not ok and args.verbose:
            print("[review-sync] pull failed or no remote — continuing with local state")

    # Step 2: read the shared queue
    queue = _read_queue(root)
    if not queue:
        if args.verbose:
            print("[review-sync] queue empty — nothing to reconcile")
        return 1

    completed = _completed_refs(root)
    pending   = _pending_refs(root)

    new_preps, already_done, skipped = 0, 0, 0

    for entry in queue:
        ref         = entry.get("resolved_ref") or entry.get("ref", "")
        review_type = entry.get("review_type", "standard")
        status      = entry.get("status", "pending")

        if not ref:
            continue

        if status == "reviewed" or ref in completed:
            # Already reviewed on some machine — import verdict to local DB
            verdict = entry.get("verdict") or "UNKNOWN"
            _mark_db_reviewed(root, ref, verdict)
            already_done += 1
            if args.verbose:
                print(f"[review-sync] {ref}: already reviewed ({verdict}) — imported to local DB")
            continue

        if ref in pending:
            if args.verbose:
                print(f"[review-sync] {ref}: local pending file exists — daemon will process")
            continue

        # Pending on another machine, not yet locally prepped
        if not _ref_exists_locally(ref, root):
            print(f"[review-sync] {ref}: ref not in local git — fetch first")
            skipped += 1
            continue

        if args.verbose:
            print(f"[review-sync] {ref}: prepping local review (from remote queue)")
        ok = _prep_review(root, ref, review_type, args.dry_run, args.verbose)
        if ok:
            new_preps += 1
        else:
            skipped += 1

    if new_preps or already_done or skipped:
        print(
            f"[review-sync] reconciled: {new_preps} new preps, "
            f"{already_done} already done, {skipped} skipped"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
