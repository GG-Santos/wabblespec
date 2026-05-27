# Game Economy Model Template

> **Platform:** Game | **Conditional load:** activate only if monetization or virtual economy declared in game-concept.md.
> **Prerequisites:** game-concept.md scope tiers complete; systems-index.md economy system listed.
> Sections marked `[REQUIRED]` must be filled before Specify receipt if this file is loaded.

---

## Economy Overview [REQUIRED]

One paragraph: what economic systems exist in this game, what they serve (player progression, engagement, monetization), and whether real money is involved.

**Economy type:** [ ] Pure progression (no real money) [ ] Cosmetic monetization [ ] Pay-to-progress [ ] Battle pass [ ] Full free-to-play

---

## Currency Registry [REQUIRED if any currency exists]

Declare every currency before implementing any. Undeclared currencies added mid-development create sink/faucet imbalance.

| Currency | Type | Purpose | Display format | Max balance | Can be purchased? |
|---|---|---|---|---|---|
| [Name] | Hard (real money) / Soft (earned) / Premium (event-only) | [What it buys] | `1,000` / `1.0k` | ___ or unlimited | Yes / No |

**Inflation control:** If soft currency has no hard cap, declare the daily maximum earn rate. Uncapped earn with no sinks = inflation = devalued rewards.

---

## Faucets — How Currency Enters [REQUIRED]

Every source of currency must be declared. Undeclared sources are economy exploits waiting to happen.

| Source | Currency | Amount | Frequency | Caps | Notes |
|---|---|---|---|---|---|
| Match completion | Soft | ___ | Per match | Max ___ per day | Scales with performance? |
| Daily login | Soft | ___ | Once per 24h | 1× per day | Day-streak bonus? |
| Quest completion | Soft / Hard | ___ | Per quest | One-time per quest | |
| Real money purchase | Hard | Varies | Unlimited | None | Platform fee applies |
| Event reward | Premium | ___ | Per event | Event duration | |

**Total daily soft currency earn (no-cap scenario):** ___ (sum of all uncapped daily faucets)
**Balance check:** Is this earn rate fast enough to feel rewarding? Too fast = devalued. Declare target days-to-first-major-purchase: ___

---

## Sinks — How Currency Leaves [REQUIRED]

A faucet-only economy is inflationary. Every currency needs sinks.

| Sink | Currency | Cost | Player motivation | Repeatable? |
|---|---|---|---|---|
| Item purchase | Soft | ___ | Progression / cosmetic | Yes / No |
| Crafting | Soft | ___ | Progression | Yes |
| Gacha / loot | Hard | ___ | Excitement, collection | Yes |
| Battle pass | Hard | ___ | Season progression | Per season |
| Entry fee (if applicable) | Soft | ___ | Access to mode | Per match |

**Sink/faucet balance:** Total per-day sinks available to an engaged player ≥ 80% of total per-day faucets. If sinks < faucets, excess currency accumulates and devalues rewards over time.

---

## Loot Tables [REQUIRED if gacha or randomized rewards exist]

| Table Name | Trigger | Item Pool | Weight system | Pity system |
|---|---|---|---|---|
| [Table] | [When triggered] | [Items in pool] | Uniform / Weighted | Yes: guaranteed at N pulls / No |

**Per item in each table:**

| Item ID | Rarity | Base weight | Floor probability | Notes |
|---|---|---|---|---|
| [item_id] | Common / Rare / Epic / Legendary | ___ | ___% min | |

**Pity system declaration:** If pity exists, state: after ___ pulls without [rarity], probability increases to ___% per subsequent pull, guaranteed at pull ___.

**Duplicate handling:** [ ] Currency refund [ ] Crafting material [ ] Allowed (player collects multiples) [ ] Not applicable

---

## Progression Curve [REQUIRED if XP or level system exists]

**XP formula:**

```
XP required for level N: [formula]
Examples:
  Linear:       XP(N) = base × N
  Quadratic:    XP(N) = base × N²
  Exponential:  XP(N) = base × growth_rate^N
  Piecewise:    XP(N) = [different formula per level band]
```

**Level unlock gates:**

| Level | Unlock |
|---|---|
| 1 | [Feature] |
| ___ | [Feature] |

**Player-time model:** Target days from start to max level for an engaged player (2 sessions/day): ___

---

## Economy Health Invariants

These must hold at all times. Gate 12 (content completeness) checks the content counts; Executor must verify these invariants before closing any economy implementation wave.

1. **No item duplicatable via transaction ordering.** All economy operations are atomic on the server (see security/platform-controls.md Control 3). No partial-success state.
2. **Sink ≥ faucet** for all engaged-player scenarios, or inflationary intent is explicitly documented.
3. **Maximum daily earn rate declared** for all soft currencies. Any source without a declared cap is a bug until documented.
4. **Pity counter persists across sessions.** Closing the game must not reset a pity counter.
5. **All prices declared in spec before implementation.** No hardcoded prices in code — all prices live in data files.

---

## GWT Acceptance Scenarios

```
Given: a player attempts to purchase an item with insufficient balance
When: the transaction is submitted to the server
Then: the server rejects the transaction before deducting any balance
      AND the player's balance remains unchanged
      AND the item is not granted

Given: a player closes the game at pull N-1 before a pity threshold
When: they reopen the game and pull again
Then: the pity counter is at N (not reset)
      AND the pull correctly calculates odds from the persisted counter

Given: a soft currency faucet is exploited (e.g., quest repeated via bug)
When: the earn from that source in one day is audited
Then: the actual earn does not exceed declared daily cap × declared max repetitions
      AND any excess is identified by the server audit log

Given: the economy model is reviewed at Alpha
When: a typical engaged player's 7-day earn and spend is simulated
Then: the player has positive surplus (not bankrupt by day 7)
      AND the player has not accumulated so much currency that new content feels underpriced
```

---

## Open Questions

Unresolved pricing, loot weights, or progression curve parameters go here. Specify receipt blocked if any REQUIRED section is incomplete when economy system is in scope.
