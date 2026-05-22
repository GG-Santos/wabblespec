> Version: 6.1.0 | Modules: ~55 planned + platform packages | Gateways: 6 | Layers: 9 (L0-L8) | Scope: Framework summary, design philosophy, 12 invariants, architecture, module definitions across all layers, shared infrastructure, three-phase model, verification modes, error taxonomy, key boundaries, changes from v5.3.
>
> v6.1 changes from v5.3: 11 build targets (was 6). Development gateway fully distributed to platform packages and _shared/dev/. Engineering and Security gateways split — platform-specific portions to L3, cross-cutting retained at L4. AI gateway restored at L4. Homowabian separated from Economy (voice register vs. token density). Adversary + Grader merged into Reviewer module with budget gate. Receipts formalized as operational artifacts (I10). Evidence expiry added as invariant (I9). Framework-product separation formalized (I11). Spec quality over volume added (I12). TeamPlan added at L2. EntityGraph, Dream, MemoryMine, Forget, ResearchLog added. All 6 staleness states defined. Vendor-neutral runtime formalized with capability descriptors. WabbleFlow removed. MCPBridge removed. No external dependencies.

---

## 1. Framework Summary

WabbleSpec is a spec-driven skill framework for the complete software development lifecycle. It provides composable modules organized across nine functional layers using a gateway architecture that scales domain knowledge through a four-level hierarchy:

**gateway → group → module → content**

Each module is a full subsystem with activation logic, orchestration rules, verification conditions, and receipt generation. The only mandatory component is `SKILL.md`. All other components load on demand.

**Module count:** ~55 core modules + 11 platform packages (each containing platform-specific dev, engineering, and security modules). **Gateway count:** 6 (Security, Engineering, AI, Aesthetic, Design, Experience). **Shared infrastructure:** `_shared/dev/` with language, database, and API consumption reference modules. **Build targets:** 11 (Web, API/Service, Game, Mobile, Desktop, CLI, IoT/Embedded, Library/Package, Extension/Plugin, Data/Pipeline, AI/Agent).

WabbleSpec runs within Claude Code Terminal. No external MCPs. No telemetry. No data export. All storage is plain files. All activation is defined in portable `skill-rules.json` files. The framework operates entirely offline with zero external dependencies.

---

### v6.1 changes from v5.3

**New in v6.1:**

1. **11 build targets.** v5.3 had 6. Added: IoT/Embedded, Library/Package, Extension/Plugin, Data/Pipeline, AI/Agent. Each target has a full L3 platform package.

2. **Development gateway distributed.** v5.3's Development gateway (6 groups, ~33 modules) fully dissolved. Languages → `_shared/dev/languages/`. Databases → `_shared/dev/databases/`. API consumption → `_shared/dev/api-consumption/`. Platform-specific frameworks → L3 platform packages. AI backend module content → L4 AI gateway.

3. **Engineering and Security gateways split.** Platform-specific portions (build toolchain, performance budgets, hardware integration, firmware signing, app permissions, extension sandboxing) moved to L3 platform packages. Cross-cutting concerns retained at L4.

4. **AI gateway restored at L4.** LLM evaluation, prompt engineering, chain design, agent architecture, safety. Applies to any target embedding AI features, not only the AI/Agent build target.

5. **Homowabian separated from Economy.** v5.3 bundled voice register and token density in one module. v6.1: Economy handles token density and compression. Homowabian handles voice register (lite/full/ultra/normal). Separate activation, separate authority.

6. **Reviewer absorbs Adversary + Grader.** Adversary and Grader no longer standalone modules. Reviewer contains both as subagents. Budget gate determines when each activates. Max 3 REVISE cycles per gate.

7. **Four new invariants.** I9: Evidence Expiry. I10: Receipts as Operational Artifacts. I11: Framework-Product Separation. I12: Spec Quality over Volume. Total: 12 invariants.

8. **TeamPlan at L2.** Multi-agent coordination with bounded non-overlapping scopes, explicit handoffs, and cannot_touch declarations. Activates only at L4 autonomy or explicit command.

9. **EntityGraph.** Relationship index with nodes.json and edges.json. Entity extraction by deterministic pattern matching. Dream-triggered cleanup.

10. **Dream.** Background memory consolidation at zero active-session cost. Staleness decay, pattern decay, evidence clustering, EntityGraph cleanup, contradiction resolution.

11. **Six staleness states.** FRESH, AGING, STALE, EXPIRED, NEEDS_REVERIFICATION, SUPERSEDED. All transitions defined and enforced by I9.

12. **Vendor-neutral runtime.** Capability descriptors replace model names throughout. RuntimeProbe detects available capabilities. ModelRouter routes by capability descriptor, not model name.

**Removed in v6.1:**

- WabbleFlow — no visual workflow output
- MCPBridge — no MCP in v6.1
- Development gateway as a top-level gateway — distributed
- Standalone Adversary module — merged into Reviewer
- Standalone Grader module — merged into Reviewer

---

## 2. Design Philosophy

### Spec-centric design

**Spec as lookup table, not documentation.** Specifications are structured for retrieval, not reading. Every spec artifact includes: canonical name, aliases, non-goals, anti-patterns, and explicit constraints.

**Robots-first specs.** Specs are optimized for agent search and execution. They favor explicit constraints, EARS syntax, aliases, and file references over narrative explanation.

**Specs evolve semantically.** Changes are classified by meaning: BREAKING, ADDITIVE, COSMETIC. BREAKING changes trigger Migrate and require two-phase deploy. ADDITIVE changes notify downstream. COSMETIC changes require no coordination.

**Spec quality enforced.** I12 prevents spec bloat. Every requirement must be testable. Duplicate requirements are rejected. Non-goals are as important as goals.

---

### Execution and verification

**Verification is non-negotiable.** Every module that produces output defines an objective, checkable completion condition. Seven verification modes cover the full range from automated assertion to human attestation.

**Receipts chain unbroken.** No phase acts without the upstream phase's receipt. No Executor wave begins without Guard passing. No Deploy activates without Package receipt. The chain is machine-checked, not assumed.

**Adversarial challenge is budget-gated.** Reviewer's Adversary subagent generates counter-analysis. Grader subagent evaluates both sides. Triggers only when ambiguity > 0.4, confidence < 0.7, impact is HIGH, or verification mode is Attestation. Max 3 REVISE cycles before human escalation.

**Controlled spec mutation during execution.** When Apply discovers a better approach mid-wave, it proposes a delta (ADDITIVE/COSMETIC → Specify --patch, BREAKING → Executor halt). No silent deviation from spec.

**Errors are typed.** Six error types with defined routing actions. Orchestration routes by type, not by parsing prose failure messages.

---

### Architecture and modularity

**Gateways route, groups organize, modules execute.** L3 platform packages load per build target. L4 capability gateways provide cross-cutting concerns. Modules remain isolated — coordination is at the orchestration layer.

**Progressive loading.** Four loading gates: Recipe (build target), Stage (P1-P4), Phase (Research/Plan/Execute), Activation (skill-rules.json match). Nothing preloaded. Nothing activated without a matched gate.

**Single output ownership.** Every artifact has one owning module declared in `skill-rules.json`. No implicit shared state. Concurrent writes prevented by ownership declaration.

**Scale-adaptive orchestration.** Autopilot selects autonomy level (L0-L4) from Decompose's complexity score. L0: minimal orchestration. L4: TeamPlan may activate for genuinely complex multi-agent tasks.

---

### Evidence and memory

**Evidence is tracked, not assumed.** All knowledge lives in Memory drawers with staleness metadata. Six states. EXPIRED evidence cannot be used without flagging. I9 enforces this unconditionally.

**Provenance follows every claim.** Each Memory drawer has a Provenance record: source, confidence, citations, contradictions. Cascade computation propagates on BREAKING changes.

**Memory consolidates in background.** Dream runs at zero active-session cost. Pattern decay via EMA. Evidence clustering for potential consolidation. EntityGraph cleanup. Never during active execution.

---

### Vendor-neutral runtime

**No model names in framework.** Capability descriptors (code-generation, analysis, synthesis, etc.) replace model names throughout. RuntimeProbe detects available capabilities. ModelRouter routes by descriptor, not by model identity.

**Ensemble for complex tasks.** Four trigger conditions: multi-target span, capability gap, Attestation/Audit verification mode, confidence below threshold after single-lane attempt. Three coordination modes: sequential, independent, cross-check.

---

## 3. The Twelve Invariants

### I1 — The spec is the anchor

Every execution loop is grounded in a spec artifact. No module invents behavior without a spec backing the decision. Spec artifacts are the only source of truth for what should be built, how it should be verified, and what constitutes completion.

**Enforcement:** Executor reads spec artifact before each wave. Guard validates wave inputs against spec. Verifier checks spec compliance as part of every verification mode — not as an optional check.

---

### I2 — Two-phase separation

Planning and execution operate in distinct contexts. Planning produces artifacts (spec, wave plan, decomposition). Execution consumes them. A context that is planning does not also execute, and vice versa.

**Exception:** Gate collapsing is allowed when Decompose scores complexity below deliberation threshold (< 0.3), spec depth is P1 only, and Recipe declares the task collapse-eligible. Collapse writes a combined receipt declaring both phases completed.

**Enforcement:** Autopilot manages phase boundaries. Executor does not invoke Specify. Specify does not invoke Apply. Receipts are phase-specific — no merged planning/execution receipt except under declared collapse.

---

### I3 — Verification gates everything

No module signals completion without meeting a defined, objective verification condition. Verification mode is declared in `skill-rules.json` and cannot be changed at runtime. The seven verification modes cover the full range from automated assertion to human attestation.

**Enforcement:** Verifier runs after every Executor wave. REVISE loops enforce correction before PASS. BLOCKED conditions halt the pipeline and require human intervention.

---

### I4 — Progressive loading

Modules activate only when needed. Nothing is preloaded unnecessarily. The four loading gates (Recipe, Stage, Phase, Activation) ensure that context contains only what the current task requires.

**Enforcement:** `skill-rules.json` activation patterns are the sole mechanism for module loading. No module may self-activate outside its declared patterns. Economy enforces context placement rules to maintain loading discipline.

---

### I5 — Adversarial challenge

Any decision-producing module may invoke adversarial review. Specifications are strengthened through structured challenge, not assumed correctness.

**Budget-gated.** Reviewer's Adversary subagent triggers only when: ambiguity score > 0.4, confidence score < 0.7, impact classification is HIGH, or verification mode is Attestation. When not triggered, modules proceed without adversarial review. Max 3 REVISE cycles per gate before human escalation.

**Enforcement:** Reviewer owns the budget gate. No module self-triggers adversarial review outside Reviewer's authority.

---

### I6 — Vendor-neutral runtime

No model name, no provider name, and no platform-specific API appears in any framework file. All runtime references use capability descriptors: code-generation, analysis, synthesis, instruction-following, reasoning, tool-use, vision, embedding.

**Enforcement:** RuntimeProbe detects available capabilities and writes runtime-state.json with capability descriptors. ModelRouter reads capability descriptors. No module reads model identity. Receipts record the capability descriptor used, not the model name.

---

### I7 — Compression by default

Output tokens are treated as a constrained resource. Economy manages token density — mechanical hedge removal, context placement rules, --budget mode. Homowabian manages voice register — lite, full, ultra, normal.

**Separation:** Economy and Homowabian are distinct modules with distinct activation and authority. Economy handles density. Homowabian handles register. Both are active simultaneously.

**Enforcement:** Economy applies hedge detection mechanically (exact pattern matching, not judgment). Homowabian applies register based on task type signals and meta.md register state.

---

### I8 — Self-improvement through evidence

The framework learns from its own execution. Instinct observes execution events and extracts patterns via EMA confidence scoring. Synth synthesizes high-confidence patterns into proposals. Blueprint converts proposals into specs. Factory/Augment implement in experiments/. Benchmark evaluates. Forge promotes — with Attestation.

**Isolation:** All Evolution writes go to `.wabblespec/experiments/`. Live framework files are read-only during Evolution until Forge promotion. Self-modification of Evolution modules requires double Attestation.

**Enforcement:** Forge is the only module that promotes from experiments/ to production. Every Forge promotion requires Attestation. Pre-promotion snapshot always written.

---

### I9 — Evidence expiry

Staleness states are enforced, not advisory. EXPIRED evidence cannot be silently used — it must be flagged with a STALENESS_VIOLATION or reverified before use. The six staleness states (FRESH, AGING, STALE, EXPIRED, NEEDS_REVERIFICATION, SUPERSEDED) are machine-tracked metadata, not human-maintained labels.

**Transitions:**
- FRESH → AGING: project activity since last verification exceeds threshold
- AGING → STALE: further activity or time fallback threshold
- STALE → EXPIRED: maximum staleness limit reached
- Any state → NEEDS_REVERIFICATION: Provenance detects contradiction
- Any state → SUPERSEDED: drawer explicitly replaced by newer drawer

**Enforcement:** Guard checks staleness of all wave inputs. STALENESS_VIOLATION is a typed error that routes to Reviewer or Attestation depending on severity. Dream applies staleness transitions in background.

---

### I10 — Receipts as operational artifacts

Receipts are not logs. They are operational artifacts that gate downstream behavior. No phase acts without the upstream phase's receipt. Receipts are written once, append-only, and cannot be retroactively modified.

**Receipt chain:** Research receipt → Plan receipt → Execute receipt → Wave receipt → Verification receipt → Delivery receipt. Each link in the chain is checked before the next activates.

**Enforcement:** Guard checks for upstream receipts before each wave. Autopilot verifies stage receipts before advancing to the next stage. Archive aggregates all receipts before version bump.

---

### I11 — Framework-product separation

`.wabblespec/` and `project/repo/` are hard boundaries. Framework files never write to product code. Product files never enter the framework control plane. This separation is architectural, not a convention.

**What lives where:**
- `.wabblespec/`: INDEX.md, memory/, runtime/, experiments/, plans/, receipts/, _shared/
- `project/repo/`: all product source code, tests, documentation, build output

**Enforcement:** Apply writes only to `project/repo/`. Guard checks write targets against declared authority before every wave. Any wave that attempts to write framework files is a SPEC_VIOLATION hard error.

---

### I12 — Spec quality over volume

Specification depth and precision matter more than coverage breadth. A short, testable, unambiguous spec is better than a long, comprehensive, untestable one. Spec bloat is a first-class defect.

**Quality indicators:** EARS syntax for all requirements. Every requirement is independently testable. Non-goals are as explicit as goals. Anti-patterns are named. Canonical name + aliases present.

**Volume indicators (flags):** Duplicate requirements. Requirements that cannot be mapped to a test case. Requirements written as implementation instructions rather than behavioral constraints. Sections that exist to demonstrate thoroughness rather than constrain behavior.

**Enforcement:** Specify enforces EARS syntax. Guard checks spec input word count against threshold. Reviewer can flag spec bloat. I12 violations are SPEC_VIOLATION errors.

---

## 4. Architecture

### Layer map

| Layer | Name | Primary responsibility |
|---|---|---|
| L0 | Intake | Target identification, reference loading, runtime detection, scope declaration, product context |
| L1 | Spec Core | Spec hierarchy writing, decomposition, exploration, interviews, proposals, execution, cleanup, triage, migration, testing |
| L2 | Orchestration | Lifecycle management, execution control, routing, verification, compression, adversarial review, multi-agent coordination |
| L3 | Platform | 11 platform packages — each with target-specific dev, engineering, and security modules |
| L4 | Capability | 6 cross-cutting gateways — Security, Engineering, AI, Aesthetic, Design, Experience |
| L5 | Memory | Evidence store, staleness tracking, relationship graph, background consolidation, controlled deletion, deep mining |
| L6 | Expression | Voice register, document generation, refinement passes, research session capture |
| L7 | Delivery | Versioning, artifact preparation, deployment, release coordination, observability configuration, project scaffolding |
| L8 | Evolution | Pattern observation, synthesis, blueprint creation, module scaffolding, content augmentation, benchmarking, promotion, retrospective, feedback capture |

---

### Gateway map (L4)

| Gateway | Cross-cutting scope | Platform-specific portions (at L3) |
|---|---|---|
| Security | Threat modeling, OWASP, pentest, compliance frameworks, cross-cutting defense | Firmware signing (IoT), app permissions (Mobile), extension sandboxing (Extension/Plugin), library supply chain (Library/Package) |
| Engineering | CI/CD patterns, architecture review, reliability principles, systems design | Build toolchain, performance budgets, hardware integration, platform build pipeline |
| AI | LLM evaluation, prompt engineering, chain design, agent architecture, safety | — (all AI content at L4) |
| Aesthetic | Visual design, brand, style systems, color, typography, motion | — |
| Design | UX, interaction design, information architecture, design systems | — |
| Experience | User research, usability testing, accessibility deep-dives, satisfaction measurement | — |

---

### Directory layout

```
.wabblespec/                      <- framework control plane (I11)
  INDEX.md                        <- module registry
  meta.md                         <- Autopilot-owned lifecycle state
  memory/                         <- evidence store with staleness tracking (I9)
    drawers/                      <- evidence files with staleness metadata
    index.md                      <- drawer registry
    tracker.json                  <- Instinct pattern tracker (Dream decays)
    entity-graph/
      nodes.json                  <- entity registry
      edges.json                  <- relationship registry
      index.md                    <- human-readable summary
    provenance/
      ledger.md                   <- append-only deletion and contradiction log
    dream-clusters.md             <- Dream/MemoryMine cluster suggestions
    gap-map.md                    <- MemoryMine evidence gap detection
    pattern-summary.md            <- MemoryMine recurring structure detection
    staleness-map.md              <- MemoryMine staleness distribution
    unresolved-contradictions.md  <- Dream escalated contradictions
  runtime/                        <- vendor-neutral runtime contracts (I6)
    runtime-state.json            <- RuntimeProbe output (capability descriptors)
    runtime.json                  <- user override (optional)
  experiments/                    <- Evolution isolation space (I8)
    proposals/                    <- Synth proposals
    blueprints/                   <- Blueprint specs
    modules/                      <- Factory/Augment working area
    benchmarks/                   <- Benchmark reports
    rollback-<timestamp>/         <- Forge pre-promotion snapshots
  plans/                          <- planning artifacts
    v61/                          <- v6.1 planning documents
  receipts/                       <- operational receipts (I10)
  research-log/                   <- ResearchLog session records
    INDEX.md
    <session-id>.md
  checkpoints/                    <- Executor wave checkpoints
    <wave-id>/                    <- rollback state per wave
  _shared/                        <- shared infrastructure
    dev/
      languages/                  <- Node, Python, Go, Rust, Java
      databases/                  <- SQL, NoSQL, ORM, Migration
      api-consumption/            <- REST, GraphQL, gRPC, Realtime
    schemas/
      error-event.schema.json     <- typed error taxonomy
    references/
      development-patterns.md     <- cross-platform integration guidance
  platforms/                      <- L3 platform packages
    web/
    api-service/
    game/
    mobile/
    desktop/
    cli/
    iot-embedded/
    library-package/
    extension-plugin/
    data-pipeline/
    ai-agent/
  gateways/                       <- L4 capability gateways
    security/
    engineering/
    ai/
    aesthetic/
    design/
    experience/

project/repo/                     <- product source — hard boundary (I11)
```

---

### Four loading gates

| Gate | Trigger | What loads |
|---|---|---|
| Recipe | Build target identified | Platform package (L3), spec template variant, target rules |
| Stage | Planning stage entered (P1-P4) | Stage-appropriate modules |
| Phase | Phase entered (Research/Plan/Execute) | Phase references, schemas, eval modes |
| Activation | `skill-rules.json` pattern match | Individual module SKILL.md, rules, references |

Nothing preloads. Nothing activates without a matched gate.

**Gate collapsing:** Plan + Execute collapse allowed when Decompose scores < 0.3 AND spec depth is P1 only AND Recipe declares collapse-eligible. Collapse writes combined receipt.

---

### Spec hierarchy (P1-P4)

```
P1  Design Document             <- Recipe selects variant per build target
     L-- P2  Systems Design
              L-- P2  System Architecture
                   L-- P3  Technical Specifications
                            |-- P4  Feature Specs
                            |-- P4  Standards
                            L-- P4  Rules
```

P2 cannot begin until P1 spec is locked. P3 cannot begin until P2 is locked. Locking requires Verifier PASS.

---

### Data flow

```
User intent
  -> L0: Product (product goals, user segments) [new project]
  -> L0: Recipe (build target detection) -> loads L3 platform package
  -> L0: ReferenceLoad (staleness-tagged evidence loading)
  -> L0: RuntimeProbe (capability descriptor detection)
  -> L0: ScopeFrame (scope declaration)
  -> L1: Interview (ambiguity resolution) -> intent.md
  -> L1: Specify (spec artifact population P1-P4)
  -> L1: Propose (options with tradeoffs)
  -> L1: Decompose (wave plan, complexity score)
  -> L2: Guard (pre-wave input validation)
  -> L2: Executor (wave execution loop)
  -> L2: Verifier (post-wave verification)
  -> L7: Archive (receipt aggregation, version bump)
  -> L7: Package (artifact signing)
  -> L7: Deploy (deployment to declared environment)
  -> L7: Release (git tag, release notes, announcement)
  -> L8: Instinct (execution pattern observation)
```

Each arrow writes a receipt. Each phase reads upstream receipt before acting.

---

## 5. Module Anatomy

Every module follows this structure:

| Component | Required | Purpose |
|---|---|---|
| `SKILL.md` | Yes | Orchestration: process, routing, decision logic |
| `skill-rules.json` | Yes | Activation patterns, authority declaration, verification_mode, collapse_eligible |
| `schemas/receipt.schema.json` | Yes | Receipt structure for I10 compliance |
| `tests/acceptance.md` | Yes | Checkable acceptance criteria |
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

### skill-rules.json schema (core fields)

```json
{
  "module": "string",
  "layer": "L0|L1|L2|L3|L4|L5|L6|L7|L8",
  "activation": {
    "triggers": ["pattern strings"],
    "commands": ["/command-name"],
    "conditions": ["prerequisite conditions"]
  },
  "authority": {
    "reads": ["file paths or patterns"],
    "writes": ["file paths or patterns — exclusive ownership"]
  },
  "verification_mode": "Test|Review|Audit|Measurement|Observation|Attestation|Demonstration",
  "collapse_eligible": "boolean",
  "receipt_required": "boolean"
}
```

---

### Receipt base schema (core fields)

```json
{
  "module": "string",
  "session_id": "string",
  "generated_at": "ISO 8601",
  "phase": "Research|Plan|Execute",
  "runtime": {
    "selected": "capability descriptor",
    "reason": "string",
    "task_shape": "string"
  },
  "inputs": [
    {
      "artifact": "string",
      "staleness": "FRESH|AGING|STALE|EXPIRED|NEEDS_REVERIFICATION|SUPERSEDED",
      "staleness_flagged": "boolean"
    }
  ],
  "outputs": ["string"],
  "verification": {
    "mode": "string",
    "result": "PASS|FAIL|BLOCKED|REVISE",
    "revise_cycles": "integer"
  },
  "not_tested": ["string"],
  "confidence": 0.0
}
```

---

## 6. L0 — Intake Layer

L0 identifies the build target, loads references, detects runtime capabilities, declares scope, and captures product context. L0 runs before any spec or execution work.

---

### Product

Captures product goals, user segments, success metrics, and business constraints before P1 spec work begins. Product context is upstream of ScopeFrame and Interview — it captures the "why" before Interview captures the "what." Activates once per major product initiative or on `/product` command. Writes `product-context.md` to `.wabblespec/plans/`. Read by Interview, ScopeFrame, and Specify for goal alignment.

---

### Recipe

Identifies the build target from tech-stack signals (file names, dependencies, frameworks, project structure). Produces `recipe.json` with: primary build target, confidence score, secondary targets, collapse_eligible flag. Supports all 11 targets. Multi-target projects declare a primary + secondaries — no target is assumed. Confidence >= 0.8 auto-declares target; below threshold prompts Interview for confirmation.

---

### ReferenceLoad

Loads external references with source trust levels (HIGH/MEDIUM/LOW). Staleness recheck policy: STALE sources recheck before loading, EXPIRED sources require explicit override. No silent external calls — every reference load declares source and triggers ResearchLog. Writes loaded content to Memory as FRESH drawers with full Provenance records.

---

### RuntimeProbe

Detects available capabilities and writes `runtime-state.json` with eight vendor-neutral capability descriptors: code-generation, analysis, synthesis, instruction-following, reasoning, tool-use, vision, embedding. User can override via `runtime.json`. RuntimeProbe never writes model names — only capability descriptors. ModelRouter reads runtime-state.json to select the right capability for each task shape.

---

### ScopeFrame

Declares and enforces project scope. Produces `scope.md` with four sections: In Scope, Out of Scope, Assumptions, Change Log. All in-scope items must be traceable to spec artifacts. Change Log is append-only — never retroactively modified. Guards against scope creep (I12). Read by Guard for scope constraint validation before every Executor wave.

---

## 7. L1 — Spec Core Layer

L1 writes and maintains the spec hierarchy (P1-P4), decomposes work into wave plans, explores the codebase, resolves ambiguity, proposes options, executes the Apply gateway routing, and manages code-level cleanup, triage, migration, and test generation.

---

### Apply

Gateway routing engine. Reads the active platform package and capability gateway modules to determine which modules are relevant to the current wave. Assembles multi-module context using Economy's placement rules (constraints top, task end, references middle). Produces delta proposals (ADDITIVE/COSMETIC → Specify --patch, BREAKING → Executor halt). Writes only to `project/repo/` — never touches `.wabblespec/` (I11).

---

### Clean

Surface-level cleanup of product code. Removes dead code, normalizes formatting, renames identifiers to match EntityGraph canonical names, removes Specify-flagged deprecated patterns. Scope always declared explicitly — no unbounded clean. Classifies each change as COSMETIC, ADDITIVE, or BREAKING before applying. BREAKING changes halt and route to Executor. Full diff written to receipt.

---

### Decompose

Breaks work into wave plans. Each wave declares: modules, inputs, outputs, checkpoint path, rollback_to, verification_mode. Scores task complexity from five weighted factors (spec depth, cross-module dependency count, build target count, unknown surface area, spec confidence). Complexity score drives Autopilot autonomy level. Collapse-eligible when score < 0.3 AND P1 only AND Recipe eligible.

---

### Explore

Graph-first codebase discovery. Traverses from high-value nodes (entry points, config files, test files, dependency manifests) to produce `project-map.md` with: tech stack, spec artifacts, conventions, git state, gaps. Writes findings to Memory as FRESH drawers. EntityGraph notified for entity extraction. Per-target traversal order accounts for platform conventions.

---

### Interview

Resolves ambiguity before spec work begins. Nine ambiguity dimensions: intent, context, constraints, scope, success criteria, failure modes, stakeholders, timeline, risk tolerance. Socratic rules: no leading questions, max 3 per batch, stop when ambiguity resolved. Produces `intent.md` with confirmed answers. Reads product-context.md open questions before generating its own.

---

### Migrate

Plans and coordinates migration for BREAKING spec changes. Activates when Specify declares a BREAKING delta. Produces migration plan, optional migration script, and consumer-facing migration guide. Default: two-phase (additive phase backward-compatible, removal phase after migration gate confirmed). Single-phase only for internal consumers or security-critical changes. Migrate routes Phase 1 and Phase 2 as separate Executor waves.

---

### Propose

Generates 2-4 options for decisions with significant trade-offs. Five evaluation dimensions per option: complexity, time, risk, reversibility, fits scope. Recommendation required with rationale. No more than 4 options — forces real trade-off analysis. Proposal document written to `.wabblespec/plans/`. Reviewer consulted when budget gate triggers on proposals with HIGH impact or Attestation verification.

---

### Specify

Writes and maintains spec artifacts across the P1-P4 hierarchy using EARS syntax (Easy Approach to Requirements Syntax). Five EARS patterns: WHEN/THEN, IF/WHEN/THEN, WHILE/THEN, WHERE/SHALL, THE/SHALL. Each spec artifact includes: canonical_name, aliases, non-goals, anti-patterns, EARS requirements. Delta classification: BREAKING (triggers Migrate, Engineering review), ADDITIVE (notify downstream), COSMETIC (no coordination needed).

---

### Test

Generates test stubs from spec acceptance criteria. Every EARS requirement maps to at least one test case. Test type derived from EARS pattern (WHEN/THEN → positive + boundary cases; IF/WHEN/THEN → condition-not-met case; etc.). Platform-appropriate test framework from platform package. Untestable requirements flagged with reason, not silently skipped. Test plan written to `.wabblespec/plans/`. Stubs written to `project/repo/tests/`.

---

### Triage

Classifies incoming issues and routes them. Five types: Bug, Feature, Debt, Question, Security. Four severity levels: Critical, High, Medium, Low. Recurrence detection: same issue triaged twice escalates severity one level; third+ time escalates to High minimum and triggers Synth proposal. Routing table: Bug/Critical → Executor immediate; Feature → Interview → Specify; Security → Security gateway immediately; Debt → Clean or Executor; Question → Interview.

---

## 8. L2 — Orchestration Layer

L2 manages execution lifecycle, routing, verification, token density, multi-agent coordination, and rollback. It is the control layer through which all execution passes.

---

### Autopilot

Full lifecycle meta-orchestrator. Exclusively owns `.wabblespec/meta.md` — all other modules submit change requests rather than writing directly. Scale-adaptive: complexity < 0.3 = L0 (minimal), 0.3-0.5 = L1, 0.5-0.7 = L2, 0.7-0.9 = L3, > 0.9 = L4 (TeamPlan may activate). Activates for multi-stage runs, full lifecycle orchestration, or explicit `/autopilot` command. Triggers Dream after major execution waves. Manages Evolution pipeline scheduling.

**meta.md structure:**

```markdown
# Framework Meta State

**session_id:** string
**active_stage:** P1|P2|P3|P4|Execution|Delivery
**active_wave:** integer
**lifecycle_phase:** Research|Plan|Execute
**complexity_score:** 0.0-1.0
**autonomy_level:** L0|L1|L2|L3|L4
**counter_state:**
  revise_cycles: 0
  waves_completed: 0
  stages_completed: 0
**last_updated:** timestamp
```

---

### Economy

Token density management. Three operations: (1) Mechanical hedge removal — exact pattern matching against 20+ hedge phrases, no judgment required. (2) Context placement — constraints at top, active task at end, references in middle. (3) --budget mode — session token ceiling with hard stop. Five context types: creative, analytical, code, conversational, technical — each with appropriate density defaults. Economy does not manage voice register — that is Homowabian's domain.

---

### Ensemble

Coordinates multiple runtime lanes for tasks that no single lane covers adequately. Triggered exclusively by ModelRouter when Ensemble conditions are met. Three coordination modes: Sequential (Lane B needs Lane A output), Independent (parallel, independent artifacts), Cross-check (both run same task, Grader compares outputs). Cross-check required for Attestation and Audit verification modes. Writes combined receipt naming all lanes used.

**Trigger conditions (any one activates Ensemble):**
1. Task spans multiple build targets simultaneously
2. No single available lane covers all required capabilities
3. Verification mode is Attestation or Audit
4. Confidence below threshold after single-lane attempt

---

### Executor

Wave execution loop. Reads wave plan from Decompose. For each wave: (1) ModelRouter selects runtime lane, (2) Guard validates inputs, (3) Load modules per wave declaration, (4) Apply executes gateway routing, (5) Delta handling (ADDITIVE/COSMETIC proceeds, BREAKING halts), (6) Error routing by type, (7) Checkpoint write, (8) Verifier gates, (9) Wave receipt. Six error types with defined routing actions. Rollback to checkpoint on HARD error or Verifier BLOCKED — human confirms before restore.

---

### Guard

Pre-execution input validation. Four layers in sequence: (1) Schema validation — malformed inputs are HARD errors, (2) Scope constraint — out-of-scope targets are SPEC_VIOLATION errors routed to Reviewer, (3) Invariant compliance — checks all 12 invariants before wave execution, (4) Authority check — module must have declared authority over target files. Guard cannot be bypassed. No Executor wave proceeds without Guard PASS. Receipt written per wave.

---

### ModelRouter

Routes tasks to runtime lanes by capability descriptor. Reads runtime-state.json and task shape to select the best available capability. Context types (creative/analytical/code/conversational/technical) map to capability requirements. Evaluates Ensemble trigger conditions after initial routing decision. Writes routing receipt with selected capability, reason, task shape, fallback, and verification_mode.

---

### Reviewer

Budget-gated adversarial review. Contains two subagents: Adversary (generates counter-analysis — no reasoning shared with main context to prevent anchoring) and Grader (evaluates main analysis against spec). Budget gate triggers on: ambiguity > 0.4, confidence < 0.7, HIGH impact, or Attestation verification mode. When not triggered, modules proceed without adversarial review. Max 3 REVISE cycles per gate — hard limit. Fourth failure → Attestation required.

---

### Rollback

Controlled restoration to prior known-good state. Three rollback target types: wave checkpoint (Executor), deploy snapshot (Deploy receipt rollback_to field), Forge pre-promotion snapshot. All rollback operations require Attestation. Release rollback (git tag revert) is partially manual — Rollback provides instructions but does not execute git operations. Hash verification required after restoration.

---

### TeamPlan

Multi-agent coordination for genuinely complex tasks. Activates only at L4 autonomy or explicit `/teamplan` command. Every agent role has: scope (bounded, non-overlapping), inputs, outputs, handoff_to, handoff_condition, verification_mode, cannot_touch. `cannot_touch` is required on every agent — prevents scope bleed. No agent begins without receiving declared inputs from prior handoff. Verifier gates every handoff. Shared state policy: read-only references allowed, no concurrent writes.

---

### Verifier

Post-wave verification against all declared conditions. Seven verification modes with specific behavior per mode:

| Mode | Verifier behavior |
|---|---|
| Test | Runs test stubs, checks pass rate against declared threshold |
| Review | Structured critique against spec and code quality standards |
| Audit | Compliance checklist against spec, standard, or gateway requirements |
| Measurement | Quantitative threshold check (performance, coverage, quality metrics) |
| Observation | Behavioral check without automation — receipt declares what was observed |
| Attestation | Human sign-off required — Verifier cannot issue PASS without human confirmation |
| Demonstration | Working proof against real conditions — Verifier checks demonstration completeness |

Spec compliance check always runs regardless of mode. REVISE loop max 3 cycles per gate per wave. BLOCKED on: max REVISE exceeded, invariant violation, Attestation not received.

---

## 9. L3 — Platform Layer

Eleven platform packages, each self-contained with target-specific dev modules, engineering modules, security modules, spec template variant, and verification gates. Platform packages load via the Recipe gate when the build target is identified.

Each platform package follows this structure:
```
.wabblespec/platforms/<target>/
  SKILL.md                      <- routing logic, module load order
  skill-rules.json              <- Recipe activation signals
  spec-template/                <- target-specific P1-P3 template variants
  dev/                          <- platform-specific dev modules
  engineering/                  <- build toolchain, performance budgets
  security/                     <- threat model, platform controls
  verification/
    gates.md                    <- checkable verification gates for this target
```

Platform packages also load shared modules from `_shared/dev/` — languages, databases, api-consumption — on demand based on detected tech stack signals.

---

### Web

Frontend targets. Dev: React, NextJS, Vue, Svelte, Angular, HTML/CSS, Styling systems, PWA. Engineering: Vite/Webpack/Turbopack, bundle size budgets, Core Web Vitals. Security: CSP, XSS prevention, CORS allowlist, subresource integrity. Verification: Lighthouse CI, axe-core accessibility scan, bundle budget enforcement.

---

### API/Service

Server-side API targets. Dev: REST server (Express/Fastify/Gin/FastAPI/Actix), GraphQL server (Apollo/Strawberry/gqlgen), gRPC server, Realtime server. Engineering: containerization (multi-stage Dockerfile), health checks, graceful shutdown. Security: auth on every endpoint, input validation, rate limiting, OWASP API Security Top 10. Verification: contract tests, auth coverage (authenticated + unauthorized), load test baseline.

---

### Game

Game development targets. Dev: Engine patterns (Unity/Godot/Bevy/Unreal), TwoD, ThreeD, GamePhysics, GameAudio. Engineering: export targets declared, asset pipeline (atlas packing, compression), frame budget. Security: anti-cheat scope declared, save data encryption, network model (server-authoritative vs P2P). Verification: frame rate profiler baseline, input scheme testing, 10-minute smoke test per target platform.

---

### Mobile

iOS, Android, React Native, Flutter. Dev: Swift/UIKit/SwiftUI, Kotlin/Jetpack Compose, RN Metro/EAS, Dart/Flutter widgets. Engineering: code signing (Xcode automatic or manual, Android keystore), OTA update strategy. Security: minimum permissions, Keychain/Keystore for sensitive data, certificate pinning for financial/health apps. Verification: device matrix (minimum OS + latest OS), App Store compliance checklist, VoiceOver/TalkBack smoke test.

---

### Desktop

Electron, Tauri, native macOS (AppKit/SwiftUI), native Windows (WPF/WinUI). Dev: main/renderer separation, IPC patterns, context isolation (Electron), Tauri commands and permissions. Engineering: code signing (Apple notarization, Windows Authenticode), auto-updater. Security: Electron context isolation ON (non-negotiable), Tauri allowlist minimal, signed updates only. Verification: code signing verified, auto-update smoke tested, tested on all declared OS targets.

---

### CLI

Command-line tools. Dev: Commander/Yargs/Click/Typer/Cobra/Clap, output formatting, config conventions, distribution (npm/PyPI/Homebrew/binary). Engineering: single binary preferred for Go/Rust, startup time < 100ms, no unnecessary runtime dependencies. Security: all arguments validated, no shell injection, secrets via env vars or stdin (never positional args). Verification: --help output on all commands, exit codes verified, shell completions tested if declared.

---

### IoT/Embedded

Firmware and embedded targets. Dev: C/C++ (CMake patterns, MISRA guidance), MicroPython (MicroPython stdlib subset, asyncio), Embedded Rust (no_std, embassy/RTIC), firmware build (linker script, objcopy, upload toolchain). Engineering: cross-compile target triple declared, vendor dependencies, flash/RAM budget. Security: signed OTA, JTAG/SWD disabled in production, hardware security element for key storage. Verification: firmware builds for target in CI, runs on hardware or declared emulator, memory within budget.

---

### Library/Package

Distributable libraries. Dev: API surface design, semver, registry publishing, doc generation. Engineering: dual ESM+CJS output (JS), type declarations shipped, tree-shakeable, source maps. Security: no typosquatting risk, no postinstall scripts, minimal transitive dependencies, 2FA on registry account. Verification: public API reviewed before minor/major bump, no `any` in public types, all public exports documented.

---

### Extension/Plugin

Browser extensions and IDE plugins. Dev: Chrome MV3 manifest, VS Code extension API, host sandbox patterns. Engineering: webpack/rollup bundle, vsce package, store review requirements. Security: minimum permissions, MV3 CSP enforced, all messages validated, no eval(). Verification: permissions audited, no CSP violations, store review checklist passed.

---

### Data/Pipeline

ETL, streaming, and orchestration targets. Dev: ETL patterns (idempotency, incremental/full load), Streaming (Kafka/Pulsar consumer patterns), Orchestration (Airflow/Prefect DAG patterns), Schema evolution. Engineering: containerized pipeline components, data quality gates (Great Expectations or equivalent). Security: data classification (PII/sensitive declared), encryption at rest + in transit, least-privilege per pipeline stage, audit log. Verification: data quality gates on sample dataset, idempotency verified, schema backward compatibility checked.

---

### AI/Agent

LLM and agent targets. No separate dev module — fed entirely by L4 AI gateway. Engineering: model version pinned, prompts versioned, eval harness required. Security: prompt injection hardening, minimum-permission tools, all LLM output validated, no PII in prompts without DPA. Verification: eval suite passes declared dimensions, tool scope reviewed, cost within declared budget.

---

## 10. L4 — Capability Gateways

Six cross-cutting gateways apply regardless of build target. Platform packages feed target-specific concerns upward to the gateway; the gateway feeds cross-cutting policy downward to Apply.

---

### Security Gateway

Cross-cutting scope: threat modeling (STRIDE), OWASP checklists (Web Top 10, API Top 10, Mobile Top 10), ASVS levels, continuous security cycles (dependency scanning, SAST, secret scanning, penetration testing), compliance frameworks (GDPR, SOC 2, HIPAA, PCI-DSS).

Rules: every external endpoint declares auth requirement; session management (tokens expire, refresh tokens rotate); MFA for admin interfaces; secrets in vault or env vars only; rotation policy on exposure.

Verification: Audit mode — security checklist completed, threat model present, no critical/high SAST findings, no secrets in repo.

---

### Engineering Gateway

Cross-cutting scope: CI/CD patterns (pipeline stages: lint → test → build → security scan → deploy), architecture review (ADR required for framework-selection decisions), reliability principles (SLOs declared, error budgets derived, circuit breakers required for external calls), systems design standards (CAP theorem trade-offs declared, idempotency declared for state mutations).

Rules: ADR required for major decisions; test coverage floor declared per project; integration tests required for external integrations; E2E tests required for critical user journeys.

Verification: Review mode — architecture reviewed, ADRs present, CI pipeline declared, SLO documented.

---

### AI Gateway

Applies to any target embedding AI features, not only the AI/Agent build target.

Cross-cutting scope: prompt engineering (system prompt versioned and tested, few-shot examples curated), chain design (each step has declared input/output schema), agent architecture (tools with declared schemas, bounded loops, human-in-the-loop for irreversible actions), evaluation (dimensions declared, dataset versioned, regression on every model/prompt change), safety (output validation, PII policy, bias eval, refusal handling).

Rules: model version pinned — never `latest` in production; eval suite required before any prompt or model change ships; no PII in prompts without explicit DPA.

Verification: Measurement mode — eval suite passes declared thresholds, model pinned, token budget declared, safety evaluated.

---

### Aesthetic Gateway

Visual design, brand identity, style systems. Color (semantic tokens, WCAG AA minimum 4.5:1 text contrast — non-negotiable, dark mode declared). Typography (modular scale, variable fonts, font-display: swap). Motion (purposeful, prefers-reduced-motion respected — non-negotiable). Design tokens for all visual values — no raw values in component code.

Verification: Review mode — design token system present, contrast ratios pass, reduced motion handled, brand assets correctly referenced.

---

### Design Gateway

UX, interaction design, information architecture, design systems. User flows completable, affordances communicated, feedback on every action < 100ms or loading indicator. Touch targets minimum 44x44px (mobile), keyboard accessible, focus management on state change. WCAG 2.1 AA minimum — non-negotiable. Component library declared. Storybook required for component-heavy projects.

Verification: Demonstration mode — user flows completable, keyboard nav works, touch targets pass, design system documented.

---

### Experience Gateway

User research, usability testing, accessibility, satisfaction measurement. Activated when research is declared in scope at P1. User research method chosen per question type. Minimum 5 participants for usability tests. Research artifacts written to Memory as FRESH drawers. Accessibility matrix tested: VoiceOver, NVDA/JAWS, TalkBack — scope declared per project. Research ethics: informed consent required, data anonymized.

Verification: Demonstration mode — usability test conducted (if in scope), accessibility matrix tested, insights written to Memory.

---

## 11. L5 — Memory Layer

L5 manages all persistent knowledge in the framework. Memory is the evidence store. EntityGraph is the relationship index. Provenance tracks source trust. Dream consolidates in background. MemoryMine discovers patterns across evidence. Forget provides controlled deletion. MemorySearch retrieves on demand.

---

### Memory

Evidence store with staleness tracking. Every drawer is a plain markdown file with staleness metadata header. Six staleness states enforced by I9. Write workflow: store with FRESH state, write Provenance record, notify EntityGraph. Read workflow: check staleness before returning, flag STALE/EXPIRED in response. Transition workflow: triggered by Dream on configured thresholds.

**Drawer format:**

```markdown
---
drawer_id: string
topic: string
staleness: FRESH|AGING|STALE|EXPIRED|NEEDS_REVERIFICATION|SUPERSEDED
confidence: 0.0-1.0
source_module: string
written_at: ISO 8601
last_verified_at: ISO 8601
superseded_by: drawer_id (if SUPERSEDED)
---

[evidence content]
```

---

### EntityGraph

Relationship index. Nodes.json (entity registry) and edges.json (relationship registry). Seven entity types: module, file, person, service, concept, standard, technology. Seven relationship types: depends-on, implements, calls, extends, replaces, contradicts, cites. Entity extraction by deterministic pattern matching — not LLM inference. Low-confidence entities included with confidence < 0.5, not excluded. Dream triggers cleanup: orphaned nodes removed, confidence recalculated, contradicting edges flagged.

---

### Dream

Background memory consolidation. Never runs during active execution. Five consolidation tasks: (1) Staleness decay — apply FRESH→AGING→STALE→EXPIRED transitions, (2) Pattern decay — EMA decay on tracker.json patterns below threshold, (3) Evidence clustering — flag clusters for potential consolidation (suggest only, no auto-merge), (4) EntityGraph cleanup — remove orphaned nodes, recalculate confidence, (5) Contradiction resolution — auto-resolve expired contradictions, escalate age-old contradictions to human. Triggers: session end, explicit `/dream` command, N new drawers threshold (default 20), Autopilot post-wave schedule.

---

### MemoryMine

Deep pattern mining across full Memory evidence store. Four operations: (1) Gap detection — spec-declared concepts absent from Memory, (2) Cluster detection — entity overlap and keyword similarity clustering, (3) Pattern extraction — recurring structures, repeated decision patterns, contradiction clusters, (4) Staleness map — distribution across staleness states, EXPIRED orphan risk flags. Never runs during active execution. Writes gap-map.md, mine-clusters.md, pattern-summary.md, staleness-map.md.

---

### MemorySearch

On-demand evidence retrieval. Six query types: topic, entity, relationship, recency, staleness, full-text. Staleness enforcement: EXPIRED evidence returned with explicit flag, not silently. Ranking: confidence → staleness → recency. Entity and relationship queries delegate to EntityGraph for traversal. Returns drawer IDs, staleness states, and confidence scores — not raw content (caller loads drawers on demand).

---

### Provenance

Source trust tracking. Every Memory drawer has a Provenance record. Four trust levels: HIGH (official docs, specs, test outputs), MEDIUM (code inspection, configuration), LOW (inference, assumption, second-hand report), UNVERIFIED (loaded but not cross-checked). Contradiction tracking: when new evidence contradicts existing, both records flagged with contradiction_with reference. Cascade computation: BREAKING changes to high-cited drawers propagate NEEDS_REVERIFICATION to all drawers citing them. Append-only ledger.md records all changes, deletions, and contradiction resolutions.

---

### Forget

Controlled deletion — the only module authorized to delete Memory drawers. Deletion types: single (confirmation prompt), bulk EXPIRED (Attestation required), compliance/GDPR (Attestation + documented legal basis). Process: write Provenance deletion record FIRST, then delete file, then remove from index, then notify EntityGraph, then cascade NEEDS_REVERIFICATION to citing drawers. Deletion record in Provenance ledger.md is permanent — never removed. No silent deletion.

---

## 12. L6 — Expression Layer

L6 manages how framework output is shaped, refined, documented, and recorded. Economy (L2) handles token density — L6 handles voice register, documentation generation, artifact refinement, and research capture.

---

### Homowabian

Voice register management. Four registers:

| Register | Usage | Characteristics |
|---|---|---|
| lite | Status updates, brief outputs, fragments | Fragments OK, no multi-paragraph prose, no trailing summaries |
| full | Synthesis, analysis, structured content | Dense prose, headers and tables for structure, complete sentences |
| ultra | Data-dense outputs, reference tables | Data only, minimal prose, maximum density |
| normal | Code, commits, security warnings, irreversible actions, Attestation content | Standard English, full sentences, no compression |

Auto-switch rules: irreversible actions → normal (always). Security warnings → normal. Attestation content → normal. Code blocks → normal regardless of surrounding register.

---

### Document

Generates long-form documentation artifacts from spec content and execution receipts. Types: README (from P1 spec, scope.md, project-map.md), Architecture guide (from P2 spec, ADRs), API reference (from P3 spec), Onboarding (from README, project-map.md, dev modules), Decision log (from all ADRs), Changelog (from Archive receipts). All content traceable to source artifacts — no invented content. STALE/EXPIRED sources flagged in output, not silently used. Writes to `project/repo/docs/`.

---

### Polish

Refinement pass on generated artifacts. Four passes in sequence: (1) Register enforcement — verify active Homowabian register applied correctly, (2) Redundancy removal — detect and remove repeated explanations, trailing summaries, hedge phrases, (3) Structural consistency — table formatting, code block labeling, heading hierarchy, internal link validity, (4) Spec compliance check — prose claims don't contradict spec, entity names match EntityGraph canonical names, no deprecated terms. Full diff written to receipt before overwriting. Cannot touch code files, schemas, or receipts.

---

### ResearchLog

Structures research sessions into persistent Memory entries. Triggered after ReferenceLoad, Explore, or any Research phase. Log entry structure: Investigated (sources), Findings (confirmed with citations), Discarded (rejected with reasons), Gaps (unresolved), Memory Writes (drawer IDs created). Discarded findings are NOT written to Memory — only to the log entry. One drawer per distinct finding, not per session. Provenance record written for each drawer. EntityGraph notified.

---

## 13. L7 — Delivery Layer

L7 manages the full delivery pipeline: version archiving, artifact preparation and signing, deployment, release coordination, observability configuration, and project scaffolding for new projects.

---

### Archive

Receipt aggregation and version management. Reads all receipts from the current execution cycle. Applies semantic version bump: BREAKING → major, ADDITIVE → minor, COSMETIC → patch. Writes changelog entry. Compiles not-tested list from all receipts. Notifies Instinct on release (pattern signal). --sweep mode: delegates EXPIRED drawer removal to Forget. --entomb mode: archives full project state. Activates after Verifier passes all delivery gates.

---

### Deploy

Executes deployment of signed artifacts to declared environments. Reads artifact manifest from Package. Requires: Deploy receipt from prior environment (for promotion), Attestation for production deployments. Rollback plan must be declared before Deploy activates — not invented during failure. Post-deploy verification: health check, smoke test, latency baseline. Trigger detection for rollback condition is automatic; rollback execution requires human confirmation. Writes deploy receipt with snapshot of prior deployment as rollback target.

---

### Monitor

Generates observability configuration. Reads Engineering gateway SLO declarations and platform-appropriate monitoring patterns. Produces: metric definitions aligned to SLO, alert rules derived from SLO thresholds, structured log schema (JSON, required for server-side targets), health check config, dashboard template (Grafana/CloudWatch skeleton), OpenTelemetry tracing config. Writes config to `project/repo/monitoring/`. Activates after Deploy.

---

### Package

Prepares and signs deployment artifacts from build output. Artifact types vary by platform (Docker image, .ipa/.aab, .dmg/.exe, binary, npm tarball, firmware binary). Signing is required — no unsigned artifacts proceed to Deploy. Artifact manifest written with: artifact_id, version, built_from (git SHA), artifact hash (SHA-256), signing method, provenance chain (references Executor and Archive receipts). Signing failure is HARD error.

---

### Release

Final release coordination. Activates after Deploy confirms production deployment. Git tag created (annotated, with release notes summary), pushed with Attestation. Release notes synthesized from Archive changelog — no invented content. Known issues compiled from Verifier not-tested list and open decisions flagged at ship. GitHub Releases (or declared equivalent) published. Notifies Archive (marks version RELEASED) and Instinct (release cycle signal).

---

### Scaffold

Generates initial project structure for new projects. Activates once — at project creation. Idempotency guard: refuses to run if project-map.md already exists. Reads active platform package to generate correct directory structure, config files, CI pipeline skeleton, spec template, .gitignore. Does not generate application code — structure only, with TODO markers. Triggers Explore after generation to produce initial project-map.md.

---

## 14. L8 — Evolution Layer

L8 enables framework self-improvement through evidence-driven pattern learning and controlled module modification. All Evolution writes go to `.wabblespec/experiments/` until Forge promotes. Active execution reads no experiment content unless explicitly loaded for evaluation.

---

### Instinct

Passive execution observer. Writes `tracker.json` (sole writer — Dream decays). Observes: wave execution outcomes, Verifier gate results, error type frequencies, Reviewer budget gate triggers, Decompose complexity vs. actual difficulty, Homowabian auto-switches. Confidence formula: `confidence_new = confidence_old * 0.9 + outcome * 0.1` (EMA). New pattern starts at 0.5. Confidence >= 0.8 eligible for Synth. Notified by Archive on release and Deploy on deployment.

---

### Synth

Synthesizes high-confidence Instinct patterns into improvement proposals. Clusters related patterns by category and evidence overlap. Each proposal declares: problem, evidence, proposed direction, affected modules, blast radius (low/medium/high), reversibility, self-modifying flag. Proposals written to `experiments/proposals/`. Triggers after N Instinct runs (default 10) or when >= 3 high-confidence patterns emerge in one category.

---

### Blueprint

Converts Synth proposals into concrete, implementable specs. Produces the equivalent of a P3 Technical Specification for a framework improvement: EARS requirements, declared new/modified/deleted files, acceptance criteria (must be checkable by Benchmark), rollback specification. Blueprint spec_type: new-module, modify-existing, schema-change, rule-change. Written to `experiments/blueprints/`.

---

### Factory

Generates new module scaffolding from Blueprint specs. Creates directory structure, SKILL.md skeleton (with Blueprint requirements embedded), skill-rules.json template, receipt schema stub, acceptance.md from Blueprint acceptance criteria. Does not write implementation content — structure and contracts only. Augment fills in content. Writes only to `experiments/modules/`.

---

### Augment

Applies content to Factory-scaffolded modules or existing module improvements. For new modules: fills in SKILL.md content, rules/, references/, evaluations/. For existing modifications: copies current live module to experiments/, applies declared changes. Applies only changes declared in Blueprint — no scope expansion. Writes only to `experiments/`. Never touches live framework files.

---

### Benchmark

Evaluates experiments against Blueprint acceptance criteria. Six evaluation dimensions: acceptance criteria completeness, EARS requirements addressed, scope adherence (no undeclared modifications), rollback viability, self-modification risk (flagged for Attestation), integration compatibility. Verdict: PASS (proceed to Forge), FAIL (return to Augment), CONDITIONAL (conditions must resolve before Forge). Benchmark report written to `experiments/benchmarks/`.

---

### Forge

Promotes validated experiments to live framework. Most restricted module. Every promotion requires Attestation. Self-modifying promotions (changes to Evolution modules themselves) require double Attestation (two separate human confirmations). Pre-promotion snapshot always written to `experiments/rollback-<timestamp>/`. Post-promotion hash verification — automatic restore from snapshot if verification fails. Notifies Archive for framework version bump.

---

### Feedback

Captures explicit human evaluation signals. Five types: Correction (negative, high signal), Preference (soft negative), Complaint (negative, flags for Synth), Endorsement (positive), Question (clarity gap for Interview). Writes feedback records to Memory as FRESH drawers. Notifies Instinct with confidence direction and signal strength. Routes actionable feedback: corrections → Triage, complaints → Synth, questions → Interview.

---

### Retro

Structured retrospective after each release cycle. Reads Instinct tracker.json, all cycle receipts, Verifier not-tested lists, and open decisions. Draft produced by framework; human reviews before routing. Three sections: What Worked (positive patterns, clean gates), What Didn't (negative patterns, REVISE-heavy waves, not-tested items), What Changes (Synth proposals and Triage records). Status: DRAFT until human confirms. No Synth or Triage routing without human confirmation.

---

## 15. Shared Infrastructure

### _shared/dev/ — Language modules

Five language reference libraries loaded by platform packages on demand. Detection by tech-stack signals (package manager files, build configs, language-specific imports).

| Module | Covers |
|---|---|
| Node | JavaScript, TypeScript — all JS-family targets. ESM preferred, CJS legacy only with justification. npm/yarn/pnpm with lockfile. TypeScript strict mode. |
| Python | API/Service, Data/Pipeline, AI/Agent, CLI, IoT. uv preferred, minimum Python 3.11. ruff for lint+format. Type hints required for library code. |
| Go | API/Service, CLI, Desktop. go.mod + go.sum committed. gofmt/goimports non-negotiable. Table-driven tests. Goroutine lifecycle always declares exit condition. |
| Rust | CLI, IoT/Embedded, Library/Package, Desktop. Cargo.lock committed for binaries. rust-toolchain.toml. rustfmt + clippy warnings-as-errors in CI. thiserror for library errors, anyhow for application errors. |
| Java | API/Service, Mobile (Android), Desktop. Gradle (Kotlin DSL) preferred. Java 21+ LTS. Records for immutable data. Optional for nullable return. |

---

### _shared/dev/ — Database modules

Four database reference libraries. Detection by connection string env vars, ORM config files, migration directories, database-specific packages.

| Module | Covers |
|---|---|
| SQL | PostgreSQL (JSONB, CTEs, EXPLAIN ANALYZE), MySQL (utf8mb4, InnoDB), SQLite (WAL mode, single-writer). Parameterized queries mandatory. Transaction scope short. Least-privilege in production. |
| NoSQL | MongoDB (collection-level validation, no unbounded arrays), Redis (TTL on all cache keys, not primary store), DynamoDB (access-pattern-first), Firestore (subcollections, Security Rules required). |
| ORM | Prisma (generated client, never edit), SQLAlchemy (Core for complex, ORM for CRUD), GORM (explicit preloading), Hibernate (second-level cache justified), Drizzle (schema-as-code). |
| Migration | Sequential or timestamp-prefixed files. Up + down required. Idempotent. Two-phase for destructive changes. Transaction wrapping where database supports. |

---

### _shared/dev/ — API Consumption modules

Four API client reference libraries (client-side only — server-side in API/Service platform package). Detection distinguishes client usage from server-side frameworks.

| Module | Covers |
|---|---|
| REST | Single configured HTTP client instance per service. Parameterized auth (bearer, API key, OAuth 2.0, mTLS). Retry policy: idempotent methods retry on 5xx, non-idempotent only on pre-receive network error. Exponential backoff with jitter. |
| GraphQL | Queries in .graphql files, not inline strings. Code generation from schema. Partial success (data + errors) handled explicitly. Normalized cache for web clients. |
| gRPC | One channel per service. Deadline on every RPC call. PerRPCCredentials for auth. Status codes (not HTTP codes). DEADLINE_EXCEEDED never retried. |
| Realtime | Single WebSocket per logical session. Auth token in first message, not URL. Heartbeat-based connection loss detection. Exponential reconnect with jitter. |

---

### _shared/schemas/ — Error taxonomy

`error-event.schema.json` defines six error types with routing actions:

| Type | Meaning | Default routing |
|---|---|---|
| SOFT | Recoverable, retry viable | Retry up to 3 times, then escalate |
| HARD | Unrecoverable, halt required | Abort wave, route to human |
| DEPENDENCY | Upstream module failed | Wait for upstream resolution |
| CONTEXT_EXHAUSTION | Context limit hit | Checkpoint, resume in new context |
| SPEC_VIOLATION | Output contradicts spec | Route to Reviewer, then Attestation |
| STALENESS_VIOLATION | Expired evidence used without flagging | Flag drawer, route to Reviewer |

---

## 16. Three-Phase Model

Every stage (P1-P4) and every Executor run follows the three-phase model:

**Research phase:** Load references, search Memory, explore codebase. ReferenceLoad + MemorySearch + Explore. Writes Research receipt and ResearchLog entry.

**Plan phase:** Write spec artifacts, generate options, decompose into waves. Specify + Propose + Decompose. Writes Plan receipt.

**Execute phase:** Run wave loop. Guard + Executor + Apply + Verifier. Writes Execute receipt and Wave receipts.

No phase begins without the prior phase's receipt. No stage advances without all three phase receipts present.

---

## 17. Verification Modes

| Mode | When used | Verifier behavior |
|---|---|---|
| Test | Automated assertion against known inputs | Runs test stubs, checks pass rate |
| Review | Structured critique | Agent or human review against spec and quality standards |
| Audit | Compliance check | Checklist against spec, standard, or gateway requirements |
| Measurement | Quantitative threshold | Metric check against declared threshold |
| Observation | Behavioral without automation | Declares what was observed, checks behavioral conditions |
| Attestation | Human sign-off | Cannot PASS without human confirmation — irreversible actions |
| Demonstration | Working proof | Checks demonstration completeness against real conditions |

REVISE loop: max 3 cycles per gate per wave. Resets per gate, per wave. Fourth failure → BLOCKED → Attestation required.

---

## 18. Scale-Adaptive Orchestration

### Autonomy levels

| Complexity score | Autonomy level | Orchestration behavior |
|---|---|---|
| < 0.3 | L0 | Collapse-eligible. Minimal orchestration. Executor directly. |
| 0.3-0.5 | L1 | Single-stage run. Executor manages waves. |
| 0.5-0.7 | L2 | Multi-stage. Autopilot routes between stages. |
| 0.7-0.9 | L3 | Full lifecycle. Autopilot manages all phases. |
| > 0.9 | L4 | Complex multi-stage. TeamPlan may activate. |

### Complexity scoring (Decompose)

Five weighted factors:
1. Spec depth required (P1 = 0.2, P4 = 1.0)
2. Cross-module dependency count (0-1.0 normalized)
3. Build target count (1 target = 0.2, multiple = 0.8)
4. Unknown surface area (% of codebase not yet in Memory)
5. Spec confidence score inverse (low confidence = higher complexity)

Weighted sum normalized to 0.0-1.0.

---

## 19. Key Boundaries

| Boundary | Rule | Enforcement |
|---|---|---|
| Framework / Product | `.wabblespec/` and `project/repo/` never mix | Guard Layer 4, Apply write authority |
| Plan / Execute | Distinct contexts, distinct receipts | Autopilot phase management, receipt chain |
| Experiment / Production | Evolution writes to experiments/ until Forge promotes | Augment write authority, Forge as sole promoter |
| Module authority | Each output has one declared owning module | skill-rules.json authority declaration, Guard Layer 4 |
| Receipt chain | No phase acts without upstream receipt | Guard Layer 3 (I10 check), Autopilot stage gates |
| Evidence trust | No expired evidence used without flagging | Guard Layer 3 (I9 check), STALENESS_VIOLATION error type |
| Self-modification | Evolution cannot promote changes to themselves without double Attestation | Forge double-Attestation rule, Benchmark self-modification flag |

---

## 20. Planning Index

All planning artifacts for v6.1 live in `.wabblespec/plans/v61/`:

| File | Contents |
|---|---|
| `01-INVARIANTS.md` | All 12 invariants fully expanded |
| `02-ARCHITECTURE.md` | Full architecture: layer map, gateway map, directory layout, loading gates, data flow |
| `03-CORE-FEATURES.md` | 14 core feature groups with full detail |
| `04-SKILLS-FLOW.md` | 10 operational flow diagrams |
| `05-MODULE-IMPORTANCE.md` | Tier 1-5 module classification, dependency chains, 15-priority planning order |
| `modules/P1-SCHEMAS.md` through `modules/P15b-FORGET.md` | Per-module planning artifacts for all ~55 modules |

Thematic long-form documents (this document and companions) are the authoritative reference for the framework as a whole. Per-module planning artifacts are the authoritative reference for individual module implementation detail.
