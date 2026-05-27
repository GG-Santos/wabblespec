# Cold-Start Behavior — Ensemble

Defines what Ensemble does when its expected upstream artifacts are absent.

## Absent: module outputs to combine

Condition: No outputs from parallel sub-agents when Ensemble attempts synthesis.
Detection: Expected sub-agent receipts absent.
Action: Surface DEPENDENCY error naming each expected sub-agent. Ensemble synthesizes — without sub-agent outputs, there is nothing to combine.
Do NOT: Synthesize from a single agent output (that is not ensemble work).

## Absent: prior receipts

Condition: `decompose-receipt.json` absent — ensemble wave plan not declared.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Decompose. Ensemble runs within an Executor wave plan — without a wave plan declaring parallel sub-tasks, Ensemble has no mandate.
Do NOT: Activate Ensemble speculatively for any parallel work.

## Default state on cold start

| Field | Default |
|---|---|
| `synthesis_strategy` | `merge-deduplicate` (conservative; override declared in wave plan) |
| `conflict_resolution` | `surface-to-human` (conflicts are not auto-resolved) |
| `quorum` | all sub-agents must complete (no partial synthesis by default) |
