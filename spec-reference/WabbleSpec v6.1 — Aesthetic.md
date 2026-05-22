# WabbleSpec v6.1 — Aesthetic

**Gateway:** Aesthetic
**Layer:** L4 Capability
**Tier:** 1 — CRITICAL ROUTING
**Document scope:** Aesthetic gateway — visual design, brand identity, design tokens, color, typography, motion

---

## Overview

The Aesthetic gateway owns visual design standards: brand identity, color systems, typography, motion, and design token policy. It applies to any build target with a visual surface — Web, Mobile, Desktop, Game, Extension/Plugin. Non-visual targets (API/Service, CLI, IoT, Library/Package, Data/Pipeline) do not activate Aesthetic unless a visual component is declared in scope.

Aesthetic and Design are separate gateways with different activation points. Aesthetic owns the visual language (what things look like). Design owns UX and interaction patterns (how things work). Both apply to visual targets.

**In scope:**
- Brand assets (logo, color palette, source of truth)
- Color system (semantic tokens, contrast, dark mode)
- Typography (type scale, font loading, hierarchy)
- Motion (motion principles, reduced motion, duration tokens)
- Design token policy (all visual values as tokens)

**Applies to:** Web, Mobile, Desktop, Game, Extension/Plugin build targets.

---

## Gateway Structure

```
.wabblespec/gateways/aesthetic/
  SKILL.md
  skill-rules.json
  references/
    brand.md
    color.md
    typography.md
    motion.md
  rules/
    design-token-policy.md
  evaluations/
  schemas/
    receipt.schema.json
```

---

## Activation

`skill-rules.json` triggers Aesthetic gateway on:
- Visual-facing build target (Web, Mobile, Desktop, Game, Extension/Plugin)
- P3 Technical Spec for visual targets — style system review
- Explicit `/aesthetic` command

Note: Homowabian ultra mode is suppressed for Aesthetic content output — prose context is needed to communicate visual design decisions accurately.

---

## Brand

**Reference:** `references/brand.md`

### Brand Asset Source of Truth

Brand assets declared in spec at P1:
- Logo: source file format and location
- Wordmark: approved variants (horizontal, stacked, icon-only)
- Color palette: primary brand colors with hex/RGB/HSL values
- Source of truth: design tool (Figma, Sketch) or committed asset directory

No brand assets embedded in code as inline values. All brand colors become design tokens.

### Brand Voice Consistency

Brand voice declared in P1 Design Document and referenced by Expression layer. Aesthetic enforces visual brand consistency; Expression layer (Homowabian) enforces voice consistency. They are coordinated — neither overrides the other.

### Asset Usage Rules

- Approved formats declared (SVG for web, PDF/EPS for print, PNG with declared minimum size)
- Minimum size declared per logo variant (below minimum = use alternate variant)
- Clear space: declared multiplier of the logo's X-height or declared unit
- Prohibited treatments: listed explicitly (no stretching, no recoloring, no drop shadows)

---

## Color

**Reference:** `references/color.md`

### Color System Architecture

All colors expressed as semantic tokens — never raw hex values in component code.

Token hierarchy:

```
Primitive tokens (raw values):
  --color-blue-500: #3B82F6

Semantic tokens (meaning-bearing):
  --color-action-primary: var(--color-blue-500)
  --color-text-default: var(--color-neutral-900)

Component tokens (component-scoped):
  --button-background: var(--color-action-primary)
```

Components consume semantic tokens. Semantic tokens reference primitive tokens. Primitive tokens hold raw values. No component references a primitive token directly.

### Contrast Requirements

Non-negotiable minimums — cannot be waived by project decision:

| Context | Minimum ratio | WCAG level |
|---|---|---|
| Normal text (< 18pt) | 4.5:1 | AA |
| Large text (>= 18pt or 14pt bold) | 3:1 | AA |
| UI components and graphical objects | 3:1 | AA |
| Decorative elements | None (not interactive, not informational) | N/A |

AAA (7:1 for normal text, 4.5:1 for large) declared when accessibility is a stated requirement beyond baseline.

### Dark Mode

Scope declared in spec at P1:
- `yes`: dark mode implemented — semantic token system required (primitives can be reassigned per theme)
- `no`: light mode only — explicitly declared
- `auto`: respects `prefers-color-scheme` — semantic token system required

No partial dark mode — either in scope or out of scope. Partially implemented dark mode is not a delivery state.

### Brand vs. Semantic Color Separation

Brand colors (defined by brand guidelines) are primitives. Semantic colors (defined by function) reference brand primitives. Components never hardcode brand colors — they reference semantic tokens.

---

## Typography

**Reference:** `references/typography.md`

### Type Scale

Modular scale declared — not ad hoc font sizes. A modular scale means each size is derived by multiplying or dividing by a consistent ratio (e.g., 1.25 major third, 1.333 perfect fourth).

Type scale declared in spec as tokens:

```
--font-size-xs:   0.75rem
--font-size-sm:   0.875rem
--font-size-base: 1rem
--font-size-lg:   1.125rem
--font-size-xl:   1.25rem
--font-size-2xl:  1.5rem
--font-size-3xl:  1.875rem
--font-size-4xl:  2.25rem
```

No font-size values in component code outside this token set.

### Font Loading

- Variable fonts preferred when available (one file, multiple weights/widths)
- `font-display: swap` required — no invisible text during font load
- Subsetting: required when font file exceeds declared size budget
- System font stack fallback: declared for every custom font

### Type Hierarchy

- H1–H6 used semantically — heading level reflects document structure, not visual size
- Visual size controlled by token; semantic level controlled by HTML element
- No `<h3>` styled to look like an `<h1>` — if visual size is needed, use CSS classes on the correct semantic element

---

## Motion

**Reference:** `references/motion.md`

### Motion Principles

Two categories:

**Purposeful motion** — communicates state change, relationship, or action outcome. Examples: element entering/leaving, state transition, loading progress.

**Decorative motion** — visual enhancement without functional communication. Requires justification if included — not prohibited, but must earn its place.

### Reduced Motion (non-negotiable)

`prefers-reduced-motion: reduce` respected for all motion. No exceptions. Implementation:

```css
@media (prefers-reduced-motion: reduce) {
  /* all transitions/animations to 0ms or instant */
}
```

Where motion communicates state (loading indicator, progress), provide a non-motion alternative (text status, static indicator).

### Duration Tokens

```
--duration-instant:  0ms
--duration-fast:     150ms
--duration-normal:   250ms
--duration-slow:     350ms
--duration-slower:   500ms
```

UI transitions: `--duration-fast` to `--duration-normal` (150ms–250ms). Page transitions: `--duration-normal` to `--duration-slow`. No inline duration values — token references only.

### Easing

Declared easing tokens — not inline cubic-bezier values in component code:

```
--easing-standard:   cubic-bezier(0.4, 0, 0.2, 1)
--easing-enter:      cubic-bezier(0, 0, 0.2, 1)
--easing-exit:       cubic-bezier(0.4, 0, 1, 1)
--easing-linear:     linear
```

---

## Design Token Policy

**Reference:** `rules/design-token-policy.md`

All visual values declared as design tokens:

| Value type | Token required |
|---|---|
| Color | Yes — semantic token required in component code |
| Spacing | Yes — spacing scale tokens |
| Typography (size, weight, line-height, family) | Yes — type tokens |
| Border radius | Yes — radius tokens |
| Shadow | Yes — shadow tokens |
| Duration (animation) | Yes — duration tokens |
| Easing | Yes — easing tokens |

**Token format:** CSS custom properties for Web and Desktop (CSS-in-JS tokens resolve to CSS custom properties). Native design tokens for Mobile (React Native StyleSheet values, SwiftUI tokens, Compose tokens). Platform-appropriate format declared in spec.

**No raw values in component code.** Audit: any color, spacing, or other visual value that is not a token reference is a policy violation. Polish Pass 3 (structural consistency) catches token policy violations in documentation; code review catches them in product code.

---

## Integration Points

| Module | Relationship |
|---|---|
| Apply | Apply reads Aesthetic gateway for routing during visual execution |
| Verifier | Verifier Review mode checks design token policy compliance, contrast audit |
| Design gateway | Design consumes Aesthetic tokens in component system; they are separate gateways with coordinated activation |
| Experience gateway | Experience uses Aesthetic brand and color standards in accessibility testing |
| Platform packages (L3) | Platform determines token format (CSS custom properties vs. native tokens) |
| Polish (L6) | Polish Pass 4 checks canonical entity names against EntityGraph — Aesthetic token names are canonical entities |

---

## Verification Mode

**Review** — design token system present, contrast ratios pass WCAG AA, reduced motion handled, dark mode scope declared, brand assets referenced correctly.

---

## Receipt Extension Fields

```json
{
  "design_tokens_present": true,
  "contrast_audit_passed": true,
  "reduced_motion_handled": true,
  "dark_mode_scope": "yes|no|auto"
}
```

---

## Cross-References

- Design gateway (UX, interaction, component system): `WabbleSpec v6.1 — Design.md`
- Experience gateway (accessibility testing, user research): `WabbleSpec v6.1 — Experience.md`
- L3 Platform packages (token format per target): `WabbleSpec v6.1 — Platform.md`
- Verification modes: `WabbleSpec v6.1 — Core.md` § Verification Modes
