# Triage — Acceptance Criteria

## BLOCK: absent issue description

Given no issue, bug report, or defect description is provided,
When Triage is invoked,
Then Triage asks the user for the issue description.
Then Triage does not invent defect scenarios to triage.
Then no triage record is written without a declared input.

## Happy path: issue classified and routed

Given an issue description is provided,
When Triage runs,
Then Memory is checked for prior triage records on the same topic before classifying.
Then severity is classified as one of: Critical, High, Medium, Low.
Then type is classified as one of: Bug, Feature, Debt, Question, Security.
Then routing is determined from the routing table.
Then a triage record is written to Memory as a FRESH drawer.
Then the issue is routed to the declared module with the triage record as context.
Then a receipt is written to `.wabblespec/state/receipts/`.

## Recurrence escalation

Given a prior triage record for the same topic exists (second occurrence),
When Triage classifies the issue,
Then severity is escalated one level above the base classification.

Given three or more prior triage records exist for the same topic,
When Triage classifies the issue,
Then severity is escalated to High minimum.
Then a Synth proposal is triggered.

## Security issues: gateway first

Given the issue type is Security (regardless of severity),
When Triage determines routing,
Then the Security gateway is the first route.
Then Security issues are never routed directly to any other module before the Security gateway.

## Routing table enforcement

Given any classified issue,
Then routing follows the declared routing table (Bug/Critical → Executor + Autopilot L3+; Bug/High → Interview → Specify → Executor; Feature → Interview → Specify → Propose → Decompose; Debt/COSMETIC → Clean; Question → Interview; Security → Security gateway).
Then Triage does not apply routing from memory — the routing table is consulted on each triage.

## No fixes: classify and route only

Given any Triage invocation,
Then Triage classifies and routes the issue only.
Then Triage does not apply fixes, write code, or modify spec artifacts.

## Triage without prior receipts: allowed with SOFT warning

Given `.wabblespec/state/receipts/` is empty (session start before Recipe),
When Triage is invoked for an urgent defect,
Then Triage runs and classifies the issue.
Then a SOFT warning is surfaced that Recipe should follow.
Then Triage is not blocked by absent receipts.

## Absent defect-patterns reference: proceed with warning

Given `.wabblespec/engine/shared/references/defect-patterns.md` is absent,
When Triage runs,
Then Triage proceeds with built-in pattern recognition.
Then the receipt logs: `defect_patterns_reference: absent` (SOFT warning).
Then the triage run is not blocked.

## Triage record required fields

Given any written triage record,
Then the record contains: `timestamp`, `severity`, `type`, `recurrence_count`, `source`, Description, Classification Rationale, Routing Decision (with `route_to` and `priority`), Prior Occurrences table.

## Do NOT: write triage records outside Memory

Given any Triage invocation,
Then triage records are written to Memory only.
Then no triage record is written to `.wabblespec/state/plans/` or product space.
