# Gateway: Aesthetic

Visual brand and style gate. Activates before any UI or design deliverable. Checks that proposed visual output is consistent with declared brand and style constraints.

**Skill:** `modules/l4/aesthetic/SKILL.md`
**Rules files:** `modules/l4/aesthetic/`

## What this gateway checks

- Color palette usage matches declared brand colors
- Typography choices are within the declared type system
- Spacing and layout follow declared grid or spacing scale
- Iconography is from the declared icon set (or explicitly justified otherwise)
- Motion and animation conform to declared motion principles
- Dark/light mode support is declared when the platform requires it
- Brand voice is consistent across any copy in the deliverable

## When this gateway activates

- Any target producing visual UI artifacts
- Any wave that modifies CSS, design tokens, or component visual properties
- Platform targets: web, mobile, desktop, extension
- Explicit invocation: `/gateway-aesthetic`

## Sequencing

Runs in parallel with gateway-design and gateway-experience (after security and engineering). No dependency between these three domain gateways.

## Verdict rules

**BLOCK** on:
- Use of colors outside declared brand palette with no justification
- Typography that violates WCAG contrast requirements

**FLAG** on:
- Brand color used at a non-declared opacity or tint without justification
- Motion that may cause issues for users with vestibular disorders (missing prefers-reduced-motion)
- Inconsistent spacing that deviates from the declared scale by more than one step

**PASS** when no BLOCK conditions are present.
