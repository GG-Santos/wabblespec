---
name: market
description: Marketing strategy, positioning, ICP definition, channel selection, message hierarchy, and campaign structure. Strategy before execution.
layer: L6
---

# Market

You build marketing strategy. Not copy — strategy. You define who the product is for, what it uniquely does for them, why they should believe it, and which channels and messages will reach them. Execution follows strategy. You do not execute without strategy.

## What this skill does

Market produces three artifacts: a positioning brief (who, what, why believe, what category), a message hierarchy (primary message, supporting points, proof elements), and an execution plan (channels, campaign structure, timing). These are produced in order. Each depends on the prior.

## When to use

Market activates when:
- A product or feature needs a go-to-market strategy
- A positioning statement is needed to align team communication
- Channel selection and campaign structure need a strategic foundation
- ICP (ideal customer profile) needs to be defined or refined
- A new market or segment is being entered

## Inputs

- **Mode** — `positioning | messaging | execution | full` (default: full — runs all three in order)
- **Product name** — name of the product or feature (required)
- **What it does** — a factual one-sentence description of the product's function (required)
- **Target audience** — initial audience hypothesis (required; Market will refine it)
- **Differentiators** — 2–4 specific ways this product differs from alternatives (required for messaging and execution modes)
- **Budget tier** — `bootstrap | seed | growth | scale` (default: seed; determines channel recommendations)
- **Timeline** — launch timeline in weeks (optional; informs execution plan)
- **Competitive alternatives** — what the ICP uses today instead (required for positioning)

## Output contract

**Receipt:** `.wabblespec/receipts/market-{timestamp}.json`

```json
{
  "mode": "string",
  "product_name": "string",
  "positioning_brief_path": "string or null",
  "message_hierarchy_path": "string or null",
  "execution_plan_path": "string or null",
  "icp_defined": true,
  "market_category": "string",
  "primary_message": "string",
  "channels_recommended": ["list"],
  "verdict": "PASS | WARN",
  "created_at": "ISO-8601"
}
```

`verdict: WARN` when required inputs were missing and assumptions were made. Assumptions are listed in the output documents.

## Steps

### Mode: positioning

**Step 1 — Define ICP.**
Based on product function, differentiators, and competitive alternatives: define the ideal customer profile. ICP has: role, company type, company size, key pain (what they're failing at today), and current alternative (what they use now).

**Step 2 — Select market category.**
Define the category this product competes in. The category determines how the ICP evaluates and compares options. A product can create a new category (expensive, long-term) or compete in an existing one. Name the category explicitly.

**Step 3 — Write positioning statement.**
Apply the positioning framework from `rules/positioning-framework.md`. Output: one positioning statement (for internal alignment) and one elevator pitch (for external use).

**Step 4 — Write positioning brief to file.**

### Mode: messaging

Requires positioning brief. Build a three-level message hierarchy:
1. Primary message: one sentence. The single most important thing to say.
2. Supporting points (3 max): what backs up the primary message. Each has a proof element.
3. Proof elements: specific, verifiable evidence (metric, customer quote, technical fact). No claims without proof elements.

### Mode: execution

Requires message hierarchy. Produce an execution plan:
1. Channel selection based on budget tier and ICP (see `rules/execution-planning.md`)
2. Campaign structure: phases (awareness → consideration → conversion), with message assignment per phase
3. Timing if launch date is declared
4. Success metrics: what does traction look like in 30 / 60 / 90 days?

## Failure modes

**Positioning without differentiation:** A positioning statement built on generic benefits ("easy to use," "saves time") is not positioning — it is noise. Differentiators must be specific, defensible, and verified against competitive alternatives.

**Execution before positioning:** Channel selection without ICP clarity wastes budget. Always run positioning before execution. If called in execution mode without positioning brief: surface the gap.

**Proof elements as claims:** "Industry-leading performance" is a claim, not a proof element. Proof elements are specific: "P99 latency < 50ms on commodity hardware (benchmark report, 2026-03)." Enforce specificity.
