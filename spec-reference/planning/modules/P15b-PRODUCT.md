# Module Plan — Product (L0)

**Tier:** 3 — SUPPORTING
**Layer:** L0 Intake
**v5.3 origin:** Product module — product context capture upstream of spec work

---

## Purpose

Capture product goals, user segments, success metrics, and business constraints before P1 spec work begins. Product context is not a spec — it informs spec decisions. Writes product-context.md to .wabblespec/plans/. Read by Interview (to frame questions), ScopeFrame (to set boundaries), and Specify (to align requirements with product goals). Activates once per major product initiative, not per feature.

---

## Activation

`skill-rules.json` triggers:
- New project detected (Scaffold completes, Product activates before Recipe for P1)
- Explicit `/product` command
- New milestone or major initiative declared (Autopilot L3+ lifecycle)
- Cannot activate without at least one of: product owner present, product brief provided, or user prompt with product context

---

## Product Context Structure

```markdown
# Product Context

**generated_at:** timestamp
**initiative:** string (what is being built at a high level)
**owner:** string (who is accountable)

## Product Goals

<what the product must achieve — business or mission objectives>
<ordered by priority>

## User Segments

| Segment | Description | Primary jobs-to-be-done |
|---|---|---|
| segment name | who they are | what they need to accomplish |

## Success Metrics

| Metric | Target | Measurement method |
|---|---|---|
| metric name | value | how measured |

## Business Constraints

<non-negotiables that bound all product decisions>
<budget, timeline, compliance, existing systems>

## Non-Goals (Product Level)

<what this initiative explicitly does not try to achieve>
<distinct from spec non-goals — these are product-level>

## Open Questions

<unresolved product-level questions — feed to Interview>
```

---

## Workflow

```
1. Collect product context from:
   -> User prompt (primary source)
   -> Existing documents (PRD, brief, deck) via ReferenceLoad
   -> Interview if context is incomplete (Interview consulted for open questions)

2. Identify: goals, segments, metrics, constraints, non-goals

3. Flag open questions for Interview routing

4. Write product-context.md to .wabblespec/plans/

5. Notify: ScopeFrame (product constraints → scope boundaries), Interview (open questions)

6. Write to Memory as FRESH drawer (product context is evidence)

7. Write Product receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — new project or initiative |
| `templates/product-context.md` | Template | Product context structure |
| `rules/no-spec-content.md` | Rules | Product context is not a spec — no EARS requirements |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | Recipe activates after Product for new projects |
| ScopeFrame | ScopeFrame reads product constraints to set scope.md boundaries |
| Interview | Interview reads open questions from product-context.md |
| Specify | Specify reads product goals for requirement alignment check |
| Memory | Product context written as FRESH drawer |
| Instinct | Instinct tracks product goal alignment across execution cycles |

---

## Verification Mode

**Observation** — product-context.md written, goals and segments declared, success metrics present, open questions routed to Interview, receipt written.

---

## Receipt Extension Fields

```json
{
  "initiative": "string",
  "goals_count": "integer",
  "segments_count": "integer",
  "metrics_count": "integer",
  "open_questions_count": "integer",
  "context_path": "string"
}
```
