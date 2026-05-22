"""
run-convo-miner.py

Project-scoped ConvoMiner runner for WabbleSpec Stop/PreCompact hooks.
Mines only the current project's Claude Code sessions into wing_sessions.
"""

import argparse
import sys
import os

# Bootstrap MUST be first
sys.path.insert(0, os.path.dirname(__file__))
import wabblespec_mempalace_bootstrap as bootstrap  # noqa: E402

from mempalace.convo_miner import mine_convos  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urgent", action="store_true",
                        help="PreCompact mode — mine immediately, higher priority")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    session_dir = bootstrap.CURRENT_PROJECT_SESSION_DIR
    if not session_dir:
        print("run-convo-miner: no Claude Code session directory found, skipping")
        sys.exit(0)

    if not os.path.exists(session_dir):
        print(f"run-convo-miner: session dir not found ({session_dir}), skipping")
        sys.exit(0)

    print(f"run-convo-miner: mining {session_dir} → {bootstrap.PALACE_PATH}")

    mine_convos(
        convo_dir=session_dir,
        palace_path=bootstrap.PALACE_PATH,
        wing="wing_sessions",
        agent="wabblespec-precompact-hook" if args.urgent else "wabblespec-stop-hook",
        dry_run=args.dry_run,
        extract_mode="exchange",
    )


if __name__ == "__main__":
    main()
