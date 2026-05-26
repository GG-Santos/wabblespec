# Executor (Augment) — Acceptance Criteria

Includes all original acceptance criteria plus new criteria for the module-build acceptance gate.

---

## BLOCK: absent decompose-receipt.json

Given `decompose-receipt.json` is missing,
When Executor is invoked,
Then Executor surfaces: "Executor requires decompose-receipt.json — cannot start without plan receipt (I10)."
Then Executor does not begin any wave.
Then no state.json is written.

---

## BLOCK: wave awaiting Attestation

Given a wave is currently blocked awaiting Attestation,
When Executor is invoked,
Then Executor does not start new waves.
Then Executor surfaces the blocked state and awaits human resolution.

---

## Pre-execution prologue

Given decompose-receipt.json exists and Executor starts,
When Executor writes the enforcement prologue,
Then `.wabblespec/session/state.json` is written with `enforcement_active: true`.
Then `required_receipts` lists all planning chain receipts.
Then `active_module` is set to "executor".

---

## Checkpoint before Guard (each wave)

Given a wave is about to begin,
When Executor prepares,
Then a checkpoint is saved to `.wabblespec/checkpoints/wave-<N>-<timestamp>/` before Guard runs.
Then `checkpoint-meta.json` records wave number, timestamp, and files to be touched.
Then the checkpoint is the rollback target for that wave.

---

## Guard PASS required before implementation

Given Guard is invoked for a wave,
When Guard returns a PASS receipt,
Then Executor appends `guard-wave-<N>` to `required_receipts` in state.json.
Then Executor proceeds to implementation.

Given Guard returns a HARD error,
Then Executor aborts the wave and does not proceed.

Given Guard returns SPEC_VIOLATION,
Then Executor pauses and surfaces the violation to the user.

---

## BREAKING deviation halts wave

Given a BREAKING deviation is discovered mid-wave,
When Executor detects it,
Then Executor stops immediately and surfaces to user.
Then Executor loops back to Specify before continuing.
Then the wave is not marked complete.

---

## ADDITIVE/COSMETIC deviations proceed

Given an ADDITIVE or COSMETIC deviation is found,
When Executor continues the wave,
Then the deviation is documented in the wave receipt under `deviations_found`.
Then the wave is not halted.

---

## Verifier PASS advances wave

Given Verifier returns PASS for a wave,
When Executor records the result,
Then the wave receipt is written to `.wabblespec/receipts/wave-<N>-receipt.json`.
Then `wave-<N>` and the verification receipt stem are appended to `required_receipts` in state.json.
Then Executor advances to the next wave.

---

## Verifier FAIL enters REVISE loop

Given Verifier returns FAIL,
When Executor enters the REVISE loop,
Then Executor applies the specific fix identified by Verifier.
Then Executor re-runs Verifier (max 3 cycles).
Then if all 3 cycles fail, the wave is BLOCKED and surfaced to user for Attestation.

---

## PASS: module-build task with acceptance file present

Given the task-card declares `task_type: module-build` with `target_module: {layer, module_id}`,
And `modules/{layer}/{module_id}/tests/acceptance.md` exists,
When all waves complete and Executor runs the acceptance gate check,
Then Executor proceeds to write `execution-receipt.json` with `acceptance_verified: true`.
Then Executor signals Archive.

---

## BLOCK: module-build task with acceptance file absent (AUGMENT)

Given the task-card declares `task_type: module-build` with `target_module: {layer, module_id}`,
And `modules/{layer}/{module_id}/tests/acceptance.md` does not exist,
When all waves complete and Executor runs the acceptance gate check,
Then Executor emits ACCEPTANCE_NOT_COVERED (SPEC_VIOLATION).
Then Executor does not write `execution-receipt.json`.
Then Executor does not signal Archive.
Then Executor surfaces: "Module build task cannot be marked complete — tests/acceptance.md is missing at {path}. Author acceptance tests before re-running."
Then the task loops back to acceptance test authorship.

---

## PASS: non-module-build task bypasses acceptance gate (AUGMENT)

Given the task-card declares any `task_type` other than `module-build`,
When all waves complete,
Then Executor does not check for `tests/acceptance.md`.
Then Executor writes `execution-receipt.json` with `acceptance_verified: null`.
Then Executor signals Archive normally.

---

## DO NOT suppress ACCEPTANCE_NOT_COVERED

Given a module-build task where acceptance.md is absent,
Then Executor does not write execution-receipt.json regardless of task urgency or human override request.
Then the acceptance file must be authored before the task can be receipted complete.

---

## Final execution receipt

Given all waves complete and acceptance gate passes (or is not applicable),
When Executor signals Archive,
Then the final execution receipt is written to `.wabblespec/receipts/execution-receipt.json`.
Then `waves_planned`, `waves_completed`, `waves_failed`, `rollbacks_triggered`, `acceptance_verified`, and `errors_by_type` are all populated.

---

## Error routing

Given a SOFT error occurs during a wave,
Then Executor retries once; if retry fails, escalates to HARD.

Given a HARD error occurs,
Then Executor halts the wave and invokes human-confirmed rollback to the prior checkpoint.

Given a CONTEXT_EXHAUSTION error occurs,
Then Executor compresses context and resumes from the last saved checkpoint.

Given a STALENESS_VIOLATION error occurs,
Then Executor quarantines the expired evidence and surfaces for fresh fetch before continuing.

---

## DO NOT

Given any Executor run,
Then Executor does not write the wave plan (that is Decompose's role).
Then Executor does not implement code directly (implementation step produces the artifacts).
Then Executor does not proceed past a Guard FAIL under any circumstance.
Then Executor does not produce artifacts outside the declared `outputs` list without documenting a deviation.
