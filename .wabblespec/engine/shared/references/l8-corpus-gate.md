---
name: l8-corpus-gate
description: Hard gate conditions that must be met before any L8 Evolution module (Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge) produces output that influences the live framework. Current status: PARTIALLY MET — receipt corpus CLEARED; human-validated patterns pending.
gate_status: MET
last_evaluated: 2026-05-25
---

# L8 Evolution Corpus Gate

## Current Status: MET — All conditions satisfied

All gate conditions are met as of 2026-05-25. The receipt corpus was cleared at seed-run-20260525ac (receipt #100). Three human-validated Instinct patterns were written to `.wabblespec/state/memory/instinct-observations.md` and confirmed on 2026-05-25. Synth is now authorized to propose framework evolution candidates.

L8 module folders exist, are registered in `framework.yaml`, and are **structurally built** and **operationally authorized**.

## Gate Conditions

All conditions must be simultaneously true. Partial satisfaction does not unlock L8 promotion.

| Condition | Requirement | Current State | Met? |
|---|---|---|---|
| Receipt corpus | 100+ verified receipts in `.wabblespec/state/receipts/` | 100 receipts (32 task entries in receipt-index.json) | **YES** |
| Human-validated patterns | 3 non-spurious patterns from Instinct runs, each attested by a human in writing | 3 patterns validated in `.wabblespec/state/memory/instinct-observations.md` (2026-05-25) | **YES** |
| Benchmark schema | `benchmark` module has a schema with `developer_outcome` field declared | CONFIRMED: `modules/l8/benchmark/schemas/benchmark.schema.json` has `developer_outcome` as a required field with four enum values | YES |
| No open contradictions | `contradictions.md` must have zero unresolved entries | CONFIRMED: `.wabblespec/state/memory/provenance/contradictions.md` has empty table | YES |
| Forge attestation | Any Blueprint → Forge promotion requires explicit human sign-off outside the wave plan | Gate not exercised (Forge not yet invoked) | N/A |

## What Changed Since Last Evaluation

- **Receipt corpus**: 67 → 100 PASS receipts (33 receipts added across seed runs s through ac); currently 117 total
- **Benchmark schema**: CONFIRMED via direct verification of `benchmark.schema.json`
- **Contradictions**: CONFIRMED via direct verification of `contradictions.md`
- **Human-validated patterns**: 0 → 3 validated (2026-05-25); patterns written to `instinct-observations.md` and marked `Human-validated: true`

## Gate Cleared (2026-05-25)

All conditions met. No further gate actions required.

Next step: run Synth to generate framework evolution proposals based on the 3 validated Instinct patterns.

## Behavioral Pressure Validation (pre-Benchmark requirement)

Before any skill candidate reaches Benchmark, it must pass behavioral pressure validation. This gate sits between Augment and Benchmark in the evolution chain. Quantitative Benchmark thresholds (80% parity for AUGMENT, 60% improvement for NEW) measure performance on fixture sets -- they do not test whether the skill actually prevents the behavioral violations it was designed to address.

**Protocol:**

1. Write 3 pressure scenarios: prompts designed to trigger the exact rationalization the skill candidate is meant to prevent. These are adversarial prompts -- they should look reasonable while leading the agent toward the violation.
2. Run each scenario against a fresh-context agent that does NOT have the skill loaded. Confirm the agent violates the rule (baseline failure). If the agent passes without the skill, the skill is solving a non-problem -- halt and surface to human.
3. Load the skill candidate. Re-run the same 3 scenarios. Confirm the agent complies with the rule in all 3 cases.
4. If the agent finds a new rationalization not covered by the skill during testing, refine the skill and re-run. Each refinement restarts the 3-scenario pass requirement.

**Pass condition:** All 3 scenarios must produce compliant agent behavior with the skill loaded. Partial pass (2/3) is a fail -- the uncovered rationalization must be closed before Benchmark.

**Evidence requirement:** 3 scenario transcripts (saved to `.wabblespec/state/experiments/pressure-validation/<candidate-id>/`) must be attached to the Benchmark receipt as `pressure_validation_transcripts`. A Benchmark receipt without this field is rejected by Guard.

**What this gate is not:** This is not a substitute for Benchmark metric thresholds. Both gates must pass. A skill that passes behavioral pressure validation but fails Benchmark is still not promoted.

## What L8 Modules May Do Now

| Module | Current authorization |
|---|---|
| Instinct | **AUTHORIZED** — observations written; 3 patterns human-validated |
| Synth | **AUTHORIZED** — 3 human-validated patterns confirmed (2026-05-25) |
| Blueprint | Read-only |
| Factory | Read-only |
| Augment | Read-only |
| Benchmark | Read-only |
| Forge | Read-only; Forge Attestation gate required before any write |
| Retro, Feedback | May read and write to own directories; unchanged |

## What L8 Modules May NOT Do (Until Full Gate Met)

- Write to any live module directory (`modules/l0`–`l7/`)
- Alter `framework.yaml`, `.wabblespec/engine/shared/`, or `hooks/`
- Promote any Blueprint to Forge without explicit human sign-off
- Apply any evolution output to the live framework without Synth authorization

## Why This Gate Exists

L8 was built before the corpus gate was met. This document records that fact and prevents the structural presence of L8 modules from being interpreted as operational authorization. The REFERENCE-INTEGRATION-MASTER-PLAN.md stated: "L8 Evolution is Later/Experimental — gate behind real receipt data exists."

The receipt gate is now cleared. The human-validated patterns condition is the final barrier before Synth gains write authorization.

## Authority

This document is authoritative over `framework.yaml` L8 entries. If `framework.yaml` marks an L8 module `build_status: built`, that refers to structural build only. Operational authorization is controlled by this gate document and updated only by a human after verifying each condition directly.

Consumers: `framework.yaml`, `modules/l8/*/SKILL.md`, `modules/l2/guard/SKILL.md` (Guard Layer 3 invariant I-L8).
