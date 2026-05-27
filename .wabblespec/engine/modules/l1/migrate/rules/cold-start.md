# Cold-Start Behavior — Migrate

Defines what Migrate does when its expected upstream artifacts are absent.

## Absent: migration source artifact

Condition: No source schema, config, or data structure to migrate from when Migrate runs.
Detection: Referenced source artifact path returns 404.
Action: Surface DEPENDENCY error naming the missing source artifact. Migrate cannot plan a migration without a declared source state.
Do NOT: Generate a migration plan based on the destination schema alone.

## Absent: prior receipts

Condition: `specify-receipt.json` absent — migration target not spec'd.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Specify. Migrate needs a declared target state before it can plan the delta.
Do NOT: Migrate toward an undefined target.

## Default state on cold start

| Field | Default |
|---|---|
| `migration_type` | null — must be declared (schema / config / data / code) |
| `rollback_plan` | required — Migrate does not run without a declared rollback path |
| `dry_run` | true (conservative default; disable explicitly to apply changes) |
| `validation_step` | required after each migration wave |
