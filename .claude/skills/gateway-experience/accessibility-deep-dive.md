# Accessibility Deep-Dive

Design gateway sets the accessibility floor (WCAG 2.1 AA). This module verifies the floor is actually met — not just that code claims to meet it.

## Screen Reader Testing Matrix

Declared per project — targets the platforms the product serves:

| Platform | Screen reader |
|---|---|
| macOS | VoiceOver |
| iOS | VoiceOver |
| Windows | NVDA (free) or JAWS (enterprise) |
| Android | TalkBack |
| Web (cross-platform) | At minimum: VoiceOver + NVDA |

Screen reader + browser combination matters. High-priority combinations for web: VoiceOver + Safari, NVDA + Chrome, JAWS + Chrome. Matrix declared in spec.

## Cognitive Accessibility

- Plain language: Flesch-Kincaid reading ease score targeted for audience (guideline, not strict requirement)
- Consistent navigation: nav structure identical across pages — no surprise changes
- No time limits without extension: timed operations offer extension option (WCAG 2.1 AA)
- Error prevention: irreversible actions have confirmation step; form inputs have review step before submission
- Clear instructions: instructions don't rely solely on sensory characteristics ("click the blue button" fails; "click the Submit button" passes)

## Color Blindness Testing

Tested with deuteranopia simulation (red-green — most common). Additional simulations declared if broader coverage required:

| Type | Prevalence | Simulation tool |
|---|---|---|
| Deuteranopia | ~6% males | Browser DevTools, Figma, Stark |
| Protanopia | ~2% males | Same tools |
| Tritanopia | Rare | Same tools |

All informational content distinguishable without color alone. Color reinforces meaning — never the sole carrier of meaning.

## Motor Accessibility

Scope declared in spec — required when product serves users with motor impairments:

| Capability | What is tested |
|---|---|
| Switch access | Single-switch scanning navigation works |
| Voice control | Dragon NaturallySpeaking / Voice Control commands work on all interactive elements |
| Keyboard-only | Full operation without mouse (Design gateway baseline — verified here) |
| Pointer size | Minimum 44x44px targets (Design gateway requirement — verified here) |

## Audit Gates

- [ ] Screen reader testing matrix declared in spec
- [ ] At minimum VoiceOver + NVDA tested for web targets
- [ ] Color blindness tested with deuteranopia simulation
- [ ] All informational content distinguishable without color
- [ ] No time limits without extension option
- [ ] Instructions don't rely solely on sensory characteristics
- [ ] Motor accessibility scope declared (in or out of scope)
