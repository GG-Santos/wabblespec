# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T15:00:00Z
**session_id:** ref-receipt-schemas-20260528

## In Scope

- Fix build_ref_eval field names and add missing defaulted fields
- Fix build_ref_comp field names (execution_classification, coverage_rate, execution_gaps as dict)
- Fix build_ref_plan field names (signal_items_found, backlog_size, ref_eval_verdict, integration_goal, risk_appetite)
- Create ref-eval-receipt.extension.schema.json
- Create ref-comp-receipt.extension.schema.json
- Create ref-plan-receipt.extension.schema.json

## Out of Scope

- Adding new dedicated CLI flags for type-specific fields (SKILL.md CLIs use generic flags intentionally)
- Modifying SKILL.md files or base receipt schema
- Changes to any other receipt type

## Assumptions

- SKILL.md schemas are the authoritative field spec — no external schema files exist yet
- All new fields use sensible defaults (0, false, empty string) when not settable via current CLI
- receipt-writer.py runs without duckdb installed — upsert is silent-fail

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
