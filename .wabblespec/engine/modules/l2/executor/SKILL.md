---
name: executor
description: Wave execution engine. Reads the locked wave plan, runs Guard before each wave, saves checkpoints, invokes Verifier after each wave, routes errors by type, and writes receipts throughout. On module-build tasks, verifies tests/acceptance.md exists before writing the final execution receipt.
promoted_from: acceptance-test-executor-enforcement-v1
promoted_at: 2026-05-25T09:12:00+00:00
---

# Executor

You run the plan. You do not write the plan and you do not implement the code — Decompose writes the plan and the implementation step produces the code. You orchestrate: checkpoint → Guard → implement → Verify, wave by wave, with error routing at every step.

## What this skill does

Works through the wave plan from Decompose, wave by wave in order. Before each wave: saves a checkpoint, runs Guard. After implementation: invokes Verifier with the declared mode. Handles errors by type. Writes wave receipts and a final execution receipt. On module-build tasks, checks that tests/acceptance.md exists for the built module before writing the execution receipt. Signals Archive when complete.

## When to use / when not to use

**Use when:**
- Wave plan is locked (decompose-receipt.json exists, Reviewer ACCEPT)
- Explicit `/execute` command with wave plan path
- Resuming from checkpoint after DEPENDENCY or CONTEXT_EXHAUSTION error

**Do not use when:**
- `decompose-receipt.json` is missing — cannot start without plan receipt (I10)
- Any wave is currently blocked awaiting Attestation

## Inputs

- `.wabblespec/state/plans/current-wave-plan.md` (locked wave plan)
- `.wabblespec/state/plans/task-card.md` (spec ground truth)
- `.wabblespec/scope.md`
- All prior wave receipts (for I10 chain)

## How to do it

### Pre-execution prologue (once, before Wave 1)

Before any wave begins, confirm `decompose-receipt.json` exists. Then write the enforcement prologue to `.wabblespec/state/session/state.json`:

```json
{
  "enforcement_active": true,
  "required_receipts": ["recipe-receipt", "scopeframe-receipt", "specify-receipt", "decompose-receipt"],
  "active_module": "executor",
  "evidence_drawers": ["<paths to any loaded evidence drawers for this task>"]
}
```

This arms the pre-tool-use hook. From this point forward, any Edit/Write/Bash call requires the planning chain receipts to exist. If they do not, the hook blocks before you can proceed.

If evidence drawers are not yet known, set `evidence_drawers: []` and update per-wave as drawers are loaded.

### For each wave in order:

**0. Update state.json for this wave**

Before the checkpoint, write the current wave into state.json:

```json
{
  "active_module": "executor-wave-<N>",
  "required_receipts": ["recipe-receipt", "scopeframe-receipt", "specify-receipt", "decompose-receipt", "<guard-wave-M-receipt, wave-M-receipt, verification-wave-M-* for each completed wave M>"]
}
```

Preserve all other fields. Do not reset `enforcement_active` to false.

**1. Establish rollback reference**

The locked wave plan at `.wabblespec/state/plans/current-wave-plan.md` is the rollback ground truth for this wave. It already declares which files this wave will touch under its `outputs` list. No pre-wave directory snapshot is written. If this wave must be rolled back, revert all files listed under this wave in `current-wave-plan.md` to their pre-wave state using git or manual revert.

**2. Run Guard**

Pass wave inputs to Guard. Wait for Guard receipt with `overall: "PASS"`. If Guard returns an error:
- HARD → abort wave, do not proceed
- SPEC_VIOLATION → surface to user, pause execution pending resolution
- DEPENDENCY → surface upstream failure, pause and await resolution

Never proceed past Guard without a PASS receipt.

After Guard returns PASS, append `"guard-wave-<N>"` to `required_receipts` in state.json before proceeding to implementation.

**2b. Optional: Context7 enrichment**

If `context7.available: true` in `.wabblespec/state/runtime/runtime-state.json`, and the wave implementation involves a named library or framework not covered by `.wabblespec/engine/shared/dev/`, use context7 to fetch the relevant API surface before implementing:

- MCP path: `resolve-library-id` → `get-library-docs` with targeted topic
- CLI path: `ctx7 <library-name>` piped to the relevant section
- Load only the section the wave plan names — not full docs

If runtime-state.json is absent, stale, or context7 is unavailable: skip silently. If the ctx7 call fails: skip silently, log in wave receipt under `context7_enrichment.status: "failed"`. Do not emit a typed error. Do not increment the REVISE counter. If context budget tier is DEGRADING or POOR: skip context7 regardless of availability.

See `.wabblespec/engine/shared/references/context7-integration.md` for full call patterns and receipt field spec.

**3. Implement the wave**

Produce the artifacts declared in the wave plan's `outputs` list. Work within scope.md boundaries. Produce exactly what was declared — no more, no less.

If a deviation is discovered mid-wave:
- ADDITIVE or COSMETIC deviation: document in wave receipt under `deviations_found`, continue
- BREAKING deviation: stop immediately, surface to user, loop back to Specify before continuing

**4. Run Verifier**

Invoke Verifier with: wave output artifacts + wave plan entry + task card. Verifier uses the `verification_mode` declared in the wave plan for this wave.

Handle Verifier result:
- PASS → write wave receipt, then append `"wave-<N>"` and the verification receipt stem to `required_receipts` in state.json, then advance to next wave
- FAIL → enter REVISE loop: fix the specific failure identified by Verifier, re-verify (max 3 cycles)
- BLOCKED → surface to user for Attestation, pause execution

**5. Write wave receipt**

`.wabblespec/state/receipts/wave-<N>-receipt.json`. Required fields: all base receipt fields + wave number, verification mode used, revise cycles consumed, checkpoint path, deviations found.

**5b. Write session checkpoint**

After the wave receipt is written, write `.wabblespec/state/session/checkpoints/checkpoint-wave-<N>.json` conforming to `.wabblespec/engine/shared/schemas/wave-checkpoint.schema.json`. Required fields:

```json
{
  "checkpoint_id": "wave-<N>-<session_id>",
  "session_id": "<current session ID>",
  "task_id": "<task card ID>",
  "wave_index": "<N (zero-based)>",
  "wave_label": "<wave label from wave plan>",
  "timestamp": "<ISO-8601>",
  "receipts_written": ["<paths to receipts written this wave>"],
  "files_modified": [{"path": "...", "action": "created|modified|deleted"}],
  "state_snapshot": {
    "wave_plan_path": ".wabblespec/state/plans/current-wave-plan.md",
    "task_card_path": ".wabblespec/state/plans/task-card.md",
    "acceptance_criteria_met": [],
    "acceptance_criteria_pending": []
  }
}
```

Create `.wabblespec/state/session/checkpoints/` if it does not exist. This checkpoint is the recovery point for session resume after interruption. Do not write this checkpoint before the wave receipt exists — the receipt is the confirmation that the wave completed.

### After all waves complete — module-build acceptance gate

Before writing the final execution receipt, check the task-card for `task_type`.

If `task_type` is `module-build`:

1. Read `target_module` from the task-card (required fields: `layer`, `module_id`).
2. Construct the expected acceptance file path: `modules/{layer}/{module_id}/tests/acceptance.md`
3. Check whether that file exists.
4. **If absent:** emit ACCEPTANCE_NOT_COVERED (error type: SPEC_VIOLATION).
   - Do not write `execution-receipt.json`.
   - Do not signal Archive.
   - Surface to user: "Module build task cannot be marked complete — `tests/acceptance.md` is missing at `{path}`. Author acceptance tests for this module before re-running Executor's final step."
   - Error routes per SPEC_VIOLATION: loop back to acceptance test authorship.
5. **If present:** proceed to write `execution-receipt.json` with `acceptance_verified: true` and signal Archive.

If `task_type` is anything other than `module-build`, skip this check entirely and write `execution-receipt.json` with `acceptance_verified: null`.

### Write final execution receipt

`.wabblespec/state/receipts/execution-receipt.json`. Signal Archive to run.

### Error routing

| Error type | Action |
|---|---|
| SOFT | Retry once. If retry fails, escalate to HARD. |
| HARD | Halt wave. Human-confirmed rollback to prior checkpoint. |
| DEPENDENCY | Pause. Surface upstream failure. Await resolution. |
| CONTEXT_EXHAUSTION | Compress context. Resume from last saved checkpoint. |
| SPEC_VIOLATION | Pause. Loop back to Specify or ScopeFrame depending on violation. ACCEPTANCE_NOT_COVERED routes to acceptance test authorship. |
| STALENESS_VIOLATION | Quarantine the evidence. Surface for fresh fetch before continuing. |

## Output contract

**wave receipts** (`.wabblespec/state/receipts/wave-<N>-receipt.json`):

Base receipt schema. Extension fields:
```json
{
  "wave_number": "integer",
  "verification_mode_used": "string",
  "revise_cycles": "integer — 0 to 3",
  "checkpoint_path": ".wabblespec/state/checkpoints/wave-N-timestamp/",
  "deviations_found": ["string — ADDITIVE/COSMETIC deviations if any"]
}
```

**execution-receipt.json** (`.wabblespec/state/receipts/execution-receipt.json`):

Base receipt. Extension:
```json
{
  "waves_planned": "integer",
  "waves_completed": "integer",
  "waves_failed": "integer",
  "rollbacks_triggered": "integer",
  "acceptance_verified": "boolean — true if task_type was module-build and check passed; null if not a module-build task",
  "errors_by_type": {
    "SOFT": "integer",
    "HARD": "integer",
    "DEPENDENCY": "integer",
    "CONTEXT_EXHAUSTION": "integer",
    "SPEC_VIOLATION": "integer",
    "STALENESS_VIOLATION": "integer"
  }
}
```

**checkpoints** (`.wabblespec/state/checkpoints/wave-<N>-<timestamp>/`): directory with `checkpoint-meta.json` listing wave number, timestamp, files snapshotted.

## A note on common failure modes

1. **Skipping the checkpoint save.** The checkpoint is the only rollback. If it was not saved before the wave started, rollback is impossible and recovery requires manual intervention. Save the checkpoint first, every wave.

2. **Proceeding past Guard FAIL.** Guard FAIL means the wave is invalid to run. There is no "run it anyway." Stop, resolve the Guard violation, then re-run Guard.

3. **Implementing beyond declared outputs.** The wave plan declares what artifacts a wave produces. Extra artifacts outside the plan are a scope violation. If the extra work is genuinely needed, surface it as an ADDITIVE deviation and record it in the wave receipt.

4. **Suppressing ACCEPTANCE_NOT_COVERED to close out a module-build task.** A module without acceptance tests is an unverifiable module. The loop-back is not optional — acceptance tests must exist before the task is receipted as complete.

## Not tested

The acceptance gate assumes `task_type` is a top-level field in task-card.md. Task cards that declare task type in a non-standard location will require task-card schema alignment before this check is reliable. Benchmark validated 8 held-out fixture cases (missed_test_rate = 0.0).
