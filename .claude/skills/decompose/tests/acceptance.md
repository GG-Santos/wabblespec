# Decompose — Acceptance Criteria

## BLOCK: absent specify receipt

Given `specify-receipt.json` is absent or has status FAIL,
When Decompose is invoked,
Then Decompose stops and surfaces the issue to the user, routing back to Specify.
Then Decompose does not generate a wave plan from the user's raw task description.
Then no wave plan is written.

## BLOCK: absent upstream receipts

Given `recipe-receipt.json` or `scopeframe-receipt.json` is absent,
When Decompose is invoked,
Then Decompose surfaces a DEPENDENCY error naming the missing upstream module.
Then Decompose does not proceed without the planning chain intact.

## Happy path: Medium complexity wave plan

Given a locked task card and complexity = Medium (from recipe.json),
When Decompose runs,
Then 2–4 waves are produced.
Then each wave declares: inputs, expected outputs, checkpoint condition, rollback target, and verification mode.
Then Wave 1 has `rollback_to: null`.
Then each subsequent wave's rollback target is the previous wave's checkpoint.
Then the wave plan is written to `.wabblespec/plans/current-wave-plan.md`.
Then the wave plan is routed to Reviewer.
Then a decompose receipt is written with: `wave_count`, `complexity_confirmed`, `reviewer_triggered: true`, `rollback_checkpoints`.

## Wave independence requirement

Given any wave plan,
Then each wave produces at least one independently verifiable artifact.
Then no wave depends on partial output of another wave.
Then foundation artifacts (schema, data model) precede integration artifacts (API, business logic).

## Rollback target selection: worktree

Given complexity = High AND a wave contains irreversible operations AND the project is a git repo,
When Decompose assigns rollback targets,
Then `rollback_type: worktree` is assigned to that wave.
Then if any of the three conditions is not met, `wave-checkpoint` is assigned instead.
Then Decompose does not assign `worktree` speculatively.

## Verification mode: strongest applicable

Given a wave that produces runnable code with automated assertions possible,
When Decompose assigns verification mode,
Then `Test` mode is assigned (not `Observation`).
Then weaker modes (Observation, Audit) are only used when Test is not applicable.

## Wave count: Low complexity

Given complexity = Low,
When Decompose produces a wave plan,
Then 1–2 waves are produced.
Then more than 2 waves for Low complexity is considered over-engineering.

## Wave count: more than 8 waves

Given complexity = High and the decomposition produces more than 8 waves,
When Decompose prepares the plan,
Then user confirmation is required before writing the plan.
Then Decompose does not write a plan with more than 8 waves without confirmation.

## Reviewer routing

Given any wave plan produced by Decompose,
Then the wave plan is routed to Reviewer before Executor starts.
Then `reviewer_triggered` in the receipt is true.

## Absent rules files: fallback

Given `recipe.json` declares complexity but no `plan-completeness.md` exists,
When Decompose runs,
Then Decompose proceeds with SKILL.md defaults.
