# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T12:01:00Z
**session_id:** phase2-script-delegation-20260528

## In Scope

- Audit all SKILL.md files to confirm the exact set performing manual writes to `.wabblespec/CHANGELOG.md`, `.wabblespec/VERSION`, or receipt JSON files
- Rewrite `archive/SKILL.md` Steps 4–6b to call `archive.py` with the correct CLI args (highest priority — eliminates 98KB+ CHANGELOG context load)
- Rewrite each other affected SKILL.md's manual write steps to call `receipt-writer.py`, `changelog-append.py`, or `version-bump.py` as appropriate
- Write `.wabblespec/engine/shared/references/script-delegation-contract.md` — canonical mapping of every standard framework write operation to its script call and example invocation
- Add `## Reference Routing` tables to each affected SKILL.md pointing to `script-delegation-contract.md`, removing superseded inline prose
- Run `wabblespec-sync-skills.py` to propagate updated SKILL.md files from `engine/modules/` to `.claude/skills/`

## Out of Scope

- Creating new Python scripts (all required scripts already exist in `engine/shared/scripts/`)
- Modifying any script logic or CLI interfaces
- Guard Layer intercept hook (Option 3 from options document — blocked, Guard is locked)
- Changes to `skill-rules.json`, schemas, or any non-SKILL.md module files
- Running live archive or receipt operations to validate scripts end-to-end
- Skills not performing manual framework writes

## Assumptions

- Phase 1 root cleanup (`phase1-root-cleanup-20260528`) is complete — delivery receipt confirmed at `state/receipts/`
- All four scripts (`archive.py`, `receipt-writer.py`, `changelog-append.py`, `version-bump.py`) exist at `.wabblespec/engine/shared/scripts/` and are functional
- The "9 affected skills" is approximate — exact count determined by audit in Wave 1; expected range 7–11
- `.claude/skills/*/SKILL.md` files are the live copies; `engine/modules/*/SKILL.md` are source of truth; sync runs post-execution
- Changes are ADDITIVE — no existing skill behavior removed, only write steps delegated to script calls
- No project-standard drawers discovered — no existing standards apply to this task

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
