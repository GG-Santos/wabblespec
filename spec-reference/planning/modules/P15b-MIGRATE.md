# Module Plan — Migrate (L1)

**Tier:** 3 — SUPPORTING
**Layer:** L1 Spec Core
**v5.3 origin:** Migrate module — migration planning and execution for breaking changes

---

## Purpose

Plan and coordinate migration for BREAKING spec changes. Migrate activates when Specify declares a BREAKING delta — it produces the migration plan, migration script (if automatable), and consumer-facing migration guide. Migrate execution is coordinated through Executor waves using two-phase deploy strategy. Migration plan is a required artifact before any BREAKING change can proceed to execution.

---

## Activation

`skill-rules.json` triggers:
- Specify produces BREAKING delta (always triggers Migrate)
- Explicit `/migrate <breaking-change-id>` command
- Cannot activate without Specify BREAKING delta receipt

---

## Two-Phase Migration Strategy

All BREAKING changes use two-phase migration (from Engineering gateway rules):

**Phase 1 — Additive (backward-compatible):**
- New API/interface added alongside old
- Old marked deprecated (but still functional)
- Consumers can migrate at their own pace
- Phase 1 is ADDITIVE — safe to deploy

**Phase 2 — Removal (clean break):**
- Old API/interface removed
- Consumers must have migrated before Phase 2
- Phase 2 is BREAKING — requires migration gate pass
- Migration gate: confirmation that all known consumers have migrated

Single-phase migration allowed only when: consumers are all internal (no external API), or breaking change is security-critical (cannot wait for two-phase).

---

## Migration Plan Structure

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

## Phase 1 — Additive (backward-compatible)

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
2. <step>

## Automated Migration Script

<if automatable — script path or inline>
<if not automatable — declare reason>

## Rollback

<how to revert if migration fails at either phase>
```

---

## Workflow

```
1. Read Specify BREAKING delta record

2. Determine migration type:
   -> Internal consumers only? → single-phase eligible
   -> Security-critical? → single-phase eligible
   -> Otherwise: two-phase required

3. Write migration plan

4. Determine if migration is automatable:
   -> IF yes: write migration script to project/repo/scripts/migrate/
   -> IF no: document why and write manual steps

5. Write consumer migration guide (input to Document module)

6. Route Phase 1 to Executor as ADDITIVE wave
   -> Phase 1 must pass Verifier before Phase 2 is authorized

7. After Phase 1 confirmed: gate Phase 2 on migration confirmation
   -> Gate confirmation: human declares all consumers migrated

8. Route Phase 2 to Executor as BREAKING wave (with Attestation)

9. Write Migrate receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — BREAKING delta trigger |
| `rules/two-phase-policy.md` | Rules | Two-phase default, single-phase exception criteria |
| `rules/migration-gate.md` | Rules | Phase 2 gate confirmation required |
| `templates/migration-plan.md` | Template | Migration plan structure |
| `templates/migration-guide.md` | Template | Consumer-facing migration guide |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Specify | Specify BREAKING delta triggers Migrate; Migrate reads delta for impact analysis |
| Executor | Migrate routes Phase 1 and Phase 2 as separate Executor waves |
| Verifier | Verifier gates Phase 1 completion before Phase 2 authorized |
| Engineering gateway | Two-phase deploy pattern sourced from Engineering gateway |
| Document | Migrate produces consumer migration guide; Document publishes it |
| Release | Release notes reference migration plan for BREAKING version bumps |

---

## Verification Mode

**Audit** — migration plan present for every BREAKING delta, two-phase used (or single-phase justified), Phase 2 gated on migration confirmation, receipt written.

---

## Receipt Extension Fields

```json
{
  "change_ref": "string",
  "migration_type": "two-phase|single-phase",
  "single_phase_justification": "string",
  "script_generated": "boolean",
  "phase1_wave": "string",
  "phase2_wave": "string",
  "phase2_gate_confirmed": "boolean"
}
```
