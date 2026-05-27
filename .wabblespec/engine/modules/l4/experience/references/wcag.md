# Experience Gateway — WCAG Reference

WCAG 2.1 AA requirements for web and native UI. Minimum compliance standard.

## WCAG principles (POUR)

| Principle | Meaning | Failure example |
|---|---|---|
| Perceivable | All information is available to all senses | Image with no alt text |
| Operable | All functionality works without a mouse | Button unreachable by keyboard |
| Understandable | Content and UI are clear | Error message with no guidance |
| Robust | Works across assistive technologies | Component not announced to screen reader |

## Level AA requirements (required for every UI spec)

### Text contrast

- Normal text: 4.5:1 minimum against background
- Large text (18pt+ or 14pt+ bold): 3:1 minimum
- UI components and graphics: 3:1 against adjacent colors
- Focus indicators: 3:1 against adjacent colors (WCAG 2.2 requires 3:1 against both adjacent colors)

Verify: `npm run a11y:contrast` or browser DevTools accessibility panel.

### Keyboard navigation

Every interactive element must be:
- **Reachable**: via Tab key traversal
- **Operable**: Enter (buttons, links) and Space (checkboxes, toggles) work as expected
- **Visible**: focus indicator clearly visible; never `outline: none` without a custom focus style

Tab order must be logical (generally: left-to-right, top-to-bottom, following reading order).

Skip navigation link: "Skip to main content" as the first focusable element on every page — required for keyboard users navigating repetitive content.

```html
<a href="#main" class="sr-only focus:not-sr-only">Skip to main content</a>
```

### Images and non-text content

- All `<img>` elements must have `alt` attribute
- Informative images: describe the content (`alt="Bar chart showing 40% increase in Q2 revenue"`)
- Decorative images: empty alt (`alt=""`) — screen reader skips it
- Complex images (charts, diagrams): extended description linked or included nearby
- Icons with meaning: `aria-label` on the parent button, or `aria-hidden="true"` on icon + visible text

### Form accessibility

```html
<!-- Correct: label associated with input -->
<label for="email">Email address</label>
<input id="email" type="email" name="email" required aria-describedby="email-hint">
<div id="email-hint">We'll use this to send your confirmation.</div>

<!-- Error state -->
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error">
<div id="email-error" role="alert">Please enter a valid email address.</div>
```

- Every input must have a visible label (not placeholder-only — placeholder disappears on type)
- Error messages must be programmatically associated with the input (`aria-describedby`)
- Required fields: `required` attribute; also visually indicated (asterisk with legend explaining it)
- `role="alert"` or `aria-live="polite"` for dynamically injected error messages

### Focus management

When UI state changes significantly, move focus appropriately:
- Dialog opens: move focus to the dialog (first focusable element or dialog heading)
- Dialog closes: move focus back to the element that opened it
- Page navigation (SPA): move focus to main heading or page landmark
- Form submission error: move focus to error summary

### Semantic HTML

Use the correct HTML element for the correct semantic purpose:
- `<button>`: for actions
- `<a>`: for navigation
- `<h1>`-`<h6>`: for headings (do not use `<div class="heading">`)
- `<nav>`, `<main>`, `<aside>`, `<footer>`: for landmarks
- `<ul>`/`<ol>`: for lists
- `<table>` with `<th scope>`: for data tables

Custom elements must have explicit ARIA roles when the semantic HTML equivalent is not used.

### Color and meaning

Never use color as the only means of conveying information:
- Error fields: red border + error icon + error text (not just red border)
- Required fields: asterisk + "Required" legend (not just red asterisk alone)
- Status: icon + text label (not just colored dot)

### Text resize and zoom

Content must remain readable and functional at 200% browser zoom (WCAG AA) and 400% (WCAG 2.2 AAA target).

Test: Ctrl+Plus in browser to 200%; verify no horizontal scroll on viewport width > 320px; verify no content is cut off.

## Testing approach

Manual testing (required):
1. Keyboard-only navigation: complete the primary user flow without mouse
2. Screen reader: NVDA + Firefox (Windows), VoiceOver + Safari (macOS/iOS), TalkBack (Android)
3. High contrast mode: Windows high contrast; verify no information is lost
4. 200% zoom: verify layout holds

Automated testing (CI):
```bash
npx axe-core-cli http://localhost:3000
# or
npx playwright test --config=a11y.config.ts
```

Automated tools catch ~30-40% of WCAG violations. Manual testing is required.

## ARIA usage rules

Use ARIA only when HTML semantics are insufficient. Incorrect ARIA is worse than no ARIA.

```html
<!-- Wrong: unnecessary ARIA on semantic element -->
<button role="button">Click me</button>

<!-- Right: button element already has button role -->
<button>Click me</button>

<!-- Right: ARIA needed for custom widget -->
<div role="switch" aria-checked="false" tabindex="0">Toggle</div>
```

First rule of ARIA: if you can use a native HTML element or attribute with the semantics already built in, use it.
