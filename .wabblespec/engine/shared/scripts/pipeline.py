"""
pipeline.py — Orchestrate WabbleSpec session boundaries via script composition.

Composes existing scripts into two primary entry points (start, close) plus
auxiliary subcommands. All scripts are invoked via subprocess — no shared imports —
so each remains independently testable.

Subcommands:
    start   Open a session: recipe + session-state init + drift check
    close   Close a session: chain validate + archive + witness + index-update + state complete
    status  Show current session state and receipt chain status
    guard   Layer 4+5 pre-wave check (delegates to guard-check.py)

Usage:
    # Open a session:
    python .wabblespec/engine/shared/scripts/pipeline.py start \\
        --session-id seed-run-20260526xx \\
        --target Framework \\
        --complexity Low \\
        --confidence 0.97 \\
        --detection-method explicit-instruction

    # Close a session:
    python .wabblespec/engine/shared/scripts/pipeline.py close \\
        --session-id seed-run-20260526xx \\
        --summary "Built foo.md and bar.md" \\
        --delta-class ADDITIVE \\
        --files-delivered ".wabblespec/engine/shared/references/foo.md" ".wabblespec/engine/shared/references/bar.md"

    # Close with optional args:
    python .wabblespec/engine/shared/scripts/pipeline.py close \\
        --session-id seed-run-20260526xx \\
        --summary "..." \\
        --delta-class ADDITIVE \\
        --files-delivered "path/to/file.md" \\
        --not-tested "item A" "item B" \\
        --extra '{"total_receipts_accumulated": 102}'

    # Show session status:
    python .wabblespec/engine/shared/scripts/pipeline.py status

    # Pre-wave guard check:
    python .wabblespec/engine/shared/scripts/pipeline.py guard \\
        --module executor \\
        --files ".wabblespec/state/receipts/wave-1-receipt.json" \\
        --commands "git add -A" "python validate.py"

    # Dry run (start or close):
    python .wabblespec/engine/shared/scripts/pipeline.py start ... --dry-run
    python .wabblespec/engine/shared/scripts/pipeline.py close ... --dry-run

Exit codes:
    0  all steps succeeded
    1  a step failed (named in output)
    2  configuration error (missing script or bad args)
"""

import sys
import os
import json
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Script runner
# ---------------------------------------------------------------------------

def run(script_name, args_list, dry_run=False, capture=False):
    """
    Run a script from SCRIPT_DIR with given args.
    Returns (exit_code, stdout, stderr).
    If dry_run, prepends --dry-run to args if the script supports it.
    """
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.isfile(script_path):
        return 2, "", f"Script not found: {script_path}"

    cmd = [sys.executable, script_path] + list(args_list)
    if dry_run and "--dry-run" not in args_list:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
        )
        stdout = result.stdout if capture else ""
        stderr = result.stderr if capture else ""
        return result.returncode, stdout, stderr
    except Exception as e:
        return 2, "", f"Failed to run {script_name}: {e}"


def run_show(script_name, args_list):
    """Run a script with captured output for display."""
    return run(script_name, args_list, capture=True)


def step(label, script_name, args_list, dry_run=False, fatal=True):
    """
    Run one pipeline step. Print label and result.
    Returns True if step succeeded, False otherwise.
    If fatal=True, any failure causes sys.exit(1).
    """
    print(f"\n[{label}]")
    code, stdout, stderr = run(script_name, args_list, dry_run=dry_run)

    if stdout:
        for line in stdout.strip().splitlines():
            print(f"  {line}")
    if stderr and code != 0:
        for line in stderr.strip().splitlines():
            print(f"  ERR: {line}")

    if code == 0:
        print(f"  -> PASS (exit {code})")
        return True
    else:
        print(f"  -> FAIL (exit {code})")
        if fatal:
            sys.exit(1)
        return False


# ---------------------------------------------------------------------------
# start
# ---------------------------------------------------------------------------

def cmd_start(args):
    print(f"=== pipeline start: {args.session_id} ===")

    # Step 1: recipe-writer.py
    recipe_args = [
        "--session-id", args.session_id,
        "--target", args.target,
        "--complexity", args.complexity,
        "--confidence", str(args.confidence),
        "--detection-method", args.detection_method,
    ]
    if args.platform:
        recipe_args += ["--platform", args.platform]
    step("Recipe", "recipe-writer.py", recipe_args, dry_run=args.dry_run)

    # Step 2: session-state.py init
    session_args = ["init", "--session-id", args.session_id]
    if args.force or args.dry_run:
        # --force needed in dry-run to avoid failing on existing state
        # (dry-run doesn't write anyway, so force-reinit is harmless)
        session_args.append("--force")
    step("Session Init", "session-state.py", session_args, dry_run=args.dry_run)

    # Step 3: validate-graph.py --check-hashes (informational — non-fatal)
    print(f"\n[Drift Check]")
    code, stdout, stderr = run(
        "validate-graph.py", ["--check-hashes"], capture=True
    )
    if stdout:
        for line in stdout.strip().splitlines():
            print(f"  {line}")
    if code == 0:
        print("  -> No drift detected (exit 0)")
    else:
        print(f"  -> WARN: drift detected or check failed (exit {code})")
        if stderr:
            for line in stderr.strip().splitlines():
                print(f"  ERR: {line}")

    print(f"\n=== start complete: {args.session_id} ===")
    if not args.dry_run:
        print(f"  recipe.json written, session state initialized.")


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------

def cmd_close(args):
    print(f"=== pipeline close: {args.session_id} ===")

    # Step 1: receipt-chain-validate.py (fatal — block archive on incomplete chain)
    chain_args = ["--session-id", args.session_id]
    step("Chain Validate", "receipt-chain-validate.py", chain_args, dry_run=False, fatal=True)

    # Step 2: archive.py
    archive_args = [
        "--session-id", args.session_id,
        "--summary", args.summary,
        "--delta-class", args.delta_class,
    ]
    for f in (args.files_delivered or []):
        archive_args += ["--files-delivered", f]
    for nt in (args.not_tested or []):
        archive_args += ["--not-tested", nt]
    if args.extra:
        archive_args += ["--extra", args.extra]
    step("Archive", "archive.py", archive_args, dry_run=args.dry_run, fatal=True)

    # Step 3: validate-graph.py --record-witness (informational — non-fatal)
    print("\n[Witness Update]")
    code, stdout, stderr = run(
        "validate-graph.py", ["--record-witness"], capture=True, dry_run=args.dry_run
    )
    if stdout:
        for line in stdout.strip().splitlines():
            print(f"  {line}")
    if code == 0:
        print("  -> Witness updated (exit 0)")
    else:
        print(f"  -> WARN: witness update failed (exit {code})")

    # Step 4: index-update.py
    index_args = []
    step("Index Update", "index-update.py", index_args, dry_run=args.dry_run, fatal=False)

    # Step 5: session-state.py complete
    state_args = ["complete", "--task", args.summary]
    step("Session Complete", "session-state.py", state_args, dry_run=args.dry_run, fatal=False)

    print(f"\n=== close complete: {args.session_id} ===")


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def cmd_status(args):
    print("=== pipeline status ===")

    # Session state
    print("\n[Session State]")
    code, stdout, stderr = run_show("session-state.py", ["show"])
    if code == 0:
        for line in stdout.strip().splitlines():
            print(f"  {line}")
    else:
        print("  No active session state.")

    # Receipt chain (all sessions, brief)
    print("\n[Receipt Chain]")
    code, stdout, stderr = run_show("receipt-chain-validate.py", ["--all"])
    if stdout:
        for line in stdout.strip().splitlines():
            print(f"  {line}")

    # Version
    print("\n[Version]")
    code, stdout, stderr = run_show("version-bump.py", ["--show"])
    if stdout:
        print(f"  {stdout.strip()}")


# ---------------------------------------------------------------------------
# guard
# ---------------------------------------------------------------------------

def cmd_guard(args):
    guard_args = ["wave", "--module", args.module]
    if args.files:
        guard_args.append("--files")
        guard_args.extend(args.files)
    if args.commands:
        guard_args.append("--commands")
        guard_args.extend(args.commands)
    if args.wave_files:
        guard_args.append("--wave-files")
        guard_args.extend(args.wave_files)
    if args.json:
        guard_args.append("--json")

    code, stdout, stderr = run("guard-check.py", guard_args, capture=args.json)
    if args.json and stdout:
        print(stdout, end="")
    sys.exit(code)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate WabbleSpec session boundaries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = sub.add_parser("start", help="Open a session.")
    p_start.add_argument("--session-id", required=True, dest="session_id")
    p_start.add_argument("--target", required=True,
                         choices=["Framework", "Script", "Web", "API-Service", "CLI",
                                  "Mobile", "Desktop", "Library-Package", "Extension-Plugin",
                                  "Data-Pipeline", "AI-Agent", "Game", "IoT-Embedded", "ALL"])
    p_start.add_argument("--complexity", required=True, choices=["Low", "Medium", "High"])
    p_start.add_argument("--confidence", type=float, default=0.97)
    p_start.add_argument("--detection-method", default="explicit-instruction",
                         dest="detection_method",
                         choices=["explicit-instruction", "file-signals",
                                  "prior-session", "complexity-scorer"])
    p_start.add_argument("--platform", metavar="TEXT")
    p_start.add_argument("--force", action="store_true",
                         help="Reinitialize session state if it already exists.")
    p_start.add_argument("--dry-run", action="store_true")

    # close
    p_close = sub.add_parser("close", help="Close a session.")
    p_close.add_argument("--session-id", required=True, dest="session_id")
    p_close.add_argument("--summary", required=True,
                         help="One-line description of what was built.")
    p_close.add_argument("--delta-class", required=True,
                         choices=["BREAKING", "ADDITIVE", "COSMETIC"], dest="delta_class")
    p_close.add_argument("--files-delivered", nargs="*", metavar="PATH",
                         dest="files_delivered")
    p_close.add_argument("--not-tested", nargs="*", metavar="ITEM", dest="not_tested")
    p_close.add_argument("--extra", metavar="JSON",
                         help='Extra fields as JSON string, e.g. \'{"key": "val"}\'.')
    p_close.add_argument("--dry-run", action="store_true")

    # status
    sub.add_parser("status", help="Show current session state and chain status.")

    # guard
    p_guard = sub.add_parser("guard", help="Pre-wave Layer 4+5 check.")
    p_guard.add_argument("--module", required=True)
    p_guard.add_argument("--files", nargs="*", default=[])
    p_guard.add_argument("--commands", nargs="*", default=[])
    p_guard.add_argument("--wave-files", nargs="*", dest="wave_files")
    p_guard.add_argument("--json", action="store_true", dest="json")

    args = parser.parse_args()
    if not hasattr(args, "dry_run"):
        args.dry_run = False

    dispatch = {
        "start": cmd_start,
        "close": cmd_close,
        "status": cmd_status,
        "guard": cmd_guard,
    }
    dispatch[args.command](args)
    sys.exit(0)


if __name__ == "__main__":
    main()
