# Design System Governance

## Component Library Declaration

Declared at P1 — one of:

| Option | Definition |
|---|---|
| Existing library | Named library adopted (Radix, shadcn/ui, MUI, etc.) — version pinned |
| Build from scratch | Custom component library — scope and timeline declared |
| Headless + styled | Headless library for behavior + custom styles — declared |

Not declared = build from scratch. Explicit decision required — default has cost implications.

## Component Documentation

Each component in the design system has:
- Usage guidelines (when to use, when not to use)
- Props/API documentation
- Do/don't examples (at least one each)
- Accessibility notes (keyboard behavior, ARIA, screen reader behavior)

## Storybook Requirement

Required for projects with >= 10 custom components. Storybook or equivalent (Histoire, Ladle, Chromatic) declared in spec when threshold is met. Stories cover:
- Default state
- All significant variants
- Error states
- Loading states
- Edge cases (empty, long content, RTL if in scope)

## Token Consumption

Design system components consume Aesthetic gateway tokens — not raw values. Components are not exempt from the design token policy. Components consume semantic tokens from the Aesthetic gateway color, spacing, and typography systems.

## Audit Gates

- [ ] Component library choice declared at P1 (not left as implicit default)
- [ ] Each component has usage guidelines, props/API docs, do/don't examples, accessibility notes
- [ ] Storybook or equivalent declared when >= 10 custom components
- [ ] Stories cover default, variants, error, loading, edge cases
- [ ] Components consume Aesthetic gateway tokens (not raw values)
