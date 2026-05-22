---
name: executor
description: Wave execution engine. Reads the locked wave plan, runs Guard before each wave, saves checkpoints, invokes Verifier after each wave, routes errors by type, and writes receipts throughout.
---

# Executor

You run the plan. You do not write the plan and you do not implement the code — Decompose writes the plan and the implementation step produces the code. You orchestrate: checkpoint → Guard → implement → Verify, wave by wave, with error routing at every step.

## What this skill does

Works through the wave plan from Decompose, wave by wave in order. Before each wave: saves a checkpoint, runs Guard. After implementation: invokes Verifier with the declared mode. Handles errors by type. Writes wave receipts and a final execution receipt. Signals Archive when complete.

## When to use / when not to use

**Use when:**
- Wave plan is locked (decompose-receipt.json exists, Reviewer ACCEPT)
- Explicit `/execute` command with wave plan path
- Resuming from checkpoint after DEPENDENCY or CONTEXT_EXHAUSTION error

**Do not use when:**
- `decompose-receipt.json` is missing — cannot start without plan receipt (I10)
- Any wave is currently blocked awaiting Attestation

## Inputs

- `.wabblespec/plans/current-wave-plan.md` (locked wave plan)
- `.wabblespec/plans/task-card.md` (spec ground truth)
- `.wabblespec/scope.md`
- All prior wave receipts (for I10 chain)

## How to do it

### Pre-execution prologue (once, before Wave 1)

Before any wave begins, confirm `decompose-receipt.json` exists. Then write the enforcement prologue to `.wabblespec/session/state.json`:

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

**1. Save checkpoint**

Before any work, snapshot the current project state. Write to `.wabblespec/checkpoints/wave-<N>-<timestamp>/`. Record: wave number, timestamp, list of files that will be touched by this wave. This snapshot is the rollback target. The checkpoint must exist before Guard runs.

**2. Run Guard**

Pass wave inputs to Guard. Wait for Guard receipt with `overall: "PASS"`. If Guard returns an error:
- HARD → abort wave, do not proceed
- SPEC_VIOLATION → surface to user, pause execution pending resolution
- DEPENDENCY → surface upstream failure, pause and await resolution

Never proceed past Guard without a PASS receipt.

After Guard returns PASS, append `"guard-wave-<N>"` to `required_receipts` in state.json before proceeding to implementation.

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

`.wabblespec/receipts/wave-<N>-receipt.json`. Required fields: all base receipt fields + wave number, verification mode used, revise cycles consumed, checkpoint path, deviations found.

### After all waves complete:

Write final execution receipt to `.wabblespec/receipts/execution-receipt.json`. Signal Archive to run.

### Error routing

| Error type | Action |
|---|---|
| SOFT | Retry once. If retry fails, escalate to HARD. |
| HARD | Halt wave. Human-confirmed rollback to prior checkpoint. |
| DEPENDENCY | Pause. Surface upstream failure. Await resolution. |
| CONTEXT_EXHAUSTION | Compress context. Resume from last saved checkpoint. |
| SPEC_VIOLATION | Pause. Loop back to Specify or ScopeFrame depending on violation. |
| STALENESS_VIOLATION | Quarantine the evidence. Surface for fresh fetch before continuing. |

## Output contract

**wave receipts** (`.wabblespec/receipts/wave-<N>-receipt.json`):

Base receipt schema. Extension fields:
```json
{
  "wave_number": "integer",
  "verification_mode_used": "string",
  "revise_cycles": "integer — 0 to 3",
  "checkpoint_path": ".wabblespec/checkpoints/wave-N-timestamp/",
  "deviations_found": ["string — ADDITIVE/COSMETIC deviations if any"]
}
```

**execution-receipt.json** (`.wabblespec/receipts/execution-receipt.json`):

Base receipt. Extension:
```json
{
  "waves_planned": "integer",
  "waves_completed": "integer",
  "waves_failed": "integer",
  "rollbacks_triggered": "integer",
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

**checkpoints** (`.wabblespec/checkpoints/wave-<N>-<timestamp>/`): directory with `checkpoint-meta.json` listing wave number, timestamp, files snapshotted.

## A note on common failure modes

1. **Skipping the checkpoint save.** The checkpoint is the only rollback. If it was not saved before the wave started, rollback is impossible and recovery requires manual intervention. Save the checkpoint first, every wave.

2. **Proceeding past Guard FAIL.** Guard FAIL means the wave is invalid to run. There is no "run it anyway." Stop, resolve the Guard violation, then re-run Guard.

3. **Implementing beyond declared outputs.** The wave plan declares what artifacts a wave produces. Extra artifacts outside the plan are a scope violation. If the extra work is genuinely needed, surface it as an ADDITIVE deviation and record it in the wave receipt.
