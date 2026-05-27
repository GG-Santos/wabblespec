# Feedback — Acceptance Criteria

## L8 corpus gate

Given receipt count in .wabblespec/state/receipts/ is fewer than 100 PASS,
When Feedback is invoked,
Then Feedback exits and outputs "GATE_NOT_MET" with the current count.
Then no feedback file is written.

## Required inputs

Given human provides observed_behavior and expected_behavior and module,
When Feedback is invoked,
Then feedback-{timestamp}.json is written to .wabblespec/state/memory/feedback/.

Given human does not provide expected_behavior,
When Feedback is invoked,
Then Feedback surfaces "expected_behavior is required" and writes nothing.

Given human does not provide module,
When Feedback is invoked,
Then Feedback surfaces "module is required — which module exhibited this behavior?" and writes nothing.

Given module name provided does not match any known module ID in framework.yaml,
When Feedback is invoked,
Then Feedback surfaces the unrecognized module ID and lists the closest matches.
Then Feedback does not write until a valid module ID is confirmed.

## Required --metrics flag

Given Feedback is invoked without --metrics flag,
Then Feedback surfaces "specify metrics: token_usage, latency, quality_score, cost, error_rate, or combination."
Then no feedback file is written.

Given Feedback is invoked with --metrics quality_score,
Then the feedback file includes metric: "quality_score".
Then the analysis covers quality score observations only.

Given Feedback is invoked with --metrics cost,budget=50.00,
Then the feedback file includes budget_target: 50.00.
Then the analysis includes whether cost observations are within budget.
Then observations exceeding budget are flagged in the report.

Given Feedback is invoked with --metrics latency,
Then the analysis includes p50 and p95 latency observations from available receipts.
Then latency values are derived from receipts, not assumed.

## Feedback content requirements

Given any feedback-{timestamp}.json written,
Then it contains all required fields: feedback_id, created_at, observed_behavior, module, expected_behavior, metrics, instinct_signal, status.
Then status is "open".
Then instinct_signal is true.
Then feedback_id is unique (timestamp-based or UUID — not sequential integer).

## Observation-only constraint

Given human submits prescriptive feedback ("module X should do Y differently"),
When Feedback processes it,
Then Feedback rephrases as "observed: [current behavior], expected: [desired behavior]" before writing.
Then the reframe is shown to the human for confirmation before writing.
Then the stored feedback uses observational language, not prescriptive.

## Trend analysis

Given a prior feedback receipt exists for the same module and metric,
When Feedback runs,
Then the report includes a trend section comparing current observation to prior.
Then the trend direction is declared: improving, degrading, stable, or insufficient_data.

Given no prior feedback receipt for this module exists,
When Feedback runs,
Then the report notes "First observation for this module — no trend available."
Then instinct_signal is still true.

## Analysis period

Given no --period flag,
Then Feedback analyzes all available receipts.
Then the report states the analysis window: "All [n] receipts from [earliest] to [latest]."

Given --period 30d,
Then only receipts from the last 30 days are included in the analysis.
Then the report states the bounded window.

Given --period 30d but fewer than 5 receipts exist in that window,
Then Feedback surfaces "insufficient data: [n] receipts in period (minimum 5 for reliable analysis)."
Then the feedback file is still written with the available data, noting the limitation.

## Duplicate detection

Given an existing open feedback item with the same module and observed_behavior (similarity > 90%),
When Feedback is about to write,
Then Feedback surfaces the potential duplicate IDs to the human before writing.
Then Feedback does not auto-merge — human decides whether to write a new item or link to existing.

Given no similar existing feedback,
When Feedback writes,
Then no duplicate warning is shown.

## No automatic downstream trigger

Given any feedback item written,
Then no Synth candidate is created automatically.
Then no Blueprint is created automatically.
Then the feedback item status remains "open" until Instinct processes it.
Then Feedback does not invoke Instinct.

## Boundary enforcement

Given any Feedback invocation,
Then no file in modules/ is created or modified.
Then no receipt in .wabblespec/state/receipts/ is created or modified.
Then no framework.yaml entry is changed.
Then only .wabblespec/state/memory/feedback/ receives new files.

## Dry-run

Given --dry-run flag,
Then Feedback prints the analysis summary and observation count to stdout.
Then no feedback-{timestamp}.json is written.
Then any duplicate warnings are still shown (so human can see them before committing).
