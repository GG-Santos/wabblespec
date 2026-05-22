# Aesthetic Gateway — Audit Gates

Verifier registers these gates when Aesthetic gateway activates. All HARD gates must PASS for gateway receipt to be PASS. SOFT gates flag only.

## Brand Gates

| Gate | Severity | Check |
|---|---|---|
| BR-1 | HARD | Brand asset source of truth declared in P1 spec |
| BR-2 | HARD | All brand colors declared as design tokens (not inline) |
| BR-3 | SOFT | Logo usage rules declared (minimum size, clear space, prohibited treatments) |

## Color Gates

| Gate | Severity | Check |
|---|---|---|
| CO-1 | HARD | Three-tier token hierarchy present (primitive → semantic → component) |
| CO-2 | HARD | No component code references primitive tokens directly |
| CO-3 | HARD | No raw hex/RGB values in component code |
| CO-4 | HARD | All text contrast ratios >= 4.5:1 (normal) or >= 3:1 (large) |
| CO-5 | HARD | All UI component contrast ratios >= 3:1 |
| CO-6 | HARD | Dark mode scope declared (yes/no/auto) |
| CO-7 | SOFT | Dark mode fully implemented if scope = yes or auto |

## Typography Gates

| Gate | Severity | Check |
|---|---|---|
| TY-1 | HARD | Modular type scale declared as tokens |
| TY-2 | HARD | No font-size values in component code outside token set |
| TY-3 | HARD | `font-display: swap` declared for all custom fonts |
| TY-4 | SOFT | System font stack fallback declared for every custom font |
| TY-5 | SOFT | Heading elements used semantically |

## Motion Gates

| Gate | Severity | Check |
|---|---|---|
| MO-1 | HARD | `prefers-reduced-motion: reduce` handled for all motion |
| MO-2 | HARD | Non-motion alternative provided for state-communicating motion |
| MO-3 | SOFT | Duration tokens used (no inline ms values) |
| MO-4 | SOFT | Easing tokens used (no inline cubic-bezier values) |

## Design Token Gates

| Gate | Severity | Check |
|---|---|---|
| DT-1 | HARD | All 7 value types tokenized |
| DT-2 | HARD | No raw visual values in component code |
| DT-3 | SOFT | Semantic token names follow function-not-appearance convention |
