# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T10:35:00Z
**session_id:** toprank-integration-phase1

## In Scope

- Add `~~capability-name` connector placeholder writing convention to `CLAUDE.md` under a new "## Skill Authoring Conventions" section with at least one concrete example (T4)
- Add `## Reference Routing` section to `.claude/skills/benchmark/SKILL.md`, routing existing inline content to `rules/benchmark-discipline.md` and/or `rules/outcome-requirement.md`; each routing entry removes the corresponding inline block; line count must decrease by ≥ 10 lines
- Add `## Reference Routing` section to `.claude/skills/executor/SKILL.md`, routing the tier table and error-routing details to `.wabblespec/engine/shared/references/system-prompt-tiers.md` and `rules/error-routing.md`; line count must decrease by ≥ 10 lines
- Assess `.claude/skills/verifier/SKILL.md` for routing potential against `pre-emit-critique.md`; apply routing table only if a genuine already-existing mapping exists — otherwise exclude from T1 this pass
- Lock a task card for this work before implementation begins (I1)

## Out of Scope

- `.claude/skills/guard/SKILL.md` — locked under `wave-checkpoint-v1` (T6 deferred)
- `.claude/skills/recipe/SKILL.md` — not part of this integration plan
- Creating any new reference files — routing entries must point to already-existing documents only
- Phase 2 items: T2 (LLM-as-judge script), T3 (instinct drawer field rename) — require separate Specify cycle
- Phase 3 item: T5 (`allowed-tools:` frontmatter enforcement)
- Any writes to `.wabblespec/` framework space from this product-space task (I11)

## Assumptions

- `wave-checkpoint-v1` task card is LOCKED but not archived — Guard SKILL.md is off-limits this session
- `rules/benchmark-discipline.md`, `rules/outcome-requirement.md`, `rules/error-routing.md`, and `.wabblespec/engine/shared/references/system-prompt-tiers.md` all exist and contain content matching inline sections in their respective SKILL.md files (confirmed present via file check)
- No project-standard Memory drawers found — none cited
- `~~capability-name` convention is a writing standard only; no code enforcement in this session
- T6 (Guard safety taxonomy in Guard SKILL.md) is queued for the next session after `wave-checkpoint-v1` archives
- Verifier SKILL.md routing is conditional: apply only if `pre-emit-critique.md` maps to genuine inline content; otherwise Verifier is excluded from T1 this pass

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
