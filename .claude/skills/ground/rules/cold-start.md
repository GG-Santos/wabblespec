# Cold-Start Behavior — Ground

Defines what Ground does when its expected upstream artifacts are absent.

## Absent: project codebase files

Condition: The target files referenced in a wave plan do not exist in the project.
Detection: File reads return 404 for paths listed in the wave plan.
Action: Flag each missing path as HALLUCINATION_RISK in the ground receipt. Do not proceed with validation of non-existent files.
Output: Ground receipt with `hallucination_count` equal to the number of missing paths.

## Absent: prior receipts

Condition: No receipts from upstream modules when Ground is called.
Detection: `.wabblespec/state/receipts/` empty or missing expected stems.
Action: Surface DEPENDENCY error naming the missing upstream module. Ground validates wave outputs — it requires a wave to have run first.
Do NOT: Validate an empty or hypothetical output.

## Default state on cold start

| Field | Default |
|---|---|
| `hallucination_count` | 0 (starts clean, increments per unverified reference) |
| `validation_scope` | all paths listed in the wave plan |
| `cross_reference_status` | PENDING until all paths verified |
