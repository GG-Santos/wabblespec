# Cold-Start Behavior — Gateway Experience

Defines how gateway-experience behaves when expected upstream artifacts are absent.

## Absent: gateway-spec-receipt (Phase A not yet run)

Condition: `gateway-experience-spec-receipt.json` absent when Phase B is triggered.
Detection: Phase B checks for spec receipt.
Action: Block Phase B — "Phase A (WCAG / platform UX analysis) must complete before Phase B verdict."

## Absent: spec to evaluate

Condition: No spec.md when Phase A is triggered.
Action: Produce minimal Phase A INFORM output. List required spec sections: accessibility target (WCAG level), platform UX guidelines, keyboard navigation support, screen reader requirements.

## Absent: reference files

Condition: `references/wcag.md` or `references/platform-ux.md` absent.
Detection: File read returns 404 during Phase A.
Action: Log absent files. Proceed with available files. Note in Phase A receipt.
Do NOT: Skip accessibility analysis when `wcag.md` is absent. Apply WCAG AA minimums from invariant knowledge.

## Absent: keyboard navigation declaration

Condition: Spec describes interactive UI but no keyboard navigation is declared.
Detection: Phase A scan finds buttons, modals, forms, dropdowns with no keyboard handling mention.
Action: Phase A issues FLAG: "Interactive elements require keyboard navigation declarations. All interactive elements must be reachable and operable via keyboard."

## Absent: focus management declaration

Condition: Spec includes modals, drawers, or route changes but no focus management.
Detection: Phase A finds modal/drawer/page transition with no focus trap or focus restoration mention.
Action: Phase A issues FLAG: "Modal/drawer/route change requires explicit focus management declaration."

## Default state on cold start

| Field | Default |
|---|---|
| `phase_a_status` | `pending` |
| `verdict` | `pending` |
| `wcag_target` | WCAG 2.1 AA — enforced minimum; AAA is optional |
| `keyboard_nav` | Required for all interactive elements — enforced invariant |
| `skip_nav` | Required for web targets — "Skip to main content" link at top of page |
| `color_meaning` | Information must not rely on color alone — enforced invariant |
| `platform_ux` | Not declared — Specify must declare which platform guidelines apply (HIG / Material / Fluent) |

WCAG 2.1 AA and keyboard navigation are experience invariants — enforced even without reference files.
