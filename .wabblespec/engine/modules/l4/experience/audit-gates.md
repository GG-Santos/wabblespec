# Experience Gateway — Audit Gates

Verifier registers these gates when Experience gateway activates. All HARD gates must PASS for gateway receipt to be PASS. SOFT gates flag only.

## User Research Gates

| Gate | Severity | Check |
|---|---|---|
| UR-1 | HARD | Research method declared with rationale |
| UR-2 | HARD | Minimum 5 participants for usability studies |
| UR-3 | HARD | Research cadence declared at P1 |
| UR-4 | HARD | Research artifacts written to Memory after every research cycle |
| UR-5 | SOFT | Screening criteria declared before recruitment |

## Usability Testing Gates

| Gate | Severity | Check |
|---|---|---|
| UT-1 | HARD | Test scenarios are task-based (not feature walkthroughs) |
| UT-2 | HARD | Every critical user journey has a corresponding test scenario |
| UT-3 | HARD | All 4 metrics declared and measured |
| UT-4 | SOFT | Facilitator guide prepared with neutral phrasing |
| UT-5 | SOFT | Remote/in-person format declared with tooling |

## Accessibility Deep-Dive Gates

| Gate | Severity | Check |
|---|---|---|
| AD-1 | HARD | Screen reader testing matrix declared |
| AD-2 | HARD | At minimum VoiceOver + NVDA tested for web targets |
| AD-3 | HARD | Deuteranopia simulation testing completed |
| AD-4 | HARD | All informational content distinguishable without color |
| AD-5 | HARD | No time limits without extension option |
| AD-6 | SOFT | Motor accessibility scope declared |

## Satisfaction Measurement Gates

| Gate | Severity | Check |
|---|---|---|
| SM-1 | HARD | SUS declared in scope or out of scope at P1 |
| SM-2 | SOFT | NPS only declared when >= 100 active users per period |
| SM-3 | SOFT | Data retention and anonymization declared for satisfaction data |

## Research Ethics Gates

| Gate | Severity | Check |
|---|---|---|
| RE-1 | HARD | Informed consent obtained from all participants |
| RE-2 | HARD | Participant data anonymized before storage |
| RE-3 | HARD | No participant PII in Memory drawers |
| RE-4 | HARD | Retention period declared |
| RE-5 | HARD | Compensation declared and provided |

## Pre-Research Design Quality Gates (5-Dimensional Critique)

Run before any participant is exposed to a deliverable. All five dimensions must score >= 3/5. Any dimension below 3 blocks this gate group.

| Gate | Severity | Dimension | Question |
|---|---|---|---|
| PQ-1 | HARD | Philosophy | Is the visual stance coherent with the brief and the declared style? Is it specific to this project or generic? |
| PQ-2 | HARD | Hierarchy | Does each view have a single declared dominant element? Is reading order obvious? |
| PQ-3 | HARD | Detail | Do motion, ease, and duration choices match the declared mood? Or are they defaulted without rationale? |
| PQ-4 | HARD | Function | Do all flows complete end-to-end without structural gaps? Do interactions match platform conventions? |
| PQ-5 | HARD | Innovation | Is there at least one moment specific to this product — not generic AI output? |

**Scoring:** 5 = fully resolved. 4 = resolved with minor gaps. 3 = acceptable baseline. 2 = significant gap. 1 = not addressed.

**Method:** For each dimension, read the deliverable and assign a score. Record the score and a one-sentence rationale. Any score below 3 fails the gate. Two rescore passes are allowed before Attestation is required. Record all scores in the gateway receipt under `pre_research_quality:`.

## Anti-Slop Intentionality Gate

| Gate | Severity | Check |
|---|---|---|
| AS-1 | SOFT | All copy in the deliverable is product-specific, not generic placeholder filler |
| AS-2 | SOFT | Color and typography choices are traceable to a stated rationale, not memory-defaulted |
| AS-3 | SOFT | Any default pattern (uniform card grids, all-centered layout, gradient text) has a documented decision |

**AS-1/AS-2/AS-3 method:** For each flagged item, check whether the relevant doc (brand.md, task-card assumptions, design spec) contains a rationale that ties the choice to the project brief. Undocumented default = SOFT flag. Documented with rationale = pass.

**Note:** AS gates do not require all defaults to be eliminated — they require all defaults to be intentional and documented. A uniform card grid with "this project is a card-based product catalog, repetition is the feature" passes.
