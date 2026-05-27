# Sharpen — Acceptance Criteria

## BLOCK: unambiguous input

Given Sharpen is invoked but the input statement has only one clear interpretation,
When breadth detection finds a single clear interpretation,
Then Sharpen surfaces: "Input appears unambiguous — no sharpening needed. Confirm or provide a broader statement to sharpen."
Then Sharpen does not artificially generate alternative interpretations.
Then no receipt is written for an unnecessary sharpening.

## Happy path: broad input resolved

Given a broad input statement is provided (triggered by Recipe with `input_broad = true`),
When Sharpen runs,
Then 2–3 genuinely distinct, plausible interpretations are produced.
Then each interpretation is written as a one-sentence summary with a confidence score (0.0–1.0).
Then interpretations are ranked by specificity, feasibility, and user signal strength.
Then the interpretations are presented to the user for selection.
Then after selection, the sharpened input is written to `.wabblespec/sharpen/sharpened-<timestamp>.md`.
Then the sharpen receipt is written to `.wabblespec/state/receipts/sharpen-receipt-<timestamp>.json`.
Then `broad_resolved` in the receipt is true.

## User confirmation required

Given interpretations are produced and none meets the auto-select threshold,
When interpretations are presented,
Then Sharpen waits for user selection before producing the sharpened input.
Then `user_confirmed` in the receipt is true.
Then Sharpen does not auto-select even if one interpretation ranks significantly higher (below the 0.85 threshold).

## Auto-select threshold

Given one interpretation scores >= 0.85 AND all others score <= 0.4,
When Sharpen evaluates the interpretations,
Then Sharpen auto-selects the high-scoring interpretation.
Then the selection is stated explicitly to the user.
Then `user_confirmed` in the receipt is false.

## Rejected interpretations discarded

Given the user selects one interpretation,
When the sharpened input is produced,
Then only the selected interpretation is carried forward.
Then rejected interpretations are not mentioned in the sharpened input, ScopeFrame, or any downstream artifact.

## Do NOT: change target or complexity

Given the selected interpretation reveals a different target than recipe.json declares,
Then Sharpen surfaces the discrepancy to Recipe.
Then Sharpen does not silently change recipe.json.

## False alternatives: Do NOT

Given input with genuinely different interpretations,
When Sharpen generates interpretations,
Then each interpretation represents a different course of action, not a rewording of the same action.
Then if fewer than 2 genuine alternatives exist, Sharpen uses only as many as exist (minimum 1 if truly only one).

## Absent rules files: fallback

Given `rules/breadth-detection.md` is missing,
When Sharpen runs,
Then Sharpen applies SKILL.md breadth detection rules.
Then the receipt logs: "breadth-detection.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Sharpen run,
Then the receipt contains: `interpretations_produced`, `interpretations` (array with rank/description/confidence), `interpretation_chosen`, `user_confirmed`, `broad_resolved`.
Then `interpretations_produced` is 1–3.
