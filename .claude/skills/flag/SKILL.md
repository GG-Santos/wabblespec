---
name: flag
description: Feature flag lifecycle management. Create, roll out, audit, and retire flags. Maintains flag manifest. Rollout gated on declared conditions.
---

# Flag

Feature flags enable safe deployment of incomplete or risky features. You manage the full flag lifecycle: creation, rollout, audit, and retirement. A flag not in the manifest does not exist as far as this framework is concerned.

## What this skill does

Manages feature flags through four modes: `--create`, `--rollout`, `--audit`, `--retire`. Maintains `.wabblespec/flags/manifest.json` as the authoritative flag registry. Writes flag receipt per operation.

## When to use

- Creating a new feature flag before deployment
- Rolling out an existing flag (expanding scope)
- Auditing flag health (stale flags, missing owners)
- Retiring a flag after feature is fully deployed or abandoned

## Inputs

- Mode: `--create` | `--rollout` | `--audit` | `--retire`
- Flag ID (kebab-case, unique)
- Flag manifest (`.wabblespec/flags/manifest.json` — read and update)

## How to do it

### --create

Validate flag ID is unique in manifest. Write entry with state `DRAFT`. Fields required: `id`, `owner`, `description`, `created_at`, `state: DRAFT`. Do not activate at creation — flags start DRAFT.

### --rollout

Read current flag state. Apply rollout gate (rules/rollout-gate.md). Gate must pass before state transitions: DRAFT → ACTIVE or ACTIVE → ROLLING. Write updated state to manifest.

ROLLING = gradual percentage-based exposure. Requires `rollout_percentage` and `rollout_target` fields.

### --audit

Scan manifest for: DRAFT flags older than 30 days (stale), ROLLING flags with no rollout_percentage update in 14 days (stuck), ACTIVE flags with no associated task card (orphaned), flags with no owner. Report each with recommended action.

### --retire

Transition state to RETIRED. Record `retired_at` timestamp and `retirement_reason`. Retired flags remain in manifest — do not delete. Deletion requires an explicit `--purge` flag (not default).

## Output contract

**flag-receipt.json** (`.wabblespec/state/receipts/flag-receipt-<timestamp>.json`):

```json
{
  "mode": "create | rollout | audit | retire",
  "flag_id": "string",
  "previous_state": "DRAFT | ACTIVE | ROLLING | RETIRED | null",
  "new_state": "DRAFT | ACTIVE | ROLLING | RETIRED",
  "rollout_gate_passed": "boolean — null if mode != rollout",
  "flag_manifest_path": ".wabblespec/flags/manifest.json"
}
```

## State machine

```
DRAFT → ACTIVE (rollout gate passed, manual promotion)
ACTIVE → ROLLING (rollout gate passed, percentage < 100%)
ROLLING → ACTIVE (100% rollout confirmed)
Any → RETIRED (explicit retire command)
```
