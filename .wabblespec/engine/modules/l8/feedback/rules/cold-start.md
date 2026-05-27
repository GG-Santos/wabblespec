# Cold-Start Behavior — Feedback

Defines what Feedback does when its session data or metrics are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Feedback requires L8 corpus gate (100+ PASS receipts)."

## Absent: session receipts to analyze

Condition: No completed session receipts to evaluate.
Detection: `.wabblespec/state/receipts/` empty or all receipts in-progress.
Action: Surface: "No completed session data to analyze. Feedback operates on completed runs."

## Absent: --metrics flag declaration

Condition: Feedback invoked without specifying which metrics to evaluate.
Detection: No metric targets in invocation.
Action: Surface: "Specify metrics: token usage, latency, quality score, cost, error rate, or combination."
Do NOT: Analyze all metrics without direction — Feedback is targeted, not exhaustive.

## Absent: prior Feedback receipt (for trend analysis)

Condition: No prior feedback receipt.
Action: Treat as first run. Trend analysis unavailable. Report current-period metrics only.

## Absent: --budget flag (for cost analysis)

Condition: Cost metric requested but no budget declared.
Detection: Cost target absent.
Action: Surface: "Cost feedback requires a declared budget. Specify: per-call, per-user-action, or monthly budget target."

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate |
| `analysis_period` | Last 30 days (or all receipts if fewer than 30 days of data) |
| `trend_available` | false on first run |
| `metrics` | Not declared — must be specified |
| `output` | Feedback report — informational, not actionable directives |
