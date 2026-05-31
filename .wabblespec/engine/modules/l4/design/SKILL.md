---
name: gateway-design
description: Design capability gateway. UX and interaction standards for any project with a visual surface — user mental models, information architecture, interaction design, design system governance, and accessibility baseline (WCAG 2.1 AA). Applies to Web, Mobile, Desktop, Game, Extension/Plugin targets. Distinct from Aesthetic gateway: Aesthetic owns the visual language; Design owns how things work and how users move through them.
---

# Gateway: Design

Cross-cutting UX and interaction standards layer. Activates on top of (not instead of) the active platform package. Owns how things work — user mental models, information architecture, interaction patterns, design system governance, and accessibility baseline.

## What this skill does

| Concern | Covered by L3 platform | Covered by L4 Design gateway |
|---|---|---|
| Platform-specific navigation patterns | Yes (L3) | — |
| User mental model gap declaration | No L3 module | Yes |
| Feedback timing (0–100ms, 1s, 10s) | No L3 module | Yes |
| Error state recovery paths | No L3 module | Yes |
| Navigation depth limit (3 levels) | No L3 module | Yes |
| Search/filter thresholds | No L3 module | Yes |
| Touch target minimums (44x44px) | No L3 module | Yes |
| Keyboard navigation audit | No L3 module | Yes |
| Focus management on state changes | No L3 module | Yes |
| Gesture alternatives (no gesture-only) | No L3 module | Yes |
| Design system declaration | No L3 module | Yes |
| Storybook requirement (10+ components) | No L3 module | Yes |
| WCAG 2.1 AA accessibility floor | No L3 module | Yes |
| Motion profile coupling (energy matches visual style) | No L3 module | Yes |
| Motion vocabulary (semantic ease/duration mapping) | No L3 module | Yes |
| Hierarchy audit (single dominant element per view) | No L3 module | Yes |
| Transition restraint (reserved effects at key moments only) | No L3 module | Yes |

## When to use

- Visual build target: Web, Mobile, Desktop, Game, Extension/Plugin (always)
- P1 Design Document stage — user flows required
- P3 Technical Spec — interaction patterns applied
- Explicit `/design` command

## Activation sequence

### Phase A (Specify time — knowledge injection)

```
1. Confirm platform package (L3) has activated and written its receipt
2. Load references/ directory into Specify context:
   - references/flows.md (user flow completeness: loading, empty, error states)
   - references/components.md (interaction patterns, component standards)
   - references/systems.md (design system structure requirements)
3. Write gateway-spec-receipt (Phase A)
```

### Phase B (pre-Executor — verdict)

```
1. Load ux-principles.md
2. Load information-architecture.md
3. Load interaction-design.md
4. Load design-system.md
5. Load accessibility-floor.md
6. Register audit-gates.md with Verifier
7. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

## Reference Routing

| Situation | Reference |
|---|---|
| design receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type gateway-spec` / `gateway-verdict` (two-phase)` |

## Output contract

- User flow completability audit
- Mental model gap declaration check
- IA depth and labeling audit
- Interaction design compliance check (touch targets, keyboard, focus, gestures)
- Motion profile check (energy level, ease vocabulary, duration semantics)
- Hierarchy audit (single dominant element per view, reading order declared)
- Transition restraint check (reserved effects at key moments; simple transitions elsewhere)
- Design system governance check
- Accessibility floor audit (WCAG 2.1 AA)
- Gateway activation receipt with all gate results

## Phase B audit gates

### Motion profile coupling

The project's motion profile must be coherent with its visual style. Motion energy (high / moderate / calm) must be declared in `interaction-design.md` and must match the Aesthetic gateway's named style declaration. A `Swiss Pulse` style (clinical, data-driven) with slow dreamy entrances is incoherent and flags this gate.

Motion vocabulary reference — semantic language mapped to technical properties:

| Feel | Ease | Duration signal |
|---|---|---|
| Smooth | `ease-out` moderate | 0.4–0.6s — professional |
| Snappy | `ease-out` aggressive | 0.2–0.3s — energy |
| Bouncy | overshoot curve | 0.3–0.5s — playful |
| Dramatic | exponential ease-out | 0.3–0.5s — impact |
| Dreamy | `ease-in-out` sine | 0.5–0.8s — luxury |
| Cinematic | very slow ease | 1–2s — prestige |

When specifying motion, use feel vocabulary first, then map to technical properties. "Snappy entrance" is a complete spec; "0.2s ease-out" without a stated feel is underspecified.

### Hierarchy per view

Every distinct view or screen state must declare a single dominant element — the one thing a user's eye should land on first. "Reading order is obvious" is not a gate condition. The specific dominant element must be named. Views with no declared dominant element fail this gate.

### Transition restraint

Most state transitions must use the simplest available transition type for that platform. Visually distinctive transitions (custom animations, route transitions, modal reveals) are reserved for key moments: primary call-to-action, onboarding completion, destructive action confirmation, hero feature reveal. Using a custom animation for every navigation transition is the equivalent of bolding every word — it erases hierarchy.

Gate condition: for each custom transition in scope, declare which key-moment category it belongs to. Custom transitions with no declared key-moment fail this gate.

## Files loaded by this module

```
modules/l4/design/
  ux-principles.md
  information-architecture.md
  interaction-design.md
  design-system.md
  accessibility-floor.md
  audit-gates.md
```
