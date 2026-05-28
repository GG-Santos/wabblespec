# Task Card

**goal:** Every SKILL.md that previously instructed manual writes to `.wabblespec/CHANGELOG.md`, `.wabblespec/VERSION`, or receipt JSON files now delegates those writes to the appropriate existing scripts via explicit Bash calls, and `script-delegation-contract.md` documents the canonical delegation pattern.
**target:** Library-Package
**complexity:** Medium
**change_class:** ADDITIVE
**locked_at:** 2026-05-28T12:03:00Z
**session_id:** phase2-script-delegation-20260528

## Non-Goals

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

## Acceptance Criteria

### AC1 — script-delegation-contract.md exists and is complete

Given `.wabblespec/engine/shared/references/` exists,
When the task completes,
Then `script-delegation-contract.md` exists at that path and contains entries for `archive.py`, `receipt-writer.py`, `changelog-append.py`, and `version-bump.py`, each with a complete CLI example invocation showing all required args.

### AC2 — archive/SKILL.md delegates Steps 4–6b to archive.py

Given `archive/SKILL.md` previously contained Steps 4–6b instructing manual writes to CHANGELOG.md, VERSION, the delivery receipt, and receipt-index.json,
When the task completes,
Then those steps reference `archive.py` with `--session-id`, `--summary`, `--delta-class`, and `--files-delivered` args, and no prose in those steps instructs direct file writes to CHANGELOG.md, VERSION, or receipt-index.json.

### AC3 — All audited skills replace manual write prose with script calls

Given the audit in Wave 1 identifies N skills (expected 7–11) with manual framework write steps,
When the task completes,
Then each identified skill's write steps contain an explicit `python .wabblespec/engine/shared/scripts/<script>.py` call in place of the manual prose, and zero prose remains instructing "append to CHANGELOG", "write VERSION", or "construct receipt JSON and write".

### AC4 — Each affected SKILL.md gains a Reference Routing table

Given each identified SKILL.md has been rewritten per AC3,
When the task completes,
Then each affected SKILL.md contains a `## Reference Routing` section with an entry routing to `script-delegation-contract.md` for the relevant delegation situation.

### AC5 — Modified SKILL.md files synced to .claude/skills/

Given `wabblespec-sync-skills.py` exists,
When `wabblespec-sync-skills.py` is run at task close,
Then all modified SKILL.md files in `engine/modules/` are reflected in their corresponding `.claude/skills/` counterparts.

### AC6 — Skills outside the audited set are unmodified

Given skills not identified by the audit perform no manual framework writes,
When the task completes,
Then those SKILL.md files show no diff — only the audited set is changed.
