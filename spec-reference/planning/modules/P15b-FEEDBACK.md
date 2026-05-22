# Module Plan — Feedback (L8)

**Tier:** 3 — SUPPORTING
**Layer:** L8 Evolution
**v5.3 origin:** Feedback module — explicit human signal capture for Evolution pipeline

---

## Purpose

Capture and structure explicit user and stakeholder feedback signals. Distinct from Instinct (which observes execution events implicitly). Feedback captures explicit human evaluation: corrections, preferences, complaints, endorsements. Structured records written to Memory. Instinct reads them as high-signal observations — corrections decay pattern confidence, endorsements reinforce it.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/feedback <type> <content>` command
- User corrects framework behavior mid-session (auto-detected correction event)
- Session end (Feedback prompted for optional session-level feedback)
- Retro produces feedback records (routed through Feedback for structuring)

---

## Feedback Types

| Type | Definition | Instinct signal |
|---|---|---|
| Correction | Framework did something wrong — explicit fix provided | Negative: decay related pattern confidence |
| Preference | User prefers a different approach — no hard error | Soft negative: minor confidence decay |
| Complaint | Something is frustrating — no specific fix provided | Negative: flag for Synth proposal |
| Endorsement | User explicitly approves an approach | Positive: reinforce pattern confidence |
| Question | User needed to ask something that should have been obvious | Neutral: flag as clarity gap for Synth |

---

## Feedback Record Format

```markdown
# Feedback Record — <feedback-id>

**timestamp:** ISO 8601
**type:** correction|preference|complaint|endorsement|question
**session_id:** string
**source:** user|stakeholder|retro

## Content

<feedback as received>

## Structured Signal

**affected_module:** string (if identifiable)
**affected_pattern:** pattern-id from tracker.json (if identifiable)
**confidence_direction:** positive|negative|neutral

## Instinct Notification

**notify_instinct:** boolean
**signal_strength:** high|medium|low
```

Signal strength: corrections = high (explicit error), endorsements = medium (explicit approval), preferences/complaints = low (implicit signal).

---

## Workflow

```
1. Receive feedback (explicit command or auto-detected correction)

2. Classify feedback type

3. Identify affected module and pattern (if identifiable via EntityGraph)

4. Write feedback record to Memory as FRESH drawer

5. Notify Instinct if signal_strength >= medium:
   -> Correction: Instinct decrements pattern confidence
   -> Endorsement: Instinct increments pattern confidence
   -> Complaint: Instinct flags for Synth proposal evaluation

6. Route actionable feedback:
   -> Correction with specific fix: route to Triage
   -> Complaint (no fix): route to Synth (pattern issue)
   -> Question: route to Interview (clarity gap)

7. Write Feedback receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — explicit command + auto-detection |
| `rules/signal-strength.md` | Rules | Signal strength per feedback type |
| `rules/routing-policy.md` | Rules | Actionable feedback routing |
| `schemas/feedback-record.schema.json` | Schema | Feedback record format |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Instinct | Feedback notifies Instinct with confidence direction and signal strength |
| Memory | Feedback writes all records to Memory as FRESH drawers |
| Triage | Corrections with fixes routed to Triage for classification and action |
| Synth | Complaints routed to Synth for improvement proposal evaluation |
| Interview | Questions routed to Interview as clarity gaps |
| Retro | Retro action items structured through Feedback before routing |

---

## Verification Mode

**Observation** — feedback record written to Memory, Instinct notified for signals >= medium, actionable feedback routed, receipt written.

---

## Receipt Extension Fields

```json
{
  "feedback_id": "string",
  "type": "string",
  "signal_strength": "string",
  "instinct_notified": "boolean",
  "routed_to": "string",
  "affected_module": "string"
}
```
