# Migration Plan — <breaking-change-id>

**change_ref:** <Specify delta ID>
**generated_at:** <ISO 8601>
**migration_type:** two-phase|single-phase
**single_phase_justification:** <required if single-phase — state which exception applies and why>

## What Changed

<BREAKING delta description from Specify — copied from delta record>

## Consumer Impact

<What consumers must change and why. Be specific about interface names, method signatures, or data formats that are affected.>

## Phase 1 — Additive (backward-compatible)

**target_wave:** <wave ID>
**changes:**
- New: <what is added>
- Deprecated: <what is marked deprecated but kept — include deprecation notice text>

## Phase 2 — Removal

**gate:** <What must be confirmed before Phase 2 executes. Name specific consumers or state "all consumers of <interface> must have migrated.">
**changes:**
- Removed: <what is removed>

## Migration Steps (consumer guide)

1. <Step — be specific enough that a consumer can follow without context>
2. <Step>
3. <Step>

## Automated Migration Script

<!-- If automatable -->
Script: `project/repo/scripts/migrate/<change-id>.sh`

<!-- If not automatable -->
Not automatable — reason: <specific reason>

## Rollback

**Phase 1 rollback:** <How to revert Phase 1 if it fails — which wave to revert, what to restore>
**Phase 2 rollback:** <How to revert Phase 2 if it fails — Phase 2 rollback is typically a re-introduction of the removed interface, which is itself a BREAKING change requiring a new migration plan>
