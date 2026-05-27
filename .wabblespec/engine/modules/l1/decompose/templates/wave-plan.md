# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** <from recipe.json — e.g., CLI, Web, API-Service>
**complexity:** Low | Medium | High
**collapse_eligible:** true | false
**generated_at:** <ISO-8601 timestamp>

---

## Waves

### Wave 1: <name — verb phrase describing the work, e.g., "Build data model">

**inputs:**
- `.wabblespec/state/plans/task-card.md` — sections: <list relevant sections>
- <any context files required — e.g., existing schema, config>

**outputs:**
- `<path/to/artifact>` — <what it is>
- `<path/to/artifact>` — <what it is>

**checkpoint:** <condition that must be true before Wave 2 begins — specific and testable, e.g., "All database migration files exist and `python manage.py migrate --check` exits 0">

**rollback_to:** null

**verification_mode:** Test | Review | Audit | Measurement | Observation | Attestation | Demonstration

---

### Wave 2: <name>

**inputs:**
- Wave 1 outputs (list specific artifacts)
- `.wabblespec/state/plans/task-card.md` — sections: <list>

**outputs:**
- `<path/to/artifact>` — <what it is>

**checkpoint:** <specific, testable condition>

**rollback_to:** Wave 1 checkpoint
<!-- rollback_to options:
  - null                              (Wave 1 only)
  - Wave N checkpoint                 (default — file copies in .wabblespec/state/checkpoints/)
  - worktree:.worktrees/<wave-id>/    (High complexity + irreversible ops + git repo confirmed)
-->

**verification_mode:** <mode>

---

<!-- Repeat for each wave. Low: 1-2 waves. Medium: 2-4. High: 4-8. More than 8 requires user confirmation. -->

---

## Rollback Map

| Wave fails | Rollback target | Trigger condition |
|---|---|---|
| Wave 2 | Wave 1 checkpoint | HARD error or BLOCKED after 3 REVISE cycles |
| Wave 3 | Wave 2 checkpoint | HARD error or BLOCKED after 3 REVISE cycles |

---

## Notes

<Anything unusual about the sequencing decision — e.g., why Wave 3 must precede Wave 2 despite the typical ordering>
