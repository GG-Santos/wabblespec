---
name: plan
description: Multi-expert strategic planning for Medium+ complexity tasks. Applies diverse expert perspectives to a chosen approach. Budget-gated Adversary challenge for High complexity or security/infrastructure scope. Sits between Propose and Decompose. Produces a plan artifact that Decompose reads.
---

# Plan

Propose names options and recommends one. You stress-test that recommendation, apply expert perspectives, identify risks, and issue a go/no-go before Decompose commits to a wave plan. A weak plan is cheaper to fix here than mid-execution.

## What this skill does

Receives Propose's recommendation. Applies domain-relevant expert perspectives. Identifies open risks. Challenges the plan with Adversary when budget gate fires. Issues go/no-go recommendation. Writes a plan artifact and receipt.

## When to use / when not to use

**Mandatory when (any one condition met):**
- Complexity is Medium or High (declared in recipe.json)
- Autopilot operating at L2+ autonomy
- Explicit `/plan` command

**Optional (Low complexity):** Low complexity tasks may skip directly from Specify to Decompose. Plan is still available on explicit request.

**Do not use when:**
- recipe.json not present (Recipe must run first)
- Propose has not produced a recommendation (Plan consumes Propose output)

## Inputs

- Propose output (options + recommendation + rationale)
- `recipe.json` (target, complexity)
- Spec artifact (task card from Specify, if available)

## How to do it

### Step 1 — Load Propose recommendation

Read Propose's output. Identify the chosen approach. If Propose did not issue a recommendation (multiple options at equal weight), invoke Brainstorm or surface the tie to the user before proceeding.

### Step 2 — Apply expert perspectives

Apply domain-relevant expert perspectives to the chosen approach. See rules/expert-roles.md for which perspectives apply by domain and complexity.

Default perspectives (apply to all plans at Medium+ complexity):

| Perspective | Question to ask |
|---|---|
| Architecture | Does this approach introduce hidden coupling or layering violations? |
| Security | What attack surface does this approach expose? |
| Operability | How does this fail in production, and is failure observable? |
| Performance | What are the scale limits of this approach? |
| Maintainability | Will a future developer understand why this approach was chosen? |

Domain-specific perspectives (from rules/expert-roles.md): add security-depth for security scope, data modeling for data pipeline scope, UX for frontend scope, etc.

Record which perspectives were applied in the receipt. At least 2 perspectives required. Document concerns raised — they become open risks.

### Step 3 — Identify open risks

List risks that remain unresolved after expert review. A risk is open if it could cause execution failure or spec deviation and cannot be mitigated within the current plan.

See rules/plan-completeness.md for risk categories. For each open risk: name it, describe the consequence if it materializes, and note whether it blocks execution or is acceptable.

### Step 4 — Budget gate — Adversary challenge

Invoke `modules/l2/adversary` with `challenger_mode: "spec-bound"` when ANY of:
- Complexity is High
- Plan touches security, infrastructure, or irreversible scope
- Any open risk is rated BLOCKING

Adversary challenges the plan artifact. Invoke `modules/l2/grader` with Adversary receipt + plan artifact + spec artifact.

If Grader returns REVISE: revise the plan (max 3 cycles). If ESCALATE: surface to user before proceeding to Decompose. Record `adversary_triggered`, `grader_score`, `grader_verdict` in receipt.

If budget gate does not fire: record `adversary_triggered: false`, proceed to Step 5.

### Step 5 — Issue go/no-go

| Verdict | When |
|---|---|
| GO | Plan is complete, risks are documented, no blockers |
| NO_GO | Plan has unresolvable issues; human judgment required before Decompose |
| CONDITIONAL | Plan is sound, but specific conditions must be met before execution (list them) |

On NO_GO or CONDITIONAL: surface to user with clear rationale. Do not proceed to Decompose until resolved. See rules/escalation-triggers.md.

### Step 6 — Write plan artifact and receipt

Write plan artifact to `.wabblespec/plans/plan-<timestamp>.md`. Receipt to `.wabblespec/receipts/plan-receipt-<timestamp>.json`.

Pass plan artifact path to Decompose. Decompose uses the chosen approach, rationale, and open risks to structure waves.

## Output contract

**plan-<timestamp>.md** (`.wabblespec/plans/plan-<timestamp>.md`):

```markdown
# Plan

**chosen_approach:** <one sentence>
**go_no_go:** GO | NO_GO | CONDITIONAL
**locked_at:** ISO-8601-timestamp

## Expert Perspectives Applied

### <Perspective 1>
<Concerns or confirmation>

### <Perspective 2>
<Concerns or confirmation>

## Open Risks

| Risk | Consequence | Status |
|---|---|---|
| <risk> | <consequence> | BLOCKING | ACCEPTABLE |

## Conditions (if CONDITIONAL)

- <condition 1>
- <condition 2>
```

**plan-receipt.json** (`.wabblespec/receipts/plan-receipt-<timestamp>.json`):

Base receipt schema extended with fields per `schemas/plan-receipt.schema.json`. Key extension fields:

```json
{
  "plan_options_count": "integer — number of Propose options evaluated",
  "chosen_approach_summary": "string — one sentence",
  "expert_perspectives_applied": ["array — e.g. security, architecture, operability"],
  "adversary_triggered": "boolean",
  "grader_score": "number 0.0–1.0 — null if adversary not triggered",
  "grader_verdict": "ACCEPT | REVISE | ESCALATE | null",
  "open_risks": ["array of risk strings"],
  "go_no_go": "GO | NO_GO | CONDITIONAL",
  "plan_artifact_path": ".wabblespec/plans/plan-<timestamp>.md",
  "human_escalation_required": "boolean"
}
```

## A note on common failure modes

1. **Planning without Propose.** Plan needs Propose's recommendation as input. Running Plan before Propose skips the options-generation step — you get a plan with no alternatives evaluated.

2. **Skipping Adversary on High complexity.** The Adversary budget gate is not optional for High complexity tasks. A plan that is not challenged is a plan with undetected weaknesses.

3. **GO with BLOCKING risks.** An open risk rated BLOCKING is a blocker. Do not issue GO when BLOCKING risks exist — issue CONDITIONAL or NO_GO and surface to user.

4. **Plan too detailed.** Plan's output guides Decompose, not replaces it. The plan names the approach and risks — Decompose decides the wave structure. Do not plan individual implementation steps here.
