---
name: sharpen
description: Resolves broad input before it reaches ScopeFrame. Surfaces competing interpretations, ranks them, and confirms the user's intended interpretation. Triggered automatically by Recipe when input_broad = true.
---

# Sharpen

Broad input produces scope drift. When the user's intent splits across multiple plausible interpretations at equal weight, scope cannot be locked until one interpretation is chosen. You surface the interpretations, rank them, and confirm the right one.

## What this skill does

Receives the opening user message (already classified as broad by Recipe). Identifies competing interpretations of user intent (up to 3). Ranks them by specificity, feasibility, and available user signals. Presents them to the user for confirmation or selection. Produces a sharpened input statement and delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| Sharpen receipt write (Step 5) | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type sharpen` |

## When to use / when not to use

**Triggered by Recipe** when `input_broad = true` in Recipe's detection. Do not invoke directly unless you have independently confirmed the input is broad.

**Do not invoke when:**
- Input has only one plausible interpretation at ≥ 0.5 confidence
- Recipe classified `input_broad = false`
- Input is vague but not broad (Enhance handles vague; both can run in sequence when vague AND broad)

## Inputs

- Opening user message (the broad statement to sharpen)
- `recipe.json` (target + complexity, already locked — Sharpen does not change these)
- Enhance output (if Enhance ran first — use the enhanced input, not the original)

## How to do it

### Step 1 — Identify competing interpretations

Generate up to 3 distinct, plausible interpretations of user intent. Each interpretation must:
- Be genuinely different from the others (not just rewordings)
- Score ≥ 0.5 confidence as a valid reading of the user's message
- Be actionable — could become a task card if selected

Do not generate more than 3. If only 2 plausible interpretations exist, use 2. See rules/breadth-detection.md for how to detect and bound interpretations.

### Step 2 — Rank interpretations

Rank by: specificity (more specific → higher), feasibility given declared target + complexity, strength of user signal. See rules/interpretation-ranking.md.

Write each interpretation as a one-sentence summary with a confidence score (0.0–1.0).

### Step 3 — Present to user and confirm

Present interpretations as a numbered list with brief descriptions. Ask the user to select one (or provide their own). Do not auto-select even if one interpretation ranks significantly higher — user confirmation is required.

**Exception:** If one interpretation scores ≥ 0.85 AND the other(s) score ≤ 0.4, auto-select the high-scoring interpretation, state the selection, and proceed. Record `user_confirmed: false` in the receipt.

### Step 4 — Produce sharpened input statement

Rewrite the original input (or enhanced input, if Enhance ran first) scoped to the confirmed interpretation. The sharpened statement becomes the input ScopeFrame receives.

Sharpened input must make explicit which interpretation was selected. Open alternatives (the non-selected interpretations) are discarded — do not carry them forward.

### Step 5 — Write receipt

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type sharpen \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --summary "<interpretation selected>" \
  --out .wabblespec/state/receipts/sharpen-receipt-<timestamp>.json
```

Pass sharpened input path to ScopeFrame as next step.

## Output contract

**sharpen-receipt.json** (`.wabblespec/state/receipts/sharpen-receipt-<timestamp>.json`):

Base receipt schema extended with fields per `schemas/sharpen-receipt.schema.json`. Key extension fields:

```json
{
  "interpretations_produced": "integer — 1 to 3",
  "interpretations": [
    {
      "rank": "integer",
      "description": "string",
      "confidence": "number 0.0–1.0"
    }
  ],
  "interpretation_chosen": "string — description of selected interpretation",
  "user_confirmed": "boolean — true if user selected; false if auto-selected",
  "broad_resolved": "boolean — input is no longer broad after Sharpen"
}
```

**sharpened-<timestamp>.md** (`.wabblespec/sharpen/`): The sharpened input statement. ScopeFrame reads this instead of the original (or enhanced) input.

## A note on common failure modes

1. **Generating false alternatives.** Do not produce interpretations that are essentially the same thing reworded. Each interpretation must represent a genuinely different course of action.

2. **Auto-selecting too aggressively.** The exception for auto-select is narrow (≥ 0.85 vs ≤ 0.4). When in doubt, ask. A wrong auto-selection sends the whole downstream chain in the wrong direction.

3. **Carrying forward rejected interpretations.** Once the user selects, the others are discarded. Do not mention them in ScopeFrame, Specify, or anywhere downstream. The selected interpretation is now the only reality.

4. **Changing target or complexity.** Sharpen operates on input clarity only. If the selected interpretation reveals a different target, surface it to Recipe — do not silently change recipe.json.
