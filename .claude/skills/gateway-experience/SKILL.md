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
| Pre-research design quality gate (5-dim critique) | No | Yes |
| Anti-slop intentionality audit before user exposure | No | Yes |

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
1. Run pre-research design quality gate (5-dim critique — see below)
2. Load user-research.md
3. Load usability-testing.md
4. Load accessibility-deep-dive.md
5. Load satisfaction-measurement.md
6. Load research-ethics.md
7. Register audit-gates.md with Verifier
8. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

## Playwright Live Verification (optional — Playwright MCP only)

When the `playwright` MCP server is active and the deliverable is a web UI, run the 5-dimension critique against a live browser render rather than a static mockup:

1. `playwright_navigate` to the deliverable URL
2. Capture screenshots at: initial load, hover states, mobile viewport (375px), form interaction, error state
3. Score each of the 5 critique dimensions against the screenshots rather than design files
4. Capture each screenshot path as evidence in the gateway receipt under `live_evidence[]`

Screenshot evidence is Tier 1 evidence (see verifier Evidence Hierarchy) — it overrides design-file-based dimension scores when they conflict.

When Playwright MCP is unavailable: run the 5-dim critique against design artifacts as before. Record `playwright_verified: false` in the gateway receipt.

See `engine/shared/references/mcp-servers-integration.md` → Playwright section for call patterns.

## Reference Routing

| Situation | Reference |
|---|---|
| experience receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type gateway-spec` / `gateway-verdict` (two-phase) |
| Playwright live verification call patterns | `engine/shared/references/mcp-servers-integration.md` → Playwright section |

## Output contract

- Pre-research design quality gate (5-dim critique score with any dimension below 3/5 blocking)
- Research method and cadence compliance check
- Usability test scenario and metrics audit
- Accessibility deep-dive matrix (screen reader, color blindness, cognitive, motor)
- Satisfaction measurement coverage check
- Research ethics compliance check
- Research insights written to Memory as FRESH drawers
- Gateway activation receipt with all gate results

## Phase B audit gates

### Pre-research design quality gate (5-dimensional critique)

Before research participants see any deliverable, score the design across five dimensions. This gate runs as Phase B step 1. Any dimension scoring below 3/5 blocks the gateway until resolved — users must not validate a design that is generically defaulted or structurally incoherent.

| Dimension | Question | Score 1–5 |
|---|---|---|
| Philosophy | Is the visual stance coherent with the brief and the declared style? Or is it generic? | |
| Hierarchy | Does each view have a single declared dominant element? Is reading order obvious? | |
| Detail | Do motion, ease, and duration choices match the declared mood? Or are they defaulted? | |
| Function | Do all flows complete end-to-end without structural gaps? Do interactions match platform conventions? | |
| Innovation | Is there at least one moment that is specific to this product — not generic AI output? | |

Scoring guide: 5 = fully resolved, no hedging. 4 = resolved with minor gaps. 3 = acceptable baseline. 2 = significant gap, needs work. 1 = not addressed.

Gate condition: all five dimensions must score 3 or above. Any dimension below 3 blocks this gate and returns a FLAG verdict with the specific gap stated. Two rescore passes are allowed before an Attestation is required.

### Anti-slop intentionality audit

Before participant exposure, verify that design deliverables were built from actual product content decisions — not AI defaults. Check:

- All copy is product-specific, not placeholder filler
- Color and typography choices are documented to a stated rationale, not memory-defaulted
- Layout patterns are chosen for this content, not applied uniformly
- Any instance of a generically defaulted pattern (uniform card grids, centered everything, gradient text without rationale) has a documented decision

This audit does not require all defaults to be eliminated — it requires all defaults to be intentional. An undocumented default is a FLAG item. A documented default with a rationale is a PASS.

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
