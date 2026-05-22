# Supporting Repository Analysis — WabbleSpec v6.1

> Analyzed: 2026-05-21
> Repos: mempalace/mempalace, Donchitos/Claude-Code-Game-Studios, obra/superpowers
> Purpose: Mechanism references — lessons, warnings, design validation. Not products to copy.

---

## MemPalace

### What It Is

Local-first AI memory system. Stores conversation content verbatim without summarization. Organizes storage in a three-level hierarchy: wings (people/projects), rooms (topics), drawers (content). ChromaDB for vector search. SQLite for a temporal entity-relationship knowledge graph. Ships as an MCP server with 29 tools. Requires ~300MB disk for the default embedding model.

### Core Mechanism

- Persistent memory (verbatim storage)
- Semantic retrieval (ChromaDB vector search, pluggable backends)
- Structured folders/categories (wings/rooms/drawers)
- Knowledge graph (SQLite, entity nodes with validity windows)
- Local-first storage (no mandatory cloud)
- Benchmark claims (LongMemEval, ConvoMem)

### What It Teaches

**Storage structure converged independently on WabbleSpec.** MemPalace's `wings/rooms/drawers` maps onto WabbleSpec's `memory/drawers/` at the naming level. WabbleSpec reached this structure from a different direction — evidence management, not conversation replay. The convergence suggests the drawer metaphor is natural and defensible.

**Verbatim vs. structured is a real architectural choice.** MemPalace stores full conversation text. WabbleSpec stores structured evidence with explicit fields (staleness, confidence, source, provenance). For WabbleSpec's use case — tracking framework execution evidence, not replaying conversations — structured is the right call. The comparison clarifies why: verbatim is only useful when the exact phrasing carries information. Framework evidence does not.

**Search and storage are correctly separated.** MemPalace has retrieval modules distinct from storage. WabbleSpec already does this (MemorySearch ↔ Memory). The separation is validated.

**Closets concept already in WabbleSpec.** MemPalace doesn't explicitly have an archive/closets concept — expired evidence disappears or gets replaced. WabbleSpec's `closets/` as a non-destructive archive with provenance records is a stricter and better design.

**Knowledge graph as a distinct layer is correct.** MemPalace uses SQLite for entity-relationship tracking separate from raw content storage. WabbleSpec's EntityGraph is the same pattern. Validated.

### What It Warns Against

**Embedding dependency creates fragility.** 300MB local model or API call to generate embeddings. Either path breaks offline-first guarantees. WabbleSpec's full-text + entity pattern matching for retrieval avoids this entirely. MemPalace's high benchmark scores are embedding-dependent — the scores don't transfer to a system without embeddings.

**Benchmark theater.** 96.6% R@5 on LongMemEval is a headline number for a benchmark that tests conversation memory retrieval. LongMemEval is designed for QA over conversation history. WabbleSpec does not use memory for conversation replay — it uses it for framework execution evidence. This benchmark score says nothing useful about whether the memory pattern improves spec quality or execution reliability. The risk: WabbleSpec's own Benchmark module (L8) could fall into the same trap — running benchmarks on metrics that don't connect to actual developer outcomes.

**29 MCP tools is scatter, not power.** WabbleSpec removed MCP entirely. This repo confirms the risk: MCP grows surface area without clear boundaries.

**Verbatim storage at scale becomes retrieval noise.** Without decay or staleness management, old content pollutes search results. WabbleSpec's six staleness states plus Dream's EMA decay is a substantially better answer to this problem. MemPalace doesn't have a staleness model.

### What To Steal

Nothing structural — WabbleSpec's memory design is already more rigorous. One terminological validation: `drawers` as the atomic evidence unit is correct and defensible vocabulary for user-facing documentation.

One process lesson: MemPalace's benchmark scripts are versioned and reproducible in the repo. WabbleSpec's Benchmark module should produce reproducible eval reports, not just ad-hoc assessments.

### What To Avoid

- Embedding-based semantic retrieval (external dep, 300MB, fragile offline)
- MCP as integration vector (already removed)
- Headline benchmark claims disconnected from practical use-case improvement
- Verbatim storage (structured evidence is better for framework use)

### Relevance to Spec

No structural changes needed. WabbleSpec's L5 Memory layer is more sophisticated. One addition worth making to the Benchmark module spec: require that eval cases connect to a developer outcome, not just an abstract retrieval metric. "Recall@5 on held-out set" is not a useful benchmark for a spec framework.

---

## Claude-Code-Game-Studios

### What It Is

A `CLAUDE.md` template system for game development. Creates a 49-agent studio hierarchy within a single Claude Code session. Three tiers: Directors (Opus), Department Leads (Sonnet), Specialists (Haiku/Sonnet). 73 slash commands. 12 automated hooks. 11 path-scoped rules enforcing coding standards by directory.

### Core Mechanism

- Multi-agent roles (49 agents, 3 tiers)
- Domain-specific skills (game dev only)
- Command palette (73 slash commands)
- Hooks (12 automated, commit/asset/session lifecycle)
- Templates (CLAUDE.md as monolithic master config)
- Path-scoped enforcement rules (gameplay/, core/, networking/)

### What It Teaches

**Path-scoped rules are a lightweight enforcement mechanism.** Rules that activate based on file path patterns (not just task type) create targeted enforcement without heavyweight module loading. WabbleSpec's `skill-rules.json` activation uses trigger patterns and command names — it doesn't explicitly bind rules to file path prefixes. This is a gap worth examining.

**12 hooks covering commit, asset, and session lifecycle show hook-based enforcement is viable.** The hooks validate at natural checkpoints (pre-commit, post-session) without requiring explicit user invocation. WabbleSpec's Guard module does input validation, but hooks at the git layer are a different enforcement point.

**"You always make the call" as an explicit UX contract.** The system enforces that agents draft and present options — humans decide. WabbleSpec has this in Attestation and Reviewer escalation, but it's structural, not UX-facing. Surface this principle explicitly in WabbleSpec's user-facing documentation.

**Platform packages with template variants per domain are correct.** WabbleSpec's 11 L3 platform packages are the same idea executed more formally. This repo validates the pattern.

### What It Warns Against

**49 agents is agent theater.** There is no actual specialization happening. "Creative Director" and "Technical Director" are the same model receiving different CLAUDE.md instructions. The agent count is a surface-level impression of sophistication, not a functional architecture. The real work happens in the underlying model — the agent labels are routing labels, not capability boundaries.

**73 slash commands create a discovery problem.** Users cannot hold 73 commands in working memory. The activation-pattern approach in WabbleSpec (commands trigger from context) is better than a command palette users must memorize.

**Tier-based model routing by role is model-name coupling.** Routing Opus to "Directors" and Haiku to "Specialists" assumes stable model pricing, capability boundaries, and naming conventions — all of which change. WabbleSpec's vendor-neutral capability descriptors solve this correctly. This repo is a concrete illustration of the problem WabbleSpec's I6 invariant prevents.

**Monolithic CLAUDE.md scales poorly.** Everything in one file violates progressive loading. Every session loads everything. WabbleSpec's four loading gates (Recipe, Stage, Phase, Activation) are architecturally superior.

**Game-domain specificity has zero portability value.** All domain knowledge in this repo is game-specific. The structural lessons apply to WabbleSpec; the content does not.

### What To Steal

**Path-scoped activation in skill-rules.json.** Add `file_path_patterns` as an optional activation field alongside `triggers` and `commands`. Rules that fire when active files match `src/networking/**` or `firmware/**` would create tighter platform-specific enforcement.

**Hook coverage at git layer.** WabbleSpec's hooks cover session and module lifecycle. A pre-commit hook that checks for pending receipts or open REVISE cycles would add a safety net. Lightweight to add; Guard does not cover this checkpoint.

### What To Avoid

- Agent count as an architecture signal
- Model-name-to-role coupling
- Command palette design (73 commands, user must remember)
- Monolithic master config files
- Domain-specific content in a general framework

### Relevance to Spec

Two specific changes worth considering:

1. Add optional `file_path_patterns` to `skill-rules.json` schema as an activation trigger for path-scoped rules. Low implementation cost, targeted enforcement benefit.
2. Add a pre-commit hook in Scaffold output that checks `.wabblespec/receipts/` for incomplete wave cycles. Catches abandoned execution states at the git boundary.

---

## Superpowers

### What It Is

Composable software development methodology. Seven-stage mandatory workflow enforced before any implementation work. Skills auto-trigger from context. Multi-platform: Claude Code, Codex CLI, Cursor, Gemini CLI, Copilot CLI. Git worktrees for task isolation. TDD as non-optional enforcement. Subagent coordination built into the workflow.

### Core Mechanism

- Reusable prompts (skills as composable units, auto-trigger)
- Hooks (automation, lifecycle)
- Enforced workflows (7-stage: brainstorm → worktree → plan → develop → TDD → review → merge)
- Worktree/branch workflow (git isolation per task)
- Templates (skill modules)
- Onboarding docs
- Multi-platform portability

### What It Teaches

**A mandatory workflow with 7 stages is comprehensible.** Users can learn and follow it. WabbleSpec's Research/Plan/Execute three-phase model maps to this pattern at a higher level. The lesson: the more stages, the higher the comprehension cost. WabbleSpec's three phases are correct for user-facing communication; the internal module complexity is implementation detail.

**Git worktrees as first-class isolation.** One worktree per task, branched, isolated. WabbleSpec's Rollback uses checkpoints at the wave level — state snapshots written to `.wabblespec/checkpoints/`. Worktrees are a stronger isolation guarantee because they operate at the git level, not the file-state level. A failed experiment in a worktree leaves the main branch untouched without needing a restore procedure. This is a concrete improvement over checkpoint-based rollback for large execution waves.

**Brainstorming as an enforced first stage prevents scope drift.** Superpowers requires brainstorming before any code is written. WabbleSpec's Interview module does this, but Interview is demand-triggered (ambiguity resolution). Making a brainstorm/proposal phase mandatory — not just available — prevents silent assumption-making.

**Skill auto-triggering from context works.** Skills that activate from context without explicit `/command` invocation reduce user friction. WabbleSpec's skill-rules.json activation patterns do this. Validated.

**Simplicity as a first-class principle is operationally important.** Superpowers explicitly names "complexity reduction" and "simplicity as primary goal" in its methodology. WabbleSpec's I12 (spec quality over volume) is the equivalent, but scoped to specs. The principle deserves to apply to the framework itself, not only to the specs it produces.

### What It Warns Against

**Multi-platform portability requires abstraction that erodes depth.** Superpowers works across Claude Code, Cursor, Codex, and Gemini. To maintain this portability, the skill system must use only capabilities common across all platforms. This trades depth (hooks, receipts, skill-rules.json activation) for breadth. WabbleSpec's Claude Code focus is the correct trade — platform-depth over portability.

**Methodology complexity inversely affects adoption.** 7 stages is manageable. WabbleSpec has 55 modules across 9 layers. The documentation burden is high. The framework is implementable — the spec is detailed enough. But a user opening WabbleSpec cold has a steep comprehension curve. Superpowers is immediately graspable. WabbleSpec should not try to be Superpowers — but it should produce first-contact documentation that is.

**"Skills trigger automatically" overpromises.** Activation pattern matching is fuzzy. WabbleSpec's skill-rules.json is more explicit about what triggers what, but even pattern-based activation can misfire. Over-claiming automation leads to user confusion when it doesn't work. WabbleSpec documentation should be precise about what activates when and why, not vague promises of automatic behavior.

### What To Steal

**Git worktrees as Executor wave isolation.** Replace or supplement checkpoint-based rollback with worktree-based isolation for high-complexity waves (Decompose score > 0.7). WabbleSpec already has `EnterWorktree`/`ExitWorktree` tool support in the harness. Rollback could declare a worktree-target type alongside wave-checkpoint and deploy-snapshot. Stronger isolation guarantee, simpler restore path.

**Mandatory brainstorm/proposal gate before P1 spec work.** Elevate Propose from demand-triggered to required on first P1 entry for new projects. Currently Propose activates when decisions have significant trade-offs — it could be mandatory as a validation that the user has considered options before Interview and Specify run. Low overhead, prevents silent assumption baking.

**7-stage user-facing mental model for onboarding.** WabbleSpec's Document module generates onboarding content. The onboarding doc should present a simple flow (analogous to Superpowers' 7 stages) that abstracts over the internal module complexity. Users need a navigable mental model, not a 55-module inventory as a first contact.

### What To Avoid

- Platform portability as a design goal (depth wins over breadth for this use case)
- Vague claims about automatic skill triggering
- Framing the framework as a methodology a user follows — WabbleSpec is a framework the user activates; it should do the following, not instruct the user to follow

---

## Shared Lessons

**Lesson 1: Hierarchy that mirrors the problem domain is naturally correct.** All three repos arrive at hierarchical organization: wings/rooms/drawers, Director/Lead/Specialist, brainstorm/plan/execute. WabbleSpec's gateway/group/module hierarchy is the same pattern at a larger scale. The hierarchy works — the risk is it becomes navigational complexity rather than structural clarity.

**Lesson 2: The best isolation mechanisms are git-native.** Superpowers uses worktrees. Game Studios uses path-scoped rules enforced by hooks. MemPalace uses local storage boundaries. All three reach for git or filesystem-level enforcement, not framework-level enforcement alone. WabbleSpec relies primarily on receipt chains and Guard validation. Git-level enforcement is a missing layer.

**Lesson 3: Activation pattern systems work, but they require explicit documentation.** All three use some form of context-triggered activation. All three have activation gaps or overpromise automatic triggering. The mechanism is sound; the documentation must be precise.

**Lesson 4: Domain-specific modules carry 80% of the value.** The most useful content in Game Studios is the game-specific hooks and rules. The most useful content in MemPalace is the structured retrieval design. WabbleSpec's 11 platform packages and 6 gateways are following the same pattern. Platform-specific content is where real constraints live — generic cross-cutting content is often underdetermined.

**Lesson 5: Benchmarks without outcome connection are noise.** All three repos either claim or imply performance gains. None connect those gains to developer outcomes. WabbleSpec's Benchmark module must avoid this. Every benchmark case should answer: "Did this improve what the developer built?"

---

## Mechanism Map

| Mechanism | Seen In | Useful Lesson | Risk | Should WabbleSpec Use It? |
|---|---|---|---|---|
| Persistent memory | MemPalace, WabbleSpec (L5) | Evidence needs staleness tracking, not just storage | Without decay, becomes noise | Yes — already designed correctly |
| Semantic retrieval (vector) | MemPalace | High recall scores on benchmarks | External dep, 300MB model, scores don't transfer to non-conversation use | No — full-text + entity pattern matching is correct for this use case |
| Structured folders/categories | All three | Hierarchy mirrors problem domain naturally | Over-nesting creates navigation burden | Yes — gateway/group/module validated |
| Multi-agent roles | Game Studios | Specialization labels create UX clarity | Fake specialization — same model, different instructions | Yes — but TeamPlan activates at L4 only, not by default |
| Domain-specific skills | Game Studios, Superpowers | Most value lives in domain-specific content | Domain lock-in; portability erodes depth | Yes — 11 platform packages is the right execution |
| Reusable prompts | Superpowers | Skills as composable units reduce duplication | Activation gaps and overpromising | Yes — skill-rules.json activation pattern is correct approach |
| Hooks | Game Studios, Superpowers | Lifecycle enforcement at natural checkpoints | Hook proliferation becomes maintenance | Yes — add git-layer hook (pre-commit receipt check) |
| Templates | All three | Reduces cold-start friction | Template staleness — must be maintained | Yes — platform spec-template variants already planned |
| Evaluation scripts | MemPalace (benchmarks) | Reproducible benchmarks build trust | Benchmark theater — metrics disconnected from outcomes | Carefully — require outcome connection in Benchmark module |
| Onboarding docs | Superpowers | Simple mental model reduces first-contact friction | WabbleSpec's complexity makes onboarding hard | Yes — Document module should produce a 7-stage equivalent |
| Command palette | Game Studios | Discoverability for known commands | 73 commands is too many to hold in memory | No — activation-pattern approach is better than command enumeration |
| Worktree/branch workflow | Superpowers | Git-level isolation is stronger than checkpoint-based | Worktree overhead for simple tasks | Yes — add worktree as Rollback target type for high-complexity waves |
| Marketplace/plugin model | Superpowers (multi-platform) | Portability signals maturity | Portability erodes depth | No — Claude Code focus is correct |
| Local-first storage | MemPalace, WabbleSpec | No external dependencies, privacy by default | Manual maintenance, no sync | Yes — already committed to, validated |
| Benchmark claims | MemPalace | Reproducible evals build credibility | Metrics not connected to user outcomes | Carefully — benchmark must define the outcome being measured |
| Generated documentation | Game Studios, WabbleSpec (Document) | Auto-generated docs reduce maintenance burden | Generated docs become stale if spec changes | Yes — Document module already designed correctly |

---

## Anti-Theater Check

### 49 Agents (Claude-Code-Game-Studios)

**Looks impressive:** A full studio hierarchy. Directors. Leads. Specialists. Titles from the games industry.

**Fake value:** The model doesn't change. A "Creative Director" prompt and a "Gameplay Programmer" prompt both route to the same Claude instance with different instruction headers. The hierarchy is vocabulary, not capability differentiation.

**How to test:** Remove 45 of the 49 agent definitions. Run the same game development task. Measure output quality difference. Predicted result: negligible.

**Verdict: Delete the pattern.** WabbleSpec's TeamPlan activating at L4 only is correct. Resist pressure to add agent roles as a complexity-justifying gesture.

---

### 96.6% R@5 Benchmark (MemPalace)

**Looks impressive:** Specific number, named benchmark, reproducible.

**Fake value:** LongMemEval tests retrieval of conversation content. WabbleSpec doesn't store conversations — it stores framework execution evidence. A 96.6% score on conversation recall has zero transfer value to framework evidence retrieval. The benchmark is real; its relevance to WabbleSpec is zero.

**How to test:** Run WabbleSpec's memory retrieval against a benchmark designed for spec evidence and execution outcome correlation. No such benchmark exists yet — which is the correct answer for why not to claim benchmark superiority.

**Verdict: Keep Benchmark module, but require outcome-linked metrics.** Not recall@5. "Did the retrieved evidence produce a better spec artifact?" is the correct dimension.

---

### 73 Slash Commands (Claude-Code-Game-Studios)

**Looks impressive:** Complete coverage of every phase, role, and workflow.

**Fake value:** Nobody uses 73 commands. Discovery fails past ~10. The commands exist to demonstrate thoroughness, not to be used.

**How to test:** Count command usage frequency from session logs. Predicted result: top 10 commands cover 90% of invocations.

**Verdict: Shrink hard.** WabbleSpec's activation-pattern approach reduces explicit commands to entry points and explicit overrides only. This is correct.

---

### Dream + MemoryMine (WabbleSpec L5)

**Looks impressive:** Background consolidation, EMA decay, pattern extraction, gap detection, staleness maps. Sounds like a self-managing intelligent memory.

**Potential fake value:** If these modules run but the outputs (gap-map.md, pattern-summary.md, mine-clusters.md) are never actually read by developers or used to change behavior, they are elaborate file-writing operations that produce no value.

**How to test:** After 10 Dream runs, check whether any gap-map.md finding resulted in a Synth proposal that became a real framework improvement. If zero: these modules are theater.

**Verdict: Keep but validate on first real implementation.** The design is sound. The risk is building all of Dream/MemoryMine before knowing whether developers actually act on the outputs. Build Memory + MemorySearch first. Observe usage. Add Dream/MemoryMine only after evidence that background consolidation is needed.

---

### EntityGraph (WabbleSpec L5)

**Looks impressive:** Entity registry, relationship edges, seven entity types, seven relationship types, confidence scoring, Dream cleanup.

**Potential fake value:** If entity extraction by pattern matching produces noisy, low-confidence graphs that nobody queries, it adds file I/O overhead and maintenance burden without improving anything.

**How to test:** After 20 drawers, check whether MemorySearch entity queries return higher-quality results than full-text queries. If not: EntityGraph is adding complexity without value.

**Verdict: Defer EntityGraph to after Memory and MemorySearch are proven.** Start with full-text + topic retrieval. Add entity tracking only when gap evidence shows it's needed.

---

### Evolution Layer L8 (WabbleSpec)

**Looks impressive:** Instinct → Synth → Blueprint → Factory → Augment → Benchmark → Forge → Retro. Framework learns from itself. Self-improving spec system.

**Potential fake value:** This is seven modules that constitute a second framework inside the framework. The entire pipeline requires implementation, testing, and validation before producing any actual improvement. A framework with zero production runs has zero patterns to learn from. Building L8 before L0-L7 are proven is building a self-improvement loop with nothing to improve.

**How to test:** Cannot test until the framework has been used. Evolution's value is entirely downstream.

**Verdict: Defer explicitly.** L8 should be designed (as it is) but not implemented until L0-L7 have accumulated enough real execution data to feed Instinct. Flag this in the planning order.

---

## Minimal Useful Version

What the smallest useful WabbleSpec would need, based on lessons from all three repos:

**Memory: Yes — but narrow.**
Start with: Memory (write path, read path, staleness states), MemorySearch (topic + full-text query), Provenance (lineage, append-only ledger).
Defer: EntityGraph (until query patterns prove it's needed), Dream (until stale drawer volume proves it's needed), MemoryMine (until pattern mining adds value over manual review), Forget (until deletion use cases emerge).

**Skills: Yes — activation-pattern based.**
Core: skill-rules.json activation patterns, SKILL.md per module, receipts.
Defer: 73-command command palettes, tier-based routing, domain-specific agents beyond the defined platform packages.

**Agents: Minimal.**
Core: Reviewer with Adversary/Grader subagents (budget-gated). TeamPlan available at L4 only.
Defer: Any expansion of agent count. Validate that Reviewer produces measurably better output before adding more agent-level complexity.

**Templates: Yes.**
Core: Platform spec-template variants for declared build targets. P1-P4 hierarchy templates.
Defer: Onboarding templates until Document module is proven.

**Workflows: Yes — but the three-phase model is sufficient.**
Core: Research/Plan/Execute with receipt chain.
Consider adding: Git worktree as rollback target for high-complexity waves (EnterWorktree/ExitWorktree harness support already exists).
Defer: Full L8 Evolution pipeline.

**Validation reason for each:**
- Memory: Every spec decision should be traceable. Evidence without staleness tracking becomes false confidence.
- Skills: Without activation patterns, modules don't load selectively — progressive loading collapses.
- Agents: Reviewer is needed because adversarial review produces demonstrably better specs. TeamPlan is needed for genuinely parallel workstreams. Nothing else is validated.
- Templates: Cold-start projects need structure or they default to ad hoc.
- Three-phase model: Research before planning, planning before execution — this is the core disciplinary value.

---

## Spec Changes Required

**Add:**
- `file_path_patterns` as optional activation field in `skill-rules.json` schema (path-scoped rule enforcement, from Game Studios)
- Git worktree as a third Rollback target type alongside wave-checkpoint and deploy-snapshot (from Superpowers)
- Mandatory first-entry Propose gate before P1 spec work on new projects (from Superpowers brainstorm enforcement)
- Explicit onboarding document (simple 5-7 step user-facing mental model) as a required Document module output type
- Outcome requirement in Benchmark module: every eval case must declare the developer outcome it measures, not only the metric

**Cut:**
- Any path toward expanding agent count beyond Reviewer subagents and TeamPlan
- Any benchmark claim framing in spec language (replace "recall@5" type metrics with outcome-linked measurements)

**Merge:**
- Nothing. The separation of modules is already correct.

**Rename:**
- Nothing critical. Drawer terminology is validated by MemPalace convergence.

**Simplify:**
- L8 Evolution: specify build order explicitly — Instinct first, Synth second, rest only after real execution data exists. Currently the spec implies L8 is a full deliverable alongside L0-L7.
- EntityGraph: reduce scope to minimum viable (file and module entities only, not all 7 entity types) until usage proves broader entity types are needed.

**Validate:**
- Dream/MemoryMine: after first 10 real Dream runs, measure whether any output file actually changed developer behavior. If not, these are theater.
- EntityGraph queries: after 20 drawers, compare entity-query result quality to full-text query result quality. If no improvement, defer EntityGraph.
- TeamPlan: validate that L4 complexity tasks actually benefit from multi-agent coordination vs. single-agent with structured wave plan.

**Defer:**
- Full L8 Evolution pipeline implementation (build Instinct's observer first, run it, see what patterns emerge — only then build Synth → Blueprint chain)
- MemoryMine until Memory evidence base has grown beyond 50 drawers in real use
- EntityGraph full seven-entity-type extraction until full-text search has been shown insufficient

**Explicitly reject:**
- Embedding-based semantic retrieval (external dep, 300MB model, not offline-safe)
- Agent count expansion as a quality signal
- Tier-based model routing by role label (violates I6)
- MCP integration (already removed — MemPalace confirms this was correct)
- Multi-platform portability as a design goal
- 73+ command palette design
- Benchmark claims not tied to developer outcomes

---

## Bloat Risk Score

**Memory system bloat risk: 6/10**

The design is correct and necessary. The risk is additive bloat: Dream + MemoryMine + EntityGraph + Provenance + Forget are five supporting modules on top of the core two (Memory + MemorySearch). Each is individually justified. Collectively they create a maintenance burden before any real usage has validated that each is needed. The activity-based staleness model is clever but requires calibrating thresholds that can only be discovered through real use. Building all seven modules before running the framework once is over-investment.

**Multi-agent bloat risk: 3/10**

Low risk. TeamPlan correctly gates behind L4 complexity. Reviewer's subagent model (Adversary + Grader) is bounded with budget gates and max 3 REVISE cycles. The risk is one: pressure to add more specialized agents after seeing Game Studios' 49-agent system. The spec is currently resistant to this. It needs to stay that way.

**Skill system bloat risk: 7/10**

~55 modules plus 11 platform packages plus 6 gateways is a large surface area. The modular design and progressive loading gates are correct mitigations. The risk is that each module adds its own references/, rules/, evaluations/, schemas/ — each component directory multiplies file count. A 55-module system with 10 components each is 550+ files. This is manageable for a human author but creates navigation friction. The loading gates prevent context bloat, but the filesystem bloat is real. Mitigation: enforce lean modules per I12. Most modules should not have all 14 optional components.

**Template bloat risk: 4/10**

11 platform packages each with a spec-template variant is 11 templates to maintain. As platform versions change (React 20, Next.js 16, etc.) templates go stale. I9 (evidence expiry) applies to these — but staleness tracking on template files is less clearly specified than on Memory drawers. Medium risk, manageable with discipline.

**Workflow bloat risk: 5/10**

The three-phase model + receipt chain + four loading gates + six staleness states + seven verification modes is a complex enforcement surface. Each component is justified. Together they create failure mode complexity: a developer debugging "why didn't this work" may need to check receipts, staleness states, Guard validation layers, activation patterns, and REVISE cycles simultaneously. The spec needs a clear "what to check first" debugging path. Currently absent.

**Documentation bloat risk: 8/10**

This is the highest real risk. WabbleSpec v6.1 Core.md is already 1100+ lines. Memory.md is 900+ lines. The spec is thorough and internally consistent — but it is robot-first (as intended), not human-first. Every module has a full SKILL.md, skill-rules.json, receipt schema, and acceptance criteria. Total anticipated file count across all modules is in the hundreds. This is sustainable if I12 (spec quality over volume) is enforced ruthlessly. But the pattern already shows pressure toward completeness-as-virtue. Cut non-goals explicitly. Do not add explanatory prose — specs should be lookup tables, not tutorials.

**Benchmark/evaluation theater risk: 7/10**

WabbleSpec has a full L8 Evolution pipeline including a Benchmark module. The module evaluates experiments against Blueprint acceptance criteria. The risk: acceptance criteria are defined by the Blueprint authors (i.e., the framework itself evaluating its own proposals). This is circular. MemPalace's LongMemEval shows exactly how a project can claim rigorous benchmarking while measuring something unrelated to practical value. WabbleSpec needs external validation cases — real developer tasks with measurable outcomes — not internal acceptance criteria written by the same system proposing changes.

---

## Final Architecture Recommendation

**Single-agent + skills (Option 2), with memory and workflow enforcement as supporting layers — not primary architecture.**

WabbleSpec is already past the point of choosing between these options for the core. The architecture is defined and the choice is correct. The question for this analysis is whether the supporting repos argue for expanding into multi-agent, memory-primary, or marketplace patterns.

They do not.

MemPalace shows that memory is a supporting mechanism, not an architecture. Making memory the center creates maintenance burden and benchmark theater. WabbleSpec's L5 as a supporting layer below the main skill system is correct placement.

Game Studios shows that 49 agents add complexity without adding capability. TeamPlan at L4 is the right ceiling.

Superpowers shows that a single-agent + skill system with enforced workflow produces real developer discipline at low complexity cost. Seven stages, git worktrees, TDD enforcement — these are concrete, testable workflow improvements. WabbleSpec's three-phase model and receipt chain are the equivalent at higher formalism.

The single-agent + skill architecture with memory as evidence infrastructure and workflows as receipt-enforced phases is the correct answer. The spec already implements this. The risk is drift toward over-elaborating supporting layers (especially L8 Evolution and L5's extended modules) before the core has been validated through real use.

**Build order implication:** L0-L2 (Intake, Spec Core, Orchestration) → L3 Platform packages (top 3 targets first) → L5 Memory core (Memory + MemorySearch + Provenance) → L7 Delivery → L4 Gateways → L5 supporting (Dream, EntityGraph) → L8 Evolution (Instinct first, rest only after real data).

---

## Final Verdict

**USE AS INSPIRATION: strong lessons, but do not copy structure.**

All three repos confirm design decisions WabbleSpec already made (local-first, no external deps, activation-pattern skills, receipt-based workflow gates, structured evidence over verbatim storage, multi-agent bounded to genuine complexity).

The structural warnings are equally important:

- MemPalace: embedding dependency and benchmark theater risk. WabbleSpec avoids both — maintain those choices.
- Game Studios: agent count theater and model-name coupling. WabbleSpec's I6 and bounded TeamPlan prevent both — maintain those constraints.
- Superpowers: complexity erosion of user comprehension. WabbleSpec needs first-contact documentation that's as clear as a 7-stage workflow, even if the internals are more sophisticated.

Two concrete additions are worth making: path-scoped `file_path_patterns` in skill-rules.json activation, and git worktree as a Rollback target type. Everything else from these repos is either already present in WabbleSpec, already rejected for good reason, or theater that would add complexity without value.

The strongest signal from all three repos combined: **WabbleSpec is at risk of being overbuilt before it is used.** The spec is detailed, coherent, and internally consistent. That same thoroughness is the risk. Build L0-L5 core, run it on real projects, observe what actually breaks, then build L6-L8 from evidence rather than anticipation.
