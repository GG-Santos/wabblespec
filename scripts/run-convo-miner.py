"""
run-convo-miner.py

Auto-ingests Claude Code session transcripts into the WabbleSpec memory store.
Called by the PreCompact hook (--urgent) and optionally the Stop hook.

Usage:
    python scripts/run-convo-miner.py            # mine all unmined sessions
    python scripts/run-convo-miner.py --urgent   # mine only the newest JSONL (fast, for PreCompact)
    python scripts/run-convo-miner.py --dry-run  # show what would be mined without writing

All drawers go to wing_sessions. Room is auto-detected by TOPIC_KEYWORDS
(technical / architecture / planning / decisions / problems / general).

WabbleSpec extends the room vocabulary with additional keywords added at
runtime via WABBLESPEC_ROOM_KEYWORDS so that WabbleSpec-specific terms
(receipt, gate, wave, invariant, etc.) route to the correct rooms.
"""

import argparse
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── Repo path ─────────────────────────────────────────────────────────────────

def _primer() -> pathlib.Path:
    """Minimal bootstrap: add repo root to sys.path so _shared is importable."""
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    print("ERROR: WabbleSpec repo root not found", flush=True)
    sys.exit(1)


_PROJECT_ROOT = _primer()


# ── Imports ────────────────────────────────────────────────────────────────────

try:
    from _shared.memory_backend import TOPIC_KEYWORDS, memory_path, mine_sessions
except ImportError as exc:
    print(f"ERROR: WabbleSpec Memory backend not available: {exc}", flush=True)
    sys.exit(1)


# ── Room keyword extension for WabbleSpec vocabulary ──────────────────────────
# Adds WabbleSpec-specific terms to existing TOPIC_KEYWORDS rooms so that
# session content mentioning receipts, gates, waves, etc. routes correctly.

_WABBLESPEC_EXTENSIONS = {
    "technical": [
        "skill", "module", "executor", "verifier", "guard", "archive",
        "reviewer", "decompose", "specif", "blueprint", "benchmark",
        "synth", "factory",
    ],
    "architecture": [
        "receipt", "drawer", "wing", "memory store", "chromadb", "invariant",
        "staleness", "provenance", "entity-graph", "memory-search",
    ],
    "planning": [
        "wave", "phase", "gate", "task card", "scope", "autopilot",
        "recipe", "dream", "scopeframe",
    ],
    "decisions": [
        "decided", "rationale", "trade-off", "adr", "invariant",
        "chose", "supersed", "breaking", "additive",
    ],
    "problems": [
        "violation", "theater", "gap", "staleness_violation",
        "spec_violation", "fail", "error", "blocked",
    ],
}

for _room, _keywords in _WABBLESPEC_EXTENSIONS.items():
    if _room in TOPIC_KEYWORDS:
        _existing = set(TOPIC_KEYWORDS[_room])
        for _kw in _keywords:
            if _kw not in _existing:
                TOPIC_KEYWORDS[_room].append(_kw)


# ── Session directory resolution ───────────────────────────────────────────────

def _project_slug(project_root: pathlib.Path) -> str:
    """Derive the Claude Code project directory slug from the project path.

    Claude Code replaces every non-alphanumeric character with '-' (no
    collapsing of consecutive dashes).  Example:
        C:\\Vaults\\WabbleSpec v6.1  ->  C--Vaults-WabbleSpec-v6-1
    """
    return "".join(ch if ch.isalnum() else "-" for ch in str(project_root))


def _resolve_session_dir() -> pathlib.Path | None:
    """Find the Claude Code session directory for this project.

    Resolution order (stops at first match):
      1. Slug-based exact lookup -- always correct.
      2. High-confidence partial match (>= 80% character overlap with slug).

    The last-resort 'most-recently-modified' fallback has been intentionally
    removed: it could mine sessions from a different project if multiple
    Claude Code projects are open simultaneously.
    """
    slug = _project_slug(_PROJECT_ROOT)
    claude_projects = pathlib.Path.home() / ".claude" / "projects"

    if not claude_projects.exists():
        return None

    # 1. Exact slug-based lookup.
    primary = claude_projects / slug
    if primary.exists() and list(primary.glob("*.jsonl")):
        return primary

    # 2. High-confidence partial match (>= 80% character overlap).
    best: pathlib.Path | None = None
    best_score = 0
    for d in claude_projects.iterdir():
        if not d.is_dir():
            continue
        score = sum(1 for a, b in zip(d.name, slug) if a == b)
        if score > best_score and list(d.glob("*.jsonl")):
            best_score = score
            best = d

    threshold = len(slug) * 0.8  # raised from 0.7 to reduce wrong-project risk
    if best and best_score >= threshold:
        return best

    print(
        f"WARNING: Could not resolve Claude Code session directory for slug '{slug}'. "
        "Skipping session mining to avoid ingesting wrong-project sessions.",
        flush=True,
    )
    return None


# ── Mining ─────────────────────────────────────────────────────────────────────

def run(urgent: bool = False, dry_run: bool = False) -> int:
    """Run the convo miner. Returns exit code (0 = success)."""
    store_path = memory_path()
    if not store_path:
        print("ERROR: WABBLESPEC_MEMORY_PATH not set", flush=True)
        return 1

    session_dir = _resolve_session_dir()
    if not session_dir:
        return 0

    jsonl_files = sorted(session_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not jsonl_files:
        print(f"WARNING: No JSONL files in {session_dir}", flush=True)
        return 0

    print(f"ConvoMiner: session_dir={session_dir.name}, files={len(jsonl_files)}", flush=True)

    if urgent:
        # PreCompact mode: mine only the newest JSONL (current session)
        print(f"  --urgent: mining newest file only ({jsonl_files[0].name})", flush=True)
        limit = 1
    else:
        limit = 0  # mine all

    try:
        mine_sessions(
            convo_dir=str(session_dir),
            wing="wing_sessions",
            agent="wabblespec",
            limit=limit,
            dry_run=dry_run,
            extract_mode="exchange",
        )
    except Exception as e:
        print(f"ERROR: convo_miner failed: {e}", flush=True)
        return 1

    return 0


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WabbleSpec ConvoMiner -- mine Claude Code sessions into the memory store"
    )
    parser.add_argument(
        "--urgent",
        action="store_true",
        help="Mine only the newest JSONL file (fast path for PreCompact hook)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be mined without writing to ChromaDB",
    )
    args = parser.parse_args()

    sys.exit(run(urgent=args.urgent, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
