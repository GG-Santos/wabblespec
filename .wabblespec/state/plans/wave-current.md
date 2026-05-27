# Wave Plan

**task_card:** .wabblespec/plans/task-card.md
**target:** AI-Agent
**complexity:** Low
**collapse_eligible:** true
**generated_at:** 2026-05-21T10:03:00Z

## Waves

### Wave 1: Write error-routing.md

**inputs:** [_shared/references/error-taxonomy.md, .wabblespec/plans/task-card.md]
**outputs:** [modules/l2/executor/rules/error-routing.md]
**checkpoint:** File exists at correct path and contains all 6 error types with recoverable, action, and target columns
**rollback_to:** null
**verification_mode:** Audit

---

## Rollback Map

| Wave | Rollback target | Trigger condition |
|---|---|---|
| Wave 1 fails | null (Wave 1 — no prior checkpoint) | HARD error or BLOCKED after 3 REVISE cycles |
