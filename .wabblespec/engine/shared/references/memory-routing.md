# Memory Routing

Which layer a fact belongs to — Memory drawer classification guide. Consumers: memory, memory-search, provenance, nexus.

## The classification question

Every fact or decision that needs to be remembered answers one question: "Is this fact stable enough to be a drawer, or transient enough to be session context?"

**Drawer:** Fact survives session end. Will be queried in future sessions. Has architectural, pattern, or evidence value.
**Session context:** Fact is useful only for the current task. Disposable after the session.

## Drawer classification by content type

### Decision (drawer — always)
An architectural or design decision with rationale. "We chose X over Y because Z."
Tags: `decision`, `<domain>`, `<affected-modules>`
Staleness: decisions are durable — mark AGING only when superseded, not on time.

### Pattern (drawer — always)
A recurring behavior, anti-pattern, or failure mode observed across sessions. "Every time we do X, Y happens."
Tags: `pattern`, `<domain>`, `observation-count: N`
Minimum: 3 observations before promoting to a pattern drawer.

### Evidence (drawer — when it changes confidence)
A measurement, test result, or real-world signal that updates the confidence of an existing belief. "Baseline measurement: P95 = 340ms (spec: 200ms)."
Tags: `evidence`, `production-evidence` (if from production), `<module>`, `<metric>`
Evidence drawers decay faster — mark STALE after 5 sessions without update.

### Constraint (drawer — when project-level)
A hard limit declared externally (legal, regulatory, platform). "GDPR requires deletion within 30 days."
Tags: `constraint`, `<source>`, `<domain>`
Constraints do not decay — they are FRESH until the constraint changes.

### Error (drawer — only if systemic)
A failure mode that has occurred and whose recurrence would benefit from prior knowledge. One-off errors are not drawer-worthy. A pattern of errors is.
Tags: `error`, `<module>`, `<error-type>`, `resolved: boolean`

### Reference (session context — not a drawer)
A file loaded for a specific task. Project map cards, reference docs, search results.
Reason: reference content is already in `.wabblespec/engine/shared/references/`. Duplicating it in Memory is redundant.

### Intermediate output (session context — not a drawer)
A draft, partial output, or work-in-progress artifact from the current session.
Reason: if the work completes, a receipt captures the outcome. If it fails, the incomplete output has no future value.

## Routing rules

### Route to Memory when:
- A decision was made that future sessions would want to understand
- A pattern was observed for the 3rd+ time
- Evidence was collected that updates a design confidence
- A constraint was discovered that affects future work

### Do not route to Memory when:
- The fact is only relevant to the current task card
- The fact is already in a `.wabblespec/engine/shared/references/` file
- The fact is already in `framework.yaml`
- The output is a receipt (receipts are their own persistence layer)

## Wing selection

Memory organizes drawers into wings by domain:

| Wing | Content |
|---|---|
| `decisions/` | Architecture and design decisions |
| `patterns/` | Recurring behaviors and anti-patterns |
| `evidence/` | Measurements, observations, production signals |
| `constraints/` | Hard limits from external sources |
| `errors/` | Systemic failure modes |

Route each drawer to the wing matching its primary content type. When ambiguous: prefer the more specific wing.
