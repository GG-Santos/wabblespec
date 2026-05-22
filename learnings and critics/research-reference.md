> Analysis date: 2026-05-21 | Projects analyzed: 5 | Verdict: SHRINK

# Competitive Research: WabbleSpec v6.1 vs. Reference Projects

---

## Project: OpenSpec (Fission-AI)

**Stars: 49,638 | Language: TypeScript | Updated: 2026-05-21**

### Project Summary
CLI framework for spec-driven development with AI coding assistants. Provides lightweight proposal → spec → design → tasks artifacts per feature. Cross-repo workspace browsing. Targets all AI assistant platforms (20+). Currently mid-reimplementation after discovering its original approach was overcomplicated.

### Core Value
"Agree before you build." Establishes shared understanding between human and AI before code is written. Lightweight integration with existing tools rather than a new ecosystem.

### Workflow Model
`/opsx:propose` → spec artifacts generated → `/opsx:apply` (implementation) → `/opsx:archive`. Workspace mode allows exploring multiple linked repos before committing to a proposal. Single-repo-slice implementation per cycle.

### Strong Ideas Worth Learning
- **Reimplementation lesson is the most valuable thing here.** Their WORKSPACE_REIMPLEMENTATION_DIRECTION document explicitly says: *"Don't predetermine the path with abstract internal machinery."* They built materialization systems, adapter layers, and target metadata management — and then tore it out because users never needed to see it. This is a direct warning to WabbleSpec.
- **"Workspace visibility is not change commitment."** Separating exploration from planning from execution is the right instinct.
- **User-visible workflow first, architecture second.** Each phase should answer: can users complete the next natural step?

### Weaknesses / Risks
- Mid-crisis. Their reimplementation signals the original over-engineered design failed.
- Broad platform support (20+ AI assistants) = lowest-common-denominator feature set.
- No memory system. No staleness tracking. No build-target routing.
- "Fluid not rigid" as a core principle produces inconsistency — no enforcement mechanism.

### What Not To Copy
- The "support every AI assistant" strategy dilutes the product.
- Avoid deferring user-visible workflow to build internal machinery first. WabbleSpec has 55 modules planned but no user-visible anything yet — same trap.

### Relevance To My Spec
Direct warning. WabbleSpec's module count (55+), loading gates, receipt chains, and orchestration layers are all the kind of internal machinery OpenSpec discovered users don't want. The reimplementation lesson applies directly.

---

## Project: GSD (get-shit-done)

**Stars: 63,383 | Language: JavaScript | Updated: 2026-05-21**

### Project Summary
Meta-prompting and context engineering orchestration system for Claude Code. Solves "context rot" (quality degradation as the LLM context fills) by routing heavy work into fresh subagent contexts while the main window stays lean. Has grown to 147 workflow files covering the full SDLC.

### Core Value
Context rot is the most concrete, measurable problem AI coding workflows face. GSD's architecture (main window stays at 30-40% capacity, subagents do the real work) is a direct engineering response to a real failure mode.

### Workflow Model
Six-command core loop: `new-project` → `discuss-phase` → `plan-phase` → `execute-phase` → `verify-work` → `ship`. `.planning/` directory holds artifacts (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md). Phases are independent — each can be discussed, planned, executed, and verified separately.

### Strong Ideas Worth Learning
- **Context rot framing is the best positioning in this space.** Not "better spec writing" — "your AI degrades as context grows, here's the fix." Problem-first framing.
- **Fresh subagent per phase is architecturally sound.** WabbleSpec's TeamPlan is in the same territory but GSD already has 63K users proving the concept.
- **Verify-work as a distinct phase** (not just part of execute) is the right separation. WabbleSpec's Verifier module matches this.
- **`.planning/` directory convention** maps cleanly to WabbleSpec's `.wabblespec/plans/`. Good precedent.
- **Machine-enforced rules via CONTEXT.md** (predicate format, grep-auditable, agent briefs cite verbatim) is a mature operational pattern WabbleSpec should study.
- **Named defect patterns** (Port Drift, State Trample, Phase-Dir Prefix Drift) — 25+ documented failure modes. WabbleSpec's error taxonomy should be this specific.

### Weaknesses / Risks
- 147 workflow files = organizational complexity. Navigation without tooling is a burden.
- No memory system with staleness. Evidence evaporates between sessions.
- No build-target routing. Same workflow regardless of whether you're building firmware or a web app.
- No self-improvement loop. Patterns discovered during execution don't feed back into the system.
- BSL license — source-available but not truly open.
- "Designed to run with --dangerously-skip-permissions" is a real adoption risk for cautious developers.

### What Not To Copy
- The 147-workflow expansion without consolidation. Surface area without structure creates confusion.
- Operator-level permissions as the default use case.

### Relevance To My Spec
GSD is WabbleSpec's most direct competitor for the "AI coding orchestration" space. WabbleSpec's L2 Orchestration layer (Autopilot, Executor, Verifier, Guard) overlaps substantially with GSD's core loop. WabbleSpec needs to be meaningfully better — not just more complex — in the areas GSD doesn't cover: memory/staleness, build-target routing, evolution. GSD's defect taxonomy work is a direct model for WabbleSpec's error taxonomy.

---

## Project: agent-os (buildermethods)

**Stars: 4,590 | Language: Shell | Updated: 2026-05-20**

### Project Summary
Codebase standards extraction and injection system. Five commands: discover-standards (extract tribal knowledge into AI-scannable docs), index-standards (catalog them), inject-standards (apply relevant standards contextually), plan-product (product planning), shape-spec (lightweight spec shaping before implementation).

### Core Value
AI agents produce inconsistent code because they don't know your project's specific conventions. agent-os makes those conventions explicit, discoverable, and injectable — without bloating context windows.

### Workflow Model
One-time: run `discover-standards` to extract patterns from existing codebase. Per-feature: `shape-spec` → `inject-standards` during implementation. Standards live in `agent-os/standards/` as plain markdown. Index in `index.yml`.

### Strong Ideas Worth Learning
- **"Every word costs tokens"** — standards must be minimal, example-driven, actionable. Rules-first, then reasoning. This is exactly right and WabbleSpec's Economy module is trying to enforce this but doesn't articulate it as a philosophy at the standards level.
- **Standards as first-class artifacts** separate from specs. WabbleSpec bundles standards into the spec hierarchy (P4 Standards) but agent-os proves there's value in standards that live outside the spec chain.
- **Discover before prescribe.** Extract real patterns before writing rules. WabbleSpec's Explore module should explicitly feed Specify in the same way — discovering before specifying.
- **One concept per standard** is a better decomposition principle than WabbleSpec's hierarchical P1-P4 depth.

### Weaknesses / Risks
- Very narrow scope — pure standards management. No execution, no verification, no delivery.
- Shell implementation limits cross-platform adoption.
- No memory between sessions. Discovery results not tracked with confidence or staleness.
- No enforcement. Standards are advisory, not mandatory. Inject is a suggestion, not a gate.
- Low stars relative to the others — signals limited adoption or niche positioning.

### What Not To Copy
- Advisory-only standards. The power comes from enforcement (Guard checking standards compliance), not documentation.
- Narrow scope without a path to expand — users will outgrow it immediately.

### Relevance To My Spec
agent-os validates WabbleSpec's standards abstraction at P4 but shows that the discovery workflow (Explore → standards extraction) needs to be a first-class explicit path, not buried in a general Explore module. WabbleSpec's `_shared/dev/` conventions and platform-specific rules benefit from the "minimal, example-driven, injectable" framing.

---

## Project: spec-kit (github)

**Stars: 104,205 | Language: Python | Updated: 2026-05-21**

### Project Summary
GitHub-owned toolkit for spec-driven development. Seven-step workflow: constitution → specify → clarify → plan → tasks → analyze → implement. `.specify/` directory holds per-feature artifacts. 30+ AI agent integrations. Constitutional framework of 9 immutable development principles. Enterprise-focused with compliance and design-system adherence built in.

### Core Value
Democratizing spec-driven development with a GitHub-branded, well-documented, multi-agent-compatible framework that works with every major AI coding assistant. Low barrier to entry, template-driven, organized.

### Workflow Model
`/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.analyze` → `/speckit.implement`. Each step produces an artifact consumed by the next. Constitution file defines project-level invariants. Feature specs live in `.specify/specs/{feature-id}/` with spec.md, plan.md, tasks.md, data-model.md, research.md.

### Strong Ideas Worth Learning
- **Constitution as invariants** — nine immutable principles that shape all code generation. WabbleSpec's 12 invariants are the same concept, better developed.
- **Feature-level spec directory** (`.specify/specs/{feature-id}/`) with multiple artifact types per feature maps to WabbleSpec's P3-P4 structure but is much simpler to navigate.
- **Given/When/Then acceptance scenarios** in spec templates — functional equivalent of WabbleSpec's EARS syntax, but more readable to humans. WabbleSpec should consider whether EARS is actually better for agents than GWT.
- **Extension/preset layering** (project-local → preset → extension → core) is a clean override system. WabbleSpec's platform packages are the same idea, less explicit.
- **Research.md per feature** — dedicated research artifact is equivalent to WabbleSpec's ResearchLog but at the feature level rather than session level. Feature-scoped research is more actionable.

### Weaknesses / Risks
- GitHub-owned = competitive moat, but also: less likely to take risks or innovate. Template-driven over-fit to greenfield web/API patterns.
- No memory system. No staleness. Research artifacts don't expire.
- No build-target routing. One workflow for all project types.
- No execution engine — spec-kit stops before it touches code. The "implement" step hands off to the AI agent without structured execution control.
- No self-improvement loop. No feedback from execution back into specs.
- Nine constitutional principles are hardcoded (Library-First, CLI Interface Mandate, etc.) — these are the author's preferences, not universally applicable.
- 104K stars partly reflects GitHub's reach, not product quality. Adoption signal is polluted.

### What Not To Copy
- The constitution as hardcoded opinionated principles. WabbleSpec's invariants are structural/behavioral constraints, not technology choices — that's better.
- Stopping before execution. A spec tool that doesn't gate execution is advisory, not operational.
- The "every project is library-first with CLI interface" assumption. That's one philosophy, not a framework principle.

### Relevance To My Spec
spec-kit is WabbleSpec's most dangerous competitive threat: GitHub backing, 104K stars, simple enough for broad adoption. WabbleSpec needs to be genuinely superior in specific dimensions — not just more comprehensive. The dimensions where WabbleSpec wins (memory/staleness, build-target routing, execution gating, evolution) are all things spec-kit explicitly doesn't do. WabbleSpec's threat is that developers will use spec-kit for the 80% case and never need WabbleSpec's 20%.

---

## Project: oh-my-claudecode (Yeachan-Heo)

**Stars: 34,455 | Language: TypeScript | Updated: 2026-05-21**

### Project Summary
Multi-agent orchestration framework for Claude Code. 39+ specialized skills/agents. Smart model routing (haiku/sonnet/opus by task complexity). Team mode orchestration pipeline. LSP integration, AST search tools, state management. Built around "zero learning curve" while providing sophisticated underlying orchestration.

### Core Value
Claude Code has powerful primitives; OMC removes the expertise barrier to using them correctly. Task routing, model selection, agent specialization, and verification loops — all automated.

### Workflow Model
Team mode: `team-plan → team-prd → team-exec → team-verify → team-fix`. Autopilot: autonomous feature completion. Ultrawork: maximum parallelism. Ralph: persistence mode with verification loops. Skill-scoped: `.omc/skills/` (project) or `~/.omc/skills/` (user).

### Strong Ideas Worth Learning
- **Model routing by task complexity** (haiku/simple, sonnet/standard, opus/architecture) is the right abstraction. WabbleSpec's ModelRouter and RuntimeProbe are the same idea but capability-descriptor-based rather than model-tier-based. WabbleSpec's approach is better (vendor-neutral) but OMC proves users want this routing.
- **Skill scoping** (project vs. user level) — `.omc/skills/` committed to version control is a concrete portability mechanism. WabbleSpec has framework vs. product separation (I11) but not this granularity.
- **Specialized agent roles** (analyst, architect, executor, verifier, debugger, tracer) are a clean decomposition. WabbleSpec's TeamPlan does this but the OMC agent list is more practical and narrower in scope.
- **`/omc-doctor` for diagnostics** — a debugging/health-check command is essential for any complex system. WabbleSpec has no equivalent health-check command.
- **Writer-memory and session search** as named skills — explicit memory as a user-invocable feature, not hidden infrastructure.

### Weaknesses / Risks
- Not spec-driven. Execution quality depends on agent quality, not on upfront spec discipline. Fast but not reliable.
- No evidence tracking. No staleness. No provenance. "Smart" but amnesiac.
- No build-target routing. Generic across all project types.
- 34K stars includes significant hype amplification (launched in a high-momentum Claude Code ecosystem).
- Zero enforcement. Skills are suggestions. Users can ignore the pipeline entirely.
- Model routing is Claude-specific despite being presented as multi-provider.

### What Not To Copy
- The "zero learning curve" marketing at the expense of structural guarantees. WabbleSpec's enforcement-first design is the right choice even if it increases learning curve.
- Growing the skill count indefinitely without a pruning/deprecation mechanism.

### Relevance To My Spec
OMC occupies the L2 Orchestration layer of WabbleSpec but without the spec anchor (I1) underneath it. Users who adopt OMC get fast execution without quality guarantees. WabbleSpec needs to show that spec-gated execution produces meaningfully better outcomes — not just more process. OMC's diagnostic command (`/omc-doctor`) and skill scoping mechanism are worth direct adoption in WabbleSpec.

---

## Shared Patterns

Across all five projects:

1. **Artifacts per phase, not one big document.** Every project separates proposal/spec/plan/tasks into distinct files per feature. WabbleSpec's P1-P4 hierarchy does this hierarchically, which is more powerful but harder to navigate.

2. **Slash commands as the UX entry point.** All five projects are slash-command driven. WabbleSpec's commands/ directory is correct.

3. **The planning directory convention.** `.planning/`, `.specify/`, `agent-os/`, `.wabblespec/` — all use a dotfolder to isolate framework artifacts from product code. WabbleSpec's I11 boundary is the strictest version of this.

4. **Verification as a distinct phase.** GSD, spec-kit, OMC all separate verification from execution. WabbleSpec's Verifier module is in the right place.

5. **Context window management is a first-class concern.** Every project addresses token density, context placement, or subagent routing. WabbleSpec's Economy module is the most formal treatment.

6. **No project has a memory system with staleness.** This is the clearest gap across all five.

7. **No project has build-target routing.** All five apply the same workflow regardless of whether you're building IoT firmware or a web app.

8. **No project has a self-improvement loop.** Patterns from execution don't feed back into the framework.

---

## Differentiation Pressure

WabbleSpec must be meaningfully different in at least 2-3 of these dimensions or it is redundant:

- spec-kit already owns "simple spec-driven development"
- GSD already owns "context-managed AI orchestration"
- OMC already owns "multi-agent skill routing"
- OpenSpec already owns "cross-repo spec exploration"
- agent-os already owns "standards injection"

WabbleSpec cannot win by doing all of these better. It must win by doing things none of them do.

---

## Feature Lessons

| Feature / Pattern | Seen In Which Projects | Lesson | Copy / Modify / Avoid / Ignore |
|---|---|---|---|
| Slash command entry points | All 5 | Non-negotiable UX pattern | Copy |
| Dotfolder framework isolation | All 5 | Non-negotiable | Copy |
| Phase artifacts (spec/plan/tasks per feature) | All 5 | Correct structure | Copy (WabbleSpec P1-P4 is this, more rigorously) |
| Verification phase separate from execution | GSD, spec-kit, OMC | Non-negotiable | Copy (already present) |
| Context window management / token density | GSD, OMC, agent-os | Critical | Modify (Economy already covers this, but "every word costs tokens" is better messaging) |
| Subagent routing by task complexity | GSD, OMC | Proven pattern | Modify (WabbleSpec ModelRouter + RuntimeProbe does this better as vendor-neutral) |
| Constitution / invariants | spec-kit, WabbleSpec | Good enforcement structure | Modify (WabbleSpec's behavioral invariants > spec-kit's technology preferences) |
| Research artifacts | spec-kit (research.md), GSD | Feature-level research better than session-level | Modify (ResearchLog is session-scoped, should also produce feature-scoped artifacts) |
| Standards extraction from codebase | agent-os | Discover before prescribe | Modify (add explicit Explore → standards extraction flow) |
| Named defect patterns | GSD (25+ patterns) | Error taxonomy should be this specific | Modify (WabbleSpec's 6 error types are too abstract) |
| Memory system with staleness | None | Genuine gap | Keep (unique differentiator) |
| Build-target routing (11 targets) | None | Genuine gap | Keep (unique differentiator) |
| Evidence provenance tracking | None | Genuine gap | Keep (unique differentiator) |
| Self-improvement/evolution loop | None | Genuine gap | Keep (unique differentiator, scope to v2+) |
| Health check / diagnostic command | OMC (/omc-doctor) | Essential for complex systems | Copy (WabbleSpec has no equivalent) |
| Skill scoping (project vs user level) | OMC | Good portability mechanism | Copy (WabbleSpec needs this distinction) |
| Multi-provider AI support (30+) | spec-kit, OpenSpec | Broad support = diluted focus | Avoid (vendor-neutral runtime via capability descriptors is better than multi-provider claiming) |
| "Fluid not rigid" philosophy | OpenSpec | Leads to unenforced specs | Avoid (12 invariants are the right counter-position) |
| 147+ workflow files | GSD | Navigation complexity without benefit | Avoid (55 modules is already too many for v1) |
| Hardcoded technology preferences as invariants | spec-kit | Framework opinions masquerading as principles | Avoid (WabbleSpec's invariants are behavioral constraints, not tech choices — keep it that way) |
| Workspace/cross-repo management | OpenSpec | In reimplementation crisis — unproven | Ignore for v1 |
| Advisory-only standards (no enforcement) | agent-os | Useless without Gate integration | Avoid |
| EARS syntax for requirements | WabbleSpec only | No evidence agents prefer EARS over Given/When/Then | Validate |
| TeamPlan / multi-agent coordination | WabbleSpec, OMC | OMC proves demand; WabbleSpec's scoped/bounded approach is better | Validate before building |
| Dream (background consolidation) | WabbleSpec only | Novel, no external validation | Validate first |
| Ensemble multi-lane execution | WabbleSpec only | Novel, no external validation | Validate first |
| Gate collapsing | WabbleSpec only | Practical escape hatch | Keep |

---

## Architecture Lessons

- **Directory layout as enforcement.** spec-kit's `.specify/`, GSD's `.planning/`, WabbleSpec's `.wabblespec/` — all use filesystem structure to make violation obvious. WabbleSpec's directory layout (I11 boundary) is the most rigorous and should stay.
- **skill-rules.json as activation contract** is WabbleSpec's strongest structural innovation. No competitor has a machine-readable activation/authority declaration per module. Worth keeping and explicitly documenting as a differentiator.
- **Progressive loading gates** (Recipe → Stage → Phase → Activation) have no direct analog in competitors. Genuinely novel. Worth keeping but must be demonstrably simpler to navigate than it looks on paper.
- **Receipt chain as operational artifacts** (I10) has no competitor analog. GSD uses STATE.md for continuity but not as a gating mechanism. Real differentiator.
- **Error taxonomy with typed routing** (6 types with defined routing actions) is better than GSD's named defect patterns approach. Both are good. WabbleSpec's is more machine-actionable; GSD's is more human-diagnostic. Both should exist.
- **Platform packages at L3** with consistent internal structure (SKILL.md, spec-template, dev/engineering/security submodules) is genuinely novel. No competitor has build-target-aware spec writing.

---

## UX Lessons

- **GSD's "complexity in the system, not workflow" is the right UX principle.** The user types 6 commands. The system does 147 workflows of orchestration. WabbleSpec must achieve the same — 9 layers of machinery behind simple entry points.
- **OpenSpec's lesson: every phase must answer "can the user complete the next natural step."** WabbleSpec's planning documents describe module internals but not user-visible flow. Fix this.
- **OMC's `/omc-doctor` is essential.** Any system with 9 layers needs a health-check entry point that surfaces state, errors, and configuration in plain language. WabbleSpec is missing this.
- **Skill scoping (project vs user) matters.** OMC's `.omc/skills/` (committed) vs. `~/.omc/skills/` (personal) solves a real organizational problem. WabbleSpec should formalize project-scoped vs. user-scoped rules.
- **The diagnostic transparency problem.** GSD's CONTEXT.md (predicate format, grep-auditable) is operational documentation for agents, not humans. WabbleSpec's `.wabblespec/meta.md` should be designed with the same machine-readable rigor.

---

## Failure Lessons

From these projects, spec-driven AI systems fail in these ways:

1. **Abstract internal machinery gets built before user-visible workflow.** OpenSpec built adapters, materializers, and target metadata before users could do anything visible. WabbleSpec is 55 modules deep without a single executed workflow.

2. **Evidence evaporates between sessions.** None of the competitors solved this. Every project restarts context from scratch each session. This is the concrete failure mode WabbleSpec's memory system addresses — but it must be the *first* thing that works, not module 47.

3. **Spec-to-execution gap.** spec-kit stops before touching code. GSD starts from execution without strong spec discipline. Neither solves the full chain reliably. WabbleSpec's receipt-gated pipeline is the theoretical answer but has no proof yet.

4. **Advisory specs are ignored.** agent-os standards are optional. spec-kit constitution is optional. Any spec system that doesn't gate execution will eventually be bypassed by the AI when the user is in a hurry.

5. **Self-referential complexity.** GSD's 147 workflows have their own operational bugs (changelog policy violations, Windows argv overflow, hook over-enforcement). A system complex enough to govern itself will have governance failures. WabbleSpec's L8 Evolution is specifically at risk here.

6. **Adoption abandonment after initial setup.** Most users set up spec-kit's constitution once and never update it. The system works for session one and degrades silently after. WabbleSpec's staleness enforcement (I9) directly addresses this but only if users understand why it matters.

---

## Anti-Bloat Lessons

Cut from WabbleSpec v1 because competitors already cover it or because complexity is unproven:

- **Cross-repo workspace management** — OpenSpec is failing here. Not worth entering.
- **30+ AI agent integrations** — spec-kit owns this. WabbleSpec doesn't need multi-platform support. Focus on Claude Code.
- **147 workflow files** — GSD already has this covered. WabbleSpec should not try to replicate GSD's breadth.
- **TeamPlan at L2** — OMC already does multi-agent orchestration. Validate single-agent execution first.
- **Ensemble multi-lane execution** — no proven demand. Build it only after ModelRouter works in production.
- **Dream background consolidation** — elegant concept, zero external validation. Build memory and staleness first, Dream later.
- **EntityGraph with 7 entity types and 7 relationship types** — over-specified before any data. Start with a simple entity list, expand from evidence.
- **Factory/Augment/Benchmark/Forge** full self-improvement chain — Instinct needs to run for months before Synth has anything to synthesize. The whole L8 chain is v3 territory, not v1.
- **Monitor (observability config generation)** — solved by every DevOps tool. Not a framework differentiator.
- **Polish module** — refinement passes on generated artifacts is a nice-to-have, not a foundation.

---

## Opportunity Gaps

None of the five reference projects solve:

1. **Memory with staleness tracking across sessions.** Competitors restart cold every session. Evidence gathered in research evaporates. No project has FRESH/AGING/STALE/EXPIRED tracking on any artifact.

2. **Build-target-aware spec writing.** No project adjusts spec templates, verification gates, or security requirements based on whether you're writing firmware, a library, or a mobile app.

3. **Provenance-tracked evidence with cascade invalidation.** No project tracks where spec claims came from or marks downstream specs NEEDS_REVERIFICATION when a source changes.

4. **A self-improvement loop grounded in execution evidence.** All five are static. Instinct/Synth/Forge (even a simple version) would be genuinely novel.

5. **Typed error routing with enforcement.** Competitors have named defect patterns (GSD) or error types (WabbleSpec) but no system routes errors by type to defined handlers automatically.

6. **Framework-product separation as an enforced boundary.** Others use conventions. WabbleSpec's I11 with machine-checked authority declarations is enforced, not advisory.

---

## My Possible Differentiation

### 1. Persistent Memory with Staleness Enforcement

**Why it matters:** Every competitor restarts cold. Research done in session 1 is invisible in session 10. AI agents confidently use stale information — wrong library versions, changed APIs, outdated architecture decisions — because nothing flags it.

**Who it helps:** Developers on projects that span weeks or months. Any project with external dependencies that change. Teams where multiple people interact with the same AI assistant across sessions.

**Why existing tools don't cover it:** Memory systems exist (file-based notes, CLAUDE.md, .clinerules) but none have staleness metadata, confidence scores, or cascade invalidation. The concept of evidence having an expiry is new to this space.

**Build difficulty:** Medium. Memory drawers + staleness metadata is 3-4 files of infrastructure. The hard part is making Guard actually enforce staleness violations before execution.

**How to validate:** Ship Memory + Guard staleness check + one STALENESS_VIOLATION error visible to the user. Does the user understand why it matters? Do they correct the stale evidence or bypass it?

---

### 2. Build-Target-Aware Spec Templates and Verification Gates

**Why it matters:** spec-kit's constitution is tech-agnostic but applies the same template to a CLI tool and an IoT device. The spec artifacts, verification gates, security requirements, and deployment concerns are completely different across build targets. Applying one template to all produces generic output.

**Who it helps:** Developers working on non-web targets (embedded, CLI, library, mobile, game) who currently get spec-kit templates that assume web/API. Any developer working across multiple target types in one organization.

**Why existing tools don't cover it:** spec-kit has 104K stars and one spec template. GSD has 147 workflows and no routing by target. The market is dominated by web-first assumptions.

**Build difficulty:** Medium-High. Need 11 platform packages with meaningful per-target content. Can start with 3-4 highest-demand targets (Web, API/Service, CLI, Mobile) and prove the value before building all 11.

**How to validate:** Ship Recipe detection + 3 platform packages. Ask: does the spec produced for a CLI look meaningfully different from the spec produced for an API? Does it catch platform-specific issues (CLI: startup time, exit codes; API: auth on every endpoint, rate limiting) that a generic template misses?

---

### 3. Receipt-Gated Execution Pipeline

**Why it matters:** spec-kit stops before execution. GSD executes without strong spec gates. OMC executes with agent routing but no spec anchor. No competitor enforces "Plan receipt must exist before Execute begins." Developers bypass planning phases when in a hurry and execution degrades silently.

**Who it helps:** Developers and teams who have experienced AI going off-spec mid-execution and producing code that technically works but violates the design intent. Teams with compliance requirements (regulated industries, security-sensitive code).

**Why existing tools don't cover it:** Pipeline enforcement requires storing receipts and checking them before proceeding. All competitors use advisory workflows. Nobody uses a receipt as an actual gate.

**Build difficulty:** Low-Medium. Receipts are JSON files. Guard is pattern matching against declared authority. The concept is simple; the discipline is hard.

**How to validate:** Show one case where the Guard receipt check prevents a module from proceeding with stale or missing inputs. Can users observe the gate firing? Do they understand why it's there?

---

### 4. Evidence Provenance with Cascade Invalidation

**Why it matters:** When an architecture decision changes (e.g., switching from REST to GraphQL), every downstream spec that assumed REST is silently wrong. No competitor detects this. Developers find out when generated code breaks production.

**Who it helps:** Any developer maintaining specs over time. Teams with changing external dependencies (API version bumps, library replacements, regulatory changes). Projects that use WabbleSpec for more than one feature cycle.

**Why existing tools don't cover it:** Nobody tracks citations between spec artifacts. The cascade problem is invisible until it's painful.

**Build difficulty:** Medium. Provenance records are metadata on drawers. Cascade computation is a simple graph traversal. The hard part is making sure spec artifacts actually cite their evidence sources (requires Specify to be disciplined about sourcing).

**How to validate:** Introduce a BREAKING change to one spec. Does the system correctly flag all specs that cited the changed artifact as NEEDS_REVERIFICATION? Do those flags help the developer, or are they noise?

---

### 5. Formal Invariants as Enforcement, Not Guidelines

**Why it matters:** spec-kit's constitution is nine technology preferences. GSD's CONTEXT.md is operational documentation. Neither can be machine-checked. WabbleSpec's 12 invariants are behavioral constraints with defined enforcement mechanisms (Guard checks I9 staleness, I10 receipts, I11 boundaries before every wave). This is a different category of structural guarantees.

**Why existing tools don't cover it:** Nobody else has tried to make the spec framework itself invariant-enforced.

**Who it helps:** Teams who have been burned by AI agents drifting off spec or making undeclared scope changes. Any use case requiring auditability (compliance, regulated industries, team environments).

**Build difficulty:** Medium. The invariants are already specified. The work is making Guard enforce them mechanically, not via prompt reasoning.

**How to validate:** Demonstrate one invariant violation being caught (e.g., Apply attempting to write a framework file → SPEC_VIOLATION). Is the error message actionable? Does the developer understand what was enforced and why?

---

## Brutal Reality Check

**1. Is my project likely redundant?**

Partially. The basic spec-driven workflow (specify → plan → execute → verify) is solved by spec-kit and GSD. If WabbleSpec's only value is "better organized spec writing," it is redundant against GitHub-owned spec-kit with 104K stars. WabbleSpec is NOT redundant on memory/staleness, build-target routing, receipt gating, and provenance — those are real gaps none of the five address.

**2. Is my project solving a real missing gap?**

Yes, on four dimensions: persistent memory with staleness enforcement, build-target-aware spec writing, receipt-gated execution pipeline, and evidence provenance with cascade invalidation. These gaps exist and cause real failures. None of the reference projects close them.

**3. Am I competing with mature tools too early?**

Yes, on the basic spec workflow. spec-kit has 104K stars, GitHub backing, and Python. GSD has 63K stars and 147 workflows. WabbleSpec should not position itself as "better spec-driven development" — it will lose that fight. It should position on the memory+staleness+build-target+provenance dimensions that the mature tools explicitly don't do.

**4. Am I building a worse version of something that already exists?**

WabbleSpec's L1 Spec Core + L2 Orchestration is a more complex version of what GSD and spec-kit already do, with no adoption yet. WabbleSpec's L5 Memory, L3 Platform routing, I10 receipts, and L8 Evolution (in a simple form) are genuinely novel. The risk is spending all implementation effort on layers 1-2 (crowded market) before reaching layers 3, 5, and 8 (differentiators).

**5. What must my spec prove to justify existing?**

WabbleSpec must demonstrate in a working product that: (a) evidence staleness is a real problem AI coding sessions face and staleness enforcement catches it, (b) build-target routing produces meaningfully different and better spec artifacts than generic templates, and (c) receipt-gated execution prevents a class of failures that advisory workflows miss. All three must be demonstrable within the first 10 modules, not after all 55 are built.

---

## Required Spec Changes

**Keep:**
- 12 invariants (behavioral constraints, not technology preferences — correct and differentiated)
- I9 evidence expiry + 6 staleness states — genuinely novel, no competitor has this
- I10 receipts as operational artifacts — genuinely novel enforcement mechanism
- I11 framework-product separation — stricter than any competitor, keep it
- skill-rules.json activation + authority declaration — unique and powerful
- 11 build targets as concept — correct differentiation
- L5 Memory layer (Memory, MemorySearch, Provenance, Forget) — core differentiator
- EARS syntax in Specify — keep but validate against Given/When/Then preference
- Four loading gates (Recipe/Stage/Phase/Activation) — clean architecture, keep
- Vendor-neutral runtime via capability descriptors — genuinely better than OMC's model-name routing

**Cut (from v1 scope):**
- TeamPlan — prove single-agent execution first, multi-agent later
- Ensemble — prove ModelRouter first
- Dream — prove Memory + staleness first, background consolidation is v2
- EntityGraph (full 7-type/7-relationship version) — start with a simple entity list, expand from data
- L8 Evolution full chain (Synth → Blueprint → Factory → Augment → Benchmark → Forge) — v3
- Polish module — nice-to-have, not foundation
- Monitor module — solved by DevOps tools, not a framework differentiator
- Homowabian ultra register — implement lite/full/normal first, ultra is marginal
- ResearchLog session-level tracking — implement feature-level research.md first (spec-kit pattern is better)
- Retro module — valuable but not core to initial proof

**Merge:**
- ResearchLog + feature-level research.md → single Research artifact per feature/phase (learn from spec-kit)
- Economy + Homowabian can share one module until proven they need separation (current separation is theoretically correct but unvalidated)
- MemoryMine can be a mode of MemorySearch rather than a separate module until scale justifies it

**Rewrite:**
- Planning documents from internal-machinery-first to user-visible-workflow-first. Every module spec should answer "what does the user experience when this module fires" before it answers "what are the internal processing steps."
- Error taxonomy: WabbleSpec's 6 types are abstract. Expand to GSD-style named defect patterns with symptom, detection method, fix-forward path, and test anchor. Keep the 6 types as routing categories but make the defect patterns specific.
- Module importance ranking: current Tier 1-5 classification should be reordered to put Memory layer (L5) as Tier 1 alongside L0/L2, because memory is the primary differentiator. Currently Memory is buried below the standard spec/execute flow.

**Validate before building:**
- EARS syntax preference over Given/When/Then — no external evidence that agents prefer EARS. Run a comparison before committing all spec templates to it.
- Dream background consolidation — validate the problem (memory drawer accumulation causing navigation friction) before building the solution.
- EntityGraph node/edge types — start with file + module + concept (3 types), expand from actual extraction data.
- Gate collapsing — validate that collapse-eligible tasks exist in real workflows before optimizing for them.

**Research more:**
- How GSD's subagent-per-phase approach actually interacts with context rot in Claude Code's current architecture. WabbleSpec's context placement rules (Economy) and subagent routing (ModelRouter) assume the same problem exists — verify before treating it as solved.
- Whether BREAKING/ADDITIVE/COSMETIC delta classification is actionable in practice, or whether all non-trivial changes end up classified as BREAKING by a cautious agent.
- Whether `skill-rules.json` activation patterns can actually be matched deterministically by Claude Code, or whether they require a loader/runtime that doesn't exist yet.

---

## Final Verdict

**SHRINK**

The reference projects prove WabbleSpec's core ideas are sound — memory/staleness, build-target routing, receipt gating, and provenance are real gaps that 280,000 combined stars have not closed. The idea justifies existing.

But the scope is 3x too large. 55 modules and 9 layers before a single user-visible workflow exists is the exact failure mode OpenSpec demonstrated and then had to rewrite. The differentiating features are buried in layers 3, 5, and 8 — which are unlikely to be reached if all v1 effort goes into reproducing what spec-kit and GSD already do in layers 0-2.

**WabbleSpec v1 scope should be: Recipe + Memory + Guard + Specify (with build-target templates for 3 targets) + Executor + Verifier.** That is the minimum viable system that proves the four differentiating claims. Everything else comes after those are validated.
