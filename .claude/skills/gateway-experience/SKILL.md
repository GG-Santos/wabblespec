---
name: gateway-experience
description: Experience capability gateway. Human-side validation for visual-facing projects — user research methods, usability testing, accessibility deep-dives (screen reader matrix, color blindness, cognitive, motor), and satisfaction measurement. Activates on visual targets where user research is declared in scope at P1. Requires explicit activation; Design gateway (accessibility floor) applies unconditionally.
---

# Gateway: Experience

Human-side validation layer. Activates on top of Design and Aesthetic gateways when user research is declared in scope. Where Design declares how flows should work and Aesthetic declares how they should look, Experience validates whether they actually work for real users.

## What this skill does

| Concern | Covered by Design gateway | Covered by L4 Experience gateway |
|---|---|---|
| Accessibility floor (WCAG 2.1 AA) | Yes | — (verified here, declared in Design) |
| User research method selection | No | Yes |
| Usability test scenarios and metrics | No | Yes |
| Screen reader testing matrix | No | Yes |
| Color blindness simulation testing | No | Yes |
| Cognitive accessibility | No | Yes |
| Motor accessibility | No | Yes |
| SUS / NPS / in-product feedback | No | Yes |
| Research ethics (consent, anonymization) | No | Yes |
| Research insights written to Memory | No | Yes |

## When to use

- Visual-facing target with user research declared in scope at P1
- P1 or P4 stage when user validation is declared
- Verifier Demonstration mode for user-facing deliverables
- Explicit `/experience` command

Note: Design gateway (accessibility floor) applies to all visual targets unconditionally. Experience adds research and deep accessibility validation on top — requires explicit scope declaration at P1.

## Activation sequence

### Phase A (Specify time — knowledge injection)

```
1. Confirm Design gateway has activated and written its receipt
2. Confirm user research declared in scope at P1
3. Load references/ directory into Specify context:
   - references/wcag.md (WCAG 2.1 AA full requirements, testing approach)
   - references/platform-ux.md (iOS HIG, Material Design, Windows Fluent, terminal UX)
4. Write gateway-spec-receipt (Phase A)
```

### Phase B (pre-Executor — verdict)

```
1. Load user-research.md
2. Load usability-testing.md
3. Load accessibility-deep-dive.md
4. Load satisfaction-measurement.md
5. Load research-ethics.md
6. Register audit-gates.md with Verifier
7. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

## Output contract

- Research method and cadence compliance check
- Usability test scenario and metrics audit
- Accessibility deep-dive matrix (screen reader, color blindness, cognitive, motor)
- Satisfaction measurement coverage check
- Research ethics compliance check
- Research insights written to Memory as FRESH drawers
- Gateway activation receipt with all gate results

## Files loaded by this module

```
modules/l4/experience/
  user-research.md
  usability-testing.md
  accessibility-deep-dive.md
  satisfaction-measurement.md
  research-ethics.md
  audit-gates.md
```
