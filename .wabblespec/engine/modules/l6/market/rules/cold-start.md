# Cold-Start Behavior — Market

Defines what Market does when its positioning data or execution plan inputs are absent.

## Absent: product context

Condition: Market invoked without declared product, target market, or value proposition.
Action: Surface: "Market requires product context: what does the product do, who uses it, and what problem does it solve?"
Do NOT: Generate marketing content without a declared value proposition.

## Absent: rule files

Condition: `rules/execution-planning.md` or `rules/positioning-framework.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md positioning and planning rules. Log: "Market rule file missing — using SKILL.md defaults."

## Absent: competitor context

Condition: Positioning analysis requested but no competitor information provided.
Detection: No competitive landscape in spec or invocation.
Action: Surface: "Positioning requires competitor context. List known competitors and their primary differentiators."
Do NOT: Fabricate competitor names or claims.

## Absent: channel declaration

Condition: Execution plan requested but no distribution channels declared.
Action: Surface: "Which channels are in scope? (e.g., product page, blog, social, email, press, developer docs)"

## Default state on cold start

| Field | Default |
|---|---|
| `product_stage` | Not declared — must specify (pre-launch / launch / post-launch / growth) |
| `audience` | Not declared — must specify (developers / end users / enterprise / both) |
| `tone` | Not declared — must specify (technical / approachable / bold / neutral) |
| `claims_policy` | Verified only — no unsubstantiated performance claims |
| `review_required` | true — marketing content requires human review before publication |
