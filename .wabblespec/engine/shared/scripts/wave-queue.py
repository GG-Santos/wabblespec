"""
wave-queue.py — File-locked task queue for parallel wave execution.

Wave tasks are written to a JSON queue file. Multiple background worker
subagents claim tasks from the queue via file locking. Wave N+1 is released
only when all Wave N items have status=PASS.

Queue file: .wabblespec/state/queue/wave-queue.json
Lock file:  .wabblespec/state/queue/wave-queue.lock

Usage:
    # Populate queue from wave plan (run by Orchestrator before starting workers):
    python .wabblespec/engine/shared/scripts/wave-queue.py populate \\
        --session-id phase9-parallel-20260528 \\
        --wave-plan .wabblespec/state/plans/current-wave-plan.md

    # Claim next available task (run by a worker subagent):
    python .wabblespec/engine/shared/scripts/wave-queue.py claim \\
        --worker-id worker-1

    # Complete a claimed task (run by worker after wave succeeds):
    python .wabblespec/engine/shared/scripts/wave-queue.py complete \\
        --task-id wave-1-task-a \\
        --worker-id worker-1 \\
        --receipt-path .wabblespec/state/receipts/wave-1a-receipt.json

    # Fail a claimed task (worker encountered a blocking error):
    python .wabblespec/engine/shared/scripts/wave-queue.py fail \\
        --task-id wave-1-task-a \\
        --worker-id worker-1 \\
        --reason "Verification FAIL after 3 REVISE cycles"

    # Check if a wave number is fully complete (all tasks PASS):
    python .wabblespec/engine/shared/scripts/wave-queue.py wave-done \\
        --wave 1
    # Exit 0 = done, 1 = pending tasks remain, 2 = any task FAIL

    # Show queue status:
    python .wabblespec/engine/shared/scripts/wave-queue.py status

    # Clear the queue (run by Orchestrator after all waves complete):
    python .wabblespec/engine/shared/scripts/wave-queue.py clear

Exit codes:
    0  success / done
    1  no task available / wave not done / bad args
    2  lock timeout / queue not found / worker error
"""

import sys
import os
import json
import time
import argparse
import re
from datetime import datetime, timezone


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
LOCK_TIMEOUT = 5  # seconds
QUEUE_SCHEMA = 1


def find_repo_root(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        if os.path.isdir(os.path.join(candidate, ".wabblespec")):
            return candidate
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def queue_dir(repo_root):
    return os.path.join(repo_root, ".wabblespec", "state", "queue")


def queue_path(repo_root):
    return os.path.join(queue_dir(repo_root), "wave-queue.json")


def lock_path(repo_root):
    return os.path.join(queue_dir(repo_root), "wave-queue.lock")


class FileLock:
    """Simple file-based lock for cross-process queue access."""

    def __init__(self, path, timeout=LOCK_TIMEOUT):
        self.path = path
        self.timeout = timeout
        self._acquired = False

    def __enter__(self):
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                time.sleep(0.1)
        raise TimeoutError(f"Could not acquire lock {self.path} within {self.timeout}s")

    def __exit__(self, *_):
        if self._acquired and os.path.isfile(self.path):
            os.unlink(self.path)
            self._acquired = False


def load_queue(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_queue(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def extract_waves_from_plan(plan_path):
    """Parse current-wave-plan.md and return list of wave dicts."""
    with open(plan_path, encoding="utf-8") as fh:
        content = fh.read()
    waves = []
    # Match ### Wave N: label
    pattern = re.compile(r"### Wave (\d+): (.+)")
    for m in pattern.finditer(content):
        waves.append({"wave_number": int(m.group(1)), "label": m.group(2).strip()})
    return waves


def cmd_populate(args, repo_root):
    qdir = queue_dir(repo_root)
    os.makedirs(qdir, exist_ok=True)
    qp = queue_path(repo_root)
    lp = lock_path(repo_root)

    waves = extract_waves_from_plan(args.wave_plan)
    if not waves:
        print("ERROR: No waves found in wave plan.", file=sys.stderr)
        sys.exit(1)

    tasks = []
    for w in waves:
        task_id = f"wave-{w['wave_number']}-{args.session_id}"
        tasks.append({
            "task_id": task_id,
            "session_id": args.session_id,
            "wave_number": w["wave_number"],
            "wave_label": w["label"],
            "status": "PENDING",
            "worker_id": None,
            "claimed_at": None,
            "completed_at": None,
            "receipt_path": None,
            "failure_reason": None,
        })

    queue = {
        "schema_version": QUEUE_SCHEMA,
        "session_id": args.session_id,
        "created_at": NOW,
        "tasks": tasks,
    }

    try:
        with FileLock(lp):
            save_queue(qp, queue)
    except TimeoutError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"Populated queue: {len(tasks)} wave tasks for session {args.session_id}")


def cmd_claim(args, repo_root):
    qp = queue_path(repo_root)
    lp = lock_path(repo_root)
    if not os.path.isfile(qp):
        print("ERROR: Queue not found. Run 'populate' first.", file=sys.stderr)
        sys.exit(2)

    try:
        with FileLock(lp):
            queue = load_queue(qp)
            # Find lowest-wave PENDING task where all prior waves are PASS
            tasks = queue["tasks"]
            # Group by wave number
            waves_done = set()
            for t in tasks:
                wn = t["wave_number"]
                prior = [x for x in tasks if x["wave_number"] < wn]
                if all(x["status"] == "PASS" for x in prior) or not prior:
                    waves_done.add(wn)

            # Claim first PENDING task in a releasable wave
            claimed = None
            for t in tasks:
                if t["status"] == "PENDING" and t["wave_number"] in waves_done:
                    t["status"] = "IN_PROGRESS"
                    t["worker_id"] = args.worker_id
                    t["claimed_at"] = NOW
                    claimed = dict(t)
                    break

            if claimed:
                save_queue(qp, queue)
    except TimeoutError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if not claimed:
        print("NO_TASK_AVAILABLE")
        sys.exit(1)

    print(json.dumps(claimed, indent=2))


def cmd_complete(args, repo_root):
    qp = queue_path(repo_root)
    lp = lock_path(repo_root)
    try:
        with FileLock(lp):
            queue = load_queue(qp)
            for t in queue["tasks"]:
                if t["task_id"] == args.task_id:
                    if t["worker_id"] != args.worker_id:
                        print(f"ERROR: Task claimed by {t['worker_id']}, not {args.worker_id}",
                              file=sys.stderr)
                        sys.exit(1)
                    t["status"] = "PASS"
                    t["completed_at"] = NOW
                    t["receipt_path"] = args.receipt_path
                    break
            else:
                print(f"ERROR: Task '{args.task_id}' not found.", file=sys.stderr)
                sys.exit(1)
            save_queue(qp, queue)
    except TimeoutError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Completed: {args.task_id}")


def cmd_fail(args, repo_root):
    qp = queue_path(repo_root)
    lp = lock_path(repo_root)
    try:
        with FileLock(lp):
            queue = load_queue(qp)
            for t in queue["tasks"]:
                if t["task_id"] == args.task_id:
                    t["status"] = "FAIL"
                    t["completed_at"] = NOW
                    t["failure_reason"] = args.reason
                    break
            else:
                print(f"ERROR: Task '{args.task_id}' not found.", file=sys.stderr)
                sys.exit(1)
            save_queue(qp, queue)
    except TimeoutError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Failed: {args.task_id}")


def cmd_wave_done(args, repo_root):
    qp = queue_path(repo_root)
    if not os.path.isfile(qp):
        print("ERROR: Queue not found.", file=sys.stderr)
        sys.exit(2)
    queue = load_queue(qp)
    wave_tasks = [t for t in queue["tasks"] if t["wave_number"] == args.wave]
    if not wave_tasks:
        print(f"Wave {args.wave}: no tasks found.")
        sys.exit(1)
    if any(t["status"] == "FAIL" for t in wave_tasks):
        print(f"Wave {args.wave}: FAIL — {sum(1 for t in wave_tasks if t['status']=='FAIL')} tasks failed")
        sys.exit(2)
    if all(t["status"] == "PASS" for t in wave_tasks):
        print(f"Wave {args.wave}: DONE — all {len(wave_tasks)} tasks PASS")
        sys.exit(0)
    pending = sum(1 for t in wave_tasks if t["status"] in ("PENDING", "IN_PROGRESS"))
    print(f"Wave {args.wave}: {pending} tasks still pending")
    sys.exit(1)


def cmd_status(args, repo_root):
    qp = queue_path(repo_root)
    if not os.path.isfile(qp):
        print("No queue found.")
        return
    queue = load_queue(qp)
    print(f"Session: {queue.get('session_id')} | Created: {queue.get('created_at')}")
    print(f"{'TASK ID':<45} {'WAVE':<6} {'STATUS':<12} {'WORKER'}")
    print("-" * 80)
    for t in queue["tasks"]:
        print(f"{t['task_id']:<45} {t['wave_number']:<6} {t['status']:<12} {t['worker_id'] or '-'}")


def cmd_clear(args, repo_root):
    qp = queue_path(repo_root)
    if os.path.isfile(qp):
        os.unlink(qp)
        print("Queue cleared.")
    else:
        print("No queue to clear.")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_pop = sub.add_parser("populate")
    p_pop.add_argument("--session-id", required=True)
    p_pop.add_argument("--wave-plan", required=True, metavar="PATH")

    p_claim = sub.add_parser("claim")
    p_claim.add_argument("--worker-id", required=True)

    p_done = sub.add_parser("complete")
    p_done.add_argument("--task-id", required=True)
    p_done.add_argument("--worker-id", required=True)
    p_done.add_argument("--receipt-path", required=True)

    p_fail = sub.add_parser("fail")
    p_fail.add_argument("--task-id", required=True)
    p_fail.add_argument("--worker-id", required=True)
    p_fail.add_argument("--reason", default="")

    p_wd = sub.add_parser("wave-done")
    p_wd.add_argument("--wave", type=int, required=True)

    sub.add_parser("status")
    sub.add_parser("clear")

    args = parser.parse_args()
    repo_root = find_repo_root()
    if not repo_root:
        print("ERROR: Cannot find repo root.", file=sys.stderr)
        sys.exit(2)

    dispatch = {
        "populate": cmd_populate,
        "claim": cmd_claim,
        "complete": cmd_complete,
        "fail": cmd_fail,
        "wave-done": cmd_wave_done,
        "status": cmd_status,
        "clear": cmd_clear,
    }
    dispatch[args.command](args, repo_root)


if __name__ == "__main__":
    main()
