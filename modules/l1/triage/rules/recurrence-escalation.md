# Recurrence Escalation — Triage

## Purpose

Recurring issues signal systemic problems that base severity alone does not capture. Recurrence escalation ensures patterns are not dismissed as isolated incidents.

## Recurrence check

Before classifying any issue, Triage reads Memory for prior triage records on the same topic. Match on:
- Same component or module
- Same symptom description (semantic match — not exact string match)
- Same error code or error event type

## Escalation rules

| Occurrence count | Action |
|---|---|
| 1 (first occurrence) | Assign base severity. No escalation. |
| 2 (second occurrence) | Escalate severity one level. Note prior occurrence in triage record. |
| 3+ (third or more) | Escalate to High minimum. Trigger Synth proposal automatically. |

Critical severity cannot be escalated further. If base severity is already Critical, recurrence still triggers Synth proposal at third+ occurrence.

## Synth proposal trigger

At third+ occurrence, Triage notifies Synth with:
- The triage record for the current occurrence
- The prior triage record IDs
- The pattern observed (same component, same symptom)

Synth generates a proposal to address the root cause rather than the symptom. Synth proposal does not block the current triage routing — both proceed.

## Recurrence count in receipt

Record the recurrence count in the triage receipt (`recurrence_count` field). Set `escalated: true` if any escalation was applied.

## False recurrence

If two issues match on component but describe unrelated symptoms, they are not recurrences of each other. Apply judgment — if the prior resolution addressed a different problem, treat as first occurrence.
