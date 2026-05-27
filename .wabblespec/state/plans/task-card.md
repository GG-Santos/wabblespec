# Task Card: wave-checkpoint-v1

**Session ID:** wave-checkpoint-v1
**Created:** 2026-05-26
**Delta class:** ADDITIVE
**Complexity:** Medium
**Status:** LOCKED

---

## Goal

After each Executor wave completes successfully, a checkpoint file is written to `.wabblespec/session/checkpoints/` so that interrupted multi-wave sessions can identify the last completed wave at the next session start without restarting from wave 1.

---

## Non-Goals

- Automatic wave re-execution from checkpoint (requires separate spec)
- Cross-session checkpoint transfer
- Checkpoint expiry or cleanup policy (follow-on)

---

## Assumptions

- Checkpoint files are written only on successful wave completion; failed waves produce no checkpoint
- Guard detection is informational — surfaces last completed wave to human; does not auto-resume
- The checkpoint schema is new; Executor writes, Guard reads, Recipe reads
- Recipe detection is read-only; does not modify session behavior

---

## Acceptance Criteria

### 1 — Executor writes checkpoint on wave completion

Given a wave plan with N waves and wave K completes all steps successfully,
When Executor finishes executing wave K,
Then `.wabblespec/session/checkpoints/checkpoint-wave-K.json` is written.
Then the checkpoint contains: `session_id`, `wave_number`, `wave_receipt_path`, `modules_activated`, `outputs_written`, `timestamp`.
Then the checkpoint validates against `_shared/schemas/wave-checkpoint.schema.json`.

### 2 — No checkpoint written on failed wave

Given a wave plan where wave K fails mid-execution,
When Executor encounters the failure,
Then no `checkpoint-wave-K.json` is written.
Then checkpoints from successfully completed prior waves are not modified.

### 3 — Multiple waves accumulate independent checkpoints

Given a 3-wave plan where waves 1 and 2 complete successfully and wave 3 has not run,
When Executor has completed wave 2,
Then `checkpoint-wave-1.json` and `checkpoint-wave-2.json` both exist.
Then `checkpoint-wave-3.json` does not exist.

### 4 — Guard detects checkpoint at session start

Given `.wabblespec/session/checkpoints/` contains one or more checkpoint files from a prior open session,
When Guard Layer 1 runs at the start of a new execution request,
Then Guard surfaces the last completed wave number (`wave_number` from the highest-numbered checkpoint) to the human before any wave executes.
Then Guard does not auto-resume execution.
Then Guard continues normally after surfacing the checkpoint state.

### 5 — Guard passes cleanly when no checkpoints exist

Given `.wabblespec/session/checkpoints/` is empty or does not exist,
When Guard Layer 1 runs,
Then Guard does not emit any checkpoint-related output.
Then Guard proceeds to Layer 2 normally.

### 6 — Recipe cold-start surfaces checkpoint state

Given checkpoint files exist in `.wabblespec/session/checkpoints/`,
When Recipe runs its cold-start procedure,
Then Recipe includes `checkpoint_detected: true` and `last_checkpoint_wave: N` in its output section.
Then the cold-start output names the last completed wave.

### 7 — Executor authority covers checkpoint path

Given `guard-check.py` is run for the executor module with proposed files including `.wabblespec/session/checkpoints/checkpoint-wave-1.json`,
When Layer 4 authority check runs,
Then the check returns PASS (the path matches a pattern in `executor.authority.owns`).

---

## Files to be Written / Modified

| File | Operation |
|---|---|
| `_shared/schemas/wave-checkpoint.schema.json` | CREATE |
| `modules/l2/executor/SKILL.md` | MODIFY — add checkpoint write step |
| `modules/l2/executor/skill-rules.json` | MODIFY — add authority.owns and produces_schemas |
| `modules/l2/executor/tests/acceptance.md` | MODIFY — add checkpoint criteria |
| `modules/l2/guard/SKILL.md` | MODIFY — add checkpoint detection to Layer 1 |
| `modules/l2/guard/tests/acceptance.md` | MODIFY — update for checkpoint check |
| `modules/l0/recipe/SKILL.md` | MODIFY — surface checkpoint state in cold-start |
| `framework.yaml` | MODIFY — executor schema registration |
