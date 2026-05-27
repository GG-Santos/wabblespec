# Cold-Start Behavior — Rollback

Defines what Rollback does when its expected upstream artifacts are absent.

## Absent: rollback target receipt

Condition: The receipt ID declared as the rollback target does not exist.
Detection: File read returns 404 for the target receipt path.
Action: Surface DEPENDENCY error — cannot roll back to a state that has no receipt anchor. Do not attempt to infer a rollback target.
Do NOT: Roll back to "the previous state" without a specific receipt ID.

## Absent: worktree

Condition: No worktree has been created for this rollback operation.
Detection: `worktree_path` is null in the operation plan.
Action: Create a worktree per `rules/worktree-policy.md` Type 4 before proceeding. Rollback must not operate on the main working tree.
Do NOT: Execute a Type 3 or Type 4 rollback without worktree isolation.

## Absent: prior receipts

Condition: No wave receipts exist — Rollback called before any execution.
Detection: No `wave-*-receipt.json` in `.wabblespec/receipts/`.
Action: Surface DEPENDENCY error — Rollback requires a prior successful wave to roll back to. There is no state to restore on a fresh project.
Do NOT: Attempt rollback when no prior wave has completed.

## Default state on cold start

| Field | Default |
|---|---|
| `worktree_isolation` | required (Type 4 for any multi-file rollback) |
| `dry_run` | true (conservative — disable explicitly to commit rollback) |
| `rollback_type` | null — must be declared (Type 1/2/3/4 per worktree-policy.md) |
| `validation_after` | required — run Guard after rollback completes |
