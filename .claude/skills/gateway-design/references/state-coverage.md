# Design Gateway — State Coverage Reference

Interactive component state requirements and input-state discipline.

## 8-State Requirement

Every interactive component (button, input, select, toggle, checkbox, radio, tab, chip, link with action) ships with explicit styling for all 8 states:

| State | Trigger | Notes |
|---|---|---|
| default | No interaction | The resting state; all other states derive from this |
| hover | Cursor over element | Enhancement only — touch users must not lose function |
| :focus-visible | Keyboard focus | Must appear instantly; no transition; 2px outline minimum |
| :active | During press | Brief; confirms physical interaction; often a scale-down or darken |
| disabled | `disabled` attr or `aria-disabled="true"` | Three independent signals required (see below) |
| loading | `data-state="loading"` or equivalent | Spinner or skeleton; element non-interactive during this state |
| error | `data-state="error"` or `aria-invalid="true"` | Color + icon + text label; not color alone |
| success | `data-state="success"` | Silent for visible effects; toast only for async or non-visible results |

Unspecified states ship with browser defaults — which are often wrong. The gate requires explicit declaration, not inheritance.

### State demo wrapper

For any component with 3+ states that differ visually, produce a `preview.html` that renders all states stacked and labelled. The user opens it once, confirms all states look correct, then discards it.

```html
<!-- State preview wrapper pattern -->
<div style="display:grid; gap:16px; padding:24px">
  <div data-state-label="default">     <!-- render component in default state --></div>
  <div data-state-label="hover">       <!-- render component with :hover class applied --></div>
  <div data-state-label="focus">       <!-- render component with :focus-visible class --></div>
  <div data-state-label="active">      <!-- render component with :active class --></div>
  <div data-state-label="disabled">    <!-- render component with disabled attribute --></div>
  <div data-state-label="loading">     <!-- render component with data-state="loading" --></div>
  <div data-state-label="error">       <!-- render component with data-state="error" --></div>
  <div data-state-label="success">     <!-- render component with data-state="success" --></div>
</div>
```

---

## Input-State Discipline

### Border-width stability

`border-width` must NOT change between states. Default, hover, focus, and error states all hold the same border width (typically 1px).

**Why.** A border-width change shifts the element's box geometry by 1px, nudging adjacent layout. On a form with multiple inputs, this produces a visible shudder as the user tabs through fields.

**Correct focus ring approach:**

```css
/* Reserve 2px outline in default to prevent geometry shift on activate */
input {
  border: 1px solid var(--color-neutral-300);
  outline: 2px solid transparent;
  outline-offset: 1px;
}

input:focus-visible {
  outline-color: var(--color-accent);
  border-color: var(--color-accent);  /* border-width stays 1px */
}

input[aria-invalid="true"] {
  border-color: var(--color-error);   /* border-width stays 1px */
}
```

### Focus ring: outline not border

The focus ring uses `outline`, not `border`. Using `border` for focus rings changes element geometry (see above). Using `outline` leaves geometry unchanged.

```css
/* Correct */
:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 1px; }

/* Wrong */
:focus-visible { border: 2px solid var(--color-accent); }
```

Focus rings must appear instantly — do not `transition` the `outline` property.

### Input height alignment

An input and its adjacent submit button on the same form must share the same computed height. The floor is 44px (touch target minimum). Mismatched heights produce a misaligned row that reads as an assembly error.

### Helper text slot reservation

The container for helper text, character count, or error message reserves vertical space even when empty:

```css
.field-helper {
  min-height: 1lh;  /* reserves one line's height; prevents layout jump on validation */
}
```

Without this, the form jumps in height when an error message appears, shifting the submit button position mid-interaction.

### Disabled state: three independent signals

A disabled interactive element requires all three of the following simultaneously:

1. `opacity: 0.55` (visual dimming)
2. `cursor: not-allowed` (cursor feedback)
3. Native `disabled` attribute OR `aria-disabled="true"` (programmatic signal to assistive technology)

One or two signals alone is insufficient. `opacity: 0.55` without `cursor: not-allowed` is ambiguous. `cursor: not-allowed` without `aria-disabled` is invisible to screen readers.

---

## Hover vs Focus Tooltip Timing

Hover-triggered tooltips and focus-triggered tooltips serve different intents and must use different delays.

| Trigger | Delay | Why |
|---|---|---|
| `:hover` | 800-1000ms | Prevents tooltips firing on mouse-transit; user must pause to indicate intent |
| `:focus-visible` | 0ms | Keyboard users navigated to the element deliberately; delay would be disorienting |

Never use the same delay for both. A 0ms hover delay fires on every mouse-over. An 800ms focus delay punishes keyboard users.
