---
name: shift
description: Semantic spec versioning and reverse drift detection. Classifies spec changes as BREAKING/DEPRECATION/ADDITIVE/COSMETIC. Detects when implementation diverges from spec. Triggered by Archive post-hook when spec changes.
---

# Shift

Specs change. Implementations drift. Your job is to detect both with precision. You classify what changed in the spec (semantic diff) and detect when implementation has moved away from it (reverse drift). You do not fix — you surface.

## What this skill does

Receives two versions of a spec artifact (before and after). Classifies the change. Detects reverse drift. Identifies downstream consumers affected. Writes compatibility report. Triggered automatically by Archive when Archive detects BREAKING or ADDITIVE spec changes.

## When to use / when not to use

**Triggered by Archive post-hook** when delta_class = BREAKING or ADDITIVE with spec artifact touched.

**Direct invocation when:**
- Explicit `/shift` command
- Decompose identifies a potential spec-implementation gap
- Any module suspects reverse drift

**Do not use when:**
- Only COSMETIC changes (documentation, rename with no behavior change)
- No prior version of the spec exists to diff against

## Inputs

- `spec_before` (path to previous spec version — from Archive or git)
- `spec_after` (path to current spec version)
- `implementation_path` (path to implementation — for reverse drift check)
- `consumer_list` (optional — module IDs that depend on this spec)

## How to do it

### Step 1 — Semantic diff

Run `scripts/semantic-differ.py --before <spec_before> --after <spec_after>`. Classifies changes per rules/change-classification.md.

| Class | Definition |
|---|---|
| `BREAKING` | Removes or incompatibly changes existing behavior — callers must change code |
| `DEPRECATION` | Marks behavior for future removal with declared sunset |
| `ADDITIVE` | New capability alongside existing behavior — no consumer change required |
| `COSMETIC` | Documentation, rename with no behavior change, whitespace |

A single spec change may produce multiple classifications (e.g., DEPRECATION + ADDITIVE when a function is deprecated and a replacement added). Write all that apply.

### Step 2 — Reverse drift detection

Run `scripts/reverse-drift-detector.py --spec <spec_after> --impl <implementation_path>`. Checks whether the implementation conforms to the spec after the change.

Reverse drift = implementation was edited without spec update, OR spec was updated without implementation following. See rules/reverse-drift-triggers.md.

Record: `reverse_drift_detected: boolean` and `reverse_drift_details: string`.

### Step 3 — Downstream consumer impact

Run `scripts/compatibility-checker.py --change-class <class> --consumers <consumer_list>`. Identifies which consumers are affected by the classified change.

A consumer is affected if the change modifies an interface they call, a schema they validate against, or a behavior they depend on.

Record: `downstream_consumers_affected: integer`, `affected_consumer_ids: array`.

### Step 4 — Loop-back decision

If change_class = BREAKING AND downstream consumers affected: set `loop_back_required: true`. This signals the originating pipeline to surface to user before proceeding — breaking changes require consumer migration coordination.

### Step 5 — Write report and receipt

Write compatibility report to `.wabblespec/shift/compat-<timestamp>.md`. Write semantic diff to `.wabblespec/shift/diff-<timestamp>.md`. Write receipt.

## Output contract

**shift-receipt.json** (`.wabblespec/receipts/shift-receipt-<timestamp>.json`):

```json
{
  "change_class": "BREAKING | DEPRECATION | ADDITIVE | COSMETIC",
  "reverse_drift_detected": "boolean",
  "reverse_drift_details": "string — null if not detected",
  "downstream_consumers_affected": "integer",
  "affected_consumer_ids": ["array of module ids"],
  "compatibility_report_path": ".wabblespec/shift/compat-<timestamp>.md",
  "semantic_diff_path": ".wabblespec/shift/diff-<timestamp>.md",
  "loop_back_required": "boolean"
}
```

## A note on common failure modes

1. **Under-classifying BREAKING as ADDITIVE.** If any existing caller must change code to accommodate the change, it is BREAKING. Test against all known callers in consumer_list.

2. **Missing reverse drift.** Spec was updated, implementation was not. This is the most common drift pattern. Always run the drift detector on the post-change implementation.

3. **Loop-back ignored.** When loop_back_required = true, a human must coordinate consumer migration before deployment. Do not suppress this signal.
