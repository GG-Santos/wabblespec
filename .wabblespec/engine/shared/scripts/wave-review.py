#!/usr/bin/env python3
"""wave-review.py — WabbleSpec native review prep engine.

Extracts git diff + context and writes a structured pending review file.
Does NOT call any AI agent. The session agent (Claude) reads the pending
review and performs the review inline during the next session.

Pattern: same as Dream (writes gap-map) or memory-mine (writes index).
Background script = pure Python. AI work = done in the session.

Usage:
    python wave-review.py --ref HEAD [--type standard|security|design]
        Extract diff for HEAD and write a pending review to state/reviews/pending/.

    python wave-review.py --list
        List pending (unreviewed) review jobs.

    python wave-review.py --list --reviewed
        List all review jobs including completed ones.

    python wave-review.py --complete <ref> --verdict PASS|FAIL [--receipt <path>]
        Mark a pending review as complete (called by the session agent after review).

    python wave-review.py --enqueue <ref> [--type standard|security|design]
        Add ref to queue without extracting (lightweight enqueue for git hooks).

    python wave-review.py stats
        Show queue statistics.

Exit codes:
    0  success
    1  no diff found / nothing to review
    2  error (git unavailable, path error)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TIMESTAMP_SHORT = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
MAX_DIFF_LINES = 800


# ---------------------------------------------------------------------------
# Git helpers (pure Python / subprocess — no AI)
# ---------------------------------------------------------------------------

def _run(args: list[str], *, cwd: Path | None = None, timeout: int = 30) -> tuple[int, str]:
    import subprocess
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout,
                           cwd=str(cwd) if cwd else None, check=False)
        stdout = r.stdout.decode("utf-8", errors="replace") if r.stdout else ""
        stderr = r.stderr.decode("utf-8", errors="replace") if r.stderr else ""
        return r.returncode, (stdout + stderr).strip()
    except Exception as exc:
        return 2, str(exc)


def _repo_root() -> Path:
    rc, out = _run(["git", "rev-parse", "--show-toplevel"])
    if rc != 0:
        raise RuntimeError(f"Not a git repository: {out}")
    return Path(out.strip())


def _resolve_ref(ref: str, root: Path) -> str:
    rc, sha = _run(["git", "rev-parse", "--short", ref], cwd=root)
    return sha.strip() if rc == 0 and sha.strip() else ref


def _get_diff(ref: str, root: Path, max_lines: int) -> str:
    rc, diff = _run(["git", "show", ref, "--format=", "--unified=5"], cwd=root)
    if rc != 0 or not diff.strip():
        rc, diff = _run(["git", "diff", "HEAD~1..HEAD"], cwd=root)
    lines = diff.splitlines()
    if len(lines) > max_lines:
        diff = "\n".join(lines[:max_lines]) + f"\n\n[... truncated at {max_lines} lines ...]"
    return diff


def _get_commit_info(ref: str, root: Path) -> str:
    rc, info = _run(
        ["git", "log", "-1", "--format=%h %s%nAuthor: %an%nDate: %ai", ref], cwd=root
    )
    return info if rc == 0 else "(commit info unavailable)"


# ---------------------------------------------------------------------------
# Context loading (pure Python — reads files, no AI)
# ---------------------------------------------------------------------------

def _load_context(root: Path) -> dict:
    ctx: dict = {}

    task_card = root / ".wabblespec" / "state" / "plans" / "task-card.md"
    if task_card.exists():
        try:
            text = task_card.read_text(encoding="utf-8")
            lines = text.splitlines()
            goal_lines = [l for l in lines if l.startswith("**goal:**")]
            ctx["task_goal"] = goal_lines[0] if goal_lines else ""
            ctx["task_card_path"] = str(task_card)
        except Exception:
            pass

    session_file = root / ".wabblespec" / "state" / "session" / "state.json"
    if session_file.exists():
        try:
            state = json.loads(session_file.read_text(encoding="utf-8"))
            ctx["session_id"] = state.get("session_id", "")
            ctx["task_id"] = state.get("task_id", "")
        except Exception:
            pass

    toml_path = root / ".roborev.toml"
    if toml_path.exists():
        try:
            raw = toml_path.read_text(encoding="utf-8")
            if 'review_guidelines' in raw:
                start = raw.find('"""', raw.find('review_guidelines'))
                end = raw.find('"""', start + 3)
                if start != -1 and end != -1:
                    ctx["review_guidelines"] = raw[start + 3:end].strip()[:2000]
        except Exception:
            pass

    return ctx


# ---------------------------------------------------------------------------
# Prompt template loading (pure Python — reads files)
# ---------------------------------------------------------------------------

def _load_template(review_type: str, root: Path) -> str:
    review_dir = root / ".wabblespec" / "engine" / "shared" / "review"
    path = review_dir / f"{review_type}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    fallback = review_dir / "standard.txt"
    if fallback.exists():
        return fallback.read_text(encoding="utf-8").strip()
    return "Review the following code changes for correctness, quality, and security."


# ---------------------------------------------------------------------------
# Pending review file (the artifact the session agent reads)
# ---------------------------------------------------------------------------

def _pending_dir(root: Path) -> Path:
    p = root / ".wabblespec" / "state" / "reviews" / "pending"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _reviewed_dir(root: Path) -> Path:
    p = root / ".wabblespec" / "state" / "reviews" / "completed"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _write_pending(root: Path, ref: str, resolved_ref: str, review_type: str,
                   diff: str, commit_info: str, ctx: dict, template: str) -> Path:
    """Write a structured pending review file. The session agent reads this."""
    pending = {
        "schema_version": 1,
        "ref": ref,
        "resolved_ref": resolved_ref,
        "review_type": review_type,
        "queued_at": NOW,
        "status": "pending",
        "session_id": ctx.get("session_id", ""),
        "task_id": ctx.get("task_id", ""),
        "commit_info": commit_info,
        "task_goal": ctx.get("task_goal", ""),
        "task_card_path": ctx.get("task_card_path", ""),
        "review_guidelines_excerpt": ctx.get("review_guidelines", "")[:500],
        "review_prompt_template": template,
        "diff": diff,
        "diff_lines": len(diff.splitlines()),
        "instructions": (
            "Read the review_prompt_template, then the diff, then produce a structured "
            "review with VERDICT: PASS or FAIL, and FINDINGS sorted HIGH → MEDIUM → LOW "
            "grouped by file. Write the receipt via receipt-writer.py --type wave-review "
            "and mark this job complete via wave-review.py --complete."
        ),
    }

    out_path = _pending_dir(root) / f"{resolved_ref}-{review_type}-{TIMESTAMP_SHORT}.json"
    out_path.write_text(json.dumps(pending, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Queue management
# ---------------------------------------------------------------------------

def _queue_path(root: Path) -> Path:
    p = root / ".wabblespec" / "state" / "reviews"
    p.mkdir(parents=True, exist_ok=True)
    return p / "queue.json"


def _read_queue(root: Path) -> list[dict]:
    q = _queue_path(root)
    if not q.exists():
        return []
    try:
        return json.loads(q.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_queue(root: Path, items: list[dict]) -> None:
    _queue_path(root).write_text(json.dumps(items, indent=2), encoding="utf-8")


def _enqueue_entry(root: Path, ref: str, resolved_ref: str,
                   review_type: str, pending_path: str) -> None:
    items = _read_queue(root)
    if any(i.get("resolved_ref") == resolved_ref and i.get("status") == "pending"
           for i in items):
        return  # already queued
    items.append({
        "ref": ref,
        "resolved_ref": resolved_ref,
        "review_type": review_type,
        "queued_at": NOW,
        "status": "pending",
        "pending_path": pending_path,
        "verdict": None,
        "receipt_path": None,
    })
    _write_queue(root, items)


def _mark_complete(root: Path, ref: str, verdict: str, receipt_path: str) -> bool:
    items = _read_queue(root)
    found = False
    for item in items:
        if item.get("ref") == ref or item.get("resolved_ref") == ref:
            item["status"] = "reviewed"
            item["verdict"] = verdict
            item["receipt_path"] = receipt_path
            item["reviewed_at"] = NOW
            found = True
    if found:
        _write_queue(root, items)
        # Move pending file to completed
        pending_path = next(
            (i.get("pending_path") for i in items if i.get("ref") == ref), None
        )
        if pending_path and Path(pending_path).exists():
            dest = _reviewed_dir(root) / Path(pending_path).name
            try:
                Path(pending_path).rename(dest)
            except Exception:
                pass
    return found


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_prep(args, root: Path) -> int:
    """Extract diff and write pending review file."""
    ref = args.ref or "HEAD"
    resolved_ref = _resolve_ref(ref, root)

    diff = _get_diff(ref, root, args.max_diff_lines)
    if not diff.strip():
        print(f"[wave-review] no diff for {ref} — nothing to review", flush=True)
        return 1

    commit_info = _get_commit_info(ref, root)
    ctx = _load_context(root)
    template = _load_template(args.review_type, root)

    pending_path = _write_pending(
        root, ref, resolved_ref, args.review_type,
        diff, commit_info, ctx, template
    )
    _enqueue_entry(root, ref, resolved_ref, args.review_type, str(pending_path))

    print(
        f"[wave-review] pending review queued: {pending_path.name}\n"
        f"  ref={resolved_ref}  type={args.review_type}  diff_lines={len(diff.splitlines())}\n"
        f"  Run /wave-review in your next session to perform the review.",
        flush=True,
    )
    return 0


def cmd_list(args, root: Path) -> int:
    items = _read_queue(root)
    if not args.reviewed:
        items = [i for i in items if i.get("status") == "pending"]
    if not items:
        print("[wave-review] no" + (" pending" if not args.reviewed else "") + " reviews")
        return 0
    if getattr(args, "format", "table") == "json":
        print(json.dumps(items, indent=2))
        return 0
    for i in items:
        verdict = i.get("verdict") or "-"
        print(f"  {i['status']:10s}  {i.get('resolved_ref','?'):12s}  "
              f"{i['review_type']:10s}  verdict={verdict}")
    return 0


def cmd_complete(args, root: Path) -> int:
    found = _mark_complete(root, args.complete, args.verdict, args.receipt or "")
    if found:
        print(f"[wave-review] marked {args.complete} as reviewed (verdict={args.verdict})")
        return 0
    print(f"[wave-review] ref not found in queue: {args.complete}")
    return 1


def cmd_enqueue_only(args, root: Path) -> int:
    resolved_ref = _resolve_ref(args.enqueue, root)
    _enqueue_entry(root, args.enqueue, resolved_ref, args.review_type, "")
    print(f"[wave-review] enqueued {resolved_ref} (prep deferred)")
    return 0


def cmd_stats(root: Path) -> int:
    items = _read_queue(root)
    pending = sum(1 for i in items if i.get("status") == "pending")
    reviewed = sum(1 for i in items if i.get("status") == "reviewed")
    passed = sum(1 for i in items if i.get("verdict") == "PASS")
    failed = sum(1 for i in items if i.get("verdict") == "FAIL")
    print(f"Total: {len(items)}  Pending: {pending}  Reviewed: {reviewed}  "
          f"Pass: {passed}  Fail: {failed}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="WabbleSpec wave review prep — extracts diff, writes pending review"
    )
    parser.add_argument("--ref", default="HEAD", help="Git ref (default: HEAD)")
    parser.add_argument("--type", dest="review_type", default="standard",
                        choices=["standard", "security", "design"])
    parser.add_argument("--max-diff-lines", type=int, default=MAX_DIFF_LINES)
    parser.add_argument("--list", action="store_true", help="List reviews")
    parser.add_argument("--reviewed", action="store_true",
                        help="Include completed reviews in --list")
    parser.add_argument("--format", default="table", choices=["table", "json"])
    parser.add_argument("--complete", metavar="REF",
                        help="Mark a ref as reviewed (called by session agent)")
    parser.add_argument("--verdict", choices=["PASS", "FAIL"],
                        help="Verdict for --complete")
    parser.add_argument("--receipt", metavar="PATH",
                        help="Receipt path for --complete")
    parser.add_argument("--enqueue", metavar="REF",
                        help="Lightweight enqueue without diff extraction")
    parser.add_argument("stats", nargs="?", help="Show statistics")

    args = parser.parse_args()

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"[wave-review] ERROR: {exc}", flush=True)
        return 2

    if args.stats == "stats":
        return cmd_stats(root)
    if args.list:
        return cmd_list(args, root)
    if args.complete:
        if not args.verdict:
            print("[wave-review] --verdict required with --complete", flush=True)
            return 1
        return cmd_complete(args, root)
    if args.enqueue:
        return cmd_enqueue_only(args, root)

    return cmd_prep(args, root)


if __name__ == "__main__":
    raise SystemExit(main())
