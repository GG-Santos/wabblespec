# Product Concept Template (P0)

> **Platform:** Web | **Phase:** P0 — complete before design-document.md.
> Sections marked `[REQUIRED]` must be filled before Specify receipt.
> This document is the design authority for the product. Decisions that conflict with declared pillars escalate — they do not override silently.

---

## Product Statement [REQUIRED]

One sentence: what the product does, who uses it, and what outcome it produces for them.

> Example: "A project tracking tool for engineering teams that replaces status meetings by surfacing blockers automatically."

---

## Product Pillars [REQUIRED]

Declare 2–4 pillars. Each must be **falsifiable** — a design or engineering decision must be able to fail it. Pillars that every product automatically satisfies ("reliable", "fast") are not pillars.

### Pillar 1: [Name]

**Definition:** One sentence stating what this pillar demands of every product decision.

**Falsifiability test:** "This design would fail Pillar 1 if it [concrete failure condition]."

**Anti-pillar:** The product we explicitly refuse to build. ("We do not build a product that [opposite behavior].")

---

### Pillar 2: [Name]

**Definition:**

**Falsifiability test:**

**Anti-pillar:**

---

### Pillar 3: [Name] *(optional)*

**Definition:**

**Falsifiability test:**

**Anti-pillar:**

---

## User Value Proposition [REQUIRED]

Complete this sentence: "Users choose this over [closest alternative] because [specific, demonstrable difference]."

The differentiator must be testable in a user session. If you cannot verify it in a 10-minute user test, it is not a real differentiator — it is a marketing claim.

**Differentiator maps to:** Pillar ___

---

## Primary User [REQUIRED]

One paragraph. Role, context, pain point this product solves, and what success looks like from their perspective.

**Session length target:** ___ minutes (typical) / ___ minutes (power user)
**Technical level:** Non-technical / Technical / Mixed — affects copy, error message depth, empty-state design.
**Device split:** ___ % desktop / ___ % mobile / ___ % tablet (affects layout priority)

---

## Scope Tiers [REQUIRED]

Every tier must be a shippable, usable product — not a fragment. Declare what is cut at each tier.

| Tier | Description | Ships if... | Core value delivered? |
|---|---|---|---|
| **MVP** | Minimum that demonstrates core value | Time or budget constraint | Yes |
| **v1** | Polished initial release | Standard launch | Yes |
| **v2** | Expanded feature set | Post-launch iteration | Yes — extended |

**MVP must include:** (list the minimum features that make the product genuinely useful, not just technically functional)

**Explicitly out of MVP:** (what will not be built for MVP — prevents scope creep)

---

## Technical Constraints [REQUIRED]

Constraints known before design begins. These bound the design-document.md decisions.

| Constraint | Value | Reason |
|---|---|---|
| Target browsers | [List] | [User research / business requirement] |
| Must work offline? | Yes / No | [Reason] |
| Authentication provider | [Provider] or "TBD" | [Reason] |
| Backend provided / TBD / to be built | [Status] | [Reason] |
| Existing design system? | [Name] or "None" | [Reason] |
| Accessibility minimum | WCAG 2.1 AA (non-negotiable) | Platform standard |

---

## Comparable Products

| Product | What we share | What we do differently | Risk: user compares us and finds us worse at ___ |
|---|---|---|---|
| [Product] | [Feature/pattern] | [Differentiator] | [Risk area] |

The risk column forces honest evaluation. If a user opens our product alongside the comparable and immediately prefers the comparable, what would that be about?

---

## GWT Acceptance Scenarios

```
Given: a first-time user arrives with no onboarding
When: they spend 5 minutes in the product
Then: they can complete the primary use case without documentation
      AND they can articulate what the product does in one sentence

Given: a design decision is proposed that conflicts with a declared pillar
When: the conflict is identified
Then: the decision is escalated before implementation begins
      AND the resolution either changes the design or revises the pillar — not both silently

Given: development stops at MVP tier
When: the product is evaluated by a user
Then: the core user value proposition is present and functional
      AND no MVP-excluded features are necessary to deliver the declared value
```

---

## Open Questions

Unresolved product decisions blocking spec work. Specify receipt blocked until REQUIRED sections complete.
