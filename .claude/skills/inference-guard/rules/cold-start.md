# InferenceGuard Cold-Start Procedure

Run at the start of any session where gateway-security is active or task_type is security-typed.

## Step 1: Read task card

Read `.wabblespec/plans/task-card.md`. Extract:
- `task_type` — must be in security-typed set to activate
- `inference_guard` — if `false`, skip all remaining steps and write suppressed receipt
- `inference_guard_tier` — defaults to `standard` for Red protocol, `light` otherwise
- `inference_guard_technique` — defaults to `leetspeak`

## Step 2: Check gateway

Read `.wabblespec/receipts/` for a `gateway-security-spec-receipt-*.json` written this session. If none found: InferenceGuard does not activate. Write non-activation receipt with `reason: gateway_inactive`.

## Step 3: Load vocabulary

Read `modules/l2/inference-guard/rules/trigger-vocabulary.md`. Load trigger sets for the declared tier (Tier 1 always, Tier 2 if standard or heavy, Tier 3 only if heavy).

## Step 4: Confirm script availability

Verify `.wabblespec/engine/shared/scripts/inference-guard.py` exists. If missing: emit `DEPENDENCY_MISSING` error. Do not proceed.

## Step 5: Write session state

Note activation conditions to session context. No writes to `.wabblespec/` at cold-start. Writes happen at execution time (Step 5 of workflow in SKILL.md).

## Non-activation on cold-start

Cold-start does not trigger a receipt write. Receipts are written at execution time, not at session initialization. Non-activation receipts are written when an execution attempt is made and conditions are not met.
