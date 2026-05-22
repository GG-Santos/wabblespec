# Module Plan — TeamPlan (L2)

**Tier:** 3 — SUPPORTING
**Layer:** L2 Orchestration
**v5.3 origin:** No direct equivalent — new in v6.1 (multi-agent coordination)

---

## Purpose

Define agent roles, responsibilities, and handoff protocols for tasks that require multiple agents. Single-agent execution is always the default. TeamPlan activates only when Autopilot reaches L4 autonomy or task explicitly requires parallel agent work. Each agent gets a bounded, non-overlapping scope. Handoffs are explicit. No implicit shared state between agents.

---

## Activation

`skill-rules.json` triggers:
- Autopilot autonomy level = L4 (complexity > 0.9)
- Explicit `/teamplan` command
- Task declared multi-agent in wave plan

Single-agent tasks never route through TeamPlan. TeamPlan is not a performance optimization — it is a coordination necessity for genuinely complex tasks.

---

## Agent Role Structure

Each agent in a team plan has:

```markdown
## Agent: <role name>

**scope:** <exactly what this agent owns — bounded, non-overlapping>
**inputs:** <what this agent receives to start>
**outputs:** <what this agent produces>
**handoff_to:** <next agent or null>
**handoff_condition:** <what must be true before handoff>
**verification_mode:** <how this agent's output is verified>
**cannot_touch:** <explicit exclusions — what this agent must not modify>
```

`cannot_touch` is required on every agent role. Prevents scope bleed.

---

## Handoff Protocol

```
Agent A completes scope
  -> Writes handoff artifact (declared output)
  -> Verifier checks handoff artifact (declared verification mode)
  -> IF PASS: handoff to Agent B with artifact as input
  -> IF FAIL: REVISE loop within Agent A's scope (max 3 cycles)
  -> IF BLOCKED: TeamPlan escalates to human (Attestation)
```

No agent begins work without receiving its declared inputs from prior handoff. No implicit context sharing. Each agent starts from its declared inputs only.

---

## Shared State Policy

Agents in a team plan may not share mutable state. Read-only shared references are allowed:

| Allowed | Not allowed |
|---|---|
| Reading spec artifacts (read-only) | Writing to same file simultaneously |
| Reading Memory drawers (read-only) | Modifying shared state without handoff |
| Reading project-map.md (read-only) | Concurrent writes to project/repo/ |

All writes go through the agent's declared output artifact, passed via handoff.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Team plan | `.wabblespec/plans/team-plan-<timestamp>.md` | Agent role definitions and handoff sequence |
| TeamPlan receipt | `.wabblespec/receipts/teamplan-receipt.md` | I10 compliance |

### Team plan structure

```markdown
# Team Plan

**task:** string
**complexity_score:** number
**agents:** integer
**generated_at:** timestamp

## Agents

[Agent role blocks per agent]

## Handoff Sequence

Agent A -> Agent B -> Agent C -> Delivery

## Shared Read-Only References

- spec artifact: path
- project-map.md: path
```

---

## Workflow

```
1. Read wave plan from Decompose (L4 complexity)

2. Identify parallelizable or sequential multi-agent opportunities:
   -> Sequential: Agent B needs Agent A output
   -> Genuinely parallel: Agent A and B produce independent artifacts
   -> Default to sequential — parallel only when independence is provable

3. Define agent roles:
   -> Bound each scope explicitly
   -> Declare cannot_touch for each
   -> Declare handoff conditions

4. Route to Reviewer (team plan reviewed before agents begin)

5. Write team plan

6. Autopilot manages agent execution against team plan

7. Write TeamPlan receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — L4 autonomy or explicit |
| `rules/scope-isolation.md` | Rules | Non-overlapping scope requirements, cannot_touch enforcement |
| `rules/handoff-protocol.md` | Rules | Handoff conditions, verification before handoff |
| `rules/parallel-conditions.md` | Rules | When parallel is provably safe |
| `schemas/team-plan.schema.json` | Schema | Team plan validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Autopilot | TeamPlan triggered by Autopilot at L4 autonomy. Autopilot manages execution against team plan. |
| Decompose | TeamPlan reads wave plan to identify multi-agent opportunities |
| Reviewer | Team plan reviewed before any agents begin |
| Verifier | Verifies each agent's output at handoff point |
| Executor | Executor runs each agent's wave within declared scope |

---

## Verification Mode

**Review** — team plan reviewed by Reviewer. All agent scopes are non-overlapping, all handoff conditions are declared, all cannot_touch lists are populated.

---

## Receipt Extension Fields

```json
{
  "agents_defined": "integer",
  "sequential_handoffs": "integer",
  "parallel_agents": "integer",
  "reviewer_triggered": "boolean",
  "handoff_failures": "integer",
  "attestation_required": "boolean"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Max agents per team plan | Unlimited vs. cap at 5 (complexity ceiling) | Per-module planning |
| Parallel safety verification | Claim-based (current) vs. automated scope overlap check | Per-module planning |
| Agent context isolation | Full isolation (current) vs. shared read-only memory pool | Per-module planning |
