# Cold-Start Behavior — Perf

Defines what Perf does when its baseline metrics or performance budget are absent.

## Absent: performance target

Condition: Perf invoked without declaring what to measure or optimize.
Action: Surface: "Perf requires a declared target. Specify: metric (latency / throughput / memory / CPU / bundle size), current baseline, and target threshold."
Do NOT: Optimize without a declared metric and target.

## Absent: baseline measurement

Condition: Perf invoked but no prior measurement exists for the declared metric.
Detection: No prior perf receipt or baseline data.
Action: Surface: "No baseline found. Perf will establish the baseline on this run — no optimization can occur without one. Run again after baseline is established."
Do NOT: Invent a baseline. Measurement must precede optimization.

## Absent: budget-definition.md

Condition: `rules/budget-definition.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md performance budget rules. Log: "budget-definition.md missing — using SKILL.md defaults."

## Absent: measurement-first.md

Condition: `rules/measurement-first.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md measurement-first rules. Log: "measurement-first.md missing — using SKILL.md defaults."

## Absent: profiling tool or measurement infrastructure

Condition: Required profiling tool not available in environment.
Detection: Tool invocation fails.
Action: Surface: "Profiling tool [name] not available. Perf cannot measure [metric] without it. Install [tool] or declare an alternative."
Do NOT: Estimate performance without measurement.

## Default state on cold start

| Field | Default |
|---|---|
| `metric` | Not declared — must be specified |
| `baseline` | null — established on first run |
| `regression_threshold` | 10% degradation from baseline triggers flag |
| `measurement_before_optimize` | true — enforced invariant; no optimization without measurement |
| `profiling_tool` | Not declared — depends on platform and metric |
