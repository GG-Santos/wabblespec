# Cold-Start Behavior — Flag

Defines what Flag does when its feature flag system or rollout config are absent.

## Absent: feature flag system declaration

Condition: Flag invoked but no flag management system declared (no LaunchDarkly, Unleash, custom system, or environment variable strategy).
Detection: No flag system in spec or invocation.
Action: Surface: "Flag requires a declared flag management system. Specify: LaunchDarkly, Unleash, environment variable, database-backed, or other."
Do NOT: Implement a flag without knowing where it lives.

## Absent: flag-lifecycle.md

Condition: `rules/flag-lifecycle.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md flag lifecycle rules. Log: "flag-lifecycle.md missing — using SKILL.md defaults."

## Absent: rollout-gate.md

Condition: `rules/rollout-gate.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md rollout gate rules. Log: "rollout-gate.md missing — using SKILL.md defaults."

## Absent: removal date / cleanup plan

Condition: Flag is being created but no removal date or cleanup condition is declared.
Detection: Invocation has no expiry or cleanup declaration.
Action: FLAG: "Feature flag has no declared removal date or cleanup condition. Flags without expiry accumulate indefinitely. Declare: removal date, removal trigger (e.g., 100% rollout stable for 7 days), or explicit 'permanent flag' justification."
Do NOT: Block flag creation — flag and require declaration before implementation.

## Absent: rollout target declaration

Condition: Flag invoked without specifying initial rollout percentage or target segment.
Action: Surface: "Specify rollout target: percentage (e.g., 5%), user segment, or boolean on/off."

## Default state on cold start

| Field | Default |
|---|---|
| `initial_rollout` | Not declared — must be specified |
| `flag_type` | release (default); override if: experiment, ops, permission |
| `cleanup_required` | true — all release flags have a removal date |
| `kill_switch` | true — all flags must be disableable without code deploy |
| `flag_system` | Not declared — must be specified |
