# Design Gateway — Component Archetypes Reference

Named patterns for nav, footer, and hero components. Genre routing tables and section-head discipline.

## Nav Archetypes

| ID | Name | Shape | Genre fit |
|---|---|---|---|
| NA-1 | Wordmark + minimal links | Wordmark left; 2 links maximum; no CTA button | Minimal portfolio, single-product, art site |
| NA-2 | Floating chip | Small centered pill, rounded, above content | App product page, modern consumer |
| NA-3 | Side-rail | Vertical nav on left edge; persistent or collapsible | Workbench, dashboard, long-document |
| NA-4 | Hidden / keyboard shortcut | No visible nav; `Cmd+K` or `?` reveals | Developer tool, internal tool, terminal aesthetic |
| NA-5 | Floating pill | Centered horizontal pill, minimal links, above fold | Modern SaaS, atmospheric tool |
| NA-6 | Newspaper masthead | Full-width editorial bar; publication name large; horizontal rule below | Editorial, journalism, publishing |
| NA-7 | Brutal slab | Heavy background, high-contrast text, full-width | Campaign, brutalist, poster-aesthetic |
| NA-8 | Terminal command | Monospace, `>` prompt, command-style aesthetics | CLI tool, developer-first, hacker |
| NA-9 | Edge-aligned minimal | Wordmark at one edge; one link or nothing at the other; vast empty space | Studio, fashion, luxury, gallery |
| NA-10 | Floating + scroll-morph | Pill nav that changes size, opacity, or shape as user scrolls | Atmospheric SaaS, interactive product |

### Default routing by genre

| Genre | Default | Acceptable alternate |
|---|---|---|
| Editorial / publishing | NA-6 | NA-9 |
| Modern SaaS / product | NA-5 | NA-9 |
| Atmospheric / AI tool | NA-5 | NA-10 |
| Consumer / playful | NA-7 | NA-5 |
| Developer tool / CLI | NA-8 | NA-4 |
| Agency / studio | NA-9 | NA-1 |
| Dashboard / workbench | NA-3 | NA-4 |
| Personal / portfolio | NA-1 | NA-9 |

### AI Nav Fingerprint (do not reach for by default)

Wordmark hard-left, 4-5 inline text links centered or right-grouped, a CTA button hard-right, full viewport width, sticky on scroll, white background, 1px hairline border-bottom. This is NA-1 in its bloated form.

Acceptable only when: (1) the page has exactly 2 destinations AND (2) the genre explicitly permits a minimal nav. For any other case, use NA-5 through NA-9.

---

## Footer Archetypes

| ID | Name | Shape | Genre fit |
|---|---|---|---|
| FA-1 | Mast-headed | Large wordmark or logotype above; minimal links below | Studio, brand, luxury |
| FA-2 | Inline single line | Wordmark + copyright + 2-3 links on one horizontal row | Small product, personal, minimal |
| FA-3 | Index columns | 4 columns of links; use only on genuine hub or docs root | Docs root, enterprise, hub |
| FA-4 | Dense colophon | Typographic, editorial style; publication credit; print reference | Editorial, journalism, publishing |
| FA-5 | Statement | Full-width closing statement + one link | Campaign, manifesto, brand |
| FA-6 | Letter close | Signed closing; personal, founder-voice, direct | Personal, letter-shaped pages |
| FA-7 | Newsletter-first | Email capture as the dominant element; minimal links below | Editorial, newsletter product |
| FA-8 | Marquee scroll | Scrolling text strip; brand name or tagline repeated | Atmospheric, fashion, campaign |

### Default routing by genre

| Genre | Default | Acceptable alternate |
|---|---|---|
| Editorial / newsletter | FA-7 | FA-4 |
| Studio / brand | FA-1 | FA-5 |
| SaaS / product | FA-2 | FA-7 |
| Personal / letter | FA-6 | FA-2 |
| Campaign / manifesto | FA-5 | FA-8 |
| Docs / hub | FA-3 | FA-2 |
| Fashion / atmospheric | FA-8 | FA-1 |

### AI Footer Fingerprint (do not reach for by default)

FA-3 with exactly four link columns (Product / Company / Resources / Legal) + social icon row beneath + copyright line + faint 1px top border + neutral grey background. This ships as visually AI-generated on any page that is not a genuine documentation hub with a real sitemap.

Acceptable only when: (1) the page is a genuine docs root or hub AND (2) there is an actual sitemap populating the columns. For all other cases, use FA-1, FA-2, FA-4, FA-5, FA-6, FA-7, or FA-8.

---

## Hero Archetypes

Reference only — structural choice, not a component prescription.

| ID | Name | Shape |
|---|---|---|
| H1 | Marquee | Large scrolling text strip as the hero statement |
| H2 | Split diptych | Two-column split: copy left / visual right (or reversed) |
| H3 | Quote-led | A primary quotation as the first visual unit |
| H4 | Stat-led | Large metric or number as the opening statement |
| H5 | Letter | First-person prose as the hero; no image |
| H6 | Photographic fold | Full-bleed or edge-to-edge photograph as the fold |
| H7 | Demo video clipped | Product video clipped at the viewport edge; continuation implied |
| H8 | Mockup split | Product mockup in a browser-like or device frame split from copy |
| H9 | Illustration centrepiece | Custom illustration as the hero; copy secondary |

The AI default hero (not listed above) is: `min-height: 100vh`, everything centered, one short headline, one subhead, one CTA button, fade-up on load. This shape is recognisable before any copy is read. Do not use it.

---

## Eyebrow Discipline

**Eyebrows are default OFF.**

An eyebrow (uppercase mono-cap label, section number, chapter tag: `01 / FEATURES`, `02 · ABOUT`, `— INSTALL`) is an ordinal device, not a stylistic flourish. Used as decoration it erases the hierarchy it was meant to create: when every section is "chaptered," none of them are. The audience reads it as AI reaching for editorial gravity it did not earn.

**Conditions for use:**
- (a) The user explicitly requested chapter numbering, step numbering, or section labels in the brief, OR
- (b) The macrostructure is Long Document, Manifesto, or a numbered Catalogue AND the content is genuinely ordinal — steps that must be done in sequence, chapters that build on each other.

Even when conditions are met: cap at 1-2 eyebrows per page. A page with 6 sections, each labelled `0N / NAME`, is a list of labelled lists — not a chaptered document.

**This rule is not bypassable by parity instructions.** If the user asks to match or mirror a prior build that contains eyebrows, and that build pre-dates this rule, the new build must drop the eyebrows and flatten the section heads to single column — even if the user says "keep parity." Reference builds often pre-date these rules; the rules are authoritative. Silently fix the inherited pattern; do not perpetuate it.

---

## Section-Head Discipline

When a section wrapper contains both an eyebrow, label, or number AND a heading, the wrapper resolves to single-column layout. The heading goes directly below the eyebrow in the same column.

**Banned:** Any `grid-template-columns` on a wrapper that contains both an eyebrow and a heading. This includes:
- `grid-template-columns: auto 1fr`
- `grid-template-columns: 1fr 2fr`
- `grid-template-columns: 200px 1fr`
- `display: flex; justify-content: space-between` on the same wrapper

**Why.** The two-column tag-left / header-right section head is the single most reliable templated-editorial tell. Audiences pattern-match it immediately as "AI chapter labels" — regardless of how strong the surrounding content is.

**Correct pattern:**

```html
<div class="section-head">  <!-- single column; no grid-template-columns -->
  <span class="eyebrow">01 / Features</span>
  <h2>What you can build</h2>
</div>
```

**Banned pattern:**

```html
<div class="section-head" style="display:grid; grid-template-columns: auto 1fr">
  <span class="eyebrow">01 / Features</span>
  <h2>What you can build</h2>
</div>
```

This rule is enforced by gate CC-3 in audit-gates.md.
