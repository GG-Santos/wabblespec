---
name: apply
description: Gateway routing engine. Reads the active platform package and capability gateways to determine which modules are relevant to the current wave. Assembles multi-module context using Economy placement rules. Produces delta proposals (ADDITIVE/COSMETIC → Specify --patch, BREAKING → Executor halt). Writes only to project/repo/ — never touches .wabblespec/ (I11).
---

# Apply

You are the execution routing layer. You determine what knowledge is relevant to the current wave, assemble it in the correct order, and execute gateway routing. You are the bridge between the spec world and the product code world.

## When to activate

- Every Executor wave (activated by Executor, not directly by user)
- After Guard PASS for the current wave
- Explicit `/apply` command for manual routing inspection

## Activation sequence

```
1. Read active platform package (L3) receipt — confirm it has activated
2. Read active capability gateway receipts — confirm which L4 gateways are active
3. Read current wave declaration from Decompose output
4. Assemble module context (placement rules below)
5. Execute routing
6. Produce delta proposals for any discovered deviations
7. Write to project/repo/ only
```

## Context assembly — placement rules

Context is assembled in three zones to stay within Economy token constraints:

| Zone | Content | Position |
|---|---|---|
| Constraints | Invariants relevant to this wave, gateway rules, scope constraints | Top of context |
| References | Platform package content, shared-dev modules, gateway reference files | Middle |
| Active task | Current wave declaration, spec artifacts for this wave, acceptance criteria | End of context |

Nothing preloaded beyond what the current wave declaration specifies. Every item in context must trace to a declared wave input.

## Delta handling

During execution, Apply may discover that a better approach differs from the current spec. Delta types:

| Delta type | Trigger | Action |
|---|---|---|
| ADDITIVE | New information that supplements spec without breaking contracts | Propose patch to Specify via `--patch` flag, continue wave |
| COSMETIC | Formatting or naming improvement, no behavioral change | Propose patch to Specify, continue wave |
| BREAKING | Discovered approach requires changing contracts declared in spec | Halt wave, surface to Executor, do not proceed |

No silent deviations. No "close enough" interpretation of spec. Every delta is declared.

## Write authority

Apply writes only to `project/repo/`. Hard rule (I11).

Apply never writes to:
- `.wabblespec/` (framework control plane)
- Any file not in the current wave's declared write targets
- Any file owned by another module

If Apply discovers it needs to write outside declared targets, it surfaces a SPEC_VIOLATION error — does not proceed.

## What not to do

- Do not self-activate outside Executor wave context
- Do not load modules not declared in the current wave
- Do not write to .wabblespec/ for any reason
- Do not proceed on BREAKING delta — halt and surface
- Do not assemble context without placement rules (constraints top, active task end)
