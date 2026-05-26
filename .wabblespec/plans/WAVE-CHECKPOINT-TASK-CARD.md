# Task Card: Wave Checkpoint — Executor Mid-Wave State Persistence

**Task ID:** wave-checkpoint-v1  
**Created:** 2026-05-25  
**Status:** PLANNED — awaiting Specify pass  
**Complexity estimate:** Medium (L2 — requires Specify before Decompose)  
**Delta class:** ADDITIVE  

---

## Problem Statement

Multi-wave executions have no checkpoint between waves. If a session crashes or is interrupted after wave N completes but before wave N+1 begins, the next session has no recovery point. It must restart from wave 1 or rely on Rollback to restore a prior snapshot — both are more disruptive than resuming from the last completed wave.

The current session state file (`.wabblespec/session/state.json`) is a single live file with no history. Rollback requires a prior worktree snapshot. Neither provides wave-granular recovery.

## Proposed Behavior

After each wave completes successfully, Executor writes a checkpoint file:

```
.wabblespec/session/checkpoints/checkpoint-wave-{N}.json
```

The checkpoint contains: session ID, wave number, wave receipt path, modules activated, outputs written, timestamp.

On Recipe cold-start for a task that has an open session, Guard Layer 1 checks for checkpoint files. If found, surfaces the last completed wave to the human before proceeding. Executor can optionally resume from checkpoint rather than re-running completed waves.

## Scope

**In scope:**
- Executor: checkpoint write after each wave completion
- Guard: checkpoint detection in Layer 1 schema check
- New schema: `wave-checkpoint.schema.json` in `_shared/schemas/`
- Recipe: surface checkpoint state in cold-start output

**Out of scope:**
- Automatic wave re-execution from checkpoint (requires separate spec)
- Cross-session checkpoint transfer
- Checkpoint expiry / cleanup policy (follow-on)

## Files Affected

- `modules/l2/executor/SKILL.md` — add checkpoint write step
- `modules/l2/guard/SKILL.md` — add checkpoint detection to Layer 1
- `modules/l0/recipe/SKILL.md` — surface checkpoint state if present
- `_shared/schemas/wave-checkpoint.schema.json` — new schema
- `modules/l2/executor/tests/acceptance.md` — new acceptance criteria
- `modules/l2/guard/tests/acceptance.md` — update for checkpoint check
- `framework.yaml` — update executor + guard `consumes_schemas`

## Gate Requirements

- Specify pass required before Decompose (I1)
- Acceptance tests required before Executor writes execution receipt (0.7.0 gate)
- Guard and Executor both require Verifier PASS before Archive
- This task does NOT enter the L8 evolution chain — it is a direct ADDITIVE build task

## Not Tested (at time of card creation)

- Recovery path (resuming from checkpoint rather than restarting)
- Checkpoint file cleanup after successful archive
- Behavior when checkpoint files exist but session.json is absent

---

*This card was created from a pattern identified in the Ruflo reference evaluation (2026-05-25).  
The pattern: periodic state snapshots for wave-level recovery. Verified against WabbleSpec's  
own reliability gap (no mid-wave recovery point). Requires normal pipeline execution to proceed.*
