# WabbleSpec v6.1 — Experience

**Gateway:** Experience
**Layer:** L4 Capability
**Tier:** 1 — CRITICAL ROUTING
**Document scope:** Experience gateway — user research, usability testing, accessibility deep-dives, satisfaction measurement

---

## Overview

The Experience gateway owns the human side of validation: user research, usability testing, deep accessibility audits, and satisfaction measurement. Where Design declares how flows should work and Aesthetic declares how they should look, Experience validates whether they actually work for real users. Experience applies to visual-facing targets where user research is declared in scope at P1.

**In scope:**
- User research (methods, participants, research artifacts, cadence)
- Usability testing (task scenarios, facilitation, metrics, remote vs. in-person)
- Accessibility deep-dives (screen reader matrix, cognitive accessibility, color blindness testing, motor accessibility)
- Satisfaction measurement (SUS, NPS, in-product feedback)
- Research ethics (informed consent, anonymization, compensation)

**Applies to:** Visual-facing targets (Web, Mobile, Desktop, Game, Extension/Plugin) where user research is declared in scope at P1.

Note: Experience gateway activation requires explicit scope declaration at P1. Design gateway (accessibility floor) applies to all visual targets unconditionally. Experience adds research and deep accessibility validation on top of Design's baseline.

---

## Gateway Structure

```
.wabblespec/gateways/experience/
  SKILL.md
  skill-rules.json
  references/
    user-research.md
    usability-testing.md
    accessibility.md
    satisfaction-measurement.md
  rules/
    research-ethics.md
  evaluations/
  schemas/
    receipt.schema.json
```

---

## Activation

`skill-rules.json` triggers Experience gateway on:
- Visual-facing target with user research declared in scope at P1
- P1 or P4 stage when user validation is declared
- Verifier Demonstration mode for user-facing deliverables
- Explicit `/experience` command

---

## User Research

**Reference:** `references/user-research.md`

### Research Methods

Method chosen based on the research question, not convenience:

| Question type | Method |
|---|---|
| What do users need? | Interviews |
| How do users use the product? | Observation / diary studies |
| Which option works better? | Usability test / A/B test |
| How satisfied are users? | Survey (SUS, NPS) |
| What are users doing? | Analytics / clickstream analysis |
| What do users think? | Focus groups (use sparingly — social dynamics distort) |

No single method for all questions. Method declared in spec with rationale.

### Participant Recruitment

- Minimum 5 participants for usability testing (Nielsen heuristic — 5 participants find ~85% of usability issues)
- Participants representative of declared target user segments (not convenience sampling unless justified)
- Screening criteria declared before recruitment
- Compensation declared and provided — no uncompensated high-effort participation

Participant data handled per research ethics policy.

### Research Artifacts

All research produces structured artifacts written to Memory as FRESH drawers:

| Artifact | Content | Written to |
|---|---|---|
| Synthesis note | Key patterns from sessions | Memory drawer (FRESH) |
| Affinity diagram | Clustered observations | Memory drawer (FRESH) |
| Insight list | Distilled findings with evidence | Memory drawer (FRESH) |
| Recommendation list | Actionable design directions | Memory drawer (FRESH) |

Research artifacts written to Memory enable Instinct to track patterns across research cycles. Insights accumulate — they are not discarded at the end of each research sprint.

### Research Cadence

Declared in spec at P1 — one of:
- **Continuous discovery:** Ongoing user contact throughout development (weekly or bi-weekly sessions)
- **Milestone-based:** Research at declared milestones (concept, prototype, beta, post-launch)

Not declared = milestone-based at minimum: concept stage and beta/launch stage. Continuous discovery requires team capacity declaration.

---

## Usability Testing

**Reference:** `references/usability-testing.md`

### Test Scenarios

Task-based scenarios — not feature walkthroughs. Users perform real tasks, not feature demonstrations.

Good scenario format:
> "You want to change the email address associated with your account. Please do that."

Not:
> "Find the Account Settings page and click on Email."

Scenarios derived from declared critical user journeys (Design gateway). Every critical user journey has a corresponding usability test scenario.

### Facilitator Guide

- Neutral phrasing — no leading questions
- Think-aloud protocol: participants narrate their thought process
- Probe questions prepared: "What were you expecting to happen?" / "What would you do next?"
- No coaching or hints during task — note confusion as data
- Debrief protocol: subjective experience captured after tasks complete

### Metrics

| Metric | Measurement |
|---|---|
| Task completion rate | Binary (completed / not completed) per task per participant |
| Time on task | Seconds from task start to task completion or abandonment |
| Error rate | Count of errors (wrong paths, backtracking, incorrect inputs) per task |
| User satisfaction | Post-session rating (SUS scale or single ease-of-use item) |

Metrics aggregated across participants. Qualitative observations annotated alongside quantitative metrics.

### Remote vs. In-Person

Declared in spec with tooling declared:
- **Remote:** Screen sharing tool + recording declared (Lookback, Maze, UserTesting, or equivalent)
- **In-person:** Location, equipment, and consent process declared

Both formats produce equivalent artifacts. Remote moderation note: watch for participant behavior changes due to technology friction vs. actual UX issues.

---

## Accessibility Deep-Dive

**Reference:** `references/accessibility.md`

The Design gateway sets the accessibility floor (WCAG 2.1 AA). The Experience gateway conducts the deep-dive testing that verifies the floor is actually met — not just that the code claims to meet it.

### Screen Reader Testing Matrix

Declared per project — targets the platforms the product serves:

| Platform | Screen reader |
|---|---|
| macOS | VoiceOver |
| iOS | VoiceOver |
| Windows | NVDA (free) or JAWS (enterprise) |
| Android | TalkBack |
| Web (cross-platform) | At minimum: VoiceOver + NVDA |

Combination tested: screen reader + browser combination matters. VoiceOver + Safari, NVDA + Chrome, JAWS + Chrome are the common high-priority combinations for web. Matrix declared in spec.

### Cognitive Accessibility

- Plain language: Flesch-Kincaid reading ease score targeted for audience (not a strict requirement — a guideline)
- Consistent navigation: nav structure identical across pages — no surprise changes
- No time limits without extension: timed operations offer extension option (WCAG 2.1 AA requirement)
- Error prevention: irreversible actions have confirmation step; form inputs have review step before submission
- Clear instructions: instructions don't rely solely on sensory characteristics ("click the blue button" is not accessible — "click the Submit button" is)

### Color Blindness Testing

Tested with deuteranopia simulation (red-green color blindness — most common form). Additional simulations declared if broader coverage is required:

| Type | Prevalence | Simulation tool |
|---|---|---|
| Deuteranopia | ~6% males | Browser DevTools, Figma, Stark |
| Protanopia | ~2% males | Same tools |
| Tritanopia | Rare | Same tools |

All informational content distinguishable without color alone. Color is used to reinforce meaning, not as the sole carrier of meaning.

### Motor Accessibility

Scope declared in spec — not required at baseline, but must be explicitly addressed if product serves users with motor impairments:

| Capability | What is tested |
|---|---|
| Switch access | Single-switch scanning navigation works |
| Voice control | Dragon NaturallySpeaking or Voice Control commands work on all interactive elements |
| Keyboard-only | Full operation without mouse (Design gateway baseline — included in deep-dive verification) |
| Pointer size | Minimum 44×44px targets (Design gateway requirement — verified here) |

---

## Satisfaction Measurement

**Reference:** `references/satisfaction-measurement.md`

### SUS (System Usability Scale)

Optional baseline metric for major releases. 10-item questionnaire, 5-point Likert scale, produces 0–100 score.

Benchmarks:
- > 80: Excellent (A grade)
- 68–80: Good (B–C grade)
- 51–68: Poor (D grade)
- < 51: Unacceptable (F grade)

SUS declared as in scope or out of scope at P1. Not required, but if customer satisfaction is a stated success metric, SUS provides a standardized baseline.

### NPS (Net Promoter Score)

Optional for long-running products with recurring users. Single question: "How likely are you to recommend [product] to a colleague? (0–10)". Promoters (9–10), Passives (7–8), Detractors (0–6).

NPS only meaningful with sample size sufficient for statistical stability. Not useful for products with < 100 active users per measurement period. Declared when in scope with measurement cadence.

### In-Product Feedback

Declared when continuous measurement is in scope:
- Micro-survey at key moments (after task completion, after error)
- Feedback widget (thumbs up/down, star rating, free text)
- Session replay sampling declared (with user consent)

Mechanism declared at P1. Data retention and anonymization declared alongside.

---

## Research Ethics

**Reference:** `rules/research-ethics.md`

### Informed Consent

Required for all research participants. Consent covers:
- What they are being asked to do
- How session data is recorded (screen, audio, video)
- How data will be used and stored
- Their right to withdraw at any time without consequence

Written consent for formal studies. Verbal consent with recording for remote sessions. No research without consent.

### Data Anonymization

Participant data anonymized before storage:
- Names replaced with participant IDs (P01, P02, etc.)
- Identifying details removed from session notes
- Recording access restricted (not shared beyond research team)
- Retention period declared — data deleted after retention window

Research artifacts stored in Memory are anonymized before writing. No participant PII in Memory drawers.

### Compensation

Declared in spec — participants compensated appropriately for their time:
- 60-minute usability session: equivalent to ~$75–100 USD depending on region and participant expertise
- Survey (10–15 minutes): smaller incentive or entry into prize draw
- Diary study (2 weeks): ongoing compensation for effort

Uncompensated high-effort participation is not an acceptable approach. Research ethics policy prohibits it.

---

## Integration Points

| Module | Relationship |
|---|---|
| Apply | Apply reads Experience gateway for routing when user research activities are declared |
| Verifier | Verifier Demonstration mode for user-facing deliverables consults Experience gateway for usability test coverage |
| Design gateway | Experience validates Design gateway user flows via usability testing |
| Aesthetic gateway | Experience deep-dive includes accessibility testing that verifies Aesthetic contrast and motion requirements |
| Memory | Research artifacts (insights, synthesis) written to Memory as FRESH drawers; Instinct tracks patterns across research cycles |
| ResearchLog (L6) | ResearchLog captures research session structure; Experience gateway writes findings through ResearchLog |

---

## Verification Mode

**Demonstration** — usability test conducted (if in scope), accessibility matrix tested against declared targets, research insights written to Memory, research ethics requirements met.

---

## Receipt Extension Fields

```json
{
  "research_in_scope": true,
  "usability_test_conducted": true,
  "accessibility_matrix_tested": ["VoiceOver+Safari", "NVDA+Chrome"],
  "insights_written_to_memory": 0
}
```

---

## Cross-References

- Design gateway (UX baseline, user flows, accessibility floor): `WabbleSpec v6.1 — Design.md`
- Aesthetic gateway (visual standards, contrast, motion): `WabbleSpec v6.1 — Aesthetic.md`
- L5 Memory (research artifact storage): `WabbleSpec v6.1 — Memory.md`
- L6 ResearchLog (research session capture): `WabbleSpec v6.1 — Expression.md` § ResearchLog
- Verification modes (Demonstration): `WabbleSpec v6.1 — Core.md` § Verification Modes
