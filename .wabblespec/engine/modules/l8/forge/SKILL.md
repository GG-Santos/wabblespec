---
name: forge
description: The only L8 module that writes to production module space. Promotes a benchmarked experiment to modules/{layer}/{module}/. Gates: benchmark-passed receipt + Blueprint approval + no open contradictions in tracker.json. Self-modification always requires Attestation. After promotion: module receipt updated, experiment archived, downstream specs marked NEEDS_REVERIFICATION.
layer: L8
---

# Forge

You are the only path from experiment to production. The gates are not optional.

## What this skill does

Forge copies a fully benchmarked experimental module from `.wabblespec/state/experiments/augments/{blueprint-id}/` to the production module path `modules/{layer}/{module}/`. After copying, it updates the module's receipt, archives the experiment with a provenance trail, and marks any downstream specs as NEEDS_REVERIFICATION. It then writes a Forge receipt.

Forge does not evaluate whether the change is good — Benchmark did that. Forge verifies that all prerequisite gates are met and executes the promotion.

**Self-modification rule (I8):** If the promoted module is an L8 module (any module under `modules/l8/`), Attestation verification mode is mandatory. Forge refuses to promote L8 self-modifications without a human Attestation receipt on file.

## When to use

Do not activate unless ALL of the following are true:

1. `blueprint.json` status is `benchmark-passed`
2. A Benchmark receipt exists for this blueprint ID with `verdict: PASS`
3. `tracker.json` has no entry for this blueprint ID with `verdict: FAIL` and `requeue_decision: null` (open contradiction)
4. For L8 self-modification: an Attestation receipt exists for this blueprint ID
5. Human explicitly invokes Forge with the blueprint ID

If any gate is unmet, Forge exits with `FORGE_BLOCKED`, names the unmet gate, and writes no files.

## Inputs

| Input | Path | Required |
|---|---|---|
| Blueprint | `.wabblespec/state/experiments/blueprints/{id}.blueprint.json` | Yes — status must be benchmark-passed |
| Benchmark receipt | `.wabblespec/state/receipts/benchmark-*.json` | Yes — verdict: PASS |
| Augment output | `.wabblespec/state/experiments/augments/{blueprint-id}/` | Yes |
| tracker.json | `.wabblespec/state/experiments/tracker.json` | Yes — checked for open contradictions |
| Attestation receipt (L8 only) | `.wabblespec/state/receipts/attestation-*.json` | Required for L8 modules |

## Workflow

1. Verify all activation gates. Exit `FORGE_BLOCKED` on any failure.
2. Identify target path: `modules/{layer}/{module}/` from blueprint `affected_module` + framework.yaml.
3. Copy augment files to target path. Overwrite existing files.
4. Write updated module receipt to `.wabblespec/state/receipts/{module}-promoted-{timestamp}.json`.
5. Mark downstream specs NEEDS_REVERIFICATION: check framework.yaml `depends_on` graph for modules that depend on the promoted module. Write NEEDS_REVERIFICATION note to each affected module's receipt.
6. Archive experiment: move `.wabblespec/state/experiments/augments/{blueprint-id}/` to `.wabblespec/state/experiments/archive/{blueprint-id}/`. Append provenance record to `.wabblespec/state/experiments/archive/provenance.json`.
7. Update framework.yaml: set promoted module's `last_validated` and `build_status: built`.
8. Write Forge receipt.

## Reference Routing

| Situation | Reference |
|---|---|
| Forge receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type forge` |

## Output contract

**Writes to production:** `modules/{layer}/{module}/` — complete replacement of module files
**Mutates:** `framework.yaml` (last_validated, build_status)
**Mutates:** `.wabblespec/state/experiments/tracker.json` (promotion record appended)
**Mutates:** Downstream module receipts (NEEDS_REVERIFICATION notes)
**Moves:** experiment to archive with provenance record

**Does not touch:** product source under product space

## Failure modes

**Gate bypass** — Forge invoked before benchmark-passed status. Fix: FORGE_BLOCKED exit. Forge never proceeds on approved-only status.

**L8 self-modification without Attestation** — Forge asked to promote a change to an L8 module without Attestation receipt. Fix: hard block. L8 self-modification without Attestation is prohibited (I8).

**Downstream NEEDS_REVERIFICATION missed** — Forge does not propagate reverification to modules that depend on the promoted module. Fix: Forge must traverse `depends_on` graph in framework.yaml before writing receipt.

**Archive skipped** — experiment directory left in augments/ after promotion. Fix: move to archive is part of the promotion workflow, not optional. A promotion without archiving leaves an orphaned experiment.

## Not tested

Forge cannot verify that the promoted module behaves correctly on real production executions — only that it passed Benchmark fixtures. Instinct will observe the promoted module's receipt pattern over the next 100+ receipts. If behavior regresses, Rollback is the recovery path.
