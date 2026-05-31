---
name: ensemble
description: Coordinates multiple runtime lanes for tasks no single lane covers adequately. Triggered exclusively by ModelRouter. Three modes: Sequential (B needs A output), Independent (parallel, independent artifacts), Cross-check (both run same task, Grader compares). Cross-check required for Attestation and Audit modes. Writes combined receipt naming all lanes used.
---

# Ensemble

You are triggered by ModelRouter only — never self-activate. You coordinate multiple lanes and write one combined receipt.

## What this skill does

Coordinates multiple runtime lanes for tasks no single lane covers adequately. Triggered exclusively by ModelRouter. Three modes: Sequential (B needs A output), Independent (parallel, independent artifacts), Cross-check (both run same task, Grader compares). Cross-check required for Attestation and Audit modes. Writes combined receipt naming all lanes used.

## When to use

Triggered by ModelRouter when any of four conditions met:
1. Task spans multiple build targets simultaneously
2. No single capability covers all required capabilities
3. Verification mode is Attestation or Audit
4. Confidence below 0.7 after single-lane attempt

## Coordination modes

**Sequential** — Lane B requires Lane A output before starting. Use when: output dependency between lanes.

**Independent** — Lanes run in parallel, produce separate artifacts. Use when: task is parallelizable with no shared output.

**Cross-check** — Both lanes run the same task independently. Grader (from Reviewer) compares outputs. Use when: verification mode is Attestation or Audit, or confidence gap between lanes.

Cross-check is mandatory for Attestation and Audit verification modes.

## Reference Routing

| Situation | Reference |
|---|---|
| Ensemble receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## Output contract

Combined receipt names all lanes, mode used, and individual lane outcomes:

```json
{
  "module": "ensemble",
  "mode": "Sequential|Independent|Cross-check",
  "lanes": [
    { "capability": "string", "outcome": "PASS|FAIL", "artifacts": [] }
  ],
  "combined_outcome": "PASS|FAIL",
  "cross_check_agreement": true
}
```

Cross-check: if lanes disagree, `cross_check_agreement: false` — route to Reviewer.

## What not to do

- Do not self-activate — ModelRouter triggers only
- Do not skip Cross-check for Attestation/Audit verification modes
- Do not write separate receipts per lane — one combined receipt only
