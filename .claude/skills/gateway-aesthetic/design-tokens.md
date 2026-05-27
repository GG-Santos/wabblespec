# Design Token Policy

## Required token types

All visual values declared as design tokens:

| Value type | Token required |
|---|---|
| Color | Yes — semantic token in component code |
| Spacing | Yes — spacing scale tokens |
| Typography (size, weight, line-height, family) | Yes — type tokens |
| Border radius | Yes — radius tokens |
| Shadow | Yes — shadow tokens |
| Duration (animation) | Yes — duration tokens |
| Easing | Yes — easing tokens |

## Token format by platform

- Web/Desktop: CSS custom properties (`--token-name: value`)
- CSS-in-JS: tokens resolve to CSS custom properties at runtime
- React Native: StyleSheet values from token constants
- SwiftUI: design tokens as SwiftUI-compatible values
- Compose: design tokens as Compose-compatible values

Platform-appropriate format declared in spec at P1.

## Enforcement rule

No raw values in component code. Any color, spacing, or other visual value that is not a token reference is a policy violation.

Code review catches violations in product code. Polish Pass 3 (structural consistency) catches token policy violations in documentation and spec files.

## Token naming convention

Tokens follow semantic naming — name describes function, not appearance:

- `--color-action-primary` not `--color-blue`
- `--spacing-content-gap` not `--spacing-16`
- `--font-size-body` not `--font-size-16`

Primitive tokens (raw values) are the only exception: primitives may use descriptive names (`--color-blue-500`) because they exist solely to be referenced by semantic tokens.

## Audit Gates

- [ ] Token file(s) committed to source control
- [ ] All 7 value types tokenized (color, spacing, typography, radius, shadow, duration, easing)
- [ ] No raw values in component code (all token references)
- [ ] Platform-appropriate token format declared
- [ ] Semantic token naming follows function-not-appearance convention
