# Gateway: Design

UX and interaction design gate. Activates before any UX or interaction deliverable. Checks that the proposed user flows, interactions, and information architecture are coherent and user-centered.

**Skill:** `modules/l4/design/SKILL.md`
**Rules files:** `modules/l4/design/`

## What this gateway checks

- User flows are complete — no dead ends, no missing error states
- Information architecture matches declared user mental model
- Interaction patterns are consistent with the declared design system
- Form design: labels, validation messages, and error states are declared
- Navigation structure is coherent — no orphaned pages or circular flows
- Empty states are handled — no missing zero-data states for list/table views
- Loading states are declared for any async operation

## When this gateway activates

- Any target producing UX flows, wireframes, or interaction specifications
- Any wave that modifies user-facing navigation or information structure
- Platform targets: web, mobile, desktop
- Explicit invocation: `/gateway-design`

## Sequencing

Runs in parallel with gateway-aesthetic (after security and engineering). Gateway-experience depends on this gateway — experience checks assume design has passed.

## Dependency

`gateway-experience` declares `depends_on: [gateway-design]`. The experience gateway will not activate if the design gateway has not yet written a PASS receipt for this execution.

## Verdict rules

**BLOCK** on:
- User flow with no declared error state for a failable action
- Navigation that creates an unreachable state (page with no back path)
- Form with validation but no declared validation message copy

**FLAG** on:
- Empty state not declared for a list or table view
- Loading state not declared for an operation estimated > 300ms
- Interaction pattern that deviates from declared design system without justification

**PASS** when no BLOCK conditions are present.
