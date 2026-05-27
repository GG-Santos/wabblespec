# Cold-Start Behavior — Apply

Defines what Apply does when its expected upstream artifacts are absent.

## Absent: delta plan

Condition: No delta plan or patch input when Apply runs.
Detection: No `--patch` input and no executor wave plan referencing Apply.
Action: Surface DEPENDENCY error — Apply requires a delta to apply. It does not derive changes from scratch.
Do NOT: Write files without an explicit, reviewed delta as input.

## Absent: prior receipts

Condition: `executor` or wave receipt absent — Apply called without a completed planning chain.
Detection: Required stems missing.
Action: Surface DEPENDENCY error naming Executor. Apply is invoked from within an Executor wave — it should not run standalone without an active wave context.
Do NOT: Apply changes that have not passed Guard.

## Absent: target files (new file creation)

Condition: Target file for a patch does not exist.
Detection: File read returns 404 for patch target.
Action: If the delta declares a create operation, create the file. If the delta declares an edit operation against a non-existent file, surface DEPENDENCY error — target file must exist for an edit.
Do NOT: Silently create files when the delta declares an edit.

## Default state on cold start

| Field | Default |
|---|---|
| `scope_class` | `LOCAL` (conservative; `BOUNDARY` requires explicit declaration from Specify) |
| `dry_run` | false (Apply is a write operation; Guard already validated it) |
| `rollback_target` | prior wave receipt (Rollback handles if Apply fails mid-wave) |
