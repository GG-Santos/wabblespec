# Module Plan — Triage (L1)

**Tier:** 3 — SUPPORTING
**Layer:** L1 Spec Core
**v5.3 origin:** Triage module — issue classification and routing

---

## Purpose

Classify incoming issues (bugs, feature requests, user feedback, error events) and route them to the correct module. Triage does not fix issues — it categorizes and routes. Writes triage records to Memory for Instinct observation. Recurrence signals (same issue triaged multiple times) escalate severity automatically.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/triage <issue>` command
- Error event received (from error-event.schema.json routing)
- Feedback module routes structured feedback requiring action
- Retro produces action items (each action item goes through Triage)

---

## Classification Dimensions

### Severity

| Level | Criteria |
|---|---|
| Critical | Production broken, data loss risk, security vulnerability |
| High | Core functionality broken, no workaround |
| Medium | Functionality degraded, workaround exists |
| Low | Minor issue, cosmetic, enhancement |

### Type

| Type | Definition |
|---|---|
| Bug | Behavior differs from spec |
| Feature | New capability not in current spec |
| Debt | Code/design quality issue without functional impact |
| Question | Ambiguity needing clarification |
| Security | Vulnerability or security concern |

### Recurrence

Triage checks Memory for prior records on the same topic:
- First occurrence: base severity
- Second occurrence: severity escalated one level
- Third+ occurrence: severity escalated to High minimum, Synth proposal triggered

---

## Routing Table

| Type | Severity | Route |
|---|---|---|
| Bug | Critical | Executor (immediate wave) + Autopilot L3+ |
| Bug | High | Interview (clarify) → Specify (delta) → Executor |
| Bug | Medium/Low | Specify (delta) → Executor (next scheduled wave) |
| Feature | Any | Interview → Specify → Propose → Decompose |
| Debt | Any | Clean (if COSMETIC) or Specify + Executor (if structural) |
| Question | Any | Interview |
| Security | Any | Security gateway (immediately) + severity-based routing |

---

## Triage Record Format

```markdown
# Triage Record — <issue-id>

**timestamp:** ISO 8601
**severity:** critical|high|medium|low
**type:** bug|feature|debt|question|security
**recurrence_count:** integer
**source:** user|error-event|feedback|retro

## Description

<issue as received>

## Classification Rationale

<why this severity and type>

## Routing Decision

**route_to:** <module>
**priority:** immediate|next-wave|scheduled

## Prior Occurrences

| Date | Triage ID | Resolution |
|---|---|---|
```

---

## Workflow

```
1. Receive issue (from any source)

2. Check Memory for prior triage records on same topic
   -> Count occurrences, apply recurrence escalation if > 1

3. Classify: severity + type

4. Determine routing from routing table

5. Write triage record to Memory as FRESH drawer

6. Route to declared module with triage record as context

7. Write Triage receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation |
| `rules/severity-matrix.md` | Rules | Severity classification criteria |
| `rules/routing-table.md` | Rules | Type + severity to module routing |
| `rules/recurrence-escalation.md` | Rules | Recurrence escalation policy |
| `schemas/triage-record.schema.json` | Schema | Triage record format |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Memory | Triage writes records to Memory; reads prior records for recurrence |
| Interview | Triage routes features and questions to Interview |
| Specify | Triage routes bugs and features to Specify for delta |
| Executor | Triage routes critical bugs directly to Executor |
| Security gateway | Triage routes security issues immediately to Security gateway |
| Clean | Triage routes debt issues to Clean (if COSMETIC scope) |
| Instinct | Instinct observes Triage patterns (recurrence signals) |
| Synth | Synth triggered when recurrence count crosses threshold |

---

## Verification Mode

**Observation** — triage record written, routing decision documented, Memory updated, receipt written.

---

## Receipt Extension Fields

```json
{
  "issue_id": "string",
  "severity": "string",
  "type": "string",
  "recurrence_count": "integer",
  "route_to": "string",
  "escalated": "boolean"
}
```
