# Accessibility Floor

WCAG 2.1 AA is the minimum baseline for all visual targets. Non-negotiable. Cannot be waived by project decision.

## Requirements

| Requirement | What it means |
|---|---|
| Keyboard navigation | Every interactive element reachable and operable by keyboard |
| Screen reader | Semantic HTML or ARIA where HTML semantics are insufficient |
| Color contrast | Aesthetic gateway contrast requirements (4.5:1 text, 3:1 UI) |
| Reduced motion | Aesthetic gateway reduced motion requirements |
| Focus indicators | Visible focus ring on all interactive elements (browser default or custom) |
| Form labels | Every input has an associated label (not placeholder-only) |
| Images | Alt text for informational images, `alt=""` for decorative |
| Tables | `scope` attributes, captions where appropriate |

## No Accessibility-Only Paths

Accessibility is integrated into the primary experience, not a separate mode or toggle. An "accessible version" of a page is not an acceptable approach. Every user takes the same path.

## AAA Declaration

WCAG 2.1 AAA (7:1 contrast for normal text, 4.5:1 for large) is declared when accessibility beyond baseline is a stated requirement. Not assumed from AA compliance — explicit declaration required.

## Audit Gates

- [ ] WCAG 2.1 AA declared as minimum (not a stretch goal)
- [ ] Every interactive element keyboard-operable
- [ ] Semantic HTML or ARIA used correctly throughout
- [ ] All form inputs have associated labels (not placeholder-only)
- [ ] All informational images have alt text
- [ ] No accessibility-only paths or "accessible version" toggles
- [ ] Visible focus indicators on all interactive elements
