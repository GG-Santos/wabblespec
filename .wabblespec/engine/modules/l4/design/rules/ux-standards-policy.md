# Gateway Design — UX Standards Policy

Rules enforced by gateway-design Phase B verdict. Applies to any visual-facing target: Web, Mobile, Desktop, Game, Extension/Plugin. Violations produce FLAG or BLOCK verdicts.

---

## Rule U1: Mental Model Gap Declaration

**Requirement:** Every spec for a user-facing target must declare the primary user mental model and any known gaps between that model and the system's actual behavior.

| Requirement | Details |
|---|---|
| Mental model statement | One-sentence description of how the target user expects the system to work |
| Known gaps | List of any system behaviors that contradict the stated mental model |
| Gap resolution | Each gap must be addressed by one of: onboarding copy, progressive disclosure, or explicit design decision in spec |

**Failure modes:**
- No mental model declaration in spec for user-facing feature = FLAG
- Known gap with no resolution path = FLAG
- Mental model declared but system spec contradicts it without acknowledgment = BLOCK

---

## Rule U2: Feedback Timing Compliance

**Requirement:** All interactive operations must provide feedback within the declared timing tiers.

| Timing tier | Threshold | User expectation | Required response |
|---|---|---|---|
| Instant | 0–100ms | Action felt immediate | No loading indicator needed |
| Responsive | 100ms–1s | Slight delay noticeable | Feedback must begin within 100ms (e.g., button state change, cursor change) |
| Processing | 1s–10s | Noticeable wait | Progress indicator required; preserve user context |
| Long operation | > 10s | User assumes something is wrong | Background processing with notification; user must be able to leave and return |

**Failure modes:**
- No feedback for operations expected to take > 100ms = BLOCK
- No progress indicator for operations expected to take > 1s = FLAG
- Long operations (> 10s) that block the UI without a way to continue elsewhere = BLOCK

---

## Rule U3: Information Architecture Depth

**Requirement:** Navigation depth must not exceed 3 levels for any user flow reaching a primary task completion.

| Depth | Definition | Rule |
|---|---|---|
| Level 1 | Top navigation / home | Always present |
| Level 2 | Section or category | Permitted |
| Level 3 | Content or task | Permitted; maximum for P0 flows |
| Level 4+ | Any node requiring > 3 navigational steps | Requires IA redesign for P0 flows |

**Exception:** Deep content archives (documentation, file browsers, administrative configuration) may exceed 3 levels with clear breadcrumb navigation and search.

**Search / filter threshold:** Lists of more than 10 items must provide search or filter capability. Lists of more than 50 items must provide both.

**Failure modes:**
- P0 user flow requiring > 3 navigation levels = BLOCK
- List of > 10 items without search or filter = FLAG
- Breadcrumbs absent in deep navigation (> 3 levels) = FLAG

---

## Rule U4: Error State Recovery Paths

**Requirement:** Every error state in the product must have a declared recovery path.

| Error type | Recovery requirement |
|---|---|
| Form validation error | Inline error message at the field level; submit retry path clear |
| Network error (failed request) | Retry action surfaced; user data preserved (no form clear on error) |
| Empty state (no data yet) | Positive empty state with action to populate; not a blank screen |
| Permission error | Explain what permission is needed and how to obtain it; do not show a 403 page with no context |
| System error (500 / crash) | Apologetic message; preserve user context; provide a path to retry or report |

**Failure modes:**
- Error state with no recovery path = BLOCK
- Form that clears user input on submission error = BLOCK
- Empty state that is a blank screen with no context or action = FLAG
- Permission error page with no explanation of how to gain access = FLAG

---

## Rule U5: Design System Governance

**Requirement:** Any visual target with 10 or more UI components must use a declared design system.

| Requirement | Details |
|---|---|
| Design system declaration | Named design system (internal or third-party) declared in spec |
| Component source | Components sourced from the declared design system; ad-hoc components justified and documented |
| Storybook (10+ components) | Storybook or equivalent component explorer required; stories cover default, hover, focus, disabled, and error states |
| Token alignment | Design system tokens must align with the aesthetic gateway token system |

**Failure modes:**
- 10+ components with no design system declared = FLAG
- Storybook absent for project with 10+ components = FLAG
- Component states (hover, focus, disabled, error) not represented in Storybook = FLAG
- Design system tokens and aesthetic gateway tokens in conflict = FLAG
