# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T11:25:00Z
**session_id:** toprank-integration-phase2-T3

## In Scope

- Extend Instinct SKILL.md `## Output contract` pattern block with three new fields: `Expected impact`, `Actionability score`, `Learned multiplier` — each with documented value vocabulary
- Add note in Instinct SKILL.md that `Expected impact` is populated by the human reviewer at validation time, not by automated scoring
- Add all three new fields (null defaults) to each of the 4 existing patterns in `instinct-observations.md`
- Mark each existing pattern with `requires_scoring: true` on the new fields to signal they need human scoring before Synth can read them

## Out of Scope

- Retroactive scoring of existing patterns (null defaults only; no human scoring applied in this task)
- Modifying Synth SKILL.md or any Synth-side gate logic
- Updating memory-mine.py or any Instinct automation to emit the new fields (separate task)
- Touching any existing field (Human-validated, Confidence, Type, Evidence, Occurrences)
- Guard SKILL.md, T5 (allowed-tools enforcement), T6 (Guard safety taxonomy)

## Assumptions

- Synth SKILL.md audit (completed during ScopeFrame): only hardcoded field reference is `Human-validated` — adding three new fields is safe
- instinct-observations.md contains exactly 4 patterns — confirmed
- No active Instinct run is concurrently writing to instinct-observations.md
- `requires_scoring: true` is a documentation convention, not a machine-enforced field
- This is a framework authoring task — writes to `.wabblespec/state/memory/` and `.claude/skills/instinct/` are permitted (I11 product-space restriction does not apply)
- VERSION bump to 0.27.0 on Archive (ADDITIVE)

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
