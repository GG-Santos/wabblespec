# Accessibility Gates

Audit enforces WCAG 2.1 AA as the minimum accessibility standard. These gates define pass/fail thresholds.

## Gate 1 — Color contrast

**Criterion:** WCAG 1.4.3 (AA)

Pass: text contrast ≥ 4.5:1 (normal text), ≥ 3:1 (large text ≥ 18pt or 14pt bold).

Fail: any text element with insufficient contrast in the primary UI flow.

**Automated check:** Use contrast ratio calculation on declared color values in design tokens, CSS, or component specs. If colors are not declared (dynamic theming): flag as `PARTIAL` — cannot verify without runtime values.

---

## Gate 2 — Keyboard navigation

**Criterion:** WCAG 2.1.1 (AA)

Pass: every interactive element (button, link, input, select, modal trigger) reachable via Tab key. No keyboard trap. Focus order follows visual order.

Fail: any interactive element not in the tab sequence without explicit `tabindex`, or a modal that cannot be closed via keyboard.

---

## Gate 3 — Alternative text

**Criterion:** WCAG 1.1.1 (AA)

Pass: all `<img>` elements have non-empty `alt` attributes. Decorative images have `alt=""`. SVG icons used as controls have `aria-label` or `title`.

Fail: any image without `alt` in a content context. Icons used as buttons without accessible name.

---

## Gate 4 — Form error identification

**Criterion:** WCAG 3.3.1 (AA)

Pass: form validation errors identify the field with the error in text (not only with color or icon). Error messages appear near the field.

Fail: errors indicated only by red border or icon without text description.

---

## Gate 5 — ARIA role correctness

**Criterion:** WCAG 4.1.2 (AA)

Pass: ARIA roles match the element's actual behavior. `role="button"` on an element that acts as a button. `aria-expanded` reflects actual state.

Fail: invalid ARIA roles, `aria-hidden` on focused elements, `role="presentation"` on interactive elements.

---

## Overall outcome

- `AA`: all five gates pass
- `PARTIAL`: one or two gates fail or are unverifiable
- `FAIL`: three or more gates fail, or Gate 1 (contrast) fails at critical severity

`attestation_required: true` on FAIL outcome — human review before release.
