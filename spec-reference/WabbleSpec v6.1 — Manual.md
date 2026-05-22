# WabbleSpec v6.1 — Manual

> Operating manual for WabbleSpec v6.1. Written for human operators and AI agents. Covers workspace setup through archived result: build targets, the normal work loop, module reference, validation rules, artifact lifecycle, and build target recipes. Does not replace module specs or gateway docs. This is the operating front door.

---

## 1. What This Manual Is

WabbleSpec v6.1 is a spec-driven skill framework for the complete software development lifecycle, operating within Claude Code Terminal. It provides approximately 145 composable modules organized across nine functional layers with six capability gateways.

This manual explains how to use WabbleSpec v6.1 from blank folder to archived project result. It names where artifacts live. It says when to route by each build target. It describes how Memory, the three-phase execution model, scale-adaptive orchestration, and verification behave in normal work.

It does not replace deep architecture docs. It does not replace module SKILL.md files. It is the operating front door.

---

## 2. Workspace Layout

The workspace has two hard-separated zones. Framework control artifacts live in `.wabblespec/`. Product source lives in `project/repo/`. These zones must never mix.

```
<Main Folder>/
  CLAUDE.md                    ← Runtime adapter guidance
  .wabblespec/                 ← Framework control plane (never mix with product)
    INDEX.md                   ← Control plane index
    meta.md                    ← Framework state (Autopilot exclusive write)
    VERSION                    ← Framework version
    specs/                     ← Target specs (P1-P4 hierarchy)
    plans/                     ← Wave plans, retros, blueprints
    reviews/                   ← Review evidence
    receipts/                  ← Proof records (every phase writes one)
    memory/                    ← Evidence drawers, index, entity graph
      index.md                 ← All drawer IDs and staleness states
      ledger.md                ← Provenance ledger (append-only)
      nodes.json               ← EntityGraph nodes
      edges.json               ← EntityGraph edges
    references/                ← Mined reference packs
    questions/                 ← Interview questions (append-only)
    experiments/               ← Evolution sandbox (isolated from canon)
  project/
    repo/                      ← Product source (the only place code lives)
    docs/                      ← Generated documentation (Document module output)
```

**Rule:** `.wabblespec/` controls the framework. `project/repo/` is the product. No framework artifact belongs inside `project/repo/`. No product source belongs inside `.wabblespec/`.

**Rule:** `meta.md` is exclusively owned by Autopilot. All other modules that need to update framework state submit a change request to Autopilot — they do not write `meta.md` directly.

---

## 3. First Five Decisions

Before any work begins, five decisions must be made explicit.

| Decision | Meaning |
|---|---|
| Build target | Web, API/Service, Game, Mobile, Desktop, CLI, IoT/Embedded, Library/Package, Extension/Plugin, Data/Pipeline, or AI/Agent |
| Scope | MVP, prototype, production, audit, migration, or research |
| Risk and quality | From ScopeFrame — affects autonomy level, verification depth, review budget |
| Scale-adaptive level | L0 (simple), L1 (routine), L2 (complex), L3 (critical), L4 (cross-system) — from Decompose |
| Verification depth | Which gates prove done; what goes in the Not-tested list |

If any of these is ambiguous, run Interview before planning proceeds. Interview asks only material questions — questions whose answers change the target, architecture, gates, data model, or risk profile. Safe defaults are assumed without asking.

---

## 4. Normal Work Loop

This is the canonical sequence for a WabbleSpec v6.1 project from blank to archived.

```
1. Load Recipe — selects the right skill modules for the build target
2. Run ScopeFrame — sets risk, depth, quality bar, autonomy constraints
3. Run ReferenceLoad — selects source packs for this target (never bulk-loaded)
4. Run RuntimeProbe — verifies available tools, shell, LSP servers
5. Run Product (if L2+) — captures product context, goals, user signals
6. Run Interview — only for material ambiguity that changes architecture or risk
7. Run Explore — if project/repo/ already contains source
8. Run Specify — writes the target spec using EARS syntax
9. Run Decompose — produces waves, dependency graph, rollback checkpoints, scale level
10. Run TeamPlan — bounded agent scopes, cannot_touch declarations, explicit handoffs
11. Execute waves — three-phase per stage: Research receipt → Plan receipt → Execute receipt
12. Run Reviewer after each wave — budget-gated, max 3 REVISE cycles
13. Run Verifier before any done claim — evidence or Not-tested, never prose
14. Run MemoryMine after major decisions — stores durable evidence drawers
15. Run Package → Deploy → Release → Archive when work closes
```

Every phase writes a receipt. No phase may proceed without the upstream receipt from the previous phase. This is the receipt chain invariant (I10).

---

## 5. Build Target Reference

WabbleSpec v6.1 supports eleven build targets. Each target activates a platform package from L3 with its own spec template, verification gates, and default capability gateways.

### 5.1 Web

**Use when:** SaaS dashboard, PWA, browser app, API-backed UI, admin panel, docs site, or any browser-primary product.

**First spec:** `WEB-SPEC.md`

**Default capabilities:** Development (distributed), Design, Experience, Security, Engineering

**Verification gates:** build passes, browser smoke, responsive check, accessibility check (WCAG 2.1 AA), route coverage, API contract, security baseline

**Not-tested examples:** Missing browser, missing dev server, missing auth credentials, no accessibility checker available

**Receipt:** `PLATFORM-WEB-RECEIPT`

---

### 5.2 API/Service

**Use when:** Backend service, REST API, GraphQL endpoint, microservice, gRPC service, background worker, or any server-side system without a primary UI.

**First spec:** `API-SPEC.md`

**Default capabilities:** Development (distributed), Engineering, Security

**Verification gates:** contract tests pass, error response coverage, auth enforcement, rate limiting configured, structured logging schema, health endpoint

**Not-tested examples:** Missing integration test environment, external API credentials unavailable, load test environment not configured

**Receipt:** `PLATFORM-API-RECEIPT`

---

### 5.3 Game

**Use when:** Game prototype, engine project, interactive toy, playable loop, visual novel, simulation, or exported build.

**First spec:** `GDD.md` + `PLAYTEST.md`

**Default capabilities:** Development (distributed), Aesthetic, Experience, Engineering, Security (if networked)

**Verification gates:** playable loop confirmed, controls responsive, performance budget met, playtest evidence written, build/export passes

**Not-tested examples:** Missing engine, no playable scene, no export target, no physical device for input testing

**Receipt:** `PLATFORM-GAME-RECEIPT`

---

### 5.4 Mobile

**Use when:** iOS, Android, React Native, Flutter, Expo, Capacitor, offline-first app, store-submitted app, or device-first product.

**First spec:** `MOBILE-SPEC.md`

**Default capabilities:** Development (distributed), Experience, Security, Engineering

**Verification gates:** simulator or device smoke, permissions declared, privacy policy compliant, offline/sync behavior verified, store submission readiness

**Not-tested examples:** Missing simulator, no physical device, no store credentials, no signing keys configured

**Receipt:** `PLATFORM-MOBILE-RECEIPT`

---

### 5.5 Desktop

**Use when:** Electron, Tauri, native desktop, local-first tool, tray app, or OS-integrated workflow.

**First spec:** `DESKTOP-SPEC.md`

**Default capabilities:** Development (distributed), Experience, Security, Engineering

**Verification gates:** launch smoke, local file access verified, sandbox constraints confirmed, updater/signing plan, OS integration tested

**Not-tested examples:** Missing OS target, no signing keys, no native dependency, no installer tool

**Receipt:** `PLATFORM-DESKTOP-RECEIPT`

---

### 5.6 CLI

**Use when:** Terminal command, automation utility, file converter, developer tool, package script, or shell workflow.

**First spec:** `CLI-SPEC.md`

**Default capabilities:** Development (distributed), Engineering, Experience (terminal UX), Security (if filesystem or network risk)

**Verification gates:** help text passes, stdout/stderr contract verified, exit codes correct, golden tests pass, packaging confirmed

**Not-tested examples:** Missing runtime, missing shell, no fixture files, no package target environment

**Receipt:** `PLATFORM-CLI-RECEIPT`

---

### 5.7 IoT/Embedded

**Use when:** Firmware, sensor system, companion dashboard, device protocol, telemetry path, or OTA workflow.

**First spec:** `IOT-SPEC.md`

**Default capabilities:** Development (distributed), Engineering, Security, Experience (companion UI if present), Web or Mobile as secondary target

**Verification gates:** compile/hardware smoke, safety constraints confirmed, protocol tests, telemetry path verified, OTA/rollback procedure documented

**Not-tested examples:** No physical board, no serial access, missing firmware toolchain, no cloud endpoint, no OTA infrastructure

**Receipt:** `PLATFORM-IOT-RECEIPT`

---

### 5.8 Library/Package

**Use when:** Reusable library, npm package, pip package, Go module, Rust crate, or any artifact distributed for use by other code.

**First spec:** `LIBRARY-SPEC.md`

**Default capabilities:** Development (distributed), Engineering

**Verification gates:** public API surface documented, semver policy declared, backward compatibility verified, consumer test suite passes, package build/publish dry-run passes

**Not-tested examples:** No real consumer integration test, no registry credentials, no signing configuration

**Receipt:** `PLATFORM-LIBRARY-RECEIPT`

---

### 5.9 Extension/Plugin

**Use when:** Browser extension, IDE plugin, editor extension, app plugin, or any artifact that extends a host application.

**First spec:** `EXTENSION-SPEC.md`

**Default capabilities:** Development (distributed), Security (host permission model), Engineering

**Verification gates:** manifest permissions minimal, host API usage verified, store/marketplace compliance checked, extension isolation confirmed

**Not-tested examples:** No host application environment, no store submission credentials, no extension testing harness

**Receipt:** `PLATFORM-EXTENSION-RECEIPT`

---

### 5.10 Data/Pipeline

**Use when:** ETL pipeline, data processing workflow, analytics system, batch job, stream processor, or data transformation layer.

**First spec:** `PIPELINE-SPEC.md`

**Default capabilities:** Development (distributed), Engineering, Security (data handling and privacy)

**Verification gates:** schema contracts validated, idempotency verified, error recovery tested, lineage documented, data quality gates defined

**Not-tested examples:** No full dataset, no production credentials, no downstream consumer integration, no load simulation

**Receipt:** `PLATFORM-PIPELINE-RECEIPT`

---

### 5.11 AI/Agent

**Use when:** LLM-integrated product, AI agent, RAG pipeline, prompt chain, model evaluation system, or AI-first feature set.

**First spec:** `AI-SPEC.md`

**Default capabilities:** Development (distributed), Engineering, Security, AI gateway

**Verification gates:** eval suite defined and run, guardrails implemented, prompt injection mitigated, cost budget declared, production monitoring configured, safety policy documented

**Not-tested examples:** No eval dataset, no production model access, no monitoring infrastructure, no cost tracking

**Receipt:** `PLATFORM-AI-RECEIPT`

---

## 6. Build Target Selection

If the user names a target explicitly, route immediately. If the user says only "app" or gives an ambiguous description, Recipe infers from context signals. If confidence is low, Interview asks one target question before proceeding.

If a project has companion surfaces — a CLI tool that also has a web dashboard, or an IoT device with a mobile companion — BuildType records the primary target and all secondary targets. Platform packages are loaded for each.

| User says | Route |
|---|---|
| Build a web dashboard | Web |
| Make a REST API | API/Service |
| Create a game prototype | Game |
| Build a mobile tracker | Mobile |
| Build a desktop editor | Desktop |
| Create a CLI converter | CLI |
| Build sensor firmware | IoT/Embedded |
| Create an npm library | Library/Package |
| Build a VS Code extension | Extension/Plugin |
| Build an ETL pipeline | Data/Pipeline |
| Build a chatbot with RAG | AI/Agent |
| Build a mobile app + API | Mobile (primary), API/Service (secondary) |

---

## 7. Loading Gates

WabbleSpec v6.1 uses four loading gates to ensure modules activate only when needed.

| Gate | Trigger | What loads |
|---|---|---|
| Recipe | Build target selected | Platform package for the target, default capability gateways |
| Stage | Stage of the project lifecycle reached | Modules relevant to the current stage (spec, plan, execute, deliver, evolve) |
| Phase | Phase within a stage begins | Specific module for this phase (e.g., Research → Specify, Plan → Decompose) |
| Activation | Explicit skill invocation or signal match | Individual module SKILL.md + skill-rules.json |

Nothing is preloaded wholesale. A module activates only when its skill-rules.json trigger conditions are met.

---

## 8. Three-Phase Execution Model

Every stage of WabbleSpec v6.1 work follows a three-phase structure. Each phase writes a receipt. The next phase may not begin without the previous receipt.

```
Stage N:
  Phase 1: Research
    → Gather evidence, load references, read Memory
    → Write: research-receipt-N.md
  Phase 2: Plan
    → Produce plan artifact from evidence
    → Write: plan-receipt-N.md
  Phase 3: Execute
    → Implement the plan
    → Write: execute-receipt-N.md
```

This pattern applies at every level: per wave, per stage, per release cycle. The receipt chain is append-only and non-negotiable. Orphan phases (execution without a plan receipt, planning without a research receipt) are SPEC_VIOLATION errors.

---

## 9. Scale-Adaptive Orchestration

Decompose assigns a scale level L0–L4 based on the complexity score of the work. Scale level determines orchestration depth and autonomy.

| Level | Complexity | Orchestration | Human checkpoints |
|---|---|---|---|
| L0 | Trivial | Plan + Apply collapse into single context | None required |
| L1 | Routine | Standard three-phase, single context | None required |
| L2 | Complex | Three-phase with Reviewer gate | After plan approval |
| L3 | Critical | Full Reviewer + Verifier + Attestation | Before execution, after each wave |
| L4 | Cross-system | Ensemble review, TeamPlan, full audit trail | At every phase boundary |

Scale level is set by Decompose. It is not a human choice made upfront — it emerges from the complexity analysis of the spec and wave structure.

---

## 10. Module Manual

Quick reference for every v6.1 module. For full behavior, read the module's SKILL.md.

### L0 — Intake

#### Recipe
**Layer:** L0  
**Use:** Select correct skill set for the build target.  
**When:** Build target identified.  
**Output:** Active module set for this project.  
**Boundary:** Does not make build target decisions.  
**Verification:** Skill set matches target.  
**Receipt:** `RECIPE-RECEIPT`

#### ScopeFrame
**Layer:** L0  
**Use:** Set risk, quality bar, depth, autonomy constraints, and deadline.  
**When:** Project starts or scope changes materially.  
**Output:** Scope frame with risk level, quality threshold, scale ceiling.  
**Boundary:** Does not replace spec. Does not execute work.  
**Verification:** Risk and autonomy explicit in receipt.  
**Receipt:** `SCOPE-FRAME-RECEIPT`

#### ReferenceLoad
**Layer:** L0  
**Use:** Load source packs for this target.  
**When:** Project needs domain references, lineage material, hardening guides, or research evidence.  
**Output:** Reference load receipt with loaded packs and SOURCE labels.  
**Boundary:** Never bulk-loads raw dumps. Loads per-target relevant packs only.  
**Verification:** SOURCE labels present on all loaded material.  
**Receipt:** `REFERENCE-LOAD-RECEIPT`

#### RuntimeProbe
**Layer:** L0  
**Use:** Detect available tools, shell access, LSP servers, and environment capability.  
**When:** Project starts or environment changes.  
**Output:** Runtime capability map.  
**Boundary:** Does not assign model routes. Detects only.  
**Verification:** Unavailable tools named with explicit fallback recorded.  
**Receipt:** `RUNTIME-PROBE-RECEIPT`

---

### L1 — Spec Core

#### Explore
**Layer:** L1  
**Use:** Map existing project source.  
**When:** Imported repo, unclear architecture, or planning needs source evidence.  
**Output:** Project map with architecture summary, entry points, tech signals.  
**Boundary:** Does not edit source. Read-only.  
**Verification:** Map is bounded and sourced from actual file contents.  
**Receipt:** `EXPLORE-RECEIPT`

#### Interview
**Layer:** L1  
**Use:** Reduce ambiguity through targeted questions.  
**When:** Ambiguity would change target, architecture, data model, gates, or risk profile.  
**Output:** Confirmed answers and recorded assumptions.  
**Boundary:** Does not ask questions with safe defaults. Does not stall.  
**Verification:** Every question changes a downstream decision.  
**Receipt:** `INTERVIEW-RECEIPT`

#### Specify
**Layer:** L1  
**Use:** Write the target spec using EARS syntax.  
**When:** Build target and scope are known.  
**Output:** `WEB-SPEC.md`, `GDD.md`, `API-SPEC.md`, or equivalent target spec. All requirements in EARS syntax.  
**Boundary:** Does not execute waves. Does not invent requirements.  
**Verification:** Every requirement is testable. No ambiguous SHALL without acceptance condition.  
**Receipt:** `SPEC-RECEIPT`

#### Propose
**Layer:** L1  
**Use:** Generate a change proposal for large or high-risk changes.  
**When:** Architecture change, migration, breaking change, or framework improvement.  
**Output:** Proposal artifact with rationale, risks, acceptance criteria, rejected alternatives.  
**Boundary:** Does not mutate canon directly. Proposal must be accepted before implementation.  
**Verification:** Risks declared, acceptance criteria present, rollback path defined.  
**Receipt:** `PROPOSE-RECEIPT`

#### Decompose
**Layer:** L1  
**Use:** Break the spec into waves with rollback checkpoints.  
**When:** Accepted spec needs implementation sequencing.  
**Output:** Wave list, dependency graph, rollback checkpoints, complexity score, scale level.  
**Boundary:** Does not write code. Does not execute waves.  
**Verification:** Every wave has a verification gate. Scale level justified.  
**Receipt:** `DECOMPOSE-RECEIPT`

#### Apply
**Layer:** L1  
**Use:** Dispatch implementation.  
**When:** Plans accepted, waves defined, routes confirmed.  
**Output:** Apply receipt and changed artifact list.  
**Boundary:** Does not redo target detection. Does not skip receipts.  
**Verification:** All claims go to Verifier. No self-verification.  
**Receipt:** `APPLY-RECEIPT`

#### Scaffold
**Layer:** L1  
**Use:** Assemble project structure from platform templates.  
**When:** New project, no `project-map.md` exists.  
**Output:** Project structure, CLAUDE.md, platform-specific files.  
**Boundary:** Idempotency guard: refuses if `project-map.md` already exists. Structure only — no app code.  
**Verification:** Triggers Explore after generation. Directory structure matches template.  
**Receipt:** `SCAFFOLD-RECEIPT`

#### Test
**Layer:** L1  
**Use:** Write tests from EARS requirements.  
**When:** EARS requirements specify testable behavior.  
**Output:** Test stubs in `project/repo/tests/`, test plan in `.wabblespec/plans/`.  
**Boundary:** Does not run tests. Does not modify production code.  
**Verification:** Every EARS requirement maps to at least one test case. WHEN/THEN → positive + boundary; IF/WHEN/THEN → condition-not-met.  
**Receipt:** `TEST-RECEIPT`

#### Clean
**Layer:** L1  
**Use:** Behavioral-preserving refactor, formatting, dead code removal.  
**When:** Post-implementation hygiene, deprecated removal, consistency pass.  
**Output:** Cleaned files with full diff in receipt.  
**Boundary:** COSMETIC only. No BREAKING changes. Any additive rename is allowed. Breaking changes halt to Executor.  
**Verification:** Full diff written to receipt before overwriting. Cannot touch schemas, receipts, or code not in scope.  
**Receipt:** `CLEAN-RECEIPT`

---

### L2 — Orchestration

#### Autopilot
**Layer:** L2  
**Use:** Full lifecycle meta-orchestrator.  
**When:** Complex or multi-stage project requiring scale-adaptive routing.  
**Output:** Orchestration decisions, scale routing, `meta.md` updates.  
**Boundary:** Sole owner of `meta.md`. All other modules submit change requests.  
**Verification:** Phase boundaries confirmed, receipts present, scale level justified.  
**Receipt:** `AUTOPILOT-RECEIPT`

#### Ensemble
**Layer:** L2  
**Use:** Cross-perspective review for high-risk decisions.  
**When:** Architecture decisions, security decisions, data model choices, irreversible changes at L3+.  
**Output:** Dissent record, consensus decision.  
**Boundary:** Not for trivial work. Only at L3+ scale.  
**Verification:** Dissent resolved or explicitly logged with rationale.  
**Receipt:** `ENSEMBLE-RECEIPT`

#### TeamPlan
**Layer:** L2  
**Use:** Define bounded non-overlapping agent scopes for multi-agent work.  
**When:** Work requires parallel agent execution.  
**Output:** Agent scope declarations, `cannot_touch` lists, explicit handoff points.  
**Boundary:** Scopes must be non-overlapping. Cannot execute — scoping only.  
**Verification:** No scope gaps, no scope overlaps. Every handoff has explicit acceptance condition.  
**Receipt:** `TEAMPLAN-RECEIPT`

#### Reviewer
**Layer:** L2  
**Use:** Budget-gated quality and adversarial review.  
**When:** After any plan or implementation wave.  
**Output:** Review findings with severity classification (CRITICAL/HIGH/MEDIUM/LOW).  
**Boundary:** Max 3 REVISE cycles per wave. Budget-gated by impact score. Cannot hide findings.  
**Verification:** Every finding has evidence. CRITICAL findings block progression.  
**Receipt:** `REVIEWER-RECEIPT`

#### Verifier
**Layer:** L2  
**Use:** Prove completion claims.  
**When:** Before any done signal.  
**Output:** Verification receipt and Not-tested list.  
**Boundary:** No prose-only success. Evidence or Not-tested — no other options.  
**Verification:** Claims proven by objective evidence (test output, build output, tool output). Unverified claims go to Not-tested with named missing dependency.  
**Receipt:** `VERIFIER-RECEIPT`

#### Executor
**Layer:** L2  
**Use:** Run work waves under Apply.  
**When:** Apply dispatches implementation.  
**Output:** Execution receipt with changed files, test results, diagnostics.  
**Boundary:** Does not claim done. Claims go to Verifier.  
**Verification:** Worktree boundary respected. No edits outside declared scope.  
**Receipt:** `EXECUTOR-RECEIPT`

#### Guard
**Layer:** L2  
**Use:** Validate operations before they execute.  
**When:** Any module produces output that could violate invariants or exceed scope.  
**Output:** Validation verdict (PASS/FAIL). FAIL surfaces as SPEC_VIOLATION.  
**Boundary:** Cannot be bypassed. Four validation layers: schema, scope, invariant compliance, authority.  
**Verification:** All 12 invariants checked. Authority declaration verified against module plan.  
**Receipt:** `GUARD-RECEIPT`

#### Rollback
**Layer:** L2  
**Use:** Revert to a prior verified checkpoint.  
**When:** Wave failed verification, deploy produced errors, Forge promotion went wrong.  
**Output:** Rollback instructions, state restored to checkpoint.  
**Boundary:** All rollbacks require Attestation. Release rollback provides instructions — git operations confirmed by human.  
**Verification:** Checkpoint exists before rollback executes. Post-rollback verification gate run.  
**Receipt:** `ROLLBACK-RECEIPT`

#### Triage
**Layer:** L2  
**Use:** Route bugs, issues, and feedback to the correct handler.  
**When:** Bug report, vulnerability, error, or user complaint received.  
**Output:** Routed issue with severity and handler assigned.  
**Boundary:** Bug/Critical → Executor immediate; Feature → Interview → Specify; Security → Security gateway immediately.  
**Verification:** Routing justified. Recurrence tracked: 2nd occurrence escalates one severity, 3rd+ → High minimum + Synth proposal.  
**Receipt:** `TRIAGE-RECEIPT`

#### Migrate
**Layer:** L2  
**Use:** Execute high-risk data and API migration workflows.  
**When:** Schema change, API breaking change, data format migration.  
**Output:** Migration plan, Phase 1 (additive) artifact, Phase 2 (breaking) artifact.  
**Boundary:** Two-phase default: Phase 1 ADDITIVE (backward compatible), Phase 2 BREAKING requires Attestation. Single-phase only for internal consumers or security-critical.  
**Verification:** Phase 1 verified before Phase 2 begins. Consumer confirmation for breaking changes.  
**Receipt:** `MIGRATE-RECEIPT`

---

### L3 — Platform

Platform packages are loaded by Recipe based on build target. Each package owns: spec template, dev modules, engineering (build toolchain, performance budgets), security (threat model, platform controls), and verification gates.

#### Web Package
**Owns:** Browser application lifecycle, WEB-SPEC template, web verification gates (build, smoke, responsive, accessibility, routes, security baseline).

#### API/Service Package
**Owns:** Backend service lifecycle, API-SPEC template, contract tests, structured logging, health check gates.

#### Game Package
**Owns:** Game development lifecycle, GDD+PLAYTEST templates, engine toolchain, playable loop gate, export gate.

#### Mobile Package
**Owns:** iOS/Android/cross-platform lifecycle, MOBILE-SPEC template, simulator smoke, store compliance gates.

#### Desktop Package
**Owns:** Desktop application lifecycle, DESKTOP-SPEC template, signing, OS integration, local file access gates.

#### CLI Package
**Owns:** Command-line tool lifecycle, CLI-SPEC template, stdout/stderr contract, exit code, golden test gates.

#### IoT/Embedded Package
**Owns:** Firmware and device lifecycle, IOT-SPEC template, safety constraints, OTA/rollback gates.

#### Library/Package Package
**Owns:** Distributable artifact lifecycle, LIBRARY-SPEC template, API surface documentation, semver policy, publish dry-run gate.

#### Extension/Plugin Package
**Owns:** Host-extension lifecycle, EXTENSION-SPEC template, manifest permission minimization, store compliance.

#### Data/Pipeline Package
**Owns:** Data processing lifecycle, PIPELINE-SPEC template, schema contract, idempotency, lineage gates.

#### AI/Agent Package
**Owns:** LLM/agent lifecycle, AI-SPEC template, eval suite, guardrails, cost budget, safety policy gates.

---

### L4 — Capability Gateways

Six capability gateways provide cross-cutting domain expertise. A gateway activates when Recipe selects it for the target.

#### Security Gateway
**Use:** Threat modeling, attack surface analysis, red/blue assessment, compliance verification.  
**Key modules:** Recon, Surface, Model, Premortem, Assess, Attack, Pentest, Defend, Harden, Detect, Respond, Cycle, Score, Evaluate, Regulatory, Forensics, Incident.  
**Critical rule:** Security gate must pass or be explicitly Not-tested before Deploy proceeds. No silent security skip.

#### Engineering Gateway
**Use:** CI/CD, infrastructure, ADRs, SLOs, reliability, operational readiness.  
**Key modules:** CI/CD pipeline, ADR registry, SLO definition, reliability patterns.  
**Critical rule:** Operational path (how the product runs in production) must be defined before Release.

#### AI Gateway
**Use:** Prompt engineering, chain design, eval planning, safety policy, cost monitoring.  
**Key modules:** Prompt design, chain architecture, eval suite design, guardrail implementation, production monitoring.  
**Critical rule:** No AI feature ships without an eval suite and a declared guardrail policy.

#### Aesthetic Gateway
**Use:** Design tokens, visual identity, contrast enforcement, motion, asset governance.  
**Key modules:** Token system, contrast checker, motion policy, asset pipeline.  
**Critical rule:** WCAG 2.1 AA contrast (4.5:1 text, 3:1 UI) is non-negotiable. Cannot be downgraded.

#### Design Gateway
**Use:** Information architecture, user flows, state design, interaction patterns, accessibility structure.  
**Key modules:** IA design, flow mapping, state machine design, touch target enforcement.  
**Critical rule:** Touch targets minimum 44×44pt (mobile). Keyboard navigation must be complete for web.

#### Experience Gateway
**Use:** Usability testing, user research, accessibility matrix, UX validation.  
**Key modules:** Usability test planning, research synthesis, accessibility audit, WCAG 2.1 AA verification.  
**Critical rule:** WCAG 2.1 AA is the minimum. Accessibility gaps are CRITICAL findings in Reviewer.

---

### L5 — Memory

#### Memory
**Layer:** L5  
**Use:** Coordinate the full memory subsystem.  
**When:** Any prior decision, source, or receipt is relevant to current work.  
**Output:** Wake-up context assembled from drawers.  
**Boundary:** No unsourced fact asserted as fact. Empty memory state is valid.

#### MemorySearch
**Layer:** L5  
**Use:** Targeted retrieval from Memory evidence store.  
**When:** Agent needs prior decisions or source facts before repeating research.  
**Output:** Evidence pack with relevance scores.  
**Boundary:** No unlimited raw context. Retrieval is bounded and relevance-ranked.

#### MemoryMine
**Layer:** L5  
**Use:** Deep pattern mining across the full evidence store.  
**When:** Explicit `/memorymine` command, Dream delegates clustering, Autopilot triggers after large Memory growth.  
**Output:** Gap map, cluster candidates, pattern summary, staleness map.  
**Boundary:** Never runs during active execution. Four operations: gap detection, cluster detection, pattern extraction, staleness map.

#### EntityGraph
**Layer:** L5  
**Use:** Track entities and relationships across the project.  
**When:** Files, modules, decisions, features, or sources need links.  
**Output:** Updated nodes.json and edges.json.  
**Boundary:** Deterministic pattern matching for extraction — no inference without evidence. Contradictions marked with `contradicts` edge.

#### Provenance
**Layer:** L5  
**Use:** Enforce source trails on all sourced claims.  
**When:** Any claim derived from a source appears.  
**Output:** Provenance record with source path, confidence, freshness.  
**Boundary:** No anonymous sourced claims. Unsupported claims marked UNVERIFIED.

#### Dream
**Layer:** L5  
**Use:** Background consolidation of Memory evidence.  
**When:** Enough activity accumulates, contradictions detected, or staleness threshold crossed.  
**Output:** Consolidated drawers, EMA-decayed staleness scores, dream receipt.  
**Boundary:** Never runs during active execution. Does not delete — Dream decays, Forget removes.

#### Forget
**Layer:** L5  
**Use:** Controlled deletion of Memory drawers.  
**When:** Explicit `/forget` command, Dream flags EXPIRED drawers (suggestion only), compliance deletion.  
**Output:** Provenance deletion record, deleted drawer, EntityGraph update.  
**Boundary:** Sole authorized deleter. Provenance deletion record written BEFORE file removed. Single drawer: confirmation prompt. Bulk: Attestation required. Deletion record in ledger.md is permanent — never removed.

---

### L6 — Expression

#### Homowabian
**Layer:** L6  
**Use:** Voice register management across all output.  
**When:** All module output. Default register is `full`.  
**Output:** Voice policy applied to current context.  
**Registers:** `lite` (user-facing progress), `full` (standard module output), `ultra` (module-to-module), `normal` (security warnings, irreversible confirmations, exact error quotes).  
**Boundary:** Never compresses: exact error messages, security warnings, irreversible action confirmations, EARS requirement text.

#### Document
**Layer:** L6  
**Use:** Write durable project documentation from spec artifacts.  
**When:** Manuals, handoffs, architecture docs, API docs needed.  
**Output:** Documentation artifact in `project/docs/`.  
**Boundary:** Traceability required — no invented content. STALE/EXPIRED sources flagged, not silently used. Cannot replace receipts.

#### Polish
**Layer:** L6  
**Use:** Final hygiene pass before handoff or publication.  
**When:** Before handoff, release, archive, or external publication.  
**Output:** Polished artifact with full diff in receipt.  
**Boundary:** Four passes only: register enforcement, redundancy removal, structural consistency, spec compliance check. Cannot touch code files, schemas, or receipts.

#### ResearchLog
**Layer:** L6  
**Use:** Record research findings and decisions durably.  
**When:** Reference research or external material creates decisions worth preserving.  
**Output:** One drawer per finding (not per session). Provenance record per drawer.  
**Boundary:** Discarded findings not written to Memory. Append-only questions file not read unless explicitly requested.

---

### L7 — Delivery

#### Package
**Layer:** L7  
**Use:** Prepare the verified build for distribution.  
**When:** Verification gate passed, ready to package.  
**Output:** Artifact manifest with: artifact_id, version, built_from git SHA, SHA-256 hash, signing method, provenance chain.  
**Boundary:** Signing failure is HARD error. No unsigned artifact proceeds to Deploy.

#### Deploy
**Layer:** L7  
**Use:** Deliver artifact to a declared environment.  
**When:** Package artifact ready, environment declared in spec.  
**Output:** Deploy receipt with environment, artifact, rollback plan.  
**Boundary:** Rollback plan required before any activation. Production deploy requires Attestation — non-negotiable. Auto rollback trigger detection available; human confirms execution.

#### Release
**Layer:** L7  
**Use:** Formally close the release cycle.  
**When:** Verification and packaging complete.  
**Output:** Git tag, release notes, release receipt.  
**Boundary:** Git tag push requires Attestation (irreversible). Release notes sourced from Archive only — no invention. Known issues drawn from Verifier not-tested list.

#### Archive
**Layer:** L7  
**Use:** Close and finalize a completed phase or release.  
**When:** Phase or release ends.  
**Output:** Archive receipt, not-tested compilation, Memory summary.  
**Boundary:** Does not delete active work. Does not close if evidence is missing. Triggers MemoryMine and Dream hooks.

#### Scaffold (also L7)
**Layer:** L7 (Delivery tier for new platform targets)  
See L1 Scaffold entry. Platform scaffold templates live in L7.

#### Monitor
**Layer:** L7  
**Use:** Configure post-deploy observability.  
**When:** After Deploy, before release is considered complete.  
**Output:** Metrics config, log schema, alert rules, health check config, dashboard template, OTel tracing config.  
**Boundary:** SLO → alert rule binding is mandatory. Structured JSON logs required for server-side targets. Alert thresholds must be justified against SLO budget.

---

### L8 — Evolution

#### Instinct
**Layer:** L8  
**Use:** Detect recurring behavioral patterns from execution history.  
**When:** Receipts reveal patterns with sufficient repetition and confidence.  
**Output:** Instinct candidate in `tracker.json`.  
**Boundary:** Does not promote. Observes only. EMA formula: `confidence_new = confidence_old × 0.9 + outcome × 0.1`. Promotion threshold: ≥ 0.8 confidence.

#### Synth
**Layer:** L8  
**Use:** Synthesize evidence into an improvement candidate.  
**When:** Instinct patterns reach promotion threshold, external reference material ingested, or Retro produces confirmed framework proposals.  
**Output:** Synthesis candidate with SOURCE labels.  
**Boundary:** No external branding in output. SOURCE labels visible on all inputs. Reads pattern-summary.md from MemoryMine.

#### Blueprint
**Layer:** L8  
**Use:** Design the framework change safely.  
**When:** Synthesis candidate accepted for implementation.  
**Output:** Blueprint with EARS requirements for the framework change, rollback path, impact analysis.  
**Boundary:** Does not mutate canon. Blueprint must be accepted before Factory runs.

#### Factory
**Layer:** L8  
**Use:** Build the experiment artifact.  
**When:** Blueprint accepted.  
**Output:** Experiment module(s) in `.wabblespec/experiments/`.  
**Boundary:** Writes only to experiments/. Never touches canon.

#### Augment
**Layer:** L8  
**Use:** Fill content into Factory structure.  
**When:** Factory produces structure skeleton.  
**Output:** Content-complete experiment artifact.  
**Boundary:** Factory produces structure. Augment fills content. The two phases are sequential and separated.

#### Benchmark
**Layer:** L8  
**Use:** Compare experiment against baseline.  
**When:** Experiment artifact complete, seeking promotion.  
**Output:** Benchmark receipt with 6-dimension score: correctness, completeness, safety, efficiency, consistency, spec-compliance. PASS/FAIL/CONDITIONAL verdict.  
**Boundary:** No forced pass. FAIL blocks Forge. CONDITIONAL requires human review before Forge.

#### Forge
**Layer:** L8  
**Use:** Promote benchmarked experiment to canon.  
**When:** Benchmark PASS and rollback path exists.  
**Output:** Canonical module updated, pre-promotion snapshot written, promotion receipt.  
**Boundary:** Every promotion requires Attestation. Self-modification (Forge modifying its own module) requires double Attestation. Pre-promotion snapshot always written before canon is touched.

#### Retro
**Layer:** L8  
**Use:** Structured retrospective after each release cycle.  
**When:** Release receipt written (always triggers), or explicit `/retro` command.  
**Output:** Retro artifact (DRAFT until human confirms). Sections: What Worked, What Didn't, Open Decisions, What Changes.  
**Boundary:** Always DRAFT first. Human confirms before "What Changes" is routed to Synth (framework) or Triage (product). No auto-routing.

#### Feedback
**Layer:** L8  
**Use:** Classify and route external signals.  
**When:** User correction, complaint, preference, endorsement, or question received.  
**Output:** Classified signal with confidence score, routing decision.  
**Signal types:** Correction (high, negative) → Instinct + Memory; Preference (soft negative) → Memory; Complaint (negative) → Synth proposal; Endorsement (positive) → Instinct; Question → Interview.

---

## 11. Shared Infrastructure — _shared/dev/

Development knowledge is distributed across `_shared/dev/` rather than consolidated in a single Development gateway. Each technology area is a standalone reference module.

### Languages

| Module | Activation signal |
|---|---|
| `_shared/dev/languages/node/` | `package.json` + no framework detection |
| `_shared/dev/languages/python/` | `pyproject.toml`, `requirements.txt`, `setup.py` |
| `_shared/dev/languages/go/` | `go.mod` |
| `_shared/dev/languages/rust/` | `Cargo.toml` |
| `_shared/dev/languages/java/` | `pom.xml`, `build.gradle`, `build.gradle.kts` |

Each language module contains: language references and idioms, toolchain guide, common pitfall patterns, test toolchain, and LSP integration notes.

### Databases

| Module | Activation signal |
|---|---|
| `_shared/dev/databases/sql/` | SQL connection string env vars, migration directory presence |
| `_shared/dev/databases/nosql/` | MongoDB/Redis/DynamoDB client in dependencies |
| `_shared/dev/databases/orm/` | ORM config file detected (`prisma/`, `drizzle.config`, `sqlalchemy`) |
| `_shared/dev/databases/migration/` | Migration directory detected (`migrations/`, `db/migrate/`) |

Security rules (injection prevention, credential handling) from database modules are forwarded to the Security gateway automatically.

### API Consumption

| Module | Activation signal |
|---|---|
| `_shared/dev/api-consumption/rest/` | HTTP client library in dependencies, fetch usage |
| `_shared/dev/api-consumption/graphql/` | GraphQL client (`apollo-client`, `urql`, `gql`) |
| `_shared/dev/api-consumption/grpc/` | gRPC client library or `.proto` files in client context |
| `_shared/dev/api-consumption/realtime/` | WebSocket or SSE client library |

**Client-vs-server disambiguation:** These modules cover client-side consumption only. Server-side API implementation lives in the API/Service platform package. skill-rules.json has explicit disambiguation logic — consuming an API is not the same as implementing one.

---

## 12. Verification and the Not-tested Rule

**Done means evidence exists.**

Evidence is: test output, build output, browser smoke result, simulator result, accessibility check output, static analysis output, review findings, package build proof, deployment proof, benchmark result, or receipt.

If evidence cannot be produced, the artifact must say **Not-tested**.

Not-tested must name exactly:
- The missing tool, device, credential, service, file, runtime, or environment
- Why it is missing
- What would need to change for the test to run

Not-tested is not failure by itself. Hidden unverified claims are failure.

**Ownership:**
- Verifier owns done state
- Reviewer owns defect findings
- Archive owns closure
- Provenance owns source-backed truth
- Guard owns invariant compliance

```yaml
# Verification claim format
claim: <what is being claimed>
evidence: <specific output proving the claim>
verification_mode: test|review|audit|measurement|observation|attestation|demonstration
platform_gate: <gate name from platform package>
not_tested:
  - <missing item 1>
  - <missing item 2>
risk: <residual risk from not-tested items>
receipt_path: <path to receipt file>
```

---

## 13. The Seven Verification Modes

Each module declares which verification mode it uses. The mode determines what constitutes valid evidence.

| Mode | Evidence required | Used by |
|---|---|---|
| Test | Test suite passes (explicit pass/fail output) | Test, Verifier (code), Benchmark |
| Review | Structured findings list with severity | Reviewer, Security gateway modules |
| Audit | Compliance mapping with evidence per control | Regulatory, Audit modules |
| Measurement | Metric against defined threshold (SLO, budget, coverage %) | Monitor, Benchmark, Aesthetic |
| Observation | Output written and present (for background/batch modules) | Dream, MemoryMine, Instinct |
| Attestation | Human confirmation received and recorded | Deploy (production), Release, Rollback, Forge, bulk Forget |
| Demonstration | Walkthrough with recorded artifacts (screenshots, video, logs) | Experience, Aesthetic, Usability |

---

## 14. Memory Everyday Use

Memory starts empty without failure.

1. **Before repeating research:** Run MemorySearch first. Retrieve evidence rather than re-deriving it.
2. **After major decisions:** Run MemoryMine to store durable evidence drawers.
3. **After every Provenance-creating event:** Provenance records the source trail automatically.
4. **After large Memory growth (50+ new drawers):** Autopilot may schedule MemoryMine for cluster detection.
5. **When contradictions appear:** Dream consolidates after contradiction threshold crossed.
6. **When drawers expire:** Dream flags EXPIRED drawers. Forget executes removal (with Attestation for bulk).
7. **For compliance deletion:** Forget requires compliance reason + Attestation. Deletion record in ledger.md is permanent.

Memory staleness states:

| State | Meaning |
|---|---|
| FRESH | Verified within current activity window |
| AGING | Some activity since last verification — still trusted |
| STALE | Significant activity since last verification — use with caution |
| EXPIRED | Activity threshold crossed — do not use without reverification |
| NEEDS_REVERIFICATION | Drawer was cited by a deleted or EXPIRED drawer |
| SUPERSEDED | A newer drawer explicitly replaces this one |

---

## 15. Error Handling

Errors are typed, not guessed. Every module emits errors from the shared taxonomy.

| Type | Meaning | Routing |
|---|---|---|
| SOFT | Recoverable, non-blocking | Log, continue |
| HARD | Unrecoverable, blocks progression | Halt, surface to Triage |
| DEPENDENCY | Upstream module failed or missing | Block, request upstream retry |
| CONTEXT_EXHAUSTION | Context window approaching limit | Split task, write checkpoint |
| SPEC_VIOLATION | Module action violates an invariant or scope constraint | Halt, surface to Guard + Reviewer |
| STALENESS_VIOLATION | Module used EXPIRED or STALE evidence without declaration | Halt, surface to Provenance + Reviewer |

Orchestration modules (Autopilot, Apply, Executor) route errors by type. Prose failure messages are not parsed — errors must be typed.

---

## 16. Recovery Flows

| Situation | Recovery action |
|---|---|
| Wrong build target detected | Re-run Recipe with correct target. Update ScopeFrame. |
| Scope too large for scale level | Re-run ScopeFrame and Decompose. Adjust wave granularity. |
| Spec is wrong mid-implementation | Return to Specify or Propose. Write delta proposal. Do not silently deviate. |
| Implementation breaks verification gate | Reviewer records finding. Executor fixes under same wave. Max 3 REVISE cycles. |
| Verification cannot run (missing tool) | Verifier records Not-tested. Blocks done claim. Names missing dependency. |
| Deploy produces errors | Auto rollback trigger detected. Human confirms execution. Rollback to last checkpoint. |
| Release blocked | Release lists blockers explicitly. Archive does not close as complete. |
| Framework experiment fails Benchmark | Experiment stays in `.wabblespec/experiments/`. Does not overwrite canon. |
| Memory contradiction detected | Dream consolidation triggered. Contradicted drawers flagged for reverification. |
| EXPIRED drawer referenced by active work | Provenance flags STALENESS_VIOLATION. MemorySearch retrieval blocked for EXPIRED drawers. |

---

## 17. Artifact Lifecycle

| Artifact | Purpose | Created | Updated | Guardrail |
|---|---|---|---|---|
| `CLAUDE.md` | Runtime adapter guidance | Scaffold | When Claude tool surface changes | Must not claim Claude is required for every workflow |
| `.wabblespec/INDEX.md` | Control plane index | Scaffold | After module, plan, receipt, or architecture changes | Must remain navigable |
| `.wabblespec/meta.md` | Framework state | Scaffold | Autopilot exclusive | No module writes meta.md directly — submit change request to Autopilot |
| `.wabblespec/specs/` | Target specs (P1-P4) | Specify | Via Specify or Propose | Must use EARS syntax. No ambiguous SHALL without acceptance condition |
| `.wabblespec/plans/` | Wave plans, retros, blueprints | Decompose, TeamPlan | Through wave execution | Must separate user-facing value from implementation mechanics |
| `.wabblespec/reviews/` | Review evidence | Reviewer | When findings resolved or accepted | Must lead with defects and risks. CRITICAL findings never dismissed silently |
| `.wabblespec/receipts/` | Proof records | Every phase that claims completion | Verifier, RuntimeProbe, Delivery, Evolution | Must include Not-tested when evidence is missing |
| `.wabblespec/memory/index.md` | Drawer index with staleness states | Memory first store | MemoryMine, Dream, Forget | Staleness states must be current |
| `.wabblespec/memory/ledger.md` | Provenance ledger | Provenance first record | Append-only — never edited | Deletion records are permanent. Append-only invariant (I7) |
| `.wabblespec/memory/nodes.json` | EntityGraph nodes | EntityGraph first write | EntityGraph, Forget | No stale triple as current. Orphan check after Forget |
| `.wabblespec/memory/edges.json` | EntityGraph edges | EntityGraph first write | EntityGraph | Contradiction edges marked explicitly |
| `.wabblespec/references/` | Mined reference packs | ReferenceLoad | One source at a time | Never raw dumps. SOURCE labels required |
| `.wabblespec/experiments/` | Evolution sandbox | Factory | Augment, Benchmark | Isolation from canon is absolute. Experiments never overwrite canon |
| `project/repo/` | Product source | Scaffold or import | Apply, Executor, platform modules | Must not contain WabbleSpec control-plane artifacts |
| `project/docs/` | Generated documentation | Document | Document | Traceability required. Source must be real spec artifacts |

---

## 18. Build Target Recipes

Full step-by-step sequences for each build target.

### 18.1 Web Recipe

```
Start: "Build a web dashboard / PWA / browser app / SaaS product"

Step 1: Recipe — load Web platform package + default gateways
Step 2: ScopeFrame — MVP depth, risk, quality bar, deadline
Step 3: ReferenceLoad — web-relevant packs only
Step 4: RuntimeProbe — tools, shell, LSP, browser access
Step 5: Interview — only if target framework, auth model, or data model is ambiguous
Step 6: Specify — write WEB-SPEC.md with EARS requirements
Step 7: Decompose — waves, dependency graph, scale level
Step 8: TeamPlan — agent scopes if parallel execution needed
Step 9: Execute waves (three-phase each): Research → Plan → Execute receipt
Step 10: Reviewer — quality gate per wave, max 3 REVISE cycles
Step 11: Verifier — build, browser smoke, responsive check, accessibility (WCAG 2.1 AA), route/API/security basics
Step 12: MemoryMine — store receipts and decisions
Step 13: Package → Deploy → Release → Archive

Archive closes only when: all evidence present or explicitly Not-tested.
```

### 18.2 API/Service Recipe

```
Start: "Build a REST API / backend service / microservice"

Step 1: Recipe — load API/Service platform package + Engineering + Security gateways
Step 2: ScopeFrame — service risk, SLO expectations, upstream/downstream dependencies
Step 3: ReferenceLoad — API design packs, OpenAPI spec references if applicable
Step 4: RuntimeProbe — shell, test runner, database tooling
Step 5: Interview — if auth model, versioning strategy, or consumer contract is unclear
Step 6: Specify — write API-SPEC.md with contract requirements
Step 7: Decompose — endpoint groups as waves
Step 8: Execute waves (three-phase each)
Step 9: Reviewer — contract coverage, error handling, auth enforcement
Step 10: Verifier — contract tests, error response coverage, auth gate, structured logging, health endpoint
Step 11: Monitor — SLO definitions, alert rules, structured log schema
Step 12: Package → Deploy → Release → Archive
```

### 18.3 Game Recipe

```
Start: "Make a game prototype / playable loop / engine project"

Step 1: Recipe — load Game platform package + Aesthetic + Experience gateways
Step 2: ScopeFrame — MVP loop definition, performance budget, export target
Step 3: ReferenceLoad — engine-specific packs
Step 4: RuntimeProbe — engine toolchain, build tools, export capability
Step 5: Specify — write GDD.md + PLAYTEST.md
Step 6: Decompose — core loop first, then systems
Step 7: Execute waves (three-phase each)
Step 8: Reviewer — loop integrity, performance budget, controls
Step 9: Verifier — playable loop, controls responsive, performance budget, playtest evidence, build/export
Step 10: MemoryMine — store design decisions
Step 11: Package → Release → Archive
```

### 18.4 Mobile Recipe

```
Start: "Create iOS / Android / React Native / Flutter app"

Step 1: Recipe — load Mobile platform package + Experience + Security gateways
Step 2: ScopeFrame — device targets, offline requirements, store submission constraints
Step 3: ReferenceLoad — platform-specific packs (iOS/Android/cross-platform)
Step 4: RuntimeProbe — simulator access, toolchain, signing tools
Step 5: Interview — if offline model, permissions, or store constraints unclear
Step 6: Specify — write MOBILE-SPEC.md
Step 7: Decompose — feature waves, device-specific gates
Step 8: Execute waves (three-phase each)
Step 9: Reviewer — permission model, privacy compliance, offline behavior
Step 10: Verifier — simulator/device smoke, permissions declared, offline/sync, store readiness
Step 11: Package → Deploy → Release → Archive
```

### 18.5 Desktop Recipe

```
Start: "Build Electron / Tauri / native desktop app"

Step 1: Recipe — load Desktop platform package + Experience + Security gateways
Step 2: ScopeFrame — OS targets, local file requirements, signing/distribution plan
Step 3: ReferenceLoad — desktop framework packs
Step 4: RuntimeProbe — build toolchain, signing keys availability, OS access
Step 5: Specify — write DESKTOP-SPEC.md
Step 6: Decompose — core shell first, then features
Step 7: Execute waves (three-phase each)
Step 8: Reviewer — sandbox constraints, local file access, updater logic
Step 9: Verifier — launch smoke, local file access, sandbox check, updater/signing, OS integration
Step 10: Package → Deploy → Release → Archive
```

### 18.6 CLI Recipe

```
Start: "Create a CLI tool / terminal command / automation script"

Step 1: Recipe — load CLI platform package + Engineering gateway
Step 2: ScopeFrame — command contract scope, packaging target
Step 3: ReferenceLoad — language toolchain packs
Step 4: RuntimeProbe — shell, runtime, package manager
Step 5: Specify — write CLI-SPEC.md with command contract (help text, exit codes, stdout/stderr)
Step 6: Decompose — commands as waves
Step 7: Execute waves (three-phase each)
Step 8: Reviewer — command contract completeness, error handling, exit codes
Step 9: Verifier — help text, stdout/stderr contract, exit codes, golden tests, packaging
Step 10: Package → Release → Archive
```

### 18.7 IoT/Embedded Recipe

```
Start: "Build firmware / sensor system / device protocol"

Step 1: Recipe — load IoT/Embedded platform package + Engineering + Security gateways + companion (Web/Mobile if needed)
Step 2: ScopeFrame — hardware target, safety constraints, OTA strategy, telemetry requirements
Step 3: ReferenceLoad — embedded packs, safety standards packs
Step 4: RuntimeProbe — toolchain, board access, serial access, cloud endpoint availability
Step 5: Interview — safety constraints, protocol requirements, OTA rollback policy
Step 6: Specify — write IOT-SPEC.md with safety requirements explicit
Step 7: Decompose — firmware core, then protocol, then telemetry, then OTA
Step 8: Execute waves (three-phase each, safety constraints enforced at every gate)
Step 9: Reviewer — safety constraints, protocol correctness, OTA rollback
Step 10: Verifier — compile/hardware smoke, safety gates, protocol tests, telemetry path, OTA/rollback procedure
Step 11: Package → Deploy → Release → Archive
```

### 18.8 Library/Package Recipe

```
Start: "Create an npm package / Go module / Python library / Rust crate"

Step 1: Recipe — load Library/Package platform package + Engineering gateway
Step 2: ScopeFrame — public API surface, semver policy, backward compatibility constraints
Step 3: ReferenceLoad — language packs
Step 4: RuntimeProbe — build toolchain, publish registry access
Step 5: Specify — write LIBRARY-SPEC.md with API surface contract
Step 6: Decompose — API design first, then implementation, then consumer tests
Step 7: Execute waves (three-phase each)
Step 8: Reviewer — API surface documentation completeness, backward compatibility, semver compliance
Step 9: Verifier — API surface documented, semver declared, consumer test suite passes, publish dry-run
Step 10: Package → Release → Archive
```

### 18.9 Extension/Plugin Recipe

```
Start: "Build a browser extension / VS Code plugin / editor extension"

Step 1: Recipe — load Extension/Plugin platform package + Security gateway
Step 2: ScopeFrame — host application targets, permission model, store submission requirements
Step 3: ReferenceLoad — host API packs
Step 4: RuntimeProbe — host application environment, store submission tools
Step 5: Specify — write EXTENSION-SPEC.md with permission declarations
Step 6: Decompose — host API integration first, then features
Step 7: Execute waves (three-phase each)
Step 8: Reviewer — permissions minimal, host API usage correct, store compliance
Step 9: Verifier — manifest permissions minimal, host API verified, store compliance checked, isolation confirmed
Step 10: Package → Release → Archive
```

### 18.10 Data/Pipeline Recipe

```
Start: "Build an ETL pipeline / data processor / analytics system"

Step 1: Recipe — load Data/Pipeline platform package + Engineering + Security gateways
Step 2: ScopeFrame — data volume, SLO, retention policy, privacy constraints
Step 3: ReferenceLoad — data format packs, integration packs
Step 4: RuntimeProbe — data infrastructure access, source/sink credentials
Step 5: Interview — if idempotency requirements, error recovery strategy, or lineage requirements unclear
Step 6: Specify — write PIPELINE-SPEC.md with schema contracts and quality gates
Step 7: Decompose — ingestion first, then transform, then load, then quality gates
Step 8: Execute waves (three-phase each)
Step 9: Reviewer — schema contracts, idempotency, error recovery, lineage
Step 10: Verifier — schema validated, idempotency verified, error recovery tested, lineage documented, quality gates defined
Step 11: Monitor — pipeline-specific SLOs, error rate alerts, data quality metrics
Step 12: Package → Deploy → Release → Archive
```

### 18.11 AI/Agent Recipe

```
Start: "Build a chatbot / RAG system / AI agent / LLM-integrated product"

Step 1: Recipe — load AI/Agent platform package + Engineering + Security + AI gateways
Step 2: ScopeFrame — model cost budget, eval requirements, safety constraints, latency targets
Step 3: ReferenceLoad — prompt engineering packs, eval methodology packs
Step 4: RuntimeProbe — model API access, eval tooling, monitoring infrastructure
Step 5: Interview — eval dataset availability, guardrail policy, cost tolerance
Step 6: Specify — write AI-SPEC.md with eval plan and safety policy
Step 7: Decompose — foundation first (model access, logging), then features, then eval, then guardrails
Step 8: Execute waves (three-phase each)
Step 9: Reviewer — eval coverage, guardrail completeness, prompt injection mitigations, cost controls
Step 10: Verifier — eval suite defined and run, guardrails implemented, prompt injection mitigated, cost budget declared, monitoring configured, safety policy documented
Step 11: Monitor — LLM-specific metrics (latency, cost, eval score drift, error rate)
Step 12: Package → Deploy → Release → Archive
```

---

## 19. Operator Checklist

Before shipping:

**Setup**
- [ ] `.wabblespec/` exists and is separate from `project/repo/`
- [ ] `CLAUDE.md` is present and current
- [ ] Recipe selected the correct platform package

**Spec**
- [ ] Build target selected (one primary, secondary targets named if present)
- [ ] ScopeFrame complete with risk level and autonomy constraints
- [ ] Spec written in EARS syntax
- [ ] Every requirement has a testable acceptance condition

**Execution**
- [ ] Receipt chain intact (no orphan phases)
- [ ] Every wave has a verification gate
- [ ] Scale level justified in Decompose receipt
- [ ] Reviewer run per wave (max 3 REVISE cycles enforced)
- [ ] No CRITICAL findings unresolved or undocumented

**Verification**
- [ ] Verifier owns done state — no self-verification
- [ ] Not-tested list is explicit when evidence cannot run
- [ ] Not-tested items name the specific missing dependency

**Memory**
- [ ] MemorySearch used before repeating prior decisions
- [ ] MemoryMine run after major decisions
- [ ] EXPIRED drawers not referenced without reverification
- [ ] Provenance records present for all sourced claims

**Delivery**
- [ ] Package artifact manifest includes git SHA and SHA-256 hash
- [ ] Package signed before Deploy
- [ ] Production Deploy required Attestation
- [ ] Rollback plan documented before activation
- [ ] Monitor configured with SLO-bound alert rules

**Closure**
- [ ] Release notes sourced from Archive only
- [ ] Known issues drawn from Verifier not-tested list
- [ ] Retro triggered after release (DRAFT until human confirms)
- [ ] Archive closes only after receipts and Memory update

---

## 20. Cross-Document Map

| If you need | See |
|---|---|
| Full invariant set (I1–I12) | WabbleSpec v6.1 — Core.md |
| Architecture, layer map, directory layout | WabbleSpec v6.1 — Core.md |
| Module anatomy, skill-rules.json schema | WabbleSpec v6.1 — Core.md |
| Platform packages detail | WabbleSpec v6.1 — Platform.md |
| Memory layer deep detail | WabbleSpec v6.1 — Memory.md |
| Expression modules detail | WabbleSpec v6.1 — Expression.md |
| Delivery pipeline detail | WabbleSpec v6.1 — Delivery.md |
| Evolution pipeline detail | WabbleSpec v6.1 — Evolution.md |
| Security gateway detail | WabbleSpec v6.1 — Security.md |
| Engineering gateway detail | WabbleSpec v6.1 — Engineering.md |
| AI gateway detail | WabbleSpec v6.1 — AI.md |
| Aesthetic gateway detail | WabbleSpec v6.1 — Aesthetic.md |
| Design gateway detail | WabbleSpec v6.1 — Design.md |
| Experience gateway detail | WabbleSpec v6.1 — Experience.md |
| _shared/dev/ modules | WabbleSpec v6.1 — Shared-Dev.md |
| Planning artifacts index | WabbleSpec v6.1 — Planning Index.md |
| Planning source files | WabbleSpec v6.1/planning/ |
