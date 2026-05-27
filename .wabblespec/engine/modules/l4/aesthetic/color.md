# Color System Standards

## Token Hierarchy

All colors expressed as semantic tokens — never raw hex values in component code.

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

## Contrast Requirements

Non-negotiable minimums — cannot be waived:

| Context | Minimum ratio | WCAG level |
|---|---|---|
| Normal text (< 18pt) | 4.5:1 | AA |
| Large text (>= 18pt or 14pt bold) | 3:1 | AA |
| UI components and graphical objects | 3:1 | AA |
| Decorative elements | None | N/A |

AAA (7:1 normal text, 4.5:1 large) declared when accessibility beyond baseline is a stated requirement.

## Dark Mode

Scope declared in spec at P1:
- `yes`: dark mode implemented — semantic token system required
- `no`: light mode only — explicitly declared
- `auto`: respects `prefers-color-scheme` — semantic token system required

No partial dark mode — either in scope or out of scope. Partially implemented dark mode is not a delivery state.

## Brand vs. Semantic Color Separation

Brand colors (defined by brand guidelines) are primitives. Semantic colors (defined by function) reference brand primitives. Components never hardcode brand colors — they reference semantic tokens.

## Audit Gates

- [ ] Three-tier token hierarchy present (primitive → semantic → component)
- [ ] No component code references a primitive token directly
- [ ] No raw hex/RGB values in component code
- [ ] All text/UI contrast ratios meet WCAG AA minimums
- [ ] Dark mode scope declared (yes/no/auto)
- [ ] Brand colors declared as primitive tokens (not hardcoded)
