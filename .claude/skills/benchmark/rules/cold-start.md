# Cold-Start Behavior — Benchmark

Defines what Benchmark does when its corpus gate or baseline data are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Benchmark requires L8 corpus gate (100+ PASS receipts)."

## Absent: baseline benchmark data

Condition: Benchmark invoked for the first time — no prior `benchmark-receipt.json`.
Detection: Receipt absent.
Action: Treat as baseline run. This run establishes the baseline — no comparison is possible yet. Log: "First benchmark run — establishing baseline."

## Absent: declared metric to benchmark

Condition: Benchmark invoked without specifying what to measure.
Action: Surface: "Benchmark requires a declared metric: latency, token count, cost, quality score, or task completion rate."
Do NOT: Benchmark without a declared metric.

## Absent: eval dataset

Condition: Benchmark requires an eval dataset but none exists.
Detection: No eval dataset at declared path.
Action: BLOCK benchmark for that metric. Surface: "Benchmark requires an eval dataset. Create a dataset (minimum size per evals.md) before benchmarking."

## Absent: benchmark-discipline.md or outcome-requirement.md

Condition: Rule files missing.
Detection: File read returns 404.
Action: Apply SKILL.md benchmark rules. Log: "Benchmark rule file missing — using SKILL.md defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate |
| `baseline` | null on first run — established by first complete run |
| `regression_threshold` | 10% degradation from baseline triggers regression flag |
| `metric` | Not declared — must be specified |
| `comparison` | null on first run; prior baseline receipt on subsequent runs |
