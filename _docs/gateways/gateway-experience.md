# Gateway: Experience

Accessibility, performance, and delight gate. The final user-facing quality check before Executor. Activates after the design gateway has passed — it assumes interaction design is coherent and checks the quality of the experience itself.

**Skill:** `modules/l4/experience/SKILL.md`
**Rules files:** `modules/l4/experience/`
**Dependency:** Requires `gateway-design` PASS receipt before activating.

## What this gateway checks

### Accessibility
- Interactive elements have declared accessible names (labels, aria-label, or visible text)
- Color contrast meets WCAG AA for all text (4.5:1 for normal, 3:1 for large)
- Keyboard navigation path is declared for all interactive flows
- Focus management is declared for modals, drawers, and dynamic content
- Screen reader behavior is declared for non-text content

### Performance
- Bundle size impact is declared for any new dependency added
- Rendering budget: list views have declared virtualization strategy if > 100 items
- Network requests: loading strategy declared (eager/lazy/prefetch) for significant fetches
- Animation frame budget: declared for any animation > 100ms

### Delight
- Feedback latency: any action > 100ms has a declared feedback state (loading indicator, optimistic update)
- Error recovery: error messages tell the user what to do, not just what went wrong
- Success confirmation: non-obvious success states have a declared confirmation signal

## When this gateway activates

- Any user-facing execution after design gateway has passed
- Platform targets: web, mobile, desktop, extension
- Explicit invocation: `/gateway-experience`

## Sequencing

Runs in parallel with gateway-aesthetic (after gateway-design has passed). Requires gateway-design PASS as precondition.

## Verdict rules

**BLOCK** on:
- Interactive element with no accessible name
- Color contrast failure for body text
- No keyboard navigation path declared for a modal or critical flow

**FLAG** on:
- Loading state not declared for an action > 100ms
- Error message that states the error without providing recovery guidance
- List view with no declared virtualization strategy for large datasets

**PASS** when no BLOCK conditions are present.
