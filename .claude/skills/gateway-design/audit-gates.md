# Design Gateway — Audit Gates

Verifier registers these gates when Design gateway activates. All HARD gates must PASS for gateway receipt to be PASS. SOFT gates flag only.

## UX Principles Gates

| Gate | Severity | Check |
|---|---|---|
| UX-1 | HARD | User mental model declared per major flow |
| UX-2 | HARD | Every interactive element has correct affordance signals |
| UX-3 | HARD | Feedback timing declared per action type |
| UX-4 | HARD | Every error type has a message and a recovery path |
| UX-5 | HARD | No generic "Something went wrong" without recovery path |

## Information Architecture Gates

| Gate | Severity | Check |
|---|---|---|
| IA-1 | HARD | Primary navigation depth <= 3 levels |
| IA-2 | SOFT | All labels reviewed against user vocabulary |
| IA-3 | HARD | Search or filter implemented when content exceeds 20 items |

## Interaction Design Gates

| Gate | Severity | Check |
|---|---|---|
| ID-1 | HARD | Touch targets meet minimums (44x44px mobile, 32x32px desktop) |
| ID-2 | HARD | All interactions keyboard-accessible |
| ID-3 | HARD | Focus management declared and implemented for state changes |
| ID-4 | HARD | No gesture-only interactions — all have visible equivalents |
| ID-5 | SOFT | Tab order follows visual/reading order |

## Design System Gates

| Gate | Severity | Check |
|---|---|---|
| DS-1 | HARD | Component library choice declared at P1 |
| DS-2 | SOFT | Each component has usage guidelines, props/API, do/don't, accessibility notes |
| DS-3 | SOFT | Storybook or equivalent declared when >= 10 custom components |
| DS-4 | HARD | Components consume Aesthetic gateway tokens (not raw values) |

## Accessibility Gates

| Gate | Severity | Check |
|---|---|---|
| AC-1 | HARD | WCAG 2.1 AA declared as minimum |
| AC-2 | HARD | Every interactive element keyboard-operable |
| AC-3 | HARD | All form inputs have associated labels (not placeholder-only) |
| AC-4 | HARD | All informational images have alt text |
| AC-5 | HARD | No accessibility-only paths |
| AC-6 | HARD | Visible focus indicators on all interactive elements |

## Motion Profile Gates

| Gate | Severity | Check |
|---|---|---|
| MP-1 | HARD | Motion energy level declared (high / moderate / calm) |
| MP-2 | HARD | Declared motion energy is coherent with the Aesthetic gateway's visual style |
| MP-3 | SOFT | Motion vocabulary documented: at least two feel → ease → duration mappings (e.g., "snappy = aggressive ease-out / 0.2–0.3s") |

**MP-1 method:** Check `interaction-design.md` for `motion_energy:` field. Absence fails.

**MP-2 coherence check:** Visual style energy must match motion energy. Swiss Pulse (clinical/high) with `calm` motion energy is incoherent and fails. If Aesthetic gateway receipt is not present, mark MP-2 as BLOCKED (Aesthetic must run first).

## View Hierarchy Gates

| Gate | Severity | Check |
|---|---|---|
| HV-1 | HARD | Each distinct view or screen state declares a single dominant element |
| HV-2 | SOFT | Reading order is declared or clearly derivable from visual weight hierarchy |

**HV-1 method:** For each view defined in `information-architecture.md` or the UX flow docs, verify a `dominant_element:` field or equivalent notation names the primary visual anchor. Views with no declared dominant element fail.

## Transition Restraint Gates

| Gate | Severity | Check |
|---|---|---|
| TR-1 | HARD | Each custom or visually distinctive transition declares a key-moment category |
| TR-2 | SOFT | Total custom transitions do not exceed 30% of total scene/view transitions |

**Key-moment categories:** primary CTA, onboarding completion, destructive action confirmation, hero feature reveal. Any category not on this list requires a named rationale.

**TR-1 method:** For each custom transition in the interaction-design spec, verify a `key_moment:` field naming which category it belongs to. Custom transitions with no category fail.
