# Project Execution Judge: WabbleSpec v6.1

Date: 2026-05-21

Verdict target: whether this idea is worth building at all, not whether the documents are internally elaborate.

## Evidence Read

- Local spec surface: 74 Markdown files, 15,654 lines, 112,960 words.
- No detected implementation files under this project root: no `.ps1`, `.js`, `.ts`, `.py`, `.json`, or schema files were returned by recursive file search.
- No `.wabblespec/` directory exists, despite specs saying that framework control plane is the canonical runtime space.
- No `canonical/` directory exists, despite `planning/00-INDEX.md` referencing `../canonical/`.
- The planning docs say v6 was treated as "AI-generated hallucination" and v5.3 is base: `planning/00-INDEX.md:23`.
- The project claims complete lifecycle scope, vendor neutrality, zero dependencies, no MCP: `planning/02-ARCHITECTURE.md:7`.
- The core doc still says the framework runs within Claude Code Terminal: `WabbleSpec v6.1 — Core.md:17`.
- The manual says approximately 145 composable modules: `WabbleSpec v6.1 — Manual.md:9`.
- The module plan says per-module planning is complete: `planning/modules/PROGRESS.md:30`.
- The module plan also says planning docs live in `.wabblespec/plans/v61/`, but the actual docs live in `planning/`: `planning/modules/PROGRESS.md:51`.

External market evidence checked:

- Claude Code already has project and personal `SKILL.md` skills with supporting files, auto discovery, and command invocation: https://code.claude.com/docs/en/skills
- OpenAI Agents SDK already covers agents, tool execution, approvals, state, handoffs, guardrails, traces, evals, and hosted workflow paths: https://developers.openai.com/api/docs/guides/agents
- LangGraph already covers durable execution, persistence, human-in-the-loop, memory, replay constraints, and checkpointing: https://docs.langchain.com/oss/python/langgraph/durable-execution
- CrewAI already packages multi-agent crews, flows, memory, knowledge, guardrails, human-in-the-loop triggers, and observability: https://docs.crewai.com/
- Continue already supports local and hub rules, Markdown/YAML rule files, project-specific rules, glob-triggered rules, and system-message customization: https://docs.continue.dev/customize/deep-dives/rules
- Cursor already has project rules and context features: https://docs.cursor.com/en/context

## Problem

The project claims to be a complete software creation system before it proves one narrow workflow is better.

## Wrong Assumption

You seem to assume breadth creates value: 9 layers, 11 platform targets, 12 invariants, 14 feature groups, 145-ish modules, complete lifecycle coverage.

## Why It May Be False

Breadth is cheap in Markdown and expensive in execution. A user does not care that a framework can theoretically route Web, Game, IoT, Mobile, Desktop, CLI, Library, Data, Extension, API, and AI work. They care whether it reduces failed builds, bad specs, context loss, or verification lies on the task in front of them.

The current plan is a taxonomy generator. It has not shown that the taxonomy improves outcomes.

## Missing Evidence

- No real users.
- No before/after benchmark against plain Codex, Claude Code skills, Cursor rules, or AGENTS.md.
- No completed task run through the full process.
- No measured reduction in rework, bug rate, missing tests, or hallucinated completion.

## Consequence If Ignored

You will build an instruction cathedral that is slower than direct agent use, harder to maintain than project rules, and too abstract for users to trust.

## Validation Test

Pick 10 real coding tasks from one repo. Run each with baseline agent instructions and with a minimal WabbleSpec slice. Measure pass rate, time, user interventions, test failures, and correctness defects.

## Action

Pivot. Stop claiming complete lifecycle scope. Prove one lifecycle slice.

## Problem

The spec confuses planning completeness with product evidence.

## Wrong Assumption

You seem to assume "per-module planning complete" means the project has become more buildable.

## Why It May Be False

Planning completion only proves you can produce more plans. It does not prove any module boundary is correct, any activation rule works, any receipt improves behavior, or any user will tolerate the process.

The project has 112,960 words of spec and no implementation artifacts. That is not maturity. It is inventory inflation.

## Missing Evidence

- No executable router.
- No schema files despite schema-heavy claims.
- No receipt validator.
- No runtime probe.
- No generated `.wabblespec/` control plane.
- No single golden path demo.

## Consequence If Ignored

You will keep mistaking document mass for progress. The project will feel "almost ready" forever because every missing proof can be answered with another module plan.

## Validation Test

Implement only `Recipe -> ScopeFrame -> Specify -> Verifier -> Archive` for CLI projects. If that cannot run end-to-end in one repository, the larger plan is fiction.

## Action

Delete most planning work from the build path. Keep it as archived research, not as implementation scope.

## Problem

"Vendor-neutral runtime" is contradicted by the current canonical prose.

## Wrong Assumption

You seem to assume vendor neutrality can be declared while the system remains shaped around Claude Code Terminal.

## Why It May Be False

The planning docs say no hardcoded runtime names. The core doc says WabbleSpec runs within Claude Code Terminal. The manual says the same. That is not neutral. It is Claude-first with neutral vocabulary.

True runtime neutrality requires adapters, capability discovery, execution semantics, filesystem permissions, subagent differences, tool differences, and state behavior per runtime. The spec mostly renames those differences as "capability descriptors."

## Missing Evidence

- No Codex adapter.
- No Claude adapter.
- No Gemini adapter.
- No compatibility matrix.
- No failing cases where runtime differences change behavior.
- No proof that `skill-rules.json` can be consumed across tools.

## Consequence If Ignored

The project will break the moment it leaves the runtime it was unconsciously designed around.

## Validation Test

Run the same minimal WabbleSpec workflow in Claude Code, Codex, and one non-Claude editor agent. Record what cannot be represented identically.

## Action

Simplify. Build one runtime first. Add neutrality only after adapter evidence exists.

## Problem

The "zero external dependencies / no MCP" claim undercuts the product.

## Wrong Assumption

You seem to assume local-first purity is automatically a strength.

## Why It May Be False

For a software creation system, useful evidence often comes from live tools: tests, browser checks, package registries, docs, issue trackers, CI, git hosting, telemetry, deployment state, and real runtime logs. A system that refuses integrations can only pretend to verify many claims.

Local-first is useful as a storage constraint. It is weak as an execution ideology.

## Missing Evidence

- No proof plain files can handle high-volume receipts without becoming noise.
- No query performance test over memory drawers.
- No stale evidence invalidation test.
- No integration story for CI, browser, package manager, docs, or hosted issue systems.

## Consequence If Ignored

Verification will degrade into local paperwork. The system will record that it verified, but the actual proof will remain outside the system.

## Validation Test

Try to verify a real web app task: install, run tests, open browser, inspect UI, check accessibility, validate build, record receipt. If "no external dependencies" blocks proof, the constraint is wrong.

## Action

Pivot from "no external dependencies" to "local-first storage with optional evidence adapters."

## Problem

Receipts are fake rigor until they are machine-checked.

## Wrong Assumption

You seem to assume writing receipts prevents false completion.

## Why It May Be False

Markdown receipts can become ceremonial checkboxes. If the system does not mechanically verify that receipts exist, schemas parse, commands ran, outputs match, and downstream phases consumed upstream evidence, receipts are just longer status updates.

The spec says every arrow writes a receipt. That multiplies artifacts before proving any artifact changes behavior.

## Missing Evidence

- No receipt schema implementation.
- No receipt parser.
- No receipt chain validator.
- No proof that missing receipts block execution.
- No tamper or contradiction detection.

## Consequence If Ignored

The system will generate plausible audit trails for bad work. That is worse than no audit trail because it creates false confidence.

## Validation Test

Create a broken execution with missing tests, stale evidence, and skipped verification. The system must block completion automatically, not by prose instruction.

## Action

Prototype. Build receipt validation before any module expansion.

## Problem

The memory system is overdesigned before the project has memory worth managing.

## Wrong Assumption

You seem to assume Evidence Expiry, Dream, EntityGraph, MemoryMine, Provenance, Forget, and staleness propagation are core.

## Why It May Be False

Most early users will not have enough high-value evidence to justify a memory subsystem. They need current repo state, current tests, current docs, and task history. A graph, dream phase, decay model, contradiction ledger, closets, drawers, provenance, and mining pipeline are maintenance load before there is signal.

## Missing Evidence

- No corpus of real receipts.
- No stale evidence dataset.
- No query success metric.
- No comparison against simple `rg`, AGENTS.md, project rules, or a compact `CONTEXT.md`.
- No proof that entity extraction improves task success.

## Consequence If Ignored

You will spend months building a knowledge-management product inside an agent workflow product, and neither will be good enough.

## Validation Test

Take 50 real prior task artifacts. Compare simple full-text search vs proposed MemorySearch/EntityGraph on retrieval accuracy and time-to-answer.

## Action

Delete for MVP. Keep only append-only receipts plus a flat index.

## Problem

The self-improvement pipeline is a golden egg fantasy.

## Wrong Assumption

You seem to assume the system can safely learn from itself, propose improvements, benchmark them, and promote them through Forge.

## Why It May Be False

Self-improving agent frameworks are not impossible, but they are easy to fake. Without trusted eval datasets, deterministic replay, strong baselines, and adversarial regression tests, the system will promote changes that look good in its own paperwork.

The proposed thresholds (`count >= 3`, confidence >= 0.7, count >= 5, 80% parity, 60% improvement) are invented. They are not validated.

## Missing Evidence

- No baseline benchmark suite.
- No real improvement candidates.
- No regression corpus.
- No rollback proof.
- No independent evaluator.
- No metric definition for "60% improvement signal."

## Consequence If Ignored

You will build an auto-rationalizing system that converts repeated mistakes into "patterns."

## Validation Test

Before building Forge, manually run 20 proposed rule changes against a fixed benchmark. If human-reviewed improvements do not reliably beat baseline, automation is unjustified.

## Action

Delete from MVP. Revisit only after 100+ real executions and a benchmark suite.

## Problem

The architecture copies existing tools without enough differentiation.

## Wrong Assumption

You seem to assume "local-first, model-neutral, receipt-backed" is enough to distinguish the product.

## Why It May Be False

The market already has:

- Skills and supporting files in Claude Code.
- Project rules in Cursor and Continue.
- AGENTS.md-style repository instructions.
- OpenAI Agents SDK with handoffs, guardrails, approvals, tracing, evals, and state.
- LangGraph durable execution, memory, interrupts, and checkpointing.
- CrewAI crews, flows, guardrails, memory, human-in-the-loop, and observability.

WabbleSpec currently looks like a grand unification document, not a sharper tool.

## Missing Evidence

- No competitor matrix.
- No migration story from existing project rules or skills.
- No user segment that existing tools fail.
- No task where WabbleSpec wins because of a unique mechanism.

## Consequence If Ignored

Potential users will ask why they should learn 145 modules instead of adding 5 project rules and a verification checklist to their current agent.

## Validation Test

For 5 representative tasks, implement the minimal equivalent in Claude Skills, Cursor rules, Continue rules, LangGraph, and WabbleSpec MVP. Show where WabbleSpec is faster, safer, or more accurate.

## Action

Research and differentiate. If no unique win appears, pivot to a plugin for an existing ecosystem.

## Problem

The feature list is bloated with internal machinery users likely will not care about.

## Wrong Assumption

You seem to assume users value visible architecture nouns: Recipe, ScopeFrame, Dream, Forge, Homowabian, EntityGraph, MemoryMine, Ensemble, TeamPlan, Instinct, Synth, Blueprint, Augment.

## Why It May Be False

Users value outcomes: fewer broken changes, less repeated context, fewer fake done claims, faster implementation, better tests. Internal names are cost unless they map directly to visible workflow control.

Several names sound like worldbuilding. They may help you think, but they make adoption harder.

## Missing Evidence

- No usability test of the vocabulary.
- No onboarding test.
- No time-to-first-success metric.
- No proof that users understand module roles.

## Consequence If Ignored

Users will bounce before reaching the alleged benefits. Maintainers will spend time explaining the system instead of improving it.

## Validation Test

Give the docs to 5 developers. Ask them to run one task without your help. Track where they stall and which concepts they ignore.

## Action

Delete or hide vocabulary. Expose only commands, inputs, outputs, and proof.

## Problem

The platform matrix is premature.

## Wrong Assumption

You seem to assume target-first routing must cover 11 targets from the start.

## Why It May Be False

Platform routing is useful only if each target has real verification and implementation patterns. Covering IoT, Game, Data/Pipeline, Extension, Mobile, Desktop, Web, API, CLI, Library, and AI requires broad domain expertise and test infrastructure.

The spec lists targets but does not prove target-specific value.

## Missing Evidence

- No platform-specific runnable examples.
- No target-specific acceptance tests.
- No proof that target detection works.
- No target where WabbleSpec beats a simpler project template.

## Consequence If Ignored

The platform packages become shallow checklists. Shallow checklists are worse than no specialization because they create false coverage.

## Validation Test

Choose one target only. Build 3 real tasks end-to-end. If target routing materially improves outcomes, then add a second target.

## Action

Shrink to one target. CLI or Web is the least bad start.

## Problem

The spec has unresolved path and authority contradictions.

## Wrong Assumption

You seem to assume the docs are coherent enough to implement from.

## Why It May Be False

The docs reference `.wabblespec/plans/v61/` but the project has `planning/`. They reference `../canonical/`, but no `canonical/` exists. They claim framework-product separation, but no actual control plane exists. They claim vendor neutrality, while core/manual prose says Claude Code Terminal.

These are not cosmetic. They show the spec cannot yet serve as a source of truth.

## Missing Evidence

- No path contract validator.
- No doc consistency checker.
- No source-of-truth map.
- No generated structure matching the plan.

## Consequence If Ignored

Implementation will inherit contradictions and then patch around them. That creates a brittle generator, not a system.

## Validation Test

Write a linter that checks every referenced path, runtime claim, module name, and required artifact. Run it on the current docs. Fix all failures before implementation.

## Action

Validate and simplify. Do not implement from contradictory docs.

## Problem

The proposed architecture is too process-heavy for typical coding tasks.

## Wrong Assumption

You seem to assume Research -> Plan -> Execute with receipts between every phase is acceptable overhead.

## Why It May Be False

Most coding tasks are small. If every non-trivial task requires staged specs, phase receipts, runtime receipts, verification receipts, archive receipts, possible reviewer receipts, and memory writes, users will bypass the system.

Even the spec admits gate collapsing, which is a sign the default process is too heavy.

## Missing Evidence

- No latency budget.
- No token budget.
- No artifact-count budget.
- No "small task" benchmark.
- No proof that users accept the friction.

## Consequence If Ignored

The system becomes a compliance machine for solo development. Compliance machines get ignored unless they are mandatory or obviously valuable.

## Validation Test

Run a 20-minute bugfix through the full process. If the process produces more artifacts than useful decisions, the flow is wrong.

## Action

Shrink. Default to one-page task card + proof log. Add stages only when risk demands them.

## Problem

The research/thesis value is undercut by lack of falsifiability.

## Wrong Assumption

You seem to assume a coherent framework thesis is enough.

## Why It May Be False

A real thesis needs falsifiable claims. Current claims are mostly architectural intentions: "evidence-based," "vendor-neutral," "target-first," "progressive loading," "quality gates." These are not research contributions unless measured against baselines.

## Missing Evidence

- No explicit hypotheses.
- No baseline selection.
- No benchmark tasks.
- No success thresholds.
- No failure thresholds.
- No ablation plan.

## Consequence If Ignored

The project will be neither product nor research. It will be a belief system written as architecture.

## Validation Test

Define 3 falsifiable claims. Example: "Receipt-gated execution reduces false completion claims by 50% on 30 coding tasks vs baseline AGENTS.md." If you cannot measure it, it is not a thesis.

## Action

Research before building. Convert claims into experiments.

## Problem

The user demand case is absent.

## Wrong Assumption

You seem to assume your own pain with agent drift generalizes into a product.

## Why It May Be False

Your pain may be real and still not be a market. Users may prefer rough agent output plus manual review over a large framework that asks them to adopt new vocabulary, folders, receipts, phases, and module rules.

## Missing Evidence

- No identified buyer/user.
- No interviews.
- No pricing or willingness-to-use signal.
- No adoption channel.
- No comparison against "just use Claude Skills / Cursor rules / AGENTS.md."

## Consequence If Ignored

You will build a tool for yourself while imagining an audience. That is fine if declared. It is fatal if you think this is a product.

## Validation Test

Interview 10 target users. Do not pitch the solution. Ask how they currently manage AI coding instructions, verification, and repeated context. Measure whether they already pay time/money for the pain.

## Action

Validate demand. If this is personal infrastructure, say so and cut product ambitions.

## Problem

The "golden egg" fantasy is that enough orchestration creates reliability.

## Wrong Assumption

You seem to assume more gates, modules, receipts, reviewers, and memory layers will make agents reliably build software.

## Why It May Be False

Reliability comes from executable checks, deterministic tools, narrow scope, real tests, and short feedback loops. Orchestration can help. It can also amplify confusion. Without implementation, the current plan mainly orchestrates abstractions.

## Missing Evidence

- No end-to-end reliable build.
- No failure-mode corpus.
- No test harness.
- No repeated task success record.
- No evidence that complexity buys reliability.

## Consequence If Ignored

The project becomes a golden egg hoax: an elaborate machine that promises higher-quality software but mostly lays more documents.

## Validation Test

Force the system to build one boring thing correctly, repeatedly, from a short prompt. If it cannot produce, test, and document a small CLI or web app better than baseline, stop.

## Action

Prototype or kill.

## Answers To The 15 Questions

1. Probably wrong assumptions: users want a full lifecycle framework; local-first/no-MCP is enough; receipts create proof; vendor-neutral can be abstracted before adapters; memory graph is core; all platforms need first-class support.
2. Smart-sounding but weak: evidence expiry, Dream, Forge, Homowabian, Ensemble, runtime descriptors, receipt chains. They are strong only when executable.
3. Fake innovation: renamed project rules, renamed workflow orchestration, renamed agent handoffs, renamed audit logs, renamed memory/indexing.
4. Feature bloat: L8 Evolution, L5 memory graph stack, L6 expression stack, 11 platform targets, delivery/deploy/release/monitor modules, all P15 carry-forward modules.
5. Users likely will not care about: module names, layer taxonomy, receipt purity, voice register theory, self-improvement pipeline, platform coverage they are not using.
6. Technically risky: runtime neutrality, cross-tool skill compatibility, receipt enforcement, staleness propagation, self-modification, multi-agent coordination, target detection.
7. Vague or not implementable yet: "zero active-session cost," "60% improvement signal," "vendor-neutral capability descriptor," "no stale evidence used," "complete lifecycle," "quality over volume" without scoring.
8. Copied without enough difference: skills/rules from Claude/Cursor/Continue, agent handoffs and guardrails from OpenAI Agents SDK, durable workflows from LangGraph, crews/flows from CrewAI, AGENTS.md project instruction patterns.
9. Delete before build: Evolution pipeline, Dream, EntityGraph, MemoryMine, Forget, Homowabian, Ensemble, TeamPlan, Deploy/Package/Release/Monitor, 10 of 11 platform packages.
10. Validate before code: one target, one runtime, one workflow, one receipt validator, one measurable baseline comparison, one real user pain.
11. Missing evidence: users, competitor analysis, benchmarks, implementation, schemas, adapters, runtime demos, path consistency, maintenance cost, willingness to adopt.
12. Not worth building if: baseline agents with 3-5 rules perform similarly; users reject artifact overhead; receipt validator cannot block false claims; one-target MVP fails; no one wants to use it outside you.
13. Harshest interpretation: this is a self-reinforcing planning artifact that launders anxiety about AI unreliability into a large control-plane fantasy.
14. Real problem or decoration: real problem, decorated solution. The problem is false completion and context drift. The current answer decorates it with too many subsystems.
15. Real or golden egg hoax: current plan is a golden egg hoax until a small executable slice beats baseline on real tasks.

## Brutal Cut List

Remove from MVP:

- 10 of 11 platform targets.
- L8 Evolution: Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge.
- Dream.
- EntityGraph.
- MemoryMine.
- Forget.
- Homowabian.
- Polish.
- ResearchLog.
- Document.
- Ensemble.
- TeamPlan.
- Deploy.
- Package.
- Release.
- Monitor.
- Product module.
- Feedback module.
- Retro module.
- Scaffold beyond one target template.
- Full three-phase process for small tasks.
- All "complete software lifecycle" language.
- All claims of vendor neutrality until two adapters exist.
- All claims of zero dependencies as a product virtue.

Keep only:

- One target.
- One runtime.
- Recipe / target detection.
- ScopeFrame.
- Specify.
- Executor/Apply collapsed into one implementation path.
- Verifier.
- Archive as proof log.
- Minimal flat Memory only if needed.
- Receipt schema and validator.

## MVP Reality Check

Smallest version that can prove the idea:

Build a local-first "verified agent task runner" for one runtime and one target.

Target: CLI or Web, not all platforms.

Runtime: Codex or Claude, not vendor-neutral.

Workflow:

1. User gives task.
2. System writes a one-page task card: goal, non-goals, assumptions, verification.
3. Agent executes.
4. System runs declared checks.
5. System writes one machine-parseable receipt.
6. System blocks "done" if checks did not run or failed.
7. System stores receipt in a flat index.

Success condition:

On 30 real tasks, this MVP must beat baseline agent instructions by a meaningful margin:

- Fewer false completion claims.
- Fewer missed tests.
- Equal or lower total time for small tasks, or clearly better correctness for larger tasks.
- Lower rework after human review.

If it cannot beat baseline, the larger WabbleSpec should not be built.

## Validation Plan

1. Baseline benchmark: 30 real tasks using plain AGENTS.md or Claude/Cursor rules. Record pass/fail, time, test status, false claims.
2. MVP benchmark: same tasks using the smallest WabbleSpec slice. Same metrics.
3. Receipt enforcement test: deliberately skip tests and see whether the system blocks completion automatically.
4. Path consistency linter: check every referenced path and required artifact in current docs.
5. User workflow test: give the MVP to 5 developers and watch whether they can complete one task without explanation.
6. Vocabulary test: ask users to explain Recipe, ScopeFrame, Verifier, Archive. Delete any term they cannot use correctly.
7. Competitor replication test: implement the same workflow using Claude Skills, Cursor/Continue rules, and a small script. WabbleSpec must still win.
8. Maintenance test: change one rule and measure how many docs/artifacts must be updated.
9. Runtime portability test: after one runtime works, port to a second runtime and record adapter breakage.
10. Cost/friction test: measure artifacts per task. If a small task creates more than 2 artifacts, reduce scope.

## Kill Criteria

Stop working on the current idea if any of these happen:

- 30-task benchmark shows no meaningful improvement over simple project rules.
- Receipt validation cannot reliably block false completion.
- Users reject the workflow as too heavy after one task.
- One-target MVP takes more than 2 weeks before end-to-end proof.
- Runtime adapter work consumes more time than product behavior.
- The project needs more than 5 exposed concepts for first use.
- Maintenance requires updating more docs than code.
- You cannot name a specific user segment that wants this.
- You cannot produce a real task receipt that a skeptical engineer accepts as proof.
- The next impulse is to add another module instead of deleting scope.

## Final Verdict

PIVOT.

The problem is real: agentic coding work suffers from context drift, fake completion, weak verification, and repeated instruction loss.

The current project is not the right build. It is too broad, too abstract, too derivative, and too unvalidated. It reads like a framework trying to become an operating system before it proves it can run one command.

Build the smallest proof engine first: one target, one runtime, one task card, one receipt, one validator, one benchmark. Everything else is golden egg decoration until that wins.
