# Cold-Start Behavior — Gateway Aesthetic

Defines how gateway-aesthetic behaves when expected upstream artifacts are absent.

## Absent: gateway-spec-receipt (Phase A not yet run)

Condition: `gateway-aesthetic-spec-receipt.json` absent when Phase B is triggered.
Detection: Phase B checks for spec receipt.
Action: Block Phase B — "Phase A (color / typography / motion analysis) must complete before Phase B verdict."

## Absent: spec to evaluate

Condition: No spec.md when Phase A is triggered.
Action: Produce minimal Phase A INFORM output. List required spec sections: color token declaration, type scale, motion preferences, brand palette, dark mode stance.

## Absent: reference files

Condition: `references/color.md`, `references/typography.md`, or `references/motion.md` absent.
Detection: File read returns 404 during Phase A.
Action: Log absent files. Proceed with available files. Note in Phase A receipt.

## Absent: prefers-reduced-motion declaration in spec

Condition: Spec includes animation or transition declarations but no `prefers-reduced-motion` handling.
Detection: Phase A scan finds motion references but no media query or reduced-motion alternative.
Action: Phase A issues FLAG: "prefers-reduced-motion not addressed. All animations must have a reduced/disabled alternative."

## Absent: color token system

Condition: Spec uses raw hex values or hardcoded colors rather than a token system.
Detection: Phase A finds `#hex` or `rgb(...)` literals in design declarations outside of a token definition file.
Action: Phase A issues FLAG: "Raw color values found. Design system requires a token layer: primitives → semantic → component."

## Default state on cold start

| Field | Default |
|---|---|
| `phase_a_status` | `pending` |
| `verdict` | `pending` |
| `dark_mode` | Not declared — Specify must declare stance (supported / not supported / deferred) |
| `token_system` | Not declared — raw hex values in spec are a FLAG |
| `motion_reduced` | Not declared — prefers-reduced-motion must be addressed if animations exist |
| `contrast_ratio` | WCAG AA minimum enforced: 4.5:1 normal text, 3:1 large text, 3:1 UI components |

WCAG AA contrast minimums are enforced as invariants even without reference files.
