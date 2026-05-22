"""
wabblespec-mempalace-bootstrap.py

Import this FIRST before any other mempalace import.
Redirects all global mempalace paths to .wabblespec/memory/ (project-local).
Scopes ConvoMiner to current project's Claude Code sessions only.

Usage:
    import scripts.wabblespec_mempalace_bootstrap  # noqa: F401 (side effects only)
    from mempalace.palace import Palace
    ...
"""

import base64
import os
from pathlib import Path


def _get_palace_path() -> str:
    """Resolve palace path from env or default to .wabblespec/memory."""
    env = os.environ.get("MEMPALACE_PALACE_PATH")
    if env:
        return os.path.abspath(env)
    # Derive from CWD — find project root (directory containing .wabblespec/)
    cwd = Path.cwd()
    for candidate in [cwd] + list(cwd.parents):
        if (candidate / ".wabblespec").exists():
            return str(candidate / ".wabblespec" / "memory")
    # Fallback: use cwd
    return str(cwd / ".wabblespec" / "memory")


PALACE_PATH = _get_palace_path()

# Ensure palace directory exists
Path(PALACE_PATH).mkdir(parents=True, exist_ok=True)

# Set env var so all mempalace modules that read it get the right value
os.environ["MEMPALACE_PALACE_PATH"] = PALACE_PATH


# ── Monkey-patch module-level path constants ───────────────────────────────────
# These are hardcoded to ~/.mempalace/ in mempalace source. Override after import.

import mempalace.hallways as _hallways
import mempalace.palace_graph as _palace_graph

_hallways._HALLWAY_FILE = os.path.join(PALACE_PATH, "hallways.json")
_palace_graph._TUNNEL_FILE = os.path.join(PALACE_PATH, "tunnels.json")

# Patch hook_state directory for ConvoMiner PID locks
try:
    import mempalace.hooks_cli as _hooks_cli
    _HOOK_STATE_DIR = os.path.join(PALACE_PATH, ".hook_state")
    Path(_HOOK_STATE_DIR).mkdir(parents=True, exist_ok=True)
    # hooks_cli builds hook state path from MEMPALACE_PALACE_PATH — already set above
    # But if it uses a hardcoded ~/.mempalace path, patch it:
    if hasattr(_hooks_cli, "_HOOK_STATE_DIR"):
        _hooks_cli._HOOK_STATE_DIR = _HOOK_STATE_DIR
except ImportError:
    pass


# ── Project-scoped ConvoMiner directory ───────────────────────────────────────
# Claude Code stores sessions under ~/.claude/projects/{project_hash}/
# The hash is derived from the project path. Compute it to scope mining to
# the current project only — prevents cross-project session contamination.

def get_current_project_session_dir() -> str | None:
    """
    Find the Claude Code session directory for the current project.

    Claude Code uses the project's absolute path as the key. The directory
    under ~/.claude/projects/ is named with a URL-safe base64 encoding of
    the path. Try to locate it by checking modification times and content.
    Falls back to the full ~/.claude/projects/ directory if not found.
    """
    claude_projects = Path.home() / ".claude" / "projects"
    if not claude_projects.exists():
        return None

    project_root = PALACE_PATH.replace(os.sep + ".wabblespec" + os.sep + "memory", "")
    project_root = project_root.replace(os.sep + ".wabblespec" + os.sep + "memory", "")

    # Try each encoding variant Claude Code might use
    for encoding in [
        base64.urlsafe_b64encode(project_root.encode()).decode().rstrip("="),
        base64.b64encode(project_root.encode()).decode(),
        base64.urlsafe_b64encode(project_root.encode()).decode(),
    ]:
        candidate = claude_projects / encoding
        if candidate.exists():
            return str(candidate)

    # Fallback: find the most recently modified subdirectory that contains
    # JSONL files (Claude Code session transcripts are JSONL)
    try:
        subdirs = [d for d in claude_projects.iterdir() if d.is_dir()]
        # Find subdirs with JSONL files
        with_jsonl = [
            d for d in subdirs
            if any(d.glob("*.jsonl"))
        ]
        if with_jsonl:
            # Return the most recently modified one as the best guess
            most_recent = max(with_jsonl, key=lambda d: d.stat().st_mtime)
            return str(most_recent)
    except OSError:
        pass

    # Last resort: mine all projects (mempalace default behavior)
    return str(claude_projects)


CURRENT_PROJECT_SESSION_DIR = get_current_project_session_dir()


# ── WabbleSpec wing taxonomy ───────────────────────────────────────────────────
# Override mempalace's default topic wings with WabbleSpec-specific wings.
# These determine how ConvoMiner routes conversation content into rooms.

WABBLESPEC_WINGS = [
    "wing_modules",    # module knowledge, SKILL.md distillations
    "wing_receipts",   # receipt schema, chain patterns, gate decisions
    "wing_specs",      # task cards, spec artifacts, acceptance criteria
    "wing_decisions",  # architecture decisions, trade-off rationale
    "wing_sessions",   # auto-mined from Claude Code conversations
    "wing_problems",   # failure modes, workarounds, error taxonomy
]

WABBLESPEC_HALL_KEYWORDS = {
    "wing_modules": [
        "skill", "module", "layer", "receipt", "executor", "verifier",
        "decompose", "specify", "recipe", "archive", "reviewer"
    ],
    "wing_receipts": [
        "receipt", "PASS", "FAIL", "chain", "upstream", "gate",
        "check", "wave", "staleness", "FRESH", "EXPIRED"
    ],
    "wing_specs": [
        "spec", "task card", "goal", "acceptance", "GWT", "given",
        "when", "then", "EARS", "non-goal", "assumption"
    ],
    "wing_decisions": [
        "decided", "chose", "trade-off", "alternative", "rationale",
        "ADR", "invariant", "because", "instead of"
    ],
    "wing_sessions": [
        "session", "conversation", "claude", "built", "updated", "fixed",
        "added", "removed", "phase", "complete"
    ],
    "wing_problems": [
        "problem", "issue", "error", "failed", "broken", "violation",
        "theater", "gap", "workaround", "blocked"
    ],
}

# Inject into mempalace config — override before MempalaceConfig is instantiated
os.environ.setdefault("MEMPALACE_TOPIC_WINGS", ",".join(WABBLESPEC_WINGS))


# ── Verification ──────────────────────────────────────────────────────────────

def verify_bootstrap() -> dict:
    """Return bootstrap state for debugging."""
    return {
        "palace_path": PALACE_PATH,
        "hallways_file": _hallways._HALLWAY_FILE,
        "tunnels_file": _palace_graph._TUNNEL_FILE,
        "session_dir": CURRENT_PROJECT_SESSION_DIR,
        "wings": WABBLESPEC_WINGS,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify_bootstrap(), indent=2))
