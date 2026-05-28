# Wave Plan: toprank-integration-phase1

**session_id:** toprank-integration-phase1
**task_card:** .wabblespec/state/plans/task-card.md
**locked_at:** 2026-05-28T10:42:00Z
**total_waves:** 2

---

## Wave 1 — T4: Capability Placeholder Convention in CLAUDE.md

**label:** claude-md-convention
**verification_mode:** Audit

### Steps

1. Read `CLAUDE.md` in full to locate the correct insertion point.
2. Add a `## Skill Authoring Conventions` section documenting the `~~capability-name` placeholder convention with at least two examples.
3. Verify no model names were introduced.

### Outputs

| Path | Operation |
|---|---|
| `CLAUDE.md` | MODIFY |

### Verification gate (Audit)

- `CLAUDE.md` contains `~~capability-name` text with at least one example placeholder
- No model names in the added section
- Acceptance criterion 1 "Then" clauses satisfied

### Rollback

Revert `CLAUDE.md` to pre-wave state.

---

## Wave 2 — T1: Reference Routing Table in Executor SKILL.md

**label:** executor-routing-table
**verification_mode:** Audit

### Steps

1. Count lines in `.claude/skills/executor/SKILL.md` before editing. Record as `pre_edit_lines`.
2. Remove the 3-row tier table (stable/context/volatile) from the Inputs section; replace with a one-line pointer to the existing "Full tier placement rules" line already present.
3. Remove the 5-row inline error routing summary table from the "### Error routing" section; replace with "See `rules/error-routing.md` for the full routing table, decision tree, and rollback protocol."
4. Add a `## Reference Routing` section with a 2-entry table pointing to `system-prompt-tiers.md` and `rules/error-routing.md`.
5. Count lines after editing. Confirm reduction ≥ 10.

### Outputs

| Path | Operation |
|---|---|
| `.claude/skills/executor/SKILL.md` | MODIFY |

### Verification gate (Audit)

- `## Reference Routing` section exists with 2-entry table
- Both referenced files exist
- Inline tier table rows absent from Inputs section
- Inline error routing table absent from Error routing section
- Line count ≥ 10 fewer than pre-edit
- Acceptance criteria 2, 3, 4, 5 "Then" clauses satisfied

### Rollback

Revert `.claude/skills/executor/SKILL.md` to pre-wave state.
