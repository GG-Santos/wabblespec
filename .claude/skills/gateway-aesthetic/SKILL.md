---
name: gateway-aesthetic
description: Aesthetic capability gateway. Visual design standards for any project with a visual surface — brand identity, color system, typography, motion, and design token policy. Applies to Web, Mobile, Desktop, Game, Extension/Plugin targets. Non-visual targets (API/Service, CLI, IoT, Library, Data/Pipeline) do not activate unless a visual component is declared in scope.
---

# Gateway: Aesthetic

Cross-cutting visual design standards layer. Activates on top of (not instead of) the active platform package. Owns what things look like — brand assets, color system, typography, motion, and design token policy. Design gateway owns how things work. Both apply to visual targets; neither replaces the other.

## What this skill does

| Concern | Covered by L3 platform | Covered by L4 Aesthetic gateway |
|---|---|---|
| Platform-specific render/layout patterns | Yes (L3) | — |
| Brand asset source of truth | No L3 module | Yes |
| Semantic color token system | No L3 module | Yes |
| 3-tier accent token structure (full/bg/border per accent) | No L3 module | Yes |
| WCAG AA contrast minimums | No L3 module | Yes |
| Dark mode scope declaration | No L3 module | Yes |
| Modular type scale | No L3 module | Yes |
| Font loading (font-display, subsetting) | No L3 module | Yes |
| Reduced motion (prefers-reduced-motion) | No L3 module | Yes |
| Motion duration and easing tokens | No L3 module | Yes |
| Design token policy (all visual values as tokens) | No L3 module | Yes |
| Shadow philosophy declaration (flat vs. elevated stance) | No L3 module | Yes |
| Anti-monoculture intentionality check | No L3 module | Yes |
| Background layer strategy declaration | No L3 module | Yes |
| Named visual style declaration (mood + motion energy) | No L3 module | Yes |

## When to use

- Visual build target: Web, Mobile, Desktop, Game, Extension/Plugin (always)
- P3 Technical Spec for any target with declared visual surface
- Explicit `/aesthetic` command

Note: Homowabian ultra mode suppressed for Aesthetic content output — prose context required for visual design decisions.

## Activation sequence

### Phase A (Specify time — knowledge injection)

```
1. Confirm platform package (L3) has activated and written its receipt
2. Load references/ directory into Specify context:
   - references/color.md (brand palette, contrast requirements, dark mode)
   - references/typography.md (type system, hierarchy, font loading)
   - references/motion.md (animation principles, timing, prefers-reduced-motion)
3. Write gateway-spec-receipt (Phase A)
```

### Phase B (pre-Executor — verdict)

```
1. Load brand.md
2. Load color.md
3. Load typography.md
4. Load motion.md
5. Load design-tokens.md
6. Register audit-gates.md with Verifier
7. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

## Reference Routing

| Situation | Reference |
|---|---|
| aesthetic receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type gateway-spec` / `gateway-verdict` (two-phase)` |

## Output contract

- Brand asset compliance check
- Color token system audit (semantic token hierarchy, contrast pass, 3-tier accent structure)
- Typography compliance check (scale, loading, hierarchy)
- Motion compliance check (reduced motion, tokens)
- Design token policy audit (no raw values in component code)
- Anti-monoculture intentionality check (lazy-default patterns flagged with rationale required)
- Shadow philosophy declaration (PASS = stance declared; BLOCK = undeclared)
- Visual style declaration (named style or custom derivation with mood + motion energy)
- Background layer strategy declaration
- Gateway activation receipt with all gate results

## Rule Categories by Priority

| Priority | Category | Impact | Gate condition |
|---|---|---|---|
| 1 | Generated code token compliance | HIGH | No raw hex, rgb(), or pixel values in generated code |
| 2 | Anti-monoculture intentionality | HIGH | Flagged patterns documented with per-project rationale |
| 3 | Named visual style declaration | HIGH | Named style in brand.md covering color, type, motion energy, atmosphere |
| 4 | Background layer strategy | MEDIUM-HIGH | Layer type declared (or "none" explicit) |
| 5 | Shadow philosophy declaration | MEDIUM | Flat / elevated / mixed stance declared |
| 6 | 3-tier accent token structure | MEDIUM | full + bg + border tiers per accent color |
| 7 | Banner safe zones | MEDIUM | Critical content in central 70-80%; CTA position and size |
| 8 | Interactive state specification | MEDIUM | State priority order and transition durations |

## Phase B audit gates

### 3-tier accent token structure

Every declared accent color must have three tiers: full value (`--accent-green`), light/background tier (`--accent-green-light`), border tier (`--accent-green-border`). A single hex accent with no bg/border tiers fails this gate. Declare all three or mark the accent as single-tier with a rationale.

### Shadow philosophy declaration

The project must declare an explicit shadow stance before Phase B closes. Accepted stances: `flat` (borders over shadows — `1px solid var(--border)` instead of box-shadow), `elevated` (shadow system with defined levels), `mixed` (declared rule for when each applies). An undeclared stance fails this gate.

### Anti-monoculture intentionality check

Before passing Phase B, verify that the visual design does not use any of these patterns without a documented rationale for why it serves this specific content:

- Gradient text (`background-clip: text` on a gradient)
- Left-edge accent stripes on cards or callouts
- Cyan-on-dark, pure purple-to-blue gradients, or neon accents as the primary palette
- Pure `#000` / `#fff` without tinting toward the accent hue
- Identical same-size card grids as the primary layout pattern
- Everything centered with equal visual weight and no declared dominant element

Each item is not banned — it is a flag requiring a one-line rationale. "Gradient text: brand guide specifies it" passes. No rationale fails.

### Background layer strategy

Every visual surface must declare a persistent decorative layer strategy. Minimum: declare at least one element type (radial glows, ghost text, accent lines, grain/noise, geometric shapes, thematic decoratives). "No background layer" is a valid declaration but must be explicit. Undeclared fails.

### Named visual style

The project's visual identity must be declared as a named style or a custom derivation. The declaration lives in `brand.md` and must cover: color stance, typography stance, motion energy level (high / moderate / calm), and primary atmosphere elements. A project with a color palette but no style rationale fails this gate.

### Generated code token compliance

Generated code must not contain raw hex values (`#RRGGBB`), raw `rgb()`/`rgba()`, or raw pixel/rem values for visual properties. Every visual value must reference a design token via `var(--token-name)`. Scan generated CSS, inline styles, and component code for hardcoded values before Phase B closes. Any instance → BLOCK (design token policy violation).

This enforces the single source of truth: if a visual value is not in a token, it cannot be maintained, themed, or audited.

## Banner Safe Zones

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

## Interactive State Specification

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

Never rely on color alone to communicate state — use icons, text, or patterns alongside color changes.

## Image Prompt Vocabulary

When generating photorealistic visual assets (photography-style hero images, product shots, portraits, lifestyle photos), use specific professional photography vocabulary. These six categories produce measurably better output than generic descriptors.

| Category | Examples | Effect |
|---|---|---|
| Camera / lens specs | "85mm f/2.8 lens", "50mm prime", "shallow depth of field at f/1.8" | Controls perspective compression and background separation |
| Lighting architecture | "three-point studio lighting with soft key light from left", "subtle fill light", "rim light for hair separation", "visible catchlights in eyes" | Controls light quality and output professionalism |
| Film stock / era aesthetics | "Kodak Portra 400 color tones", "Fujifilm Pro 400H tones", "early-2000s digital camera look", "subtle film grain" | Sets color science and texture character |
| Texture and material details | "natural skin texture with visible pores", "fine wool texture visible", "silk sheen and drape" | Forces detail rendering rather than smooth interpolation |
| Facial consistency phrases | "Keep the facial features exactly consistent", "do not alter the face" | Required when facial identity must be preserved across variations |
| Composition and framing | "chest-up framing", "3/4 body shot", "rule of thirds placement", "mirror selfie angle" | Controls shot composition and subject positioning |

Stack multiple categories for compound effect. Example for a corporate headshot: `"85mm f/2.8 lens, three-point studio lighting with soft key light from left, subtle fill light, rim light for hair separation, neutral gray backdrop, visible catchlights, chest-up framing, natural skin texture with visible pores"`.

## Files loaded by this module

```
modules/l4/aesthetic/
  brand.md
  color.md
  typography.md
  motion.md
  design-tokens.md
  audit-gates.md
```
