# Task Card

**goal:** receipt-writer.py correctly outputs all schema-declared fields for ref-eval, ref-comp, and ref-plan types with matching field names, types, and three schema JSON files created.
**target:** Library-Package
**complexity:** Medium
**change_class:** ADDITIVE
**locked_at:** 2026-05-28T15:00:00Z
**session_id:** ref-receipt-schemas-20260528

## Non-Goals

- Adding new dedicated CLI flags for type-specific fields
- Modifying SKILL.md files or base receipt schema
- Changes to any other receipt type

## Assumptions

- SKILL.md schemas are the authoritative field spec
- All new fields use sensible defaults when not settable via current CLI

## Acceptance Criteria

### AC1 — ref-eval fields correct

Given receipt-writer.py --type ref-eval is invoked
When output JSON is inspected
Then all 16 SKILL.md fields present with correct names including reference_path, reference_type, benefits_identified, risks_identified, adapt_items, avoid_items, drawers_written, depth, report_path

### AC2 — ref-comp fields correct

Given receipt-writer.py --type ref-comp is invoked
When output JSON is inspected
Then fields are execution_classification (not verdict), coverage_rate (not coverage_score), execution_gaps as dict with critical/major/minor keys, improvements_beyond_plan as int

### AC3 — ref-plan fields correct

Given receipt-writer.py --type ref-plan is invoked
When output JSON is inspected
Then fields are signal_items_found (not total_items_extracted), backlog_size, ref_eval_verdict, integration_goal, risk_appetite all present

### AC4 — schema files created

Given no schema files existed before this session
When three schema JSON files are written
Then ref-eval-receipt.extension.schema.json, ref-comp-receipt.extension.schema.json, and ref-plan-receipt.extension.schema.json exist under .wabblespec/engine/shared/schemas/
