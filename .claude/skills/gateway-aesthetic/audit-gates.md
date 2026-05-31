# Aesthetic Gateway — Audit Gates

Verifier registers these gates when Aesthetic gateway activates. All HARD gates must PASS for gateway receipt to be PASS. SOFT gates flag only.

## Standards Basis

Gates in this document derive from the following standards. When citing a gate finding, name the standard and version. Platform-specific guidelines (HIG, Material Design) update; verify the version referenced matches the current platform target before applying platform-specific rules.

| Standard | Covers | Freshness risk |
|---|---|---|
| WCAG 2.1 (W3C) | Contrast ratios, keyboard accessibility, alt text, color not sole indicator | Low — versioned; current is WCAG 2.1 (2018); WCAG 2.2 adds new criteria |
| Apple Human Interface Guidelines | iOS/macOS/watchOS/tvOS/visionOS design: touch targets (44pt), Dynamic Type, Reduce Motion, SF Symbols, semantic colors | HIGH — Apple updates HIG with OS releases; cite the OS version being targeted |
| Material Design 3 (Google) | Android/web: touch targets (48dp), state layers, typography roles, color tokens | Medium — versioned releases; cite MD3 when targeting Android or cross-platform |
| ui-ux-pro-max reference pack | Cross-platform synthesis: accessibility, interaction, performance, layout, animation, forms | Medium — synthesized from HIG + MD3; check against live HIG/MD3 for recent changes |

**Freshness policy:** Before applying any Apple HIG or Material Design rule in a gate finding, confirm the rule is current for the declared OS/platform version of the target project. Note the version in the gate receipt.

---

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

## Touch & Interaction Gates

Applies to Web, Mobile, Desktop targets with interactive UI. Skip for API/CLI/Library targets.

| Gate | Severity | Check | Reference |
|---|---|---|---|
| TI-1 | HARD | All interactive elements meet minimum touch target size: 44×44pt (Apple HIG) / 48×48dp (Material Design 3) | HIG: Targets; MD3: Accessible design |
| TI-2 | HARD | Minimum 8px gap between adjacent touch targets | HIG: Layout; MD3: Touch targets |
| TI-3 | HARD | Primary interactions use click/tap — no hover-only interactions for critical actions | WCAG 2.1 SC 2.5.3 |
| TI-4 | HARD | `prefers-reduced-motion` respected for all motion (gate supplements MO-1 — confirms implementation, not just declaration) | WCAG 2.1 SC 2.3.3; HIG: Reduce Motion |
| TI-5 | SOFT | Visual press feedback provided within 100ms of tap (highlight, ripple, or scale) | HIG: Fluid interfaces; MD3: Interaction states |
| TI-6 | SOFT | Loading state shown for async actions exceeding 300ms; button disabled during in-flight request | HIG: Loading; MD3: Progress indicators |

**Method:**
```bash
# TI-1: Check touch target sizes (automated partial check)
# In Playwright or browser devtools, inspect computed size of all button/a/input elements:
# page.$$eval('button, a, input, [role="button"]', els => els.map(el => ({
#   tag: el.tagName, w: el.offsetWidth, h: el.offsetHeight, text: el.textContent?.trim().slice(0,30)
# })).filter(el => el.w < 44 || el.h < 44))

# TI-3: Search for hover-only interactions in source
grep -rn ':hover' src/ --include="*.css" --include="*.scss" --include="*.tsx" \
  | grep -v ':focus\|:active\|:focus-visible'
# Review matches — each :hover-only style that communicates state or triggers action is a finding.
```

**Pass:** TI-1 through TI-4 pass. TI-5/TI-6 flagged only.
**Fail:** Any HARD gate fails. Action: resize elements, add focus/tap state, add reduced-motion handling.

---

## Design Token Gates

| Gate | Severity | Check |
|---|---|---|
| DT-1 | HARD | All 7 value types tokenized |
| DT-2 | HARD | No raw visual values in component code |
| DT-3 | SOFT | Semantic token names follow function-not-appearance convention |

## Extended Color Gates (3-tier accent structure)

| Gate | Severity | Check |
|---|---|---|
| CO-8 | HARD | Every declared accent color has three tiers: full value, light/background tier, border tier |
| CO-9 | SOFT | Accent tiers follow naming convention: `--accent-<name>`, `--accent-<name>-light`, `--accent-<name>-border` |

**CO-8 method:** For each declared accent color, verify all three token tiers exist in the token file. A single hex value with no bg/border tiers fails. "Single-tier accent" is acceptable only with explicit rationale in brand.md.

## Shadow Philosophy Gates

| Gate | Severity | Check |
|---|---|---|
| SH-1 | HARD | Shadow philosophy declared as one of: `flat`, `elevated`, or `mixed` |
| SH-2 | SOFT | If `flat`: border (`1px solid var(--border)`) used in place of box-shadow in component code |
| SH-3 | SOFT | If `elevated`: shadow levels defined as tokens (not inline values) |

**SH-1 method:** Check `brand.md` for `shadow_philosophy:` field or equivalent declaration. Absence fails.

## Anti-Monoculture Gates

| Gate | Severity | Check |
|---|---|---|
| AN-1 | SOFT | Any of the following patterns present in the design must have a documented rationale: gradient text, left-edge accent stripes on cards, cyan-on-dark / neon primary palette, pure `#000`/`#fff` untinted, identical same-size card grids as primary layout, everything centered with equal visual weight |
| AN-2 | HARD | Primary typeface is NOT one of: Inter, Roboto, Arial, system-ui, or bare sans-serif as the sole font declaration. These are the most common AI-generation convergence fonts. Exception requires a documented rationale citing why the content specifically calls for this choice. |
| AN-3 | HARD | Primary color palette does NOT use purple-to-blue gradient as dominant visual statement, or purple background with white text as the primary surface. These combinations appear in the majority of AI-generated UIs — flag without exception. |
| AN-4 | SOFT | This project's visual identity is distinct from recent WabbleSpec project outputs. If the same primary typeface, color palette, or layout pattern was used in a prior project in this session, this project must differentiate unless the brand brief explicitly reuses it. |

**AN-1 method:** The presence of these patterns is not a failure — the absence of rationale is. For each pattern found, check whether `brand.md` or the design spec contains a one-line rationale tying the choice to the project brief. No rationale = SOFT flag. Documented rationale = pass.

**AN-2/AN-3 method:** Check the declared typeface in `typography.md` and primary palette in `color.md`. AN-2 and AN-3 are HARD gates — no rationale exception for these specific choices. If the brand brief explicitly specifies Inter or purple/white, treat that as a brand constraint and escalate to user for confirmation before passing.

## Background Layer Gates

| Gate | Severity | Check |
|---|---|---|
| BL-1 | HARD | Visual surface background layer strategy explicitly declared |
| BL-2 | SOFT | If background layer declared, at least one element type specified (radial glows, ghost text, accent lines, grain/noise, geometric shapes, thematic decoratives) |

**BL-1 method:** Check `brand.md` for `background_layer:` field. Acceptable values: any declared element type, or "none" with explicit declaration. Absence fails — undeclared is not the same as "none".

## Named Visual Style Gates

| Gate | Severity | Check |
|---|---|---|
| VS-1 | HARD | Visual style declared with mood, motion energy level, and atmosphere elements |
| VS-2 | SOFT | If custom style (not a named standard): rationale block covers why not a standard style |

**VS-1 method:** Check `brand.md` for `visual_style:` block containing at minimum: `mood`, `motion_energy` (high/moderate/calm), and `atmosphere[]`. Absence of any field fails.
