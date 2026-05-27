# Plan — Acceptance Criteria

## BLOCK: absent Propose recommendation

Given Plan is invoked but no Propose receipt or recommendation exists,
Then Plan surfaces: "Plan requires a Propose recommendation. Run Propose first. If Propose produced a tie, invoke Brainstorm to resolve it before Plan."
Then Plan does not begin planning without a declared approach.
Then no plan artifact is written.

## BLOCK: absent recipe.json

Given Plan is invoked but recipe.json is not found,
Then Plan blocks and surfaces: "Plan requires recipe.json. Recipe must run before Plan to establish target and complexity."
Then Plan does not infer complexity or target from the user message alone.
Then no plan artifact is written.

## Happy path: Medium complexity

Given Propose has produced a recommendation and recipe.json declares complexity = Medium,
When Plan runs,
Then at least 2 expert perspectives are applied (Architecture, Security, Operability, Performance, Maintainability).
Then open risks identified during expert review are listed in the plan artifact.
Then a plan artifact is written to `.wabblespec/plans/plan-<timestamp>.md`.
Then a receipt is written to `.wabblespec/receipts/plan-receipt-<timestamp>.json`.
Then `adversary_triggered` is false (budget gate does not fire at Medium complexity without additional triggers).

## Adversary: mandatory at High complexity

Given recipe.json declares complexity = High,
When Plan evaluates the budget gate,
Then `adversary_triggered` is true.
Then Adversary is invoked in `challenger_mode: "spec-bound"`.
Then Grader is invoked with the Adversary receipt, plan artifact, and spec artifact.
Then `grader_score` and `grader_verdict` are recorded in the receipt.

## Adversary: mandatory for security/infra/irreversible scope

Given recipe.json declares complexity = Low or Medium BUT the plan touches security, infrastructure, or irreversible scope,
When Plan evaluates the budget gate,
Then `adversary_triggered` is true regardless of complexity level.

## Grader REVISE cycle

Given Grader returns REVISE,
When Plan processes the verdict,
Then Plan revises the plan artifact (maximum 3 revision cycles).
Then if REVISE persists after 3 cycles, Plan escalates to the user.

## go/no-go: BLOCKING risk blocks GO

Given any open risk is rated BLOCKING,
When Plan issues the go/no-go verdict,
Then Plan does not issue GO.
Then Plan issues CONDITIONAL (with conditions listed) or NO_GO.
Then `human_escalation_required` in the receipt is true.

## go/no-go: NO_GO surfaces to user

Given Plan issues NO_GO,
Then the user is notified with clear rationale.
Then Decompose is not invoked until the user resolves the NO_GO.

## Expert perspectives: minimum 2

Given any Plan run,
Then at least 2 expert perspectives are applied and recorded in the receipt.
Then `expert_perspectives_applied` in the receipt lists the perspectives by name.

## Absent rules files: fallback

Given `rules/expert-roles.md` is missing,
When Plan runs,
Then Plan applies SKILL.md expert perspective set.
Then the receipt logs: "expert-roles.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Plan run,
Then the receipt contains: `plan_options_count`, `chosen_approach_summary`, `expert_perspectives_applied`, `adversary_triggered`, `grader_score`, `grader_verdict`, `open_risks`, `go_no_go`, `plan_artifact_path`, `human_escalation_required`.
Then `grader_score` and `grader_verdict` are null when `adversary_triggered` is false.
