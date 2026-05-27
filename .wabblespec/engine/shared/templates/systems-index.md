# Systems Index Template (Platform-Agnostic)

> **Usage:** Copy into `modules/l3/[platform]/spec-template/systems-index.md` and fill in platform-appropriate examples.
> **Phase:** P1.5 — complete after P0 concept document, before design-document.md detailed sections.
> **Purpose:** Enumerate all systems, declare their dependencies, and establish implementation order before any detailed spec is written.
> A system not listed here does not get specced. A system specced before its dependencies are listed here creates ordering debt.

---

## System Layers

Systems are assigned to exactly one layer. Foundation must stabilize before Core begins. Core before Feature. Feature before Polish.

| Layer | Definition |
|---|---|
| **Foundation** | Infrastructure, configuration, cross-cutting concerns. No business logic. No layer may depend downward on Feature or Polish. |
| **Core** | Primary functionality that delivers the product's declared value proposition. Pillar-1 features live here. |
| **Feature** | Secondary systems that extend Core. May depend on Core and Foundation. Features should not depend on each other unless explicitly declared. |
| **Polish** | UX improvements, telemetry, non-blocking enhancements. Depends on Core and Feature. Never blocks MVP. |

---

## Systems Registry [REQUIRED]

One row per system. Complete before writing any detailed spec.

| System Name | Layer | Pillar(s) Served | Depends On | Priority Tier | Spec File |
|---|---|---|---|---|---|
| [System] | Foundation / Core / Feature / Polish | Pillar N / None | [System], [System] | MVP / v1 / v2 / Out of scope | spec pending |
| | | | | | |

**Minimum viable systems for MVP:** All systems in the table marked MVP priority. A system not marked MVP does not block the MVP build.

---

## Dependency Graph

Format: `System → requires → [Dependency1, Dependency2]`. Circular dependencies must be resolved before spec writing begins.

```
[System A] → requires → [none]                   (Foundation)
[System B] → requires → [System A]               (Core)
[System C] → requires → [System A, System B]     (Feature)
[System D] → requires → [none]                   (Foundation, parallel to A)
```

**Bottleneck systems** (3+ other systems depend on this one): ___
Bottleneck systems must be specced and validated first. A block here blocks multiple downstream systems.

**Circular dependencies found:** ___
Resolution: (break cycle by introducing an interface, event, or shared Foundation artifact)

---

## Implementation Wave Sequence

Derived from the dependency graph. Each wave is independently verifiable.

| Wave | Systems | Layer(s) | Checkpoint |
|---|---|---|---|
| 1 | [Foundation systems] | Foundation | Foundation systems individually tested and stable |
| 2 | [Core systems] | Core | Core value proposition demonstrable end-to-end |
| 3 | [Feature systems] | Feature | All MVP features present and testable |
| 4 | [Polish systems] | Polish | Performance gates pass; UX complete |

---

## Pillar Coverage Check

Every declared pillar must have at least one Core-layer system delivering it. A pillar with no Core system is not designed — it is aspirational.

| Pillar | Delivering System(s) | Layer | If cut from MVP: impact |
|---|---|---|---|
| Pillar 1: [Name] | [System] | Core | High — primary value proposition absent |
| Pillar 2: [Name] | [System] | Core / Feature | Medium / Low |

---

## GWT Acceptance Scenarios

```
Given: the systems index is complete
When: every declared pillar is checked against the Pillar Coverage Check table
Then: each pillar has at least one Core-layer system assigned
      AND no Core system has a declared dependency on a Feature or Polish system

Given: a new system is proposed after the index is complete
When: it is evaluated for inclusion
Then: it is assigned to a layer, its dependencies are declared, its priority tier is stated
      AND if MVP-priority: the wave plan is updated before implementation begins

Given: a bottleneck system is blocked
When: the dependency graph is evaluated
Then: all downstream systems are identified and marked blocked
      AND no downstream system begins implementation until the bottleneck resolves
```

---

## Open Questions

Unresolved system boundaries, unclear ownership, or dependency cycles. Specify receipt blocked until registry is complete with no unresolved cycles.
