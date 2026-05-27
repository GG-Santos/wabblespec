# Session Scope

**target:** Framework
**complexity:** Medium
**locked_at:** 2026-05-26T00:00:00Z
**session_id:** wave-checkpoint-v1

## In Scope

- `_shared/schemas/wave-checkpoint.schema.json` — new JSON schema for checkpoint files
- `modules/l2/executor/SKILL.md` — add checkpoint write step after each wave completes
- `modules/l2/executor/skill-rules.json` — add `.wabblespec/session/checkpoints/*` to `authority.owns`; add `wave-checkpoint.schema.json` to `produces_schemas`
- `modules/l2/executor/tests/acceptance.md` — add acceptance criteria for checkpoint write
- `modules/l2/guard/SKILL.md` — add checkpoint detection to Layer 1 schema check
- `modules/l2/guard/tests/acceptance.md` — update for checkpoint detection
- `modules/l0/recipe/SKILL.md` — surface checkpoint state in cold-start output
- `framework.yaml` — update executor `produces_schemas`, `authority.owns`; add schema to shared.schemas

## Out of Scope

- Automatic wave re-execution from checkpoint (separate spec)
- Cross-session checkpoint transfer
- Checkpoint expiry or cleanup policy (follow-on)
- Executor `skill-rules.json` changes beyond `authority.owns` and `produces_schemas`

## Assumptions

- Checkpoint files are written only when a wave completes successfully; failed waves produce no checkpoint
- Checkpoint detection in Guard is informational — Guard surfaces the last wave to the human but does not auto-resume
- The checkpoint schema is a new shared artifact consumed by Executor (writes) and Guard (reads)
- Recipe cold-start detection is read-only; it surfaces checkpoint state without modifying session behavior

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
