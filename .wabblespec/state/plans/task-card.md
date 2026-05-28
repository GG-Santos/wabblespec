# Task Card: toprank-integration-phase1

**Session ID:** toprank-integration-phase1
**Created:** 2026-05-28
**Delta class:** ADDITIVE
**Complexity:** Medium
**Status:** LOCKED
**Task type:** content-edit
**Prior task (suspended):** wave-checkpoint-v1

---

## Goal

Implement Phase 1 Safe Wins from the toprank-main integration plan. Two changes:
1. Document the `~~capability-name` connector placeholder convention in `CLAUDE.md` (T4).
2. Add a `## Reference Routing` section to `.claude/skills/executor/SKILL.md`, routing the inline tier table to `system-prompt-tiers.md` and the inline error routing table to `rules/error-routing.md`, removing the corresponding inline blocks so the SKILL.md body shrinks (T1 — Executor only this pass).

---

## Non-Goals

- Modifying Guard SKILL.md (locked under wave-checkpoint-v1)
- Creating new reference files
- Applying routing tables to Benchmark or Verifier SKILL.md this pass
- Phase 2 items (T2 LLM-as-judge, T3 instinct drawer rename)

---

## Assumptions

- `.wabblespec/engine/shared/references/system-prompt-tiers.md` exists and its content covers the inline tier table in Executor SKILL.md
- `.claude/skills/executor/rules/error-routing.md` exists and covers the inline error routing table in Executor SKILL.md
- Executor SKILL.md line count before edits is the ground truth; ≥10 line reduction is verified against it
- No model names are introduced in any edited file

---

## Acceptance Criteria

### 1 — CLAUDE.md contains the capability placeholder convention

Given `CLAUDE.md` in the project root,
When this task completes,
Then `CLAUDE.md` contains a section or paragraph documenting the `~~capability-name` placeholder convention for tool references in SKILL.md files.
Then that section includes at least one concrete example (e.g. `~~search-console`, `~~vector-store`).
Then no model names are introduced in the added text.

### 2 — Executor SKILL.md has a Reference Routing section

Given `.claude/skills/executor/SKILL.md`,
When this task completes,
Then the file contains a `## Reference Routing` section.
Then the section has a table with at least two entries: one routing to `system-prompt-tiers.md` and one routing to `rules/error-routing.md`.

### 3 — Executor SKILL.md is shorter

Given `.claude/skills/executor/SKILL.md` before and after this task,
When this task completes,
Then the post-edit line count is at least 10 lines fewer than the pre-edit line count.
Then the inline tier table (stable/context/volatile rows) has been removed from the Inputs section.
Then the inline error routing summary table has been removed from the Error routing section.

### 4 — No new reference files created

Given the set of files in `.claude/skills/executor/rules/` and `.wabblespec/engine/shared/references/` before this task,
When this task completes,
Then no new files exist in those directories that did not exist before.

### 5 — Benchmark and Guard SKILL.md untouched

Given `.claude/skills/benchmark/SKILL.md` and `.claude/skills/guard/SKILL.md`,
When this task completes,
Then both files are byte-for-byte identical to their pre-task state.

---

## Files to be Written / Modified

| File | Operation |
|---|---|
| `CLAUDE.md` | MODIFY — add Skill Authoring Conventions section |
| `.claude/skills/executor/SKILL.md` | MODIFY — add Reference Routing section, remove inline tier table and error routing table |
