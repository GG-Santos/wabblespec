# Context Engineering

Context window best practices for WabbleSpec modules. Consumers: executor, autopilot, economy, model-router.

## Context is a finite resource

A context window is not infinite. Every token loaded is a token not available for output or reasoning. Context engineering is the discipline of loading the right information at the right moment.

## What to load (signal)

| Priority | Content type | When to load |
|---|---|---|
| P1 | Current task card | Always — defines the work |
| P1 | Active wave plan | Always — defines the step |
| P1 | Error text (exact) | Always when error exists |
| P2 | Receipts from prior waves | When verifying cross-wave continuity |
| P2 | Spec artifacts (EARS requirements) | When implementing or verifying |
| P3 | Reference files | Only when directly needed |
| P4 | Historical drawers | Only when cross-session context is required |

## What not to load (noise)

- Full file contents when only a section is needed
- Prior completed waves' full output (receipts sufficient)
- Reference files speculatively ("might be useful")
- Entire SKILL.md of a module when only one step is relevant
- Search results beyond top 3 relevant matches

## Context placement rules

### System context (persistent across turns)
Framework invariants, guard-policy.md, active task card. Load once at session start. Use prompt caching if available.

### Working context (per-wave)
Current wave plan, prior wave receipts, active spec artifacts. Load at wave start. Clear non-essential items between waves.

### On-demand context (load when needed, drop after)
Reference files, Memory drawers, search results. Load for the specific step that needs them. Do not carry forward.

## KV-cache strategy

If runtime supports prompt_caching:
1. Place system context + invariants in the cacheable prefix
2. Place task card immediately after (cache-warm after first turn)
3. Place working context after task card (cache-warm within session)
4. Place on-demand context last (not cached — changes per request)

Cache misses reset position 3 and below. Keep positions 1 and 2 stable.

## Context rot detection

Context is "rotting" when:
- The same information appears in multiple forms (original + summary + receipt)
- Prior wave outputs are still fully present when only their receipts are needed
- Reference files loaded 5+ turns ago with no subsequent use

Rotting context → apply progressive-disclosure.md remediation: summarize to receipt, drop full content.

## Wave isolation

Each wave starts with minimal context. Do not carry a prior wave's full output into the next wave. Instead: write a receipt, then load only the receipt in the next wave. This prevents context from growing monotonically.
