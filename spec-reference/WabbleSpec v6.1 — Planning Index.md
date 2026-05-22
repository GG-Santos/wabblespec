# WabbleSpec v6.1 — Planning Index

**Document scope:** Meta-index of all planning artifacts and thematic documentation
**Status:** Complete — per-module planning done (P1–P15b), long-form documentation done

---

## Thematic Documentation

The long-form documentation set. These are the authoritative reference documents for WabbleSpec v6.1 — written from planning artifacts, not the other way around.

| Document | Scope | Key content |
|---|---|---|
| `WabbleSpec v6.1 — Core.md` | Framework ground truth | 12 invariants, 9-layer architecture, all module definitions, three-phase model, verification modes, scale-adaptive orchestration |
| `WabbleSpec v6.1 — Manual.md` | Operator guide | Workspace layout, 11 build targets, normal work loop, loading gates, full module reference, all build target recipes, operator checklist |
| `WabbleSpec v6.1 — Platform.md` | All 11 platform packages | Recipe signals, spec templates, capability defaults, engineering and security per target, verification gates, walkthroughs |
| `WabbleSpec v6.1 — Memory.md` | L5 Memory layer | Memory, MemorySearch, EntityGraph, Provenance, Dream, MemoryMine, Forget — storage structure, staleness machine, all workflows |
| `WabbleSpec v6.1 — Expression.md` | L6 Expression layer | Homowabian (4 registers, auto-switch rules), Document (6 doc types), Polish (4-pass refinement), ResearchLog |
| `WabbleSpec v6.1 — Delivery.md` | L7 Delivery layer | Archive (receipt aggregation, version bump), Package (artifact signing), Deploy (environments, rollback), Release (git tag, Attestation), Scaffold, Monitor |
| `WabbleSpec v6.1 — Evolution.md` | L8 Evolution layer | Instinct → Synth → Blueprint → Factory → Augment → Benchmark → Forge pipeline, Retro, Feedback |
| `WabbleSpec v6.1 — Security.md` | Security gateway | Threat modeling (STRIDE), OWASP checklists, continuous security, compliance frameworks, auth and secrets policy |
| `WabbleSpec v6.1 — Engineering.md` | Engineering gateway | Architecture review, ADR policy, CI/CD declaration, reliability (SLO, error budget, circuit breaker), systems design standards |
| `WabbleSpec v6.1 — AI.md` | AI gateway | Prompt engineering, chain design, agent architecture, eval policy, model governance, safety requirements |
| `WabbleSpec v6.1 — Aesthetic.md` | Aesthetic gateway | Brand, color system (semantic tokens, contrast), typography (modular scale), motion (reduced motion), design token policy |
| `WabbleSpec v6.1 — Design.md` | Design gateway | UX principles, information architecture, interaction design (touch targets, keyboard, focus, gestures), design system, accessibility floor |
| `WabbleSpec v6.1 — Experience.md` | Experience gateway | User research, usability testing, accessibility deep-dive, satisfaction measurement, research ethics |
| `WabbleSpec v6.1 — Shared-Dev.md` | _shared/dev/ | 5 language modules, 4 database modules, 4 API consumption modules — load model, activation signals, content per module |

---

## Planning Root Documents

Six foundational planning documents locked before module planning began. Authoritative for architectural decisions and invariants.

| File | Purpose |
|---|---|
| `planning/00-INDEX.md` | Planning directory index — entry point |
| `planning/01-INVARIANTS.md` | All 12 framework invariants (I1–I12) with rationale |
| `planning/02-ARCHITECTURE.md` | 9-layer architecture, module inventory, layer dependencies |
| `planning/03-CORE-FEATURES.md` | Key feature decisions: receipt chain, three-phase model, scale-adaptive autonomy, loading gates |
| `planning/04-SKILLS-FLOW.md` | Skill activation flow, routing logic, session lifecycle |
| `planning/05-MODULE-IMPORTANCE.md` | Module priority tiers (1 CRITICAL → 3 SUPPORTING), planning priority order |

---

## Module Planning Files

59 files in `planning/modules/`. Each file is the planning artifact for one or more modules, written before the long-form docs. These are sources, not destinations — the thematic docs synthesize from them.

### P1 — Schemas

| File | Content |
|---|---|
| `P1-SCHEMAS.md` | skill-rules.json schema, receipt.base.schema.json, error-event.schema.json |

### P2 — Foundation Modules

| File | Modules | Layer |
|---|---|---|
| `P2-RECIPE.md` | Recipe | L0 Intake |
| `P2-MEMORY.md` | Memory | L5 Memory |
| `P2-ECONOMY.md` | Economy | L2 Orchestration |

### P3 — Core Infrastructure

| File | Modules | Layer |
|---|---|---|
| `P3-SCOPEFRAME.md` | ScopeFrame | L1 Spec Core |
| `P3-REFERENCELOAD.md` | ReferenceLoad | L3 Platform |
| `P3-RUNTIMEPROBE.md` | RuntimeProbe | L3 Platform |
| `P3-PROVENANCE.md` | Provenance | L5 Memory |

### P4 — Spec and Routing

| File | Modules | Layer |
|---|---|---|
| `P4-SPECIFY.md` | Specify | L1 Spec Core |
| `P4-MEMORYSEARCH.md` | MemorySearch | L5 Memory |
| `P4-MODELROUTER.md` | ModelRouter | L4 Capability |
| `P4-HOMOWABIAN.md` | Homowabian | L6 Expression |

### P5 — Intake and Review

| File | Modules | Layer |
|---|---|---|
| `P5-INTERVIEW.md` | Interview | L0 Intake |
| `P5-EXPLORE.md` | Explore | L0 Intake |
| `P5-DECOMPOSE.md` | Decompose | L1 Spec Core |
| `P5-REVIEWER.md` | Reviewer | L2 Orchestration |

### P6 — Execution Core

| File | Modules | Layer |
|---|---|---|
| `P6-PROPOSE.md` | Propose | L1 Spec Core |
| `P6-EXECUTOR.md` | Executor | L2 Orchestration |
| `P6-VERIFIER.md` | Verifier | L2 Orchestration |

### P7 — Application and Archive

| File | Modules | Layer |
|---|---|---|
| `P7-APPLY.md` | Apply | L2 Orchestration |
| `P7-ARCHIVE.md` | Archive | L7 Delivery |

### P8 — Orchestration and Memory Intelligence

| File | Modules | Layer |
|---|---|---|
| `P8-AUTOPILOT.md` | Autopilot | L2 Orchestration |
| `P8-ENSEMBLE.md` | Ensemble | L2 Orchestration |
| `P8-ENTITYGRAPH.md` | EntityGraph | L5 Memory |
| `P8-DREAM.md` | Dream | L5 Memory |
| `P8-TEAMPLAN.md` | TeamPlan | L2 Orchestration |

### P9 — Shared Development Infrastructure

| File | Modules | Layer |
|---|---|---|
| `P9-SHARED-LANGUAGES.md` | node, python, go, rust, java | L3 Shared |
| `P9-SHARED-DATABASES.md` | sql, nosql, orm, migration | L3 Shared |
| `P9-SHARED-API-CONSUMPTION.md` | rest, graphql, grpc, realtime | L3 Shared |

### P10 — Platform Packages

| File | Content |
|---|---|
| `P10-PLATFORMS.md` | All 11 platform packages: Web, API/Service, Game, Mobile, Desktop, CLI, IoT/Embedded, Library/Package, Extension/Plugin, Data/Pipeline, AI/Agent |

### P11 — Capability Gateways

| File | Content |
|---|---|
| `P11-GATEWAYS.md` | All 6 gateways: Security, Engineering, AI, Aesthetic, Design, Experience |

### P12 — Expression Layer

| File | Modules | Layer |
|---|---|---|
| `P12-DOCUMENT.md` | Document | L6 Expression |
| `P12-POLISH.md` | Polish | L6 Expression |
| `P12-RESEARCHLOG.md` | ResearchLog | L6 Expression |

### P13 — Delivery Layer

| File | Modules | Layer |
|---|---|---|
| `P13-DEPLOY.md` | Deploy | L7 Delivery |
| `P13-PACKAGE.md` | Package | L7 Delivery |
| `P13-RELEASE.md` | Release | L7 Delivery |

### P14 — Evolution Pipeline

| File | Modules | Layer |
|---|---|---|
| `P14-EVOLUTION.md` | Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge | L8 Evolution |

### P15 — v5.3 Carry-Forward

| File | Content |
|---|---|
| `P15-CARRY-FORWARD.md` | 29 modules from v5.3 with carry-forward decisions and v6.1 treatment |

### P15b — Additional Modules

| File | Modules | Layer |
|---|---|---|
| `P15b-SCAFFOLD.md` | Scaffold | L7 Delivery |
| `P15b-GUARD.md` | Guard | L2 Orchestration |
| `P15b-ROLLBACK.md` | Rollback | L2 Orchestration |
| `P15b-TEST.md` | Test | L1 Spec Core |
| `P15b-CLEAN.md` | Clean | L1 Spec Core |
| `P15b-TRIAGE.md` | Triage | L1 Spec Core |
| `P15b-MIGRATE.md` | Migrate | L1 Spec Core |
| `P15b-PRODUCT.md` | Product | L0 Intake |
| `P15b-FEEDBACK.md` | Feedback | L8 Evolution |
| `P15b-MONITOR.md` | Monitor | L7 Delivery |
| `P15b-RETRO.md` | Retro | L8 Evolution |
| `P15b-MEMORYMINE.md` | MemoryMine | L5 Memory |
| `P15b-FORGET.md` | Forget | L5 Memory |

### Planning Status

| File | Purpose |
|---|---|
| `planning/modules/PROGRESS.md` | Planning phase completion tracker — all P1–P15b complete |

---

## Module Coverage Map

All modules indexed by layer, with planning source and thematic doc.

### L0 Intake

| Module | Planning source | Thematic doc |
|---|---|---|
| Recipe | P2-RECIPE.md | Manual.md, Platform.md |
| Interview | P5-INTERVIEW.md | Manual.md |
| Explore | P5-EXPLORE.md | Manual.md |
| Product | P15b-PRODUCT.md | Manual.md |

### L1 Spec Core

| Module | Planning source | Thematic doc |
|---|---|---|
| ScopeFrame | P3-SCOPEFRAME.md | Manual.md |
| Specify | P4-SPECIFY.md | Manual.md |
| Decompose | P5-DECOMPOSE.md | Manual.md |
| Propose | P6-PROPOSE.md | Manual.md |
| Test | P15b-TEST.md | Manual.md |
| Clean | P15b-CLEAN.md | Manual.md |
| Triage | P15b-TRIAGE.md | Manual.md |
| Migrate | P15b-MIGRATE.md | Manual.md |

### L2 Orchestration

| Module | Planning source | Thematic doc |
|---|---|---|
| Executor | P6-EXECUTOR.md | Manual.md |
| Verifier | P6-VERIFIER.md | Manual.md |
| Apply | P7-APPLY.md | Manual.md |
| Reviewer | P5-REVIEWER.md | Manual.md |
| Economy | P2-ECONOMY.md | Manual.md |
| Autopilot | P8-AUTOPILOT.md | Manual.md |
| Ensemble | P8-ENSEMBLE.md | Manual.md |
| TeamPlan | P8-TEAMPLAN.md | Manual.md |
| Guard | P15b-GUARD.md | Manual.md |
| Rollback | P15b-ROLLBACK.md | Manual.md |

### L3 Platform

| Module | Planning source | Thematic doc |
|---|---|---|
| ReferenceLoad | P3-REFERENCELOAD.md | Manual.md |
| RuntimeProbe | P3-RUNTIMEPROBE.md | Manual.md |
| All 11 platform packages | P10-PLATFORMS.md | Platform.md |
| _shared/dev/languages/ (5) | P9-SHARED-LANGUAGES.md | Shared-Dev.md |
| _shared/dev/databases/ (4) | P9-SHARED-DATABASES.md | Shared-Dev.md |
| _shared/dev/api-consumption/ (4) | P9-SHARED-API-CONSUMPTION.md | Shared-Dev.md |

### L4 Capability

| Module | Planning source | Thematic doc |
|---|---|---|
| ModelRouter | P4-MODELROUTER.md | Manual.md |
| Security gateway | P11-GATEWAYS.md | Security.md |
| Engineering gateway | P11-GATEWAYS.md | Engineering.md |
| AI gateway | P11-GATEWAYS.md | AI.md |
| Aesthetic gateway | P11-GATEWAYS.md | Aesthetic.md |
| Design gateway | P11-GATEWAYS.md | Design.md |
| Experience gateway | P11-GATEWAYS.md | Experience.md |

### L5 Memory

| Module | Planning source | Thematic doc |
|---|---|---|
| Memory | P2-MEMORY.md | Memory.md |
| MemorySearch | P4-MEMORYSEARCH.md | Memory.md |
| EntityGraph | P8-ENTITYGRAPH.md | Memory.md |
| Provenance | P3-PROVENANCE.md | Memory.md |
| Dream | P8-DREAM.md | Memory.md |
| MemoryMine | P15b-MEMORYMINE.md | Memory.md |
| Forget | P15b-FORGET.md | Memory.md |

### L6 Expression

| Module | Planning source | Thematic doc |
|---|---|---|
| Homowabian | P4-HOMOWABIAN.md | Expression.md |
| Document | P12-DOCUMENT.md | Expression.md |
| Polish | P12-POLISH.md | Expression.md |
| ResearchLog | P12-RESEARCHLOG.md | Expression.md |

### L7 Delivery

| Module | Planning source | Thematic doc |
|---|---|---|
| Archive | P7-ARCHIVE.md | Delivery.md |
| Package | P13-PACKAGE.md | Delivery.md |
| Deploy | P13-DEPLOY.md | Delivery.md |
| Release | P13-RELEASE.md | Delivery.md |
| Scaffold | P15b-SCAFFOLD.md | Delivery.md |
| Monitor | P15b-MONITOR.md | Delivery.md |

### L8 Evolution

| Module | Planning source | Thematic doc |
|---|---|---|
| Instinct | P14-EVOLUTION.md | Evolution.md |
| Synth | P14-EVOLUTION.md | Evolution.md |
| Blueprint | P14-EVOLUTION.md | Evolution.md |
| Factory | P14-EVOLUTION.md | Evolution.md |
| Augment | P14-EVOLUTION.md | Evolution.md |
| Benchmark | P14-EVOLUTION.md | Evolution.md |
| Forge | P14-EVOLUTION.md | Evolution.md |
| Retro | P15b-RETRO.md | Evolution.md |
| Feedback | P15b-FEEDBACK.md | Evolution.md |

---

## Key Decisions Locked in Planning

These decisions are not open — they were resolved in planning and locked. The thematic docs implement them.

| Decision | Locked answer | Source |
|---|---|---|
| Single runtime | Claude Code Terminal only — no Codex, Gemini, WabbleFlow, MCPBridge | 01-INVARIANTS.md |
| Build targets | 11 targets (expanded from v5.3's 6) | 02-ARCHITECTURE.md |
| Invariant count | 12 (I1–I12) | 01-INVARIANTS.md |
| Layer count | 9 (L0–L8) | 02-ARCHITECTURE.md |
| Capability gateways | 6 (Development distributed to _shared/dev/) | 02-ARCHITECTURE.md |
| Loading gates | 4 (Recipe, Stage, Phase, Activation) | 03-CORE-FEATURES.md |
| Verification modes | 7 (Test, Review, Audit, Measurement, Observation, Attestation, Demonstration) | 03-CORE-FEATURES.md |
| Staleness states | 6 (FRESH, AGING, STALE, EXPIRED, NEEDS_REVERIFICATION, SUPERSEDED) | P2-MEMORY.md |
| Error types | 6 (SOFT, HARD, DEPENDENCY, CONTEXT_EXHAUSTION, SPEC_VIOLATION, STALENESS_VIOLATION) | P1-SCHEMAS.md |
| Confidence decay | EMA: `confidence_new = confidence_old × 0.9 + outcome × 0.1` | P8-DREAM.md, P14-EVOLUTION.md |
| Reviewer merge | Adversary + Grader merged, budget-gated, max 3 REVISE cycles | P5-REVIEWER.md |
| Autopilot exclusivity | Sole owner of meta.md — others submit change requests | P8-AUTOPILOT.md |
| Design/Aesthetic separation | Kept separate — different activation points | P11-GATEWAYS.md |

---

## v5.3 → v6.1 Tracing

Planning artifacts that document the v5.3 carry-forward decisions:

| Source | Content |
|---|---|
| `P15-CARRY-FORWARD.md` | 29 modules with carry-forward decisions |
| `01-INVARIANTS.md` | 8 invariants expanded from v5.3 + 4 new |
| All thematic docs | v5.3 Mapping section per module where applicable |

Major changes from v5.3:
- Homowabian separated from Economy (voice register is now standalone)
- 11 build targets (was 6) — Game, Extension/Plugin, IoT/Embedded, Library/Package, AI/Agent added
- 4 new invariants: I9 (Evidence Expiry), I10 (Receipts as Operational Artifacts), I11 (Framework-Product Separation), I12 (Spec Quality over Volume)
- MemoryMine and Forget added to L5 (new in v6.1)
- Retro, Feedback, Monitor, Scaffold, Guard, Rollback, Test, Clean, Triage, Migrate, Product added (P15b)
- v6's WabbleFlow, MCPBridge, Codex/Gemini routing stripped — single runtime only
- Development gateway dissolved into _shared/dev/ (no separate gateway)

---

## Reading Guide

For different readers, recommended entry points:

**Starting fresh with v6.1:**
1. Core.md (ground truth — invariants, architecture, all modules)
2. Manual.md (operator guide — how to use the framework)

**Understanding a specific layer:**
- L5 Memory → Memory.md
- L6 Expression → Expression.md
- L7 Delivery → Delivery.md
- L8 Evolution → Evolution.md

**Understanding a specific gateway:**
- Security → Security.md
- Engineering → Engineering.md
- AI → AI.md
- Aesthetic → Aesthetic.md
- Design → Design.md
- Experience → Experience.md

**Understanding a specific build target:**
- Platform.md (all 11 targets in one document)

**Understanding shared dev infrastructure:**
- Shared-Dev.md (_shared/dev/ languages, databases, api-consumption)

**Tracing a planning decision:**
- Check the relevant planning/modules/P*.md file
- Then the thematic doc that synthesizes from it
- Then Core.md for invariant context
