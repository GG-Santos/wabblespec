---
name: enhance
description: Resolves vague input before it reaches ScopeFrame. Extracts intent across 9 dimensions. Asks at most 3 targeted clarifying questions. Triggered automatically by Recipe when input_vague = true.
---

# Enhance

Vague input produces bad specs. Bad specs produce bad execution. You catch vague input before it reaches ScopeFrame and resolve it into a statement specific enough to scope.

## What this skill does

Receives the opening user message (already classified as vague by Recipe). Scores it across 9 intent dimensions. Asks targeted clarifying questions for critical missing dimensions (max 3). Produces an enhanced input statement and writes an enhance receipt.

## When to use / when not to use

**Triggered by Recipe** when `input_vague = true` in Recipe's detection. Do not invoke directly unless you have independently confirmed the input is vague.

**Do not invoke when:**
- Input already has a named artifact, measurable outcome, named constraint, and scope boundary
- Recipe classified `input_vague = false`
- Input is broad but not vague (Sharpen handles broad)

## Inputs

- Opening user message (the vague statement to enhance)
- `recipe.json` (target + complexity, already locked — Enhance does not change these)

## How to do it

### Step 1 — Score the 9 intent dimensions

For each dimension, determine: Present (explicitly stated), Absent (not present), or Derived (inferred without explicit statement). See rules/intent-dimensions.md for dimension definitions.

| # | Dimension | Critical? |
|---|---|---|
| 1 | Task (what action to perform) | Yes |
| 2 | Target (named artifact — file, module, feature, service) | Yes |
| 3 | Format (output format expected — code, document, list, analysis) | Yes |
| 4 | Constraints (must-not, deadlines, resource limits, compatibility) | No |
| 5 | Input (what the user is providing as material to work from) | No |
| 6 | Context (background why this matters) | No |
| 7 | Audience (who will consume the output) | No |
| 8 | Success criteria (how user will know the output is good) | No |
| 9 | Examples (examples of what good looks like) | No |

Record each dimension as `present`, `absent`, or `derived`. Derived dimensions count as resolved — do not ask about them.

### Step 2 — Check critical dimension resolution

All three critical dimensions (Task, Target, Format) must be present or derived before Enhance exits. See rules/critical-dimensions.md.

If any critical dimension is absent and cannot be derived: that dimension requires a question.

### Step 3 — Ask clarifying questions (max 3)

Prioritize questions by criticality: critical dimensions first, then non-critical dimensions by most-likely-to-unblock-downstream order (Constraints, Success criteria, Input).

See rules/question-budget.md. Never ask more than 3 questions in one pass. If more than 3 dimensions are missing: ask about the 3 most critical; derive or leave non-critical dimensions for downstream resolution.

Write questions as a numbered list. Wait for user response before proceeding to Step 4.

### Step 4 — Produce enhanced input statement

Synthesize the original message + user responses into a specific enhanced input statement. This is the new input that ScopeFrame receives.

Enhanced input must contain:
- A named artifact (or explicit confirmation none is appropriate)
- A measurable or observable outcome
- At least one constraint or scope boundary (if none stated, use recipe.json target + complexity as implicit scope)

Do not invent specifics the user did not provide. If a dimension remains unclear after questions, state it as an open assumption in the enhanced input.

### Step 5 — Write receipt

Write to `.wabblespec/state/receipts/enhance-receipt-<timestamp>.json`. Schema: `modules/l1/enhance/schemas/enhance-receipt.schema.json`.

Pass enhanced input path to ScopeFrame as next step.

## Output contract

**enhance-receipt.json** (`.wabblespec/state/receipts/enhance-receipt-<timestamp>.json`):

Base receipt schema extended with fields per `schemas/enhance-receipt.schema.json`. Key extension fields:

```json
{
  "dimensions_present": ["array — dimensions explicitly present in original input"],
  "dimensions_absent": ["array — dimensions missing from original input"],
  "dimensions_derived": ["array — dimensions inferred without explicit user statement"],
  "critical_dimensions_resolved": "boolean — Task + Target + Format all present or derived",
  "questions_asked": "integer — 0 to 3",
  "questions_answered": "integer",
  "vague_resolved": "boolean — input is no longer vague after Enhance",
  "enhanced_input_path": ".wabblespec/enhance/enhanced-<timestamp>.md"
}
```

**enhanced-<timestamp>.md** (`.wabblespec/enhance/`): The enhanced input statement. ScopeFrame reads this instead of the original user message.

## A note on common failure modes

1. **Asking too many questions.** Max 3. More than 3 questions at once causes user fatigue. Prioritize ruthlessly — critical dimensions first.

2. **Inventing specifics.** Do not fill in what the user did not say. Mark absent non-critical dimensions as open assumptions in the enhanced input so ScopeFrame and downstream modules can surface them if needed.

3. **Changing target or complexity.** Enhance operates on input clarity only. The target and complexity locked by Recipe are not Enhance's to change. If enhanced input reveals a different target, surface it to Recipe — do not silently change recipe.json.

4. **Stopping early.** If critical dimensions remain absent after the question round, do not proceed to ScopeFrame. Surface the unresolved dimensions to the user before proceeding.
