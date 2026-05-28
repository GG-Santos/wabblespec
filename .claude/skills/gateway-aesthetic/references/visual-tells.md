# Aesthetic Gateway — Visual Tells Reference

Named anti-pattern taxonomy for AI-generated web UI. Each entry: the tell name, why it reads as AI-generated, and the fix. Used by the `gateway-aesthetic` Phase B verdict and Verifier when a visual output is in scope.

Severity levels:
- **Critical** — ships as visually AI-generated; block delivery
- **Major** — reads as AI-generated to most audiences; flag for fix
- **Minor** — small taste failure; flag for awareness

---

## Critical

### Gradient headline

A heading rendered with `background-clip: text` and a gradient fill — usually purple-to-pink or blue-to-cyan.

**Why it fails.** Every LLM reaches for this. Audiences pattern-match it in under a second. It signals "generated" faster than almost any other single element.

**Fix.** Solid ink color on all headings. If the headline needs energy, use weight contrast, size contrast, or a distinctive display face — not a gradient fill.

---

### Purple-to-blue / purple-to-cyan hero background

A hero section with a background gradient from purple to blue, purple to cyan, or purple to pink — often with white centered text.

**Why it fails.** The most-recognised AI aesthetic of 2023-2025. The training distribution is saturated with it. Audiences read it as "generated" before reading a word.

**Fix.** Single anchor hue. One accent. No gradient backgrounds on heroes. If warmth is needed, tint the surface neutrals toward the anchor hue. See `references/color.md` for OKLCH palette construction.

---

### Default-font monoculture

Inter, Roboto, Open Sans, Lato, Poppins, Nunito, Montserrat, Work Sans, or DM Sans used as both display and body with no pairing face — or as the only display face on the page.

**Why it fails.** Every LLM defaults to these because they dominated the training data. A one-font page in one of these faces is indistinguishable from an unstyled template.

**Fix.** Pair a distinctive display face with a refined body face. See `references/typography.md` § Font Catalog and § Banned Font Defaults for the approved list and banned defaults.

---

### 3-equal-column feature grid

Three equal columns, each with an icon above a two-line heading above a three-line body. Usually full-width with a 24px gap. Often inside bordered or shadowed cards.

**Why it fails.** Every LLM emits this. It is the structural fingerprint of an AI-generated landing page — the single most-recognised page shape after the full-viewport centered hero.

**Fix.** Break the grid. Vary column widths. Mix card heights. Remove one card and use negative space. Move icons inline with headings rather than above. Or drop the cards entirely and use typographic rhythm. See `references/page-structure.md` for named page shapes that produce structural variety.

---

### Full-viewport centred hero

`min-height: 100vh` (or `100dvh`), everything centered, one short sentence, one big CTA button. The structural template every LLM reaches for when given a vague brief.

**Why it fails.** Audiences recognise this shape before reading any copy. It signals "AI default" in the same way a purple gradient does — through shape, not content.

**Fix.** Let the hero be the height of its content. Bias left or right. Put more than one sentence in it. Pick a macrostructure before writing code — see `references/page-structure.md`.

---

### Pure black and pure white surfaces

`#000000` background or `#ffffff` surface used as the base layer of the design.

**Why it fails.** Both read as flat and synthetic. The absence of any chromatic tint signals "unstyled default" rather than a deliberate palette choice.

**Fix.** Tint toward the anchor hue. `oklch(96% 0.012 80)` for warm off-white; `oklch(14% 0.008 250)` for deep navy-tinted dark. See `references/color.md` § OKLCH Palette Construction.

---

### Re-drawn UI chrome

A fake browser bar (URL pill + traffic-light dots), a fake phone frame (rounded rectangle + notch + speaker slit), a fake code-block window (mock title bar + close dots wrapping a `<pre>`), or fake IDE chrome — hand-built in HTML/CSS or SVG.

**Why it fails.** The user already has real chrome. Redrawing it in a page is fakery that audiences pattern-match immediately: the dots are wrong, the URL is wrong, the notch is the wrong shape. It reads as "the model invented a UI that already exists."

**Fix.** Use a real screenshot wrapped in a `<figure>` (hairline border at most). For code blocks, use a typographic frame (top rule + label + bottom rule) instead of faked window chrome. For phone mockups, use a real photograph or a vendor-supplied transparent-PNG device frame — never a CSS-drawn one.

---

### Invented metrics

A stat-led layout, comparison row, or proof bar carrying numbers the designer did not supply: "10× faster", "saves 5 hours per week", "trusted by 50,000+ teams", "99.9% uptime", "+47% conversion".

**Why it fails.** Audiences read fabricated stats as fast as they read fabricated testimonials. A page that lies on its proof bar signals "this was generated, not written." The number-shaped hole is honest; the fabricated number is slop.

**Fix.** Three options in preference order: (1) replace the number with `—` and a labelled grey block ("metric to confirm"); (2) ask the user for the real number and pause the build; (3) rebuild the section without the stat slot — a stat-led shape with no real stats is the wrong shape for this content.

---

### Emoji as primary feature icon

A feature card, value prop, step number, or pricing tier using ✨ 🚀 ⚡ 🔥 🎯 ✅ as its primary icon. Also: a sparkle emoji in a hero badge or eyebrow.

**Why it fails.** Emoji are OS-rendered typography, not an icon system. They break the page's stroke voice (an SVG line icon next to a Twemoji blob), look different on every device, and are the recognisable AI shortcut of 2024-2025.

**Fix.** Pick one icon library per project (Lucide for SaaS, Phosphor for weight variants, Heroicons for Tailwind/shadcn projects) and use it consistently. Or build a custom SVG mark. Or omit the icon entirely and lead with typography — most feature lists do not need icons.

---

### AI nav fingerprint

Wordmark hard-left, 4-5 inline text links centered or right-grouped, a CTA button hard-right, full viewport width, sticky on scroll, white background, 1px hairline border-bottom.

**Why it fails.** Genre-blind. It lands the same on a wedding photographer's portfolio, a bakery, a B2B SaaS, and a manifesto. When the nav cannot tell you what kind of site you are on, the page is templated.

**Fix.** See `references/component-archetypes.md` § Nav Archetypes. Default to NA-5 through NA-9 by genre. Reach for NA-1 only when the page has exactly 2 destinations AND the genre permits it.

---

### AI footer fingerprint

4 columns of links (Product / Company / Resources / Legal), social-icon row beneath, copyright line at the very bottom, faint 1px top-border, neutral grey background.

**Why it fails.** Standard SaaS footer, identical across thousands of pages. A bakery does not have a "Resources" column. An editorial page does not have a "Legal" column with four links. The footer should close the page, not catalogue an absent sitemap.

**Fix.** See `references/component-archetypes.md` § Footer Archetypes. Default to FA-1, FA-2, FA-4, FA-5, FA-6, FA-7, or FA-8. Reach for FA-3 only on a genuine docs root with a real sitemap — and even then, never with the social-icon row + tiny copyright tail.

---

### Aurora-blob / mesh-gradient background

Flowing organic mesh blobs in purple-to-pink-to-cyan layered behind hero text. Or: ambient blurred coloured circles drifting behind the hero with no semantic role.

**Why it fails.** The 2022-2023 generated-design default. Audiences pattern-match it in milliseconds: AI template.

**Fix.** Solid surface. Or a subtle two-stop CSS gradient plus `<feTurbulence>` grain at < 0.1 opacity on a specific element. Never mesh-animated across the whole page. Decoration must be motivated by content, not added for ambient "depth."

---

### All-caps display head with `line-height < 1.0`

A display-size element (`h1`, `h2`, hero headline, section title) that combines `text-transform: uppercase` with a `line-height` below `1.0`.

**Why it fails.** Uppercase glyphs have no descenders — their cap-tops sit at the very top of the line box. At `line-height: 0.94` the cap-tops of line N+1 visibly collide with the baseline or commas of line N when the heading wraps. Condensed display faces (Anton, Bebas Neue, Inter Tight 900) make this worse. The result is glyph collision that reads as a rendering error, not a design choice.

**Fix.** Floor for all-caps display heads is `line-height: 1.0`; recommended `1.02–1.08`. Either increase the `line-height` token for these elements, or drop `text-transform: uppercase` on the display element.

---

### Section eyebrow beside heading (tag-left / header-right)

An eyebrow, number, or mono-cap label (`01 / FEATURES`, `02 · ABOUT`, `Chapter Three`) rendered in a narrow column to the left of — or to the right of — the section heading on the same horizontal row.

**Why it fails.** The two-column tag-left / header-right section head is the single most reliable templated-editorial tell. Audiences read it as "AI reached for chapter labels" in one glance, regardless of the content quality.

**Fix.** When an eyebrow is used at all — and it is OFF by default — the heading goes **directly below it in the same column**. Vertical stack only. Any `grid-template-columns` on a wrapper containing both an eyebrow and a heading is banned (see gate CC-3 in `audit-gates.md`).

---

### Side-stripe card

A card with a thick coloured border (4-6px) on one edge — typically the left, in purple or green.

**Why it fails.** Very recognisable. Very 2018-SaaS-AI. The asymmetric thick stripe was cloned aggressively into LLM training data from early SaaS documentation sites. Audiences pattern-match it in one glance.

**Fix.** Use a hairline border all around, or no border, or a small accent square beside the heading. Never an asymmetric thick edge stripe.

---

### Lazy-loaded LCP

`loading="lazy"` on the hero image or the hero video — the element that is the Largest Contentful Paint target.

**Why it fails.** The browser defers download until the user scrolls to the element — except the user is already looking at it, so the page sits blank. Real-world data: lazy-loaded LCP images show p75 of 720ms vs 364ms for preloaded — 2× slower. It is a performance failure that also reads as an incomplete implementation.

**Fix.** `fetchpriority="high"` on the hero image. `preload="metadata"` on the hero video. Apply `loading="lazy"` only to below-the-fold media.

---

### Sound-on autoplay

A `<video>` element with `autoplay` but without `muted` — or a hero that attempts to autoplay audio.

**Why it fails.** Browsers block it anyway, but intent matters: a video element without `muted` is hostile to the audience, an accessibility failure, and an SEO penalty. It signals the build was not tested.

**Fix.** Always: `<video autoplay muted loop playsinline>`. All four attributes, always. A separate audio-toggle button only if sound is genuinely useful content.

---

## Major

### Card-in-card nesting

A bordered container with cards inside it. Or a card containing another card containing a micro-card. Visual nesting with no semantic reason.

**Fix.** Pick one containment layer. Usually the outer one is the wrong one. Remove it and let the inner cards breathe against the page surface directly.

---

### Centred everything

Headline centred, body centred, button centred, section after section of identical centered alignment.

**Fix.** Break alignment for at least two elements per section. Wide left margin, narrow right. Or the reverse. The intentional break is what communicates craft.

---

### Hover-only affordances

Hover reveals a menu, hover shows a delete button, hover triggers a tooltip containing crucial information. Touch users and keyboard users get nothing.

**Fix.** Every hover affordance has a `:focus-visible` state and is accessible via tap or click on coarse pointers. Hover is an enhancement, never the only interaction path.

---

### Mismatched icon sets

Material Icons in the navbar, Heroicons in the feature cards, Lucide in the footer, and an emoji in the hero badge. Each library has its own stroke weight and corner radius; mixing them is the icon-set tell.

**Why it fails.** Icons are typography. You would not ship a page with three different body fonts.

**Fix.** Declare one icon library at P1. All icons in the project come from that library. No mixing.

---

### Animate-on-scroll on every section

Every section fades in on IntersectionObserver entry. Every list staggers. The page never settles.

**Fix.** One orchestrated entrance sequence on first load. After that, content is just there. An IntersectionObserver reveal applied to every `<section>` class-wide is the motion equivalent of a 3-column feature grid.

---

### Shadow-glow on dark surfaces

A card on a dark background with a `box-shadow` that leaves a soft coloured halo around it.

**Fix.** On dark surfaces, use elevation via lightness (brighter surface = higher elevation), not shadow colour. If a shadow is needed, keep it tight and dark — no chroma in the shadow value.

---

### Icon-tile feature card

Rounded rectangle, coloured icon square at top-left, heading below, two lines of copy below that, optional "Learn more →" link. The universal AI card template.

**Fix.** If feature cards are needed, break the template. Different sizes. Different alignments. Icons inline with headings rather than above. Or drop the icon entirely and lead with a typographic numeral or a bold subheading.

---

### Glassmorphism without purpose

Frosted-glass panels everywhere — usually layered over a gradient that should not exist either.

**Fix.** Glassmorphism communicates depth when an overlay sits over content the user can see through it. As decoration it adds visual noise. Cut it unless the glass is over real content that the blur meaningfully obscures.

---

### Tabular data without tabular-nums

A list of prices, dates, or metrics where numbers do not align vertically because the font uses proportional figures.

**Fix.** `font-variant-numeric: tabular-nums` on any container displaying columns of numbers.

---

### Bouncy / elastic easings on UI state

Buttons that bounce in. Icons that wobble on hover. `cubic-bezier(0.34, 1.56, ...)` on modal open.

**Fix.** Exponential ease-out for UI state transitions. Reserve overshoot easings for genuine physical interactions (drag-and-drop release). See `motion.md` § Three Named Easings.

---

### `transition-all` or `transition-property: all`

Every CSS property animates, including properties that should change instantly (visibility, display, z-index, focus rings).

**Fix.** Specify the properties. `transition: background-color var(--dur-short) var(--ease-out), transform 100ms var(--ease-out)`. `transition-all` is a performance tell and a correctness risk.

---

### Universal `hover:scale-105`

Every card lifts to 105% scale on hover, with no shadow change, no easing specified, no purpose.

**Fix.** Pick one signal per interactive element. A 1px translate, a colour shift, or an underline thickening — not all three, and not the same lift on every unrelated element. Scale transforms on cards often cause layout jank on repaint.

---

### Focus ring that animates in

The focus ring fades in over 200ms — keyboard users have no visible indicator at the start of the transition.

**Fix.** Focus rings appear instantly. Always. Do not transition `outline` or `box-shadow` when an element gains focus. The ring's purpose is immediate orientation — a 200ms fade defeats that purpose.

---

### Celebratory success toast for visible effects

A toast notification reading "Done!" or "Saved!" for an action whose effect the user can already see (e.g., a list item they just deleted is gone from the list).

**Fix.** Silent success for actions whose effect is visible. Reserve toasts for failures, async actions whose effect is not immediately visible, and explicit confirmations the user needs to retain. A toast for a visible delete is noise.

---

### Eyebrow on every section

A section eyebrow (label or chapter number: `01 / FEATURES`, `02 · ABOUT`) above every section heading, applied as decoration rather than genuine chapter structure.

**Why it fails.** Eyebrows are ordinal devices that lose meaning when applied universally. When every section is labelled `0N / NAME`, none of them are chaptered -- the page reads as a list of AI-formatted sections. The audience pattern-matches it as "LLM reached for editorial gravity it did not earn."

**Fix.** Eyebrows are default OFF. Use them only when (a) the user explicitly requested chapter or step numbering, or (b) the content is genuinely ordinal (steps that must be done in sequence). Cap at 1-2 eyebrows per page. See `references/component-archetypes.md` § Eyebrow Discipline.

---

### Wrap-to-two-lines clickable text

A link, button, or CTA that wraps to a second line at normal viewport sizes -- particularly visible in nav links, card CTAs, or inline call-to-action phrases.

**Why it fails.** Wrapped interactive text creates an ambiguous tap/click target. The hit area is split across two lines with unpredictable whitespace between. It reads as text that was never tested in a browser.

**Fix.** `white-space: nowrap` on nav links and short CTAs. Keep button labels under 4 words. For inline CTAs, reduce the surrounding prose rather than letting the link fragment.

---

## Microinteraction tells

Microinteraction patterns that signal generated UI. Each is recognisable in isolation; appearing together they compound the AI signal.

---

### Animated hover gradient

A card, button, or surface where the background shifts hue, lightness, or gradient angle continuously on cursor-enter -- a transition that never resolves to a resting state.

**Fix.** Hover state is an instant switch: one token value to another. `transition: background-color 150ms var(--ease-out)` moving between two static tokens. No gradient animation on hover. No continuously shifting hue.

---

### Cursor follower dot

A small circle or glowing orb that trails the user's cursor, implemented in JavaScript with `mousemove`.

**Why it fails.** Custom cursors break on touch devices. Cursor-follower scripts run on every `mousemove` event, burning CPU on the main thread. The pattern is immediately recognisable as a 2022-design-portfolio tell.

**Fix.** Do not replace or augment the native cursor. If a hover highlight is needed for interactive zones, implement it as a CSS `:hover` state on the element, not a cursor replacement.

---

### Confirmation dialog for a reversible action

A modal dialog ("Are you sure?") appearing before a delete, archive, or move action that can be immediately undone.

**Why it fails.** It interrupts the user's workflow to confirm an action they can already undo. It signals the UI does not trust its own undo architecture. The dialog is friction, not safety.

**Fix.** For reversible actions: execute immediately, offer an inline undo for 5-8 seconds (toast or inline banner), then commit. Reserve confirmation dialogs for irreversible actions with significant consequences (permanent deletion, cancellation of a paid subscription).

---

### Toast that shifts layout

A toast notification that pushes page content down when it appears -- inserted into document flow rather than positioned fixed.

**Fix.** Toasts are always `position: fixed`. They do not participate in document flow. They appear in a corner, overlap content, and dismiss without causing reflow. A toast that shifts layout is a positioning failure.

---

### Spinner that flashes

A loading spinner that appears for under 100ms before data arrives -- visible as a brief flash that vanishes immediately.

**Fix.** Delay the spinner: show it only if the operation takes longer than 200ms. Below that threshold, a blank state is less disorienting than a flash. Use `animation-delay` or a 200ms guard before mounting the spinner element.

---

## Minor

### Straight quotes in rendered text

`"Hello"` and `'word'` in visible UI text.

**Fix.** Curly quotes: `"Hello"`, `'word'`. This is a detail that reads immediately as un-proofed when absent.

---

### Double-hyphen dashes in body copy

`--` where an em-dash belongs.

**Fix.** `—` (U+2014). Never `--`.

---

### Three periods instead of ellipsis

`...` in rendered text.

**Fix.** `…` (U+2026).

---

### Placeholder names

"Jane Doe", "John Smith", "Example User", "Test Company" in demo content.

**Fix.** Plausible, audience-specific placeholder names: "Maya Okonkwo", "Sam Tan", "Elena Ruiz". Or domain-specific: "Maple Weekly", "Ridgeline Inventory" — not abstract startup bingo.

---

### `z-index: 9999`

Arbitrary large z-values with no named scale, creating an unmanageable z-index war.

**Fix.** Declare a six-level named z-index scale as tokens: `--z-base`, `--z-dropdown`, `--z-sticky`, `--z-sticky-nav`, `--z-overlay`, `--z-modal`, `--z-toast`. Use names, not magic numbers.

---

### `width: 100vw` on any element

Breaks on scrollbar-visible desktops — the scrollbar width is included in `100vw` but not in the layout width, causing horizontal overflow.

**Fix.** `width: 100%` with container padding for most elements. `100vw` is correct only for viewport-covering overlays with `position: fixed`.

---

### Every section padded identically

Top padding, bottom padding, horizontal padding equal across every section of the page.

**Fix.** Vary. Tighten one section, expand another. Rhythm comes from contrast, not uniformity.

---

### Startup-cliché product names in demo content

Placeholder product or company names that read as AI-generated bingo: Acme, Nexus, Pulse, Seamless, Supercharge, Elevate, Synergy, Catalyst, Momentum, Apex, Pinnacle.

**Fix.** Use domain-specific placeholder names that match the brief's industry. A project management tool's demo content references "Ridgeline Q4 Roadmap", not "Acme Project 1". A restaurant booking app shows "The Larder, Tuesday 7pm", not "Test Booking".

---

## How the audit verb should report

For each finding:

```
[severity] Tell name — file:line
  why it is a tell (one line)
  → fix (one line)
```

Then:

```
Summary — N critical · M major · K minor
Verdict — [ships as visually AI-generated | reads as AI-generated | close, fix the minors]
```
