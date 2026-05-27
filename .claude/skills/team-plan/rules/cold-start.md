# Cold-Start Behavior — Team Plan

Defines what Team Plan does when its expected upstream artifacts are absent.

## Absent: team configuration

Condition: No team config (agent roster, role assignments) when Team Plan runs.
Detection: No team config file in `.wabblespec/team/` or equivalent.
Action: Derive a default team from the recipe target and complexity level. For Low: 1 agent. For Medium: 2 agents. For High: 3+ agents. Log SOFT warning: `team_config: absent — using derived defaults`.
Do NOT: Block Team Plan because no prior team config exists — it is valid to plan a fresh team from scratch.

## Absent: decompose receipt

Condition: No `decompose-receipt.json` when Team Plan runs.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Decompose. Team Plan assigns agents to wave tasks — without a wave plan, there are no tasks to assign.
Do NOT: Plan a team without a wave plan structure.

## Default state on cold start

| Field | Default |
|---|---|
| `team_size` | derived from complexity (Low: 1, Medium: 2, High: 3) |
| `role_assignments` | all unassigned — must be declared before wave execution |
| `coordination_mode` | `sequential` (conservative; parallel requires explicit Ensemble declaration) |
