# Design Gateway — Page Structure Reference

Structural variety doctrine and macrostructure selection discipline.

## Macrostructure-First Discipline

A page's structural shape (macrostructure) is selected before any visual system is applied. Structure drives variety; visual styling is downstream. Selecting visual elements ad-hoc — font, color, spacing, hero height — without a structural frame produces default-attractor sameness regardless of how those elements differ from defaults. The shape of the page is the first decision.

## 21 Named Macrostructures

One-line index. Each represents a distinct page-shape family — not a visual style, but a structural logic.

| # | Name | Shape logic |
|---|---|---|
| 01 | Bento Grid | Asymmetric grid of card-sized modules; no single primary element |
| 02 | Long Document | Vertical prose flow; left nav or anchor bar; no hero |
| 03 | Marquee Hero | Full-width scrolling text strip as primary hero; typographic scale as the spectacle |
| 04 | Stat-Led | Large numeric or metric as the first visual unit; proof before pitch |
| 05 | Workbench | Split-pane UI with a live editable area; tool-first, not marketing-first |
| 06 | Conversational FAQ | Accordion or expand list as the dominant structure; question-answer rhythm |
| 07 | Manifesto | Dense prose statements; no cards, no features grid; type and negative space only |
| 08 | Photographic | Full-bleed or oversize photography as the structural anchor; copy is secondary |
| 09 | Quote-Led | A primary quotation as the first visual unit; attribution and source prominent |
| 10 | Specimen | A product, artifact, or sample rendered at full fidelity as the page's centre |
| 11 | Catalogue | Filterable or browsable item list as the primary experience |
| 12 | Letter | First-person prose in letter or email form; signed, personal, direct |
| 13 | Index-First | Linked index or table of contents as the primary page body |
| 14 | Narrative Workflow | Numbered steps or stages that scroll vertically; story-arc structure |
| 15 | Split Studio | Two-column persistent split; content on one side, output or media on the other |
| 16 | Feature Stack | Alternating feature rows (copy left / image right, then reversed); no grid |
| 17 | Type Specimen | Typography itself is the content and the spectacle; font showcase or editorial display |
| 18 | Portfolio Grid | Equal or varied grid of work samples; item click → detail |
| 19 | Map / Diagram | An interactive map, diagram, or canvas is the primary interface element |
| 20 | Ecosystem Index | Interconnected product tiles or integrations; hub-and-spoke visual |
| 21 | Component Playground | Interactive demo or configurator as the dominant page element |

## Six Structural Axes

Used for audit, deviation analysis, and deliberate structural differentiation. Any two macrostructures that share the same value on all six axes are structurally identical regardless of visual differences.

| Axis | Options |
|---|---|
| Section-heading placement | Left-margin / hanging / centered / bottom-aligned / overlapping / sticky / inline |
| Body composition | Single column / two-column asymmetric / multi-column justified / marginalia / asymmetric spans |
| Divider language | Hairline / ornament / negative space / color block / double rule |
| Button voice | Outlined / unstyled link / oversized solid / typographic-only / form-as-CTA |
| Image treatment | Full-bleed / tightly cropped / inline / margin-aligned / none |
| Reveal pattern | Fade-up stagger / horizontal sweep / type-unmask / number-tick / none |

## Diversification Rule

Before selecting a macrostructure for a new page build in an existing project: check the project's existing CSS for a structural stamp comment (`/* WS · structure: <macrostructure-name> */`). If one exists, the new pick must differ from the most recent stamp.

No two consecutive page builds in the same project share a macrostructure.

## Rejected Structural Fingerprints

These are the AI-default page shapes. Do not use them without explicit user brief naming them:

- Centered display heading + centered subhead + centered pill CTA + `min-height: 100vh` hero + fade-up on scroll
- Three equal columns of icon-above-heading-above-two-line-body, 24px gap, optional shadow cards
- Hero → benefits list → "Sign up" button block
- Every section gets identical scroll-triggered fade-up; page never settles
- Wordmark + 4-5 inline text links + CTA button nav, white background, 1px hairline border-bottom
- 4 link-columns footer (Product / Company / Resources / Legal) + social icon row + copyright

Any page that contains more than two of these fingerprints simultaneously ships as visually AI-generated.

## Domain to Macrostructure Decision Table

Starting trios by domain. Pick one; deviate intentionally.

| Domain | Primary | Alternate A | Alternate B |
|---|---|---|---|
| Podcast / audio | Quote-Led (09) | Manifesto (07) | Catalogue (11) |
| E-commerce | Catalogue (11) | Photographic (08) | Bento Grid (01) |
| Docs / CLI / API | Long Document (02) | Index-First (13) | Workbench (05) |
| Platform / SaaS / B2B | Feature Stack (16) | Stat-Led (04) | Split Studio (15) |
| Agency / studio | Portfolio Grid (18) | Photographic (08) | Manifesto (07) |
| Personal / portfolio | Letter (12) | Type Specimen (17) | Portfolio Grid (18) |
| Restaurant / café | Photographic (08) | Quote-Led (09) | Manifesto (07) |
| Fashion | Photographic (08) | Specimen (10) | Marquee Hero (03) |
| Fintech | Stat-Led (04) | Long Document (02) | Feature Stack (16) |
| Manifesto / campaign | Manifesto (07) | Marquee Hero (03) | Quote-Led (09) |
| Editorial / foundry | Type Specimen (17) | Long Document (02) | Catalogue (11) |
| Product launch | Specimen (10) | Bento Grid (01) | Marquee Hero (03) |
| Conference / event | Stat-Led (04) | Narrative Workflow (14) | Index-First (13) |

---

## Picking Guide

Five steps. Run them in order before writing code.

1. **Read the brief.** Note any words that strongly signal one macrostructure: "data heavy" → Stat-Led; "tell a story" → Narrative Workflow or Long Document; "a list of links" → Index-First; "many small features" → Bento Grid; "personal note" → Letter.

2. **Check the project CSS** for a `/* WS · structure: <macrostructure-name> */` stamp. If found, exclude that name from the choice set.

3. **Match brief energy to macrostructure** using the domain table above. When brief energy matches 2-4 macrostructures, pick the one most categorically distant from any past stamp in this project.

4. **State the pick** in plain text before writing code: "Macrostructure: Bento Grid." Then write the code, opening the CSS with the structural stamp.

5. **If genuinely torn**, offer the user three choices from different categories — e.g., Bento Grid + Long Document + Manifesto. Let them pick. Do not silently resolve the ambiguity.

**When the brief is vague** (no tone, no domain, no named reference), pick from macrostructures 01-10 before reaching for 11-21. The first ten cover approximately 80% of briefs and are structurally the most diverse.

---

## SaaS Page Sequence

When the macrostructure is Bento Grid, Stat-Led, Workbench, or Marquee Hero and the brief is a B2B SaaS marketing page, these sections should be present in roughly this order. None are mandatory — skipping more than two reads as incomplete:

1. **Hero** — macrostructure-specific. Two CTAs: primary action + secondary "Talk to sales".
2. **Social proof / logo wall** — 6-8 customer logos in monochrome. Real company names; never "Company A" or a placeholder grid.
3. **Features** — 3-6 feature entries; treatment varies by macrostructure (Bento Grid: inline; Stat-Led: after the supporting-stats block).
4. **Testimonials** — 2-4 quotes. Quote + name + role + company. Quote must be specific to a use case, not "We use it every day."
5. **Pricing** — 2-3 tiers. Show the actual price. "Contact sales" on every tier signals the brand does not trust the buyer.
6. **FAQ** — 5-10 questions in Conversational FAQ style. Answer like a person, not a sales document.
7. **Final CTA strip** — one button, one sentence. Not two buttons.
8. **Footer** — theme-appropriate archetype from component-archetypes.md.

This sequence is **not** a template — it is a list of what should be present. The macrostructure determines how each section looks. For non-SaaS work (Editorial, Manifesto, Letter, Long Document, Restaurant), this sequence does not apply.
