# Gateway Aesthetic — Design Token Policy

Rules enforced by gateway-aesthetic Phase B verdict. Applies to any visual target using a component library or design system. Violations produce FLAG or BLOCK verdicts.

---

## Rule T1: All Visual Values as Tokens

**Requirement:** Every visual value in component code must reference a design token. Raw values are only permitted in the token definition file itself.

| Value type | Must be tokenized |
|---|---|
| Colors | Yes (see visual-standards-policy.md Rule V2) |
| Font size | Yes |
| Font weight | Yes |
| Line height | Yes |
| Letter spacing | Yes |
| Spacing (margin, padding, gap) | Yes |
| Border radius | Yes |
| Border width and style | Yes |
| Shadow | Yes |
| Z-index | Yes |
| Transition duration and easing | Yes |

**Failure modes:**
- Any of the above value types hardcoded in component files outside the token definition = BLOCK
- Spacing values expressed as px without token reference (e.g., `margin: 12px` in component CSS) = BLOCK
- Z-index values scattered across component files without a declared z-index scale = FLAG

---

## Rule T2: Modular Type Scale

**Requirement:** All typography must use a modular scale declared in the design token system.

**Required type scale properties:**

| Property | Requirement |
|---|---|
| Scale ratio | Declared (common: 1.25 Major Third, 1.333 Perfect Fourth, 1.5 Perfect Fifth) |
| Named scale steps | At minimum: xs, sm, base, lg, xl, 2xl (exact names may vary; must be declared) |
| Base font size | Declared as a root em value (typically `16px` = `1rem`) |
| Font families | Maximum 2 distinct font families declared in tokens; additional requires justification |

**Failure modes:**
- Font sizes not on the declared type scale = FLAG
- More than 2 distinct font families without written justification = FLAG
- Base font size set in px on the `<html>` or `<body>` element overriding user browser preferences = FLAG (use `rem`; user zoom preference must be respected)

---

## Rule T3: Font Loading Requirements

**Requirement:** Custom fonts must be loaded with declared performance and accessibility considerations.

| Requirement | Details |
|---|---|
| `font-display` | Must be declared on every `@font-face` rule; `swap` or `optional` preferred for body text |
| Subsetting | Production font files must be subset to the character sets actually used; full Unicode font files not permitted without justification |
| Fallback stack | Every font declaration includes a system font fallback stack |
| Font format | WOFF2 required for production; WOFF as fallback; TTF/OTF not shipped directly to browser |

**Failure modes:**
- `@font-face` without `font-display` = FLAG
- Full Unicode font file shipped to browser without subsetting = FLAG
- No system fallback stack declared = FLAG
- Custom fonts loaded via third-party CDN without declared SRI hash = FLAG

---

## Rule T4: Motion and Animation Standards

**Requirement:** All animation and transition values must use tokens, and motion must respect user preferences.

| Requirement | Details |
|---|---|
| Duration tokens | All transition durations reference a duration token (e.g., `--duration-fast: 150ms`, `--duration-moderate: 300ms`) |
| Easing tokens | All easing functions reference an easing token (e.g., `--ease-standard: cubic-bezier(0.4, 0, 0.2, 1)`) |
| prefers-reduced-motion | `@media (prefers-reduced-motion: reduce)` block present; all non-essential animation disabled or reduced to instant |
| Essential motion only | Animations that convey information (loading spinner, progress bar) are not removed under reduced-motion; they are simplified |

**Failure modes:**
- Transition `duration` hardcoded in component CSS (not a token reference) = FLAG
- `prefers-reduced-motion` not implemented for any animated component = BLOCK
- Decorative animation continues at full speed under `prefers-reduced-motion: reduce` = BLOCK
