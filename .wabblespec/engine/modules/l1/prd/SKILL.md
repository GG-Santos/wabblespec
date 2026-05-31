---
name: prd
description: Produces a structured Product Requirements Document from a user's product concept or existing draft, applying a 7-criterion quality gate and optionally continuing to a technical task card. Use when a stakeholder-facing PRD is needed before technical spec work begins.
allowed-tools: Read, Write, Edit, Bash
---

# PRD

You produce a structured, stakeholder-ready Product Requirements Document. A PRD describes what to build and why — not how to build it. Technical implementation details belong in a technical spec or task card downstream.

## What this skill does

Accepts a product concept description or an existing PRD draft. Produces an 11-section PRD using a structured format and validates it against 7 quality criteria. Optionally continues into a technical task card via Specify.

Does not generate system architecture, database schemas, API contracts, or implementation plans — those belong downstream in Specify or Decompose.

Not guaranteed: PRD produces a document artifact; the user decides whether it is ready for stakeholder review. The skill validates structure and quality criteria, not business correctness.

## When to use

- User wants a stakeholder-facing document before technical work begins
- Explicit `/prd` command
- Specify receives a user description that is too high-level for a task card (no concrete acceptance criteria possible yet)
- Product concept exists but no written requirements document

## When NOT to use

- A task card already exists and scope is defined — use Specify or Decompose instead
- The user wants an engineering spec or API design — those are task cards, not PRDs
- The output of a completed PRD is already available and the user wants implementation — go to Specify or Decompose

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `concept` | string | yes (if no file) | Product concept description from user |
| `existing_file` | file path | no | Existing PRD draft to validate and improve |
| `target_audience` | string | no | Stakeholder type (PM, investors, designers, engineering) — defaults to general |
| `continue_to_spec` | bool | no | After PRD locks, continue to Specify for a technical task card. Default: false. |

## How to do it

### Step 1 — Gather requirements

**If `existing_file` provided:** read it. Use it as the starting document. Identify which sections are missing or incomplete — these become the interview targets.

**If `concept` provided without a file:** ask up to 3 clarifying questions before drafting, covering the highest-priority gaps:
- Who are the target users and what specific pain do they have?
- What does success look like — how will you know this worked?
- What is explicitly out of scope for this version?

Do not draft until you have enough to write substantive answers for at least the Problem Statement, Target Users, and Success Metrics sections.

### Step 2 — Draft the PRD

Produce all 11 sections. For sections where information is thin, state the assumption explicitly ("Assumed: X — validate with stakeholder") rather than leaving the section empty.

**PRD structure:**

```
# Product Requirements Document

**Product:** <name>
**Version:** 1.0
**Date:** <ISO-8601>
**Status:** Draft

## 1. Executive Summary
2–3 paragraphs. Problem, solution, and target outcome. No technical details.

## 2. Problem Statement / Opportunity
What specific problem exists. Evidence of the pain (user quotes, data, observation). What happens if this is not solved.

## 3. Target Users / Personas
Named personas with: role, goals, pain points, technical sophistication level, privacy/security concerns, and devices/environments used. Minimum 1 primary persona, optional secondary personas.

## 4. User Stories / Use Cases
As a <persona>, I want <action> so that <benefit>.
Each story maps to a persona. Cover the core journey and critical edge cases.

## 5. Functional Requirements
Numbered list. What the product does. Verb-noun form: "The system shall allow users to X."
No implementation details.

## 6. Non-Functional Requirements
Performance, availability, security, accessibility, compliance, localization.
Each requirement is measurable.

## 7. Success Metrics / KPIs
Specific, measurable outcomes. Format: Metric / Target value / Measurement method / Timeline.

## 8. Scope
### In Scope
### Out of Scope

## 9. Dependencies
External systems, teams, data sources, or third-party services this requires.

## 10. Risks and Mitigations
Risk / Likelihood / Impact / Mitigation for each.

## 11. Timeline / Milestones (optional)
If known. Do not fabricate.
```

### Step 3 — Validate against 7 PRD criteria

Before presenting the draft to the user, check all 7 criteria. Fix any that fail:

- [ ] **Problem definition has evidence** — not just "users struggle with X" but why, with specifics or data
- [ ] **Personas are specific** — named, with real pain points, not generic demographic descriptions
- [ ] **User stories use proper format** — "As a [persona], I want [action] so that [benefit]" — every story traceable to a persona
- [ ] **Success metrics are measurable** — specific numeric targets with measurement methods (not "improve user satisfaction")
- [ ] **Scope explicitly lists what is OUT** — not just what is in scope
- [ ] **Risk assessment is realistic** — risks have likelihood + impact + mitigation, not just a list of fears
- [ ] **No technical implementation details** — databases, frameworks, deployment strategies, API schemas belong in a tech spec, not a PRD

For each failed criterion, rewrite the relevant section before proceeding. Do not surface a draft that fails criteria 3, 4, or 5 — these are the most commonly requested by stakeholders.

### Step 4 — Present and confirm

Show the user the complete draft. Report how many criteria passed (target: 7/7). Ask one question:

> "Does this capture your intent? Any changes before I write the final version?"

Incorporate feedback and re-run the 7-criterion check if substantive changes were made.

### Step 5 — Write PRD artifact and receipt

Write the final PRD to `.wabblespec/state/plans/prd.md` (if operating in framework context) or `prd-output.md` in the working directory (if operating ad-hoc).

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type generic \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --target prd \
  --summary "PRD: <product name>; <N>/7 criteria passed; <persona-count> personas; <story-count> user stories" \
  --out .wabblespec/state/receipts/prd-receipt-<timestamp>.json
```

### Step 6 — Optional: Continue to Technical Task Card

If `continue_to_spec: true` or user requests it after reviewing the PRD:

1. Tell the user: "PRD is complete. I'll now generate a technical task card based on this PRD."
2. Extract the core goal from the Executive Summary
3. Derive acceptance criteria from the Functional Requirements and Success Metrics — translate each functional requirement into a GWT criterion
4. Pass to Specify with the PRD as context: invoke Specify with the PRD as the backing document, scope set to the PRD's In Scope section, and non-goals from the PRD's Out of Scope section
5. The resulting task card references the PRD for business rationale — engineers reading the task card can trace back to the PRD for the "why"

## Output contract

**prd.md** (written to `.wabblespec/state/plans/prd.md` or `prd-output.md`):
- All 11 sections present (Section 11 may be empty if timeline unknown)
- 7/7 criteria passed (or document notes which criteria have open assumptions)
- Personas named and described
- User stories in proper format

**receipt** (`.wabblespec/state/receipts/prd-receipt-<timestamp>.json`):
- `status: PASS`
- `summary` includes product name, criteria count, and persona count

## Pitfalls

- **Writing technical details into functional requirements.** "The system shall store data in PostgreSQL" is a technical decision, not a requirement. Rewrite as "The system shall persist user data across sessions."
- **Generic personas.** "A typical user who wants to save time" is not a persona. Name them, give them a job, a specific workflow pain, and a device context.
- **Unmeasurable success metrics.** "Improve user engagement" cannot be tracked. "Increase daily active users from 1,000 to 5,000 within 90 days of launch" can.
- **Skipping the Out of Scope section.** Stakeholders argue about scope more than anything else. The Out of Scope section prevents scope creep and misaligned expectations.
- **Confusing assumptions with facts.** When you write an assumption, mark it explicitly. Unmarked assumptions become requirements that no one agreed to.

## When NOT to use

- Technical spec or engineering design needed — use Specify or Decompose
- Task card already exists with concrete acceptance criteria — PRD is upstream, not a replacement
- User asks to review or critique an existing PRD without producing a new one — use Adversary (`challenger_mode: open`) instead
