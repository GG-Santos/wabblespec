# Migrate — Acceptance Criteria

## BLOCK: absent Specify BREAKING delta receipt

Given `specify-receipt.json` is absent or has `delta_class` other than `BREAKING`,
When Migrate is invoked,
Then Migrate surfaces a DEPENDENCY error naming Specify.
Then Migrate does not activate without a BREAKING delta receipt.
Then no migration plan is written.

## BLOCK: absent source artifact

Given the source schema, config, or data structure to migrate from is not found at the declared path,
When Migrate runs,
Then Migrate surfaces a DEPENDENCY error naming the missing source artifact.
Then Migrate does not generate a migration plan based on the destination schema alone.

## Happy path: two-phase migration (default)

Given a Specify receipt with `delta_class: BREAKING`, `change_summary`, and `affected_specs`,
When Migrate runs,
Then `migration_type` is `two-phase` by default.
Then the migration plan declares Phase 1 (ADDITIVE — new alongside old, old deprecated) and Phase 2 (REMOVING — old removed after gate).
Then the migration plan is written to `.wabblespec/state/plans/migration-plan-<id>.md`.
Then Phase 1 is routed to Executor as an ADDITIVE wave.
Then Phase 2 is gated on human confirmation that all known consumers have migrated.
Then a receipt is written to `.wabblespec/state/receipts/`.

## Phase 2 gate: no auto-advance

Given Phase 1 has been executed and verified,
When Migrate evaluates the Phase 2 gate,
Then Phase 2 does not auto-advance.
Then human confirmation is required that consumers have migrated before Phase 2 executes.

## Single-phase exception: internal consumers only

Given all consumers are internal (no external API) OR the change is security-critical and cannot wait,
When Migrate determines migration type,
Then `migration_type` may be `single-phase`.
Then `single_phase_justification` is required and written to the migration plan.
Then single-phase without meeting exception criteria is not allowed.

## Automated migration script

Given the migration is automatable (deterministic transformation),
When Migrate produces the migration plan,
Then a migration script is written to `scripts/migrate/`.
Then if not automatable, manual steps are documented with the reason automation is not possible.

## Consumer migration guide

Given any migration plan,
Then a consumer-facing migration guide is written as input to the Document module.
Then the guide lists steps consumers must take to migrate from the old interface to the new one.

## Do NOT: execute migration

Given any Migrate invocation,
Then Migrate produces the plan only.
Then Migrate does not execute migration steps itself — that is Executor's role.

## Write location invariant

Given Migrate writes a migration script,
Then the script is written to `scripts/migrate/` only.
Then Migrate does not write scripts outside that path.

## Migration plan required fields

Given any produced migration plan,
Then the plan contains: `change_ref`, `generated_at`, `migration_type`, Phase 1 section, Phase 2 section with gate declaration, Migration Steps, and Rollback instructions.
Then `single_phase_justification` is present when `migration_type` is `single-phase`.
