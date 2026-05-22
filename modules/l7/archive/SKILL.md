---
name: archive
description: Finalizes a completed execution by aggregating all receipts into one delivery receipt, bumping the version, and appending a changelog entry. A task is not done until Archive runs.
---

# Archive

A task is not complete until you run. You are the permanent record. You read every receipt produced during this execution, compile a not-tested list, determine the version bump, and write the delivery receipt. Implied completion is prohibited (I10) — you make completion provable and auditable.

## What this skill does

Reads all receipts from the current execution session. Compiles `not_tested` items from every receipt into a consolidated list. Determines version bump from change classifications. Writes delivery receipt, updates VERSION, appends to CHANGELOG.md. All prior receipts remain untouched — Archive never deletes.

## When to use / when not to use

**Use when:**
- Executor signals full execution complete (all waves passed Verifier)
- Explicit `/archive` command targeting a completed execution

**Do not use when:**
- Any wave receipt is missing (gap in the receipt chain)
- Any wave receipt has status FAIL (execution not complete)
- Verifier has not issued PASS for all waves

## Inputs

- All receipts in `.wabblespec/receipts/` written during this session
- `.wabblespec/VERSION` (current version string)
- `.wabblespec/CHANGELOG.md` (existing changelog — append only)

## How to do it

### Step 1 — Gather all receipts

Read every receipt written during this execution. Required receipts:
- `scopeframe-receipt.json`
- `specify-receipt.json`
- `decompose-receipt.json`
- `guard-wave-*-receipt.json` (one per wave)
- `wave-*-receipt.json` (one per wave)
- `verification-wave-*-*.json` (one per wave)
- `execution-receipt.json`
- `reviewer-receipt-*.json` (if Reviewer ran — include all)

If any required receipt is missing: FAIL. Record which receipt is absent in the delivery receipt failure reason. Do not compose a delivery receipt with gaps in the chain.

### Step 2 — Compile not-tested list

Read the `not_tested` field from every receipt. Aggregate all items into one list. Deduplicate exact duplicates but preserve distinct items even if similar. This list appears verbatim in the delivery receipt.

No items are minimized, summarized away, or hidden. Delivery is not blocked by not-tested items — they are recorded, not resolved. They become the starting scope for the next related session.

### Step 3 — Determine version bump

Read all receipts for change classification signals:
- Any `BREAKING` deviation found in any receipt → major version bump (x.0.0)
- Only `ADDITIVE` deviations, no BREAKING → minor version bump (0.x.0)
- Only `COSMETIC` deviations, or no deviations at all → patch bump (0.0.x)

### Step 4 — Append changelog entry

Append to `.wabblespec/CHANGELOG.md`. Never overwrite existing entries.

```markdown
## [new-version] — ISO-8601-timestamp

### Changed
- <BREAKING or ADDITIVE items from wave receipts>

### Fixed
- <COSMETIC or correction items>

### Not Tested
- <aggregated not-tested list — verbatim>

### Receipts
- execution-receipt: .wabblespec/receipts/execution-receipt.json
- waves: <N> planned, <N> completed, <N> failed
- verification: all waves PASS
```

### Step 5 — Bump VERSION

Read `.wabblespec/VERSION`. Increment the correct semver component. Write the new version string back.

### Step 6 — Write delivery receipt

Write to `.wabblespec/receipts/delivery-receipt-<timestamp>.json`. This is the master I10 record for this execution.

### Step 7 — Report to user

Surface: version bumped from X to Y, N receipts aggregated, not-tested count. Provide delivery receipt path. If not-tested list is non-empty, name the items — they are actionable future scope.

## Output contract

**delivery-receipt** (`.wabblespec/receipts/delivery-receipt-<timestamp>.json`):

Base receipt schema. Extension fields:
```json
{
  "receipts_aggregated": "integer",
  "not_tested_items": "integer",
  "version_previous": "string",
  "version_new": "string",
  "version_bump_reason": "BREAKING|ADDITIVE|COSMETIC",
  "waves_completed": "integer",
  "all_waves_passed": "boolean"
}
```

**VERSION** (`.wabblespec/VERSION`): plain text semver string, e.g. `0.2.0`. Single line, no trailing newline needed.

**CHANGELOG.md** (`.wabblespec/CHANGELOG.md`): append-only. New entry prepended at top (most recent first) or appended at bottom — be consistent with any existing format. Never modify existing entries.

## A note on common failure modes

1. **Declaring complete with missing receipts.** Count the expected receipts before composing the delivery receipt. One missing wave receipt means the execution chain is broken. Surface the gap rather than composing a partial delivery receipt.

2. **Hiding not-tested items.** If a receipt says `not_tested: ["edge case X", "performance under load"]`, those appear in the delivery receipt exactly as written. Never summarize them. The not-tested list is how future sessions know what was deferred.

3. **Treating Archive as optional admin.** Archive is the completion gate. A session that ends without an Archive receipt did not officially complete. The hook in `.claude/settings.json` will surface this as a missing receipt at the next session start.
