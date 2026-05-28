# Task Card: toprank-integration-phase2-T3

**Session ID:** toprank-integration-phase2-T3
**Created:** 2026-05-28
**Delta class:** ADDITIVE
**Complexity:** Medium
**Status:** LOCKED
**Task type:** framework-authoring

---

## Goal

The Instinct output contract and all 4 existing instinct observation patterns are extended with three judgment lever fields (`Expected impact`, `Actionability score`, `Learned multiplier`), each with a documented value vocabulary and null defaults, leaving all existing fields and Synth gate logic unchanged.

---

## Non-Goals

- Retroactive scoring of existing patterns (null defaults only; no human scoring applied in this task)
- Modifying Synth SKILL.md or any Synth-side gate logic
- Updating memory-mine.py or any Instinct automation to emit the new fields (separate task)
- Touching any existing field (Human-validated, Confidence, Type, Evidence, Occurrences)
- Guard SKILL.md, T5 (allowed-tools enforcement), T6 (Guard safety taxonomy)

---

## Assumptions

- Synth SKILL.md audit (completed during ScopeFrame): only hardcoded field reference is `Human-validated` — adding three new fields is safe
- instinct-observations.md contains exactly 4 patterns — confirmed
- No active Instinct run is concurrently writing to instinct-observations.md
- `requires_scoring: true` is a documentation convention, not a machine-enforced field
- This is a framework authoring task — writes to `.wabblespec/state/memory/` and `.claude/skills/instinct/` are permitted (I11 product-space restriction does not apply)
- VERSION bump to 0.27.0 on Archive (ADDITIVE)

---

## Acceptance Criteria

### AC1 — Pattern block contains three new fields

Given the Instinct SKILL.md `## Output contract` section,
When this task completes,
Then the pattern block contains all three new fields with their full value vocabularies:
  `Expected impact: null | low | medium | high`
  `Actionability score: null | specific-lever | investigation | vague`
  `Learned multiplier: null | single-corpus | cross-corpus`

### AC2 — Human-reviewer note present

Given the Instinct SKILL.md `## Output contract` section,
When this task completes,
Then a note exists stating that `Expected impact` is populated by the human reviewer at validation time, not by automated scoring.

### AC3 — All 4 patterns updated with null defaults

Given `instinct-observations.md` containing 4 existing patterns,
When this task completes,
Then each pattern contains all three new fields set to `null`.
Then each pattern contains `requires_scoring: true` for the new fields.

### AC4 — No existing fields removed or modified

Given `instinct-observations.md` containing 4 existing patterns,
When this task completes,
Then every existing field (`Type`, `Confidence`, `Evidence`, `Occurrences`, `Human-validated`) is still present on each pattern with its original value unchanged.

### AC5 — Synth gate unaffected (failure path)

Given Synth SKILL.md reads only `Human-validated: true` as its gate condition,
When this task completes,
Then no modification has been made to Synth SKILL.md, any Synth script, or any Synth-side gate logic.

### AC6 — No model names introduced (I6)

Given the Instinct SKILL.md and instinct-observations.md,
When this task completes,
Then neither file contains any string matching `claude-`, `gpt-`, `gemini-`, or any versioned model identifier.

---

## Files to be Written / Modified

| File | Operation |
|---|---|
| `.claude/skills/instinct/SKILL.md` | MODIFY — extend output contract pattern block |
| `.wabblespec/state/memory/instinct-observations.md` | MODIFY — add three null fields to 4 patterns |
