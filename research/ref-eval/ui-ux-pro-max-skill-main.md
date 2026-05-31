# Ref-Eval: ui-ux-pro-max-skill-main

**Date:** 2026-05-31  
**Slug:** ui-ux-pro-max-skill-main  
**Trust level:** MEDIUM  
**Reference path:** `C:\Vaults\references\Core Project References\ui-ux-pro-max-skill-main`

---

## File Inventory

| File | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| .claude/skills/design/SKILL.md | Master design router | Medium | Sub-skill routing, banner safe zones, icon styles (15), CIP deliverables (50+), social photo workflow 8-step | Read |
| .claude/skills/brand/SKILL.md | Brand identity | Small | inject-brand-context, sync-brand-to-tokens pattern, 10 reference docs | Read |
| .claude/skills/design-system/SKILL.md | Token + slides | Medium | Three-layer token system, contextual slide decision CSVs, token compliance rule | Read |
| .claude/skills/slides/SKILL.md | Slides routing | Small | Delegates to references/create.md | Read |
| .claude/skills/design/references/design-routing.md | Task-to-skill router | Medium | Full task-type → sub-skill routing table, multi-skill workflow sequences, skill dependency tree | Read |
| .claude/skills/design-system/references/token-architecture.md | Token spec | Medium | Three-layer CSS with W3C DTCG alignment, naming convention `--{category}-{item}-{variant}-{state}` | Read |
| .claude/skills/design-system/references/states-and-variants.md | Component states | Medium | State priority order, focus ring spec (2px/2px), transition durations (150ms/200ms), ARIA state patterns | Read |
| .claude/skills/design/references/slides-create.md | Slides trigger | Small | Delegates to slides skill | Read |
| .claude/skills/design/references/* (remaining) | Logo/CIP/banner/icon references | Various | Domain-specific design knowledge | Transfer check: banner sizes (exact dimensions transferable), logo/CIP are Gemini-API dependent |
| .claude/skills/design-system/data/*.csv | Decision databases | Various | 15 slide strategies, 25 layouts, 25 copy formulas, 25 chart types, emotion arcs | Skimmed |
| .claude/skills/*/scripts/ | Generation scripts | Various | BM25 search engines, Gemini API calls, token validators, Node CJS scripts | Not read — Transfer check: Python scripts have BM25 patterns; Node CJS not portable; Gemini API dependency not transferable |
| .claude/skills/ui-styling/ | shadcn/Tailwind implementation | Various | Component implementation patterns | Not read — Transfer check: Tailwind/shadcn is web-stack-specific |
| .claude/skills/banner-design/SKILL.md | Banner skill | Small | Routes to design/references/banner-sizes-and-styles.md | Not read |
| canvas-fonts/ (various .ttf/.txt) | Font files | Binary | Not applicable | Skipped — font binary assets not transferable |

---

## Connection Map

```
[design/SKILL.md] --routes--> [brand/SKILL.md]: brand identity tasks
[design/SKILL.md] --routes--> [design-system/SKILL.md]: token architecture, slide generation
[design/SKILL.md] --routes--> [ui-styling/SKILL.md]: component implementation
[brand-guidelines.md] --sync--> [design-tokens.json] --sync--> [design-tokens.css]: single source of truth via sync-brand-to-tokens.cjs
[design-system/SKILL.md] --queries--> [data/*.csv]: slide strategy/layout/typography/color/animation selection
[design-system/SKILL.md] --validates--> [slide-token-validator.py]: HTML slides must pass token compliance check
[design/scripts/logo/search.py] --BM25--> [design/data/logo/*.csv]: returns brief → [generate.py] → image output
[design/references/design-routing.md]: canonical task-to-skill routing table referenced by all sub-skills
```

If `design-tokens.css` changes without updating `brand-guidelines.md`: sync script produces correct tokens but guidelines become out of date; audit trail breaks.

---

## Dimension 1 — Behavior

**Three-layer token system:**
1. Primitive: raw values (`--color-blue-600: #2563EB`; `--space-4: 1rem`)
2. Semantic: purpose aliases (`--color-primary: var(--color-blue-600)`)
3. Component: component-specific (`--button-bg: var(--color-primary)`)
Dark mode: override semantic layer only (`.dark { --color-background: var(--color-gray-900) }`). Never override primitive layer for theming.

**Token compliance hard rule:** Never use raw hex/px in component code. Always `var(--token-name)`. Validated by `slide-token-validator.py`. This is a non-negotiable constraint — slides that use `#FF6B6B` instead of `var(--color-primary)` fail validation.

**Naming convention:** `--{category}-{item}-{variant}-{state}`. Category set: `color`, `space`, `font-size`, `radius`, `shadow`, `duration`. Examples: `--color-primary`, `--color-primary-hover`, `--button-bg-hover`.

**State priority order (highest → lowest):** disabled > loading > active > focus > hover > default. When multiple states apply simultaneously, the highest-priority state wins.

**State transition duration constants:**
- Color changes: 150ms ease-in-out
- Background: 150ms ease-in-out
- Transform: 200ms ease-out
- Opacity: 150ms ease
- Shadow: 200ms ease-out

**Focus ring spec:** `box-shadow: 0 0 0 2px var(--color-background), 0 0 0 4px var(--ring-color)`. Ring width: 2px. Ring offset: 2px. Ring color: primary (blue-500).

**Banner safe zone rules (verbatim):**
- Critical content in central 70-80%
- One CTA per banner, bottom-right, min 44px height
- Max 2 fonts, min 16px body, ≥32px headline
- Text under 20% for ads (Meta penalizes)
- Print: 300 DPI, CMYK, 3-5mm bleed

**Duarte Sparkline emotional arc:**
- Premium decks alternate between "What Is" (frustration) ↔ "What Could Be" (hope)
- Pattern breaks applied at 1/3 and 2/3 positions in deck
- 15 deck structures with emotion arcs in `slide-strategies.csv`

**Contextual slide decision flow:**
1. Parse goal → query `slide-strategies.csv` → strategy + emotion beats
2. For each slide: query layout-logic.csv (layout + break_pattern) + typography.csv (type scale) + color-logic.csv (emotion → color) + backgrounds.csv (image category) + apply animation
3. Generate HTML with design tokens
4. Validate with `slide-token-validator.py`

---

## Dimension 2 — Format

**Token naming:** `--{category}-{item}-{variant}-{state}` — category is always first.

**CSS file structure:**
```css
/* === PRIMITIVES === */
:root { ... }
/* === SEMANTIC === */
:root { ... }
/* === COMPONENTS === */
:root { ... }
/* === DARK MODE === */
.dark { ... }
```

**W3C DTCG token JSON format:**
```json
{ "color": { "blue": { "600": { "$value": "#2563EB", "$type": "color" } } } }
```

**Component spec table (canonical format):**
| Property | Default | Hover | Active | Disabled |

**Color contrast minimums:** Normal text 4.5:1, Large text (18px+) 3:1, UI components 3:1, Focus indicator 3:1.

**Banner sizes (key platform values):**
- Facebook Cover: 820×312px
- Twitter/X Header: 1500×500px
- LinkedIn Personal: 1584×396px
- YouTube Channel: 2560×1440px
- Instagram Story: 1080×1920px
- Instagram Post: 1080×1080px
- Google Ads Med Rectangle: 300×250px
- Website Hero: 1920×600-1080px

---

## Dimension 3 — Interactions

**brand-guidelines.md → tokens:** One-way sync via `sync-brand-to-tokens.cjs`. Editing tokens.json directly → drift from guidelines. Protocol: edit guidelines first, then sync.

**Slide system CSVs:** Goal → strategies.csv is the entry point. All other CSVs (layout, typography, color, backgrounds, charts) are queried per-slide; they don't interact with each other directly.

**Token validator contract:** Slide HTML must import `assets/design-tokens.css` AND use only `var()` references. Any raw value in slide HTML = validator failure.

---

## Reference Type and Maturity

- **Type:** Production skill bundle — commercial claudekit design toolkit, version 2.1.0, MIT license
- **Maturity signals:** Versioned, published author, comprehensive reference docs, working scripts with test data
- **Red flags:** Model names hardcoded (`gemini-2.5-flash-image`, `gemini-3-pro-image-preview`, `gemini-3.1-pro-preview`) — I6 violations. Uses `AskUserQuestion` tool — prior directive prohibits adoption. External API dependency (Gemini API key). Node CJS scripts not portable to WabbleSpec Python environment.

---

## Section 1 — Reference Summary

Commercial claudekit design skill bundle covering brand identity, design tokens, UI implementation, logo/icon generation (AI), corporate identity program, HTML presentations, banner design, and social photos. Solves: consistent, token-compliant design output across multiple output types from a single brand source of truth.

**Behavioral content:** Three-layer token system; token compliance enforcement; state priority ordering; transition duration constants; Duarte Sparkline emotional arc for presentations; banner safe zone rules; contextual slide decision flow via CSV databases.

**Structural content:** `--{category}-{item}-{variant}-{state}` naming convention; 4-section CSS file structure; W3C DTCG JSON token format; component spec table pattern; task-to-skill routing table.

**Interaction content:** brand-guidelines.md → design-tokens sync; slide token validator as a hard gate; BM25 search → AI generation pipeline.

**Mature:** Token architecture, state specs, banner rules. **Experimental:** AI image generation (Gemini API). **Not portable:** Node CJS scripts, Gemini API dependency, AskUserQuestion calls.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| design/SKILL.md lines 172-177 | Banner safe zone rules (verbatim numeric constants) | WabbleSpec's gateway-aesthetic has banner content in audit-gates but no specific safe zone percentages or CTA size minimums | Add `## Banner Safe Zones` to `gateway-aesthetic/SKILL.md` with verbatim constants | Medium |
| design-system/references/states-and-variants.md | State priority order + transition duration constants | gateway-aesthetic currently covers design token policy and motion tokens but not the canonical state priority ordering or specific ms values | Add state priority table and transition duration constants to `gateway-aesthetic/SKILL.md` motion section | Medium |
| design-system/SKILL.md (Duarte Sparkline section) | "What Is ↔ What Could Be" emotional arc with 1/3 and 2/3 pattern breaks | WabbleSpec's `present` skill generates .pptx delivery presentations but has no guidance on narrative arc or emotional engagement structure | Add `## Narrative Arc` section to `present/SKILL.md` with Duarte Sparkline pattern | Medium |
| design-system/references/token-architecture.md | Token compliance rule: "never raw hex — always var()" | gateway-aesthetic already has design token policy and no-raw-values gate, but the specific "hardcoded hex in generated code" pattern is not named | Add explicit prohibition: "Generated code must not contain raw hex, px, or rgb() values for visual properties — all must reference tokens via var()" as a HARD-GATE | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| design/SKILL.md, design-system/SKILL.md | Hardcoded model names (gemini-2.5-flash-image, gemini-3-pro-image-preview, gemini-3.1-pro-preview) | I6 | Do not copy model references | Critical |
| brand/SKILL.md, design/SKILL.md | AskUserQuestion calls (`AskUserQuestion` for gallery, ideation) | Prior directive prohibits AskUserQuestion adoption | Adopt behavioral content only | High |
| scripts/ (CJS, Python with Gemini) | External API dependency + Node CJS not portable | WabbleSpec uses Python; Gemini API key requirement adds external vendor coupling | Do not adopt scripts; adopt rule content only | Medium |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Banner safe zone rules (numeric) | Adapt | Fills gap in gateway-aesthetic | `.claude/skills/gateway-aesthetic/SKILL.md` | Medium |
| State priority + transition durations | Adapt | Extends gateway-aesthetic motion tokens with specific ms values | `.claude/skills/gateway-aesthetic/SKILL.md` | Medium |
| Duarte Sparkline emotional arc | Adapt | Adds narrative structure to present skill | `.claude/skills/present/SKILL.md` | Medium |
| Token compliance HARD-GATE (no raw hex) | Adapt (strengthen existing gate) | Extends existing no-raw-values gate with explicit prohibition | `.claude/skills/gateway-aesthetic/SKILL.md` | Low |
| Model names (Gemini) | Avoid | I6 | Anywhere | Critical |
| AskUserQuestion calls | Avoid | Prior directive | Anywhere | High |
| Node CJS scripts | Avoid | Not portable | — | High |
| Three-layer token system (as new content) | Study Only | Already covered by gateway-aesthetic's design-tokens.md reference + hyperframes adoption | — | Low |
| BM25 search + AI generation pipeline | Study Only | Interesting pattern but requires external APIs and is not portable to WabbleSpec's Python environment | — | Low |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 7 | Design token policy, motion standards, and presentation narrative are directly relevant to gateway-aesthetic and present skills |
| Architecture fit | 5 | Skill structure is similar (.claude/skills/) but scripts (CJS/Gemini) are not portable |
| Implementation fit | 8 | All adoptable items are additive text additions to existing skills |
| Maintenance fit | 8 | Banner safe zones, state durations, and Duarte Sparkline are stable; not tied to external API evolution |
| Risk level | 2 | Only risk is model names and AskUserQuestion; both easily avoided |
| Overall usefulness | 6 | High value in specific numeric constants and narrative arc; lower value in AI generation pipeline |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (implement now):**
- Banner safe zone rules → gateway-aesthetic SKILL.md
- State priority + transition duration constants → gateway-aesthetic SKILL.md
- Duarte Sparkline → present SKILL.md
- Token compliance HARD-GATE strengthening → gateway-aesthetic SKILL.md

**Phase 4 (do not cross):** Model names, AskUserQuestion calls, Node CJS scripts.

---

## Section 7 — Final Verdict

**Classification: supporting-reference (6/10)**

**Best 3 to steal:**
1. Duarte Sparkline emotional arc (What Is ↔ What Could Be, 1/3 and 2/3 breaks) — `design-system/SKILL.md` — no equivalent in WabbleSpec's present skill
2. Banner safe zone rules with exact numeric constants — `design/SKILL.md` lines 172-177 — production-hardened output quality rules
3. State priority order (disabled > loading > active > focus > hover > default) — `design-system/references/states-and-variants.md` — precise enumeration missing from gateway-aesthetic

**Worst 3 to avoid:**
1. `gemini-2.5-flash-image`, `gemini-3-pro-image-preview` model references — I6
2. AskUserQuestion calls (`AskUserQuestion` for gallery, ideation) — prior directive
3. Node CJS scripts — not portable to WabbleSpec Python environment

**Recommended next action:** Implement Phase 1 items.

---

## Section 8 — Project Synthesis

**Synthesis 1: Token compliance gate in gateway-aesthetic verifying generated code**
- What: gateway-aesthetic's existing HARD GATE for no-raw-values + this reference's explicit "never raw hex in components" rule → add a generated-code check to the Phase B verdict: scan output artifacts for raw hex/px/rgb() in CSS/style contexts
- Reference contribution: "never use raw hex in components — always reference tokens" (design-system/SKILL.md)
- Project contribution: gateway-aesthetic's existing design token policy and Phase B audit gate
- Target: `.claude/skills/gateway-aesthetic/SKILL.md` Phase B section + `gateway-aesthetic/audit-gates.md`
- Gap closed: Current gate says "no raw values" but doesn't specify the check procedure in generated code

**Synthesis 2: Presentation narrative arc in present + report skills**
- What: present and report skills both generate structured deliveries; adding the Duarte Sparkline emotional arc gives them a vocabulary for persuasive narrative sequencing
- Reference contribution: "What Is (frustration) ↔ What Could Be (hope)" arc at 1/3 and 2/3 positions
- Project contribution: present's .pptx generation and report's structured document output
- Target: `.claude/skills/present/SKILL.md`
- Gap closed: Currently present generates delivery slides with no guidance on engagement structure

---

## Section 9 — Expansion Opportunities

**Per-skill growth scan:**

| Reference Capability | Project Equivalent? | Tier 7 Candidate |
|---|---|---|
| Logo AI generation (55 styles, BM25 search) | No — WabbleSpec has no AI image generation capability | Yes (but external Gemini API dependency) |
| CIP deliverable generation (50 types, mockups) | gateway-document covers DOCX/PDF/XLSX but not CIP mockups | Yes — Tier 7 (weeks, Gemini API) |
| HTML slide generation with Chart.js + token validation | present skill generates .pptx via gateway-document; no HTML slide path | No (Tier 4 — new capability within present module) |
| Brand token sync script (brand-guidelines.md → tokens) | No equivalent script | No (Tier 3 — new shared script) |

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| AI logo + CIP generation | `design/scripts/logo/generate.py`, `design/scripts/cip/generate.py` | WabbleSpec has no image generation capability whatsoever | Complete brand identity output from a single task (logo → CIP deliverables → pitch deck) | Gemini API key, google-genai Python package | weeks | Yes |
| HTML slide generation with token validation | `design-system/SKILL.md` slide system, `scripts/generate-slide.py`, `scripts/slide-token-validator.py` | present skill produces .pptx via gateway-document; no HTML presentation path exists | HTML presentations for in-browser delivery, Chart.js data visualization, no PowerPoint dependency | Python (no external AI API needed for HTML generation) | days | Yes |

**Gateway bundling signal:** AI logo generation + CIP deliverable generation both produce visual brand assets via Gemini API — they could be bundled as a `gateway-brand-assets` module if the Gemini API dependency is ever resolved. Flag for future session.

---

## Memory Drawers Written

- `wings/references/rooms/ui-ux-pro-max-skill-main/` — 2 drawers:
  - `banner-safe-zones-and-state-specs.json`
  - `duarte-sparkline-and-tier7.json`
