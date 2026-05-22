# WabbleSpec v6.1 Architecture

---

## Structural Overview

v6.1 is a spec-driven skill framework for the complete software development lifecycle. Target-first routing. Vendor-neutral runtime. Evidence-based execution. Local-first storage. Zero external dependencies. No MCP.

Hierarchy unchanged from v5.3:

```
gateway -> group -> module -> content
```

Module count is provisional until per-module planning completes.

---

## Directory Layout

```
.wabblespec/                      # framework control plane (I11)
  INDEX.md                        # module registry
  memory/                         # evidence store with staleness tracking (I9)
  runtime/                        # vendor-neutral runtime contracts (I6)
  experiments/                    # Evolution isolation space (I8)
  plans/                          # planning artifacts
  receipts/                       # operational receipts (I10)
  _shared/                        # hooks, references, templates, scripts, schemas
    dev/
      languages/                  # Node, Python, Go, Rust, Java
      databases/                  # SQL, NoSQL, ORM, Migration
      api-consumption/            # REST/GraphQL/gRPC/Realtime client patterns
    schemas/
      error-event.schema.json     # typed error taxonomy
    references/
      development-patterns.md     # cross-platform integration guidance

project/repo/                     # product source — hard boundary (I11)
```

Framework files never cross into `project/repo/`. Product files never enter `.wabblespec/`.

---

## Layer Map

| Layer | Name | Modules |
|---|---|---|
| L0 | Intake | Recipe, ReferenceLoad, RuntimeProbe, ScopeFrame |
| L1 | Spec Core | Apply, Decompose, Explore, Interview, Propose, Specify |
| L2 | Orchestration | Autopilot, Economy, Ensemble, Executor, ModelRouter, Reviewer, TeamPlan, Verifier |
| L3 | Platform | 11 platform targets (see below) |
| L4 | Capability | Security, Engineering, AI, Aesthetic, Design, Experience (6 gateways) |
| L5 | Memory | Dream, EntityGraph, Forget, Memory, MemoryMine, MemorySearch, Provenance |
| L6 | Expression | Document, Homowabian, Polish, ResearchLog |
| L7 | Delivery | Archive, Deploy, Package, Release |
| L8 | Evolution | Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge |

---

## L3 Platform — 11 Targets

Each platform package contains:
- Platform SKILL.md with routing logic
- Platform-specific dev modules (from Development gateway distribution)
- Platform-specific engineering modules (from Engineering gateway split)
- Platform-specific security modules (from Security gateway split)
- Platform spec template variant
- Platform verification gates

| Target | Dev modules absorbed | New dev modules needed |
|---|---|---|
| Web | Frontend group (React, NextJS, Vue, Svelte, Angular, HTML, Styling), PWA | — |
| API/Service | API group server-side (REST, GraphQL, gRPC, Realtime) | — |
| Game | GameDev group (Engine, TwoD, ThreeD, GamePhysics, GameAudio) | — |
| Mobile | Client group (iOS, Android, ReactNative, Flutter) | — |
| Desktop | Client > Desktop | — |
| CLI | Backend > CLI | — |
| IoT/Embedded | — | C/C++, MicroPython, Embedded Rust, firmware build patterns |
| Library/Package | — | API surface design, semver, registry publishing, doc generation |
| Extension/Plugin | Frontend > HTML (partial) | Chrome manifest, VS Code extension API, host sandbox patterns |
| Data/Pipeline | Database group (reference) | ETL, streaming, orchestration, schema evolution |
| AI/Agent | — | Fed by L4 AI gateway — no separate dev module |

---

## L4 Capability Gateways — 6 Gateways

**Security** — Cross-cutting security only.
Retained: threat modeling, continuous security cycles, OWASP, pentest, compliance, cross-cutting defense.
Moved to L3 Platform: firmware signing (IoT), app permissions (Mobile), extension sandboxing (Extension/Plugin), library supply chain (Library/Package).

**Engineering** — Cross-cutting engineering only.
Retained: CI/CD patterns, architecture review, reliability principles, systems design, cross-cutting technical standards.
Moved to L3 Platform: build toolchain, target-specific performance budgets, hardware integration, platform build pipeline.

**AI** — Restored from v5.3/v6.
LLM evaluation, prompt engineering, chain design, agent architecture, safety considerations. Applies to any target embedding AI features, not only AI/Agent build target. AI Backend module from v5.3 Development gateway absorbed here.

**Aesthetic** — Unchanged from v5.3. Visual design, brand, style systems.

**Design** — Unchanged from v5.3. UX, interaction design, information architecture.

**Experience** — Unchanged from v5.3. User research, usability, accessibility.

---

## Development Gateway Distribution

v5.3 Development gateway (6 groups, 33 modules) fully distributed. No top-level Development gateway in v6.1. Routing distributed to each platform package.

| Bucket | Contents | Destination |
|---|---|---|
| Shared Languages | Node, Python, Go, Rust, Java | `_shared/dev/languages/` |
| Shared Databases | SQL, NoSQL, ORM, Migration | `_shared/dev/databases/` |
| Shared API Consumption | Client-side REST/GraphQL/gRPC/Realtime | `_shared/dev/api-consumption/` |
| Platform-Specific | 23 framework/platform modules | Respective L3 platform packages |
| Repurposed | AI (Backend group) | Content absorbed into L4 AI gateway |
| Eliminated | Development gateway router, terminal-specific workarounds | — |

---

## Module Anatomy

| Component | Required | Purpose |
|---|---|---|
| `SKILL.md` | Yes | Orchestration spec: process, routing, decision logic |
| `skill-rules.json` | Yes | Activation patterns and module authority declaration |
| `schemas/receipt.schema.json` | Yes | Receipt structure for I10 compliance |
| `tests/acceptance.md` | Yes | Checkable acceptance criteria |
| `receipts/MODULE-RECEIPT.md` | Yes | Generation receipt (operational artifact) |
| `references/` | Conditional | Domain knowledge loaded on demand |
| `rules/` | Conditional | Constraints, policy, validation logic |
| `evaluations/` | Conditional | Eval cases, assertions, quality measurement |
| `agents/` | Conditional | Subagent role definitions |
| `commands/` | Conditional | Slash command entry points |
| `hooks/` | Conditional | Lifecycle automation |
| `scripts/` | Conditional | Deterministic computation offloaded from LLM context |
| `schemas/` | Conditional | Input/output schemas beyond receipt |
| `data/` | Conditional | Queryable lookup tables — never loaded wholesale |
| `templates/` | Conditional | Output templates |

---

## Four Loading Gates

| Gate | Trigger | Loads |
|---|---|---|
| Recipe | Build target identified | Platform package, spec template, target rules |
| Stage | Planning stage entered (P1-P4) | Stage-appropriate modules |
| Phase | Phase entered (Research/Plan/Execute) | Phase references, schemas, eval modes |
| Activation | `skill-rules.json` pattern match | Individual module SKILL.md, rules, references |

Nothing preloaded. Nothing activated without a matched gate.

**Gate collapsing:** Plan+Execute collapse allowed when Decompose scores complexity below deliberation threshold AND spec depth is P1 only AND Recipe declares collapse-eligible. Collapse writes combined receipt.

---

## Spec Hierarchy

```
Design Document             <- Recipe selects variant per build target
  L-- Systems Design
       L-- System Architecture
            L-- Technical Specifications
                 |-- Feature Specs
                 |-- Standards
                 L-- Rules
```

---

## P1-P4 Stage to Module Activation

| Stage | Primary Modules | Phase Sequence |
|---|---|---|
| P1 — Design Document | Recipe, ScopeFrame, Interview, Specify | Research -> Plan -> Execute |
| P2 — Systems Design + Architecture | Explore, Decompose, Propose, Specify | Research -> Plan -> Execute |
| P3 — Technical Specifications | Specify, Decompose, platform modules, Engineering gateway | Research -> Plan -> Execute |
| P4 — Feature Specs + Standards + Rules | Specify, Decompose, Apply preparation, Verifier | Research -> Plan -> Execute |

P2 cannot begin until P1 spec is locked. P3 cannot begin until P2 is locked. Full per-module activation detail defined during per-module planning.

---

## Data Flow

```
User intent
  -> L0: Recipe identifies build target -> loads Platform package
  -> L0: ReferenceLoad fetches staleness-tagged evidence
  -> L0: RuntimeProbe selects runtime lane (vendor-neutral)
  -> L1: Specify populates spec hierarchy (P1 -> P4)
  -> L1: Propose generates options with tradeoffs
  -> L1: Decompose produces stage plans
  -> L2: Executor runs waves into project/repo/
  -> L2: Verifier checks target-specific gates
  -> L7: Archive writes receipts, preserves provenance
  -> L8: Instinct observes execution for pattern extraction
```

Each arrow writes a receipt. Each phase reads the upstream receipt before acting.

---

## Verification Modes

| Mode | When used |
|---|---|
| Test | Automated assertion against known inputs |
| Review | Structured human or agent critique |
| Audit | Compliance check against spec or standard |
| Measurement | Quantitative threshold check |
| Observation | Behavioral check without automation |
| Attestation | Human sign-off for irreversible actions and self-modification |
| Demonstration | Working proof against real conditions |

REVISE loop bounds: max 3 cycles per gate. Max 3 failed attempts before Attestation required.

---

## Runtime Contract

Vendor-neutral. RuntimeProbe detects environment. ModelRouter routes per task shape. Economy governs output density.

Ensemble trigger conditions: task spans multiple targets, no single lane covers capability, verification mode is Attestation or Audit, or confidence below threshold after single-lane attempt. Must be declared in task shape. Writes combined receipt naming all lanes.

Runtime receipt required fields: `selected`, `reason`, `task_shape`, `available_tools`, `fallback`, `verification_mode`.

---

## Expression and Compression

Separate concerns:
- **Homowabian (I7, L6):** voice register — lite, full, ultra, normal
- **Economy (L2):** token density — compression, hedge removal, context placement, context-type classification

---

## Error Taxonomy

`_shared/schemas/error-event.schema.json`

| Type | Meaning |
|---|---|
| SOFT | Recoverable, retry viable |
| HARD | Unrecoverable, halt required |
| DEPENDENCY | Upstream module failed |
| CONTEXT_EXHAUSTION | Context limit hit |
| SPEC_VIOLATION | Output contradicts spec |
| STALENESS_VIOLATION | Evidence used past expiry without flagging (I9) |

Orchestration routes by type, not by prose parsing.

---

## Key Boundaries

| Boundary | Rule |
|---|---|
| Framework / Product | `.wabblespec/` and `project/repo/` never mix (I11) |
| Plan / Execute | Planning and execution contexts are separate (I2). Exception: gate collapsing under defined conditions. |
| Experiment / Production | Evolution writes to `experiments/` until Forge promotes (I8) |
| Module authority | Each output has one owning module declared in `skill-rules.json` |
| Receipt chain | No phase acts without upstream receipt (I10) |
| Evidence trust | No stale/expired evidence used without flagging (I9) |
| Self-modification | Evolution modules cannot promote changes to themselves without Attestation (I8) |
