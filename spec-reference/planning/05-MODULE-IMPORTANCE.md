# WabbleSpec v6.1 Module Importance

Tier classification, dependency chains, and per-module planning order. Governs the sequence of per-module planning work.

---

## Confirmed Module Inventory (Pre-Planning)

| Layer | Confirmed Modules |
|---|---|
| L0 | Recipe, ReferenceLoad, RuntimeProbe, ScopeFrame |
| L1 | Apply, Decompose, Explore, Interview, Propose, Specify |
| L2 | Autopilot, Economy, Ensemble, Executor, ModelRouter, Reviewer, TeamPlan, Verifier |
| L3 | 11 platform packages (each a module group) |
| L4 | Security, Engineering, AI, Aesthetic, Design, Experience (6 gateway groups) |
| L5 | Dream, EntityGraph, Forget, Memory, MemoryMine, MemorySearch, Provenance |
| L6 | Document, Homowabian, Polish, ResearchLog |
| L7 | Archive, Deploy, Package, Release |
| L8 | Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge |

**v5.3 modules not yet assigned — status TBD per-module planning:**
Scaffold, Enhance, Sharpen, Nexus, Shift, Sync, Migrate, Organize, Retro, Rollback, Monitor, Flag, Brainstorm, Feedback, Product, Analyze, Triage, Test, Review, Clean, Perf, Deps, Ground, Audit, Guard, Grader, Plan

---

## Tier Definitions

| Tier | Meaning |
|---|---|
| 1 — CRITICAL | Framework cannot function. Breaks all downstream. Plan and build first. |
| 2 — CORE | Primary user-facing value. Framework severely diminished without. |
| 3 — SUPPORTING | Enhances core. Framework operates without but quality degrades. |
| 4 — SPECIALIZED | Target-specific or domain-specific. Only needed per target or capability. |
| 5 — EXTENDED | Lifecycle utilities, evolution, edge cases. Framework fully usable without. |

---

## Tier 1 — CRITICAL

7 load-bearing modules. Nothing else works without them.

| Module | Layer | Why Critical |
|---|---|---|
| Recipe | L0 | Entry point. Nothing loads without build target. All gates depend on it. |
| Specify | L1 | Spec creation mechanism. I1 cannot exist without it. |
| Verifier | L2 | All verification gates. I4 cannot exist without it. |
| Executor | L2 | Wave execution engine. No implementation runs without it. |
| Memory | L5 | Evidence store. I9 has no backing store without it. |
| Archive | L7 | Receipt persistence. I10 has no storage without it. |
| skill-rules.json schema | `_shared/` | Activation gate infrastructure. I5 progressive loading breaks without it. |

---

## Tier 2 — CORE

Primary pipeline. Framework exists but delivers no user value without these.

| Module | Layer | Why Core |
|---|---|---|
| Apply | L1 | Implementation execution. Spec -> code path. |
| Decompose | L1 | Wave planning. Executor has nothing to run without it. |
| Explore | L1 | Project orientation. Research phase has no starting map without it. |
| Interview | L1 | Ambiguity reduction. Spec quality degrades without it. |
| Propose | L1 | Options generation. P2 stage has no tradeoff surface without it. |
| ReferenceLoad | L0 | External evidence fetching. Research phase has no external input without it. |
| ScopeFrame | L0 | Session boundary definition. Spec scope undefined without it. |
| RuntimeProbe | L0 | Environment detection. ModelRouter has nothing to route without it. |
| ModelRouter | L2 | Runtime lane selection. I6 vendor-neutral runtime has no mechanism without it. |
| Economy | L2 | Token discipline. Compression by default has no enforcement without it. |
| Reviewer | L2 | Adversarial review + Grader. Quality gate on spec and output decisions. |
| Homowabian | L6 | Expression system. I7 has no mechanism without it. |
| Provenance | L5 | Evidence lineage. I9 staleness tracking has no traceability without it. |
| MemorySearch | L5 | Evidence query. Research phase reads nothing from Memory without it. |

---

## Tier 3 — SUPPORTING

Framework operates but loses depth of capability.

| Module | Layer | What degrades without it |
|---|---|---|
| Autopilot | L2 | Meta-orchestration. Manual coordination still possible. |
| Ensemble | L2 | Multi-lane runtime. Single lane still works. |
| TeamPlan | L2 | Multi-agent coordination. Single-agent still works. |
| EntityGraph | L5 | Relationship tracking. Memory stores, just not indexed by entity. |
| Dream | L5 | Evidence consolidation. Memory works, just not auto-maintained. |
| MemoryMine | L5 | Implicit knowledge extraction. Explicit memory still works. |
| ResearchLog | L6 | Research documentation. Research still happens, just not dedicated artifact. |
| Document | L6 | Output documentation generation. Implementation still works. |
| Polish | L6 | Post-apply quality pipeline. Apply still works. |

---

## Tier 4 — SPECIALIZED

Required for their specific context. Not universally needed.

| Module/Group | Layer | Context |
|---|---|---|
| Web Platform | L3 | Web builds only |
| API/Service Platform | L3 | API/Service builds only |
| Game Platform | L3 | Game builds only |
| Mobile Platform | L3 | Mobile builds only |
| Desktop Platform | L3 | Desktop builds only |
| CLI Platform | L3 | CLI builds only |
| IoT/Embedded Platform | L3 | IoT builds only |
| Library/Package Platform | L3 | Library builds only |
| Extension/Plugin Platform | L3 | Extension builds only |
| Data/Pipeline Platform | L3 | Data pipeline builds only |
| AI/Agent Platform | L3 | AI/Agent builds only |
| Security Gateway | L4 | Threat modeling, security-critical work |
| Engineering Gateway | L4 | Architecture review, reliability work |
| AI Gateway | L4 | AI feature development across any target |
| Aesthetic Gateway | L4 | Visual design work |
| Design Gateway | L4 | UX/interaction design work |
| Experience Gateway | L4 | User research, accessibility work |
| _shared/dev/languages/ | _shared/ | When language-specific patterns needed |
| _shared/dev/databases/ | _shared/ | When database patterns needed |
| _shared/dev/api-consumption/ | _shared/ | When client API patterns needed |

---

## Tier 5 — EXTENDED

Lifecycle utilities, evolution pipeline, edge-case coverage.

| Module | Layer | Notes |
|---|---|---|
| Instinct | L8 | Evolution pipeline entry. Framework improves manually without it. |
| Synth | L8 | Depends on Instinct. |
| Blueprint | L8 | Depends on Synth. |
| Factory | L8 | New module creation. Depends on Blueprint. |
| Augment | L8 | Module modification. Depends on Blueprint. |
| Benchmark | L8 | Quality gate. Depends on Augment/Factory. |
| Forge | L8 | Production integration. Depends on Benchmark. |
| Forget | L5 | Evidence deletion. Memory works without structured deletion. |
| Deploy | L7 | Deployment. Archive still works without it. |
| Package | L7 | Packaging. Target-specific. |
| Release | L7 | Release management. Target-specific. |

---

## Dependency Chain

Critical dependencies that determine planning order:

```
Recipe
  L-- depends on: nothing (entry point)

ScopeFrame, ReferenceLoad, RuntimeProbe
  L-- depends on: Recipe

Specify
  L-- depends on: ScopeFrame, Interview, ReferenceLoad

Decompose
  L-- depends on: Specify

Executor
  L-- depends on: Decompose

Apply
  L-- depends on: Executor, Platform packages

Verifier
  L-- depends on: Executor (reads output)

Archive
  L-- depends on: Verifier (reads verification receipt)

Memory
  L-- depends on: nothing (storage layer)

MemorySearch
  L-- depends on: Memory

Provenance
  L-- depends on: Memory

EntityGraph
  L-- depends on: Memory, Provenance

Dream
  L-- depends on: Memory, EntityGraph

Reviewer
  L-- depends on: Specify (reads spec), Verifier (reads gate results)

ModelRouter
  L-- depends on: RuntimeProbe

Ensemble
  L-- depends on: ModelRouter

Economy
  L-- depends on: nothing (passive enforcement layer)

Homowabian
  L-- depends on: Economy (compression is separate)

Platform packages
  L-- depends on: Recipe (target selected), _shared/dev/ (language/database patterns)

Evolution pipeline
  L-- Instinct depends on: Archive (reads receipts)
  L-- Synth depends on: Instinct
  L-- Blueprint depends on: Synth
  L-- Augment/Factory depends on: Blueprint
  L-- Benchmark depends on: Augment/Factory
  L-- Forge depends on: Benchmark
```

---

## Per-Module Planning Order

15 priority levels. Plan in this order.

| Priority | Modules | Reason |
|---|---|---|
| 1 | `skill-rules.json` schema, `receipt.schema.json`, `error-event.schema.json` | Infrastructure before modules |
| 2 | Recipe, Memory, Economy | No dependencies — foundational |
| 3 | ScopeFrame, ReferenceLoad, RuntimeProbe, Provenance | Depend only on P1-P2 |
| 4 | Specify, MemorySearch, ModelRouter, Homowabian | Depend on P2-P3 |
| 5 | Interview, Explore, Decompose, Reviewer | Depend on Specify |
| 6 | Propose, Executor, Verifier | Depend on Decompose |
| 7 | Apply, Archive | Depend on Executor/Verifier |
| 8 | Autopilot, Ensemble, EntityGraph, Dream, TeamPlan | Depend on P2-P7 |
| 9 | _shared/dev/ (languages, databases, api-consumption) | Shared infrastructure before platforms |
| 10 | All 11 Platform packages | Depend on _shared/dev/ + Recipe |
| 11 | All 6 Capability gateways | Independent but need platform context |
| 12 | L6 Expression (Document, Polish, ResearchLog) | Depend on core pipeline |
| 13 | L7 Delivery remaining (Deploy, Package, Release) | Depend on Archive |
| 14 | L8 Evolution pipeline (Instinct -> Forge in sequence) | Depend on Archive + full module space |
| 15 | v5.3 carry-forward decisions (see below) | Require context from all prior modules |

---

## v5.3 Carry-Forward Decisions

Each module needs carry / merge / drop decision during per-module planning.

| Module | Likely disposition | Action needed |
|---|---|---|
| Scaffold | Keep — project assembly distinct from spec | Confirm |
| Grader | Keep or merge into Reviewer | Decide |
| Guard | Keep — operational guardrails adjacent to I11 | Confirm |
| Test | Keep — test strategy distinct from Verifier | Confirm |
| Review (standalone) | Merge into Reviewer or keep as quality audit | Decide |
| Clean | Keep — behavioral-preserving refactor is distinct | Confirm |
| Analyze | Keep — root cause investigation | Confirm |
| Triage | Keep — targeted bug/vulnerability hunting | Confirm |
| Perf | Keep — performance profiling | Confirm |
| Deps | Keep — dependency health | Confirm |
| Nexus | Keep — tribal knowledge retrieval | Confirm |
| Shift | Keep — spec version control | Confirm |
| Monitor | Keep — post-deploy observability | Confirm |
| Ground | Keep — hallucination detection is critical for I9 | Confirm |
| Audit | Keep — compliance verification | Confirm |
| Enhance | Keep or merge into Interview | Decide |
| Sharpen | Keep or merge into Interview | Decide |
| Brainstorm | Keep or merge into Propose | Decide |
| Plan (v5.3) | Merge into Decompose/Propose or keep | Decide |
| Product | Keep — product management intelligence | Confirm |
| Feedback | Keep — external signal routing | Confirm |
| Sync | Keep — spec reconciliation for parallel changes | Confirm |
| Migrate | Keep — high-risk migration is distinct | Confirm |
| Organize | Keep — file/folder structure audit | Confirm |
| Retro | Keep | Confirm |
| Rollback | Keep — always human-confirmed | Confirm |
| Flag | Keep — feature flag lifecycle | Confirm |
| MemoryMine | Keep — implicit knowledge extraction | Confirm |
| Forget | Keep — structured deletion | Confirm |
