---
name: session-isolation
description: Session isolation architecture — namespaced paths, session registry, and git worktree pattern for concurrent Claude Code terminals.
---

# Session Isolation

Two concurrent Claude Code terminals writing to the same `scope.md`, `recipe.json`, or `state.json` corrupt each other's session. This reference documents the isolation architecture: namespaced session directories, a session registry, and the git worktree pattern.

---

## Problem

All session-scoped state currently lives in flat paths:

```
.wabblespec/state/scope.md          <- last writer wins
.wabblespec/state/recipe.json       <- last writer wins
.wabblespec/state/session/state.json  <- last writer wins
```

Two terminals opening simultaneously produce a race condition. The second terminal's Recipe overwrites the first's scope.md mid-execution.

---

## Solution: Namespaced Session Directories

Each session owns its directory under `state/sessions/<session-id>/`:

```
.wabblespec/state/sessions/
  registry.json                          <- session list (session-registry.py manages)
  phase3-new-scripts-20260528/
    scope.md
    recipe.json
    state.json
    checkpoints/
      checkpoint-wave-1.json
```

The canonical flat paths (`state/scope.md`, `state/recipe.json`) remain for single-terminal backward compatibility. Multi-terminal sessions use the namespaced paths.

---

## Session Registry

`session-registry.py` manages `state/sessions/registry.json`:

```bash
# Open a new session:
python .wabblespec/engine/shared/scripts/session-registry.py create \
  --session-id phase4-isolation-20260528 \
  --task-id phase4-isolation-20260528

# List active sessions:
python .wabblespec/engine/shared/scripts/session-registry.py list --active

# Close when done:
python .wabblespec/engine/shared/scripts/session-registry.py close \
  --session-id phase4-isolation-20260528

# Get the session directory path:
python .wabblespec/engine/shared/scripts/session-registry.py path \
  --session-id phase4-isolation-20260528
```

Registry entry schema:

```json
{
  "session_id": "string",
  "task_id": "string",
  "status": "IN_PROGRESS | COMPLETE",
  "created_at": "ISO-8601",
  "completed_at": "ISO-8601 | null",
  "session_dir": "relative path to session directory"
}
```

---

## Git Worktree Pattern (Recommended for Concurrent Sessions)

Claude Code's native isolation mechanism is git worktrees. Each `claude --worktree <name>` session gets its own filesystem checkout. Relative paths are naturally isolated because the sessions are in different directories.

```bash
# Terminal 1: open a worktree session for feature A
git worktree add .worktrees/feature-a main
claude --worktree feature-a

# Terminal 2: open a worktree session for feature B (fully isolated)
git worktree add .worktrees/feature-b main
claude --worktree feature-b

# Cleanup:
git worktree remove .worktrees/feature-a
```

With worktrees, each session has its own `.wabblespec/state/` directory — no shared scope.md, no conflicts. This is the recommended approach for concurrent sessions.

---

## Migration Path

| Phase | State |
|---|---|
| Current | Single flat paths; single terminal; session-registry.py available but opt-in |
| After Phase 4 | Session registry tracks all sessions; namespaced directories created per session; skills read from `session_dir` when `--session-id` is given to session-state.py |
| After Phase 5 | Skills run as subagents in their own context windows; session dirs are isolated by design |

---

## session-state.py Integration

When `session-registry.py create` runs, it creates the session directory. Scripts that write session-scoped state (scope-writer.py, task-card-writer.py, wave-plan-writer.py) should accept a `--session-dir` flag to write into the namespaced path instead of the flat path.

```bash
# Write scope to namespaced path:
python .wabblespec/engine/shared/scripts/scope-writer.py \
  --session-id phase4-isolation-20260528 \
  --session-dir .wabblespec/state/sessions/phase4-isolation-20260528 \
  [other args] \
  --out .wabblespec/state/sessions/phase4-isolation-20260528/scope.md
```

---

## Cross-references

- Session registry script: `.wabblespec/engine/shared/scripts/session-registry.py`
- Session state script: `.wabblespec/engine/shared/scripts/session-state.py`
- Scope writer: `.wabblespec/engine/shared/scripts/scope-writer.py`
- State protocol: `.wabblespec/engine/shared/references/state-protocol.md`
