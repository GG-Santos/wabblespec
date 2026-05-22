# Task Card

**goal:** `modules/l2/executor/rules/error-routing.md` exists and contains a complete error-type-to-action routing table covering all 6 error types defined in `_shared/references/error-taxonomy.md`.
**target:** AI-Agent
**complexity:** Low
**locked_at:** 2026-05-21T10:02:00Z

## Non-Goals

- Modifying `modules/l2/executor/SKILL.md`
- Creating test files or validation scripts
- Updating any other module files
- Adding new error types beyond those defined in the taxonomy

## Assumptions

- The 6 error types in `_shared/references/error-taxonomy.md` are the complete set for Phase 2
- File format is Markdown (not JSON or YAML)
- No schema validation of the routing table itself is required in Phase 2

## Acceptance Criteria

### Criterion 1: File exists at correct path

Given the WabbleSpec v6.1 repository
When `modules/l2/executor/rules/error-routing.md` is read
Then the file exists and is non-empty

### Criterion 2: All 6 error types covered

Given the error taxonomy in `_shared/references/error-taxonomy.md` defines SOFT, HARD, DEPENDENCY, CONTEXT_EXHAUSTION, SPEC_VIOLATION, STALENESS_VIOLATION
When the routing table in `error-routing.md` is checked
Then all 6 types appear as rows with `recoverable`, `action`, and `target` columns matching the taxonomy definitions

## Open Questions

<!-- (none) -->
