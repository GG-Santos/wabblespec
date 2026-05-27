# Aesthetic Gateway — Motion Reference

Animation principles, timing standards, and prefers-reduced-motion requirements.

## Motion principles

Motion must serve a purpose. Every animation must answer: what does this motion communicate?

### The four purposes of motion

1. **Continuity**: show relationship between states (elements that move together belong together)
2. **Feedback**: confirm user action (button press, form submission, loading)
3. **Focus**: direct attention to what matters (new content, error, notification)
4. **Delight**: make interactions feel alive (used sparingly — not as a default)

Motion that serves none of these purposes should be removed.

## Timing standards

```yaml
motion_tokens:
  instant:
    duration: 50ms
    usage: "Immediate state changes (checkbox tick, toggle)"
    
  fast:
    duration: 100-150ms
    usage: "Hover states, focus rings, small UI feedback"
    
  normal:
    duration: 200-300ms
    usage: "Most transitions — modals entering, panels sliding, tooltips appearing"
    easing: "ease-out (enters fast, settles)"
    
  slow:
    duration: 400-500ms
    usage: "Complex transitions — page transitions, hero animations"
    easing: "ease-in-out"
    
  deliberate:
    duration: 600ms+
    usage: "Onboarding, success states — used sparingly"
```

### Easing guide

| Easing | CSS | Feel | Use |
|---|---|---|---|
| ease-out | `cubic-bezier(0, 0, 0.2, 1)` | Enters fast, settles | Elements entering the screen |
| ease-in | `cubic-bezier(0.4, 0, 1, 1)` | Slow start, fast exit | Elements leaving the screen |
| ease-in-out | `cubic-bezier(0.4, 0, 0.2, 1)` | Symmetric | Elements moving between positions |
| linear | `linear` | Mechanical | Spinners, progress bars |
| spring | Custom (Framer Motion, react-spring) | Natural | Interactive drag, physics-based |

Never use the browser default `ease` (`cubic-bezier(0.25, 0.1, 0.25, 1)`) — it feels generic. Use one of the above with intention.

## prefers-reduced-motion — required

Every animation must respect the user's motion preference:

```css
/* Method 1: CSS media query */
@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: none;
  }
}

/* Method 2: CSS variable approach (preferred) */
:root {
  --transition-normal: 200ms ease-out;
}
@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-normal: 0ms;  /* or a very short, non-animated substitute */
  }
}

/* Method 3: JavaScript */
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const duration = prefersReducedMotion ? 0 : 250
```

Rules:
- **Required**: every animation must be suppressible via `prefers-reduced-motion`
- **Allowed with reduced motion**: instant state changes, non-looping very short transitions (≤ 100ms)
- **Not allowed with reduced motion**: looping animations, parallax effects, large-scale motion

## Loading states

Spec must declare the loading experience for all async operations:

```yaml
loading_patterns:
  instant (< 200ms):
    treatment: "No loading indicator — instant feels synchronous"
    
  short (200ms - 1s):
    treatment: "Spinner or pulse — small, non-distracting"
    
  medium (1s - 3s):
    treatment: "Skeleton screen — layout placeholder that reduces layout shift"
    
  long (> 3s):
    treatment: "Progress indicator with label explaining what is happening"
    
  unknown duration:
    treatment: "Animated spinner + estimated wait time if known; cancel option after 5s"
```

Skeleton screens are preferred over spinners for content-heavy loading (reduces perceived wait time and layout shift).

## Interaction feedback animations

Required feedback animations:

```css
/* Button press feedback */
button:active {
  transform: scale(0.97);
  transition: transform 50ms ease-out;
}

/* Form submission loading */
button[aria-busy="true"] {
  /* spinner inside button; do not remove button text */
}

/* Error shake */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-4px); }
  40%, 80% { transform: translateX(4px); }
}
.error { animation: shake 300ms ease-in-out; }
```

Feedback animations must be under 150ms to feel responsive. Animations that take longer than the action feel punishing.

## What not to animate

- Do not animate color changes for text (hard to read mid-transition)
- Do not animate border-radius on large elements (expensive paint operation)
- Do not loop ambient animations without a pause/stop option
- Do not use animations as a substitute for clear information hierarchy
- Do not autoplay video or animations with sound without user initiation
