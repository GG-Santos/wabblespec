# Enhance — Acceptance Criteria

## BLOCK: absent target artifact

Given Enhance is invoked without a declared target artifact (no spec, document, or artifact path),
Then Enhance surfaces: "Enhance requires a target artifact. Specify the spec, document, or output to enhance."
Then Enhance does not enhance an implied artifact without confirmation.
Then no receipt is written.

## Happy path: vague input resolved

Given a vague input statement is provided (triggered by Recipe with `input_vague = true`),
When Enhance runs,
Then all 9 intent dimensions are scored as present, absent, or derived.
Then critical dimensions (Task, Target, Format) are all present or derived before Enhance exits.
Then the enhanced input is written to `.wabblespec/enhance/enhanced-<timestamp>.md`.
Then the enhance receipt is written to `.wabblespec/state/receipts/enhance-receipt-<timestamp>.json`.
Then `vague_resolved` in the receipt is true.

## Question budget: maximum 3

Given more than 3 intent dimensions are absent,
When Enhance asks clarifying questions,
Then at most 3 questions are asked in one pass.
Then critical dimensions are prioritized over non-critical.
Then non-critical absent dimensions are recorded as open assumptions, not asked about in the first pass.

## Critical dimensions unresolved after questions

Given critical dimensions remain absent after the question round,
Then Enhance does not proceed to ScopeFrame.
Then Enhance surfaces the unresolved dimensions to the user before proceeding.

## Derived dimensions count as resolved

Given a dimension is inferable from context without an explicit user statement,
When Enhance processes it,
Then that dimension is recorded as `derived` in the receipt.
Then no question is asked about a derived dimension.

## Do NOT: change target or complexity

Given Enhance's enhanced input reveals a potentially different target than what recipe.json declares,
Then Enhance surfaces the discrepancy to Recipe.
Then Enhance does not silently change recipe.json.
Then `recipe.json` target and complexity remain unchanged after Enhance runs.

## Do NOT: invent specifics

Given a non-critical dimension is absent after questions,
Then Enhance records it as an open assumption in the enhanced input.
Then the enhanced input does not contain invented specifics the user did not provide.

## Absent rules files: fallback

Given `rules/intent-dimensions.md` is missing,
When Enhance runs,
Then Enhance applies SKILL.md intent dimension defaults.
Then the receipt logs: "intent-dimensions.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Enhance run,
Then the receipt contains: `dimensions_present`, `dimensions_absent`, `dimensions_derived`, `critical_dimensions_resolved`, `questions_asked`, `questions_answered`, `vague_resolved`, `enhanced_input_path`.
Then `questions_asked` is 0–3 (never exceeds 3).
