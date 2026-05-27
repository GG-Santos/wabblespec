# Typography Standards

## Type Scale

Modular scale declared — not ad hoc font sizes. Each size derived by multiplying or dividing by a consistent ratio (e.g., 1.25 major third, 1.333 perfect fourth).

Type scale declared as tokens:

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

## Font Loading

- Variable fonts preferred when available (one file, multiple weights/widths)
- `font-display: swap` required — no invisible text during font load
- Subsetting: required when font file exceeds declared size budget
- System font stack fallback: declared for every custom font

## Type Hierarchy

- H1–H6 used semantically — heading level reflects document structure, not visual size
- Visual size controlled by token; semantic level controlled by HTML element
- No heading element styled to look like a larger heading level — use CSS classes on correct semantic element

## Audit Gates

- [ ] Modular type scale declared as tokens
- [ ] No font-size values in component code outside token set
- [ ] `font-display: swap` declared for all custom fonts
- [ ] System font stack fallback declared for every custom font
- [ ] Variable fonts used where available
- [ ] Heading elements used semantically (H1–H6 reflect structure, not size)
