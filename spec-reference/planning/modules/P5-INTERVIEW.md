# Module Plan — Interview (L1)

**Tier:** 2 — CORE
**Layer:** L1 Spec Core
**v5.3 origin:** Interview module — same purpose, integrated with ScopeFrame in v6.1

---

## Purpose

Reduce ambiguity through Socratic questioning. Runs before Specify when intent is unclear, before ScopeFrame when scope boundaries are unknown, and before Recipe when build target cannot be detected. Does not lead the user toward a predetermined answer — surfaces what the user actually means.

---

## Activation

`skill-rules.json` triggers:
- Recipe cannot auto-detect build target (confidence < 0.8)
- ScopeFrame detects ambiguous in-scope / out-of-scope boundaries
- Specify detects open questions in intent before populating template
- Ambiguity score above threshold on any L1 module input
- Explicit `/interview` command

---

## Ambiguity Dimensions

Interview evaluates ambiguity across 9 dimensions (from v5.3 Enhance intent-extraction):

| Dimension | Question it answers |
|---|---|
| Target | What kind of thing are we building? |
| Scope | What is in and explicitly out of scope? |
| Users | Who will use this? |
| Success | What does done look like? |
| Constraints | What must this work within (time, tech, budget, compliance)? |
| Risks | What could go wrong that we know about? |
| Dependencies | What does this depend on that isn't in our control? |
| Priority | If forced to cut, what survives? |
| Assumptions | What are we taking as given without verification? |

Interview does not ask all 9 every time. It asks only the dimensions with unresolved ambiguity.

---

## Questioning Rules

- Ask one question at a time, or a small numbered batch (max 3) when questions are tightly related
- Never lead: "Would you say this is a Web app?" is wrong. "What type of product are you building?" is correct
- Stop when ambiguity score drops below threshold — do not over-interview
- Record each answer immediately — do not wait until all questions answered
- If user answer introduces new ambiguity: ask follow-up before moving on

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Clarified intent document | `.wabblespec/intent.md` | Input to ScopeFrame and Specify |
| Interview receipt | `.wabblespec/receipts/interview-receipt.md` | I10 compliance |

### intent.md structure

```markdown
# Clarified Intent

**session:** <id>
**target:** <declared or inferred>
**ambiguity_resolved:** true|false
**timestamp:** <when completed>

## Answers by Dimension

### Target
<user answer>

### Scope
<user answer>

### Users
<user answer>

[... per dimension interviewed ...]

## Remaining Open Questions

<any unresolved items — must be empty before Specify begins>

## Assumptions Declared

<assumptions surfaced during interview>
```

---

## Workflow

```
1. Identify trigger source (Recipe, ScopeFrame, Specify, or explicit)

2. Evaluate ambiguity score per dimension
   -> Score each of the 9 dimensions: RESOLVED | PARTIAL | UNRESOLVED
   -> Identify dimensions with UNRESOLVED or PARTIAL

3. For each unresolved dimension (in priority order: Target first):
   a. Ask focused question
   b. Record answer
   c. Re-evaluate ambiguity score for that dimension
   d. IF new ambiguity introduced: ask follow-up
   e. IF resolved: mark dimension RESOLVED, move to next

4. Check remaining open questions
   -> IF any: continue until empty
   -> IF user cannot answer: mark as declared assumption

5. Write intent.md

6. Write Interview receipt

7. Return control to trigger module (Recipe, ScopeFrame, or Specify)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over intent.md |
| `references/intent-dimensions.md` | Reference | 9-dimension intent extraction guide with example questions |
| `rules/questioning-rules.md` | Rules | Socratic constraints, batch size, stop conditions |
| `rules/ambiguity-scoring.md` | Rules | How to score RESOLVED/PARTIAL/UNRESOLVED per dimension |
| `schemas/intent.schema.json` | Schema | intent.md validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | Delegates target detection ambiguity to Interview |
| ScopeFrame | Delegates scope boundary ambiguity to Interview |
| Specify | Delegates requirement ambiguity to Interview before populating template |
| Enhance (v5.3 carry-forward) | Enhance expands vague input before Interview — Interview reduces ambiguity in expanded input |

---

## Verification Mode

**Observation** — intent.md exists, all interviewed dimensions are RESOLVED, no remaining open questions, assumptions declared.

---

## Receipt Extension Fields

```json
{
  "trigger_source": "Recipe|ScopeFrame|Specify|explicit",
  "dimensions_interviewed": "integer",
  "dimensions_resolved": "integer",
  "questions_asked": "integer",
  "assumptions_declared": "integer",
  "ambiguity_remaining": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 Interview | v6.1 Interview |
|---|---|
| Socratic questioning | Same |
| 9-dimension intent extraction (from Enhance enrichment) | Same dimensions, now native to Interview |
| No intent.md output | intent.md produced and persisted |
| Triggered by user or Specify | Now also triggered by Recipe and ScopeFrame |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Ambiguity threshold | Score < 0.3 UNRESOLVED = stop (proposed) vs. configurable | Per-module planning |
| Max questions per session | Unlimited vs. cap at 12 (3 batches × 4) | Per-module planning |
| intent.md lifetime | Session-scoped vs. persists with spec | Per-module planning |
