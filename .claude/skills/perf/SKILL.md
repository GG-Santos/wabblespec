---
name: perf
description: Performance profiling, baseline measurement, and optimization. Measurement before optimization is mandatory. Platform budget definitions apply.
---

# Perf

No optimization without measurement. You establish a baseline, find real bottlenecks, and optimize against evidence. "It feels slow" is not a performance problem — a measured P95 above its budget is.

## What this skill does

Measures performance baseline. Identifies optimization opportunities against declared platform budgets. Applies optimizations with evidence. Checks for regressions. Writes perf receipt.

## When to use

- Performance complaint backed by a specific metric or symptom
- Pre-deployment performance gate (explicit in task card)
- Explicit `/perf` command
- Post-optimization regression check

## Do not use when

- No performance budget declared and no specific metric complaint — "make it faster" requires a measurable goal first

## Inputs

- Target system/function/endpoint
- Platform performance budget (from recipe.json target → `rules/budget-definition.md`)
- Profiling method (auto-selected by platform if not specified)

## How to do it

### Step 1 — Establish baseline (mandatory)

Measure current performance before any change. Record: P50, P95, P99 latency (or equivalent for platform), throughput, resource utilization. Write baseline to `.wabblespec/perf/baseline-<timestamp>.json`.

`baseline_measured: false` in receipt = FAIL. No optimization without baseline.

### Step 2 — Apply platform budget

Look up the declared budget for the detected platform from rules/budget-definition.md. Compare measured baseline to budget. Gaps = optimization opportunities.

### Step 3 — Profile and identify bottlenecks

Use platform-appropriate profiling method. Identify the actual bottleneck — not the slowest line of code, but the highest-contribution bottleneck to the budget gap.

### Step 4 — Optimize against evidence

Address the identified bottleneck. One optimization at a time. Measure after each change to confirm improvement. Do not batch optimizations — you cannot attribute improvement to cause.

### Step 5 — Check for regressions

After optimization: run baseline measurement again. Compare all metrics, not just the targeted one. An optimization that improves P95 latency but doubles memory usage may not be acceptable. Record `regressions_detected: integer`.

### Step 6 — Write receipt

## Output contract

**perf-receipt.json** (`.wabblespec/state/receipts/perf-receipt-<timestamp>.json`):

```json
{
  "baseline_measured": "boolean — must be true",
  "platform_budget_applied": "string — which platform budget was used",
  "optimization_opportunities": "integer",
  "estimated_improvement_pct": "number — null if unmeasurable",
  "profiling_method": "string",
  "perf_baseline_path": ".wabblespec/perf/baseline-<timestamp>.json",
  "regressions_detected": "integer — 0 is clean"
}
```
