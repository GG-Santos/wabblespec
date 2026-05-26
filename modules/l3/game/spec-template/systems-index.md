# Game Systems Index (P1.5)

> **Platform:** Game | **Prerequisite:** game-concept.md complete and pillars locked.
> **Purpose:** Enumerate all game systems, declare their dependencies, and establish implementation order before any GDD is written.
> A system that isn't listed here doesn't get specced. A system specced before its dependencies are listed here causes ordering debt.

---

## System Layers

Systems are assigned to layers. Foundation systems must be stable before Core systems begin. Core before Feature. Feature before Polish.

| Layer | Rule |
|---|---|
| **Foundation** | No game-specific logic. Engine integration, data containers, event bus, serialization. No layer depends downward on Feature or Polish. |
| **Core** | Primary game loop systems. Depends only on Foundation. All Pillar-1 features live here. |
| **Feature** | Secondary systems that extend Core. Can depend on Core, not on each other unless declared. |
| **Polish** | Effects, juice, non-blocking UX improvements. Depends on Core and Feature. Never blocks MVP. |

---

## Systems Registry [REQUIRED]

One row per system. Complete this table before writing any GDD.

| System Name | Layer | Pillar(s) Served | Depends On | Priority Tier | GDD File |
|---|---|---|---|---|---|
| [System] | Foundation / Core / Feature / Polish | Pillar N | [System], [System] | MVP / VS / Alpha / Full | spec pending |
| | | | | | |

**Minimum viable systems for MVP tier:** All MVP-priority systems in the table above. A system not listed as MVP does not block the MVP build.

---

## Dependency Graph

List each system and what it requires to function. Format: `System → requires → [Dependency1, Dependency2]`.

```
[System A] → requires → [none]          (Foundation, no deps)
[System B] → requires → [System A]      (Core, depends on Foundation)
[System C] → requires → [System A, B]   (Feature, depends on both)
```

**Bottleneck systems** (3+ systems depend on this): ___
Bottleneck systems must be specced and implemented first. Any block here blocks multiple downstream teams.

---

## Implementation Sequence

Derived from dependency graph. Wave N cannot begin until Wave N-1 is complete and verified.

| Wave | Systems | Layer | Gate to advance |
|---|---|---|---|
| Wave 1 | [Foundation systems] | Foundation | All Foundation systems unit-tested |
| Wave 2 | [Core systems] | Core | Core loop playable end-to-end |
| Wave 3 | [Feature systems] | Feature | All MVP features present |
| Wave 4 | [Polish systems] | Polish | Frame budget and soak test pass |

---

## Pillar Coverage Check

Every pillar must have at least one Core-layer system that delivers it. If a pillar has no Core-layer system, the decomposition is incomplete.

| Pillar | Delivering System(s) | Layer | Risk if cut |
|---|---|---|---|
| Pillar 1: [Name] | [System] | Core | High — pillar absent from MVP |
| Pillar 2: [Name] | [System] | Core | Medium — experiential degradation |

---

## GWT Acceptance Scenarios

```
Given: the systems index is complete
When: every pillar is checked against the Pillar Coverage Check table
Then: each pillar has at least one Core-layer system assigned to it
      AND no Core-layer system has a dependency on a Feature or Polish system

Given: a new system is proposed mid-development
When: it is evaluated for inclusion
Then: it is assigned to a layer
      AND its dependencies are declared
      AND its priority tier is stated
      AND if MVP: existing MVP wave plan is updated before implementation begins

Given: a bottleneck system is blocked or delayed
When: the dependency graph is evaluated
Then: all dependent systems are identified and marked blocked
      AND no dependent system begins implementation until the bottleneck is resolved
```

---

## Open Questions

Unresolved system boundaries, unclear ownership, or dependency cycles go here. Specify receipt blocked until REQUIRED table is complete.
