# Task Card

**goal:** recipe-writer.py and wabblespec-sync-skills.py support selective skill preloading: a skills list in recipe.json filters which WabbleSpec skills are synced to .claude/skills/ for the session.
**target:** Library-Package
**complexity:** Medium
**change_class:** ADDITIVE
**locked_at:** 2026-05-28T15:30:00Z
**session_id:** selective-skills-20260528

## Non-Goals

- Session-start or stop-hook modifications
- Modifying wabblespec.yaml schema or any SKILL.md files

## Assumptions

- active_skills: [] means all skills — backward compatible default
- Filter does not affect unmanaged external skills in .claude/skills/

## Acceptance Criteria

### AC1 — recipe-writer writes active_skills

Given recipe-writer.py is invoked with --skills executor --skills verifier
When recipe.json is written
Then active_skills field contains exactly executor and verifier

### AC2 — sync honors filter

Given wabblespec-sync-skills.py is invoked with --filter-recipe pointing to a recipe with active_skills=[executor,verifier]
When sync runs
Then only executor and verifier are synced; other WabbleSpec skills are not copied; external skills untouched

### AC3 — sync default unchanged

Given wabblespec-sync-skills.py is invoked without --filter-recipe
When sync runs
Then all 100 WabbleSpec skills are synced exactly as before

### AC4 — CLAUDE.md documented

Given CLAUDE.md is opened for edit
When the selective preloading pattern is added
Then --filter-recipe usage and the active_skills field are described in the Key Scripts section
