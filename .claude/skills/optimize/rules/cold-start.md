# Cold-Start Behavior — Optimize

Defines what Optimize does when its signal data or commands are absent.

## Absent: target to optimize

Condition: Optimize invoked without declaring what to optimize.
Action: Surface: "Optimize requires a target: prompt, context window, token budget, latency, or cost."
Do NOT: Optimize arbitrarily — always optimize against a declared metric.

## Absent: signal hierarchy

Condition: `rules/signal-hierarchy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md signal priority order. Log: "signal-hierarchy.md missing — using SKILL.md defaults."

## Absent: baseline measurement

Condition: Optimize invoked but no baseline metric is known.
Detection: No prior benchmark receipt, no declared current token count, no declared current latency.
Action: Surface: "Optimization requires a baseline. Provide: current metric value, target metric value, and acceptable trade-offs."
Do NOT: Optimize without knowing the starting point.

## Absent: commands file

Condition: `commands/optimize-commands.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md command set. Log: "optimize-commands.md missing — using SKILL.md defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `optimization_target` | Not declared — must be specified |
| `baseline_metric` | Not declared — must be provided |
| `trade_off_policy` | Quality first — do not sacrifice output quality for token reduction without explicit authorization |
| `diff_required` | true — show before/after for all changes |
| `revert_point` | Capture pre-optimization state before applying changes |
