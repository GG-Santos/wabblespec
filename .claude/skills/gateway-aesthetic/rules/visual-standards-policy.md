# Gateway Aesthetic — Visual Standards Policy

Rules enforced by gateway-aesthetic Phase B verdict. Applies to any target with a visual surface: Web, Mobile, Desktop, Game, Extension/Plugin. Violations produce FLAG or BLOCK verdicts.

---

## Rule V1: Brand Asset Source of Truth

**Requirement:** Every project with a visual surface must declare a single source of truth for brand assets.

| Asset type | Requirement |
|---|---|
| Logo (primary, monochrome, reversed) | Stored in VCS at a declared path; no hotlinks to external CDN |
| Favicon / app icon | All required sizes generated from the primary logo source; not manually cropped |
| Brand guidelines document | Referenced in spec; designers and engineers consult it before producing visual output |
| Asset format | SVG for vector assets; PNG exports at declared resolutions for raster needs |

**Failure modes:**
- Logo sourced from external hotlink in production = FLAG
- Multiple conflicting logo versions present in VCS without a designated primary = FLAG
- No brand guidelines reference in spec for visual-facing target = FLAG

---

## Rule V2: Semantic Color Token System

**Requirement:** All colors used in a visual target must be expressed as semantic tokens, not raw hex or RGB values, in component code.

**Token hierarchy:**

| Tier | Example | Purpose |
|---|---|---|
| Primitive (palette) | `--color-blue-500: #3B82F6` | Raw brand palette; defined once in design tokens |
| Semantic (role-based) | `--color-interactive-default: var(--color-blue-500)` | Maps primitive to purpose |
| Component | `--button-primary-bg: var(--color-interactive-default)` | Component-level override (optional) |

**Failure modes:**
- Raw hex, RGB, or HSL values in component CSS or inline styles (outside token definition files) = BLOCK
- Semantic token layer absent (components reference primitives directly) = FLAG
- Color token system not portable to dark mode (primitive values hardcoded) = FLAG

---

## Rule V3: WCAG AA Contrast Minimum

**Requirement:** All text and interactive elements must meet WCAG 2.1 AA contrast ratios.

| Content type | Minimum contrast ratio |
|---|---|
| Normal text (< 18pt / < 14pt bold) | 4.5:1 |
| Large text (>= 18pt / >= 14pt bold) | 3:1 |
| UI components and graphical objects | 3:1 against adjacent colors |
| Placeholder text | 4.5:1 (not exempt from contrast requirements) |
| Decorative content only | Exempt |

**Verification:** Automated contrast check (axe-core, Lighthouse accessibility audit, or Storybook accessibility addon) must run in CI. Manual review required for custom color combinations not covered by automated tools.

**Failure modes:**
- Text contrast below 4.5:1 for normal body text = BLOCK
- UI component contrast below 3:1 = FLAG
- No automated contrast check in CI = FLAG

---

## Rule V4: Dark Mode Scope Declaration

**Requirement:** Every visual target must explicitly declare its dark mode position in the spec.

| Position | Definition | Requirements |
|---|---|---|
| Full dark mode support | Product supports both light and dark | Color tokens must include dark mode semantic mapping; `prefers-color-scheme` honored |
| Light only (intentional) | Product does not support dark mode | Declared in spec with rationale; no unthemed dark mode artifacts |
| System-default pass-through | Product defers to OS default | Tokens must not hardcode light-only values; test with both OS settings |

**Failure modes:**
- Dark mode position undeclared in spec for visual target = FLAG
- Semantic color tokens that only work in light mode with "Full dark mode support" declared = BLOCK
- `prefers-color-scheme` media query absent when "Full dark mode support" is declared = FLAG
