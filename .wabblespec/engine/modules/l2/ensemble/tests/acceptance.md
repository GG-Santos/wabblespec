# Ensemble — Acceptance Criteria

## BLOCK: self-activation

Given Ensemble is invoked by any module other than ModelRouter,
Then Ensemble surfaces: "Ensemble is triggered by ModelRouter only — do not self-activate."
Then Ensemble does not run.
Then no receipt is written.

## BLOCK: no lanes declared

Given ModelRouter triggers Ensemble but provides no lane assignments,
Then Ensemble surfaces: "Ensemble requires at least two lanes to coordinate."
Then Ensemble does not proceed.
Then no receipt is written.

## Trigger condition 1: multiple build targets

Given a task spans multiple build targets simultaneously,
When ModelRouter evaluates Ensemble conditions,
Then ModelRouter triggers Ensemble with trigger condition 1.
Then Ensemble activates with the appropriate mode.

## Trigger condition 2: no single capability covers requirements

Given no single available capability covers all required capabilities for a task,
When ModelRouter evaluates Ensemble conditions,
Then ModelRouter triggers Ensemble with trigger condition 2.
Then Ensemble is assigned two or more lanes covering the required capabilities.

## Trigger condition 3: Attestation or Audit verification mode

Given the declared verification mode is Attestation or Audit,
When ModelRouter evaluates Ensemble conditions,
Then Cross-check mode is mandatory.
Then Ensemble is triggered by ModelRouter with Cross-check forced.
Then no other mode is accepted for Attestation or Audit.

## Trigger condition 4: confidence below 0.7

Given confidence is below 0.7 after initial single-lane routing,
When ModelRouter evaluates Ensemble conditions,
Then ModelRouter triggers Ensemble with trigger condition 4.
Then Cross-check mode is used.

## Sequential mode

Given Lane B requires Lane A's output before it can start,
When Ensemble runs Sequential mode,
Then Lane A completes first and its output is passed to Lane B.
Then Lanes are not run in parallel.
Then the combined receipt names both lanes and their individual outcomes.

## Independent mode

Given lanes produce separate artifacts with no output dependency between them,
When Ensemble runs Independent mode,
Then lanes run in parallel.
Then each lane produces its own artifacts.
Then the combined receipt names all lanes and their individual outcomes.

## Cross-check mode

Given Cross-check mode is active,
When both lanes run the same task independently,
Then both lanes receive the same task input and run without knowledge of the other lane's output.
Then Grader (from Reviewer) compares outputs.
Then if lanes agree, `cross_check_agreement: true` is recorded.
Then if lanes disagree, `cross_check_agreement: false` is recorded and the result routes to Reviewer.

## One combined receipt

Given any Ensemble run,
Then one combined receipt is written — not a separate receipt per lane.
Then the combined receipt contains: `mode`, `lanes` (with capability, outcome, and artifacts per lane), `combined_outcome`, `cross_check_agreement`.
Then `combined_outcome` is PASS only when all lanes required for the task are PASS.

## Do NOT

Given any Ensemble run,
Then Ensemble does not self-activate — ModelRouter triggers it.
Then Ensemble does not skip Cross-check for Attestation or Audit verification modes.
Then Ensemble does not write separate receipts per lane.

## Missing-rules fallback

Given `rules/task-shapes.md` or capability descriptor references are absent,
When Ensemble is triggered,
Then Ensemble logs: "rules/task-shapes.md absent — using declared capabilities from trigger context."
Then Ensemble proceeds with the capabilities provided by ModelRouter.

## Receipt fields

Given any successful Ensemble run,
Then the combined receipt contains: `module` (ensemble), `mode`, `lanes` (array with `capability`, `outcome`, `artifacts`), `combined_outcome`, `cross_check_agreement`.
