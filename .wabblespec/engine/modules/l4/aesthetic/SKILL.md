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
| WCAG AA contrast minimums | No L3 module | Yes |
| Dark mode scope declaration | No L3 module | Yes |
| Modular type scale | No L3 module | Yes |
| Font loading (font-display, subsetting) | No L3 module | Yes |
| Reduced motion (prefers-reduced-motion) | No L3 module | Yes |
| Motion duration and easing tokens | No L3 module | Yes |
| Design token policy (all visual values as tokens) | No L3 module | Yes |

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

## Output contract

- Brand asset compliance check
- Color token system audit (semantic token hierarchy, contrast pass)
- Typography compliance check (scale, loading, hierarchy)
- Motion compliance check (reduced motion, tokens)
- Design token policy audit (no raw values in component code)
- Gateway activation receipt with all gate results

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
