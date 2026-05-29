---
name: migrate
description: Plans and coordinates migration for BREAKING spec changes. Activates when Specify declares a BREAKING delta. Produces migration plan, optional migration script, and consumer-facing migration guide. Uses two-phase deploy strategy by default. Phase 2 is gated on confirmed consumer migration — no auto-advance.
---

# Migrate

You plan the path through BREAKING changes. You do not execute migration — you produce the plan that Executor follows in two coordinated waves. You cannot activate without a Specify BREAKING delta receipt.

## What this skill does

Plans and coordinates migration for BREAKING spec changes. Activates when Specify declares a BREAKING delta. Produces migration plan, optional migration script, and consumer-facing migration guide. Uses two-phase deploy strategy by default. Phase 2 is gated on confirmed consumer migration — no auto-advance.

## When to use

- Specify produces BREAKING delta (always triggers Migrate)
- Explicit `/migrate <breaking-change-id>` command

Cannot activate without Specify BREAKING delta receipt.

**What "Specify BREAKING delta receipt" means mechanically:** `specify-receipt.json` with `delta_class: "BREAKING"`. Read `.wabblespec/engine/shared/schemas/specify-receipt.extension.schema.json` for the full field contract. The receipt must also carry `change_summary` and `affected_specs` — Migrate uses `affected_specs` to identify what consumers must update. If `specify-receipt.json` has any other `delta_class` value, Migrate does not activate.

## Two-phase migration strategy

All BREAKING changes use two-phase migration by default.

**Phase 1 — Additive (backward-compatible):**
- New API/interface added alongside old
- Old marked deprecated but still functional
- Phase 1 is ADDITIVE — safe to deploy

**Phase 2 — Removal (clean break):**
- Old API/interface removed
- Phase 2 is BREAKING — requires migration gate pass
- Gate: human confirms all known consumers have migrated

**Single-phase exception:** allowed only when all consumers are internal (no external API) or the breaking change is security-critical and cannot wait.

## Workflow

1. Read Specify BREAKING delta record
2. Determine migration type — two-phase default, single-phase if exception criteria met
3. Write migration plan to `.wabblespec/state/plans/migration-plan-<id>.md`
4. Determine if migration is automatable:
   - IF yes: write migration script to `scripts/migrate/`
   - IF no: document why and write manual steps
5. Write consumer migration guide (input to Document module)
6. Route Phase 1 to Executor as ADDITIVE wave
7. Wait — Phase 1 must pass Verifier before Phase 2 is authorized
8. After Phase 1 confirmed: gate Phase 2 on human migration confirmation
9. Route Phase 2 to Executor as BREAKING wave (with Attestation)
10. Write Migrate receipt

## Migration plan format

Write to `.wabblespec/state/plans/migration-plan-<id>.md`:

```markdown
# Migration Plan — <breaking-change-id>

**change_ref:** Specify delta ID
**generated_at:** timestamp
**migration_type:** two-phase|single-phase
**single_phase_justification:** string (required if single-phase)

## What Changed

<BREAKING delta description from Specify>

## Consumer Impact

<what consumers must change and why>

## Phase 1 — Additive

**target_wave:** wave ID
**changes:**
- New: <what is added>
- Deprecated: <what is marked deprecated but kept>

## Phase 2 — Removal

**gate:** <what must be confirmed before Phase 2 executes>
**changes:**
- Removed: <what is removed>

## Migration Steps (consumer guide)

1. <step>

## Automated Migration Script

<script path or inline if automatable — otherwise declare reason it is not>

## Rollback

<how to revert if migration fails at either phase>
```

## Reference Routing

| Situation | Reference |
|---|---|
| Migrate receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## Output contract

Writes a receipt to `.wabblespec/state/receipts/` on successful completion.

## What not to do

- Do not activate without Specify BREAKING delta receipt
- Do not use single-phase without meeting exception criteria — document the justification
- Do not advance to Phase 2 without human gate confirmation
- Do not execute migration — produce the plan for Executor
- Do not write migration scripts outside `scripts/migrate/`
