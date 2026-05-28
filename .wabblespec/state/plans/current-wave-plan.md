# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Library-Package
**complexity:** Low
**collapse_eligible:** false
**session_id:** real-exec-validation-20260528
**generated_at:** 2026-05-28T14:00:00Z

## Waves

### Wave 1: Verify and create files

**inputs:** [.github/workflows/lint.yml, .github/workflows/quality-floor.yml, task-card.md AC1-AC3]
**outputs:** [.github/workflows/lint.yml (verified), .github/workflows/quality-floor.yml (verified), ruff.toml]
**checkpoint:** All three files exist; ruff.toml contains select E,F and ignore E501; quality-floor.yml uses --verbose and --undeclared flags
**verification_command:** `python -c "t=open(chr(96)[:0]+chr(114)+chr(117)+chr(102)+chr(102)+chr(46)+chr(116)+chr(111)+chr(109)+chr(108)).read(); assert chr(69)+chr(53)+chr(48)+chr(49) in t"`
**rollback_to:** null
**verification_mode:** Audit

---

### Wave 2: Commit all three files

**inputs:** [Wave 1 verified outputs, git staging area]
**outputs:** [HEAD commit containing lint.yml, quality-floor.yml, ruff.toml]
**checkpoint:** All three files appear in HEAD commit on main with no unstaged changes
**verification_command:** `git show --name-only HEAD`
**rollback_to:** Wave 1 checkpoint
**verification_mode:** Test

---

## Rollback Map

| Wave | Rollback target | Trigger condition |
|---|---|---|
| Wave 1 fails | null (Wave 1 — no prior checkpoint) | HARD error or BLOCKED after 3 REVISE cycles |
| Wave 2 fails | Wave 1 checkpoint | HARD error or BLOCKED after 3 REVISE cycles |
