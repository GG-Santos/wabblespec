---
name: augment
description: Writes experimental implementation of a module change from an approved Blueprint. For AUGMENT type: completes a modified copy of the existing module. For NEW type: completes Factory stubs. All output goes to .wabblespec/state/experiments/augments/. Never touches production module space.
layer: L8
---

# Augment

You write the experiment. Not the production module — the experiment.

## What this skill does

Augment reads an approved blueprint.json and produces a working experimental module implementation in `.wabblespec/state/experiments/augments/{blueprint-id}/`. For AUGMENT type blueprints, it copies the current module files and applies the `after_behavior` change described in the blueprint. For NEW type blueprints, it completes the Factory stubs. The result must be a complete, runnable module — not a partial draft.

Augment does not write to `modules/`. It does not modify existing receipts. It is the only step between Blueprint and Benchmark.

## When to use

Augment activates when:
1. `blueprint.json` exists with `status: approved` and Blueprint receipt confirms Attestation
2. For AUGMENT type: current module files at `modules/{layer}/{module}/` are readable
3. For NEW type: Factory stubs exist at `.wabblespec/state/experiments/augments/{blueprint-id}/`
4. Human explicitly invokes Augment with the blueprint ID

## Inputs

| Input | Path | Required |
|---|---|---|
| Approved blueprint | `.wabblespec/state/experiments/blueprints/{id}.blueprint.json` | Yes |
| Blueprint receipt | `.wabblespec/state/receipts/blueprint-*.json` | Yes |
| Current module (AUGMENT) | `modules/{layer}/{module}/` | Yes for AUGMENT type |
| Factory stubs (NEW) | `.wabblespec/state/experiments/augments/{blueprint-id}/` | Yes for NEW type |

## Workflow

**For AUGMENT type:**
1. Copy all files from `modules/{layer}/{module}/` to `.wabblespec/state/experiments/augments/{blueprint-id}/`
2. Apply the `after_behavior` change from blueprint.json to the copied SKILL.md
3. Update skill-rules.json as needed for the behavior change
4. Update receipt schema if new fields are required
5. Update tests/acceptance.md to include criteria for the new behavior
6. Do not copy receipts/ directory from the source module

**For NEW type:**
1. Complete each [FILL] stub in the Factory scaffold
2. Write full SKILL.md — all required sections (purpose, activation, inputs, output contract, failure modes, not-tested)
3. Populate skill-rules.json activators, anti_activators, preconditions
4. Extend receipt schema with module-specific required fields
5. Write concrete GWT acceptance scenarios

## Output contract

**Directory:** `.wabblespec/state/experiments/augments/{blueprint-id}/`

Complete module files — no [FILL] markers, no placeholders. Every section populated. Receipt schema contains at least one module-specific required field beyond the base.

The experimental module must pass the same structural checks as a production module: SKILL.md has purpose statement, activation, input/output contracts, failure modes, not-tested. skill-rules.json has layer, activators, authority, verification_mode. Receipt schema is valid JSON Schema extending the base.

## Failure modes

**Incomplete stub** — Augment writes a file with [FILL] markers remaining. Fix: all placeholders must be resolved before receipt is written. Not-tested section must name what Augment could not complete.

**Scope drift** — Augment implements more than what blueprint.json specifies. Fix: stay within `before_behavior` → `after_behavior` scope. Additional improvements go through a new Synth cycle.

**Production contamination** — Augment modifies files in `modules/`. Fix: only `.wabblespec/state/experiments/augments/` is writable. Any write to `modules/` is a hard violation of I11.

## Not tested

Augment cannot verify that the experimental module will pass Benchmark. Augment verifies structural completeness only. Benchmark validates behavioral quality against fixtures.
