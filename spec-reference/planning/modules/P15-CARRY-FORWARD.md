# v5.3 Carry-Forward Decisions — 29 Modules

**Purpose:** Map every v5.3 module not explicitly planned in P1-P14 to a v6.1 disposition. Each module is either Retained (lives in v6.1 with mapping), Merged (consolidated into a planned module), Distributed (split across multiple modules), Deferred (out of v6.1 scope, candidate for v6.2+), or Eliminated (not needed in v6.1 architecture).

---

## Decision Table

| v5.3 Module | Disposition | v6.1 Home | Notes |
|---|---|---|---|
| Scaffold | Retained | L7 Delivery — new module | See below |
| Grader | Merged | Reviewer (P5) | Grader subagent within Reviewer |
| Guard | Retained | L2 Orchestration — new module | See below |
| Test | Retained | L1 Spec Core — new module | See below |
| Review | Merged | Reviewer (P5) | Code review is Grader subagent in Reviewer |
| Clean | Retained | L1 Spec Core — new module | See below |
| Analyze | Merged | Explore (P5) + Engineering gateway (P11) | Static analysis split by scope |
| Triage | Retained | L1 Spec Core — new module | See below |
| Perf | Retained | Engineering gateway (P11) + platform packages | Performance budgets in platform; cross-cutting in Engineering |
| Deps | Retained | Platform packages (P10) + Security gateway | Dependency management platform-specific; security cross-cutting |
| Nexus | Distributed | EntityGraph (P8) + MemorySearch (P4) | Relationship tracking → EntityGraph; search → MemorySearch |
| Shift | Merged | Economy (P2) + Homowabian (P4) | Context management split: density → Economy, register → Homowabian |
| Monitor | Retained | L7 Delivery — new module | See below |
| Ground | Merged | Provenance (P3) + ReferenceLoad (P3) | Fact-checking → Provenance; source loading → ReferenceLoad |
| Audit | Merged | Security gateway (P11) | Compliance audit absorbed into Security gateway Audit verification mode |
| Enhance | Merged | Specify (P4) + Propose (P6) | Feature enhancement = spec delta + options |
| Sharpen | Merged | Interview (P5) | Requirements sharpening is Interview's core function |
| Brainstorm | Merged | Propose (P6) | Brainstorm = Propose without constraint — same options generation |
| Plan | Merged | Decompose (P5) | Planning is Decompose's output |
| Product | Retained | L0 Intake — new module | See below |
| Feedback | Retained | L8 Evolution — feeds Instinct | See below |
| Sync | Merged | ReferenceLoad (P3) | External sync = reference load with staleness recheck |
| Migrate | Retained | L1 Spec Core — new module | See below |
| Organize | Merged | Explore (P5) + Clean | Codebase organization: Explore maps, Clean executes |
| Retro | Retained | L8 Evolution — new module | See below |
| Rollback | Retained | L2 Orchestration — clarified scope | See below |
| Flag | Merged | Provenance (P3) | Flagging contradictions/issues is Provenance's contradiction tracking |
| MemoryMine | Retained | L5 Memory — existing planned module | Already in layer map; deep pattern mining beyond MemorySearch |
| Forget | Retained | L5 Memory — existing planned module | Already in layer map; controlled evidence deletion |

---

## Expanded Decisions — Retained New Modules

The following v5.3 modules are retained in v6.1 as new modules not yet fully planned. Each needs a module plan written before per-module planning is complete.

---

### Scaffold

**v6.1 Layer:** L7 Delivery
**Disposition:** Retained — generates initial project structure for new projects

**Scope in v6.1:**
- Activated by Recipe when new project detected (no existing project-map.md, empty repo)
- Reads active platform package to determine correct directory structure
- Generates: README skeleton, .gitignore, CI config, spec template, basic directory structure
- Does NOT generate application code — structure only
- Writes to project/repo/ (I11 compliant — Scaffold output is product files)

**Key decision:** Scaffold moves from Development gateway (v5.3) to L7 Delivery — it's a one-time delivery artifact, not a development tool.

**Sub-components needed:** SKILL.md, skill-rules.json, templates/ per build target (11 templates), schemas/receipt.schema.json

---

### Guard

**v6.1 Layer:** L2 Orchestration
**Disposition:** Retained — runtime input validation and constraint enforcement

**Scope in v6.1:**
- Runs as a pre-execution gate before Executor processes any wave
- Validates: inputs against declared schemas, scope constraints (I12), invariant compliance
- Detects: spec violations before execution (not after), out-of-scope requests
- Routes: violations to Reviewer (minor) or SPEC_VIOLATION error (hard block)
- Does NOT modify inputs — validates only, never transforms

**Key decision:** Guard is distinct from Security gateway (which does threat modeling and compliance). Guard is operational input validation in the execution pipeline.

**Integration:** Executor calls Guard before each wave. Guard reads skill-rules.json authority declarations to validate scope.

**Sub-components needed:** SKILL.md, skill-rules.json, rules/invariant-checklist.md, rules/scope-validation.md, schemas/receipt.schema.json

---

### Test

**v6.1 Layer:** L1 Spec Core
**Disposition:** Retained — test generation, test strategy, test execution coordination

**Scope in v6.1:**
- Generates test stubs from spec acceptance criteria (P4 stage output)
- Applies platform-appropriate test framework conventions (from platform package testing.md)
- Produces: unit test stubs, integration test stubs, acceptance test checklist
- Does NOT execute tests — coordinates with Verifier (Test verification mode)
- Maps spec requirements to test cases: each EARS requirement → at least one test case

**Key decision:** Test is a spec-driven module — tests are derived from spec, not written independently. Untestable requirements are flagged as gaps, not silently skipped.

**Integration:** Verifier Test mode reads Test module output. Platform packages provide framework-specific test patterns. Engineering gateway sets coverage policy.

**Sub-components needed:** SKILL.md, skill-rules.json, rules/coverage-floor.md, rules/requirement-mapping.md, templates/test-stub.md per target, schemas/receipt.schema.json

---

### Clean

**v6.1 Layer:** L1 Spec Core
**Disposition:** Retained — targeted code cleanup within declared scope

**Scope in v6.1:**
- Applies to project/repo/ code only (I11 — never touches .wabblespec/)
- Operations: remove dead code, normalize formatting, rename to match spec conventions, remove deprecated patterns flagged by Specify
- Scope always declared explicitly — Clean never decides its own scope
- Writes delta proposal (ADDITIVE/COSMETIC) before making changes — BREAKING changes route to Executor halt
- All changes verifiable: before/after diff written to receipt

**Key decision:** Clean is not a refactor module. Structural changes (refactoring) require Specify (spec delta) + Executor (wave execution). Clean is surface-level only: formatting, dead code, naming alignment.

**Integration:** Specify flags deprecated patterns → Clean removes them. Verifier Review mode checks Clean output. Instinct observes Clean patterns.

**Sub-components needed:** SKILL.md, skill-rules.json, rules/scope-declaration.md, rules/delta-policy.md, schemas/receipt.schema.json

---

### Triage

**v6.1 Layer:** L1 Spec Core
**Disposition:** Retained — issue classification and routing

**Scope in v6.1:**
- Receives: bug reports, feature requests, user feedback, error events
- Classifies: severity (critical/high/medium/low), type (bug/feature/debt/question), affected module
- Routes: critical bugs → immediate Executor wave, features → Interview → Specify, debt → Clean or Augment, questions → Interview
- Writes triage record to Memory as FRESH drawer with full classification

**Key decision:** Triage is a classification and routing module — it does not fix issues, only categorizes and routes. Triage reads error taxonomy (error-event.schema.json) for bug classification.

**Integration:** Feeds Interview, Specify, Clean, Executor depending on classification. Instinct observes triage patterns (recurrence signals).

**Sub-components needed:** SKILL.md, skill-rules.json, rules/severity-matrix.md, rules/routing-table.md, schemas/triage-record.schema.json, schemas/receipt.schema.json

---

### Product

**v6.1 Layer:** L0 Intake
**Disposition:** Retained — product context capture before spec work begins

**Scope in v6.1:**
- Captures: product goals, user segments, success metrics, business constraints before P1 spec stage
- Writes: product-context.md to .wabblespec/plans/
- Product context is read by Interview, Specify, and ScopeFrame — it is not a spec artifact itself
- Activates before Recipe for new projects or at /product command for existing

**Key decision:** Product is upstream of ScopeFrame and Interview. It captures the "why" before Interview captures the "what". Product context is not a spec — it informs spec decisions.

**Integration:** ScopeFrame reads product-context.md. Interview uses product goals to frame questions. Instinct tracks product goal alignment across execution.

**Sub-components needed:** SKILL.md, skill-rules.json, templates/product-context.md, schemas/receipt.schema.json

---

### Feedback

**v6.1 Layer:** L8 Evolution (feeds Instinct)
**Disposition:** Retained — structured capture of user/stakeholder feedback for Evolution pipeline

**Scope in v6.1:**
- Captures: explicit user feedback (corrections, preferences, complaints, praise)
- Structures feedback into typed records: correction/preference/complaint/endorsement
- Writes records to Memory as FRESH drawers
- Notifies Instinct: feedback event (pattern signal — corrections are high-signal observations)
- Endorsements update Instinct pattern confidence upward; corrections update downward

**Key decision:** Feedback is distinct from Instinct (which observes execution events). Feedback captures explicit human signals. Together they give Instinct both implicit execution data and explicit human evaluation.

**Sub-components needed:** SKILL.md, skill-rules.json, schemas/feedback-record.schema.json, schemas/receipt.schema.json

---

### Migrate

**v6.1 Layer:** L1 Spec Core
**Disposition:** Retained — migration planning and execution for breaking changes

**Scope in v6.1:**
- Activates when BREAKING spec delta declared (from Specify)
- Produces: migration plan (what consumers must do), migration script (if automatable), migration receipt
- Migration plan written to .wabblespec/plans/migration-<version>.md
- Migration execution coordinated through Executor waves
- Two-phase migration support: additive phase (backward-compatible) + removal phase (clean break)

**Key decision:** Migrate is triggered by BREAKING changes, not by any code change. It is a spec-driven module — the migration plan derives from the spec delta, not from inspecting code independently.

**Integration:** Specify's BREAKING delta triggers Migrate. Engineering gateway's two-phase deploy pattern applies. Release notes reference migration plan. Archive versions include migration path.

**Sub-components needed:** SKILL.md, skill-rules.json, templates/migration-plan.md, rules/two-phase-policy.md, schemas/receipt.schema.json

---

### Monitor

**v6.1 Layer:** L7 Delivery
**Disposition:** Retained — post-deployment observability setup and monitoring configuration

**Scope in v6.1:**
- Generates: observability configuration for deployed artifacts (metrics, logging, alerting)
- Platform-specific: reads platform package for target-appropriate monitoring patterns
- Writes monitoring config to project/repo/ (I11 compliant)
- Declares: SLO alert thresholds from Engineering gateway spec
- Does NOT operate monitors — configures them. Runtime monitoring is external to the framework.

**Key decision:** Monitor is a delivery module (generates config) not an operational module (does not run). It closes the loop between Engineering gateway's SLO declarations and the actual monitoring configuration deployed alongside the artifact.

**Integration:** Engineering gateway SLO declarations → Monitor alert thresholds. Deploy triggers Monitor config deployment. Instinct reads Monitor alert patterns as execution observations.

**Sub-components needed:** SKILL.md, skill-rules.json, templates/ per platform target, rules/slo-binding.md, schemas/receipt.schema.json

---

### Retro

**v6.1 Layer:** L8 Evolution
**Disposition:** Retained — structured retrospective after release cycle

**Scope in v6.1:**
- Activates after Release receipt (end of delivery cycle)
- Reads: Instinct tracker.json, all receipts from the cycle, Verifier not-tested list, open decisions
- Produces: retro-<version>.md with three sections: What worked, What didn't, What changes
- "What changes" section produces concrete Synth proposals or Triage records
- Retro is a human-collaborative artifact — framework drafts, human reviews

**Key decision:** Retro feeds Synth (framework improvement) and Triage (product improvement). It is the explicit reflection step that converts accumulated execution observations into directed improvement proposals.

**Integration:** Release triggers Retro. Retro reads Instinct patterns. Retro output feeds Synth (Evolution) or Triage (product). Memory gets retro as FRESH drawer.

**Sub-components needed:** SKILL.md, skill-rules.json, templates/retro.md, schemas/receipt.schema.json

---

### Rollback

**v6.1 Layer:** L2 Orchestration (clarified scope)
**Disposition:** Retained — explicit rollback execution module

**Scope in v6.1:**
- Distinct from Executor's checkpoint-based rollback (which is mid-wave recovery)
- Rollback activates for post-wave, post-deploy, or post-Forge rollbacks
- Reads rollback specification from: wave plan (Executor), deploy receipt (Deploy), or Forge snapshot
- Executes rollback to declared prior state
- All Rollback operations require human confirmation (irreversible state change — Attestation)
- Writes rollback receipt with: what was restored, from where, verification of restored state

**Key decision:** Rollback is not Executor's undo button — it is an explicit recovery module for cases where verification fails post-completion. Executor handles mid-wave recovery internally. Rollback handles completed-state recovery.

**Integration:** Deploy receipt references rollback plan → Rollback reads it. Forge snapshot → Rollback can restore. Release receipt → Rollback can revert git tag (with Attestation + manual git steps documented).

**Sub-components needed:** SKILL.md, skill-rules.json, rules/attestation-required.md, rules/restore-verification.md, schemas/rollback-record.schema.json, schemas/receipt.schema.json

---

## Merged Module Notes

### Grader → Reviewer

Grader subagent within Reviewer evaluates output against spec. Grader does not get a standalone module. Reviewer SKILL.md declares the Grader subagent role. See P5-REVIEWER.md.

### Review → Reviewer (Grader subagent)

Code review (v5.3 Review module) is the Grader subagent's function when applied to code artifacts. No separate module. Reviewer's budget gate determines when code review runs.

### Analyze → Explore + Engineering gateway

Static analysis (code complexity, dependency graph analysis) is split: Explore handles project structure analysis (project-map.md). Engineering gateway handles cross-cutting quality analysis in architecture review. No separate Analyze module.

### Nexus → EntityGraph + MemorySearch

v5.3 Nexus tracked relationships. EntityGraph (P8) owns the graph structure (nodes.json, edges.json). MemorySearch (P4) handles queries. Nexus is fully replaced — not a separate module.

### Shift → Economy + Homowabian

v5.3 Shift managed context shifting. In v6.1: token density management → Economy. Voice register management → Homowabian. Context placement rules → Economy. No separate Shift module.

### Ground → Provenance + ReferenceLoad

Grounding (verifying claims against sources) is split: ReferenceLoad loads sources with trust levels. Provenance tracks which claims cite which sources and flags contradictions. No separate Ground module.

### Audit → Security gateway

Compliance audit is Security gateway's Audit verification mode. No separate Audit module.

### Enhance → Specify + Propose

Feature enhancement = declaring a spec delta (Specify) + generating options (Propose). The combination is the enhancement workflow. No separate Enhance module.

### Sharpen → Interview

Requirements sharpening is Interview's core function. No separate Sharpen module.

### Brainstorm → Propose

Brainstorm is Propose without hard constraints. Propose already generates 2-4 options — this covers brainstorm scope. No separate Brainstorm module.

### Plan → Decompose

Planning is Decompose's output (wave plan). No separate Plan module.

### Sync → ReferenceLoad

External synchronization is ReferenceLoad with staleness recheck triggered. No separate Sync module.

### Organize → Explore + Clean

Codebase organization: Explore maps current state, Clean executes surface changes. Structural reorganization requires Specify delta + Executor. No separate Organize module.

### Flag → Provenance

Flagging issues/contradictions is Provenance's contradiction tracking and appendix. No separate Flag module.

---

## New Modules Added to Layer Map

The following modules are new to v6.1 (not v5.3 carry-forwards but created by this planning process):

| Module | Layer | Added by |
|---|---|---|
| TeamPlan | L2 Orchestration | P8 planning |
| Dream | L5 Memory | P8 planning |
| EntityGraph | L5 Memory | P8 planning |
| Ensemble | L2 Orchestration | P8 planning |
| RuntimeProbe | L0 Intake | P3 planning |
| Homowabian | L6 Expression | P4 planning |

---

## Open Decisions from Carry-Forward

| Decision | Module | Options | When to resolve |
|---|---|---|---|
| Scaffold: new project only vs. any target reset | Scaffold | New projects only (current) vs. also re-scaffold existing | Per-module planning |
| Guard: per-wave vs. per-input | Guard | Before each wave (current) vs. at input boundary only | Implementation |
| Test: stub generation vs. full test generation | Test | Stubs only (current) vs. full test generation from spec | Per-module planning |
| Product: required vs. optional | Product | Optional (explicit command) vs. required before P1 for new projects | Per-module planning |
| Retro: human-required vs. auto-draft | Retro | Framework drafts, human reviews (current) vs. auto-publish to Memory | Per-module planning |
| Monitor: which platforms require it | Monitor | All platforms vs. only server-side targets | P10 platform refinement |
