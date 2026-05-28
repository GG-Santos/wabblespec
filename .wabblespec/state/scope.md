# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T13:01:00Z
**session_id:** phase3-new-scripts-20260528

## In Scope

- Build `task-card-writer.py` — writes task-card.md from CLI args, eliminating manual JSON/Markdown construction
- Build `wave-plan-writer.py` — writes current-wave-plan.md from structured wave JSON input
- Build `scope-writer.py` — writes scope.md from CLI args (in-scope, out-of-scope, assumptions)
- Extend `guard-check.py` with a `chain` subcommand that validates the receipt chain for a session
- Update `script-delegation-contract.md` with entries for the three new writer scripts
- Add `--dry-run` and correct exit codes (0/1/2) to all four scripts

## Out of Scope

- SKILL.md updates to call the new scripts (Phase 2 pattern — separate session)
- Modifying existing guard-check.py authority/commands subcommands
- Integration testing across multiple sessions
- DuckDB receipt store (Phase 8)

## Assumptions

- Phase 2 complete — script-delegation-contract.md exists at `engine/shared/references/`
- `guard-check.py` already has `authority` and `commands` subcommands — `chain` is additive
- Task card schema is stable (task-card.schema.json defines the required fields)
- Scripts go in `engine/shared/scripts/` alongside the existing 30+
- Python 3.8+ stdlib only — no new pip dependencies

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
