# Motion Standards

## Motion Principles

Two categories:

**Purposeful motion** — communicates state change, relationship, or action outcome. Examples: element entering/leaving, state transition, loading progress.

**Decorative motion** — visual enhancement without functional communication. Requires justification if included — not prohibited, but must earn its place.

## Reduced Motion (non-negotiable)

`prefers-reduced-motion: reduce` respected for all motion. No exceptions.

```css
@media (prefers-reduced-motion: reduce) {
  /* all transitions/animations set to 0ms or instant */
}
```

Where motion communicates state (loading indicator, progress), provide a non-motion alternative (text status, static indicator).

## Duration Tokens

```
--duration-instant:  0ms
--duration-fast:     150ms
--duration-normal:   250ms
--duration-slow:     350ms
--duration-slower:   500ms
```

UI transitions: `--duration-fast` to `--duration-normal` (150ms–250ms). Page transitions: `--duration-normal` to `--duration-slow`. No inline duration values — token references only.

## Easing Tokens

```
--easing-standard:   cubic-bezier(0.4, 0, 0.2, 1)
--easing-enter:      cubic-bezier(0, 0, 0.2, 1)
--easing-exit:       cubic-bezier(0.4, 0, 1, 1)
--easing-linear:     linear
```

No inline cubic-bezier values in component code — token references only.

## Audit Gates

- [ ] `prefers-reduced-motion: reduce` handled for all animations/transitions
- [ ] Non-motion alternative provided for state-communicating motion
- [ ] Duration tokens declared and used (no inline ms values)
- [ ] Easing tokens declared and used (no inline cubic-bezier values)
- [ ] Decorative motion has justification declared in spec
