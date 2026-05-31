# Ref-Plan: ui-ux-pro-max-skill-main

**Date:** 2026-05-31  
**Session:** tier7-expansions-20260530  
**Based on:** `research/ref-eval/ui-ux-pro-max-skill-main.md`  
**Goal directive:** implement all tiers

---

## Candidate Table

| ID | Item | Type | Impact | Project fit | Risk |
|---|---|---|---|---|---|
| C1 | Banner safe zone rules (numeric constants) | Behavioral | Medium | High | Low |
| C2 | State priority order + transition duration constants | Behavioral | Medium | High | Low |
| C3 | Duarte Sparkline emotional arc | Behavioral | Medium | High | Low |
| C4 | Token compliance HARD-GATE (no raw hex) strengthening | Behavioral | Low | High | Low |

## Exclusion List

| Item | Reason |
|---|---|
| Model names (gemini-*) | I6 |
| AskUserQuestion calls | Prior directive |
| Node CJS scripts | Not portable |
| Three-layer token system (as new content) | Already covered by gateway-aesthetic |

## Scored and Ranked

| ID | Score | Tier |
|---|---|---|
| C1 | (2×2)+3-1 = 6 | Tier 1 |
| C2 | (2×2)+3-1 = 6 | Tier 1 |
| C3 | (2×2)+3-1 = 6 | Tier 1 |
| C4 | (1×2)+3-1 = 4 | Tier 1 |

---

## Tier 1 — Behavioral additions

**[T1-1] Banner safe zone rules in gateway-aesthetic**
- What: Add `## Banner Safe Zones` section to gateway-aesthetic SKILL.md
- Where: `.claude/skills/gateway-aesthetic/SKILL.md`
- How: Add after the existing 3-tier accent token section. Content:

  `## Banner Safe Zones`
  
  When generating banner or cover assets for any platform, enforce:
  - Critical content (text, logo, CTA) must occupy the central 70-80% only — never bleed to edges
  - One CTA per banner, positioned bottom-right, minimum 44px height
  - Maximum 2 font families; body text minimum 16px; headline minimum 32px
  - Ad banners (Google, Meta): text coverage must remain under 20% of total area (Meta penalizes text-heavy ads)
  - Print assets: 300 DPI minimum, CMYK color space, 3-5mm bleed margin
  
  Platform reference dimensions (px):
  | Platform | Type | Dimensions |
  |---|---|---|
  | Facebook | Cover | 820 × 312 |
  | Twitter/X | Header | 1500 × 500 |
  | LinkedIn | Personal | 1584 × 396 |
  | YouTube | Channel art | 2560 × 1440 |
  | Instagram | Story | 1080 × 1920 |
  | Instagram | Post | 1080 × 1080 |
  | Google Ads | Med Rectangle | 300 × 250 |
  | Website | Hero | 1920 × 600-1080 |

- Literal values: 70-80%; 44px; 16px; 32px; 20%; 300 DPI; 3-5mm; all platform pixel dimensions verbatim
- Gate: `## Banner Safe Zones` section present with 5 rules and the platform dimension table
- Reference location: `design/SKILL.md` lines 172-177; drawer `banner-safe-zones-and-state-specs.json`
- Sync: `.wabblespec/engine/modules/l4/gateway-aesthetic/SKILL.md`

**[T1-2] State priority order and transition duration constants in gateway-aesthetic**
- What: Add `## Interactive State Specification` section to gateway-aesthetic SKILL.md
- Where: `.claude/skills/gateway-aesthetic/SKILL.md`
- How: Add after Banner Safe Zones. Content:

  `## Interactive State Specification`
  
  **State priority order (when multiple states apply simultaneously, highest wins):**
  disabled > loading > active > focus > hover > default
  
  **Transition duration constants:**
  | Property | Duration | Easing |
  |---|---|---|
  | Color changes | 150ms | ease-in-out |
  | Background | 150ms | ease-in-out |
  | Transform | 200ms | ease-out |
  | Opacity | 150ms | ease |
  | Shadow | 200ms | ease-out |
  
  **Focus ring spec:** `box-shadow: 0 0 0 2px var(--color-background), 0 0 0 4px var(--ring-color)` — ring width 2px, ring offset 2px, ring color = primary.
  
  **Color contrast minimums:** Normal text 4.5:1; Large text (18px+) 3:1; UI components 3:1; Focus indicator 3:1.

- Literal values: Priority order (disabled > loading > active > focus > hover > default); all ms values verbatim; focus ring CSS pattern; contrast ratios
- Gate: Section present with priority order listed, duration table with all 5 rows, focus ring CSS, contrast ratios
- Reference location: `design-system/references/states-and-variants.md`; drawer `banner-safe-zones-and-state-specs.json`
- Sync: `.wabblespec/engine/modules/l4/gateway-aesthetic/SKILL.md`

**[T1-3] Duarte Sparkline emotional arc in present**
- What: Add `## Narrative Arc` section to present SKILL.md
- Where: `.claude/skills/present/SKILL.md`
- How: Add before the output contract section. Content:

  `## Narrative Arc`
  
  For delivery presentations, apply the Duarte Sparkline emotional arc to maintain stakeholder engagement:
  
  - Alternate between "What Is" (current state, tension, problem framing) and "What Could Be" (resolved state, opportunity, future vision)
  - Apply pattern breaks at the 1/3 and 2/3 positions in the deck: a slide that shifts emotional register prevents the audience from going numb to a uniform tone
  - A 9-slide deck: slides 1-3 establish "What Is", slide 3 breaks to "What Could Be", slides 4-6 return to "What Is" complexity, slide 6 breaks again, slides 7-9 close on "What Could Be"
  - This applies to both the wave summary deliveries and the standalone task delivery formats

- Literal values: "What Is" and "What Could Be"; "1/3 and 2/3 positions"
- Gate: `## Narrative Arc` section present with Duarte Sparkline named, What Is / What Could Be pattern, and 1/3 + 2/3 break positions
- Reference location: `design-system/SKILL.md` Duarte Sparkline section; drawer `duarte-sparkline-and-tier7.json`
- Sync: `.wabblespec/engine/modules/l7/present/SKILL.md`

**[T1-4] Token compliance HARD-GATE in gateway-aesthetic**
- What: Add explicit "no raw hex in generated code" rule to gateway-aesthetic's existing design token policy section
- Where: `.claude/skills/gateway-aesthetic/SKILL.md`
- How: Find the existing design token policy gate (near `## Phase B` or `## What this skill does` table row about "Design token policy"). Add: "Generated code must not contain raw hex values (`#RRGGBB`), raw `rgb()`/`rgba()`, or raw `px`/`rem` values for visual properties. Every visual value must reference a design token via `var(--token-name)`. Hardcoded values in generated CSS, inline styles, or component code are a design token policy violation — flag as BLOCK."
- Literal values: "#RRGGBB"; "rgb()/rgba()"; "var(--token-name)"; "flag as BLOCK"
- Gate: Rule present in gateway-aesthetic SKILL.md with hex pattern, function patterns, and BLOCK verdict named
- Reference location: `design-system/references/token-architecture.md` + `design-system/SKILL.md` Token Compliance section
- Sync: `.wabblespec/engine/modules/l4/gateway-aesthetic/SKILL.md`

---

## Tier 6 — Synthesis (implement per goal directive)

**[T6-1] Token compliance check in gateway-aesthetic Phase B audit**
- What: Add generated-code hex scan to gateway-aesthetic's Phase B verdict procedure
- Where: `.claude/skills/gateway-aesthetic/SKILL.md` Phase B section + `gateway-aesthetic/audit-gates.md`
- How: In the Phase B section, add to the audit sequence: "Scan generated output artifacts for raw hex/px/rgb() in CSS or style contexts. Any instance → BLOCK (design token policy violation)."
- Gate: Hex scan present in Phase B procedure; audit-gates.md has entry for "raw-value-in-generated-code → BLOCK"
- Reference location: `design-system/SKILL.md` Token Compliance section

---

## Tier 7 — Expansion Roadmap

| Capability | Effort | Session seed |
|---|---|---|
| HTML slide generation with Chart.js + token validation | days | "Add HTML slide generation to present skill: create `.wabblespec/engine/shared/scripts/generate-slide.py` that reads design-tokens.css and produces Chart.js HTML presentation; create `slide-token-validator.py` that greps generated HTML for raw hex/rgb patterns and exits non-zero if found; reference: `design-system/SKILL.md` slide system and `scripts/generate-slide.py`; drawer: `ui-ux-pro-max-skill-main/duarte-sparkline-and-tier7.json`" |
| AI logo + CIP generation (gated on Gemini API) | weeks | "Build `.wabblespec/engine/shared/scripts/brand-assets.py` that wraps Gemini image generation for logo (55 styles) and CIP deliverables (50 types); reference: `design/scripts/logo/generate.py` and `design/scripts/cip/generate.py`; gated on `GEMINI_API_KEY` env var availability" |

---

## Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| `gemini-*` model names | I6 |
| AskUserQuestion calls | Prior directive |
| Node CJS scripts | Not portable |

## Priority Implementation Order

| Order | ID | Item | Why first |
|---|---|---|---|
| 1 | T1-1 | Banner safe zones | Pure addition, no dependency |
| 2 | T1-2 | State priority + transition durations | Pure addition, no dependency |
| 3 | T1-3 | Duarte Sparkline | Different file from T1-1/T1-2; independent |
| 4 | T1-4 | Token compliance HARD-GATE | Strengthens existing gate; no dependency |
| 5 | T6-1 | Phase B hex scan | Depends on T1-4 defining the rule it enforces |

## Execution Notes
- T1-1 and T1-2 both target gateway-aesthetic SKILL.md; apply sequentially
- T1-3 targets present SKILL.md — independent; read present SKILL.md before editing
- T6-1 also requires editing audit-gates.md — check if that file exists
- All items require engine module sync
