# Design Gateway — Design Systems Reference

Design system structure requirements and component pattern standards.

## Design system requirements

A design system is required when: more than one screen shares visual patterns, or more than one engineer works on UI.

Spec must declare one of:
1. **Building design system**: spec includes design token declarations, component library structure, and documentation plan
2. **Using existing design system**: declare which system (Material UI, Ant Design, Radix UI, shadcn/ui, etc.) and how it is configured
3. **No design system** (single-screen, single-use tool): acknowledge the trade-off — no token/component reuse expected

## Design system components

### Layer 1 — Foundations (required first)

Foundations must be declared before components:
- **Color tokens**: semantic color palette (see aesthetic/color.md)
- **Typography scale**: type scale and font declarations (see aesthetic/typography.md)
- **Spacing scale**: consistent spacing values (4px base grid recommended)
- **Border radius scale**: consistent corner radii
- **Shadow scale**: elevation levels
- **Motion tokens**: duration and easing values (see aesthetic/motion.md)

```yaml
spacing_scale:
  0: 0px
  1: 4px
  2: 8px
  3: 12px
  4: 16px
  5: 20px
  6: 24px
  8: 32px
  10: 40px
  12: 48px
  16: 64px
```

### Layer 2 — Primitives (base components)

- Button (variants: primary, secondary, ghost, destructive; sizes: sm, md, lg)
- Input (text, email, password, number, textarea)
- Select / Dropdown
- Checkbox, Radio, Toggle
- Badge / Tag
- Avatar
- Icon (icon system declared)
- Spinner / Loading indicator

Each primitive must declare: variants, sizes, states (default, hover, focus, active, disabled, error), and accessibility behavior.

### Layer 3 — Composites (assembled from primitives)

- Form (label + input + hint + error)
- Search input (input + icon + clear button)
- Date picker
- Table (with sorting, pagination)
- Modal / Dialog
- Toast / Notification
- Dropdown menu
- Tabs
- Accordion

### Layer 4 — Patterns (page-level)

- Empty state (see design/flows.md)
- Error state
- Loading skeleton
- Data table with actions
- Form with validation
- Navigation with active states

## Component specification format

Each component in the design system must have:

```markdown
## Component: {name}

**Usage**: {when to use this component}
**Do not use when**: {when to prefer an alternative}

### Props / API

| Prop | Type | Default | Description |
|---|---|---|---|
| variant | "primary" | "secondary" | "ghost" | "primary" | Visual style |
| size | "sm" | "md" | "lg" | "md" | Component size |
| disabled | boolean | false | Disables interaction |
| loading | boolean | false | Shows loading state |
| onClick | function | undefined | Click handler |

### States

| State | Visual | Behavior |
|---|---|---|
| default | {describe appearance} | {normal behavior} |
| hover | {describe appearance} | {cursor: pointer} |
| focus | {describe focus ring} | {keyboard navigable} |
| active | {describe press state} | {scale(0.97)} |
| disabled | {opacity 0.5, cursor: not-allowed} | {no events} |
| loading | {spinner visible} | {no events; aria-busy} |

### Accessibility

- Role: `button` (native element preferred)
- Keyboard: Enter and Space activate
- ARIA: `aria-disabled` when disabled; `aria-busy` when loading
- Focus: visible focus ring; never remove outline without replacement
```

## Token consumption rules

```typescript
// WRONG: raw values — creates inconsistency and maintenance debt
<div style={{ padding: '12px', color: '#1f2937', borderRadius: '6px' }}>

// RIGHT: tokens — consistent and maintainable
<div className="p-3 text-gray-800 rounded-md">
// OR with CSS variables:
<div style={{ padding: 'var(--spacing-3)', color: 'var(--color-text-primary)' }}>
```

Rules:
- Never use raw hex values for colors in UI components
- Never use arbitrary px values for spacing — use the scale
- Never use arbitrary border-radius values — use the scale
- If a design requires a value not in the token scale, either update the scale or escalate to design

## Documentation requirements

A design system must be documented or it will not be used correctly:
- **Component playground**: interactive examples (Storybook, or equivalent)
- **Usage guidelines**: when to use each component; common mistakes
- **Changelog**: what changed per version; migration guides for breaking changes
- **Accessibility notes**: per-component accessibility behavior and requirements

Storybook is the standard for component documentation. If not using Storybook, declare the alternative.
