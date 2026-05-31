---
name: sync
description: Reconciles diverged spec artifacts from parallel changes. Detects divergence, applies merge strategy, escalates unresolvable conflicts. On-demand when parallel work produces conflicting specs.
---

# Sync

Parallel work produces parallel specs. When two spec versions diverge from the same base, you reconcile them. You merge what can be auto-merged, escalate what cannot, and leave a clear record of every decision.

## What this skill does

Receives two or more diverged spec artifacts. Detects divergence severity. Applies merge strategy (auto or manual). Produces a reconciled spec or escalates to human if conflicts are unresolvable. Writes sync receipt.

## When to use / when not to use

**Use when:**
- Two spec artifacts both derived from the same base have been independently modified
- TeamPlan signals parallel work produced conflicting specs
- Explicit `/sync` command

**Do not use when:**
- Only one version of the spec exists — no divergence possible
- Divergence is intentional (A/B test, feature branch) — those are not conflicts

## Inputs

- `spec_a` (path to first spec version)
- `spec_b` (path to second spec version)
- `spec_base` (path to common ancestor, if available)

## How to do it

### Step 1 — Detect divergence

Compare `spec_a` and `spec_b`. Classify divergence severity per rules/divergence-detection.md.

| Severity | Definition |
|---|---|
| `MINOR` | Additive differences only — A adds criteria not in B, or vice versa |
| `MAJOR` | Same criterion defined differently in A and B (conflicting) |

If base is provided: three-way diff. Changes in A but not base + changes in B but not base = both sets of changes. Conflicts = same section changed differently in A and B.

### Step 2 — Apply merge strategy

See rules/merge-policy.md for full decision table.

| Condition | Strategy |
|---|---|
| MINOR + no conflicts | `auto` — merge both additive sets |
| MAJOR + conflicts with clear priority signal | `manual` — apply priority signal |
| MAJOR + conflicts with no priority signal | `escalated` — surface to human |

On `auto` merge: produce merged spec and record what was merged. On `manual` merge: apply the declared priority, document the decision. On `escalated`: stop. Do not produce a partial merged spec. Surface exact conflict locations to user.

### Step 3 — Record decisions

For every resolved conflict: record which version "won" and why. For every escalated conflict: record exactly what question needs human resolution.

### Step 4 — Write result and receipt

Write merged spec to `.wabblespec/sync/result-<timestamp>.md` (or mark as escalated). Write receipt.

## Reference Routing

| Situation | Reference |
|---|---|
| Sync receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` for the base, then `--extra-json` for the module-specific fields defined in `schemas/sync-receipt.schema.json` |

## Output contract

**sync-receipt.json** (`.wabblespec/state/receipts/sync-receipt-<timestamp>.json`):

```json
{
  "specs_reconciled": "integer — number of spec artifacts involved",
  "divergence_severity": "MINOR | MAJOR",
  "auto_merged": "boolean",
  "human_review_required": "boolean",
  "merge_strategy": "auto | manual | escalated",
  "conflicts_resolved": "integer",
  "conflicts_escalated": "integer",
  "sync_result_path": ".wabblespec/sync/result-<timestamp>.md"
}
```

## A note on common failure modes

1. **Auto-merging conflicting content.** MAJOR conflicts with no priority signal must escalate. Do not invent a resolution — the two spec authors must agree.

2. **Partial merged spec on escalation.** When escalating: produce no merged artifact. An incomplete merge is worse than no merge — it looks resolved when it is not.
