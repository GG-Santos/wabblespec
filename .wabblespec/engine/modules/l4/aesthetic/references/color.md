# Aesthetic Gateway — Color Reference

Brand palette enforcement, contrast requirements, and dark mode declaration standards.

## Color system requirements

Spec must declare a complete color system before any UI work begins. Ad-hoc color values in components are a quality floor violation.

### Color token structure

```
colors/
  primitives/      — raw values (never used directly in UI)
    blue-500: #2563eb
    gray-100: #f3f4f6
  
  semantic/        — meaning-mapped (used in UI)
    primary: {value: blue-500, dark: blue-400}
    surface: {value: white, dark: gray-900}
    text-primary: {value: gray-900, dark: gray-50}
    text-secondary: {value: gray-600, dark: gray-400}
    border: {value: gray-200, dark: gray-700}
    
  status/          — feedback colors
    success: {value: green-600, dark: green-400}
    warning: {value: amber-600, dark: amber-400}
    error: {value: red-600, dark: red-400}
    info: {value: blue-600, dark: blue-400}
```

All UI components use semantic tokens, not primitive values. If a designer specifies `#2563eb`, convert it to `primary` before implementing.

## Contrast requirements

WCAG 2.1 AA minimum (required):

| Text type | Minimum contrast ratio | Against |
|---|---|---|
| Normal text (< 18pt / < 14pt bold) | 4.5:1 | Background |
| Large text (≥ 18pt / ≥ 14pt bold) | 3:1 | Background |
| UI components and graphics | 3:1 | Adjacent color |
| Focus indicators | 3:1 | Adjacent color |

WCAG 2.1 AAA (declare if targeting):
- Normal text: 7:1
- Large text: 4.5:1

### Verification

```bash
# Check contrast programmatically
npx @accessibility-checker/color-contrast check --foreground "#1f2937" --background "#ffffff"
# Output: 12.63:1 — PASS (AA)
```

Every color pair used for text must be verified and the ratio declared in spec or design tokens.

## Dark mode

Spec must explicitly declare whether dark mode is supported. Three valid declarations:

1. **Supported**: full dark mode implementation required; all color tokens have dark variants
2. **Not supported**: declare explicitly; user preference for dark mode ignored
3. **Deferred**: not in current scope; dark mode support added in a later milestone

If supported, dark mode must use `prefers-color-scheme` media query:
```css
:root { --color-surface: #ffffff; --color-text: #111827; }
@media (prefers-color-scheme: dark) {
  :root { --color-surface: #111827; --color-text: #f9fafb; }
}
```

Or JavaScript-controlled class:
```javascript
document.documentElement.classList.toggle('dark', userPreference === 'dark')
```

## Brand palette usage rules

Spec must declare brand palette and usage constraints:

```yaml
brand_palette:
  primary:
    value: "#2563eb"
    usage: "Primary actions, links, focus rings"
    do_not_use_for: "Error states, success states"
    
  accent:
    value: "#7c3aed"
    usage: "Highlights, special features, premium indicators"
    frequency: "Use sparingly — not for general UI"
    
  neutral:
    range: "gray-50 through gray-950"
    usage: "Surfaces, text, borders — most of the UI"
    
  semantic:
    success: "#16a34a"
    warning: "#d97706"
    error: "#dc2626"
    info: "#2563eb"
```

Color should not compete — every screen should have one dominant color. Exceptions require explicit justification.

## Color blindness considerations

Design for the most common forms of color blindness:
- **Red-green (deuteranopia/protanopia)**: do not rely on red/green alone to convey meaning
- Always use: color + icon, color + label, color + pattern

```
Error state: red color + ✕ icon + "Error:" label prefix
Success state: green color + ✓ icon + "Success:" label prefix
```

Never: "The red items need attention." → "The flagged items (marked with ⚠) need attention."
