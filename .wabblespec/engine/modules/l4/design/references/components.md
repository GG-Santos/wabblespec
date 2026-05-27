# Design Gateway — Component Pattern Reference

Component pattern library references and interaction design standards.

## Interaction design principles

### Affordance

Components must look like what they do:
- Buttons: elevated appearance (background color, border, shadow) signals clickability
- Links: underlined or colored text signals navigation
- Inputs: bordered, inset appearance signals editability
- Disabled: reduced opacity + `not-allowed` cursor signals non-interactivity

Never use non-interactive elements that look interactive, or interactive elements that look static.

### Feedback

Every action must have a response:
- Immediate (< 100ms): visual change (hover state, button press)
- Short (100ms-1s): loading indicator if result is pending
- Long (> 1s): progress indicator with label

Silence after a user action (no visible change) is always a bug.

### Forgiveness

Users make mistakes. UI must make recovery easy:
- Undo: wherever destructive actions are available (delete, archive, send)
- Confirmation dialogs: for irreversible high-consequence actions only (not every delete)
- Autosave: reduce the cost of browser close / accidental navigation
- Draft state: preserve in-progress work across sessions

## Navigation components

### Tab bar (primary navigation)

- 2-5 items maximum; more than 5 becomes unmanageable
- Active state must be clearly distinct from inactive
- Touch target: 44×44pt minimum (iOS), 48×48dp (Android)
- Labels: text + icon preferred; icon-only requires tooltip on web

### Breadcrumb

Use when: hierarchical navigation with more than 2 levels:
```
Home > Products > Electronics > Headphones
```
- Current page: not a link; visually distinct from ancestors
- Truncate middle levels on mobile if depth > 4 levels
- `aria-label="Breadcrumb"` on `<nav>`; `aria-current="page"` on current level

### Pagination

| Pattern | Use |
|---|---|
| Page numbers (1, 2, 3...) | < 20 pages; user needs to jump to a specific page |
| Previous / Next only | When total count is unknown or very large |
| Load more button | Append to list; preserves scroll position |
| Infinite scroll | Automatic; but must have footer footer accessible and "back to top" available |

Spec must declare: which pagination pattern and why.

## Form components

### Text input

```html
<div class="form-field">
  <label for="name" class="label">
    Full name
    <span aria-hidden="true" class="required-indicator">*</span>
  </label>
  <input 
    id="name" 
    type="text" 
    name="name"
    required
    autocomplete="name"
    aria-describedby="name-hint name-error"
    aria-invalid="true"  <!-- only when invalid -->
  >
  <p id="name-hint" class="hint">Enter your legal name as it appears on your ID.</p>
  <p id="name-error" class="error" role="alert">Please enter your full name.</p>
</div>
```

- Always use `autocomplete` for standard fields (name, email, address, cc-number)
- `type` attribute matches the expected input (email, tel, url, number, date)
- Placeholder: hint text only (disappears on input); never a replacement for the label
- Error on blur (not on keystroke) — less disruptive

### Select / Dropdown

When to use Select vs Combobox:
- Select: ≤ 7 options; no search needed; options are well-known
- Combobox (searchable): > 7 options; options may be unknown to user

Custom dropdowns must be keyboard accessible:
- Arrow keys navigate options
- Enter or Space selects
- Escape closes
- Type-ahead search: pressing "C" jumps to first option starting with "C"

### Checkbox vs Radio vs Toggle

| Component | Use when |
|---|---|
| Checkbox | Multiple selection from a group; or a single on/off |
| Radio | Single selection from a mutually exclusive group (2-6 options) |
| Toggle | Immediate on/off action (settings, features); no confirm needed |
| Select | Single selection from > 6 options |

### Validation patterns

```
Timing:
  On submit:   validate all fields; highlight failures; focus first failure
  On blur:     validate individual field after user leaves it
  On change:   only for password strength and format-heavy fields (phone, card number)
  On type:     only for character count / length indicators
```

Validate server-side always — client validation is UX, not security.

## Feedback components

### Toast / Snackbar

```
Toast placement: bottom-right (desktop), bottom center (mobile)
Duration: 4-6 seconds auto-dismiss
Dismiss: always provide manual dismiss button (keyboard and screen reader accessible)
Limit: maximum 3 toasts visible at once; queue remainder
```

Use toasts for: success confirmations, non-critical errors that do not block workflow.
Do not use toasts for: errors that require user action, important information users need to retain.

### Modal / Dialog

```
Trigger: user action (never auto-open on page load)
Focus: trap focus within modal while open; move focus to modal on open
Close: Escape key + close button + backdrop click (optional; not for forms with data)
Return: focus returns to trigger element on close
Scroll: body scroll locked while modal is open
```

ARIA requirements:
```html
<div role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <h2 id="modal-title">Confirm deletion</h2>
  <!-- content -->
</div>
```

### Alert / Banner

- **Informational** (blue): provides context; no action required
- **Success** (green): confirms completed action
- **Warning** (amber): warns of potential issue; may need action
- **Error** (red): reports failure; usually requires action

Use `role="alert"` for dynamically injected error banners (screen reader announces immediately).
Use `role="status"` for success messages (less urgent; screen reader announces when available).
