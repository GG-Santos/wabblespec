"""
queue-orchestrator.py — Parallel wave execution coordinator.

Bridges wave-queue.py (file-locked task queue) and the Claude Code Executor
skill (which fires parallel Agent calls). The orchestrator manages queue
lifecycle and surfaces ready-task manifests; actual agent spawning is done
by the Executor reading this script's output via the Agent tool.

Subcommands:
    populate    Populate queue from wave plan (wraps wave-queue populate)
    ready       Output JSON of tasks claimable in parallel right now
    advance     Check overall queue progress; exit 0=done, 1=pending, 2=fail
    status      Human-readable queue summary
    run         Sequential fallback: loop populate→claim→complete without agents

Usage:
    # 1. Populate at session start:
    python queue-orchestrator.py populate \\
        --session-id my-session \\
        --wave-plan .wabblespec/state/plans/current-wave-plan.md

    # 2. Get tasks ready for parallel dispatch:
    python queue-orchestrator.py ready
    # → Executor reads JSON output and fires one Agent per task

    # 3. After agents complete, check progress:
    python queue-orchestrator.py advance
    # → exit 0: all waves done → signal Archive
    # → exit 1: more waves pending → loop back to 'ready'
    # → exit 2: a task failed → surface to user

    # 4. (Optional) Non-parallel fallback for debugging:
    python queue-orchestrator.py run \\
        --session-id my-session \\
        --wave-plan .wabblespec/state/plans/current-wave-plan.md

Exit codes:
    0  success / all done
    1  pending work remains / no tasks available
    2  queue error / task failure detected
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Bootstrap repo root
_HERE = Path(__file__).resolve()
_REPO_ROOT_SENTINEL = ".wabblespec"
_probe = _HERE
while _probe != _probe.parent:
    if (_probe / _REPO_ROOT_SENTINEL).exists():
        break
    _probe = _probe.parent
if not (_probe / _REPO_ROOT_SENTINEL).exists():
    sys.exit("ERROR: cannot find WabbleSpec repo root")
ROOT = _probe

WAVE_QUEUE = ROOT / ".wabblespec" / "engine" / "shared" / "scripts" / "wave-queue.py"
QUEUE_PATH = ROOT / ".wabblespec" / "state" / "queue" / "wave-queue.json"


def _wq(*args: str) -> subprocess.CompletedProcess:
    """Run wave-queue.py with given args. Returns CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(WAVE_QUEUE)] + list(args),
        capture_output=True,
        text=True,
    )


def _load_queue() -> dict | None:
    if not QUEUE_PATH.exists():
        return None
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


# ── Subcommands ───────────────────────────────────────────────────────────────

def cmd_populate(args: argparse.Namespace) -> int:
    """Populate the queue from a wave plan. Delegates to wave-queue populate."""
    r = _wq("populate", "--session-id", args.session_id, "--wave-plan", args.wave_plan)
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
        return 2
    print(r.stdout.strip())
    return 0


def cmd_ready(args: argparse.Namespace) -> int:
    """Output JSON array of tasks that can be claimed and run in parallel right now.

    A task is ready when:
    - Its status is PENDING
    - All tasks in prior waves have status PASS

    Executor reads this output and fires one Agent call per task.
    Returns exit 1 if no tasks are ready (all pending in locked waves or all done).
    """
    queue = _load_queue()
    if queue is None:
        print("ERROR: No queue found. Run 'populate' first.", file=sys.stderr)
        return 2

    tasks = queue["tasks"]

    # Determine which wave numbers are unlocked (all prior waves fully PASS)
    by_wave: dict[int, list[dict]] = {}
    for t in tasks:
        by_wave.setdefault(t["wave_number"], []).append(t)

    wave_pass: dict[int, bool] = {}
    for wn in sorted(by_wave):
        prior = [wn2 for wn2 in by_wave if wn2 < wn]
        wave_pass[wn] = all(wave_pass.get(p, False) for p in prior) if prior else True
        # A wave is only PASS if all its tasks are PASS
        if wave_pass[wn]:
            wave_pass[wn] = all(t["status"] == "PASS" for t in by_wave[wn])

    unlocked: set[int] = set()
    for wn in sorted(by_wave):
        prior = [wn2 for wn2 in by_wave if wn2 < wn]
        all_prior_pass = all(wave_pass.get(p, False) for p in prior)
        has_pending = any(t["status"] == "PENDING" for t in by_wave[wn])
        if all_prior_pass and has_pending:
            unlocked.add(wn)

    ready = [
        t for t in tasks
        if t["status"] == "PENDING" and t["wave_number"] in unlocked
    ]

    if not ready:
        return 1

    print(json.dumps(ready, indent=2))
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    """Check overall queue progress.

    Exit 0: all waves complete (all tasks PASS) → signal Archive
    Exit 1: work in progress or pending → loop back to 'ready'
    Exit 2: one or more tasks FAIL → surface to user
    """
    queue = _load_queue()
    if queue is None:
        print("ERROR: No queue found.", file=sys.stderr)
        return 2

    tasks = queue["tasks"]
    failed = [t for t in tasks if t["status"] == "FAIL"]
    pending = [t for t in tasks if t["status"] in ("PENDING", "IN_PROGRESS")]

    if failed:
        print(f"FAIL — {len(failed)} task(s) failed:")
        for t in failed:
            print(f"  {t['task_id']}: {t.get('failure_reason', 'no reason given')}")
        return 2

    if pending:
        total = len(tasks)
        done = total - len(pending)
        print(f"IN_PROGRESS — {done}/{total} tasks complete, {len(pending)} pending")
        return 1

    total = len(tasks)
    print(f"DONE — all {total} tasks PASS")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Human-readable queue summary. Delegates to wave-queue status."""
    r = _wq("status")
    print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
    return r.returncode


def cmd_run(args: argparse.Namespace) -> int:
    """Sequential fallback: populate queue then claim/complete each task in order.

    Used for debugging or single-agent environments without parallel dispatch.
    Does not spawn subagents — prints task details for Claude to execute inline.
    """
    # Populate
    rc = cmd_populate(args)
    if rc != 0:
        return rc

    print("\n[queue-orchestrator] Sequential run mode — claim tasks one at a time.")
    while True:
        # Get next ready task
        r = _wq("claim", "--worker-id", "orchestrator-sequential")
        if r.returncode == 1:
            # No task available — check if done
            adv = cmd_advance(args)
            if adv == 0:
                print("[queue-orchestrator] All waves complete.")
                return 0
            if adv == 2:
                return 2
            print("[queue-orchestrator] No tasks claimable — waiting for in-progress tasks.")
            return 1
        if r.returncode != 0:
            print(r.stderr.strip(), file=sys.stderr)
            return 2

        task = json.loads(r.stdout)
        print(f"\n[queue-orchestrator] Ready to execute:")
        print(json.dumps(task, indent=2))
        print(f"[queue-orchestrator] Execute wave {task['wave_number']}: {task['wave_label']}")
        print(f"[queue-orchestrator] Then run: wave-queue.py complete --task-id {task['task_id']} --worker-id orchestrator-sequential --receipt-path <path>")
        # In sequential mode, return after surfacing each task for inline execution
        return 0


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pop = sub.add_parser("populate", help="Populate queue from wave plan")
    p_pop.add_argument("--session-id", required=True, metavar="ID")
    p_pop.add_argument("--wave-plan", required=True, metavar="PATH")

    sub.add_parser("ready", help="Output JSON of tasks ready for parallel dispatch")

    sub.add_parser("advance", help="Check wave progress (exit 0=done, 1=pending, 2=fail)")

    sub.add_parser("status", help="Human-readable queue summary")

    p_run = sub.add_parser("run", help="Sequential fallback (no parallel agents)")
    p_run.add_argument("--session-id", required=True, metavar="ID")
    p_run.add_argument("--wave-plan", required=True, metavar="PATH")

    args = parser.parse_args()

    dispatch = {
        "populate": cmd_populate,
        "ready":    cmd_ready,
        "advance":  cmd_advance,
        "status":   cmd_status,
        "run":      cmd_run,
    }
    sys.exit(dispatch[args.command](args))


if __name__ == "__main__":
    main()
