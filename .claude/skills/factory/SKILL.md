---
name: factory
description: Scaffolds a net-new module from an approved Blueprint. Writes stub files (SKILL.md, skill-rules.json, receipt schema, tests/acceptance.md) to .wabblespec/state/experiments/augments/. Never writes to production module space.
layer: L8
---

# Factory

You scaffold the shape of a new module. Augment fills it in.

## What this skill does

Factory reads an approved `blueprint.json` with `change_type: NEW`, then generates a complete module directory scaffold in `.wabblespec/state/experiments/augments/{blueprint-id}/`. The scaffold contains stub files pre-populated from the blueprint's specifications: SKILL.md with purpose, activation, input/output contracts, and failure mode placeholders; skill-rules.json with layer, authority, and verification_mode from the blueprint; receipt schema extending the base; and acceptance criteria stubs.

Factory writes structure only. It does not write behavioral logic, decision trees, or implementation details — those belong in the stub placeholders for Augment to complete.

## When to use

Factory activates when:
1. `blueprint.json` exists with `change_type: NEW` and `status: approved`
2. Blueprint receipt exists confirming human Attestation was obtained
3. No existing directory at `.wabblespec/state/experiments/augments/{blueprint-id}/`
4. Human explicitly invokes Factory with the blueprint ID

If the augments directory already contains the blueprint ID, Factory exits with `IDEMPOTENCY_GUARD` rather than overwriting.

## Inputs

| Input | Path | Required |
|---|---|---|
| Approved blueprint | `.wabblespec/state/experiments/blueprints/{id}.blueprint.json` | Yes — status must be approved |
| Blueprint receipt | `.wabblespec/state/receipts/blueprint-*.json` | Yes — confirms Attestation |
| Framework manifest | `framework.yaml` | Yes — checks for ID conflicts |

Check `framework.yaml` for ID conflicts before scaffolding. A proposed module ID that already exists in framework.yaml must be surfaced to the human before proceeding.

## Reference Routing

| Situation | Reference |
|---|---|
| Factory receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## Output contract

**Directory:** `.wabblespec/state/experiments/augments/{blueprint-id}/`

```
{blueprint-id}/
  SKILL.md               # stub: frontmatter + sections with [FILL] placeholders
  skill-rules.json       # stub: layer/authority/verification_mode from blueprint
  schemas/
    receipt.schema.json  # stub: allOf base + [FILL] extension fields
  tests/
    acceptance.md        # stub: GWT scenario skeletons from blueprint after_behavior
```

Stub SKILL.md frontmatter is populated from blueprint fields. Sections contain `[FILL: description of what goes here]` markers — never left blank. Every placeholder names what Augment must supply.

Stub skill-rules.json contains correct `layer`, `authority.owns` path, and `verification_mode` from the blueprint. `activators` and `anti_activators` contain `["[FILL: activation patterns]"]`.

## Self-validation against prompt failure patterns

Before writing any stub, Factory checks the proposed SKILL.md workflow sections against `.wabblespec/engine/shared/references/prompt-patterns.md`. Any pattern violation found in the blueprint's workflow description blocks Factory from scaffolding until resolved.

Patterns checked per category:
- **Task (T1-T6):** Goal inflation, implicit preconditions, unbounded iteration
- **Context (C1-C6):** Evidence-free assertions, missing not-tested, unsourced defaults
- **Scope (S1-S6):** Missing authority declaration, self-verification, silent scope expansion
- **Agentic (A1-A7):** Missing human gate, receipt chain gap, spawn without scope

**On violation found:**
1. List each violated pattern (code + description)
2. Return `PATTERN_VIOLATION` error — do not scaffold
3. Propose specific fix for each violation in the receipt

Violations from Category 3 (Format) and Category 5 (Reasoning) are warnings, not blocks — logged to receipt but do not halt scaffolding.

## Failure modes

**ID collision** — proposed module ID already exists in framework.yaml. Fix: surface to human, do not scaffold, wait for resolution.

**Idempotency bypass** — Factory called twice for the same blueprint ID. Fix: IDEMPOTENCY_GUARD exit on duplicate directory, no overwrite.

**Overspecified stubs** — Factory writes behavioral logic in SKILL.md stubs, not placeholders. Fix: SKILL.md stubs contain only frontmatter + section headers + [FILL] markers. No prose logic.

## Not tested

Factory cannot verify that the stubs are correct inputs for Augment — Augment reads and completes them. Factory verifies only that the required files exist and contain the correct structure markers.
