---
name: wave-fix
description: Fix open wave review findings. Discovers findings from the wave-queue or a specific receipt, fixes them by severity order (CRITICAL→HIGH→MEDIUM→LOW, grouped by file), runs quality-floor-check, writes the resolution receipt to the main chain, and marks the job done in wave-queue. Use when the user asks to fix review findings, address open issues from the last review, or close a wave-review.
---

# wave-fix

Fix open findings from the most recent WabbleSpec wave review. Uses the existing
wave-queue and receipt chain — no separate tracking system.

## Usage

```
/wave-fix [ref]
```

## When NOT to use

- No `/wave-review` has run yet — run `/wave-review` first to discover findings
- User asks for a new review only (use `/wave-review`)
- Findings are already in the conversation — fix them directly without re-fetching

## Instructions

### 1. Discover open findings

Check conversation context first. If findings are present, skip fetch.

Otherwise, check wave-queue for FAIL entries:

```bash
python .wabblespec/engine/shared/scripts/wave-review.py --list --all
```

Read the receipt JSON for any FAIL entry to get the findings array.

### 2. Prioritize and fix

Sort: CRITICAL → HIGH → MEDIUM → LOW. Group by file within each tier.
Batch all edits to the same file together to minimize context switches.
Note any false positives explicitly — do not silently skip them.

### 3. Verify fixes

```bash
python .wabblespec/engine/shared/scripts/quality-floor-check.py
```

Fix any regressions before proceeding.

### 4. Write resolution receipt and close

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type wave-review \
  --task-id <task-id> --session-id <session-id> \
  --status PASS --target <ref> \
  --summary "Fixed <N> findings: <brief>" \
  --out .wabblespec/state/receipts/wave-review-fix-<ref>-<timestamp>.json

python .wabblespec/engine/shared/scripts/wave-review.py \
  --complete <ref> --verdict PASS \
  --receipt .wabblespec/state/receipts/wave-review-fix-<ref>-<timestamp>.json
```

**Closure ordering:** Close the original review set BEFORE treating any post-fix review
as the current state. The original finding set must be confirmed resolved first.

### 5. Update quality drawers

Mark the corresponding quality drawers as SUPERSEDED so Dream removes them from gap-map:

For each fixed HIGH/CRITICAL finding, find the drawer in `wings/quality/` matching
the ref and location, and set `staleness_state: SUPERSEDED`.

## See also

- `/wave-review` — run a new wave review
- `/wave-refine` — iterative fix-review loop
