# WabbleSpec Reference Integration Master Plan

Status: planning artifact only  
Created: 2026-05-22  
Workspace: `C:\Vaults\WabbleSpec v6.1`  
Primary current anchors:
- `C:\Vaults\WabbleSpec v6.1\BUILD-PLAN.md`
- `C:\Vaults\WabbleSpec v6.1\framework.yaml`

Primary reference-map anchors:
- `C:\Vaults\references\.planning\project-map`
- `C:\Vaults\references\Core Project References\.planning\project-map`
- `C:\Vaults\references\Extra Project References\.planning\project-map`
- `C:\Vaults\references\Other Projects References\.planning\project-map`

This plan is implementation-ready for manual integration. It does not copy reference projects. It maps reference concepts to WabbleSpec modules, gives exact paths to inspect, names risks, and orders integration from critical to later.

## 1. Executive Summary

The reference integration effort exists to strengthen WabbleSpec without turning it into a clone of GSD, OpenSpec, OMX, MemPalace, Cartographer, Superpowers, or any other reference. The useful work is concept extraction: gates, schemas, memory structures, graph maps, hook contracts, verification workflows, role boundaries, domain reference packs, packaging rules, and validation loops.

The reference folders matter because they contain a broad mapped corpus of 104 repo snapshots and 1,713 top-level path classifications. The project maps already resolve unknowns to zero and identify core/support/reference/generated boundaries. Use those maps first. Raw repo browsing comes later, only for the exact paths named here.

Use this plan as a manual queue. Start at Critical. For each item, inspect the exact reference path, extract the idea, write a small adaptation plan, integrate one WabbleSpec module or shared contract, run validation, then document the borrowed concept with path citations. Do not integrate lower-priority references until critical gates and schemas are stable.

Integrate first:
- Receipt enforcement backbone from `get-shit-done-main`, Wabble hooks, and existing receipt schemas.
- Formal spec/change schema discipline from `OpenSpec-main`.
- Project-map and impact context from `cartographer-main`.
- Local evidence memory from `mempalace-develop` plus FTS/search ideas from `context-mode-main`.
- Command safety policy from `destructive_command_guard-main` and `claude-code-safety-net-main`.
- Thin orchestration adapter ideas from `oh-my-codex-main`, without replacing WabbleSpec identity.

Avoid:
- Blind copying command surfaces, skill catalogs, generated bundles, marketplace directories, prompt instructions, or domain content.
- Reading or printing `.npmrc`, private journals, generated eval workspaces, or external connector configs.
- Building L8 Evolution before real receipt data exists.
- Treating duplicate references as independent signal.
- Treating critique calls to "shrink" as permission to abandon ambition. Reinterpret them as ordering discipline: prove gates early, then expand.

## 2. Current WabbleSpec Architecture

### Current Framework Summary

WabbleSpec is currently a spec-driven, receipt-gated, hook-enforced software-development framework inside `C:\Vaults\WabbleSpec v6.1`. `BUILD-PLAN.md` describes a built-out 2026-05-22 state with modules, hooks, `.wabblespec/`, receipts, memory, platform packages, gateways, delivery modules, and shared dev modules. `framework.yaml` describes the framework schema and module registry, but it is stale in several layer/path/status fields.

Important source-truth note:
- `BUILD-PLAN.md` is more current for build status and path corrections.
- `framework.yaml` remains important for declared module ids, schema consumers, tags, and dependencies.
- `spec-reference\planning` remains important for original architectural intent and module boundaries.
- The live `modules\` directory confirms 327 files and 59 `skill-rules.json` files.

Known conflict to fix before future build planning:
- `framework.yaml` still says `archive` is `modules/l2/archive/`; current build moved it to `modules/l7/archive/`.
- `framework.yaml` still says `economy` is `modules/l6/economy/`; current build moved it to `modules/l2/economy/`.
- `framework.yaml` marks many modules planned/deferred despite built files in `modules\`.
- `modules/l8` is missing in the live module tree even though planning docs describe L8 and `BUILD-PLAN.md` says L8 pipeline planning exists.

### Current Module List

L0 Intake:
- `product`
- `recipe`
- `reference-load`
- `runtime-probe`

L1 Spec Core:
- `apply`
- `clean`
- `decompose`
- `explore`
- `interview`
- `migrate`
- `propose`
- `scope-frame`
- `specify`
- `test`
- `triage`

L2 Orchestration:
- `autopilot`
- `economy`
- `ensemble`
- `executor`
- `guard`
- `model-router`
- `reviewer`
- `rollback`
- `team-plan`
- `verifier`

L3 Platform:
- `ai-agent`
- `api-service`
- `cli`
- `data-pipeline`
- `desktop`
- `extension`
- `game`
- `iot`
- `library`
- `mobile`
- `web`

L4 Capability:
- `aesthetic`
- `ai`
- `design`
- `engineering`
- `experience`
- `security`

L5 Memory:
- `dream`
- `entity-graph`
- `forget`
- `memory`
- `memory-mine`
- `memory-search`
- `provenance`

L6 Expression:
- `document`
- `homowabian`
- `polish`
- `research-log`

L7 Delivery:
- `archive`
- `deploy`
- `monitor`
- `package`
- `release`
- `scaffold`

Shared:
- `_shared\schemas\receipt.base.schema.json`
- `_shared\schemas\skill-rules.schema.json`
- `_shared\schemas\error-event.schema.json`
- `_shared\schemas\drawer.schema.json`
- `_shared\dev\languages`
- `_shared\dev\databases`
- `_shared\dev\api`
- `_shared\references`

Planned but not present as live module folders:
- L8 `instinct`, `synth`, `blueprint`, `factory`, `augment`, `benchmark`, `forge`, `feedback`, `retro`.

### Module Purposes

| Module | Current Purpose | Main Outputs |
|---|---|---|
| Product | Product goals, user segments, success metrics | `product-context.md` |
| Recipe | Target detection and initial routing | `.wabblespec\recipe.json`, recipe receipt |
| ReferenceLoad | External/internal reference loading with trust and staleness | Memory drawers, reference receipt |
| RuntimeProbe | Runtime capability detection | runtime state, capability descriptors |
| ScopeFrame | Scope, authority, assumptions, boundaries | `.wabblespec\scope.md`, scope receipt |
| Specify | Intent to P1-P4 specs/task cards | spec artifacts, specify receipt |
| Explore | Codebase/reference discovery | `project-map.md`, memory drawers |
| Interview | Ambiguity reduction | `intent.md` |
| Propose | Options and tradeoff selection | options artifact, proposal receipt |
| Decompose | Wave plan and acceptance criteria | wave plan, decompose receipt |
| Apply | Spec-to-artifact application and patch routing | product deltas, apply receipt |
| Test | Acceptance-to-test mapping | test stubs/cases, test receipt |
| Clean | Behavior-preserving cleanup | scoped cleanup diff, clean receipt |
| Triage | Issue classification/routing | triage records |
| Migrate | Breaking-change migration | migration plan, consumer guide |
| Executor | Wave execution | execution artifacts, execution receipt |
| Guard | Invariant, authority, scope, receipt validation | PASS/error event |
| Verifier | Declared checks and revise loop | verification receipt |
| Reviewer | Adversarial critique and grading | ACCEPT/REVISE/ESCALATE |
| Rollback | Checkpoint/worktree/deploy restore | rollback receipt |
| Autopilot | Lifecycle orchestration | meta/state updates |
| Economy | Token density and context placement | compression decisions |
| ModelRouter | Runtime lane selection | runtime receipt |
| Ensemble | Multi-lane coordination | combined receipt |
| TeamPlan | Multi-agent handoff plan | team plan |
| L3 Platforms | Target-specific specs/gates/security/engineering | platform receipts/templates |
| L4 Gateways | Cross-cutting capability policy | audit/review inputs |
| Memory | Evidence drawers/staleness | drawers, memory receipt |
| MemorySearch | Evidence retrieval | ranked evidence |
| Provenance | Lineage and cascade trace | ledger, citation records |
| EntityGraph | Entity/relationship index | graph index |
| Dream | Staleness/gap consolidation | gap-map, staleness-map |
| MemoryMine | Pattern mining | cluster/pattern outputs |
| Forget | Controlled deletion | deletion records |
| Homowabian | Voice/register discipline | expression decisions |
| Document | Documentation generation | docs from specs/receipts |
| Polish | Non-semantic refinement | diff and polish receipt |
| ResearchLog | Research capture | research drawers/log |
| Archive | Receipt index and changelog | archive index/version |
| Package | Signed/versioned package artifacts | manifest |
| Deploy | Deployment with rollback plan | deploy receipt |
| Release | Tag/release notes/publish | release receipt |
| Scaffold | Idempotent project structure generation | scaffolded structure |
| Monitor | Observability config | metrics, alerts, dashboards |

### Module Dependencies

Critical flow:
`Recipe -> ScopeFrame/ReferenceLoad/RuntimeProbe -> Specify -> Decompose -> Executor -> Verifier -> Archive`

Implementation flow:
`Recipe -> L3 Platform + _shared/dev + L4 Gateways -> Apply -> Executor -> Verifier`

Memory flow:
`Memory -> MemorySearch/Provenance -> EntityGraph -> Dream -> MemoryMine`

Runtime flow:
`RuntimeProbe -> ModelRouter -> Ensemble`

Delivery flow:
`Verifier + Archive -> Package -> Deploy -> Release -> Monitor`

Evolution flow:
`Archive receipts -> Instinct -> Synth -> Blueprint -> Augment/Factory -> Benchmark -> Forge`

### Current Strengths

- Real hook exists: `hooks\pre-tool-use-receipt-check.py`.
- Real schemas exist: `_shared\schemas\receipt.base.schema.json`, `_shared\schemas\skill-rules.schema.json`, `_shared\schemas\error-event.schema.json`, `_shared\schemas\drawer.schema.json`.
- Real `.wabblespec\` state exists with receipts, memory, plans, checkpoints, archive, session state.
- Live modules exist across L0-L7 with `SKILL.md` and `skill-rules.json`.
- `file_path_patterns` already exists in the skill-rules schema.
- `BUILD-PLAN.md` records concrete validation examples for Phase 1 hook, Phase 2 receipt chain, Phase 3 memory, Phase 4 Dream, L3 CLI/Web/API gates, and L4 Security.

### Current Weaknesses

- `framework.yaml` is stale against live modules and `BUILD-PLAN.md`.
- L8 module folders are absent.
- Many module quality floors are false/stale in `framework.yaml`.
- Later claims are mostly module-build claims, not real-project validation claims.
- Dream behavior-change validation remains a long-run risk even if script exists.
- Memory integration direction changed: early planning rejected ChromaDB, while `BUILD-PLAN.md` now approves MemPalace/ChromaDB as backend. This needs a formal decision record.
- Delivery pipeline done condition requires a full real run; evidence from read scope is not enough to claim this.
- Platform packages exist, but many need external reference hardening and real target runs.

### Missing Pieces

- `framework.yaml` refresh.
- L8 live module folders or explicit "planned only" status.
- `/wabble-health` or equivalent diagnostic command.
- Machine validation that all `skill-rules.json` layer/path/status fields match the live tree.
- Baseline comparison against plain AGENTS.md/GSD/OMX.
- Real multi-project receipt-chain corpus.
- Outcome-linked benchmark suite.

### Unclear Areas

- Whether WabbleSpec should remain local-first with optional local scripts/SQLite or fully adopt MemPalace/ChromaDB.
- Whether vendor-neutral runtime is still active policy or a later adapter goal.
- Whether specs live in product space (`project/repo/specs`) or framework space for all use cases.
- Whether `ResearchLog`, `Homowabian`, and `Economy` are durable modules or rules within other modules.
- Whether L8 is a build target or a future research track.

## 3. Critique Synthesis

### Major Critiques Found

The critique corpus says:
- The project risks mistaking document mass for implementation.
- Receipt chains are theater if only LLM-written and LLM-checked.
- Vendor-neutral claims are not earned until at least two runtime adapters work.
- Memory is dangerous if it is file discipline without real validation.
- L8 Evolution is ungrounded before a receipt corpus exists.
- 11 platform targets are dangerous before one or three prove target-specific value.
- Formal scoring, EARS enforcement, and multi-agent routing must be validated, not assumed.
- Existing GSD, OMC, OpenSpec, spec-kit, agent-os, and Superpowers overlap heavily.

### What They Mean

The critiques are not a command to abandon ambition. They are a command to stop letting unproven layers sit in the same priority bucket as proven gates. WabbleSpec's ambition is strongest when staged:
1. Mechanical enforcement.
2. Spec/change schemas.
3. Evidence memory.
4. Platform-specific value.
5. Provenance/cascade.
6. Graph/mining/evolution.

### What To Follow

- Build and validate mechanical hooks before expanding behavior modules.
- Keep receipts, but bind them to executed checks and schema validation.
- Keep memory/staleness, but start with FRESH/EXPIRED or clearly justify richer states.
- Keep platform routing, but prove differences with CLI/Web/API before broad expansion.
- Keep L8 as an explicit future track gated by 100+ verified receipts.
- Add health diagnostics.
- Compare against GSD/OMX/OpenSpec baselines.

### What To Reject

- Reject deleting WabbleSpec's differentiators only because they are ambitious.
- Reject copying any reference project wholesale.
- Reject product-market critiques when the goal is personal/project infrastructure, unless the project becomes a product.
- Reject generic "shrink" as a permanent scope reduction.
- Reject benchmark claims without developer-outcome evidence.

### What To Reinterpret

| Critique Phrase | Reinterpretation |
|---|---|
| Shrink | Stage active implementation behind gates; keep ambition as roadmap |
| Receipts are theater | Receipts need hook/schema/check binding |
| Vendor neutral is false | Make single-runtime explicit now; earn neutrality later |
| Memory is overbuilt | Build core memory first; defer graph/mining/dream |
| 11 targets are too many | Integrate target refs in priority order, not all at once |
| L8 is fantasy | L8 is later research, not current runtime |

### Keep Ambition Without Chaos

Use a proof ladder:
1. Receipt hook blocks missing or invalid upstream receipts.
2. WabbleSpec runs one CLI/Web/API task with correct receipts.
3. WabbleSpec beats plain AGENTS.md on false completion or missed-check rate.
4. WabbleSpec catches a failure GSD/OMX misses.
5. Memory prevents stale evidence from being used.
6. Platform routing produces a spec/gate a generic template misses.
7. Provenance marks downstream specs when a source changes.
8. EntityGraph only starts when MemorySearch limitations are proven.
9. L8 starts only after real receipt data exists.

## 4. Reference Inventory

### Reference: oh-my-codex-main

- Path: `C:\Vaults\references\Core Project References\oh-my-codex-main`
- Category: Core
- Purpose: Codex orchestration layer with `omx` CLI, skills, prompts, hooks, MCP/state helpers, and Rust helper crates.
- Strongest Concepts: Codex-native runtime, role prompt registry, team runtime, hook lifecycle, skill/plugin mirroring, compact explore/sparkshell workflows.
- Strongest Files/Folders: `src`, `skills`, `prompts`, `templates`, `plugins/oh-my-codex`, `.agents/plugins/marketplace.json`, `crates`.
- Useful For These WabbleSpec Modules: Autopilot, TeamPlan, ModelRouter, Ensemble, Economy, Guard, Explore.
- Integration Value: Very high. Current workspace already runs OMX/WabbleHooks; this is the closest architecture reference.
- Integration Risk: High. Large surface, skill mirror drift, runtime coupling.
- Priority: Critical.
- Notes: Integrate thin adapters and ideas only. Do not make WabbleSpec an OMX clone.

### Reference: get-shit-done-main

- Path: `C:\Vaults\references\Core Project References\get-shit-done-main`
- Category: Core
- Purpose: Workflow system with installer, commands, agents, hooks, templates, references, and TypeScript SDK.
- Strongest Concepts: phase gates, state, workstreams, plan/execute/verify split, verification evidence, codebase mapping.
- Strongest Files/Folders: `get-shit-done`, `commands/gsd`, `agents`, `hooks`, `sdk/src`, `tests`.
- Useful For These WabbleSpec Modules: Recipe, Decompose, Executor, Verifier, Archive, Guard, Autopilot.
- Integration Value: Critical. Directly informs receipt-gated phase execution.
- Integration Risk: Medium. Avoid copying workflow sprawl.
- Priority: Critical.
- Notes: First manual integration source for receipt enforcement and verification separation.

### Reference: OpenSpec-main

- Path: `C:\Vaults\references\Core Project References\OpenSpec-main`
- Category: Core
- Purpose: AI-native spec-driven CLI/framework with schemas, changes, specs, and validation.
- Strongest Concepts: spec schema, change schema, proposal lifecycle, archive flow, spec corpus.
- Strongest Files/Folders: `src`, `bin`, `schemas`, `openspec/specs`, `openspec/changes`, `test`.
- Useful For These WabbleSpec Modules: Specify, ScopeFrame, Migrate, Archive, Guard.
- Integration Value: Critical for formal spec/change validation.
- Integration Risk: Medium. It is not WabbleSpec's execution engine.
- Priority: Critical.
- Notes: Copy schema discipline, not CLI identity.

### Reference: cartographer-main

- Path: `C:\Vaults\references\Core Project References\cartographer-main`
- Category: Core
- Purpose: Bun TypeScript code graph CLI/plugin for indexing, briefs, audits, notes, SQLite graph storage, MCP, and evals.
- Strongest Concepts: code graph, impact/context briefs, audits, notes, deterministic eval reports.
- Strongest Files/Folders: `src/code-graph`, `src/cli/index.ts`, `plugins/cartographer`, `docs/features`, `docs/evals`.
- Useful For These WabbleSpec Modules: Explore, ReferenceLoad, EntityGraph, MemorySearch, Decompose.
- Integration Value: Critical for project/reference mapping.
- Integration Risk: Medium. Generated docs/reports and old graph docs need care.
- Priority: Critical.
- Notes: Use for WabbleSpec `project-map` and impact-context design.

### Reference: mempalace-develop

- Path: `C:\Vaults\references\Core Project References\mempalace-develop`
- Category: Core
- Purpose: Local-first AI memory package with Chroma backend, MCP server, CLI, hooks, Codex/Claude plugins.
- Strongest Concepts: memory drawers, search/storage separation, session mining, hook capture, knowledge graph.
- Strongest Files/Folders: `mempalace`, `hooks`, `.claude-plugin`, `.codex-plugin`, `tests`, `docs/schema.sql`.
- Useful For These WabbleSpec Modules: Memory, MemorySearch, Provenance, Dream, MemoryMine, EntityGraph.
- Integration Value: Critical, especially because `BUILD-PLAN.md` now approves MemPalace backend integration.
- Integration Risk: High. ChromaDB and MCP/tooling details conflict with earlier no-dependency/no-MCP planning.
- Priority: Critical.
- Notes: Formalize backend decision before deeper integration.

### Reference: context-mode-main

- Path: `C:\Vaults\references\Extra Project References\context-mode-main`
- Category: Extra
- Purpose: Context-saving MCP plugin with FTS5 store, sandboxed execution, intent search, and cross-host adapters.
- Strongest Concepts: SQLite/FTS5 retrieval, sandboxed verbose output, session continuity, memory diagnostics.
- Strongest Files/Folders: `src/server.ts`, `src/store.ts`, `src/executor.ts`, `src/session`, `hooks`, `.codex-plugin/plugin.json`.
- Useful For These WabbleSpec Modules: MemorySearch, Memory, Economy, Guard, Autopilot.
- Integration Value: Critical for local searchable state without embeddings.
- Integration Risk: High. Hook auto-injection and filesystem scope need control.
- Priority: Critical.
- Notes: Good alternative/complement to MemPalace search.

### Reference: destructive_command_guard-main

- Path: `C:\Vaults\references\Other Projects References\destructive_command_guard-main\destructive_command_guard-main`
- Category: Other
- Purpose: Rust destructive-command guard with policy, tests, action, fuzzing, and benchmarks.
- Strongest Concepts: pre-exec command classification, block/warn/explain policy, shell safety.
- Strongest Files/Folders: `src`, `build.rs`, `Cargo.toml`, `action/action.yml`, `tests`, `fuzz`, `benches`, `SKILL.md`.
- Useful For These WabbleSpec Modules: Guard, Executor, Rollback, Verifier.
- Integration Value: Critical for safety gates.
- Integration Risk: Medium. Policy must match WabbleSpec's execution context.
- Priority: Critical.
- Notes: `build.rs` is source, not generated.

### Reference: claude-code-safety-net-main

- Path: `C:\Vaults\references\Other Projects References\claude-code-safety-net-main\claude-code-safety-net-main`
- Category: Other
- Purpose: Claude/OpenCode plugin blocking destructive git/filesystem commands.
- Strongest Concepts: TypeScript hook guard, plugin packaging, command policy.
- Strongest Files/Folders: `src`, `hooks`, `commands`, `scripts`, `tests`, `.claude-plugin/plugin.json`.
- Useful For These WabbleSpec Modules: Guard, Executor, Rollback.
- Integration Value: Critical complement to destructive command guard.
- Integration Risk: Medium. `dist` may be generated but runnable.
- Priority: Critical.
- Notes: Use as lightweight policy contrast.

### Reference: claude-code-security-review-main

- Path: `C:\Vaults\references\Core Project References\claude-code-security-review-main`
- Category: Core
- Purpose: GitHub Action and Claude Code slash command for PR security review.
- Strongest Concepts: PR diff audit, generated-file filtering, finding parsing, comment publishing.
- Strongest Files/Folders: `action.yml`, `claudecode`, `scripts/comment-pr-findings.js`, `.claude/commands/security-review.md`, tests/evals.
- Useful For These WabbleSpec Modules: Reviewer, Security, Verifier, Triage.
- Integration Value: High.
- Integration Risk: Medium. Trusted-PR assumptions and prompt-injection risks.
- Priority: High.
- Notes: Extract finding schema and review flow, not GitHub-only assumptions.

### Reference: superpowers-main

- Path: `C:\Vaults\references\Core Project References\superpowers-main`
- Category: Core
- Purpose: Cross-agent software-development methodology/skill/plugin bundle.
- Strongest Concepts: verification-before-completion, TDD, debugging methods, worktree isolation, skill-trigger discipline.
- Strongest Files/Folders: `skills`, `hooks`, `.opencode/plugins/superpowers.js`, `.codex-plugin`, `.claude-plugin`, `tests`.
- Useful For These WabbleSpec Modules: Decompose, Executor, Verifier, Reviewer, Rollback, Test.
- Integration Value: High.
- Integration Risk: Medium. Host-specific instructions should not be copied as rules.
- Priority: High.
- Notes: Worktree isolation is worth adapting for high-risk waves.

### Reference: graphify-7

- Path: `C:\Vaults\references\Core Project References\graphify-7`
- Category: Core
- Purpose: Python CLI/package for graphifying code/docs/media into queryable knowledge graphs and assistant skills.
- Strongest Concepts: graph extraction, path queries, clustering, exports, global graph.
- Strongest Files/Folders: `graphify`, `graphify/skill*.md`, `pyproject.toml`, `tests`, `docs/how-it-works.md`, `worked`.
- Useful For These WabbleSpec Modules: EntityGraph, MemoryMine, Dream, Synth, Explore.
- Integration Value: High but later.
- Integration Risk: High. Graph before evidence corpus is bloat.
- Priority: Later/High.
- Notes: Gate behind real MemorySearch failures.

### Reference: agent-os-main

- Path: `C:\Vaults\references\Core Project References\agent-os-main`
- Category: Core
- Purpose: Lightweight Agent OS standards/spec workflow installer.
- Strongest Concepts: standards discovery, standards injection, product/spec shaping.
- Strongest Files/Folders: `commands/agent-os`, `scripts`, `config.yml`, `profiles/default/global/tech-stack.md`.
- Useful For These WabbleSpec Modules: Product, ScopeFrame, Specify, Explore, Economy.
- Integration Value: High.
- Integration Risk: Medium. Shell/client-specific flow.
- Priority: High.
- Notes: Use "discover before prescribe" to harden standards extraction.

### Reference: caveman-main

- Path: `C:\Vaults\references\Core Project References\caveman-main`
- Category: Core
- Purpose: Compressed-output mode, hooks, skills, commands, agents, and MCP shrink proxy across hosts.
- Strongest Concepts: compact output policy, hook activation, context economy, MCP description compression.
- Strongest Files/Folders: `bin`, `src/hooks`, `src/mcp-servers/caveman-shrink`, `commands`, `skills`, `agents`, `plugins/caveman`, `.codex`.
- Useful For These WabbleSpec Modules: Economy, RuntimeProbe, ModelRouter, Homowabian.
- Integration Value: High.
- Integration Risk: Medium. Provider copies and generated artifacts require care.
- Priority: High.
- Notes: Current session uses Caveman mode, so integration must not fight active output policy.

### Reference: codeflow-main

- Path: `C:\Vaults\references\Core Project References\codeflow-main`
- Category: Core
- Purpose: Browser-first architecture/dependency/security/health analyzer plus action card generator.
- Strongest Concepts: health card, analyzer UI, drift tests, SVG/report rendering.
- Strongest Files/Folders: `index.html`, `card`, `card/lib/analyzer.js`, `tests`.
- Useful For These WabbleSpec Modules: Monitor, Archive, Benchmark, Document.
- Integration Value: Medium.
- Integration Risk: Medium. Large coupled HTML/analyzer.
- Priority: Medium.
- Notes: Use for `/wabble-health` and receipt dashboard concept.

### Reference: anthropic-skills-main

- Path: `C:\Vaults\references\Core Project References\anthropic-skills-main`
- Category: Core
- Purpose: Official example skill suite for documents, artifacts, API, MCP, web testing, skill creation.
- Strongest Concepts: skill anatomy, scripts in skills, references/templates, evals.
- Strongest Files/Folders: `.claude-plugin/marketplace.json`, `skills/*/SKILL.md`, `template`, `spec`, skill scripts.
- Useful For These WabbleSpec Modules: L3 Platforms, Document, Skill packaging, Test.
- Integration Value: Medium.
- Integration Risk: Medium. Heavy assets and licenses.
- Priority: Medium.
- Notes: Use as skill-packaging reference only.

### Reference: ui-ux-pro-max-skill-main

- Path: `C:\Vaults\references\Core Project References\ui-ux-pro-max-skill-main`
- Category: Core
- Purpose: UI/UX design intelligence skill and installer.
- Strongest Concepts: design datasets, design-system skill packaging, installer lifecycle.
- Strongest Files/Folders: `skill.json`, `src/ui-ux-pro-max`, `cli/src`, `cli/assets`, `.claude/skills`, `.claude-plugin`.
- Useful For These WabbleSpec Modules: Web, Aesthetic, Design, Experience.
- Integration Value: Medium.
- Integration Risk: Medium. Version/license mismatches and duplicate data.
- Priority: Medium.
- Notes: Use for UI reference packs after core gates.

### Reference: Claude-Code-Game-Studios-main

- Path: `C:\Vaults\references\Core Project References\Claude-Code-Game-Studios-main`
- Category: Core
- Purpose: Game studio template with agents, skills, hooks, rules, registries, engine references.
- Strongest Concepts: domain template layout, path-scoped rules, engine reference docs.
- Strongest Files/Folders: `.claude`, `CCGS Skill Testing Framework`, `docs/engine-reference`, `docs/architecture`, `design/registry`.
- Useful For These WabbleSpec Modules: Game platform, skill-rules path patterns, hooks.
- Integration Value: Medium.
- Integration Risk: Medium. 49-agent/73-command theater risk.
- Priority: Medium.
- Notes: Extract path-scoped activation and game domain layout only.

### Reference: adversarial-spec-main

- Path: `C:\Vaults\references\Other Projects References\adversarial-spec-main\adversarial-spec-main`
- Category: Other
- Purpose: Multi-model adversarial spec refinement.
- Strongest Concepts: adversarial debate, consensus, early-agreement verification, interview mode.
- Strongest Files/Folders: `skills/adversarial-spec/SKILL.md`, Python debate/provider/session scripts, `.claude-plugin`.
- Useful For These WabbleSpec Modules: Reviewer, Propose, Specify, AI gateway.
- Integration Value: Later.
- Integration Risk: High. Provider execution not verified here.
- Priority: Later/Experimental.
- Notes: Use after baseline verifier works.

### Reference: hyperframes-main

- Path: `C:\Vaults\references\Extra Project References\hyperframes-main`
- Category: Extra
- Purpose: HTML-native video rendering framework plus agent skills/plugins.
- Strongest Concepts: render pipeline, registry, block/component catalog.
- Strongest Files/Folders: `packages/cli`, `packages/core`, `packages/engine`, `packages/producer`, `packages/player`, `packages/studio`, `registry`, `skills`.
- Useful For These WabbleSpec Modules: future visual/media platform, Package, Monitor.
- Integration Value: Low now, high for visual/media later.
- Integration Risk: High. Media/generated footprint.
- Priority: Later.
- Notes: Do not include in core framework.

### Reference: claude-plugins-official-main

- Path: `C:\Vaults\references\Core Project References\claude-plugins-official-main`
- Category: Core
- Purpose: Official plugin marketplace/catalog snapshot.
- Strongest Concepts: marketplace manifest, plugin validation, MCP configs, local/external plugin structure.
- Strongest Files/Folders: `.claude-plugin/marketplace.json`, `plugins`, `external_plugins`, `.github/scripts`, `.github/workflows`.
- Useful For These WabbleSpec Modules: Extension/Plugin, Package, Release, Scaffold.
- Integration Value: Low/Medium.
- Integration Risk: Medium. `.npmrc` paths exist and were intentionally not read.
- Priority: Low.
- Notes: Use for manifest schema only.

### Reference: financial-services-main

- Path: `C:\Vaults\references\Core Project References\financial-services-main`
- Category: Core
- Purpose: Financial-services marketplace with vertical plugins, managed-agent cookbooks, partner plugins, provisioning.
- Strongest Concepts: vertical plugin packs, cookbooks, manifest validation, skill sync.
- Strongest Files/Folders: `.claude-plugin/marketplace.json`, `plugins`, `managed-agent-cookbooks`, `scripts/check.py`, `scripts/sync-agent-skills.py`.
- Useful For These WabbleSpec Modules: future domain packs, Package, Release.
- Integration Value: Low.
- Integration Risk: Medium. Connector/external access unavailable.
- Priority: Low.
- Notes: Useful only after core platform packs stabilize.

### Reference: G0DM0D3-main

- Path: `C:\Vaults\references\Core Project References\G0DM0D3-main`
- Category: Core
- Purpose: Multi-model chat/research app with Next frontend, Express API, HF variant, telemetry.
- Strongest Concepts: model racing, AutoTune, prompt transformation, feedback datasets.
- Strongest Files/Folders: `index.html`, `src`, `api`, `HF`, `functions/api/telemetry.ts`, `research`.
- Useful For These WabbleSpec Modules: Benchmark, Feedback, AI gateway.
- Integration Value: Later/experimental.
- Integration Risk: High. Privacy/consent/PII and duplicate root files require review.
- Priority: Later.
- Notes: Do not use until AI/Benchmark work begins.

### Reference: Open-LLM-VTuber-main

- Path: `C:\Vaults\references\Extra Project References\Open-LLM-VTuber-main`
- Category: Extra
- Purpose: Voice-interactive local AI companion with ASR/TTS/VAD, Live2D, MCP, character YAML.
- Strongest Concepts: local multimodal runtime, character configuration, provider abstraction.
- Strongest Files/Folders: `run_server.py`, `src/open_llm_vtuber`, `characters`, `prompts`, `web_tool`, `mcp_servers.json`, `model_dict.json`.
- Useful For These WabbleSpec Modules: future voice/embodied interface.
- Integration Value: Low.
- Integration Risk: High. Media-heavy, not core.
- Priority: Later/Experimental.
- Notes: Keep out of core WabbleSpec.

### Reference: top-ranked Low/Rejected Surface References

These are intentionally low authority or rejected:
- `C:\Vaults\WabbleSpec v6.1\learnings and critics\Reference`: older surface-level WabbleSpec reference notes. Use only as supporting material.
- `C:\Vaults\references\Other Projects References\marketingskills-main (1)\marketingskills-main`: duplicate.
- `C:\Vaults\references\Other Projects References\claudian-main\claudian-main`: duplicate.
- `C:\Vaults\references\Other Projects References\superpowers-main\superpowers-main`: duplicate of core Superpowers signal.
- `C:\Vaults\references\Other Projects References\template`: scaffold only.
- `C:\Vaults\references\Other Projects References\claude-skills-main\custom-gpt`: archive/reference only.
- `C:\Vaults\references\Other Projects References\claude-skills-main\eval-workspace`: generated eval workspace.

## 5. Module-to-Reference Matrix

| WabbleSpec Module | Current Weakness | Best Reference | Exact Reference Path | Useful Concept | How To Adapt | Priority | Risk | Manual Integration Notes |
|---|---|---|---|---|---|---|---|---|
| Product | Thin product context; not tied to standards | agent-os-main | `C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os` | product planning and standards discovery | Add product-context plus discovered standards profile | High | Medium | Do before Specify schema hardening |
| Recipe | Target detection needs reference-backed signals | cartographer-main, get-shit-done-main | `C:\Vaults\references\Core Project References\cartographer-main\src\code-graph`; `C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd` | project indexing and phase routing | Use graph/signals to justify target selection | Critical | Medium | Update `recipe.json` evidence fields |
| ReferenceLoad | Risk of arbitrary reference sprawl | cartographer-main | `C:\Vaults\references\Core Project References\cartographer-main\docs\features` | bounded briefs and context slicing | Load exact reference cards and map snippets only | Critical | Low | Prevent raw repo over-reading |
| RuntimeProbe | Vendor-neutral claims unearned | oh-my-codex-main, caveman-main | `C:\Vaults\references\Core Project References\oh-my-codex-main\src`; `C:\Vaults\references\Core Project References\caveman-main\src` | runtime detection and context economy | Make current runtime explicit; log adapter gaps | High | High | Earn neutrality later |
| ScopeFrame | Scope conflicts across docs | OpenSpec-main, agent-os-main | `C:\Vaults\references\Core Project References\OpenSpec-main\schemas`; `agent-os-main\commands\agent-os` | schema-backed boundaries | Add scope schema and standards links | Critical | Medium | Must resolve spec location policy |
| Specify | EARS/templates need validation | OpenSpec-main | `C:\Vaults\references\Core Project References\OpenSpec-main\schemas`, `openspec\specs`, `openspec\changes` | spec/change lifecycle | Add schema and change classification checks | Critical | Medium | Compare EARS vs GWT before hardening |
| Explore | Project maps not yet formalized as runtime dependency | cartographer-main | `C:\Vaults\references\Core Project References\cartographer-main\src\code-graph` | index/brief/impact/context | Build Wabble project-map contract | Critical | Medium | First reference-loading enabler |
| Interview | Ambiguity logic needs adversarial controls | adversarial-spec-main, agent-creator | `C:\Vaults\references\Other Projects References\adversarial-spec-main\adversarial-spec-main\skills\adversarial-spec\SKILL.md`; `C:\Vaults\references\Extra Project References\agent-creator` | interview/debate boundary | Use only for high ambiguity | Medium | High | Do not make multi-model default |
| Propose | Options risk vague tradeoffs | agent-os-main, adversarial-spec-main | listed above | proposal and consensus structure | Require 2-4 bounded options with evidence | Medium | Medium | Keep simple |
| Decompose | Wave planning needs proven phase model | get-shit-done-main, superpowers-main | `C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`; `superpowers-main\skills` | phase/wave and worktree mental model | Tie waves to receipts and rollback type | High | Medium | Useful before Executor changes |
| Apply | Path authority risks | OpenSpec-main, get-shit-done-main | `OpenSpec-main\openspec\changes`; `get-shit-done-main\hooks` | change application and phase boundary | Require delta class and receipt gate | High | Medium | Avoid framework/product mixing |
| Test | Needs explicit acceptance-test mapping | superpowers-main, mattpocock-skills-main | `superpowers-main\skills`; `mattpocock-skills-main\skills\engineering` | TDD and verification-before-complete | Map every acceptance criterion to a test or not-tested note | High | Low | High leverage |
| Clean | Cleanup requires behavior lock | superpowers-main | `C:\Vaults\references\Core Project References\superpowers-main\skills` | behavior-preserving cleanup discipline | Require regression lock before cleanup | Medium | Low | Align with AGENTS cleanup rules |
| Triage | Needs specific defect taxonomy | get-shit-done-main | `C:\Vaults\references\Core Project References\get-shit-done-main\get-shit-done` | named defect patterns | Add symptom/detection/fix/test anchors | High | Medium | Improves error taxonomy |
| Migrate | Needs formal change lifecycle | OpenSpec-main | `C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes` | change proposals and archive | Use BREAKING/ADDITIVE/COSMETIC with downstream flags | Critical | Medium | Connect to Provenance |
| Autopilot | Orchestration can become opaque | oh-my-codex-main, GSD | `oh-my-codex-main\src`; `get-shit-done-main\commands\gsd` | command/runtime/state model | Build health-visible orchestration state | Critical | High | Thin adapter only |
| Economy | Thin module; needs mechanical policy | caveman-main, context-mode-main | `caveman-main\src`; `context-mode-main\src` | compression, sandboxed outputs | Add measurable token/context policy | High | Medium | Avoid prose-only economy |
| Ensemble | Unvalidated multi-lane execution | oh-my-codex-main | `oh-my-codex-main\src\team` if present in source tree | team/runtime concepts | Defer until single lane verified | Later | High | Keep planned only |
| Executor | Needs safe and auditable execution | get-shit-done-main, destructive_command_guard-main | `get-shit-done-main\commands\gsd`; `destructive_command_guard-main\src` | execute phase plus command guard | Check receipts before and after each wave | Critical | Medium | Top 5 integration |
| Guard | Real differentiator, needs stronger policies | destructive_command_guard-main, claude-code-safety-net-main | listed above | pre-tool command safety and policy | Add policy table and block/warn semantics | Critical | Medium | Must not overblock |
| ModelRouter | Runtime abstraction risky | oh-my-codex-main, caveman-main | listed above | role/routing evidence | Route by current available capabilities and log fallback | High | High | Adapter later |
| Reviewer | Needs structured findings | claude-code-security-review-main, agent-creator | `claude-code-security-review-main\claudecode`; `agent-creator\references\prompt-patterns.md` | finding schema and hard-stop role prompt | Output findings with severity/evidence/fix | High | Medium | Use prompt-injection caution |
| Rollback | Checkpoints weaker than git isolation | superpowers-main | `C:\Vaults\references\Core Project References\superpowers-main\skills` | worktree isolation | Add worktree rollback target for high-risk waves | High | Medium | Keep checkpoint for low-risk |
| TeamPlan | Multi-agent bloat risk | oh-my-codex-main, awesome-claude-agents-main | `oh-my-codex-main\prompts`; `C:\Vaults\references\Other Projects References\awesome-claude-agents-main` | bounded role registry | Gate behind high complexity only | Later | High | No 49-agent copy |
| Verifier | Must bind checks to receipts | get-shit-done-main, toprank-main | `get-shit-done-main\commands\gsd`; `C:\Vaults\references\Extra Project References\toprank-main` | verify-work and fixture evals | Persist check evidence and not-tested list | Critical | Medium | First integration |
| L3 Web | Needs UI/design/security hardening | ui-ux-pro-max, hig-doctor, superpowers-chrome | paths above | UI audit/browser verification | Add web-specific gates from refs | Medium | Medium | after core |
| L3 API-Service | Needs API-specific contract refs | claude-cookbooks, OpenSpec | `claude-cookbooks-main\claude_agent_sdk`; `OpenSpec-main\schemas` | API/agent examples and schemas | Use after spec schema stable | Medium | Medium | external setup risk |
| L3 CLI | Needs command UX/exit code refs | get-shit-done-main, agent-os-main | listed above | command lifecycle | Strengthen CLI gates | High | Low | already validated in BUILD-PLAN |
| L3 Mobile | Needs HIG/store/platform refs | hig-doctor-main, aso-skills-main | `C:\Vaults\references\Other Projects References\hig-doctor-main\hig-doctor-main\skills`; `aso-skills-main` | platform policy | Add freshness review before use | Low | Medium | later |
| L3 Game | Needs engine-specific refs | Claude-Code-Game-Studios-main | `C:\Vaults\references\Core Project References\Claude-Code-Game-Studios-main\docs\engine-reference` | engine/domain template | Mine target-specific gates only | Medium | Medium | avoid agent theater |
| L3 IoT | Needs defensive scope guard | iothackbot-master | `C:\Vaults\references\Other Projects References\iothackbot-master\iothackbot-master` | IoT/security workflow | Defensive-only reference pack | Low | High | dual-use gate |
| L3 Extension | Needs manifest/package refs | claude-plugins-official-main | `C:\Vaults\references\Core Project References\claude-plugins-official-main\.claude-plugin\marketplace.json` | plugin manifests | Use manifest shape only | Low | Medium | avoid `.npmrc` |
| L3 Library | Needs semver/package refs | OpenSpec-main, agent-os-main | listed above | schema/change contracts | Add package contract gates | Medium | Low | after core |
| L3 Data-Pipeline | Needs data quality refs | financial-services-main, csv-data-summarizer | paths above | schemas/data checks | Later domain pack | Low | Medium | not core |
| L3 AI-Agent | Needs eval/prompt refs | claude-cookbooks, G0DM0D3 | listed above | eval loops/model tests | Gate behind AI module | Medium-Later | High | privacy risk |
| Security Gateway | Needs finding schema and dual-use policy | claude-code-security-review, Anthropic-Cybersecurity-Skills | listed above | findings and coverage | Defensive-only review receipts | High | High | prompt-injection hardening |
| Engineering Gateway | Needs build/quality gates | get-shit-done, superpowers | listed above | quality gates and test discipline | Add check matrix | High | Medium | central |
| AI Gateway | Needs eval policy | claude-cookbooks, G0DM0D3, adversarial-spec | listed above | eval/human review/model racing | Build only after core verifier | Medium | High | avoid provider lock-in claims |
| Aesthetic Gateway | Needs design tokens | ui-ux-pro-max | listed above | design datasets | Use as reference pack | Medium | Medium | after UI tasks |
| Design Gateway | Needs IA/UX patterns | ui-ux-pro-max, mcp-server-guide | listed above | design-system workflow | Add UI/UX validation gates | Medium | Medium | cite freshness |
| Experience Gateway | Needs user research/testing refs | pm-skills, Product-Manager-Skills | listed above | research flow | Optional module hardening | Low | Medium | product-only |
| Memory | Backend decision conflict | mempalace, context-mode | listed above | drawers/FTS/search | Formalize storage backend and staleness states | Critical | High | exact first memory step |
| MemorySearch | Full-text/semantic strategy unclear | context-mode, mempalace | listed above | FTS5 and Chroma options | Start FTS/local, add semantic only with reason | Critical | High | avoid benchmark theater |
| Provenance | Needs cascade schema | OpenSpec-main, mempalace | listed above | change graph and evidence links | Link spec citations to source drawers | Critical | Medium | supports Migrate |
| EntityGraph | Too early | graphify-7, mempalace | listed above | graph extraction | Defer until query need proven | Later | High | gate hard |
| Dream | Risk of file-writing theater | mempalace, graphify-7 | listed above | consolidation/mining | Validate output changes behavior | Later | High | 10-run gate |
| MemoryMine | Requires corpus | graphify-7 | listed above | clustering/patterns | 50+ drawers first | Later | High | no early build |
| Forget | Needs deletion/provenance policy | mempalace, context-mode | listed above | controlled deletion | Write deletion record first | Medium | Medium | privacy useful |
| Homowabian | Thin module | caveman-main, humanizer-main | listed above | register/tone | Keep rule-level unless use grows | Low | Low | avoid bloat |
| Document | Needs docs generation refs | anthropic-skills, mattpocock | listed above | document skills/PRD docs | Generate from receipts/specs | Medium | Low | useful after core |
| Polish | Nice-to-have | mattpocock-skills, caveman | listed above | refinement discipline | Keep post-archive only | Low | Low | avoid semantic edits |
| ResearchLog | Session-level less useful than feature-level | spec-kit/OpenSpec, agent-os | listed above | feature research artifacts | Produce feature-scoped research | Medium | Medium | merge with ReferenceLoad if thin |
| Archive | Needs receipt index and audit | get-shit-done-main, pentest-ai-agents-main | listed above | state/finding DB | Append-only JSON index and changelog | Critical | Medium | central proof artifact |
| Package | Needs manifests | claude-plugins-official, hyperframes | listed above | manifest validation | Low priority until release flow | Low | Medium | no broad package copy |
| Deploy | Not core | existing CI/CD, GSD | `get-shit-done-main` | deploy receipts | Use existing tools; Wabble records | Low | Medium | avoid building CI/CD clone |
| Release | Needs tag/notes discipline | GSD, claude-plugins-official | listed above | release gates | Receipt-backed release note generation | Low | Medium | later |
| Scaffold | Needs idempotency/template refs | agent-os-main, OpenSpec-main | listed above | template installers | Refuse if project-map exists | Medium | Medium | avoid template sprawl |
| Monitor | Needs health diagnostics | codeflow-main, OMC doctor idea | listed above | health report/card | Build `/wabble-health` concept | Medium | Medium | early diagnostic helpful |
| Instinct | No corpus | graphify-7, GSD defect patterns | listed above | passive observation | Observer only after 100 receipts | Later | High | no promotion |
| Synth | No corpus | adversarial-spec-main | listed above | hypothesis generation | Later only | Later | High | no auto changes |
| Blueprint | No corpus | OpenSpec-main | listed above | change proposal | Later only | Later | High | require human attest |
| Factory | No corpus | skill-factory, SkillForge | `C:\Vaults\references\Other Projects References\SkillForge` | skill scaffolding | Later only | Later | High | no self-gen early |
| Augment | No corpus | SkillForge, OpenSpec-main | listed above | experimental patch | Later only | Later | High | experiments only |
| Benchmark | Risk of theater | mempalace eval warning, codeflow tests | listed above | outcome-linked evals | Require developer outcome field | Later | High | no recall-only metrics |
| Forge | Self-modification risk | OpenSpec-main, Wabble attest rules | listed above | promotion gate | Human attestation always | Later | High | only after benchmark |
| Feedback | No live feedback loop | G0DM0D3, PM skills | listed above | telemetry/feedback datasets | Later optional | Later | High | privacy review |
| Retro | No real corpus | GSD, superpowers | listed above | retrospective learning | Add after real releases | Later | Medium | manual first |

## 6. Integration Priority Ladder

## Critical

### Receipt Enforcement Backbone

- Why: WabbleSpec's strongest differentiator is false if receipts are not mechanically enforced.
- Module: Guard, Verifier, Archive, Executor.
- Reference: `get-shit-done-main`, Wabble hook, `destructive_command_guard-main`.
- Exact path to inspect: `C:\Vaults\references\Core Project References\get-shit-done-main\hooks`, `C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`, `C:\Vaults\references\Other Projects References\destructive_command_guard-main\destructive_command_guard-main\src`.
- Success: missing upstream receipt blocks downstream action; receipt schema validates; not-tested is explicit.
- Failure: receipts exist but do not prove checks ran.

### Formal Spec and Change Schema

- Why: Specify is the source of truth; changes must be machine-checkable.
- Module: Specify, ScopeFrame, Migrate, Provenance.
- Reference: `OpenSpec-main`.
- Exact path: `C:\Vaults\references\Core Project References\OpenSpec-main\schemas`, `C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`.
- Success: Wabble spec/change artifacts validate and carry change class.
- Failure: specs stay Markdown prose without enforceable fields.

### Project Map and Impact Context

- Why: manual integration requires exact context; Explore/ReferenceLoad need bounded evidence.
- Module: Explore, ReferenceLoad, Recipe.
- Reference: `cartographer-main`.
- Exact path: `C:\Vaults\references\Core Project References\cartographer-main\src\code-graph`.
- Success: Wabble can map project/reference context before planning and cite exact evidence.
- Failure: ReferenceLoad becomes raw repo browsing.

### Local Evidence Memory

- Why: staleness and provenance are real gaps in competitor tools.
- Module: Memory, MemorySearch, Provenance.
- Reference: `mempalace-develop`, `context-mode-main`.
- Exact path: `C:\Vaults\references\Core Project References\mempalace-develop\mempalace`, `C:\Vaults\references\Extra Project References\context-mode-main\src`.
- Success: FRESH/EXPIRED evidence controls reference use and search is usable.
- Failure: memory becomes a stale file pile or dependency contradiction.

### Command Safety Gate

- Why: broad autonomous execution needs safety policy before scale.
- Module: Guard, Executor, Rollback.
- Reference: `destructive_command_guard-main`, `claude-code-safety-net-main`.
- Exact path: `C:\Vaults\references\Other Projects References\destructive_command_guard-main\destructive_command_guard-main\src`, `C:\Vaults\references\Other Projects References\claude-code-safety-net-main\claude-code-safety-net-main\src`.
- Success: unsafe commands require explicit policy path.
- Failure: overblocking normal work or letting destructive operations pass.

## High

### Wabble Orchestration Adapter

- Why: WabbleSpec should use current Codex/OMX strengths without cloning them.
- Module: Autopilot, TeamPlan, ModelRouter, Ensemble, Economy.
- Reference: `oh-my-codex-main`.
- Exact path: `C:\Vaults\references\Core Project References\oh-my-codex-main\src`, `skills`, `prompts`, `templates`, `crates`.
- Success: thin adapter around orchestration state and subagent roles.
- Failure: WabbleSpec identity collapses into OMX clone.

### Security Review Finding Schema

- Why: security reviews need structured findings, not prose.
- Module: Reviewer, Security, Triage.
- Reference: `claude-code-security-review-main`.
- Exact path: `C:\Vaults\references\Core Project References\claude-code-security-review-main\claudecode`.
- Success: security findings become receipts with severity/evidence/fix.
- Failure: trusted-PR assumptions or prompt injection vulnerabilities leak into WabbleSpec.

### Worktree and TDD Discipline

- Why: rollback and verification benefit from git-native isolation and TDD.
- Module: Decompose, Executor, Rollback, Test.
- Reference: `superpowers-main`.
- Exact path: `C:\Vaults\references\Core Project References\superpowers-main\skills`.
- Success: high-risk waves use worktree target; test-first flow is available.
- Failure: every small task gets heavy process.

### Standards Discovery

- Why: WabbleSpec should discover project conventions before prescribing.
- Module: Product, ScopeFrame, Explore, Specify.
- Reference: `agent-os-main`.
- Exact path: `C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os`.
- Success: standards profile constrains specs with minimal examples.
- Failure: standards are advisory noise.

## Medium

### Health Dashboard

- Why: WabbleSpec needs a visible state/gate/receipt health report.
- Module: Monitor, Archive, Benchmark, Document.
- Reference: `codeflow-main`.
- Exact path: `C:\Vaults\references\Core Project References\codeflow-main\card`.
- Success: `/wabble-health` or equivalent reports broken gates and stale schemas.
- Failure: large UI copy or reporting theater.

### Platform Reference Packs

- Why: platform routing is valuable only if target-specific gates are real.
- Module: L3 Platform packages, L4 Gateways.
- Reference: `anthropic-skills-main`, `ui-ux-pro-max-skill-main`, `Claude-Code-Game-Studios-main`, `hig-doctor-main`.
- Exact path: their `skills`, `docs`, `engine-reference`, and design folders.
- Success: each target catches issues generic templates miss.
- Failure: broad skill catalog imported unfiltered.

### Document and Research Artifacts

- Why: docs and research should be generated from receipts/specs, not freeform summaries.
- Module: Document, ResearchLog, Polish.
- Reference: `mattpocock-skills-main`, `anthropic-skills-main`.
- Exact path: `C:\Vaults\references\Core Project References\mattpocock-skills-main\skills\engineering`, `C:\Vaults\references\Core Project References\anthropic-skills-main\skills`.
- Success: docs cite receipts and specs.
- Failure: expression layer becomes extra prose.

## Low

### Plugin and Domain Pack Manifests

- Why: useful later for packaged Wabble distributions.
- Module: Extension/Plugin, Package, Release, domain packs.
- Reference: `claude-plugins-official-main`, `financial-services-main`.
- Exact path: marketplace/manifests/plugin paths.
- Success: manifest schema informs Wabble packaging.
- Failure: copying marketplace content or reading sensitive config.

### Marketing/Growth Packs

- Why: optional domain packs, not core framework.
- Module: future domain-specific modules.
- Reference: `toprank-main`, `claude-ads-main`.
- Exact path: `C:\Vaults\references\Extra Project References\toprank-main`, `C:\Vaults\references\Extra Project References\claude-ads-main`.
- Success: domain pack only after platform/gateway contracts stabilize.
- Failure: external account assumptions enter core.

## Later / Experimental

### Graph Intelligence

- Why: entity graph and mining can add value after memory corpus exists.
- Module: EntityGraph, Dream, MemoryMine, Instinct, Synth.
- Reference: `graphify-7`, `mempalace-develop`.
- Exact path: `C:\Vaults\references\Core Project References\graphify-7\graphify`, `C:\Vaults\references\Core Project References\mempalace-develop\docs\schema.sql`.
- Success: graph queries beat full-text on real Wabble tasks.
- Failure: graph/mining files nobody uses.

### Adversarial Spec Debate

- Why: useful for high-risk ambiguous specs.
- Module: Reviewer, Propose, AI gateway.
- Reference: `adversarial-spec-main`.
- Exact path: `C:\Vaults\references\Other Projects References\adversarial-spec-main\adversarial-spec-main\skills\adversarial-spec\SKILL.md`.
- Success: adversarial pass catches real spec failure.
- Failure: provider theater and slow debate loops.

### Self-Improvement Runtime

- Why: core ambition, but requires data.
- Module: L8 Evolution.
- Reference: Wabble receipts plus future Graphify/OpenSpec patterns.
- Exact path: no current live `modules\l8`; future path must be created or explicitly deferred.
- Success: after 100+ receipts, Instinct surfaces validated non-spurious patterns.
- Failure: framework rewrites itself from weak evidence.

## Reject / Do Not Copy

- Duplicate references: `marketingskills-main (1)`, `claudian-main`, `superpowers-main` under Other.
- Generated eval workspaces: `claude-skills-main\eval-workspace` unless preserving evidence archive.
- Archive-only surfaces: `claude-skills-main\custom-gpt`.
- Empty template: `Other Projects References\template`.
- 49-agent / 73-command surfaces from game-studio style repos.
- `.npmrc`, private journals, live connector configs, generated package bundles without package-entry review.

## 7. Per-Module Upgrade Plans

## Module: Product

### Current Role
Captures product goals, users, and success metrics.
### Current Weakness
Thin context; not connected to discovered project standards.
### Best Reference Sources
`agent-os-main`, `pm-skills-main`, `Product-Manager-Skills-main`.
### Concepts To Borrow
Product plan, standards discovery, one-concept-per-standard.
### Concepts To Avoid
Market validation burden unless WabbleSpec becomes a product.
### Proposed Upgrade
Add a product-context schema and standards-profile link.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os`
### Manual Integration Steps
Define product-context fields; map to Specify non-goals and success criteria; validate against receipt.
### Validation Checklist
Product context exists; success metrics are measurable; non-goals feed ScopeFrame.
### Regression Risks
Product planning slows small tasks.
### Priority
High.

## Module: Recipe

### Current Role
Detects build target and initial routing.
### Current Weakness
Target detection needs stronger evidence and framework.yaml alignment.
### Best Reference Sources
`cartographer-main`, `get-shit-done-main`.
### Concepts To Borrow
Project indexing, phase routing, bounded context.
### Concepts To Avoid
Raw broad scans without receipts.
### Proposed Upgrade
Attach evidence source paths and confidence rationale to `recipe.json`.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\cartographer-main\src\code-graph`
### Manual Integration Steps
Add detection evidence array; validate target against platform package presence; log ambiguous targets.
### Validation Checklist
Target declared; evidence path exists; secondary targets recorded.
### Regression Risks
False target detection loads wrong platform.
### Priority
Critical.

## Module: ReferenceLoad

### Current Role
Loads external and internal references.
### Current Weakness
Can become unbounded raw browsing.
### Best Reference Sources
`cartographer-main`, `context-mode-main`.
### Concepts To Borrow
Bounded briefs, searchable store, exact source slices.
### Concepts To Avoid
Dumping full repos into context.
### Proposed Upgrade
Require reference-card summary plus exact path citations before any raw file inspection.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\cartographer-main\docs\features`
### Manual Integration Steps
Create reference-load policy; store loaded references as FRESH drawers; cite map source.
### Validation Checklist
Each loaded reference has path, trust, staleness, purpose.
### Regression Risks
Important raw details missed by map-only approach.
### Priority
Critical.

## Module: RuntimeProbe

### Current Role
Detects runtime capabilities.
### Current Weakness
Vendor-neutral claims not fully earned.
### Best Reference Sources
`oh-my-codex-main`, `caveman-main`, `Open-LLM-VTuber-main`.
### Concepts To Borrow
Runtime capability reporting, compact output policy, provider abstraction later.
### Concepts To Avoid
Claiming neutrality before adapters.
### Proposed Upgrade
Record current runtime and missing adapter gaps explicitly.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\oh-my-codex-main\src`
### Manual Integration Steps
Add current-host field and adapter capability matrix.
### Validation Checklist
Runtime receipt names tools available and fallback.
### Regression Risks
Extra routing abstraction slows execution.
### Priority
High.

## Module: ScopeFrame

### Current Role
Defines boundaries, non-goals, authority.
### Current Weakness
Layer/path conflicts and framework/product boundary risks.
### Best Reference Sources
`OpenSpec-main`, `agent-os-main`.
### Concepts To Borrow
Schema-backed scope/change boundaries.
### Concepts To Avoid
Fluid scope without gate.
### Proposed Upgrade
Add scope schema and authority conflict check.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\schemas`
### Manual Integration Steps
Define scope schema; validate no module writes outside authority.
### Validation Checklist
Scope has goals, non-goals, owned outputs, forbidden outputs.
### Regression Risks
Too strict for exploratory work.
### Priority
Critical.

## Module: Specify

### Current Role
Creates task/spec artifacts.
### Current Weakness
EARS vs GWT and template count need validation.
### Best Reference Sources
`OpenSpec-main`, `agent-os-main`.
### Concepts To Borrow
Spec/change schema, proposal lifecycle, standards injection.
### Concepts To Avoid
Advice-only specs.
### Proposed Upgrade
Add formal spec schema; compare EARS and GWT before hard enforcement.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\specs`
### Manual Integration Steps
Schema fields; migration/change class; not-tested hooks.
### Validation Checklist
Spec validates; no open questions; citations exist.
### Regression Risks
Template bloat.
### Priority
Critical.

## Module: Explore

### Current Role
Maps project/reference state.
### Current Weakness
Needs deterministic project-map contract.
### Best Reference Sources
`cartographer-main`, `graphify-7`.
### Concepts To Borrow
Code graph, impact briefs, path queries.
### Concepts To Avoid
Generated reports as permanent truth.
### Proposed Upgrade
Create Wabble project-map schema and freshness policy.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\cartographer-main\src\code-graph`
### Manual Integration Steps
Define map sections; write freshness metadata; add impact query.
### Validation Checklist
Map names entry points, modules, tests, risky files.
### Regression Risks
Map goes stale.
### Priority
Critical.

## Module: Interview

### Current Role
Resolves ambiguity.
### Current Weakness
May under-trigger or over-question.
### Best Reference Sources
`adversarial-spec-main`, `agent-creator`.
### Concepts To Borrow
Interview/debate boundary and hard-stop prompts.
### Concepts To Avoid
Multi-provider debate as default.
### Proposed Upgrade
Use 9-dimension ambiguity scoring; trigger adversarial only above threshold.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\adversarial-spec-main\adversarial-spec-main\skills\adversarial-spec\SKILL.md`
### Manual Integration Steps
Add ambiguity evidence fields; connect unanswered items to ScopeFrame.
### Validation Checklist
No more than 3 questions per batch; open questions resolved or marked.
### Regression Risks
Slows obvious tasks.
### Priority
Medium.

## Module: Propose

### Current Role
Generates options and tradeoffs.
### Current Weakness
Tradeoffs can be vague.
### Best Reference Sources
`agent-os-main`, `adversarial-spec-main`.
### Concepts To Borrow
Option shaping and consensus challenge.
### Concepts To Avoid
Decision theater.
### Proposed Upgrade
Require 2-4 options, dimensions, recommendation rationale, rejected alternatives.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os`
### Manual Integration Steps
Add option schema and decision receipt.
### Validation Checklist
Each option has risk, reversibility, evidence.
### Regression Risks
Too much planning for low-risk tasks.
### Priority
Medium.

## Module: Decompose

### Current Role
Creates wave plan.
### Current Weakness
Needs stronger rollback and verification links.
### Best Reference Sources
`get-shit-done-main`, `superpowers-main`.
### Concepts To Borrow
Phase breakdown and worktree isolation.
### Concepts To Avoid
Huge workflow sprawl.
### Proposed Upgrade
Wave plan includes rollback target, verification mode, acceptance evidence.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`
### Manual Integration Steps
Add rollback target enum; link tests; cite spec requirements.
### Validation Checklist
Every wave has owner, output, check, rollback.
### Regression Risks
Overhead on tiny tasks.
### Priority
High.

## Module: Apply

### Current Role
Applies specs to product artifacts.
### Current Weakness
Authority and delta classification are high-risk.
### Best Reference Sources
`OpenSpec-main`, `get-shit-done-main`.
### Concepts To Borrow
Change proposals and hook-state checks.
### Concepts To Avoid
Undeclared source edits.
### Proposed Upgrade
Require delta class and spec patch receipt for mid-execution changes.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`
### Manual Integration Steps
Classify change; update spec if needed; block breaking deltas without migration.
### Validation Checklist
No write outside declared scope; change class recorded.
### Regression Risks
False breaking classification.
### Priority
High.

## Module: Test

### Current Role
Maps acceptance criteria to tests.
### Current Weakness
Needs stronger TDD/test-first guidance.
### Best Reference Sources
`superpowers-main`, `mattpocock-skills-main`.
### Concepts To Borrow
TDD, verification-before-completion.
### Concepts To Avoid
Testing as prose only.
### Proposed Upgrade
Every requirement maps to executable test or explicit not-tested entry.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\superpowers-main\skills`
### Manual Integration Steps
Add requirement-test trace table.
### Validation Checklist
All EARS/GWT criteria mapped.
### Regression Risks
Test stubs without execution.
### Priority
High.

## Module: Clean

### Current Role
Behavior-preserving cleanup.
### Current Weakness
Needs regression lock before refactor.
### Best Reference Sources
`superpowers-main`, `andrej-karpathy-skills-main`.
### Concepts To Borrow
Small diffs, no overengineering, behavior lock.
### Concepts To Avoid
Cleanup as broad rewrite.
### Proposed Upgrade
Require cleanup plan and existing/new regression evidence.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\andrej-karpathy-skills-main\skills\karpathy-guidelines\SKILL.md`
### Manual Integration Steps
Write cleanup receipt fields for before/after behavior.
### Validation Checklist
Tests/lint pass or not-tested recorded.
### Regression Risks
Accidental semantic change.
### Priority
Medium.

## Module: Triage

### Current Role
Classifies incoming issues/errors.
### Current Weakness
Current taxonomy is too abstract.
### Best Reference Sources
`get-shit-done-main`, `claude-code-security-review-main`.
### Concepts To Borrow
Named defect patterns and security finding fields.
### Concepts To Avoid
Severity without fix path.
### Proposed Upgrade
Add symptom, detection, fix-forward, test anchor.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\get-shit-done`
### Manual Integration Steps
Extend triage record schema.
### Validation Checklist
Every triage item routes to owner and validation.
### Regression Risks
Taxonomy sprawl.
### Priority
High.

## Module: Migrate

### Current Role
Handles breaking changes.
### Current Weakness
Needs formal downstream invalidation.
### Best Reference Sources
`OpenSpec-main`, `mempalace-develop`.
### Concepts To Borrow
Change lifecycle and graph-like dependency tracking.
### Concepts To Avoid
Silent migration.
### Proposed Upgrade
BREAKING changes trigger Provenance cascade and consumer guide.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`
### Manual Integration Steps
Link migration plan to affected specs/drawers.
### Validation Checklist
Affected consumers listed; rollback path declared.
### Regression Risks
Over-classifying changes.
### Priority
Critical.

## Module: Autopilot

### Current Role
Lifecycle orchestration.
### Current Weakness
Can become opaque and over-powerful.
### Best Reference Sources
`oh-my-codex-main`, `get-shit-done-main`.
### Concepts To Borrow
State, phase transitions, role routing.
### Concepts To Avoid
Hidden mode state.
### Proposed Upgrade
Expose state through health report and receipts.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\oh-my-codex-main\src`
### Manual Integration Steps
Map Autopilot transitions to receipt preconditions.
### Validation Checklist
Current phase visible; next valid actions listed.
### Regression Risks
Autonomy bypasses gates.
### Priority
Critical.

## Module: Economy

### Current Role
Token/context discipline.
### Current Weakness
Thin, mostly behavioral.
### Best Reference Sources
`caveman-main`, `context-mode-main`.
### Concepts To Borrow
Compression policy, sandboxing verbose outputs.
### Concepts To Avoid
Unreadably compressed technical proof.
### Proposed Upgrade
Add measurable context budget and verbose-output capture policy.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\caveman-main\src`
### Manual Integration Steps
Define token-density receipt fields.
### Validation Checklist
Large outputs captured not pasted; exact errors preserved when needed.
### Regression Risks
Over-compression hides risk.
### Priority
High.

## Module: Ensemble

### Current Role
Multi-lane coordination.
### Current Weakness
Unvalidated until ModelRouter works.
### Best Reference Sources
`oh-my-codex-main`, `adversarial-spec-main`.
### Concepts To Borrow
Bounded parallel roles, consensus only when useful.
### Concepts To Avoid
Parallelism theater.
### Proposed Upgrade
Keep gated to high-risk independent tasks.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\oh-my-codex-main\prompts`
### Manual Integration Steps
Define trigger thresholds and result merge receipt.
### Validation Checklist
Independent lanes; no duplicate work; merge rationale.
### Regression Risks
Cost and complexity.
### Priority
Later.

## Module: Executor

### Current Role
Executes waves.
### Current Weakness
Needs stronger safety and receipt evidence.
### Best Reference Sources
`get-shit-done-main`, `destructive_command_guard-main`.
### Concepts To Borrow
Execute-phase and command guard.
### Concepts To Avoid
Unsafe autonomous shell.
### Proposed Upgrade
Before each wave, require plan receipt; after each wave, require verification evidence.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`
### Manual Integration Steps
Add pre-wave and post-wave hook checks.
### Validation Checklist
No wave without plan; no done without verification.
### Regression Risks
False block.
### Priority
Critical.

## Module: Guard

### Current Role
Invariant and authority enforcement.
### Current Weakness
Needs command policy and schema drift checks.
### Best Reference Sources
`destructive_command_guard-main`, `claude-code-safety-net-main`.
### Concepts To Borrow
Block/warn/allow semantics.
### Concepts To Avoid
One-size command blocking.
### Proposed Upgrade
Add policy table: receipt gate, path gate, command risk gate.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\destructive_command_guard-main\destructive_command_guard-main\src`
### Manual Integration Steps
Define command classes and Wabble-specific allowed exceptions.
### Validation Checklist
Risky commands classified; error message actionable.
### Regression Risks
Developer frustration from overblocking.
### Priority
Critical.

## Module: ModelRouter

### Current Role
Routes by capability descriptor.
### Current Weakness
Vendor-neutral claim ahead of proof.
### Best Reference Sources
`oh-my-codex-main`, `caveman-main`.
### Concepts To Borrow
Role and capability routing.
### Concepts To Avoid
Hardcoded stale model names.
### Proposed Upgrade
Route current available lanes; record missing lanes.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\oh-my-codex-main\src`
### Manual Integration Steps
Add adapter matrix with current host.
### Validation Checklist
Route reason logged; fallback declared.
### Regression Risks
Lowest-common-denominator routing.
### Priority
High.

## Module: Reviewer

### Current Role
Adversarial review and grading.
### Current Weakness
Needs structured finding output and role hard stops.
### Best Reference Sources
`claude-code-security-review-main`, `agent-creator`.
### Concepts To Borrow
Finding parser, hard-stop prompt, quality gates.
### Concepts To Avoid
Reviewer editing files.
### Proposed Upgrade
Reviewer returns severity, evidence, impact, fix recommendation, not code edits.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\claude-code-security-review-main\claudecode`
### Manual Integration Steps
Add reviewer finding schema.
### Validation Checklist
Findings are actionable and cited.
### Regression Risks
False positives.
### Priority
High.

## Module: Rollback

### Current Role
Restores checkpoints.
### Current Weakness
Checkpoint may be weaker than git isolation.
### Best Reference Sources
`superpowers-main`.
### Concepts To Borrow
Git worktree per high-risk task.
### Concepts To Avoid
Worktree overhead for simple tasks.
### Proposed Upgrade
Support `wave-checkpoint`, `worktree`, and `deploy-snapshot`.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\superpowers-main\skills`
### Manual Integration Steps
Add rollback target selection rules.
### Validation Checklist
Rollback path declared before execution.
### Regression Risks
Worktree drift.
### Priority
High.

## Module: TeamPlan

### Current Role
Multi-agent coordination.
### Current Weakness
Could become agent-count theater.
### Best Reference Sources
`oh-my-codex-main`, `awesome-claude-agents-main`.
### Concepts To Borrow
Bounded roles and handoffs.
### Concepts To Avoid
49-agent catalog.
### Proposed Upgrade
Keep only for high-complexity independent work.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\oh-my-codex-main\prompts`
### Manual Integration Steps
Define max agents, ownership, stop criteria.
### Validation Checklist
No duplicate tasks; outputs merge cleanly.
### Regression Risks
Subagent overhead.
### Priority
Later.

## Module: Verifier

### Current Role
Runs declared checks.
### Current Weakness
Must prove checks ran, not just say they did.
### Best Reference Sources
`get-shit-done-main`, `toprank-main`.
### Concepts To Borrow
Verify-work separation and fixture-backed evals.
### Concepts To Avoid
LLM-only PASS.
### Proposed Upgrade
Receipt includes command/check evidence, outputs, not-tested, confidence.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`
### Manual Integration Steps
Bind verification receipt to actual check output.
### Validation Checklist
PASS only when checks pass; PARTIAL/FAIL honest.
### Regression Risks
Check output too verbose.
### Priority
Critical.

## Module: L3 Platforms

### Current Role
Target-specific specs and gates.
### Current Weakness
Needs reference-backed depth per platform.
### Best Reference Sources
`anthropic-skills-main`, `ui-ux-pro-max-skill-main`, `Claude-Code-Game-Studios-main`, `hig-doctor-main`, `iothackbot-master`.
### Concepts To Borrow
Domain-specific gates, skill packaging, path-scoped rules.
### Concepts To Avoid
Shallow checklists for all targets at once.
### Proposed Upgrade
Integrate platform refs in order: CLI/API/Web first, then Library/Extension, then Mobile/Game/IoT/Data/AI.
### Files/Folders To Inspect
Reference-specific `skills`, `docs`, `engineering`, `security`, `verification`.
### Manual Integration Steps
For each target, add 3 checks generic Specify misses.
### Validation Checklist
Target output differs meaningfully from generic template.
### Regression Risks
Template staleness.
### Priority
Medium to High by target.

## Module: L4 Gateways

### Current Role
Cross-cutting capability policies.
### Current Weakness
Need evidence-backed rules and freshness policy.
### Best Reference Sources
Security: `claude-code-security-review-main`, `Anthropic-Cybersecurity-Skills-main`; Design: `ui-ux-pro-max-skill-main`; AI: `claude-cookbooks-main`, `G0DM0D3-main`.
### Concepts To Borrow
Finding schemas, design audit gates, eval policies.
### Concepts To Avoid
Domain content copied into core.
### Proposed Upgrade
Add gateway-specific receipt and freshness metadata.
### Files/Folders To Inspect
Listed reference roots.
### Manual Integration Steps
One gateway at a time; validate against a task generic platform misses.
### Validation Checklist
Gateway catches at least one issue not caught at L3.
### Regression Risks
Gate sprawl.
### Priority
High for Security/Engineering/AI; Medium for Aesthetic/Design/Experience.

## Module: Memory

### Current Role
Evidence storage.
### Current Weakness
Backend direction conflict and staleness complexity.
### Best Reference Sources
`mempalace-develop`, `context-mode-main`.
### Concepts To Borrow
Drawer structure, local FTS, session continuity.
### Concepts To Avoid
Benchmark claims unrelated to developer outcomes.
### Proposed Upgrade
Write a backend decision: MemPalace/Chroma vs SQLite/FTS vs flat JSON.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\mempalace-develop\mempalace`, `C:\Vaults\references\Extra Project References\context-mode-main\src\store.ts`
### Manual Integration Steps
Define storage API, staleness fields, migration path.
### Validation Checklist
10 drawers can be queried and stale evidence blocked.
### Regression Risks
Dependency lock-in.
### Priority
Critical.

## Module: MemorySearch

### Current Role
Evidence retrieval.
### Current Weakness
Search strategy unsettled.
### Best Reference Sources
`context-mode-main`, `mempalace-develop`.
### Concepts To Borrow
SQLite/FTS5 and semantic search tradeoffs.
### Concepts To Avoid
Embeddings without proven need.
### Proposed Upgrade
Start with FTS/local search, allow semantic backend only by decision record.
### Files/Folders To Inspect
`C:\Vaults\references\Extra Project References\context-mode-main\src`
### Manual Integration Steps
Define query fields and staleness filter.
### Validation Checklist
Search excludes EXPIRED by default.
### Regression Risks
False missing evidence.
### Priority
Critical.

## Module: Provenance

### Current Role
Evidence lineage and cascade.
### Current Weakness
Needs hard schema and cascade rules.
### Best Reference Sources
`OpenSpec-main`, `mempalace-develop`.
### Concepts To Borrow
Change graph and source citations.
### Concepts To Avoid
LLM-maintained ledger without parser.
### Proposed Upgrade
Machine-readable provenance records; markdown mirror optional.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\schemas`
### Manual Integration Steps
Add cited_by, source_hash, change_class.
### Validation Checklist
BREAKING source marks dependents NEEDS_REVERIFICATION.
### Regression Risks
Cascade noise.
### Priority
Critical.

## Module: EntityGraph

### Current Role
Relationship index.
### Current Weakness
Premature before search corpus proves need.
### Best Reference Sources
`graphify-7`, `mempalace-develop`.
### Concepts To Borrow
Graph extraction and path query.
### Concepts To Avoid
Seven entity types before real queries.
### Proposed Upgrade
Start with file/module/concept only after query failures.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\graphify-7\graphify`
### Manual Integration Steps
Collect failed search cases; define graph MVP.
### Validation Checklist
Graph beats full-text on recorded cases.
### Regression Risks
Noisy graph.
### Priority
Later.

## Module: Dream

### Current Role
Memory consolidation/staleness outputs.
### Current Weakness
Risk of theater outputs.
### Best Reference Sources
`mempalace-develop`, `graphify-7`.
### Concepts To Borrow
Mining, clustering, repair.
### Concepts To Avoid
Background-daemon claims.
### Proposed Upgrade
Run only when invoked; measure whether findings change behavior.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\mempalace-develop\mempalace`
### Manual Integration Steps
Add behavior-change log per Dream run.
### Validation Checklist
After 10 runs, at least one finding led to update; otherwise redesign.
### Regression Risks
File churn.
### Priority
Later.

## Module: MemoryMine

### Current Role
Pattern mining.
### Current Weakness
Needs 50+ drawers and real corpus.
### Best Reference Sources
`graphify-7`.
### Concepts To Borrow
Clustering and pattern extraction.
### Concepts To Avoid
Mining an empty corpus.
### Proposed Upgrade
Hard gate on drawer count and query failures.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\graphify-7\graphify`
### Manual Integration Steps
Define corpus threshold and output consumption path.
### Validation Checklist
Mined pattern changes a module or rule.
### Regression Risks
Spurious patterns.
### Priority
Later.

## Module: Forget

### Current Role
Controlled evidence deletion.
### Current Weakness
Needs deletion proof and privacy policy.
### Best Reference Sources
`mempalace-develop`, `context-mode-main`.
### Concepts To Borrow
Local storage operations and repair.
### Concepts To Avoid
Silent deletion.
### Proposed Upgrade
Deletion record first, remove drawer second, update indexes third.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\mempalace-develop\mempalace`
### Manual Integration Steps
Add deletion schema.
### Validation Checklist
Deleted evidence has provenance record.
### Regression Risks
Accidental evidence loss.
### Priority
Medium.

## Module: Homowabian

### Current Role
Voice/register.
### Current Weakness
Thin module.
### Best Reference Sources
`caveman-main`, `humanizer-main`.
### Concepts To Borrow
Compact register and style rules.
### Concepts To Avoid
Voice theory as framework overhead.
### Proposed Upgrade
Keep as rules unless repeated use proves module value.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\caveman-main\skills`
### Manual Integration Steps
Define register policy only.
### Validation Checklist
No technical detail lost.
### Regression Risks
Style over precision.
### Priority
Low.

## Module: Document

### Current Role
Generates docs.
### Current Weakness
Docs can become summaries detached from proof.
### Best Reference Sources
`anthropic-skills-main`, `mattpocock-skills-main`.
### Concepts To Borrow
Document skill workflows and PRD docs.
### Concepts To Avoid
Generated docs without source citations.
### Proposed Upgrade
Docs must cite specs/receipts/memory drawers.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\anthropic-skills-main\skills`
### Manual Integration Steps
Add doc source-citation checklist.
### Validation Checklist
Every claim traces to source artifact.
### Regression Risks
Documentation bloat.
### Priority
Medium.

## Module: Polish

### Current Role
Non-semantic refinement.
### Current Weakness
Can accidentally change meaning.
### Best Reference Sources
`mattpocock-skills-main`, `caveman-main`.
### Concepts To Borrow
Diff-based refinement and compact prose.
### Concepts To Avoid
Semantic rewrites.
### Proposed Upgrade
Post-archive only, with diff and semantic-change check.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\mattpocock-skills-main\skills\engineering`
### Manual Integration Steps
Require before/after diff.
### Validation Checklist
No requirement changes.
### Regression Risks
Meaning drift.
### Priority
Low.

## Module: ResearchLog

### Current Role
Captures research.
### Current Weakness
Session-level logs less useful than feature-level evidence.
### Best Reference Sources
`OpenSpec-main`, `agent-os-main`.
### Concepts To Borrow
Feature research artifacts and standards discovery.
### Concepts To Avoid
Loose note piles.
### Proposed Upgrade
Feature-scoped research with drawer citations.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\specs`
### Manual Integration Steps
Link research notes to Memory/Provenance.
### Validation Checklist
Research has source, trust, staleness.
### Regression Risks
Duplicating ReferenceLoad.
### Priority
Medium.

## Module: Archive

### Current Role
Stores receipt/audit trail.
### Current Weakness
Needs index/query and proof chain.
### Best Reference Sources
`get-shit-done-main`, `pentest-ai-agents-main`.
### Concepts To Borrow
State continuity and findings DB status transitions.
### Concepts To Avoid
Markdown-only ledger.
### Proposed Upgrade
JSON index plus markdown changelog.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\get-shit-done`
### Manual Integration Steps
Index every receipt by module, phase, status, evidence, not-tested.
### Validation Checklist
Archive can answer what was verified and what was not.
### Regression Risks
Index drift.
### Priority
Critical.

## Module: Package

### Current Role
Signs/versions artifacts.
### Current Weakness
Not core until real release flow.
### Best Reference Sources
`claude-plugins-official-main`, `hyperframes-main`.
### Concepts To Borrow
Manifest validation.
### Concepts To Avoid
Package-specific generated bundles copied into core.
### Proposed Upgrade
Keep package module but gate by platform.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\claude-plugins-official-main\.claude-plugin`
### Manual Integration Steps
Define manifest per target.
### Validation Checklist
Artifact hash and signature present.
### Regression Risks
Packaging without build proof.
### Priority
Low.

## Module: Deploy

### Current Role
Deploys artifacts.
### Current Weakness
Can duplicate CI/CD.
### Best Reference Sources
`get-shit-done-main`.
### Concepts To Borrow
Deploy receipts and guarded phases.
### Concepts To Avoid
Building deployment platform.
### Proposed Upgrade
Wabble records and gates deployments; existing tools perform deploy.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`
### Manual Integration Steps
Require rollback plan and prior env receipt.
### Validation Checklist
Deploy receipt references external output.
### Regression Risks
Irreversible side effects.
### Priority
Low.

## Module: Release

### Current Role
Tags/publishes release notes.
### Current Weakness
Needs archive-driven notes.
### Best Reference Sources
`get-shit-done-main`, `claude-plugins-official-main`.
### Concepts To Borrow
Release gates and manifest versioning.
### Concepts To Avoid
Manual release claims.
### Proposed Upgrade
Generate release notes from Archive.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\claude-plugins-official-main\.claude-plugin\marketplace.json`
### Manual Integration Steps
Tag only after Package + Archive pass.
### Validation Checklist
Release note cites receipts.
### Regression Risks
Publishing wrong artifact.
### Priority
Low.

## Module: Scaffold

### Current Role
Generates project structure.
### Current Weakness
Template/idempotency needs checks.
### Best Reference Sources
`agent-os-main`, `OpenSpec-main`.
### Concepts To Borrow
Installer/template conventions.
### Concepts To Avoid
Overwriting existing projects.
### Proposed Upgrade
Refuse if project-map exists unless migration mode.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\agent-os-main\scripts`
### Manual Integration Steps
Add idempotency and post-scaffold Explore.
### Validation Checklist
Second run is no-op or guided migration.
### Regression Risks
Scaffold overwrites user files.
### Priority
Medium.

## Module: Monitor

### Current Role
Observability config.
### Current Weakness
Needs health/reporting role clarity.
### Best Reference Sources
`codeflow-main`, OMC doctor concept from `oh-my-codex-main`/`oh-my-claudecode-main`.
### Concepts To Borrow
Health card and diagnostics.
### Concepts To Avoid
Full observability platform.
### Proposed Upgrade
Add Wabble health diagnostic before observability generation.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\codeflow-main\card`
### Manual Integration Steps
Report broken receipts, stale memory, schema drift.
### Validation Checklist
Health report catches known stale `framework.yaml` conflicts.
### Regression Risks
Dashboard theater.
### Priority
Medium.

## Module: L8 Evolution

### Current Role
Future self-improvement pipeline.
### Current Weakness
No live module folders and no receipt corpus.
### Best Reference Sources
`graphify-7`, `OpenSpec-main`, `SkillForge`, future Wabble receipts.
### Concepts To Borrow
Graph/query, change proposal, skill scaffolding.
### Concepts To Avoid
Self-modifying framework from weak data.
### Proposed Upgrade
Keep as roadmap. Build only Instinct observer after 100+ receipts.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\graphify-7\graphify`, `C:\Vaults\references\Other Projects References\SkillForge`
### Manual Integration Steps
Create L8 folders only after gate; start read-only.
### Validation Checklist
100+ receipts; 3 human-validated patterns; no self-promotion.
### Regression Risks
Recursive prompt/policy drift.
### Priority
Later/Experimental.

## Module: Web Platform

### Current Role
Browser app platform package.
### Current Weakness
Needs browser/UI/accessibility validation beyond generic specs.
### Best Reference Sources
`ui-ux-pro-max-skill-main`, `superpowers-chrome-main`, `anthropic-skills-main`.
### Concepts To Borrow
Visual audit gates, browser verification, web skill packaging.
### Concepts To Avoid
Bulk design dataset import.
### Proposed Upgrade
Add browser-render, responsive, accessibility, asset, and performance gates.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\ui-ux-pro-max-skill-main\src\ui-ux-pro-max`, `C:\Vaults\references\Other Projects References\superpowers-chrome-main\superpowers-chrome-main\mcp\src`
### Manual Integration Steps
Review Web platform gates; add exact reference-backed checks; validate on a web task.
### Validation Checklist
Web pack catches at least 3 issues generic Specify misses.
### Regression Risks
Stale frontend framework assumptions.
### Priority
Medium.

## Module: API-Service Platform

### Current Role
Backend/API/service platform package.
### Current Weakness
Needs stronger contract, auth, rate-limit, and schema gates.
### Best Reference Sources
`OpenSpec-main`, `claude-cookbooks-main`.
### Concepts To Borrow
Schema validation and API/agent examples.
### Concepts To Avoid
External service setup as core requirement.
### Proposed Upgrade
Add endpoint contract, auth, error, observability, and integration-test gates.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\schemas`, `C:\Vaults\references\Other Projects References\claude-cookbooks-main\claude-cookbooks-main\claude_agent_sdk`
### Manual Integration Steps
Map service requirements to contract tests and security checks.
### Validation Checklist
API-Service catches an auth or contract issue generic template misses.
### Regression Risks
Overfitting to one web/API stack.
### Priority
Medium.

## Module: CLI Platform

### Current Role
Command-line platform package.
### Current Weakness
Needs mature command UX and verification gates.
### Best Reference Sources
`get-shit-done-main`, `agent-os-main`.
### Concepts To Borrow
Command lifecycle, standards extraction, explicit verification.
### Concepts To Avoid
Unix-only shell assumptions.
### Proposed Upgrade
Strengthen exit-code, stdout/stderr, help, config, startup, and JSON-mode gates.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`, `C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os`
### Manual Integration Steps
Compare current CLI gates to references; add missing command-behavior checks.
### Validation Checklist
CLI pack still catches the 7 issues recorded in `BUILD-PLAN.md`.
### Regression Risks
Windows/PowerShell mismatch.
### Priority
High.

## Module: Game Platform

### Current Role
Game development platform package.
### Current Weakness
Needs engine-specific gates without agent theater.
### Best Reference Sources
`Claude-Code-Game-Studios-main`.
### Concepts To Borrow
Engine references, domain template layout, path-scoped rules.
### Concepts To Avoid
49-agent studio hierarchy and 73-command surface.
### Proposed Upgrade
Add engine, asset, frame budget, input, save-state, and build gates.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\Claude-Code-Game-Studios-main\docs\engine-reference`, `C:\Vaults\references\Core Project References\Claude-Code-Game-Studios-main\design\registry`
### Manual Integration Steps
Extract engine-neutral checks; keep engine-specific references loaded only by target.
### Validation Checklist
Game pack catches frame/asset/engine issue generic template misses.
### Regression Risks
Domain references become stale or too engine-specific.
### Priority
Medium.

## Module: Mobile Platform

### Current Role
iOS/Android/cross-platform mobile package.
### Current Weakness
Needs platform policy, store, permission, and device gates.
### Best Reference Sources
`hig-doctor-main`, `aso-skills-main`, `Open-LLM-VTuber-main` for device-permission patterns only.
### Concepts To Borrow
HIG/app-store checks, ASO/store submission concerns, device permission warnings.
### Concepts To Avoid
Stale platform guideline claims.
### Proposed Upgrade
Add freshness date to mobile platform references and permission gates.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\hig-doctor-main\hig-doctor-main\skills`, `C:\Vaults\references\Other Projects References\aso-skills-main\aso-skills-main\skills`
### Manual Integration Steps
Inspect guideline refs; add exact source freshness notes.
### Validation Checklist
Mobile pack names permissions, signing, store, accessibility, and offline checks.
### Regression Risks
Platform rules change frequently.
### Priority
Low/Medium.

## Module: Desktop Platform

### Current Role
Desktop app platform package.
### Current Weakness
Needs IPC, updater, signing, packaging, and OS integration depth.
### Best Reference Sources
`OpenSpec-main`, `anthropic-skills-main`, `claude-plugins-official-main` for manifest/package patterns.
### Concepts To Borrow
Manifest validation and package safety.
### Concepts To Avoid
Assuming Electron/Tauri/native are interchangeable.
### Proposed Upgrade
Split desktop gates by runtime family where needed.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\claude-plugins-official-main\plugins`
### Manual Integration Steps
Add runtime-family field and signing/updater checks.
### Validation Checklist
Desktop pack declares runtime, updater, IPC, permissions, signing.
### Regression Risks
Generic checks hide runtime-specific risk.
### Priority
Low/Medium.

## Module: IoT Platform

### Current Role
Firmware/hardware-coupled software package.
### Current Weakness
Needs safety, firmware, OTA, resource-budget, and dual-use caution.
### Best Reference Sources
`iothackbot-master`, `destructive_command_guard-main`.
### Concepts To Borrow
Device safety, firmware security, command guard mindset.
### Concepts To Avoid
Offensive dual-use operations in core.
### Proposed Upgrade
Defensive-only IoT gates with explicit scope and hardware assumptions.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\iothackbot-master\iothackbot-master\skills`, `C:\Vaults\references\Other Projects References\iothackbot-master\iothackbot-master\config`
### Manual Integration Steps
Extract safe, defensive validation patterns only.
### Validation Checklist
IoT pack names flash/RAM, OTA signing, hardware assumptions, safety stop.
### Regression Risks
Dual-use content leakage.
### Priority
Low.

## Module: Library Platform

### Current Role
Reusable library/package platform package.
### Current Weakness
Needs public API, semver, registry, compatibility, and docs gates.
### Best Reference Sources
`OpenSpec-main`, `agent-os-main`, `claude-plugins-official-main`.
### Concepts To Borrow
Schema/change lifecycle and manifest validation.
### Concepts To Avoid
Publishing assumptions without package target.
### Proposed Upgrade
Add API surface contract and breaking-change migration checks.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`
### Manual Integration Steps
Tie Library to Migrate and Release.
### Validation Checklist
Public API diff and semver impact recorded.
### Regression Risks
False semver classification.
### Priority
Medium.

## Module: Extension Platform

### Current Role
Browser/IDE/host plugin package.
### Current Weakness
Needs manifest, host-boundary, permission, and packaging checks.
### Best Reference Sources
`claude-plugins-official-main`, `claude-code-safety-net-main`.
### Concepts To Borrow
Plugin manifests and hook packaging.
### Concepts To Avoid
Reading or copying `.npmrc`/private configs.
### Proposed Upgrade
Add manifest schema, permissions review, host sandbox checks.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\claude-plugins-official-main\.claude-plugin\marketplace.json`, `C:\Vaults\references\Core Project References\claude-plugins-official-main\plugins`
### Manual Integration Steps
Define extension manifest fields and forbidden permission patterns.
### Validation Checklist
Manifest validates and permissions have rationale.
### Regression Risks
Host-specific manifest drift.
### Priority
Medium/Low.

## Module: Data-Pipeline Platform

### Current Role
ETL/batch/streaming/schema evolution platform package.
### Current Weakness
Needs data quality and migration gates.
### Best Reference Sources
`financial-services-main`, `csv-data-summarizer-claude-skill-main`.
### Concepts To Borrow
Data schemas, data analysis scripts, quality scoring.
### Concepts To Avoid
Vertical finance assumptions in core.
### Proposed Upgrade
Add data contract, schema evolution, lineage, quality thresholds.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\financial-services-main\plugins`, `C:\Vaults\references\Other Projects References\csv-data-summarizer-claude-skill-main\csv-data-summarizer-claude-skill-main`
### Manual Integration Steps
Define pipeline receipt fields for data quality and lineage.
### Validation Checklist
Pipeline pack names source, transform, schema, quality, rollback.
### Regression Risks
External data/source assumptions.
### Priority
Low/Medium.

## Module: AI-Agent Platform

### Current Role
LLM app and agentic workflow platform package.
### Current Weakness
Needs eval, prompt, safety, cost, and trace gates.
### Best Reference Sources
`claude-cookbooks-main`, `G0DM0D3-main`, `adversarial-spec-main`.
### Concepts To Borrow
Agent examples, eval loops, model comparison, adversarial review.
### Concepts To Avoid
Telemetry or provider lock-in without consent.
### Proposed Upgrade
Add AI eval policy, prompt/version tracking, safety and trace requirements.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\claude-cookbooks-main\claude-cookbooks-main`, `C:\Vaults\references\Core Project References\G0DM0D3-main\research`
### Manual Integration Steps
Tie AI-Agent platform to L4 AI gateway.
### Validation Checklist
AI-Agent spec includes eval dataset, failure modes, monitor plan, not-tested gaps.
### Regression Risks
Eval theater.
### Priority
Medium/Later.

## Module: Security Gateway

### Current Role
Cross-cutting security policy and audit gate.
### Current Weakness
Needs structured findings and dual-use boundary.
### Best Reference Sources
`claude-code-security-review-main`, `Anthropic-Cybersecurity-Skills-main`, `clawsec-main`.
### Concepts To Borrow
Finding schema, defensive security coverage, audit workflow.
### Concepts To Avoid
Offensive steps outside authorized scope.
### Proposed Upgrade
Add defensive scope declaration and finding receipt schema.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\claude-code-security-review-main\claudecode`, `C:\Vaults\references\Other Projects References\Anthropic-Cybersecurity-Skills-main\Anthropic-Cybersecurity-Skills-main\mappings`
### Manual Integration Steps
Map vulnerability patterns to audit gates and Triage categories.
### Validation Checklist
Security gate finds issue platform gate misses.
### Regression Risks
False positives or unsafe advice.
### Priority
High.

## Module: Engineering Gateway

### Current Role
Build quality, reliability, dependency, architecture standards.
### Current Weakness
Needs executable check matrix.
### Best Reference Sources
`get-shit-done-main`, `superpowers-main`, `mattpocock-skills-main`.
### Concepts To Borrow
Verify-work, TDD/debug workflows, architecture diagnosis.
### Concepts To Avoid
Checklist-only engineering.
### Proposed Upgrade
Add build/lint/type/test/perf/dependency gate table.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\superpowers-main\skills`, `C:\Vaults\references\Core Project References\mattpocock-skills-main\skills\engineering`
### Manual Integration Steps
Map each engineering check to executable command or not-tested.
### Validation Checklist
Engineering gate blocks one failed build/lint/type/test.
### Regression Risks
Toolchain-specific assumptions.
### Priority
High.

## Module: AI Gateway

### Current Role
Cross-target AI/LLM policy.
### Current Weakness
Needs eval and safety proof.
### Best Reference Sources
`claude-cookbooks-main`, `G0DM0D3-main`, `adversarial-spec-main`.
### Concepts To Borrow
Agent SDK examples, model racing, adversarial eval.
### Concepts To Avoid
Provider-specific claims as framework truth.
### Proposed Upgrade
Require eval plan, prompt versioning, safety gates, and monitoring notes.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\claude-cookbooks-main\claude-cookbooks-main`, `C:\Vaults\references\Core Project References\G0DM0D3-main\research`
### Manual Integration Steps
Create AI gateway eval artifact schema.
### Validation Checklist
AI feature cannot pass without eval/not-tested fields.
### Regression Risks
Benchmark theater.
### Priority
Medium/High.

## Module: Aesthetic Gateway

### Current Role
Brand, color, typography, motion, design tokens.
### Current Weakness
Needs reference-backed visual rules.
### Best Reference Sources
`ui-ux-pro-max-skill-main`, `skill.color-expert-main`.
### Concepts To Borrow
Design token and color-system references.
### Concepts To Avoid
One-note palettes or arbitrary style catalogs.
### Proposed Upgrade
Add visual decision source, token rationale, and accessibility check.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\ui-ux-pro-max-skill-main\src\ui-ux-pro-max`
### Manual Integration Steps
Map tokens to platform design requirements.
### Validation Checklist
Visual choices cite a design rule or project context.
### Regression Risks
Design bloat.
### Priority
Medium.

## Module: Design Gateway

### Current Role
UX, interaction, information architecture, accessibility floor.
### Current Weakness
Needs workflow and design-system validation.
### Best Reference Sources
`ui-ux-pro-max-skill-main`, `mcp-server-guide-main`, `stitch-skills-main`.
### Concepts To Borrow
Design-system rules and Figma/Stitch style workflows.
### Concepts To Avoid
External tool dependence in core.
### Proposed Upgrade
Add IA, interaction, and accessibility validation gates.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\mcp-server-guide-main\mcp-server-guide-main\skills`, `C:\Vaults\references\Other Projects References\stitch-skills-main\stitch-skills-main\skills`
### Manual Integration Steps
Reference optional design-tool integrations without making them mandatory.
### Validation Checklist
Design gate catches navigation/interaction/accessibility issue.
### Regression Risks
Tool-specific assumptions.
### Priority
Medium.

## Module: Experience Gateway

### Current Role
User research, usability, accessibility, satisfaction.
### Current Weakness
May be too product-focused for internal tooling.
### Best Reference Sources
`pm-skills-main`, `Product-Manager-Skills-main`, `hig-doctor-main`.
### Concepts To Borrow
Research and usability test structures.
### Concepts To Avoid
Market/monetization overhead unless productized.
### Proposed Upgrade
Gate only user-facing or product-context tasks.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\pm-skills-main\pm-skills-main`
### Manual Integration Steps
Add activation policy for when Experience is relevant.
### Validation Checklist
Experience gate only fires on user-facing work.
### Regression Risks
Unneeded process on internal tasks.
### Priority
Low/Medium.

## Module: Instinct

### Current Role
Future passive observer for execution patterns.
### Current Weakness
No live module folder and no 100+ receipt corpus.
### Best Reference Sources
`graphify-7`, Wabble Archive.
### Concepts To Borrow
Passive graph/pattern observation.
### Concepts To Avoid
Proposal generation before evidence.
### Proposed Upgrade
Create only as read-only observer after corpus gate.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\graphify-7\graphify`
### Manual Integration Steps
Wait for 100+ receipts; implement read-only pattern extraction.
### Validation Checklist
3 human-validated non-spurious patterns.
### Regression Risks
Spurious pattern mining.
### Priority
Later.

## Module: Synth

### Current Role
Future improvement hypothesis generator.
### Current Weakness
Depends on Instinct evidence.
### Best Reference Sources
`adversarial-spec-main`, `OpenSpec-main`.
### Concepts To Borrow
Hypothesis framing and change proposal discipline.
### Concepts To Avoid
Self-justifying proposals.
### Proposed Upgrade
Only activate for human-validated Instinct patterns.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\adversarial-spec-main\adversarial-spec-main`
### Manual Integration Steps
Define hypothesis schema and rejection criteria.
### Validation Checklist
Every hypothesis cites receipt evidence.
### Regression Risks
Pattern theater.
### Priority
Later.

## Module: Blueprint

### Current Role
Future formal promotion proposal.
### Current Weakness
No runtime proof.
### Best Reference Sources
`OpenSpec-main`.
### Concepts To Borrow
Formal change proposal lifecycle.
### Concepts To Avoid
Promotion without benchmark.
### Proposed Upgrade
Use OpenSpec-style change discipline for module improvements.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`
### Manual Integration Steps
Define before/after behavior, risk, rollback, benchmark gates.
### Validation Checklist
Blueprint cannot proceed without Synth evidence.
### Regression Risks
Process bulk.
### Priority
Later.

## Module: Factory

### Current Role
Future new-module creation.
### Current Weakness
High bloat risk.
### Best Reference Sources
`SkillForge`, `anthropic-skills-main`.
### Concepts To Borrow
Skill scaffolding and validation.
### Concepts To Avoid
Creating modules because ideas exist.
### Proposed Upgrade
Require proven missing module need and benchmark target.
### Files/Folders To Inspect
`C:\Vaults\references\Other Projects References\SkillForge`, `C:\Vaults\references\Core Project References\anthropic-skills-main\template`
### Manual Integration Steps
Define module-creation gate and anti-bloat checklist.
### Validation Checklist
New module has owner, trigger, receipt, tests, rollback.
### Regression Risks
Module explosion.
### Priority
Later.

## Module: Augment

### Current Role
Future experimental module modification.
### Current Weakness
Self-modification risk.
### Best Reference Sources
`OpenSpec-main`, `SkillForge`.
### Concepts To Borrow
Experimental change isolation.
### Concepts To Avoid
Writing directly to production modules.
### Proposed Upgrade
Only write under experiments until benchmark and attestation pass.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`
### Manual Integration Steps
Define experiment folder and rollback condition.
### Validation Checklist
No production module write before Forge.
### Regression Risks
Framework drift.
### Priority
Later.

## Module: Benchmark

### Current Role
Future quality gate for module changes.
### Current Weakness
Benchmark theater risk.
### Best Reference Sources
`codeflow-main`, `mempalace-develop` as warning, Wabble receipts.
### Concepts To Borrow
Reproducible tests; avoid irrelevant metrics.
### Concepts To Avoid
Recall-only or self-authored acceptance as proof.
### Proposed Upgrade
Every benchmark declares developer outcome.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\codeflow-main\tests`, `C:\Vaults\references\Core Project References\mempalace-develop\benchmarks`
### Manual Integration Steps
Define benchmark schema: baseline, outcome, task, regression, evidence.
### Validation Checklist
Benchmark can reject a worse module.
### Regression Risks
Overfitting to internal tests.
### Priority
Later.

## Module: Forge

### Current Role
Future production promotion.
### Current Weakness
Highest self-modification risk.
### Best Reference Sources
`OpenSpec-main`, Wabble Attestation rules.
### Concepts To Borrow
Promotion gate and archive.
### Concepts To Avoid
Automatic promotion.
### Proposed Upgrade
Require Attestation, Benchmark PASS, rollback, no open contradictions.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`
### Manual Integration Steps
Define promotion receipt and affected-module cascade.
### Validation Checklist
No Forge action without human attestation.
### Regression Risks
Core framework corruption.
### Priority
Later.

## Module: Feedback

### Current Role
Future explicit signal capture.
### Current Weakness
No privacy/product boundary yet.
### Best Reference Sources
`G0DM0D3-main`, `pm-skills-main`.
### Concepts To Borrow
Feedback datasets and product signal capture.
### Concepts To Avoid
Telemetry without consent.
### Proposed Upgrade
Manual feedback only until privacy policy exists.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\G0DM0D3-main\functions\api\telemetry.ts`
### Manual Integration Steps
Define feedback record schema and opt-in boundary.
### Validation Checklist
Feedback source and consent state recorded.
### Regression Risks
Privacy breach or noisy feedback.
### Priority
Later.

## Module: Retro

### Current Role
Future retrospective learning.
### Current Weakness
Needs real release/task corpus.
### Best Reference Sources
`get-shit-done-main`, `superpowers-main`.
### Concepts To Borrow
Verification and post-phase review practices.
### Concepts To Avoid
Retrospective before real work.
### Proposed Upgrade
Manual retro after completed integrations; automate later.
### Files/Folders To Inspect
`C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`
### Manual Integration Steps
Create retro template tied to receipts and defects.
### Validation Checklist
Retro produces one actionable rule or no-op.
### Regression Risks
Ceremony without change.
### Priority
Later.

## 8. Cross-Cutting Improvements

### Naming Conventions

- Align `framework.yaml` ids with live module directories.
- Decide canonical platform ids: `iot` vs `iot-embedded`, `library` vs `library-package`, `extension` vs `extension-plugin`.
- Keep module names stable even if implementation files move.
- Every borrowed idea must cite exact reference path.

### Module Contracts

- `skill-rules.json` remains the activation and authority contract.
- Add or validate: `module`, `layer`, `tier`, `activators`, `file_path_patterns`, `authority`, `verification_mode`, `receipt_required`, `requires_receipts_from`.
- No two modules own the same output in a session.

### Spec Lifecycle

- Use OpenSpec-style change lifecycle: proposal, spec, change class, archive.
- Keep Wabble P1-P4 hierarchy, but schema-validate each stage.
- BREAKING changes trigger Migrate + Provenance cascade.

### Planning Workflow

- Use GSD's phase discipline as reference, but keep Wabble's receipt gate.
- Make Research -> Plan -> Execute receipts machine-readable.
- Gate collapse only with explicit low-risk conditions.

### Agent Workflow

- Use agent-creator hard-stop pattern for Reviewer/Verifier subagents.
- Use TeamPlan only for independent bounded work.
- No role catalogs that exist only for theater.

### Validation Gates

- Every PASS receipt must include actual checks and evidence.
- Every PARTIAL/FAIL receipt must include failure reason.
- Every not-tested gap must be visible.
- Add schema validation for receipts and skill-rules.

### Artifact Standards

- Specs: schema + citations.
- Receipts: JSON first; markdown summaries optional.
- Memory: drawer schema + staleness.
- Reference notes: exact path + source map citation + trust level.

### Documentation Standards

- Docs are generated from specs, receipts, and memory.
- No vague "inspired by" claims.
- Do not duplicate reference docs into WabbleSpec.

### Memory/Reference Systems

- Resolve backend decision: MemPalace/Chroma, SQLite/FTS, or flat JSON.
- Start with search/storage separation.
- Defer EntityGraph until full-text limitation is proven.

### Benchmark Systems

- Each benchmark must state developer outcome measured.
- Avoid recall@5 style metrics unless directly tied to Wabble tasks.
- Compare against AGENTS.md, GSD, and OMX on representative tasks.

### Anti-Slop Systems

- Cleanup plan before cleanup edits.
- Regression lock before refactor.
- Prefer deletion/reuse/boundary repair over new modules.

### Dashboard/Reporting Systems

- Add `/wabble-health` or equivalent.
- Health must detect stale `framework.yaml`, missing L8 folders, invalid receipts, stale evidence, schema mismatches.

### Failure Handling

- Use typed error events from `_shared\schemas\error-event.schema.json`.
- Add GSD-style named defect patterns under each type.
- Route failures to Triage/Guard/Verifier, not freeform prose.

### Critique Loops

- Critiques are adversarial guidance.
- Do not shrink ambition by default.
- Convert critique into gates, thresholds, and validation cases.

## 9. Integration Rules

- Never copy blindly.
- Preserve WabbleSpec identity.
- Adapt concepts, not surface syntax.
- Document every borrowed idea.
- Cite exact reference paths.
- Validate against `framework.yaml`, then update `framework.yaml` only after plan is clear.
- Update `BUILD-PLAN.md` only after integration decision and validation evidence exist.
- One integration at a time.
- Critical before low.
- No shrinking by default.
- No bloat without module purpose.
- No vague "inspired by" notes.
- No raw `.npmrc`, private journal, external connector, or credential config inspection.
- No generated bundle pruning or copying until package entrypoints are checked.
- No L8 runtime before receipt corpus gate.
- No new dependency without decision record and rollback path.
- No schema change without revalidating consumers.
- No module owns output already owned by another module.

## 10. Validation Framework

Run these checks for every integration:

- Does this improve a real module?
- Does this duplicate an existing feature?
- Does this increase clarity?
- Does this increase execution power?
- Does this increase maintenance burden?
- Is the reference path exact?
- Is the adaptation strategy clear?
- Is there a rollback path?
- Does this preserve current build direction?
- Does this align with `framework.yaml`?
- Does it align with `BUILD-PLAN.md` or require a documented correction?
- Does it need a schema update?
- Does it need a receipt update?
- Does it create a new dependency?
- Does it create a new hook?
- Does it increase user-visible command count?
- Does it cite evidence and not just an idea?
- Does it have a not-tested field?
- Does it have a failure mode and stop condition?

Per-priority validation:

Critical:
- Must run schema/path/receipt validation.
- Must include exact source map path.
- Must prove it blocks or detects a real failure.

High:
- Must improve a current module or quality gate.
- Must include rollback or disable path.

Medium:
- Must be behind target/gateway activation.
- Must not increase default context.

Low:
- Must stay optional.
- Must not enter core flow.

Later:
- Must have explicit corpus/data gate.

Reject:
- Must document why rejected and where it lives.

## 11. Final Execution Roadmap

## Phase 0 - Read and Map Current Project

- Goal: Align current architecture, live modules, `BUILD-PLAN.md`, and `framework.yaml`.
- References used: current project anchors only.
- Modules affected: all.
- Tasks:
  - Refresh module inventory.
  - Record stale `framework.yaml` conflicts.
  - Verify live `modules\` and `.wabblespec\`.
  - Decide whether L8 is planned-only or missing.
- Expected output: current architecture correction note.
- Validation checklist:
  - Live module paths listed.
  - Stale framework fields named.
  - No source changes beyond planning docs.
- Stop conditions:
  - Missing critical anchors.
  - Source-truth conflict cannot be resolved.

## Phase 1 - Critical Reference Integrations

- Goal: Make the core enforceable.
- References used: `get-shit-done-main`, `OpenSpec-main`, `cartographer-main`, `mempalace-develop`, `context-mode-main`, `destructive_command_guard-main`, `claude-code-safety-net-main`.
- Modules affected: Recipe, ScopeFrame, Specify, Explore, ReferenceLoad, Guard, Executor, Verifier, Archive, Memory, MemorySearch, Provenance, Rollback.
- Tasks:
  - Receipt enforcement backbone.
  - Spec/change schemas.
  - Wabble project-map contract.
  - Memory backend decision.
  - Command safety gate.
- Expected output: core proof loop that blocks missing/invalid receipts.
- Validation checklist:
  - Missing receipt blocks.
  - Spec schema validates.
  - Reference path exact.
  - Memory excludes EXPIRED by default.
- Stop conditions:
  - Hook cannot block.
  - Receipts cannot prove checks.

## Phase 2 - High-Value Module Upgrades

- Goal: Strengthen execution quality and safety.
- References used: `oh-my-codex-main`, `claude-code-security-review-main`, `superpowers-main`, `agent-os-main`, `caveman-main`.
- Modules affected: Autopilot, ModelRouter, Economy, Reviewer, Security, Test, Decompose, Rollback, Product.
- Tasks:
  - Thin orchestration adapter.
  - Structured finding schema.
  - Worktree rollback target.
  - Standards discovery.
  - Context economy policy.
- Expected output: safer, clearer execution loop.
- Validation checklist:
  - Reviewer findings structured.
  - Worktree/checkpoint target chosen per risk.
  - Economy captures verbose outputs.
- Stop conditions:
  - Orchestration bypasses gates.
  - Review becomes noisy.

## Phase 3 - Cross-Cutting Framework Upgrades

- Goal: Make WabbleSpec maintainable.
- References used: `codeflow-main`, `cartographer-main`, GSD defect patterns, current schemas.
- Modules affected: Monitor, Triage, Guard, Archive, Document.
- Tasks:
  - `/wabble-health` design.
  - Named defect taxonomy.
  - Schema drift checks.
  - Documentation citation policy.
- Expected output: diagnostic/reporting layer.
- Validation checklist:
  - Health report detects known stale framework fields.
  - Defects route to owners.
- Stop conditions:
  - Dashboard becomes decorative.

## Phase 4 - Secondary Reference Integrations

- Goal: Add target/gateway depth after core proof.
- References used: `anthropic-skills-main`, `ui-ux-pro-max-skill-main`, `Claude-Code-Game-Studios-main`, `hig-doctor-main`, `claude-cookbooks-main`.
- Modules affected: L3 platforms, L4 gateways, Document, ResearchLog.
- Tasks:
  - Platform reference packs.
  - UI/design/security/AI gateway hardening.
  - Feature-scoped research artifacts.
- Expected output: target-specific checks generic templates miss.
- Validation checklist:
  - Each target catches 3 target-specific issues.
  - References have freshness notes.
- Stop conditions:
  - Packs are shallow checklists.

## Phase 5 - Experimental Integrations

- Goal: Add graph, debate, model-eval, and evolution only after evidence.
- References used: `graphify-7`, `adversarial-spec-main`, `G0DM0D3-main`, `SkillForge`, future Wabble receipts.
- Modules affected: EntityGraph, Dream, MemoryMine, AI, Benchmark, Feedback, L8.
- Tasks:
  - Graph MVP after MemorySearch failure cases.
  - Adversarial spec debate for high-risk specs.
  - Benchmark outcome schema.
  - Instinct observer only after receipt corpus.
- Expected output: evidence-backed experiments.
- Validation checklist:
  - 50+ drawers before MemoryMine.
  - 100+ receipts before Instinct/Synth.
  - 3 human-validated patterns before Blueprint.
- Stop conditions:
  - No corpus.
  - No measurable developer outcome.

## Phase 6 - Cleanup, Validation, and Documentation

- Goal: Lock integrations and remove ambiguity.
- References used: all integrated refs, current schemas, `BUILD-PLAN.md`, `framework.yaml`.
- Modules affected: all integrated modules.
- Tasks:
  - Update `framework.yaml`.
  - Update `BUILD-PLAN.md`.
  - Add decision records.
  - Run path/schema/receipt validation.
  - Generate docs from receipts.
- Expected output: coherent framework state.
- Validation checklist:
  - No stale paths.
  - No invalid skill-rules.
  - No missing receipts for completed integrations.
  - Remaining risks documented.
- Stop conditions:
  - Validation fails and cannot be fixed in same integration.

## 12. Human Manual Integration Queue

# Manual Integration Queue

## Item 001 - Receipt Enforcement Backbone

- Priority: Critical
- Module: Guard, Verifier, Archive, Executor
- Reference: `get-shit-done-main`
- Exact Path: `C:\Vaults\references\Core Project References\get-shit-done-main\hooks`, `C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`, `C:\Vaults\references\Core Project References\get-shit-done-main\sdk\src`
- Why It Matters: Turns receipts from documents into operational gates.
- What To Borrow: Phase gate structure, verify-work separation, state continuity.
- What Not To Borrow: Full command surface or workflow sprawl.
- Integration Steps: Inspect hooks/commands; define Wabble receipt preconditions; update Guard/Verifier/Archive schema; test missing receipt block.
- Validation: Missing upstream receipt blocks downstream action.
- Done When: A deliberately skipped receipt cannot proceed.

## Item 002 - Formal Spec and Change Schema

- Priority: Critical
- Module: Specify, ScopeFrame, Migrate
- Reference: `OpenSpec-main`
- Exact Path: `C:\Vaults\references\Core Project References\OpenSpec-main\schemas`, `C:\Vaults\references\Core Project References\OpenSpec-main\openspec\specs`, `C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`
- Why It Matters: Spec is WabbleSpec's source of truth.
- What To Borrow: Schema validation, change proposal lifecycle.
- What Not To Borrow: OpenSpec CLI identity or multi-assistant strategy.
- Integration Steps: Define Wabble spec schema; define change schema; connect Migrate and Provenance.
- Validation: Spec/change files validate and trigger correct downstream action.
- Done When: BREAKING change marks dependents.

## Item 003 - Project Map Contract

- Priority: Critical
- Module: Explore, ReferenceLoad, Recipe
- Reference: `cartographer-main`
- Exact Path: `C:\Vaults\references\Core Project References\cartographer-main\src\code-graph`
- Why It Matters: Prevents planning from using vague or stale context.
- What To Borrow: Index/brief/impact/context concepts.
- What Not To Borrow: Generated report churn.
- Integration Steps: Define Wabble project-map schema; add freshness; add impact brief.
- Validation: Explore produces map with entry points, modules, tests, risks.
- Done When: ReferenceLoad uses map slices, not raw repo dumps.

## Item 004 - Memory Backend Decision

- Priority: Critical
- Module: Memory, MemorySearch, Provenance
- Reference: `mempalace-develop`, `context-mode-main`
- Exact Path: `C:\Vaults\references\Core Project References\mempalace-develop\mempalace`, `C:\Vaults\references\Extra Project References\context-mode-main\src\store.ts`
- Why It Matters: Current memory direction conflicts across docs.
- What To Borrow: Drawer hierarchy, FTS/searchable local state, hook capture.
- What Not To Borrow: Unjustified Chroma/embedding dependency or benchmark claims.
- Integration Steps: Write decision record; select backend; define migration; update module docs.
- Validation: 10 drawers searchable; EXPIRED excluded by default.
- Done When: Memory has one clear backend path.

## Item 005 - Command Safety Gate

- Priority: Critical
- Module: Guard, Executor, Rollback
- Reference: `destructive_command_guard-main`, `claude-code-safety-net-main`
- Exact Path: `C:\Vaults\references\Other Projects References\destructive_command_guard-main\destructive_command_guard-main\src`, `C:\Vaults\references\Other Projects References\claude-code-safety-net-main\claude-code-safety-net-main\src`
- Why It Matters: Autonomous execution needs deterministic safety checks.
- What To Borrow: Command classification and block/warn semantics.
- What Not To Borrow: Overblocking policy.
- Integration Steps: Define Wabble command classes; add hook messages; test risky examples.
- Validation: Safe commands pass, risky commands block with reason.
- Done When: Guard has command-risk gate.

## Item 006 - Thin Orchestration Adapter

- Priority: High
- Module: Autopilot, ModelRouter, Ensemble, TeamPlan
- Reference: `oh-my-codex-main`
- Exact Path: `C:\Vaults\references\Core Project References\oh-my-codex-main\src`, `C:\Vaults\references\Core Project References\oh-my-codex-main\prompts`, `C:\Vaults\references\Core Project References\oh-my-codex-main\skills`
- Why It Matters: Wabble runs in Codex/OMX context.
- What To Borrow: Role registry, hook lifecycle, compact explore/sparkshell ideas.
- What Not To Borrow: Whole framework identity.
- Integration Steps: Map Wabble phases to current orchestration surfaces; define adapter boundary.
- Validation: Adapter does not bypass Wabble receipts.
- Done When: Wabble can call orchestration helpers with receipt gates intact.

## Item 007 - Structured Reviewer Findings

- Priority: High
- Module: Reviewer, Security, Triage
- Reference: `claude-code-security-review-main`
- Exact Path: `C:\Vaults\references\Core Project References\claude-code-security-review-main\claudecode`
- Why It Matters: Reviews need structured actionable output.
- What To Borrow: Finding parser/filter, generated-file filtering, severity structure.
- What Not To Borrow: Trusted-PR assumptions.
- Integration Steps: Create Wabble finding schema; add prompt-injection caution; wire to Triage.
- Validation: Reviewer produces severity/evidence/fix/test anchor.
- Done When: Findings become review receipts.

## Item 008 - Worktree Rollback Target

- Priority: High
- Module: Decompose, Executor, Rollback
- Reference: `superpowers-main`
- Exact Path: `C:\Vaults\references\Core Project References\superpowers-main\skills`
- Why It Matters: Git-native isolation is stronger than file checkpoints for high-risk waves.
- What To Borrow: Worktree-per-task pattern.
- What Not To Borrow: Heavy process for small tasks.
- Integration Steps: Add rollback target enum; set trigger threshold; document cleanup.
- Validation: High-risk wave gets worktree rollback plan.
- Done When: Rollback supports checkpoint and worktree.

## Item 009 - Standards Discovery Profile

- Priority: High
- Module: Product, ScopeFrame, Specify, Explore
- Reference: `agent-os-main`
- Exact Path: `C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os`
- Why It Matters: Discover before prescribe.
- What To Borrow: Standards discovery and injection.
- What Not To Borrow: Advisory-only standards.
- Integration Steps: Extract project standards into Wabble memory; cite in specs; Guard enforces critical ones.
- Validation: Specify uses discovered standards.
- Done When: Standards are evidence, not vibes.

## Item 010 - Context Economy Policy

- Priority: High
- Module: Economy, MemorySearch, ReferenceLoad
- Reference: `caveman-main`, `context-mode-main`
- Exact Path: `C:\Vaults\references\Core Project References\caveman-main\src`, `C:\Vaults\references\Extra Project References\context-mode-main\src`
- Why It Matters: Reference integration can flood context.
- What To Borrow: Compact policy and sandboxed verbose output.
- What Not To Borrow: Lossy compression of errors.
- Integration Steps: Add capture policy, output thresholds, exact-error preservation rule.
- Validation: Large outputs stored/cited, not pasted.
- Done When: Economy has mechanical rules.

## Item 011 - Health Diagnostic

- Priority: Medium
- Module: Monitor, Archive, Guard
- Reference: `codeflow-main`, OMC doctor concept
- Exact Path: `C:\Vaults\references\Core Project References\codeflow-main\card`, `C:\Vaults\references\Core Project References\codeflow-main\card\lib\analyzer.js`
- Why It Matters: Wabble needs self-diagnosis.
- What To Borrow: Health card/report structure.
- What Not To Borrow: Large single-file UI coupling.
- Integration Steps: Define health checks; include schema drift, stale framework, missing L8, bad receipts.
- Validation: Health report catches known framework.yaml conflicts.
- Done When: `/wabble-health` design exists.

## Item 012 - Platform Pack Hardening: CLI

- Priority: High
- Module: L3 CLI, Recipe, Verifier
- Reference: `get-shit-done-main`, `agent-os-main`
- Exact Path: `C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`, `C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os`
- Why It Matters: CLI already has validation evidence in `BUILD-PLAN.md`.
- What To Borrow: command/standards flow.
- What Not To Borrow: shell-specific assumptions.
- Integration Steps: Add exit code, stdout/stderr, startup, config, help, test gates.
- Validation: CLI spec catches issues generic Specify misses.
- Done When: CLI pack is reference-backed.

## Item 013 - Platform Pack Hardening: Web

- Priority: Medium
- Module: L3 Web, Aesthetic, Design, Experience
- Reference: `ui-ux-pro-max-skill-main`, `superpowers-chrome-main`
- Exact Path: `C:\Vaults\references\Core Project References\ui-ux-pro-max-skill-main\src\ui-ux-pro-max`, `C:\Vaults\references\Other Projects References\superpowers-chrome-main\superpowers-chrome-main\mcp\src`
- Why It Matters: Web needs visual/browser verification.
- What To Borrow: design gates and browser capture.
- What Not To Borrow: visual asset catalogs wholesale.
- Integration Steps: Add browser/render/accessibility gates.
- Validation: Web pack catches UI issue generic template misses.
- Done When: Web pack has exact reference-backed checks.

## Item 014 - Platform Pack Hardening: API-Service

- Priority: Medium
- Module: L3 API-Service, Security, Engineering
- Reference: `claude-cookbooks-main`, `OpenSpec-main`
- Exact Path: `C:\Vaults\references\Other Projects References\claude-cookbooks-main\claude-cookbooks-main\claude_agent_sdk`, `C:\Vaults\references\Core Project References\OpenSpec-main\schemas`
- Why It Matters: API contracts need schemas and examples.
- What To Borrow: API/agent examples and schema discipline.
- What Not To Borrow: external service assumptions.
- Integration Steps: Add auth/rate/error/schema/e2e gates.
- Validation: API pack catches an auth or contract issue generic template misses.
- Done When: API-Service has reference-backed validation.

## Item 015 - Named Defect Taxonomy

- Priority: High
- Module: Triage, Guard, Verifier
- Reference: `get-shit-done-main`
- Exact Path: `C:\Vaults\references\Core Project References\get-shit-done-main\get-shit-done`
- Why It Matters: Six error types are too broad for action.
- What To Borrow: named defect pattern style.
- What Not To Borrow: exact defect list without Wabble validation.
- Integration Steps: Add Wabble defect cards: symptom, detection, fix, test.
- Validation: Triage routes each defect.
- Done When: error taxonomy has actionable children.

## Item 016 - Provenance Cascade

- Priority: Critical
- Module: Provenance, Migrate, Specify, Memory
- Reference: `OpenSpec-main`, `mempalace-develop`
- Exact Path: `C:\Vaults\references\Core Project References\OpenSpec-main\openspec\changes`, `C:\Vaults\references\Core Project References\mempalace-develop\docs\schema.sql`
- Why It Matters: Stale dependencies are a unique Wabble differentiator.
- What To Borrow: change lifecycle and relational memory ideas.
- What Not To Borrow: hidden database without schema docs.
- Integration Steps: Add source_hash, cited_by, change_class, affected_specs.
- Validation: Source update marks dependents NEEDS_REVERIFICATION.
- Done When: Cascade works on one test set.

## Item 017 - Archive Index

- Priority: Critical
- Module: Archive
- Reference: `get-shit-done-main`, `pentest-ai-agents-main`
- Exact Path: `C:\Vaults\references\Core Project References\get-shit-done-main\get-shit-done`, `C:\Vaults\references\Extra Project References\pentest-ai-agents-main\db`
- Why It Matters: Receipts need queryable audit history.
- What To Borrow: state continuity and status transitions.
- What Not To Borrow: offensive pentest instructions.
- Integration Steps: Build receipt index fields; map PENDING/IN_PROGRESS/PASS/FAIL/BLOCKED.
- Validation: Query archive by module/status/not-tested.
- Done When: Archive answers completion evidence.

## Item 018 - Reviewer Role Hard Stops

- Priority: High
- Module: Reviewer, Verifier
- Reference: `agent-creator`
- Exact Path: `C:\Vaults\references\Extra Project References\agent-creator\references\prompt-patterns.md`
- Why It Matters: Reviewers should not implement fixes.
- What To Borrow: description trigger and hard-stop sections.
- What Not To Borrow: tool overload.
- Integration Steps: Update reviewer/adversary/grader role specs.
- Validation: Reviewer outputs findings only.
- Done When: Role boundary is explicit.

## Item 019 - Feature-Scoped Research

- Priority: Medium
- Module: ResearchLog, ReferenceLoad, Specify
- Reference: `OpenSpec-main`, `agent-os-main`
- Exact Path: `C:\Vaults\references\Core Project References\OpenSpec-main\openspec\specs`, `C:\Vaults\references\Core Project References\agent-os-main\commands\agent-os`
- Why It Matters: Research must bind to feature/spec, not session prose.
- What To Borrow: feature artifact structure.
- What Not To Borrow: advisory notes.
- Integration Steps: Add feature research artifact and memory citations.
- Validation: Research artifact feeds Specify.
- Done When: ResearchLog is not duplicate note-taking.

## Item 020 - Gateway Security Pack

- Priority: High
- Module: Security, Reviewer, Triage
- Reference: `claude-code-security-review-main`, `Anthropic-Cybersecurity-Skills-main`
- Exact Path: `C:\Vaults\references\Core Project References\claude-code-security-review-main\claudecode`, `C:\Vaults\references\Other Projects References\Anthropic-Cybersecurity-Skills-main\Anthropic-Cybersecurity-Skills-main\skills`
- Why It Matters: Security gateway needs concrete threat patterns.
- What To Borrow: defensive review patterns and coverage mapping.
- What Not To Borrow: dual-use/offensive procedure.
- Integration Steps: Scope defensive use; map patterns to audit gates.
- Validation: Gateway catches issue missed by platform.
- Done When: Security findings are structured and scoped.

## Item 021 - Gateway Engineering Pack

- Priority: High
- Module: Engineering, Verifier, Test
- Reference: `superpowers-main`, `get-shit-done-main`
- Exact Path: `C:\Vaults\references\Core Project References\superpowers-main\skills`, `C:\Vaults\references\Core Project References\get-shit-done-main\commands\gsd`
- Why It Matters: Engineering gates need practical tests.
- What To Borrow: TDD, verify-work, build quality.
- What Not To Borrow: workflow sprawl.
- Integration Steps: Add build/lint/type/test/perf check matrix.
- Validation: Engineering gate blocks bad build.
- Done When: Checks are executable or not-tested recorded.

## Item 022 - Gateway AI Pack

- Priority: Medium
- Module: AI, AI-Agent, Benchmark
- Reference: `claude-cookbooks-main`, `G0DM0D3-main`, `adversarial-spec-main`
- Exact Path: `C:\Vaults\references\Other Projects References\claude-cookbooks-main\claude-cookbooks-main`, `C:\Vaults\references\Core Project References\G0DM0D3-main\research`
- Why It Matters: AI features need eval and safety.
- What To Borrow: eval loops, model racing, adversarial review.
- What Not To Borrow: provider-specific claims or telemetry without privacy review.
- Integration Steps: Add AI eval artifact and safety checklist.
- Validation: AI gate names model/eval/not-tested risks.
- Done When: AI feature spec has eval plan.

## Item 023 - UI/UX Gateway Pack

- Priority: Medium
- Module: Aesthetic, Design, Experience, Web
- Reference: `ui-ux-pro-max-skill-main`, `hig-doctor-main`
- Exact Path: `C:\Vaults\references\Core Project References\ui-ux-pro-max-skill-main\src\ui-ux-pro-max`, `C:\Vaults\references\Other Projects References\hig-doctor-main\hig-doctor-main\skills`
- Why It Matters: Frontend quality needs concrete visual gates.
- What To Borrow: design-system and platform guideline checks.
- What Not To Borrow: stale HIG claims without freshness.
- Integration Steps: Add freshness and visual validation checklist.
- Validation: UI gate catches visual/accessibility issue.
- Done When: Gateway has exact referenced rules.

## Item 024 - Game Platform Reference Pack

- Priority: Medium
- Module: Game
- Reference: `Claude-Code-Game-Studios-main`
- Exact Path: `C:\Vaults\references\Core Project References\Claude-Code-Game-Studios-main\docs\engine-reference`
- Why It Matters: Game target needs engine-specific gates.
- What To Borrow: engine refs and domain template layout.
- What Not To Borrow: 49-agent studio hierarchy.
- Integration Steps: Mine engine constraints and verification gates.
- Validation: Game template catches frame/asset/engine issue.
- Done When: Game pack is not generic.

## Item 025 - Plugin Manifest Reference

- Priority: Low
- Module: Extension/Plugin, Package, Release
- Reference: `claude-plugins-official-main`
- Exact Path: `C:\Vaults\references\Core Project References\claude-plugins-official-main\.claude-plugin\marketplace.json`
- Why It Matters: Plugin packaging needs manifest schema.
- What To Borrow: manifest fields and validation ideas.
- What Not To Borrow: plugin contents or `.npmrc`.
- Integration Steps: Define Wabble plugin manifest template.
- Validation: Manifest validates without sensitive files.
- Done When: Extension package has schema.

## Item 026 - Domain Pack Architecture

- Priority: Low
- Module: future domain packs, Package
- Reference: `financial-services-main`
- Exact Path: `C:\Vaults\references\Core Project References\financial-services-main\plugins`, `C:\Vaults\references\Core Project References\financial-services-main\managed-agent-cookbooks`
- Why It Matters: Shows vertical pack organization.
- What To Borrow: cookbook/manifest structure.
- What Not To Borrow: live connector assumptions.
- Integration Steps: Draft optional domain-pack pattern.
- Validation: Domain pack does not affect core.
- Done When: Optional pack spec exists.

## Item 027 - Graph Intelligence Gate

- Priority: Later
- Module: EntityGraph, Dream, MemoryMine
- Reference: `graphify-7`
- Exact Path: `C:\Vaults\references\Core Project References\graphify-7\graphify`
- Why It Matters: Graphs may improve memory retrieval.
- What To Borrow: graph extraction/query/path.
- What Not To Borrow: graph before corpus.
- Integration Steps: Collect full-text failure cases; define graph MVP.
- Validation: Graph answers cases full-text missed.
- Done When: Evidence justifies graph.

## Item 028 - Adversarial Spec Gate

- Priority: Later
- Module: Reviewer, Propose, Specify
- Reference: `adversarial-spec-main`
- Exact Path: `C:\Vaults\references\Other Projects References\adversarial-spec-main\adversarial-spec-main\skills\adversarial-spec\SKILL.md`
- Why It Matters: High-risk specs need challenge.
- What To Borrow: adversarial consensus pattern.
- What Not To Borrow: provider panel by default.
- Integration Steps: Add high-risk trigger; require bounded output.
- Validation: Catches real spec weakness.
- Done When: Used on high-risk spec only.

## Item 029 - Outcome-Linked Benchmark

- Priority: Later
- Module: Benchmark, Forge, Instinct
- Reference: MemPalace benchmark warning, codeflow tests, Wabble receipts.
- Exact Path: `C:\Vaults\references\Core Project References\mempalace-develop`, `C:\Vaults\references\Core Project References\codeflow-main\tests`
- Why It Matters: L8 needs proof, not self-praise.
- What To Borrow: reproducible eval discipline.
- What Not To Borrow: irrelevant recall metrics.
- Integration Steps: Add benchmark schema with developer outcome field.
- Validation: Each benchmark ties to false completion, missed test, stale evidence, or rework.
- Done When: Benchmark can reject bad module improvement.

## Item 030 - L8 Observer Only

- Priority: Later/Experimental
- Module: Instinct
- Reference: future Wabble receipts, `graphify-7`
- Exact Path: future `C:\Vaults\WabbleSpec v6.1\modules\l8\instinct`
- Why It Matters: Self-improvement ambition preserved safely.
- What To Borrow: passive graph/pattern observation.
- What Not To Borrow: auto-promotion.
- Integration Steps: Wait for 100+ verified receipts; create read-only observer; no Synth.
- Validation: 3 human-validated non-spurious patterns.
- Done When: Instinct observes only.

## Rejected Reference Queue

## Item R01 - Duplicate Marketing Skills

- Priority: Reject
- Module: none
- Reference: `marketingskills-main (1)`
- Exact Path: `C:\Vaults\references\Other Projects References\marketingskills-main (1)\marketingskills-main`
- Why It Matters: Duplicate signal.
- What To Borrow: nothing.
- What Not To Borrow: duplicate content.
- Integration Steps: none.
- Validation: use canonical if ever needed.
- Done When: excluded from plan.

## Item R02 - Duplicate Claudian

- Priority: Reject
- Module: none
- Reference: `claudian-main`
- Exact Path: `C:\Vaults\references\Other Projects References\claudian-main\claudian-main`
- Why It Matters: Duplicate of `claudian`.
- What To Borrow: nothing.
- What Not To Borrow: duplicate content.
- Integration Steps: none.
- Validation: keep one canonical.
- Done When: excluded.

## Item R03 - Duplicate Superpowers

- Priority: Reject
- Module: none
- Reference: Other `superpowers-main`
- Exact Path: `C:\Vaults\references\Other Projects References\superpowers-main\superpowers-main`
- Why It Matters: Duplicate of core `superpowers-main`.
- What To Borrow: use core copy only.
- What Not To Borrow: duplicate path.
- Integration Steps: none.
- Validation: core path cited.
- Done When: excluded.

## Item R04 - Empty Template

- Priority: Reject
- Module: none
- Reference: `template`
- Exact Path: `C:\Vaults\references\Other Projects References\template`
- Why It Matters: scaffold only.
- What To Borrow: nothing.
- What Not To Borrow: placeholder content.
- Integration Steps: none.
- Validation: no module depends on it.
- Done When: excluded.

## Item R05 - Generated Eval Workspace

- Priority: Reject unless evidence archive
- Module: none
- Reference: `claude-skills-main\eval-workspace`
- Exact Path: `C:\Vaults\references\Other Projects References\claude-skills-main\eval-workspace`
- Why It Matters: generated workspace, not runtime signal.
- What To Borrow: nothing now.
- What Not To Borrow: generated artifacts.
- Integration Steps: none.
- Validation: only preserve if explicit evidence archive.
- Done When: excluded from active integration.

## Completion Evidence Targets For This Plan

- The plan file exists at `C:\Vaults\WabbleSpec v6.1\REFERENCE-INTEGRATION-MASTER-PLAN.md`.
- All required sections 1-12 exist.
- Critical/high/medium/low/later/reject integration priority is present.
- Per-module plans include every current live module family and planned L8 family.
- Manual integration queue includes critical through rejected items.
