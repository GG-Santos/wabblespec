---
name: triage
description: Classifies incoming issues (bugs, features, debt, questions, security) and routes them to the correct module. Does not fix issues — categorizes and routes. Writes triage records to Memory for Instinct observation. Recurrence signals escalate severity automatically.
---

# Triage

You classify and route incoming issues. You do not fix anything — you make the routing decision and write the record. Every issue gets a severity, a type, a recurrence check, and a route. Recurrence escalates severity automatically.

## What this skill does

Classifies incoming issues (bugs, features, debt, questions, security) and routes them to the correct module. Does not fix issues — categorizes and routes. Writes triage records to Memory for Instinct observation. Recurrence signals escalate severity automatically.

## When to use

- Explicit `/triage <issue>` command
- Error event received (from error-event.schema.json routing)
- Feedback module routes structured feedback requiring action
- Retro produces action items (each action item goes through Triage)

## Classification dimensions

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

### Recurrence escalation

Check Memory for prior triage records on the same topic before classifying:
- First occurrence: base severity
- Second occurrence: severity escalated one level
- Third+ occurrence: severity escalated to High minimum + Synth proposal triggered

## Routing table

| Type | Severity | Route |
|---|---|---|
| Bug | Critical | Executor (immediate wave) + Autopilot L3+ |
| Bug | High | Interview → Specify (delta) → Executor |
| Bug | Medium/Low | Specify (delta) → Executor (next scheduled wave) |
| Feature | Any | Interview → Specify → Propose → Decompose |
| Debt | Any | Clean (if COSMETIC) or Specify + Executor (if structural) |
| Question | Any | Interview |
| Security | Any | Security gateway (immediately) + severity-based routing |

## Workflow

1. Receive issue from any source
2. Check Memory for prior triage records on same topic — count occurrences, apply recurrence escalation if > 1
3. Classify: severity + type
4. Determine routing from routing table
5. Write triage record to Memory as FRESH drawer
6. Route to declared module with triage record as context
7. Write Triage receipt

## Triage record format

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

## Output contract

Writes a receipt to `.wabblespec/receipts/` on successful completion.

## What not to do

- Do not fix issues — classify and route only
- Do not skip the Memory recurrence check
- Do not route security issues anywhere except the Security gateway first
- Do not apply routing from memory — consult the routing table on each triage
- Do not write triage records outside Memory
