# Plan Escalation Triggers

When Plan must surface to user before Decompose proceeds.

## Hard escalation (NO_GO — human must resolve before execution)

| Trigger | Description |
|---|---|
| BLOCKING risk unresolved | Any open risk rated BLOCKING with no mitigation path |
| Adversary ESCALATE verdict | Grader returned ESCALATE after max REVISE cycles |
| Approach not confirmed by Propose | No Propose recommendation exists; Plan cannot pick an approach unilaterally |
| Spec conflict | Chosen approach contradicts a locked acceptance criterion in the task card |
| Security expert: privilege escalation | Expert perspective found unmitigated privilege escalation |

NO_GO surface message must include: what the specific blocker is, what needs to happen to resolve it, and whether it requires human decision or additional investigation.

## Conditional escalation (CONDITIONAL — execution may start after conditions met)

| Trigger | Description |
|---|---|
| Infrastructure coordination needed | External team must be notified before execution starts |
| Feature flag required | Approach requires a flag to be created before the first wave runs |
| ACCEPTABLE risk with mitigation required | Risk is acceptable but mitigation must be in place before wave N |
| Dependency not yet available | Approach depends on a module or service that is not yet deployed |

CONDITIONAL surface message must include: the specific condition, who resolves it, and which wave is gated on it.

## What Plan does NOT escalate

- Complexity — Recipe declared complexity; Plan does not change it
- Target — Recipe declared target; Plan does not change it
- Approach selection between equally weighted options — Propose or user resolves this, not Plan
- Implementation detail questions — Executor resolves these

If Plan finds itself escalating on implementation details: it has overreached into Executor's territory. Stop and hand off.
