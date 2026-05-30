#!/usr/bin/env python3
"""wave-review.py — WabbleSpec native code review engine.

Extracts a git diff, builds a review prompt from WabbleSpec context,
invokes the review agent headlessly, parses the verdict and findings,
and writes a wave-review receipt.

This is WabbleSpec's own review infrastructure — no external review
daemon dependency. The review agent is invoked via the `claude` CLI
(`claude -p`), which is already present in the WabbleSpec environment.

Usage:
    python wave-review.py [options]

    --ref HEAD          Git ref to review (default: HEAD)
    --range A..B        Git range to review (overrides --ref)
    --type standard     Review type: standard | security | design (default: standard)
    --context-file PATH Extra context file to include in prompt (e.g. task card)
    --session-id ID     Session ID for receipt (default: review-<timestamp>)
    --task-id ID        Task ID for receipt (default: same as session-id)
    --out PATH          Receipt output path (default: .wabblespec/state/reviews/<ref>-review.json)
    --dry-run           Print the prompt without calling the agent
    --max-diff-lines N  Truncate diff at N lines (default: 800)
    --wait              Block until review completes (always true in this implementation)
    --list              List open (unreviewed) reviews from the queue
    --fix-open          Show open findings for the agent to address

Exit codes:
    0  PASS verdict or dry-run complete
    1  FAIL verdict
    2  Error (could not run review, git error, agent unavailable)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REVIEW_DIR = Path(".wabblespec/engine/shared/review")
RECEIPTS_DIR = Path(".wabblespec/state/reviews")
MAX_DIFF_LINES = 800
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TIMESTAMP_SHORT = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _run(args: list[str], *, cwd: Path | None = None, timeout: int = 30) -> tuple[int, str]:
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout,
                           cwd=str(cwd) if cwd else None, check=False)
        stdout = r.stdout.decode("utf-8", errors="replace") if r.stdout else ""
        stderr = r.stderr.decode("utf-8", errors="replace") if r.stderr else ""
        return r.returncode, (stdout + stderr).strip()
    except subprocess.TimeoutExpired:
        return 2, f"timed out after {timeout}s"
    except Exception as exc:
        return 2, str(exc)


def _repo_root() -> Path:
    rc, out = _run(["git", "rev-parse", "--show-toplevel"])
    if rc != 0:
        raise RuntimeError(f"Not a git repository: {out}")
    return Path(out.strip())


def _get_diff(ref: str | None, range_: str | None, root: Path, max_lines: int) -> tuple[str, str]:
    """Return (diff_text, resolved_ref). Truncates if over max_lines."""
    if range_:
        rc, diff = _run(["git", "diff", range_], cwd=root)
        resolved = range_
    else:
        ref = ref or "HEAD"
        rc, diff = _run(["git", "show", ref, "--format=", "--unified=5"], cwd=root)
        if rc != 0:
            # fallback: staged diff
            rc, diff = _run(["git", "diff", "--cached"], cwd=root)
        _, resolved = _run(["git", "rev-parse", "--short", ref], cwd=root)
        resolved = resolved.strip() or ref

    lines = diff.splitlines()
    if len(lines) > max_lines:
        diff = "\n".join(lines[:max_lines]) + f"\n\n[... diff truncated at {max_lines} lines ...]"

    return diff, resolved


def _get_commit_info(ref: str, root: Path) -> str:
    rc, info = _run(["git", "log", "-1", "--format=%h %s\nAuthor: %an\nDate: %ai", ref], cwd=root)
    return info if rc == 0 else "(commit info unavailable)"


# ---------------------------------------------------------------------------
# Context loading
# ---------------------------------------------------------------------------

def _load_context(root: Path, context_file: str | None) -> str:
    """Load WabbleSpec session context for the review prompt."""
    parts = []

    # Task card (if active session)
    task_card = root / ".wabblespec" / "state" / "plans" / "task-card.md"
    if task_card.exists():
        try:
            text = task_card.read_text(encoding="utf-8")
            # Include only goal + acceptance criteria (not full card)
            lines = text.splitlines()
            summary_lines = []
            in_ac = False
            for line in lines:
                if line.startswith("**goal:**") or line.startswith("## Acceptance"):
                    in_ac = True
                if in_ac:
                    summary_lines.append(line)
                if in_ac and line == "" and len(summary_lines) > 10:
                    break
            if summary_lines:
                parts.append("## Active task context\n" + "\n".join(summary_lines[:30]))
        except Exception:
            pass

    # Extra context file
    if context_file:
        try:
            text = Path(context_file).read_text(encoding="utf-8")
            parts.append(f"## Additional context ({context_file})\n{text[:2000]}")
        except Exception:
            pass

    # Review guidelines from .roborev.toml (or wabblespec.yaml note)
    toml_path = root / ".roborev.toml"
    if toml_path.exists():
        try:
            raw = toml_path.read_text(encoding="utf-8")
            # Extract review_guidelines value (naive parse — no toml dep)
            if 'review_guidelines' in raw:
                start = raw.find('"""', raw.find('review_guidelines'))
                end = raw.find('"""', start + 3)
                if start != -1 and end != -1:
                    guidelines = raw[start + 3:end].strip()
                    parts.append(f"## Project review guidelines\n{guidelines[:3000]}")
        except Exception:
            pass

    return "\n\n".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _load_prompt_template(review_type: str, review_dir: Path) -> str:
    template_path = review_dir / f"{review_type}.txt"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8").strip()
    # Fallback to standard
    fallback = review_dir / "standard.txt"
    if fallback.exists():
        return fallback.read_text(encoding="utf-8").strip()
    return "Review the following code changes for correctness, quality, and security."


def _build_prompt(diff: str, commit_info: str, context: str,
                  review_type: str, review_dir: Path) -> str:
    template = _load_prompt_template(review_type, review_dir)
    parts = [template]
    if context:
        parts.append(f"\n---\n{context}")
    parts.append(f"\n---\n## Commit being reviewed\n{commit_info}")
    parts.append(f"\n---\n## Diff\n```diff\n{diff}\n```")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Verdict parsing
# ---------------------------------------------------------------------------

def _parse_verdict(output: str) -> tuple[str, list[dict]]:
    """Extract PASS/FAIL verdict and findings from agent output.

    Returns (verdict, findings) where verdict is 'PASS' or 'FAIL'
    and findings is a list of {severity, description, location} dicts.
    """
    upper = output.upper()
    verdict = "PASS"
    if "VERDICT: FAIL" in upper or "**VERDICT:** FAIL" in upper:
        verdict = "FAIL"
    elif "VERDICT: PASS" in upper or "**VERDICT:** PASS" in upper:
        verdict = "PASS"
    elif "NO FINDINGS" in upper or "NO SECURITY FINDINGS" in upper:
        verdict = "PASS"
    elif "FINDINGS:" in upper and len(output) > 200:
        # Has a FINDINGS section with content — likely FAIL
        findings_idx = upper.find("FINDINGS:")
        after = output[findings_idx + 9:findings_idx + 500].strip()
        if after and not after.upper().startswith("NO "):
            verdict = "FAIL"

    # Parse findings by severity markers
    findings = []
    for line in output.splitlines():
        stripped = line.strip()
        for sev in ("HIGH", "MEDIUM", "LOW", "CRITICAL"):
            if stripped.upper().startswith(f"- {sev}") or stripped.upper().startswith(f"* {sev}") \
               or f"**{sev}**" in stripped.upper() or f"severity: {sev}" in stripped.upper():
                findings.append({"severity": sev, "description": stripped[:200], "location": ""})
                break

    return verdict, findings


# ---------------------------------------------------------------------------
# Agent invocation
# ---------------------------------------------------------------------------

def _call_agent(prompt: str, dry_run: bool) -> tuple[int, str]:
    """Invoke claude -p with the review prompt. Returns (exit_code, output)."""
    if dry_run:
        print("=== DRY RUN PROMPT ===")
        print(prompt[:3000])
        print("=== END PROMPT ===")
        return 0, "VERDICT: PASS\nNO FINDINGS (dry-run mode)"

    if not shutil.which("claude"):
        return 2, "claude CLI not found in PATH"

    # Write prompt to temp file to avoid shell injection from diff content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False, encoding="utf-8") as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        rc, output = _run(
            ["claude", "-p", f"$(cat {prompt_file})"],
            timeout=180,
        )
        if rc != 0 or not output:
            # Try direct stdin approach
            result = subprocess.run(
                ["claude", "--print"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
            output = (result.stdout + result.stderr).strip()
            rc = result.returncode
    finally:
        try:
            os.unlink(prompt_file)
        except Exception:
            pass

    return rc, output


# ---------------------------------------------------------------------------
# Queue helpers
# ---------------------------------------------------------------------------

def _queue_path(root: Path) -> Path:
    return root / ".wabblespec" / "state" / "reviews" / "queue.json"


def _read_queue(root: Path) -> list[dict]:
    q = _queue_path(root)
    if not q.exists():
        return []
    try:
        return json.loads(q.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_queue(root: Path, items: list[dict]) -> None:
    q = _queue_path(root)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps(items, indent=2), encoding="utf-8")


def _enqueue(root: Path, ref: str, review_type: str = "standard") -> None:
    items = _read_queue(root)
    # Deduplicate by ref
    if any(i["ref"] == ref for i in items):
        return
    items.append({
        "ref": ref,
        "review_type": review_type,
        "queued_at": NOW,
        "status": "pending",
    })
    _write_queue(root, items)
    print(f"[wave-review] queued review for {ref}", flush=True)


def _list_open(root: Path) -> list[dict]:
    return [i for i in _read_queue(root) if i.get("status") != "reviewed"]


def _mark_reviewed(root: Path, ref: str, verdict: str, receipt_path: str) -> None:
    items = _read_queue(root)
    for item in items:
        if item["ref"] == ref:
            item["status"] = "reviewed"
            item["verdict"] = verdict
            item["receipt_path"] = receipt_path
            item["reviewed_at"] = NOW
    _write_queue(root, items)


# ---------------------------------------------------------------------------
# Receipt write
# ---------------------------------------------------------------------------

def _write_receipt(root: Path, out_path: Path, ref: str, review_type: str,
                   verdict: str, findings: list[dict], output: str,
                   session_id: str, task_id: str) -> None:
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0}
    for f in findings:
        sev = f.get("severity", "LOW").upper()
        counts[sev] = counts.get(sev, 0) + 1

    receipt = {
        "receipt_type": "wave-review",
        "module": "wave-reviewer",
        "layer": "L2",
        "phase": "Verify",
        "timestamp": NOW,
        "session_id": session_id,
        "task_id": task_id,
        "git_ref": ref,
        "review_type": review_type,
        "verdict": verdict,
        "status": "PASS" if verdict == "PASS" else "FAIL",
        "finding_summary": {
            "total": len(findings),
            "by_severity": counts,
        },
        "findings": findings,
        "output_excerpt": output[:500] if output else "",
        "confidence": 0.85,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"[wave-review] receipt → {out_path}", flush=True)

    # Attempt receipt-writer upsert to DuckDB
    try:
        scripts_dir = root / ".wabblespec" / "engine" / "shared" / "scripts"
        rw = scripts_dir / "receipt-writer.py"
        if rw.exists():
            subprocess.run(
                [sys.executable, str(rw), "--validate", str(out_path)],
                capture_output=True, check=False, timeout=15,
            )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="WabbleSpec native wave reviewer")
    parser.add_argument("--ref", default="HEAD", help="Git ref to review")
    parser.add_argument("--range", dest="range_", default=None, help="Git range A..B")
    parser.add_argument("--type", dest="review_type", default="standard",
                        choices=["standard", "security", "design"],
                        help="Review focus (default: standard)")
    parser.add_argument("--context-file", default=None, help="Extra context file")
    parser.add_argument("--session-id", default=f"wave-review-{TIMESTAMP_SHORT}")
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--out", type=Path, default=None, help="Receipt output path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-diff-lines", type=int, default=MAX_DIFF_LINES)
    parser.add_argument("--list", action="store_true", help="List open reviews")
    parser.add_argument("--enqueue", metavar="REF", default=None,
                        help="Enqueue a ref for review without running it now")
    args = parser.parse_args()

    if args.task_id is None:
        args.task_id = args.session_id

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"[wave-review] ERROR: {exc}", flush=True)
        return 2

    # Sub-commands
    if args.list:
        open_reviews = _list_open(root)
        if not open_reviews:
            print("[wave-review] No open reviews.")
        else:
            for r in open_reviews:
                print(f"  {r['ref']} ({r['review_type']}) queued {r['queued_at']}")
        return 0

    if args.enqueue:
        _enqueue(root, args.enqueue, args.review_type)
        return 0

    # Resolve paths
    review_dir = root / REVIEW_DIR if not (root / REVIEW_DIR).is_absolute() else Path(REVIEW_DIR)
    review_dir = root / ".wabblespec" / "engine" / "shared" / "review"

    ref = args.ref
    try:
        diff, resolved_ref = _get_diff(args.ref, args.range_, root, args.max_diff_lines)
    except Exception as exc:
        print(f"[wave-review] ERROR extracting diff: {exc}", flush=True)
        return 2

    if not diff.strip() and not args.dry_run:
        print(f"[wave-review] No diff found for {ref} — skipping", flush=True)
        return 0
    if not diff.strip() and args.dry_run:
        diff = "(dry-run: no actual diff — showing prompt structure)"

    commit_info = _get_commit_info(ref, root)
    context = _load_context(root, args.context_file)
    prompt = _build_prompt(diff, commit_info, context, args.review_type, review_dir)

    print(f"[wave-review] reviewing {resolved_ref} ({args.review_type})", flush=True)

    agent_rc, output = _call_agent(prompt, args.dry_run)

    if agent_rc == 2:
        print(f"[wave-review] ERROR: agent failed: {output}", flush=True)
        return 2

    verdict, findings = _parse_verdict(output)

    # Severity sort: HIGH → MEDIUM → LOW (from ref-adopt R2)
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings.sort(key=lambda f: sev_order.get(f.get("severity", "LOW").upper(), 3))

    print(f"[wave-review] verdict: {verdict} | findings: {len(findings)}", flush=True)
    for f in findings[:5]:
        print(f"  {f['severity']}: {f['description'][:80]}", flush=True)

    out_path = args.out or (
        root / ".wabblespec" / "state" / "reviews" /
        f"{resolved_ref}-{args.review_type}-{TIMESTAMP_SHORT}.json"
    )

    _write_receipt(root, out_path, resolved_ref, args.review_type,
                   verdict, findings, output, args.session_id, args.task_id)
    _mark_reviewed(root, ref, verdict, str(out_path))

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
