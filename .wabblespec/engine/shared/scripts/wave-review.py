#!/usr/bin/env python3
"""wave-review.py — WabbleSpec native review prep engine.

Extracts git diff + context from existing WabbleSpec session sources and writes
a pending review file. Does NOT call any AI. The session agent performs the
review inline using /wave-review skill.

Pattern: same as dream.py (writes gap-map) — background script is pure Python,
AI work happens in the session.

Context sources:
  .wabblespec/state/plans/task-card.md     (acceptance criteria = review criteria)
  .wabblespec/state/scope.md               (boundaries = what to flag/not flag)
  .wabblespec/engine/shared/references/invariants.md  (12 invariants = hard rules)

Queue: uses wave-queue.py (existing file-locked queue) NOT a separate SQLite DB.
Receipts: writes to .wabblespec/state/receipts/ (main chain, auto-imported to DuckDB).

Usage:
    wave-review.py --ref HEAD [--type standard|security|design]
        Extract diff, write pending file, enqueue in wave-queue.

    wave-review.py --range A..B [--type ...]
        Review a commit range.

    wave-review.py --dirty [--type ...]
        Review uncommitted changes.

    wave-review.py --list [--all]
        List pending (or all) review jobs from wave-queue.

    wave-review.py --complete <ref> --verdict PASS|FAIL --receipt <path>
        Mark a job done (called by /wave-review skill after inline review).

    wave-review.py --enqueue <ref>
        Lightweight enqueue without diff extraction (for post-commit hook).

    wave-review.py --install-hook
        Install git post-commit hook in current repo.

    wave-review.py stats
        Show queue statistics via wave-queue.

Exit codes: 0 success, 1 no diff / nothing to review, 2 error
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

NOW   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
SHORT = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
MAX_DIFF_LINES = 800


# ---------------------------------------------------------------------------
# Repo resolution
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError("Not a git repository")
    return Path(r.stdout.strip())


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _run(args: list[str], *, cwd: Path | None = None, timeout: int = 30) -> tuple[int, str]:
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout,
                           cwd=str(cwd) if cwd else None, check=False)
        out = (r.stdout or b"").decode("utf-8", errors="replace")
        err = (r.stderr or b"").decode("utf-8", errors="replace")
        return r.returncode, (out + err).strip()
    except Exception as exc:
        return 2, str(exc)


def _get_diff(ref: str, root: Path, max_lines: int,
              range_: str | None = None, dirty: bool = False) -> str:
    if dirty:
        rc, diff = _run(["git", "diff"], cwd=root)
        if not diff.strip():
            rc, diff = _run(["git", "diff", "--cached"], cwd=root)
    elif range_:
        rc, diff = _run(["git", "diff", range_], cwd=root)
    else:
        rc, diff = _run(["git", "show", ref, "--format=", "--unified=5"], cwd=root)
        if rc != 0 or not diff.strip():
            rc, diff = _run(["git", "diff", "HEAD~1..HEAD"], cwd=root)
    lines = diff.splitlines()
    if len(lines) > max_lines:
        diff = "\n".join(lines[:max_lines]) + f"\n\n[...truncated at {max_lines} lines...]"
    return diff


def _resolve_ref(ref: str, root: Path) -> str:
    rc, out = _run(["git", "rev-parse", "--short", ref], cwd=root)
    return out.strip() if rc == 0 and out.strip() else ref


def _commit_info(ref: str, root: Path) -> str:
    rc, out = _run(["git", "log", "-1", "--format=%h %s%nAuthor: %an%nDate: %ai", ref], cwd=root)
    return out if rc == 0 else "(commit info unavailable)"


# ---------------------------------------------------------------------------
# Context loading from WabbleSpec session sources — NOT from .roborev.toml
# ---------------------------------------------------------------------------

def _load_context(root: Path) -> dict:
    ctx: dict = {}
    ws = root / ".wabblespec"

    # Task card — acceptance criteria are the review criteria
    tc = ws / "state" / "plans" / "task-card.md"
    if tc.exists():
        try:
            text = tc.read_text(encoding="utf-8")
            lines = text.splitlines()
            goal = next((l for l in lines if l.startswith("**goal:**")), "")
            ac_start = next((i for i, l in enumerate(lines) if "## Acceptance" in l), -1)
            ac = "\n".join(lines[ac_start:ac_start + 20]) if ac_start >= 0 else ""
            ctx["task_goal"]   = goal
            ctx["task_criteria"] = ac
            ctx["task_card_path"] = str(tc)
        except Exception:
            pass

    # Scope — what is and isn't in scope drives what to flag
    sc = ws / "state" / "scope.md"
    if sc.exists():
        try:
            ctx["scope_excerpt"] = sc.read_text(encoding="utf-8")[:1500]
        except Exception:
            pass

    # Invariants — hard rules; violations are always HIGH
    inv = ws / "engine" / "shared" / "references" / "invariants.md"
    if inv.exists():
        try:
            ctx["invariants_excerpt"] = inv.read_text(encoding="utf-8")[:1500]
        except Exception:
            pass

    # Session state
    ss = ws / "state" / "session" / "state.json"
    if ss.exists():
        try:
            state = json.loads(ss.read_text(encoding="utf-8"))
            ctx["session_id"] = state.get("session_id", "")
            ctx["task_id"]    = state.get("task_id", "")
        except Exception:
            pass

    return ctx


# ---------------------------------------------------------------------------
# Prompt template loading
# ---------------------------------------------------------------------------

def _load_template(review_type: str, root: Path) -> str:
    d = root / ".wabblespec" / "engine" / "shared" / "review"
    p = d / f"{review_type}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    f = d / "standard.txt"
    return f.read_text(encoding="utf-8").strip() if f.exists() else \
        "Review the diff for correctness, quality, and security."


# ---------------------------------------------------------------------------
# Pending file (what the session agent reads)
# ---------------------------------------------------------------------------

def _pending_dir(root: Path) -> Path:
    p = root / ".wabblespec" / "state" / "reviews" / "pending"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _completed_dir(root: Path) -> Path:
    p = root / ".wabblespec" / "state" / "reviews" / "completed"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _write_pending(root: Path, ref: str, resolved_ref: str, review_type: str,
                   diff: str, commit_info: str, ctx: dict, template: str) -> Path:
    job = {
        "schema_version": 1,
        "ref": ref,
        "resolved_ref": resolved_ref,
        "review_type": review_type,
        "queued_at": NOW,
        "session_id": ctx.get("session_id", ""),
        "task_id": ctx.get("task_id", ""),
        "commit_info": commit_info,
        "task_goal":     ctx.get("task_goal", ""),
        "task_criteria": ctx.get("task_criteria", ""),
        "scope_excerpt": ctx.get("scope_excerpt", ""),
        "invariants_excerpt": ctx.get("invariants_excerpt", ""),
        "review_prompt_template": template,
        "diff": diff,
        "diff_lines": len(diff.splitlines()),
        "instructions": (
            "Read review_prompt_template → review diff against task_criteria and scope_excerpt "
            "→ flag invariants_excerpt violations as HIGH → produce VERDICT: PASS|FAIL "
            "and FINDINGS sorted HIGH→MEDIUM→LOW grouped by file "
            "→ write receipt via receipt-writer.py --type wave-review to state/receipts/ "
            "→ call wave-review.py --complete to mark done."
        ),
    }
    out = _pending_dir(root) / f"{resolved_ref}-{review_type}-{SHORT}.json"
    out.write_text(json.dumps(job, indent=2), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Wave-queue integration (replaces custom SQLite queue)
# ---------------------------------------------------------------------------

def _wave_queue(root: Path) -> Path:
    return root / ".wabblespec" / "engine" / "shared" / "scripts" / "wave-queue.py"


def _enqueue_wave_queue(root: Path, task_id: str, label: str, pending_path: str) -> bool:
    """Add a review job to the existing wave-queue system."""
    wq = _wave_queue(root)
    if not wq.exists():
        return False
    # wave-queue populate expects a wave plan; for reviews we use its JSON API directly
    queue_dir = root / ".wabblespec" / "state" / "queue"
    queue_dir.mkdir(parents=True, exist_ok=True)
    queue_file = queue_dir / "wave-queue.json"

    # Load or create queue
    try:
        q = json.loads(queue_file.read_text(encoding="utf-8")) if queue_file.exists() else \
            {"schema_version": 1, "session_id": task_id, "tasks": []}
    except Exception:
        q = {"schema_version": 1, "session_id": task_id, "tasks": []}

    # Deduplicate by task_id
    if any(t.get("task_id") == task_id for t in q.get("tasks", [])):
        return True

    q.setdefault("tasks", []).append({
        "task_id":      task_id,
        "wave_number":  0,
        "label":        label,
        "status":       "pending",
        "worker_id":    None,
        "receipt_path": None,
        "pending_path": pending_path,
        "queued_at":    NOW,
    })

    tmp = str(queue_file) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(q, f, indent=2)
    os.replace(tmp, str(queue_file))
    return True


def _mark_complete(root: Path, task_id: str, verdict: str, receipt_path: str) -> bool:
    queue_file = root / ".wabblespec" / "state" / "queue" / "wave-queue.json"
    if not queue_file.exists():
        return False
    try:
        q = json.loads(queue_file.read_text(encoding="utf-8"))
    except Exception:
        return False
    found = False
    for t in q.get("tasks", []):
        if t.get("task_id") == task_id or t.get("pending_path", "").find(task_id.split("-")[0]) >= 0:
            t["status"]       = "PASS" if verdict == "PASS" else "FAIL"
            t["receipt_path"] = receipt_path
            t["completed_at"] = NOW
            found = True
    if found:
        tmp = str(queue_file) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(q, f, indent=2)
        os.replace(tmp, str(queue_file))
    return found


def _list_queue(root: Path, show_all: bool = False) -> list[dict]:
    queue_file = root / ".wabblespec" / "state" / "queue" / "wave-queue.json"
    if not queue_file.exists():
        return []
    try:
        q = json.loads(queue_file.read_text(encoding="utf-8"))
        tasks = [t for t in q.get("tasks", [])
                 if t.get("label", "").startswith("wave-review")]
        if not show_all:
            tasks = [t for t in tasks if t.get("status") == "pending"]
        return tasks
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_prep(args, root: Path) -> int:
    ref = args.ref or "HEAD"
    resolved = _resolve_ref(ref, root)

    diff = _get_diff(ref, root, args.max_diff_lines,
                     range_=getattr(args, "range_", None),
                     dirty=getattr(args, "dirty", False))
    if not diff.strip():
        print(f"[wave-review] no diff for {ref} — nothing to review")
        return 1

    commit  = _commit_info(ref, root)
    ctx     = _load_context(root)
    tmpl    = _load_template(args.review_type, root)
    pending = _write_pending(root, ref, resolved, args.review_type,
                             diff, commit, ctx, tmpl)

    task_id = f"wave-review-{resolved}-{args.review_type}"
    _enqueue_wave_queue(root, task_id, f"wave-review:{resolved}", str(pending))

    print(f"[wave-review] queued {resolved} ({args.review_type}) "
          f"diff_lines={len(diff.splitlines())}")
    print(f"  pending: {pending.name}")
    print(f"  Run /wave-review in your session to perform the review.")
    return 0


def cmd_list(args, root: Path) -> int:
    tasks = _list_queue(root, show_all=getattr(args, "all", False))
    if not tasks:
        print("[wave-review] no pending reviews")
        return 0
    for t in tasks:
        pp = t.get("pending_path", "")
        ref = t.get("label", "").replace("wave-review:", "")
        print(f"  {t['status']:9s}  {ref:14s}  {t.get('queued_at','')}")
        if pp:
            try:
                j = json.loads(Path(pp).read_text(encoding="utf-8"))
                print(f"             diff_lines={j.get('diff_lines','?')}  "
                      f"type={j.get('review_type','?')}")
            except Exception:
                pass
    return 0


def write_quality_drawers(root: Path, resolved_ref: str, findings: list[dict],
                          session_id: str, task_id: str) -> list[Path]:
    """Write HIGH/CRITICAL findings as memory drawers in wings/quality/.

    Dream and entity-graph pick these up automatically on the next session stop:
    - Dream decays their confidence over time (findings become STALE if not re-raised)
    - entity-graph builds file co-occurrence edges (files with repeated findings
      become high-degree nodes)

    Only HIGH and CRITICAL findings are written — MEDIUM/LOW are informational
    only and would create too much noise in the gap-map.
    """
    wings = root / ".wabblespec" / "state" / "memory" / "wings" / "quality"
    written: list[Path] = []

    for i, f in enumerate(findings):
        sev = f.get("severity", "LOW").upper()
        if sev not in ("HIGH", "CRITICAL"):
            continue

        location = f.get("location", "") or f.get("file", "")
        desc     = f.get("description", "")[:200]
        fix      = f.get("fix_recommendation", "") or f.get("fix", "")

        # Room = file path slugified (or "general" if no file)
        room_slug = location.replace("/", "-").replace("\\", "-").replace(".", "-") \
                    if location else "general"
        room_dir = wings / room_slug
        room_dir.mkdir(parents=True, exist_ok=True)

        drawer_id = f"quality-{resolved_ref}-{i:02d}"
        drawer = {
            "drawer_id":       drawer_id,
            "id":              drawer_id,
            "wing":            "quality",
            "room":            room_slug,
            "topic":           f"[{sev}] {desc[:60]}",
            "staleness_state": "FRESH",
            "confidence":      1.0,
            "written_at":      NOW,
            "tags":            [sev.lower(), "wave-review", "code-quality"],
            "body": {
                "severity":    sev,
                "ref":         resolved_ref,
                "location":    location,
                "description": desc,
                "fix":         fix,
                "session_id":  session_id,
                "task_id":     task_id,
            },
            "evidence":  [f"{location}: {desc[:100]}"] if location else [desc[:100]],
            "provenance": [{"event": "WAVE_REVIEW", "timestamp": NOW,
                            "actor": "wave-reviewer", "ref": resolved_ref}],
        }
        out = room_dir / f"{drawer_id}.json"
        out.write_text(json.dumps(drawer, indent=2), encoding="utf-8")
        written.append(out)

    if written:
        print(f"[wave-review] wrote {len(written)} quality drawers → Dream+entity-graph will process")
    return written


def cmd_complete(args, root: Path) -> int:
    # Move pending file to completed
    pending_dir = _pending_dir(root)
    completed   = _completed_dir(root)
    for p in pending_dir.glob(f"{args.complete}*.json"):
        try:
            p.rename(completed / p.name)
        except Exception:
            pass
    # Mark in wave-queue
    task_id = f"wave-review-{args.complete}-"
    queue_file = root / ".wabblespec" / "state" / "queue" / "wave-queue.json"
    if queue_file.exists():
        try:
            q = json.loads(queue_file.read_text(encoding="utf-8"))
            for t in q.get("tasks", []):
                if t.get("task_id", "").startswith(f"wave-review-{args.complete}"):
                    t["status"]       = "PASS" if args.verdict == "PASS" else "FAIL"
                    t["receipt_path"] = args.receipt or ""
                    t["completed_at"] = NOW
            tmp = str(queue_file) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(q, f, indent=2)
            os.replace(tmp, str(queue_file))
        except Exception:
            pass
    print(f"[wave-review] {args.complete} → {args.verdict}")
    return 0


def cmd_enqueue_only(args, root: Path) -> int:
    resolved = _resolve_ref(args.enqueue, root)
    task_id  = f"wave-review-{resolved}-{args.review_type}"
    _enqueue_wave_queue(root, task_id, f"wave-review:{resolved}", "")
    print(f"[wave-review] enqueued {resolved} (prep deferred)")
    return 0


def cmd_stats(root: Path) -> int:
    tasks = _list_queue(root, show_all=True)
    pending  = sum(1 for t in tasks if t.get("status") == "pending")
    passed   = sum(1 for t in tasks if t.get("status") == "PASS")
    failed   = sum(1 for t in tasks if t.get("status") == "FAIL")
    print(f"Total: {len(tasks)}  Pending: {pending}  Pass: {passed}  Fail: {failed}")
    return 0


def cmd_install_hook(root: Path) -> int:
    hook    = root / ".git" / "hooks" / "post-commit"
    script  = Path(__file__).resolve()
    marker  = "# WabbleSpec wave-review"
    snippet = f"\n{marker}\npython \"{script}\" --enqueue HEAD 2>/dev/null &\n"

    if hook.exists():
        existing = hook.read_text(encoding="utf-8")
        if marker in existing:
            print(f"Hook already installed: {hook}")
            return 0
        hook.write_text(existing.rstrip() + "\n" + snippet, encoding="utf-8")
    else:
        hook.write_text("#!/bin/sh" + snippet, encoding="utf-8")
    try:
        hook.chmod(0o755)
    except Exception:
        pass
    print(f"Post-commit hook installed: {hook}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="WabbleSpec wave review prep")
    p.add_argument("--ref",   default="HEAD")
    p.add_argument("--range", dest="range_", default=None)
    p.add_argument("--dirty", action="store_true")
    p.add_argument("--type",  dest="review_type", default="standard",
                   choices=["standard", "security", "design"])
    p.add_argument("--max-diff-lines", type=int, default=MAX_DIFF_LINES)
    p.add_argument("--list",     action="store_true")
    p.add_argument("--all",      action="store_true", help="Include completed in --list")
    p.add_argument("--complete", metavar="REF")
    p.add_argument("--verdict",  choices=["PASS", "FAIL"])
    p.add_argument("--receipt",  metavar="PATH", default="")
    p.add_argument("--enqueue",  metavar="REF")
    p.add_argument("--install-hook", action="store_true")
    p.add_argument("--write-drawers", metavar="FINDINGS_JSON",
                   help="Write quality drawers from a JSON array of findings (called after review)")
    p.add_argument("--session-id", default="")
    p.add_argument("--task-id",    default="")
    p.add_argument("stats",      nargs="?")
    args = p.parse_args()

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"[wave-review] ERROR: {exc}", file=sys.stderr)
        return 2

    if args.stats == "stats":  return cmd_stats(root)
    if args.list:              return cmd_list(args, root)
    if args.install_hook:      return cmd_install_hook(root)
    if args.write_drawers:
        try:
            findings = json.loads(args.write_drawers)
            written  = write_quality_drawers(root, args.ref or "unknown",
                                             findings, args.session_id, args.task_id)
            return 0
        except Exception as exc:
            print(f"[wave-review] --write-drawers error: {exc}", file=sys.stderr)
            return 2
    if args.complete:
        if not args.verdict:
            print("[wave-review] --verdict required with --complete", file=sys.stderr)
            return 1
        return cmd_complete(args, root)
    if args.enqueue:           return cmd_enqueue_only(args, root)
    return cmd_prep(args, root)


if __name__ == "__main__":
    raise SystemExit(main())
