# WabbleSpec v6.1 — Standalone Module Integration Plan

**Date:** 2026-05-23  
**Scope:** All 26 missing standalone modules from v5.3 + required shared infrastructure  
**Excludes:** Gateway sub-modules (Security leaf modules, Development leaf modules, etc.) — separate plan after v4–v5.2 gateway architecture review  
**Source spec:** WabbleSpec v5.3 Core.md  

---

## 1. Architectural decisions locked before any build

### 1.1 Layer mapping (v6.1 layer scheme)

v6.1 layers are not v5.3 layers. Every new module goes into the v6.1 layer that matches its function:

| v5.3 Module | v6.1 Target Layer | Rationale |
|---|---|---|
| Enhance | L1 | Pre-spec input processing |
| Sharpen | L1 | Pre-spec input narrowing |
| Brainstorm | L1 | Pre-spec divergent exploration |
| Plan | L1 | Spec lifecycle — sits between Propose and Decompose |
| Adversary | L2 | Extracted from Reviewer — orchestration-level evaluator |
| Grader | L2 | Extracted from Reviewer — orchestration-level scorer |
| Analyze | L1 | On-demand quality investigation |
| Perf | L1 | On-demand performance work |
| Deps | L1 | On-demand dependency health |
| Audit | L2 | Cross-cutting compliance (same tier as Guard) |
| Nexus | L5 | Tribal knowledge — lives in memory layer, cross-invokable |
| Shift | L1 | Spec semantic versioning — spec lifecycle |
| Sync | L1 | Spec reconciliation — spec lifecycle |
| Organize | L1 | Project file hygiene — on-demand |
| Flag | L1 | Feature flag lifecycle — dev lifecycle |
| API | L1 | API lifecycle management — dev lifecycle |
| Proofread | L6 | Output/expression quality gate |
| Markdown | L6 | Output formatter |
| Copy | L6 | UI micro-text — expression layer |
| Writer | L6 | Long-form content — expression layer |
| Legal | L6 | Compliance documents — expression layer |
| Translate | L6 | i18n/l10n — expression layer |
| Optimize | L6 | Discoverability — expression layer |
| Market | L6 | Marketing strategy — expression layer |
| Changelog | L7 | Delivery artifact — sits alongside Release |
| Commit | L7 | Delivery artifact — final delivery step |

### 1.2 Adversary + Grader extraction (BREAKING internal surgery)

**Current state:** Reviewer (l2/reviewer/SKILL.md) embeds all Adversary + Grader logic inline. agents/adversary.md and agents/grader.md are sub-agent role stubs only — not invokable modules.

**Target state:**
- `modules/l2/adversary/SKILL.md` — full standalone module with its own SKILL.md, skill-rules.json, schemas, rules
- `modules/l2/grader/SKILL.md` — full standalone module
- `modules/l2/reviewer/SKILL.md` — updated to delegate to Adversary and Grader explicitly; no logic duplication
- `modules/l2/reviewer/agents/adversary.md` — becomes a thin invocation reference, not a full spec
- `modules/l2/reviewer/agents/grader.md` — same

**Why this is worth the surgery:**
- Any module can now call Adversary directly (Specify before locking, Decompose before wave execution, Plan before commitment)
- Grader can be called by any module that needs scoring, not only via Reviewer's full cycle
- Reviewer's external interface (receipt schema) does NOT change — consumers are unaffected
- Without this extraction, every future module that needs adversarial challenge has to call Reviewer as a full cycle even when it only needs one component

**External interface contract preserved:**
- Reviewer receipt schema unchanged
- Reviewer still emits `triggered: true|false`, `verdict: ACCEPT|REVISE|ESCALATE`, `revise_cycles`
- framework.yaml consumers list for Reviewer unchanged

### 1.3 Pipeline wiring for new modules

Updated pipeline after all phases complete:

```
Recipe
  → [Enhance] (when input vague — triggered by Recipe)
  → [Sharpen] (when input broad — triggered by Recipe)
  → ScopeFrame
  → [Brainstorm] (on-demand, pre-Specify)
  → [Interview] (on-demand)
  → Specify
    → [Adversary] (budget-gated, BREAKING delta class)
  → Propose
  → [Plan] (on-demand or Autopilot-triggered for L2+)
    → [Adversary] (budget-gated)
    → [Grader]
  → Decompose
  → [Ground]
  → Executor
  → Verifier
  → [Reviewer] (budget-gated)
  → [Polish] (Review → Clean → Proofread → Markdown → Changelog → Commit)
  → [Flag --rollout] (if flag exists)
  → Deploy
  → Archive
    → [Shift] (if spec changed)
  → Retro (periodic)

On-demand (no fixed position):
  Analyze, Triage, Perf, Deps, Organize, Audit, Nexus, Sync, API
  Adversary (direct), Grader (direct)
```

### 1.4 Enhance + Sharpen trigger strategy

**Decision:** Auto-triggered from Recipe, not from ScopeFrame. Recipe already classifies complexity — it can also classify input quality. Recipe adds two new detection outputs: `input_vague: boolean` and `input_broad: boolean`. If vague → Enhance runs. If broad → Sharpen runs. If both → Enhance then Sharpen.

**Why not ScopeFrame:** ScopeFrame assumes input is reasonably clear — it frames scope, not expands intent. Pushing vague input to ScopeFrame produces bad scope.md. Better to fix input quality before scope is touched.

**Recipe surgery needed:** Add input_vague and input_broad detection to Recipe's rules/target-detection.md and routing logic.

### 1.5 Shared infrastructure strategy

v6.1 currently has no `_shared/infrastructure/` directory. v5.3 uses it for framework config and lifecycle specs (economy-principles, guard-policy, gateway-pattern, security-cycle, etc.).

**Decision:** Create `_shared/infrastructure/` for framework-configuration-level files only. Do NOT mix with `_shared/references/` (domain knowledge). The distinction:

- `_shared/infrastructure/` — how the framework runs (economy principles, guard defaults, gateway patterns, version tracking protocol)
- `_shared/references/` — what modules know (domain knowledge, attack patterns, compression rules, LSP availability)

New `_shared/references/` files go through framework.yaml `shared.references` list with explicit consumers declared. No reference file is added without at least one declared consumer.

### 1.6 framework.yaml update protocol

Every new module added to this plan requires a framework.yaml entry with:
- `id`: kebab-case module name
- `path`: correct modules/lN/name/ path
- `type`: skill or script
- `layer`: correct L-level
- `tags`: accurate search terms
- `produces_schemas`: any schemas the module writes
- `consumes_schemas`: schemas it reads
- `depends_on`: upstream modules required
- `last_validated`: "" (empty until first validated run)
- `quality_floor_passed`: false (set to true after passing quality-floor-check)
- `build_status`: planned → built → validated

---

## 2. Modules that need surgery (existing modules to modify)

Before building anything new, document exactly what changes existing modules need. These are changes, not new files.

### 2.1 Reviewer (l2/reviewer/SKILL.md)

**Changes needed (Phase 1):**
1. Remove inline Adversary analysis logic — replace with "invoke Adversary module, pass primary output"
2. Remove inline Grader evaluation logic — replace with "invoke Grader module, pass primary output + Adversary counter-analysis + spec artifact"
3. Keep: budget gate check, REVISE loop management, receipt writing
4. Update agents/adversary.md and agents/grader.md to be delegation stubs
5. Keep all receipt fields unchanged

**SKILL.md diff (concept):**
- Step 2 changes from "Adversary produces counter-analysis [inline spec]" to "Route primary output to `l2/adversary`. Adversary returns counter-analysis."
- Step 3 changes from "Grader evaluates [inline spec]" to "Route primary output + counter-analysis + spec artifact to `l2/grader`. Grader returns verdict."
- The REVISE loop (Step 4) remains in Reviewer — it manages the cycle, not the evaluation logic

### 2.2 Recipe (l0/recipe/SKILL.md)

**Changes needed (Phase 2):**
1. Add input quality classification to detection step: `input_vague: boolean`, `input_broad: boolean`
2. Add routing: if `input_vague` → invoke Enhance before ScopeFrame; if `input_broad` → invoke Sharpen before ScopeFrame; if both → Enhance → Sharpen
3. Add to receipt schema: `input_quality: { vague: boolean, broad: boolean, enhanced: boolean, sharpened: boolean }`

**Detection rules (go into rules/target-detection.md update):**
- Vague: input contains no specific artifact, no measurable outcome, no named component, no constraint
- Broad: input contains more than one viable interpretation at equal plausibility, no priority signal
- Both are independent — a vague input can also be broad

### 2.3 Autopilot (l2/autopilot/SKILL.md)

**DEFERRED — 2026-05-23.** Autopilot surgery postponed until all 26 standalone modules are built and wired. The orchestration layer should not be modified until it has a stable, complete module inventory to route against. All Phase 2 and Phase 3 Autopilot surgical items are removed from scope. Autopilot surgery will be planned separately after integration is complete.

### 2.4 Archive (l7/archive/SKILL.md)

**Changes needed (Phase 3):**
1. Add post-archive hook: if spec changed (delta_class = BREAKING or ADDITIVE with spec touch), invoke Shift for semantic diff
2. Add Shift result to archive receipt: `shift_triggered: boolean`, `shift_receipt_path: string`
3. *(v5.2)* Add `--sweep` mode: batch scan for EXPIRED entries (staleness ≥ 50 changes), batch entomb them in one operation
4. *(v5.2)* Add Nexus refresh hook: post-archive, trigger targeted Nexus `graph-builder.py --scope {changed-files}` for dependency edges only (not full graph reconstruction)

### 2.5 Feedback (l2/feedback/SKILL.md)

**Changes needed (Phase 4):**
1. *(v5.2)* Add `--metrics` mode: ingest structured CSV/JSON performance/analytics files, route to Memory (vault entries tagged `layer: production-evidence`), notify Product module that new evidence is available, flag relevant Specify specs for review if metrics contradict spec assumptions

### 2.6 Economy (l2/economy/SKILL.md)

**Changes needed (Phase 4):**
1. *(v5.2)* Add `--budget` mode: accept `budget_ceiling` token count from AGENT.md; at pipeline planning time project total token cost (model tier × task count × average tokens per task); emit advisory warning with breakdown if projected > ceiling

### 2.7 Monitor (l1/monitor/SKILL.md)

**Changes needed (Phase 3):**
1. *(v5.2)* Add Guard log signal source to PostToolUse hook: when Guard logs show error patterns (repeated blocked operations, risk tier escalations, freeze violations), auto-emit a typed DEPENDENCY error event routed to Triage

### 2.8 Guard (l2/guard/SKILL.md)

**Changes needed (Phase 4):**
1. Reference `_shared/infrastructure/guard-policy.md` for default risk tier policy (currently hardcoded in SKILL.md rules)
2. This is a refactor — behavior unchanged, defaults externalized so multiple modules can share the same policy config

### 2.6 Specify (l1/specify/SKILL.md)

**Changes needed (Phase 3):**
1. After delta_class classification, if BREAKING and tags intersect adversarial_required: invoke Adversary directly (not via Reviewer full cycle) to challenge the spec before locking
2. The current Step 3.6 (adversarial_spec_gate) says "invoke Reviewer" — change to "invoke Adversary" after Phase 1 extraction

---

## 3. Phase plan

### Phase 0 — Confirm and lock (no build)

**Goal:** Lock all architectural decisions, identify all file paths, define every receipt schema change needed. No SKILL.md written until this is complete.

**Deliverables:**
- This document reviewed and confirmed
- Receipt schema fields defined for all 26 new modules (can be done module-by-module in Phases 1–5)
- Reviewer surgery diff written (not applied)
- Recipe surgery diff written (not applied)

---

### Phase 1 — Extract Adversary + Grader (4 files + 2 surgery)

**Goal:** Adversary and Grader are standalone invokable modules. Reviewer delegates to them.

**New files:**

```
modules/l2/adversary/
  SKILL.md
  skill-rules.json
  rules/
    budget-thresholds.md       — confidence <0.7, impact HIGH, explicit request
    challenge-format.md        — Weaknesses / Missed alternatives / Unstated assumptions / Failure scenarios
    anchoring-prevention.md    — Adversary receives output only, no context
  schemas/
    adversary-receipt.schema.json
```

```
modules/l2/grader/
  SKILL.md
  skill-rules.json
  rules/
    verdict-matrix.md          — ACCEPT/REVISE/ESCALATE thresholds
    revision-guidance.md       — guidance must be specific and actionable
    anti-inflation.md          — guard against grade inflation
  schemas/
    grader-receipt.schema.json
    grade-score.schema.json    — 0.0–1.0 with structured findings
```

**Surgical files changed:**
- `modules/l2/reviewer/SKILL.md` — Steps 2 and 3 updated (delegates out)
- `modules/l2/reviewer/agents/adversary.md` — becomes invocation stub
- `modules/l2/reviewer/agents/grader.md` — becomes invocation stub

**framework.yaml additions:**
- adversary entry (L2, depends_on: [])
- grader entry (L2, depends_on: [adversary])
- Update reviewer depends_on: [adversary, grader, verifier]

**Validation gate:** Reviewer end-to-end receipt format unchanged. Adversary and Grader each produce their own receipts. A caller can now invoke `l2/adversary` directly without going through Reviewer.

---

### Phase 2 — Core intelligence gap (6 files + 1 surgery)

**Goal:** Plan, Brainstorm, Enhance, Sharpen exist. Recipe routes vague/broad input through them.

**New files:**

```
modules/l1/enhance/
  SKILL.md                     — 9-dimension intent extraction; max 3 clarifying questions
  skill-rules.json
  rules/
    intent-dimensions.md       — Task, Target tool, Output format, Constraints, Input,
                                  Context, Audience, Success criteria, Examples
    critical-dimensions.md     — Task + Target + Format are critical; missing = question
    question-budget.md         — max 3 questions, prioritized by criticality
  schemas/
    enhance-receipt.schema.json — dimensions_extracted, questions_asked, vague_resolved
```

```
modules/l1/sharpen/
  SKILL.md                     — narrow broad inputs; ranked interpretations; cap 3
  skill-rules.json
  rules/
    breadth-detection.md       — how to identify overly broad input
    interpretation-ranking.md  — rank by specificity, feasibility, user signal
  schemas/
    sharpen-receipt.schema.json — interpretations_produced, interpretation_chosen, broad_resolved
```

```
modules/l1/brainstorm/
  SKILL.md                     — divergent exploration before convergent planning
  skill-rules.json
  rules/
    divergence-rules.md        — no evaluation during generation; quantity over quality
    convergence-gate.md        — signals to stop generating, start evaluating
  schemas/
    brainstorm-receipt.schema.json
```

```
modules/l1/plan/
  SKILL.md                     — multi-expert strategic planning; L2+ tasks
  skill-rules.json
  agents/
    planner.md                 — generates plan options
    architect.md               — reviews structural soundness
  rules/
    plan-completeness.md       — what a complete plan contains
    expert-roles.md            — which expert perspectives to apply by domain
    escalation-triggers.md     — when Plan must surface to human
  schemas/
    plan-receipt.schema.json
    plan-artifact.schema.json  — plan options, chosen approach, rationale, risks
```

**Surgical files changed:**
- `modules/l0/recipe/SKILL.md` — adds input quality detection and Enhance/Sharpen routing
- `modules/l0/recipe/rules/target-detection.md` — adds vague/broad classification rules

**framework.yaml additions:**
- enhance (L1)
- sharpen (L1)
- brainstorm (L1)
- plan (L1, depends_on: [specify, propose])
- Update recipe depends_on to include enhance, sharpen (conditional)
- Update autopilot depends_on to include plan

**Validation gate:** Recipe detects vague input, routes to Enhance, Enhance produces enhance-receipt.json. Enhance exits with all 9 dimensions scored (present/absent/derived). Plan produces plan-artifact.json readable by Decompose.

---

### Phase 3 — Core lifecycle gaps (10 files + 3 surgery)

**Goal:** Nexus, Shift, Sync, Organize, Flag, Analyze, Perf, Deps, Audit, API exist.

**New files:**

```
modules/l5/nexus/
  SKILL.md                     — tribal knowledge retrieval; cross-module architectural reasoning
  skill-rules.json
  scripts/
    graph-builder.py           — builds relationship graph from Memory drawers + Entity-Graph
    blast-radius.py            — computes change impact surface
    pattern-matcher.py         — finds recurring cross-module patterns
  rules/
    nexus-vs-explore.md        — Explore: surface patterns. Nexus: deep cross-module reasoning
    query-types.md             — why-query, what-changed, blast-radius, pattern-discovery
  schemas/
    nexus-receipt.schema.json
    why-query-response.schema.json
  agents/
    why-query-agent.md
    pattern-discovery-agent.md
```

Note: Nexus lives at L5 (memory layer) because it queries Memory and EntityGraph. It is cross-invokable from any layer. The graph schemas must be interoperable with `_shared/schemas/drawer.schema.json` and EntityGraph's output format.

```
modules/l1/shift/
  SKILL.md                     — semantic spec versioning + reverse drift detection
  skill-rules.json
  scripts/
    semantic-differ.py         — classifies changes as BREAKING/DEPRECATION/ADDITIVE/COSMETIC
    reverse-drift-detector.py  — detects implementation edited without spec update
    compatibility-checker.py   — evaluates downstream consumer impact
  rules/
    change-classification.md   — BREAKING / DEPRECATION / ADDITIVE / COSMETIC definitions
    reverse-drift-triggers.md  — conditions that activate reverse drift detection
  schemas/
    shift-receipt.schema.json
    compatibility-report.schema.json
```

```
modules/l1/sync/
  SKILL.md                     — reconcile diverged specs from parallel changes
  skill-rules.json
  rules/
    divergence-detection.md    — how to identify spec divergence
    merge-policy.md            — when to auto-merge vs escalate
  schemas/
    sync-receipt.schema.json
```

```
modules/l1/organize/
  SKILL.md                     — audit and repair project file/folder structure
  skill-rules.json
  rules/
    audit-dimensions.md        — naming, depth, orphans, dead files, duplication
    repair-policy.md           — what Organize can move vs what needs human confirmation
  schemas/
    organize-receipt.schema.json
```

```
modules/l1/flag/
  SKILL.md                     — feature flag lifecycle: create, rollout, audit, retire
  skill-rules.json
  commands/
    flag-commands.md           — --create, --rollout, --audit, --retire
  rules/
    flag-lifecycle.md          — state machine: DRAFT → ACTIVE → ROLLING → RETIRED
    rollout-gate.md            — conditions required before rollout
  schemas/
    flag-receipt.schema.json
    flag-manifest.schema.json  — flag registry entry format
```

```
modules/l1/analyze/
  SKILL.md                     — root cause investigation; knowledge-graph-leveraged
  skill-rules.json
  rules/
    rca-method.md              — 5-whys, fishbone, fault tree selection by context
    evidence-requirements.md   — what counts as confirmed vs probable cause
  schemas/
    analyze-receipt.schema.json
    rca-report.schema.json
```

```
modules/l1/perf/
  SKILL.md                     — performance profiling, benchmarking, optimization
  skill-rules.json
  rules/
    measurement-first.md       — no optimization without baseline measurement
    budget-definition.md       — performance budgets by platform type
  schemas/
    perf-receipt.schema.json
    perf-baseline.schema.json
```

```
modules/l1/deps/
  SKILL.md                     — dependency health, supply chain risk, SBOM
  skill-rules.json
  rules/
    health-dimensions.md       — age, vulnerability, license, maintainer activity
    risk-tiers.md              — CRITICAL / HIGH / MEDIUM / LOW risk classification
    sbom-format.md             — output format for software bill of materials
  schemas/
    deps-receipt.schema.json
    sbom.schema.json
```

```
modules/l2/audit/
  SKILL.md                     — compliance and accessibility verification
  skill-rules.json
  rules/
    audit-dimensions.md        — WCAG, GDPR, license compliance, Guard log review
    guard-log-consumption.md   — how to read Guard operation logs for compliance signals
    accessibility-gates.md     — WCAG 2.1 AA minimum; WCAG 2.2 AAA targets
  schemas/
    audit-receipt.schema.json
    compliance-report.schema.json
```

```
modules/l1/api/
  SKILL.md                     — API lifecycle: versioning, deprecation, contracts
  skill-rules.json
  rules/
    versioning-policy.md       — semver, date-based, header-based versioning
    deprecation-lifecycle.md   — DRAFT → STABLE → DEPRECATED → SUNSET state machine
    contract-enforcement.md    — backward compatibility rules
  schemas/
    api-receipt.schema.json
    api-contract.schema.json
```

**Surgical files changed:**
- `modules/l7/archive/SKILL.md` — adds Shift trigger post-archive + --sweep mode + Nexus refresh hook (§2.4)
- `modules/l1/monitor/SKILL.md` — adds Guard log auto-routing to Triage (§2.7)
- `modules/l1/specify/SKILL.md` — Step 3.6 updated: invoke Adversary directly (not Reviewer) for adversarial spec gate

**framework.yaml additions:** All 10 new modules. Update archive, autopilot, specify consumers.

**Notable dependency:** Nexus depends on memory + entity-graph. Its graph-builder.py must read from `_shared/schemas/drawer.schema.json` format. This is why Nexus is L5, not L1.

**Validation gates:**
- Nexus: given Memory with 10+ drawers, produces a why-query-response with at least one relationship identified
- Shift: given two versions of a task card where a criterion changed, classifies change as ADDITIVE or BREAKING correctly
- Flag: --create produces flag-manifest entry; --retire removes it cleanly

---

### Phase 4 — Shared infrastructure (files only, no new modules)

**Goal:** All shared references and infrastructure files that Phases 1–3 modules depend on exist and are registered in framework.yaml.

**New `_shared/infrastructure/` files:**

```
_shared/infrastructure/
  economy-principles.md        — compression discipline, context placement, budget ceiling, context-type profiles
  guard-policy.md              — default risk tier policy (Guard reads this at cold-start)
  gateway-pattern.md           — gateway architecture specification + routing protocol
  version-tracking.md          — semver automation protocol (Archive exclusive write)
  completion-promise.md        — loop patterns + error recovery for all modules
```

**New `_shared/references/` files:**

```
_shared/references/
  compression-discipline.md    — lite/full/ultra levels, grammar rules, mechanical hedge detection
  model-routing.md             — model tier routing + context-type parameter profiles (5 types × 6 params)
  adversarial-patterns.md      — cognitive biases, challenge modes, assumption frameworks, budget thresholds
  ears-syntax.md               — EARS pattern reference (currently inline in Specify; externalize here)
  robots-first-spec.md         — spec-as-lookup-table guide, Robot-Centric-Code principles
  progressive-disclosure.md    — index-first retrieval, on-demand hydration patterns
  delta-spec-patterns.md       — ADDED/MODIFIED/REMOVED delta spec patterns
  lsp-integration.md           — 22-language LSP availability, diagnostics, module integration
  secure-defaults.md           — secure-by-default coding patterns
  exploit-patterns.md          — attack/defense pattern library (for gateway-security + Audit)
  security-ownership.md        — module security responsibility map
  context-engineering.md       — context window best practices
  context-integrity.md         — context rot detection patterns
  context-optimization.md      — compaction, masking, partitioning, KV-cache techniques
  reasoning-patterns.md        — deep thinking techniques for high-complexity tasks
  memory-routing.md            — which layer a fact belongs to (Memory drawer classification)
```

**New `_shared/scripts/` files:**

```
_shared/scripts/
  graph-traverse.py            — shared BFS/DFS (consumed by Nexus, Shift, Memory)
  bm25.py                      — shared BM25 search engine (consumed by Nexus, Explore)
```

**New `_shared/schemas/` files:**

```
_shared/schemas/
  wave-checkpoint.schema.json          — wave rollback state (Decompose writes, Rollback reads)
  counter-increment-request.schema.json — counter change request format (Archive/Memory submit to Autopilot)
```

**framework.yaml updates:**
- Add all new shared.references entries with accurate consumers lists
- Add all new shared.schemas entries
- Guard: add `_shared/infrastructure/guard-policy.md` as consumed reference
- Economy: add `_shared/infrastructure/economy-principles.md`, `_shared/references/compression-discipline.md`, `_shared/references/model-routing.md`
- Specify: add `_shared/references/ears-syntax.md` as consumed reference
- Apply: add `_shared/references/secure-defaults.md`, `_shared/references/lsp-integration.md`
- Reviewer/Adversary: add `_shared/references/adversarial-patterns.md`
- Decompose: add `_shared/schemas/wave-checkpoint.schema.json`
- Autopilot/Archive/Memory: add `_shared/schemas/counter-increment-request.schema.json`

**Surgery note:** After ears-syntax.md is created, Specify's SKILL.md should reference it rather than embed the syntax inline. This is a documentation refactor — no behavior change.

**Module modification surgeries (Phase 4, v5.2 additions):**
- `modules/l2/feedback/SKILL.md` — add `--metrics` mode (§2.5)
- `modules/l2/economy/SKILL.md` — add `--budget` mode (§2.6)

**Validation gate:** Every new `_shared/references/` file has at least one declared consumer in framework.yaml. No orphaned reference files.

---

### Phase 5 — Output and craft layer (10 files)

**Goal:** L6 and L7 output modules exist. Polish pipeline now has all its components.

**New files:**

```
modules/l6/proofread/
  SKILL.md                     — content quality gate for text-producing modules
  skill-rules.json
  rules/
    readability-gates.md       — Flesch-Kincaid targets by content type
    technical-accuracy.md      — facts verifiable; no hallucinated citations
    consistency.md             — terminology consistency; no contradiction within document
  schemas/
    proofread-receipt.schema.json
```

```
modules/l6/markdown/
  SKILL.md                     — Obsidian-compatible markdown output formatter
  skill-rules.json
  rules/
    obsidian-format.md         — frontmatter, linking, callout syntax
    agentskills-format.md      — agentskills.io compatible output format
  templates/
    obsidian-note.md
  schemas/
    markdown-receipt.schema.json
```

```
modules/l6/copy/
  SKILL.md                     — UI micro-text: labels, errors, tooltips, security warnings
  skill-rules.json
  rules/
    microcopy-principles.md    — concise, action-oriented, error messages with recovery path
    security-warning-format.md — security warnings must not be dismissable without acknowledgment
  schemas/
    copy-receipt.schema.json
```

```
modules/l6/writer/
  SKILL.md                     — long-form content: landing pages, blogs, awareness materials
  skill-rules.json
  rules/
    content-types.md           — landing page vs blog vs technical article vs case study
    structure-templates.md     — AIDA, problem-solution, storytelling frameworks
  schemas/
    writer-receipt.schema.json
```

```
modules/l6/legal/
  SKILL.md                     — privacy policies, ToS, GDPR docs, disclaimers
  skill-rules.json
  rules/
    jurisdiction-defaults.md   — GDPR (EU), CCPA (CA), PIPEDA (CA), default to GDPR
    required-clauses.md        — minimum required content per document type
  templates/
    privacy-policy-gdpr.md
    terms-of-service-base.md
    gdpr-data-processing.md
    disclaimer-base.md
  schemas/
    legal-receipt.schema.json
```

```
modules/l6/translate/
  SKILL.md                     — i18n/l10n infrastructure, locale management, verification
  skill-rules.json
  rules/
    locale-format.md           — BCP 47 locale tags; CLDR formatting conventions
    string-extraction.md       — what qualifies as a translatable string
    verification-gates.md      — translated strings must render without truncation
  schemas/
    translate-receipt.schema.json
    locale-manifest.schema.json
```

```
modules/l6/optimize/
  SKILL.md                     — discoverability: SEO, AI search surfaces, 8 sub-modes
  skill-rules.json
  commands/
    optimize-commands.md       — --seo, --ai-search, --structured-data, --performance,
                                  --social, --local, --video, --voice
  rules/
    signal-hierarchy.md        — Core Web Vitals > structured data > metadata > copy
  schemas/
    optimize-receipt.schema.json
```

```
modules/l6/market/
  SKILL.md                     — marketing strategy, positioning, execution planning
  skill-rules.json
  rules/
    positioning-framework.md   — market category, differentiators, ICP definition
    execution-planning.md      — channel selection, message hierarchy, campaign structure
  schemas/
    market-receipt.schema.json
```

```
modules/l7/changelog/
  SKILL.md                     — git history into user-facing release notes
  skill-rules.json
  rules/
    git-parsing.md             — which commits to include; conventional commit parsing
    user-language.md           — technical → user-facing translation patterns
  templates/
    changelog-entry.md
  schemas/
    changelog-receipt.schema.json
```

```
modules/l7/commit/
  SKILL.md                     — stage, split, and write conventional git commits
  skill-rules.json
  rules/
    conventional-commits.md    — type(scope): description format; types: feat/fix/chore/docs/refactor/test/perf
    staging-policy.md          — what to include in a single commit; when to split
    message-quality.md         — message describes why, not what; 72-char subject line
  schemas/
    commit-receipt.schema.json
```

**Polish pipeline update (l6/polish/SKILL.md):**
After Phase 5, Polish's pass sequence should reference the full set:
`Review → Clean → [Proofread] → [Markdown] → Changelog → Commit`
Polish's rules/pass-sequence.md needs updating to include Proofread and Markdown as optional steps.

**framework.yaml additions:** All 10 new modules. Update polish dependencies.

**Validation gate:** Changelog given a conventional commit log produces a structured user-facing entry. Commit given staged changes produces a conventional commit message with correct type + scope. Proofread catches a seeded factual error and fails the receipt.

---

### Phase 6 — Templates directory (non-module, infrastructure only)

**Goal:** `_shared/templates/` exists with standardized output templates for modules that produce common artifacts.

```
_shared/templates/
  legal/
    privacy-policy-gdpr.md     — GDPR-compliant privacy policy base
    terms-of-service-base.md
    disclaimer-base.md
  changelog/
    release-notes.md           — user-facing release note format
    conventional-changelog.md  — developer changelog format
  specs/
    task-card.md               — task card template (currently inline in Specify)
    spec-folder-readme.md      — how to use a spec folder
  handoff/
    session-handoff.md         — session handoff format (used by TeamPlan, Document)
  standards/
    index-template.yml         — standards/ folder index template
```

**framework.yaml update:** Add shared.templates section. Document which modules consume each template.

---

## 4. Surgery checklist

For each surgical change, the existing module's external interface must be preserved. List every external-facing artifact that must not change:

| Module | External interface locked |
|---|---|
| Reviewer | Receipt schema fields: triggered, trigger_condition, revise_cycles, verdict, grader_score, escalated, escalation_reason, findings, finding_summary |
| Recipe | Receipt schema fields: target, complexity; new fields: input_quality (additive only) |
| Autopilot | meta.md structure; handoff record format |
| Archive | Receipt schema; CHANGELOG.md format |
| Guard | Error-event.schema.json output; invariant enforcement behavior |
| Specify | task-card.md format; specify-receipt.json fields |

---

## 5. Build order dependencies

The phases are ordered by dependency. Within a phase, modules without cross-dependencies can be built in parallel.

```
Phase 0 (lock decisions) — must complete before any other phase
Phase 1 (Adversary + Grader) — must complete before Phase 2 (Plan uses Adversary/Grader), Phase 3 (Specify uses Adversary directly)
Phase 2 (Enhance, Sharpen, Brainstorm, Plan) — must complete before Phase 3 (Autopilot wiring)
Phase 3 (10 core lifecycle modules) — can start after Phase 1; independent of Phase 2 except for Autopilot wiring
Phase 4 (shared infrastructure) — can run in parallel with Phase 3; required before Phase 5 modules that reference shared refs
Phase 5 (output layer) — requires Phase 4 (some L6 modules reference shared references)
Phase 6 (templates) — can run in parallel with Phase 5
```

Phases 3, 4, 5, 6 are largely independent after Phase 1 completes.

---

## 6. What this plan explicitly excludes

1. **Gateway sub-modules** (Security leaf modules: Recon, Surface, Model, Attack, Defend, etc.; Development leaf modules: React, Python, Go, etc.; Engineering, Aesthetic, Design, Experience leaf modules): These require separate planning. Must consult v4 and v5.2 to understand how the gateway architecture evolved before building leaf modules into v6.1's L4 gateway design.

2. **L8 Evolution pipeline changes**: Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge already exist. No changes in this plan — L8 gate blocks any promotion.

3. **Nexus graph schema interoperability with Shift and Memory**: This is noted as a dependency for Phase 3. A separate sub-decision on the exact graph schema format (nodes, edges, relationship types) needs to be locked before building Nexus, Shift, and any Memory updates. Both must use `_shared/schemas/drawer.schema.json` as the base.

4. **LSP integration in Apply/Review/Clean**: lsp-integration.md will be created in Phase 4, but wiring LSP diagnostics into Apply, Review, and Clean is a separate initiative — it requires the LSP reference to exist first, which Phase 4 provides.

5. **test.wabblespec/ or evaluations/**: No eval harness is built in this plan. Quality is validated by manual SKILL.md review + the existing quality-floor-check.py script.

---

## 7. Completion criteria

This plan is complete when:

- [ ] All 26 standalone modules have SKILL.md + skill-rules.json
- [ ] All 26 modules have entries in framework.yaml with accurate metadata
- [ ] All surgical modules (Reviewer, Recipe, Archive, Monitor, Specify, Feedback, Economy) updated and pass quality-floor-check
- [ ] Autopilot surgery DEFERRED (planned separately after all 26 modules complete)
- [ ] All Phase 4 shared references exist with declared consumers in framework.yaml
- [ ] `_shared/infrastructure/` directory exists with 5 files
- [ ] `_shared/templates/` directory exists with all template files
- [ ] Reviewer surgery: Adversary and Grader are independently callable; Reviewer receipt format unchanged
- [ ] Polish pass-sequence.md updated to include Proofread and Markdown
- [ ] Archive post-hook triggers Shift on BREAKING/ADDITIVE spec changes
- [ ] No shared reference file exists without at least one declared consumer in framework.yaml
- [ ] CHANGELOG.md updated with a single entry for this integration batch
- [ ] VERSION bumped (MINOR — new capabilities, no breaking external interface changes)
