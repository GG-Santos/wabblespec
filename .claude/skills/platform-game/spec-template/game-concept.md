# Game Concept Template (P0)

> **Platform:** Game | **Phase:** P0 — complete before any other game spec.
> Sections marked `[REQUIRED]` must be filled before Specify receipt.
> This document is the design authority. Decisions that conflict with declared pillars escalate — they do not override silently.

---

## Elevator Pitch [REQUIRED]

One sentence: genre + core verb + setting + player count.

> Example: "A co-op puzzle platformer where two players control the same character from different time points."

---

## Game Pillars [REQUIRED]

Declare 2–4 pillars. Each pillar must be **falsifiable** — a real design decision must be able to fail it.
Vague pillars ("fun", "immersive") are not pillars. If a decision can never violate it, it carries no weight.

### Pillar 1: [Name]

**Definition:** One sentence stating what this pillar demands of every design decision.

**Falsifiability test:** "This design would fail Pillar 1 if it [concrete failure condition]."

**Anti-pillar:** The opposite of this pillar that we explicitly reject. ("We do not make a game that [opposite behavior].")

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

### Pillar 4: [Name] *(optional)*

**Definition:**

**Falsifiability test:**

**Anti-pillar:**

---

## Player Fantasy [REQUIRED]

One paragraph. Not "what the player does" — what the player **feels** during the core loop.
Target adjectives: what words should a player use when describing the game to a friend after 10 minutes?

> Example: "Players feel like a ghost detective — powerful enough to know everything, helpless enough that knowledge alone can't save anyone. Every reveal should produce dread alongside understanding."

**Target adjectives (2–4 words the player should use):** ___, ___, ___

---

## Core Loop [REQUIRED]

The minimum repeating cycle that delivers the player fantasy. Use verb → object → reward → repeat.

```
[Verb] ──→ [Object/Challenge] ──→ [Reward/Feedback] ──→ [Return to start]
  │                                                              │
  └──────────────── repeat until session end ───────────────────┘
```

**Micro loop** (seconds): ___
**Macro loop** (minutes): ___
**Meta loop** (session/day): ___

---

## Unique Hook [REQUIRED]

Complete this sentence: "Like [closest comparable game], AND ALSO [the thing that differentiates us]."

> Example: "Like Celeste, AND ALSO your deaths replay as ghost enemies you must navigate around."

This hook must map to at least one Pillar. If it doesn't touch a pillar, it is not the hook — it is a feature.

**Hook maps to:** Pillar ___

---

## Scope Tiers [REQUIRED]

Declare what ships at each cut point. Assume you will run out of time. Each tier must be a shippable, coherent game — not a broken fragment of the full vision.

| Tier | Description | Ships if... | Core loop intact? |
|---|---|---|---|
| **MVP** | Minimum playable product | Time or budget runs out | Yes |
| **Vertical Slice** | Polished end-to-end demo of core loop | Pre-production validation | Yes |
| **Alpha** | All systems present, rough | Alpha milestone hit | Yes |
| **Full Vision** | Complete as designed | Full schedule delivered | Yes |

**MVP must include:** (list the minimum features that make the core loop playable)

---

## Comparable Games

| Game | What we share | What we do differently |
|---|---|---|
| [Title] | [Mechanic/feel] | [Differentiator] |
| [Title] | [Mechanic/feel] | [Differentiator] |

---

## Target Platform & Audience

**Primary platform:** ___
**Target player:** One sentence (experience level, play style, session length)
**Session length target:** ___ minutes (casual) / ___ minutes (engaged)
**Age rating target:** ESRB ___ / PEGI ___

---

## GWT Acceptance Scenarios

```
Given: a player has played for 10 minutes
When: asked to describe the game to a friend
Then: they use at least 2 of the declared target adjectives
      AND they can state the core loop in one sentence

Given: a design decision is proposed that contradicts Pillar 1
When: evaluated against the falsifiability test
Then: the violation is named and documented before any decision is made
      AND the decision either revises the pillar or changes the design — not both silently

Given: development time runs out at MVP tier
When: the build is evaluated for shippability
Then: the core loop is intact and playable
      AND at least one Pillar is experientially present
```

---

## Open Questions

List decisions that are unresolved and blocking. Specify receipt blocked until REQUIRED sections complete and open questions either resolved or explicitly deferred with a rationale.
