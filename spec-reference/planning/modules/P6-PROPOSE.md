# Module Plan — Propose (L1)

**Tier:** 2 — CORE
**Layer:** L1 Spec Core
**v5.3 origin:** Propose module — functional/technical spec awareness

---

## Purpose

Generate implementable options with explicit tradeoffs before Specify commits to a direction. Propose surfaces alternatives — it does not make decisions. Human or Reviewer selects. Used when multiple valid approaches exist and the choice has downstream consequences.

---

## Activation

`skill-rules.json` triggers:
- P1 stage: multiple valid Design Document approaches detected
- P2 stage: architectural alternatives must be evaluated before Systems Design locks
- Specify detects branching point (cannot populate template without direction)
- Explicit `/propose` command

Propose does not activate for routine decisions with one obvious answer.

---

## Option Structure

Each option Propose generates must be:
- **Implementable:** achievable within declared scope (scope.md)
- **Distinct:** meaningfully different from other options (not variations of same approach)
- **Honest:** tradeoffs are stated, not hidden
- **Bounded:** 2-4 options maximum — more options increase decision paralysis

### Option document format

```markdown
# Options: <decision point>

**stage:** P1|P2|P3|P4
**target:** build target
**generated_at:** timestamp
**recommendation:** Option N (with brief rationale)

---

## Option 1: <name>

**Summary:** one sentence description

**How it works:** brief technical description

**Tradeoffs:**
| Dimension | Assessment |
|---|---|
| Complexity | Low / Medium / High |
| Time to implement | estimate |
| Risk | Low / Medium / High |
| Reversibility | Easy / Hard / Irreversible |
| Fits scope | Yes / Partially / No |

**When to choose this:** conditions under which this is the best option

**When NOT to choose this:** conditions that make this a poor choice

---

## Option 2: <name>

[same structure]

---

## Recommendation

Option N — because <concise rationale tied to scope and target>.

This recommendation is advisory. The selected option becomes the input to Specify.
```

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Options document | `.wabblespec/options-<stage>-<timestamp>.md` | Decision input |
| Propose receipt | `.wabblespec/receipts/propose-receipt.md` | I10 compliance |

---

## Workflow

```
1. Identify decision point (from Specify, stage context, or explicit command)

2. Read scope.md — options outside scope are excluded immediately

3. Read intent.md — options that contradict declared intent are excluded

4. Read project-map.md — options incompatible with existing stack flagged

5. Generate 2-4 distinct, implementable options

6. For each option: assess tradeoffs across 5 dimensions

7. Select recommendation (most aligned with scope + target + constraints)

8. Write options document

9. Present to user or route to Reviewer (if impact = HIGH)

10. Record selected option in receipt

11. Pass selected option to Specify
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over options documents |
| `references/tradeoff-dimensions.md` | Reference | Tradeoff dimension definitions and assessment criteria |
| `rules/option-count.md` | Rules | 2-4 option bounds and rationale |
| `rules/recommendation-policy.md` | Rules | When to make strong recommendation vs. neutral presentation |
| `schemas/options.schema.json` | Schema | Options document header validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Specify | Propose precedes Specify when branching point detected. Selected option becomes Specify input. |
| Reviewer | HIGH-impact architectural options route through Reviewer before selection |
| ScopeFrame | Propose reads scope.md to exclude out-of-scope options |
| Decompose | Reads selected option from options document to size wave plan |
| Brainstorm (v5.3 carry-forward) | Brainstorm expands possibility space BEFORE Propose narrows to implementable options |

---

## Verification Mode

**Review** — options are distinct, tradeoffs are honest, recommendation is tied to scope. Reviewer triggered if impact = HIGH.

---

## Receipt Extension Fields

```json
{
  "stage": "P1|P2|P3|P4",
  "decision_point": "string",
  "options_generated": "integer",
  "option_selected": "integer",
  "selection_method": "user|reviewer|auto-recommendation",
  "reviewer_triggered": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 Propose | v6.1 Propose |
|---|---|
| Generate spec artifacts with options | Options document separate from spec artifact |
| Functional/technical spec awareness | Stage-aware (P1-P4) |
| No structured tradeoff format | Structured 5-dimension tradeoff table |
| No recommendation policy | Recommendation required with rationale |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Options document persistence | Session-scoped vs. archived with spec | Per-module planning |
| Auto-select when one option clearly dominates | Auto-select + notify vs. always present to user | Per-module planning |
| Brainstorm integration | Explicit trigger vs. auto-trigger before Propose when option space unknown | Resolve during Brainstorm carry-forward planning |
