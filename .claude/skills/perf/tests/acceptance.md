# Perf — Acceptance Criteria

## BLOCK: absent performance target

Given Perf is invoked without declaring what to measure or optimize,
Then Perf surfaces: "Perf requires a declared target. Specify: metric (latency / throughput / memory / CPU / bundle size), current baseline, and target threshold."
Then Perf does not optimize without a declared metric and target.
Then no receipt is written.

## BLOCK: no baseline measurement

Given Perf is invoked but no prior baseline exists for the declared metric,
When Perf attempts to optimize,
Then Perf surfaces: "No baseline found. Perf will establish the baseline on this run — no optimization can occur without one. Run again after baseline is established."
Then no optimization is applied on the first run.
Then `baseline_measured` in the receipt is true only after baseline is successfully measured.

## baseline_measured invariant

Given any Perf run,
Then if `baseline_measured` is false in the receipt, the receipt status is FAIL.
Then optimization is never applied when `baseline_measured` is false.

## Happy path: baseline then optimize

Given a baseline is measured on a first run,
When Perf is run again with the baseline available,
Then Perf applies the platform budget from rules/budget-definition.md.
Then profiling identifies the highest-contribution bottleneck to the budget gap.
Then exactly one optimization is applied at a time.
Then performance is measured again after the optimization.
Then `regressions_detected` is recorded.
Then the receipt is written to `.wabblespec/receipts/perf-receipt-<timestamp>.json`.
Then the baseline is written to `.wabblespec/perf/baseline-<timestamp>.json`.

## One optimization at a time

Given Perf identifies multiple bottlenecks,
When optimizations are applied,
Then only one optimization is applied per cycle.
Then measurement occurs after each optimization before the next is applied.
Then Perf does not batch optimizations.

## Regression detection

Given an optimization improves the targeted metric but degrades another (e.g., P95 latency improves but memory doubles),
When Perf checks for regressions,
Then the regression is detected and `regressions_detected` is incremented.
Then the tradeoff is surfaced to the user before proceeding.

## Profiling tool unavailable

Given the required profiling tool is not available in the environment,
When Perf runs,
Then Perf surfaces: "Profiling tool [name] not available."
Then Perf does not estimate performance without measurement.

## Absent rules files: fallback

Given `rules/budget-definition.md` is missing,
When Perf runs,
Then Perf applies SKILL.md performance budget rules.
Then the receipt logs: "budget-definition.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Perf run,
Then the receipt contains: `baseline_measured`, `platform_budget_applied`, `optimization_opportunities`, `estimated_improvement_pct`, `profiling_method`, `perf_baseline_path`, `regressions_detected`.
Then `regressions_detected` is 0 when no regressions occurred.
