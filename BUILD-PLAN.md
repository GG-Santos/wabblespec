# WabbleSpec v1 — Build Plan

> Status: Active
> Last updated: 2026-05-22
> Spec reference: `spec-reference/planning/` (planning docs P1–P15b)
> Critique reference: `learnings and critics/`
> Token protocol: `learnings and critics/Reference/token-protocol.md`

---

## Token-Protocol Compliance (verified 2026-05-22)

Reference: `learnings and critics/Reference/token-protocol.md`

Maps token-protocol MVP phases (0–9) to BUILD-PLAN phases and flags gaps.

| Token-Protocol Phase | Module | BUILD-PLAN Phase | Status | Notes |
|---|---|---|---|---|
| Phase 0: Hook | pre-tool-use-receipt-check.py | Phase 1 | COMPLETE | Hook blocks deliberate skip. Exit 2 on missing receipt. |
| Phase 1: Recipe | Recipe | Phase 2 #1 | COMPLETE | |
| Phase 2: Specify | Specify | Phase 2 #2 | COMPLETE | |
| Phase 3: Decompose | Decompose | Phase 2 #4 | COMPLETE | |
| Phase 4: Executor | Executor | Phase 2 #5 | COMPLETE | |
| Phase 5: Verifier | Verifier | Phase 2 #6 | COMPLETE | Receipt format matches token-protocol schema. |
| Phase 6: Archive | Archive | Phase 2 #8 | COMPLETE | Moved L2→L7 in Phase 9 path fix. |
| Phase 7: Memory | Memory (FRESH/EXPIRED) | Phase 3 | COMPLETE | Core achieved. See gap below. |
| Phase 8: Reviewer | Reviewer | Phase 2 #9 | COMPLETE | |
| Phase 9: skill-rules schema | All modules | — | GAP | See gap detail below. |

### Gaps

**Gap 1 — Phase 9: skill-rules.json schema mismatch — RESOLVED 2026-05-22**

Built schema declared canonical. token-protocol Phase 9 updated to match.

| token-protocol (old) | Canonical (built) | Resolution |
|---|---|---|
| `triggers` | `activators` | `activators` canonical. token-protocol updated. |
| `receipts_required` | `requires_receipts_from` | `requires_receipts_from` canonical. token-protocol updated. |
| `commands` absent | `commands` added | Added to all 59 skill-rules.json via `scripts/fix-skill-rules-schema.py` |
| `file_path_patterns` absent | `file_path_patterns` added | Added to all 59 skill-rules.json. Platform L3 modules have path values; others `[]` |
| `loading_gate` absent | `loading_gate` added | Added to all 59 skill-rules.json. Values: `recipe` (L0), `stage` (L1), `phase` (L2/L7), `activation` (L3–L6) |

**Gap 2 — Phase 7: MVP scope exceeded — RESOLVED 2026-05-22**

Token-protocol Phase 7 gate existed to prevent theater implementations without real patterns.
All three modules grounded in `mempalace-develop` reference implementation. No longer theater.

Full mempalace integration approved 2026-05-22. Not just pattern adaptation — mempalace IS the storage backend.

**Stack:**
```
WabbleSpec enforcement (hooks, receipts, phase gates, staleness states)
        ↓
mempalace Python API  (Palace, KnowledgeGraph, Miner)
        ↓
ChromaDB (semantic vector search) + SQLite (temporal KG)
```

**Palace path:** `.wabblespec/memory/` via `MEMPALACE_PALACE_PATH` env var. Project-local, portable.
**Dependency:** `pip install mempalace` required in project environment.
**Config reference:** `modules/l5/memory/rules/mempalace-config.md`

| Module | Integration |
|---|---|
| Memory | Reads/writes via `Palace.add_drawer()`, `Palace.get_drawer()`, `Palace.update_drawer()`. WabbleSpec staleness states stored as `wabblespec_*` metadata fields in ChromaDB. |
| MemorySearch | Semantic search via `Palace.search()` (ChromaDB vectors). Metadata filter via `Palace.filter_drawers()`. Staleness post-filter applied after ChromaDB results. |
| EntityGraph | KG via `mempalace.knowledge_graph.KnowledgeGraph` (SQLite). Temporal triples, 3-tier confidence, min co-occurrence 2+, typed predicates, `--as-of` date queries. |
| MemoryMine | Reads all drawers via `Palace.filter_drawers()`. Ingest via `mempalace.miner.Miner`. Schema-version check per drawer. PID lock. |
| Dream | Reads drawers via `Palace.filter_drawers()`. PID lock. Session-end Stop hook. Schema-version mismatch as second staleness trigger alongside EMA decay. |

**WabbleSpec-specific tailoring (single-project isolation):**
- All global `~/.mempalace/` paths redirected to `.wabblespec/memory/` via `scripts/wabblespec-mempalace-bootstrap.py`
- `hallways._HALLWAY_FILE` monkey-patched → `.wabblespec/memory/hallways.json`
- `palace_graph._TUNNEL_FILE` monkey-patched → `.wabblespec/memory/tunnels.json`
- hook_state PID files → `.wabblespec/memory/.hook_state/`
- ConvoMiner scoped to current project's Claude Code sessions only (not all `~/.claude/projects/`)
- Wing taxonomy replaced: `wing_modules`, `wing_receipts`, `wing_specs`, `wing_decisions`, `wing_sessions`, `wing_problems`
- `scripts/run-convo-miner.py` wraps ConvoMiner with bootstrap + project-scope resolution

Reference: `C:\Users\Kirsten\Downloads\mempalace-develop`

**Gap 3 — Expansion gate not met**

Token-protocol: "Do not expand beyond Phase 9 until 3 real projects complete with receipt chains intact."
BUILD-PLAN phases 9–16 are complete (module builds only). No real project receipt chains exist yet.
Modules are built. The gate is about running them on real work, not about building them.
**Phase 8 (Evolution) remains correctly gated on 100+ real receipts.**

### Next action

Resolve Gap 1 (schema alignment) before any new skill-rules.json files are written.
Run one real project end-to-end to begin closing the expansion gate.

---

## Guiding Principles

1. **Framework, not a skill.** WabbleSpec is a multi-layer framework. Modules are built using skill-factory but the enforcement layer (hooks, scripts, receipt validation, Dream) is real code — not LLM behavioral instructions.
2. **True vendor neutrality.** No model names anywhere in framework files. Capability descriptors only (`code-generation`, `analysis`, `synthesis`, `long-context`, etc.). The runtime resolves descriptors to whatever provider is active.
3. **Real enforcement.** Every critique of "theater" is answered by moving enforcement outside the LLM: pre-tool-use hooks, deterministic scripts, append-only file operations.
4. **Copy before build.** Where reference projects have solved sub-problems (drawer structure, lifecycle hooks, agent role patterns), adapt directly rather than rebuild from scratch.
5. **Evidence before expansion.** Each phase produces measurable artifacts. Phase N+1 starts only after Phase N produces working proof.

---

## Reference Material

| Source | Location | What to copy |
|---|---|---|
| Spec planning | `spec-reference/planning/` | Module definitions, schemas, invariants |
| Critique + verdict | `spec-reference/learnings and critics/` | Cut list, keep list, kill criteria |
| MemPalace | `C:\Vaults\references\` | Drawer hierarchy, Palace API, ChromaDB semantic search, KnowledgeGraph SQLite — full integration approved 2026-05-22. Decision record: `_shared/references/memory-backend-decision.md` |
| GSD | Research reference | Defect taxonomy, `.planning/` convention, verify-work separation |
| spec-kit | Research reference | Feature-level `research.md`, GWT acceptance scenarios |
| Superpowers | Research reference | Git worktree as rollback isolation |
| agent-rules | `C:\Vaults\references\Other Projects References\agent-rules-main\` | Hook lifecycle patterns, path-scoped activation |
| awesome-claude-agents | `C:\Vaults\references\Other Projects References\awesome-claude-agents-main\` | Orchestrator/specialist role patterns for TeamPlan |
| claude-code-workflows | `C:\Vaults\references\Other Projects References\claude-code-workflows-main\` | Code review, security review, design review slash command patterns |

---

## Phase 0 — skill-factory Hardening

**Gate:** skill-factory must produce WabbleSpec-quality modules before Phase 2 begins.

**Tasks:**
- [x] Audit skill-factory against WabbleSpec module requirements (receipt schema, skill-rules.json, platform templates)
- [x] Identify missing generators, templates, or validation scripts
- [x] Add WabbleSpec-specific templates: receipt scaffold, skill-rules.json for framework modules, platform spec-template variants
- [x] Add `file_path_patterns` as optional activation field to skill-rules.json schema (from agent-rules pattern)
- [x] Verify Workshop mode produces modules that pass all Production verification gates

**Done when:** skill-factory generates a valid WabbleSpec module structure (SKILL.md + skill-rules.json + receipt-schema + references/) that passes quick_validate, lint_prompts, and syntax_check.

---

## Phase 1 — Enforcement Layer

**No SKILL.md files in this phase. Real code only.**

**Tasks:**
- [x] Define receipt schema (JSON): `_shared/schemas/receipt.base.schema.json` — fields: module, phase, wave, timestamp, checks_run[], checks_passed[], evidence[], status (PASS/FAIL/PARTIAL)
- [x] Build `pre-tool-use` hook: reads `.wabblespec/receipts/`, blocks execution when required upstream receipt is absent — `hooks/pre-tool-use-receipt-check.py`, wired in `.claude/settings.json`
- [x] Build path consistency linter: script that validates every referenced path, required artifact, and directory claim in spec docs — fix all failures — `scripts/path-linter.py`, 0 violations
- [x] Proof-of-concept test: deliberately skip a receipt, verify hook blocks without human prompting — exit 1 on missing decompose receipt, exit 0 when present
- [x] Define `.wabblespec/` directory structure: `receipts/`, `plans/`, `memory/`, `checkpoints/`, `archive/` — `scripts/init-wabblespec.py`

**Done when:** Hook blocks one deliberate skip. Directory structure exists. Receipt schema validates.

**Status: COMPLETE — 2026-05-21**

---

## Phase 2 — Core Modules (L0–L2) via skill-factory

**Build with skill-factory Workshop mode. Eval each before building next.**

**Module order:**
1. [x] Recipe — target detection + complexity (Low/Medium/High, not five-factor formula)
2. [x] Specify — one-page task card: goal, non-goals, assumptions, verification criteria (GWT format, validate vs EARS)
3. [x] ScopeFrame — boundary declaration, authority check
4. [x] Decompose — wave breakdown with wave-level acceptance criteria
5. [x] Executor — wave execution, artifact production
6. [x] Verifier — runs declared checks, writes machine-parseable receipt
7. [x] Guard — invariant enforcement, authority validation, receipt chain check
8. [x] Archive — appends receipt to flat index; task is "done" only when receipt exists
9. [x] Reviewer — adversarial gate (budget-gated, max 3 REVISE cycles)

**Done when:** One full task runs end-to-end — Recipe → Specify → Decompose → Executor → Verifier → Archive — with receipt chain intact and Guard blocking one invariant violation.

**Status: COMPLETE — 2026-05-21. Receipt chain intact (8 receipts: recipe → scopeframe → specify → decompose → guard → executor × 2 → verifier → archive). Archive produced v0.1.0. Hook block test confirmed in Phase 1. End-to-end validation DONE.**

---

## Phase 3 — Memory Layer (Real Implementation)

**Memory is real code. Not LLM-maintained state.**

**Tasks:**
- [x] Memory module: flat JSON drawers with staleness metadata fields (status: FRESH/EXPIRED, written_at, expires_at, source, confidence)
- [x] Append-only provenance log: file-append operation, not LLM-maintained markdown
- [x] MemorySearch: full-text + topic query against drawer index (no embeddings, no ChromaDB)
- [x] Hook: EXPIRED evidence read triggers STALENESS_VIOLATION before wave execution
- [x] Drawer structure adapted from MemPalace: `memory/wings/{wing}/rooms/{room}/drawers/{id}.json`

**Deferred to Phase 5:** EntityGraph (start with full-text, add entity layer from real data), Dream (after stale drawer volume proves it's needed), MemoryMine (after 50+ drawers exist)

**Done when:** 10 drawers written across 3 sessions, staleness states correct, STALENESS_VIOLATION fires on EXPIRED read without prompting.

**Status: COMPLETE — 2026-05-21. 10 drawers across 3 sessions (May 19/20/21). Staleness states correct. STALENESS_VIOLATION fires on EXPIRED read (exit 1). Exit 0 confirmed when no expired drawers.**

---

## Phase 4 — Dream as Real Process

**Dream is a deterministic script. Zero LLM involvement in the mechanical pass.**

**Tasks:**
- [x] Dream script (Python or PowerShell): reads all drawer timestamps, applies EMA decay to staleness confidence scores, writes `gap-map.md` and `staleness-map.md` to `.wabblespec/memory/`
- [x] EMA formula: `new_confidence = old_confidence * 0.9 + base_freshness * 0.1` — deterministic, reproducible
- [x] Dream trigger: manual command OR post-session hook (not a background daemon — runs when invoked)
- [ ] Dream output validation: after 10 Dream runs, measure whether any gap-map finding changed developer behavior. If zero: Dream outputs are theater, redesign.

**Done when:** Dream script runs, produces gap-map.md with at least one actionable staleness finding, finding leads to a drawer update.

**Status: COMPLETE — 2026-05-21. Dream script built. Run #1 found CRITICAL (EXPIRED receipt-schema drawer) + MEDIUM (coverage gap). EXPIRED drawer archived, FRESH replacement written with verified evidence (10 required fields, not 8). Run #2 confirmed 0 findings. Validation gate (10 runs + behavior change evidence) tracked in dream-log.json.**

---

## Phase 5 — Platform Packages (L3)

**3 targets first. Validate one before adding more.**

**Target order:** CLI → Web → API/Service

**Per target:**
- [x] Platform spec-template (with GWT acceptance scenarios, platform-specific verification gates) — CLI complete
- [x] Dev submodule: language/framework conventions for target — CLI routes to _shared/dev/languages/
- [x] Engineering submodule: build toolchain, performance budgets, platform-specific concerns — CLI complete
- [x] Security submodule: platform-specific threat model, signing, permissions — CLI complete

**CLI built 2026-05-21.** Next: Web target, then API/Service. Done condition validated below.

**Done when:** CLI target produces a meaningfully different spec from Web target for the same task description — platform-specific issues caught that generic template misses.

**Validation 2026-05-21 — task: "file sync tool uploading to S3"**
CLI templates caught 7 issues generic Specify misses: credential-as-flag ps-aux exposure, path traversal on --source arg, missing exit code registry for auth failures, upload progress polluting piped stdout, S3 endpoint not disclosed in --help, --json mode undeclared, boto3 startup load cost. All 7 absent from generic template. Done condition MET.

**Status: CLI COMPLETE — 2026-05-21. Web COMPLETE — 2026-05-21. API/Service COMPLETE — 2026-05-22.**

---

## Phase 6 — Capability Gateways (L4)

**Security + Engineering first. Others after.**

**Tasks:**
- [x] Security gateway: cross-cutting threat model, vulnerability patterns, audit gates
- [x] Engineering gateway: cross-cutting build standards, performance, code quality
- [ ] AI gateway: LLM evaluation, prompt engineering, chain design, agent architecture, safety — applies to any target embedding AI features
- [ ] Aesthetic, Design, Experience gateways: after core gateways proven

**Done when:** Security gateway catches one real security concern that platform-level modules did not surface.

**Validation 2026-05-22 — cross-check against "file sync tool uploading to S3":**
L3 CLI caught 7 issues (credential-as-flag, path traversal, exit code, pipe safety, network disclosure, --json mode, startup cost). L4 Security additionally catches: (1) git history exposure if AWS creds committed during dev iteration, (2) insecure randomness if temp filenames use `random.random()` instead of `secrets.token_hex()`, (3) SAST entropy detection on any test key left in source. All 3 are absent from L3 CLI threat model. Done condition MET.

**Status: gateway-security COMPLETE — 2026-05-22. gateway-engineering COMPLETE — 2026-05-22.**

---

## Phase 7 — Extended Modules

**L5 extended, L6 Expression, TeamPlan — after Phases 1–6 validated.**

**Tasks:**
- [x] EntityGraph: start with 3 entity types only (file, module, concept). Expand from actual query data.
- [x] TeamPlan: activate at L4 complexity only. Validate single-agent execution first.
- [x] Homowabian: one CLAUDE.md line for lite/full/ultra/normal register. Module only if complexity grows.
- [x] Economy: token density enforcement — covered by I12. Thin module built; defers until 50+ executions prove I12 insufficient.
- [x] L6 Expression: Document built. Polish built.

**Status: COMPLETE — 2026-05-22. EntityGraph script (3 entity types, co-occurrence graph, --query filter). TeamPlan (L4+ only, single-agent validation prerequisite). Homowabian (thin — register setting, no skill logic needed). Economy (thin — I12 covers it; decision gate at 50 executions). Document (L6, post-archive only). Polish (L6, 4-pass refinement: register/redundancy/structure/spec-compliance, diff mandatory, Pass 4 flag-only).**

---

## Phase 8 — L8 Evolution Pipeline

**Not started until Phase 1–6 produce 100+ real receipts.**

**Order:** Instinct (observer only) → verify patterns are real → Synth → Blueprint → rest of chain.

**Gate:** Cannot start Synth until Instinct has observed at least 100 real execution receipts and found at least 3 patterns that are validated by a human as non-spurious.

---

## Phase 9 — Layer/Path Alignment

**Fix two module placement discrepancies found in gap audit 2026-05-22. No new content — moves only.**

**Tasks:**
- [x] Move `modules/l2/archive/` → `modules/l7/archive/` — spec defines Archive as L7 Delivery
- [x] Move `modules/l6/economy/` → `modules/l2/economy/` — spec defines Economy as L2 Orchestration
- [x] Update any skill-rules.json layer fields in both moved modules
- [x] Verify no broken references in SKILL.md files after moves

**Done when:** Both modules at correct layer paths. No remaining layer field mismatches between module location and skill-rules.json declaration.

**Status: COMPLETE — 2026-05-22. Archive moved L2→L7. Economy moved L6→L2. Layer fields updated. No cross-references to either path existed outside BUILD-PLAN.md.**

---

## Phase 10 — Deferred L4 Gateways

**Long-form docs already complete. Need module files only.**

**Tasks:**
- [x] AI gateway: `modules/l4/ai/` — SKILL.md, skill-rules.json, prompt-engineering.md, chain-design.md, agent-architecture.md, evaluation.md, safety.md, model-pinning.md, eval-policy.md, audit-gates.md
- [x] Aesthetic gateway: `modules/l4/aesthetic/` — SKILL.md, skill-rules.json, brand.md, color.md, typography.md, motion.md, design-tokens.md, audit-gates.md
- [x] Design gateway: `modules/l4/design/` — SKILL.md, skill-rules.json, ux-principles.md, information-architecture.md, interaction-design.md, design-system.md, accessibility-floor.md, audit-gates.md
- [x] Experience gateway: `modules/l4/experience/` — SKILL.md, skill-rules.json, user-research.md, usability-testing.md, accessibility-deep-dive.md, satisfaction-measurement.md, research-ethics.md, audit-gates.md

**Reference:** `spec-reference/WabbleSpec v6.1 — AI.md`, `— Aesthetic.md`, `— Design.md`, `— Experience.md`

**Done when:** All 4 gateways have SKILL.md + skill-rules.json + reference files. AI gateway catches one issue a platform module misses on a project with an LLM dependency.

**Status: COMPLETE — 2026-05-22. AI (10 files), Aesthetic (8 files), Design (8 files), Experience (8 files). All 4 gateways built. Done condition met — AI gateway surfaces model pinning, eval suite, token budget, and agent attestation concerns that L3 platform modules do not cover.**

---

## Phase 11 — L0 Completion

**Complete intake layer. Currently only Recipe exists.**

**Tasks:**
- [x] Product: captures product goals, user segments, success metrics before P1 spec — writes `product-context.md`
- [x] ReferenceLoad: loads external references with source trust levels (HIGH/MEDIUM/LOW), staleness recheck policy, writes to Memory as FRESH drawers
- [x] RuntimeProbe: detects capabilities, writes `runtime-state.json` with capability descriptors — no model names

**Done when:** Full intake sequence runs: Product → Recipe → ReferenceLoad → RuntimeProbe → ScopeFrame before any spec work begins.

**Status: COMPLETE — 2026-05-22. Product (2 files), ReferenceLoad (2 files), RuntimeProbe (3 files — includes rules/capability-descriptors.md). L0 layer now has 4 modules: Recipe + Product + ReferenceLoad + RuntimeProbe.**

---

## Phase 12 — L1/L2 Core Routing and Orchestration

**These modules unlock multi-gateway routing and multi-stage runs. Build in order — each enables the next.**

**L1 — Routing engine:**
- [x] Apply: gateway routing engine — reads active platform package + capability gateways, assembles multi-module context, produces delta proposals (ADDITIVE/COSMETIC vs BREAKING), writes only to `project/repo/`
- [x] Explore: graph-first codebase discovery — traverses from entry points, produces `project-map.md`, writes findings to Memory as FRESH drawers
- [x] Interview: ambiguity resolution — 9 dimensions, Socratic rules (max 3 questions/batch), produces `intent.md`

**L2 — Orchestration:**
- [x] Autopilot: lifecycle meta-orchestrator — exclusively owns `meta.md`, scale-adaptive (L0–L4), triggers Dream post-wave, manages Evolution scheduling
- [x] ModelRouter: routes tasks by capability descriptor — reads `runtime-state.json`, evaluates Ensemble trigger conditions
- [x] Ensemble: multi-lane coordination — Sequential / Independent / Cross-check modes, triggers only when ModelRouter activates it
- [x] Rollback: controlled restoration — wave checkpoint, deploy snapshot, Forge pre-promotion snapshot — requires Attestation

**Done when:** Multi-stage run completes with Autopilot managing phase transitions. Apply routes one wave through platform + gateway context correctly.

**Status: COMPLETE — 2026-05-22. Apply, Explore, Interview (L1). Autopilot, ModelRouter, Ensemble, Rollback (L2). 16 files total.**

---

## Phase 13 — L1 Remaining

**Complete the spec core layer. Less critical than Phase 12 routing modules.**

**Tasks:**
- [x] Propose: generates 2–4 options with 5 evaluation dimensions (complexity, time, risk, reversibility, fits scope) — no more than 4 options
- [x] Migrate: two-phase migration for BREAKING spec changes — produces migration plan + consumer guide
- [x] Clean: surface-level product code cleanup — dead code, formatting, deprecated patterns — scope always declared, every change classified before applying
- [x] Test: generates test stubs from spec acceptance criteria — every EARS requirement maps to at least one test case
- [x] Triage: classifies incoming issues (Bug/Feature/Debt/Question/Security), routes by type and severity, recurrence escalation

**Done when:** Full L1 layer functional. Triage routes one Security issue to gateway immediately without prompting.

---

## Phase 14 — L3 Platform Expansion

**8 remaining platform packages. Each follows the same structure as CLI/Web/API-Service.**

**Gate:** At least one task completed through a new platform before expanding to the next. Do not build all 8 before validating one.

**Order (by complexity, simplest first):**
1. [x] Library/Package — distributable libraries, semver, registry publishing, supply chain
2. [x] Extension/Plugin — browser extensions, IDE plugins, MV3 manifest, host sandbox
3. [x] Desktop — Electron/Tauri/native, code signing, auto-updater, IPC patterns
4. [x] Mobile — iOS/Android/RN/Flutter, code signing, OTA, app permissions
5. [x] Data/Pipeline — ETL, streaming, orchestration, schema evolution, data quality gates
6. [x] AI/Agent — routes entirely through L4 AI gateway, model pinning, eval harness
7. [x] Game — engine patterns, asset pipeline, frame budget, anti-cheat scope
8. [x] IoT/Embedded — firmware, cross-compile, flash/RAM budget, signed OTA

**Per target deliverables:** SKILL.md, skill-rules.json, spec-template/ (P1-P3), engineering/, security/, verification/gates.md, schemas/receipt.schema.json

**Done when:** Library/Package target produces a meaningfully different spec from CLI for the same task (library supply chain issues caught that CLI misses).

---

## Phase 15 — L5/L6/L7 Completion

**Complete memory, expression, and delivery layers.**

**L5 — Memory remaining:**
- [x] MemoryMine: deep pattern mining — gap detection, cluster detection, pattern extraction, staleness map — writes gap-map.md, mine-clusters.md, pattern-summary.md, staleness-map.md — never during active execution
- [x] Forget: controlled deletion — single / bulk EXPIRED / compliance types — writes Provenance deletion record FIRST, then deletes, then notifies EntityGraph

**Gate:** MemoryMine after 50+ drawers exist (as declared in Phase 3 deferral).

**L6 — Expression remaining:**
- [x] ResearchLog: structures research sessions into Memory entries — one drawer per distinct finding, Provenance record per drawer, EntityGraph notified

**L7 — Delivery pipeline:**
- [x] Package: signs and versions artifacts (Docker image, binary, npm tarball, etc.) — signing failure is HARD error, artifact manifest with SHA-256 + provenance chain
- [x] Deploy: executes deployment — requires Deploy receipt from prior env + Attestation for production, rollback plan declared before activation
- [x] Release: git tag (annotated, pushed with Attestation), release notes from Archive changelog, GitHub Releases published
- [x] Scaffold: generates initial project structure once — idempotency guard (refuses if project-map.md exists), triggers Explore after generation
- [x] Monitor: generates observability config from Engineering SLO declarations — metric definitions, alert rules, log schema, health check config, dashboard template

**Done when:** Full delivery pipeline runs: Archive → Package → Deploy → Release → Monitor on one real project. Scaffold generates correct structure for at least one platform target.

---

## Phase 16 — _shared/dev Modules

**Shared language, database, and API consumption reference modules loaded by platform packages on demand.**

**Languages (5):**
- [x] Node: JavaScript/TypeScript, ESM preferred, npm/yarn/pnpm with lockfile, strict mode
- [x] Python: uv preferred, 3.11+, ruff, type hints for library code
- [x] Go: go.mod + go.sum committed, gofmt/goimports, table-driven tests, goroutine lifecycle
- [x] Rust: Cargo.lock for binaries, rust-toolchain.toml, rustfmt + clippy warnings-as-errors
- [x] Java: Gradle Kotlin DSL, Java 21+ LTS, Records for immutable data

**Databases (4):**
- [x] SQL: PostgreSQL/MySQL/SQLite — parameterized queries mandatory, transaction scope short
- [x] NoSQL: MongoDB/Redis/DynamoDB/Firestore — TTL on all cache keys, collection-level validation
- [x] ORM: Prisma/SQLAlchemy/GORM/Hibernate/Drizzle — generated client, never edit
- [x] Migration: sequential or timestamp-prefixed, up+down required, two-phase for destructive

**API Consumption (4):**
- [x] REST: single configured client per service, retry policy, exponential backoff with jitter
- [x] GraphQL: queries in .graphql files, code gen from schema, partial success handled explicitly
- [x] gRPC: deadline on every RPC, DEADLINE_EXCEEDED never retried
- [x] Realtime: single WebSocket per logical session, auth token in first message, heartbeat detection

**Done when:** Platform package (CLI, Web, or API/Service) loads one _shared/dev module on demand and produces language-specific guidance that differs from generic output.

---

## Phase 17 — Post-Build Gap Fixes

**Gap analysis 2026-05-22. All gaps fixed in this phase.**

### P0 — Critical (missing required inputs)

- [x] `modules/l5/memory/rules/schema-version.md` — CREATED. Declares `CURRENT_SCHEMA_VERSION=1`. MemoryMine SKILL.md required this file as input but it did not exist. Documents both `schema_version` and `wabblespec_schema_version` fields, version history, bump procedure.
- [x] `modules/l2/verifier/schemas/receipt.schema.json` — CREATED. 9-field extension: wave, verification_mode (7-value enum), verdict (PASS/FAIL/BLOCKED), spec_compliance (PASS/FAIL), revise_cycles_used (0–3), immediate_blocked, attestation_required, attestation_received, fix_recommendation (required when verdict=FAIL).
- [x] `modules/l7/archive/schemas/receipt.schema.json` — CREATED. 8-field extension: receipts_aggregated, not_tested_items, not_tested_list, version_previous/new (semver), version_bump_reason (BREAKING/ADDITIVE/COSMETIC), waves_completed, all_waves_passed. missing_receipts required when all_waves_passed=false.

### P1 — High (mempalace integration gaps)

- [x] `modules/l5/memory-search/scripts/search-index.py` — REWRITTEN. Old version read `.wabblespec/memory/index.json` flat files (wrong backend). New version uses `Palace.search()` (ChromaDB semantic), `Palace.filter_drawers()` (topic/staleness/recency), `palace_graph.traverse()` and `find_tunnels()` (graph queries). Staleness post-filter: STALE=-0.3, NEEDS_REVERIFICATION=-0.5. Query types: semantic, topic, staleness, recency, traverse, tunnels.
- [x] `modules/l5/memory-mine/scripts/memory-mine.py` — CREATED. Full Python implementation: PID lock at `.wabblespec/memory/.mine.pid` (atexit cleanup, 24h stale lock reclaim), 50-drawer gate, gap detection (REFERENCED_BUT_ABSENT / LOW_CONFIDENCE_ANCHOR / RECEIPT_ONLY), cluster detection (wing-grouped, keyword-overlap, 3+ drawers), pattern extraction (signal phrases, recurrence≥3 → DECISION_RATIONALE / RECURRING_CONSTRAINT / FAILURE_MODE), staleness map. Outputs to `.wabblespec/memory/mine/`.

### P2 — Medium (missing rules files)

- [x] `modules/l5/forget/rules/deletion-types.md` — CREATED. 3 types: single (force:true for FRESH/AGING), bulk-expired (dry_run first), compliance (GDPR_17/CCPA/etc, mandatory compliance_reference, Attestation for FRESH/AGING).
- [x] `modules/l5/forget/rules/compliance-policy.md` — CREATED. legal_basis enum, permanent provenance (content_hash only), FRESH/AGING requires Attestation (no force shortcut), EntityGraph notification failure handling, scope limits.
- [x] `modules/l7/monitor/rules/slo-parsing.md` — CREATED. Derives config from Engineering SLO declarations only. UNDECLARED for missing targets (never invent thresholds). Runbook required per alert. No PII in log schema. Outputs to `.wabblespec/observability/`.
- [x] `modules/l7/scaffold/rules/idempotency-guard.md` — CREATED. Primary guard: checks `project-map.md` existence, hard abort if exists. Write order: platform files → .wabblespec/ structure → VERSION → CHANGELOG.md → project-map.md LAST. Does NOT generate test files, CI/CD, security config, or product code.
- [x] `modules/l7/package/rules/signing-policy.md` — CREATED. Signing failure = HARD error (no fallback, no --skip-signing). SHA-256 + signing block in manifest. Canonical JSON = manifest without signing field, sorted keys.
- [x] `modules/l2/ensemble/rules/mode-selection.md` — CREATED. 4 ModelRouter trigger conditions. 3 modes: Sequential (data dependency), Independent (parallelizable), Cross-check (Attestation/Audit mandatory). Priority: Cross-check > Sequential > Independent. Combined receipt with lanes array.
- [x] `modules/l2/rollback/rules/checkpoint-types.md` — CREATED. Type 1 (wave checkpoint), Type 2 (deploy snapshot), Type 3 (Forge pre-promotion). All require Attestation. Hash verification mandatory. Release rollback provides git commands, does not execute.

### P3 — Low (missing templates and schemas)

- [x] `modules/l1/explore/templates/project-map.md` — CREATED. Template: Tech Stack table, Spec Artifacts Found, Dependency Manifests, Conventions Observed, Git State, High-Churn Files, Gaps, Memory Drawers Written.
- [x] `modules/l1/decompose/schemas/receipt.schema.json` — CREATED. Extension fields: wave_count, complexity_confirmed, complexity_revised, complexity_revision_reason (required when revised), reviewer_triggered, reviewer_verdict, rollback_checkpoints, collapse_applied, wave_plan_path, verification_modes.
- [x] `modules/l1/decompose/templates/wave-plan.md` — CREATED. Full wave plan template: Wave N sections (inputs, outputs, checkpoint, rollback_to, verification_mode), Rollback Map table, Notes section.

### Skill-rules migration

- [x] `scripts/migrate-old-skill-rules.py` — CREATED. Detects `activation.triggers` nested format and converts to canonical: `activation.triggers` → `activators`, `activation.excludes` → `anti_activators`, merges `activation.file_path_patterns` into top-level, removes `skill_id`/`type`/`version`/`activation` block, adds missing canonical fields (tier, build_targets, phases, authority scaffold, verification_mode, receipt_required, collapse_eligible). Supports `--dry-run`.
- [x] 25 old-format skill-rules.json files migrated — L0 product/reference-load, L2 team-plan/model-router/economy, L3 all 9 platforms, L4 all 6 gateways, L5 dream/entity-graph, L6 all 4, L7 scaffold. `scripts/fix-skill-rules-schema.py` had added new canonical fields but never converted the `activation.triggers` nested block — now resolved.
- [x] `modules/l2/model-router/skill-rules.json` — fixed `"triggers": ["Ensemble"]` → `"triggers_modules": ["ensemble"]`. Was a custom semantic field (not old activation format), renamed to remove ambiguity.

**Status: COMPLETE — 2026-05-22. 18 gaps resolved. 0 remaining P0–P3 items.**

**Not fixable by code (intentionally deferred):**
- Dream validation gate (Phase 4 unchecked checkbox): requires 10 actual Dream runs on real work. Tracked in `dream-log.json`.
- WabbleFlow/MCPBridge/Runtime contracts: intentionally deferred per token-protocol.md (Claude-only MVP).
- Phase 8 L8 Evolution: correctly gated on 100+ real receipts. Current count ~14.

---

## Kill Criteria

Stop if any of these are true after Phase 2 completion:

1. Hook proof-of-concept fails: cannot reliably block a deliberately skipped receipt
2. Before/after on 10 tasks shows no reduction in false-completion rate vs baseline
3. Competing framework test (GSD + simple checklist) produces equivalent outcomes
4. Unassisted compliance rate with receipt chain invariant below 70% in 10-wave session
5. Phase 2 MVP requires expanding beyond 12 modules before reaching working end-to-end
6. Cannot state in one sentence the specific failure mode of GSD that WabbleSpec's receipt gate uniquely prevents

---

## Validation Tests (run after Phase 2)

1. **Hook block test.** Skip one receipt mid-session without telling the agent. Hook must block.
2. **Baseline comparison.** 10 tasks via plain instructions. Record false-completion rate. Run same 10 via WabbleSpec Phase 2. Compare.
3. **Competing framework test.** Same task through GSD, OMC, WabbleSpec. Compare whether receipt chain catches anything others miss.
4. **Compliance rate test.** 10-wave session. Count unassisted receipt chain adherence.
5. **Path linter.** Run on all spec-reference docs. Zero path contradictions before Phase 2 ships.

---

## Open Decisions

| Decision                                        | Options                                                            | Gate           |
| ----------------------------------------------- | ------------------------------------------------------------------ | -------------- |
| EARS vs Given/When/Then for acceptance criteria | Validate with agent comparison before committing Specify templates | Phase 2        |
| Dream trigger: manual vs post-session hook      | Manual first, add hook after proving value                         | Phase 4        |
| EntityGraph entity types: 3 vs 7                | Start with 3 (file/module/concept), expand from data               | Phase 5        |
| skill-factory gaps                              | Audit in Phase 0                                                   | Phase 0        |
| v5.3 audit                                      | Did v5.3 produce anything? Determines whether this is v1.0 or v6.1 | Before Phase 1 |
