# Aesthetic Gateway — Typography Reference

Type system constraints, hierarchy rules, and font loading requirements.

## Type system requirements

Spec must declare a complete type system. Arbitrary font sizes in components are a quality floor violation.

### Type scale declaration

```yaml
type_scale:
  display:
    size: 48px / 3rem
    weight: 700
    line_height: 1.15
    letter_spacing: -0.02em
    usage: "Hero headings, marketing headlines"
    
  h1:
    size: 36px / 2.25rem
    weight: 700
    line_height: 1.2
    usage: "Page titles"
    
  h2:
    size: 28px / 1.75rem
    weight: 600
    line_height: 1.25
    usage: "Section headings"
    
  h3:
    size: 22px / 1.375rem
    weight: 600
    line_height: 1.3
    usage: "Sub-section headings, card titles"
    
  body-lg:
    size: 18px / 1.125rem
    weight: 400
    line_height: 1.6
    usage: "Editorial body text, important descriptions"
    
  body:
    size: 16px / 1rem
    weight: 400
    line_height: 1.5
    usage: "Default body text, UI text"
    
  body-sm:
    size: 14px / 0.875rem
    weight: 400
    line_height: 1.5
    usage: "Supporting text, labels, captions"
    
  caption:
    size: 12px / 0.75rem
    weight: 400
    line_height: 1.4
    usage: "Timestamps, fine print, helper text"
    
  code:
    size: 14px / 0.875rem
    weight: 400
    font_family: "monospace"
    usage: "Code blocks, technical strings"
```

### Type hierarchy rules

1. Maximum 3 type levels visible on a single screen at the same time (prevents visual chaos)
2. Heading levels must be sequential (h1 → h2 → h3) — never skip levels for styling purposes
3. Body text line length: 45-75 characters per line optimal; declare max-width to enforce
4. Minimum body text size: 16px for body copy (14px for UI labels acceptable)

## Font declaration

Spec must declare:

```yaml
fonts:
  primary:
    family: "Inter"
    source: "Google Fonts"
    weights: [400, 500, 600, 700]
    usage: "All UI text"
    fallback: "system-ui, -apple-system, sans-serif"
    
  monospace:
    family: "JetBrains Mono"
    source: "Google Fonts"
    weights: [400]
    usage: "Code blocks, technical content"
    fallback: "Consolas, Monaco, monospace"
```

### Font loading performance

```html
<!-- Preload critical fonts to prevent FOUT/FOIT -->
<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>

<!-- CSS font-face -->
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;   /* show fallback immediately; swap when loaded */
}
```

Use `font-display: swap` to prevent invisible text during font load.

Next.js users: use `next/font` — handles preloading, CLS prevention, and self-hosting automatically.

## Readability standards

### Line height

| Text type | Line height |
|---|---|
| Headings (tight) | 1.1 - 1.3 |
| Body (comfortable) | 1.5 - 1.7 |
| UI labels (tight) | 1.25 - 1.4 |

Line height below 1.2 on body text is a readability failure. Line height above 2.0 feels disconnected.

### Letter spacing

- Headings: slightly negative (`-0.01em` to `-0.03em`) makes tight display text feel balanced
- Body: 0 (default tracking)
- Small caps / all-caps labels: slightly positive (`0.05em` to `0.1em`) aids readability

### Text color contrast

See `color.md` for contrast ratios. Additional readability rule:

Do not use pure black (`#000000`) on pure white (`#ffffff`) for body text — the maximum contrast (21:1) can cause visual fatigue for long-form reading. Use `gray-900` (`#111827`) on `white` for body (18:1) or the reverse.

## Dark mode typography adjustments

In dark mode:
- Reduce font weight by one step where available (`700` → `600`, `600` → `500`) — light text on dark backgrounds appears heavier
- Consider slightly larger letter spacing on light text — improves readability
- Keep the same type scale — do not change sizes between light and dark

## Responsive typography

Declare how type scales across breakpoints:

```css
/* Fluid typography (recommended for display sizes) */
.display {
  font-size: clamp(2rem, 5vw, 3rem);  /* 32px → 48px */
}

/* Or breakpoint steps */
@media (max-width: 640px) {
  h1 { font-size: 1.75rem; }   /* 28px on mobile */
}
```

Minimum font size on mobile: 14px for labels, 16px for body text (browser zoom compensates for accessibility, but 14px is the floor before the text becomes genuinely unreadable).
