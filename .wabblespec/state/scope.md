# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T15:30:00Z
**session_id:** selective-skills-20260528

## In Scope

- Add --skills flag to recipe-writer.py writing active_skills to recipe.json
- Add --filter-recipe flag to wabblespec-sync-skills.py to honor active_skills list
- Update CLAUDE.md to document the selective preloading pattern

## Out of Scope

- Session-start or stop-hook modifications
- Modifying wabblespec.yaml schema or any SKILL.md files

## Assumptions

- active_skills: [] (empty) means all skills — backward compatible default
- Filter does not remove unmanaged external skills from .claude/skills/
- Stale removal still applies only to WabbleSpec-managed skills not in the filter list

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
