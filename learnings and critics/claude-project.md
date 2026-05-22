# WabbleSpec v6.1 — Project Execution Critique

**Date:** 2026-05-21  
**Version reviewed:** 6.1.0  
**Scope:** All planning documents, Core.md, Manual.md, AI.md, 05-MODULE-IMPORTANCE.md, 01-INVARIANTS.md

---

## Summary Judgment (read before details)

WabbleSpec is an elaborate behavioral spec telling an LLM how to behave. It has no implementation. Its verification system is self-attestation. Its vendor-neutral runtime claim is false given its deployment target. Its memory system is markdown files. Its evolution pipeline is speculative. Competing tools are already installed and running in this project. The version number (6.1) implies maturity that does not exist.

---

## Problem 1: The Execution Model Does Not Exist

### Problem
WabbleSpec describes ~145 modules with SKILL.md files, skill-rules.json activation patterns, receipt schemas, and evaluation suites. None of these files exist. The planning documents describe what these files will contain, not the files themselves.

### Wrong Assumption
"v6.1" implies a working framework being improved. The version number signals maturity.

### Why It May Be False
This is v6.1 of a spec. The index explicitly states v6 was treated as "AI-generated hallucination" and v5.3 is "ground truth." There is no confirmation that v5.3 actually ran reliably. Version numbers here track planning sessions, not shipped software. Calling it 6.1 is false advertising to yourself.

### Missing Evidence
- Any working SKILL.md file from v5.3 or earlier
- A session log showing the framework executing without deviating from spec
- A single receipt chain from a completed project built with WabbleSpec

### Consequence If Ignored
You will plan v7 before v6.1 is built. The planning-to-implementation ratio will remain infinite.

### Validation Test
Pick the five Tier 1 modules. Build them. Run one full project through them end-to-end. Document how many times Claude deviated from the spec. If deviation rate is above 20%, the framework premise is broken.

### Action
**Validate.** No more planning until something runs.

---

## Problem 2: The Receipt Chain Is Self-Attestation Theater

### Problem
Receipts are written by Claude. Verification is done by Verifier, which is Claude. Guard checks invariants — Guard is Claude. The entire "machine-checked" pipeline is one LLM writing documents about what it did, then checking those documents by reading them.

### Wrong Assumption
"Receipts gate downstream behavior" implies an external enforcer. The spec language — "machine-checked," "cannot be bypassed," "HARD error" — implies there is a system enforcing these rules.

### Why It May Be False
There is no system. There is no runtime engine. There is no code that reads a receipt and blocks execution. There is only Claude, which is instructed to behave as if these receipts exist and matter. Claude regularly deviates from complex multi-step behavioral instructions, especially across long sessions. "Guard cannot be bypassed" is a behavioral instruction to an LLM that has no bypass protection mechanism.

### Missing Evidence
- A single case where Claude refused to proceed because a receipt was missing, without being explicitly prompted to check
- Any mechanism that enforces receipt presence outside of Claude's own compliance with its own instructions
- Benchmark data on Claude's receipt-chain compliance rate over 10+ wave sessions

### Consequence If Ignored
You build 145 modules of process theater. Developers will feel disciplined but Claude will still hallucinate completions, skip steps it finds redundant, and write PASS receipts for work it hasn't fully done.

### Validation Test
Run a 5-wave session. Deliberately skip writing one receipt mid-session. Do not tell Claude you skipped it. See if it detects and blocks. If it proceeds without noticing, the receipt chain enforcement is broken by design.

### Action
**Pivot.** The enforcement mechanism needs to be something outside the LLM — a hook, a script, a pre-tool-use check. Without that, receipts are documentation, not gates.

---

## Problem 3: Vendor-Neutral Runtime Solves a Non-Existent Problem

### Problem
Invariant I6 and the entire RuntimeProbe/ModelRouter/capability-descriptor architecture exists to avoid hardcoding model names. The spec states "No model name, no provider name, and no platform-specific API appears in any framework file."

### Wrong Assumption
WabbleSpec will run on multiple LLM providers and needs to abstract away provider identity.

### Why It May Be False
The spec explicitly states "WabbleSpec runs within Claude Code Terminal." Claude Code Terminal runs Claude (Anthropic). This is not an abstraction layer for a multi-provider system — it is instructions for one specific provider's product. The capability descriptors (code-generation, analysis, synthesis, etc.) will always resolve to Claude. ModelRouter will always route to Claude. The vendor-neutral architecture is solving a problem that does not exist in this deployment context.

### Missing Evidence
- Any deployment scenario where WabbleSpec runs on a non-Claude LLM
- Any plan for WabbleSpec to ship as a product that users install on different providers
- Evidence that the capability descriptor abstraction adds value over just calling Claude directly

### Consequence If Ignored
Significant complexity (RuntimeProbe, ModelRouter, Ensemble, capability descriptors throughout) adds implementation cost and cognitive load with zero practical benefit. You are building an abstraction for one thing.

### Validation Test
Name one concrete scenario where a WabbleSpec user routes a task to a non-Claude model through ModelRouter. If you cannot name one, delete the abstraction.

### Action
**Delete** RuntimeProbe, ModelRouter capability-descriptor layer, and vendor-neutral language. Call it Claude. Ship faster.

---

## Problem 4: The Memory System Is Markdown Files With No Enforcement

### Problem
L5 describes a sophisticated memory system: staleness states, provenance ledger, entity graph with nodes.json and edges.json, confidence scores, cascade reverification, EMA decay. This is described with the rigor of a database design.

### Wrong Assumption
This is a reliable evidence store with enforced staleness tracking.

### Why It May Be False
Every component of this system is a markdown or JSON file that Claude is supposed to read, maintain, and enforce. There is no database. There are no atomic writes. There is no process watching staleness thresholds. Dream "never runs during active execution" — but Dream is not a daemon; it runs when Claude is asked to run it. EntityGraph uses "deterministic pattern matching" for entity extraction — but the extraction is done by Claude in-context, which is not deterministic. STALENESS_VIOLATION errors are emitted when expired evidence is used — but only if Claude notices and self-reports the violation.

The entire memory system depends on Claude perfectly tracking metadata across sessions in files it reads inconsistently.

### Missing Evidence
- Any evidence that Claude reliably maintains staleness state across 20+ sessions
- Any test showing EntityGraph extraction is actually deterministic (same input, same output, every time)
- Any demonstration that STALENESS_VIOLATION fires correctly without being explicitly prompted

### Consequence If Ignored
You build a fake database. Developers trust the memory system, rely on FRESH/AGING states, and make decisions based on staleness metadata that Claude has been silently corrupting or ignoring for sessions.

### Validation Test
Create 10 drawers. Perform 30 writes across 3 sessions. At session 4, query staleness without prompting. Compare actual states to expected states per the transition rules. Measure error rate.

### Action
**Simplify.** Drop staleness states to FRESH/STALE/EXPIRED. Drop the full provenance ledger. Keep MemorySearch. Kill EntityGraph until you have evidence LLM-based deterministic extraction is reliable enough to trust.

---

## Problem 5: 145 Modules at LLM Compliance Rates Breaks the Framework

### Problem
The framework has ~145 modules, 12 enforced invariants, 7 verification modes, 4 loading gates, 3 phases per stage, and a receipt chain connecting all of them. Every module is behavioral instruction for an LLM.

### Wrong Assumption
Claude will reliably follow a 145-module, 9-layer framework with 12 invariants across long sessions.

### Why It May Be False
LLM compliance with complex multi-step behavioral protocols degrades with:
- Session length (context fills, compression loses detail)
- Framework complexity (more rules = more collision, more ambiguity)
- Implicit vs. explicit instruction (modules not in current context are not followed)

The framework's own progressive loading design (I4/I5) means most modules are not loaded at any given time. Modules not in context cannot be followed. The framework assumes all 145 modules are active and enforced simultaneously, but the loading model guarantees they are not.

### Missing Evidence
- Any compliance test across a 15+ wave session
- Any measurement of invariant violation rate in live use
- Any evidence that progressive loading maintains behavioral consistency across session boundaries

### Consequence If Ignored
The framework drifts in practice. Users compensate by re-prompting, which undermines the automation premise. The more complex the framework, the more the user ends up manually driving Claude.

### Validation Test
Run the same 10-wave project twice without manual intervention. Compare receipts. Measure how many spec decisions diverge between runs. If variance is high, the framework is not deterministic enough to be trusted.

### Action
**Shrink.** Tier 1 + Tier 2 modules only for v1. That is ~21 modules. Build those. Validate compliance. Then grow.

---

## Problem 6: No User Demand Evidence Exists

### Problem
WabbleSpec is described as a framework for "the complete software development lifecycle." There is no user research, no pain-point validation, no evidence anyone outside the spec author wants or would use this framework.

### Wrong Assumption
Other developers using Claude Code have the same pain points this framework addresses and will adopt a structured spec-driven framework to solve them.

### Why It May Be False
The Claude Code user base skews toward developers who want AI to move fast, not developers who want to add a 15-step receipt-chained verification pipeline to every project. The framework's overhead — ScopeFrame, Interview, Specify, Decompose, Guard, Executor, Verifier, Archive — before any code is written — is not a feature to most developers; it is a reason to not use the framework.

The one person confirmed to want this framework is the person writing it.

### Missing Evidence
- Any user interview with a developer who expressed frustration that Claude Code lacks receipt chains
- Any GitHub issue, forum post, or community discussion requesting structured spec-driven frameworks for Claude Code
- Any usage metric from v5.3 showing adoption beyond the spec author

### Consequence If Ignored
You build an elaborate framework for an audience of one. The engineering investment is real. The user impact is zero.

### Validation Test
Post a description of the core concept (not the whole framework) to 3 developer communities. Ask: "Would you use a structured spec-driven framework for Claude Code that adds this overhead to get these guarantees?" Measure actual interest, not validation bias.

### Action
**Validate** demand before writing module 1. No code before 5 developer conversations.

---

## Problem 7: Competing Tools Are Already Running in This Project

### Problem
The user's own Claude Code environment contains oh-my-claudecode (v4.13.5, with v4.14.1 available) and GSD (visible in skills list). Both frameworks overlap heavily with WabbleSpec's scope.

### Wrong Assumption
WabbleSpec fills a gap that existing frameworks do not.

### Why It May Be False

**oh-my-claudecode** provides: planning, execution, debugging, verification, git management, test engineering, code review, security review, UI/UX, documentation, architect, analyst, tracer, verifier, and more. This overlaps directly with WabbleSpec's L1 (Specify, Decompose, Apply), L2 (Reviewer, Verifier, Executor), L7 (Release), and L8 (Retro, Feedback).

**GSD** provides: phase planning, execution, verification, code review, security audit, UI phases, AI integration phases, codebase mapping, and more. This overlaps with WabbleSpec's entire lifecycle model.

WabbleSpec is not filling a gap. It is a third framework for a problem the user already has two frameworks attempting to solve. The unique differentiators — receipt chains, staleness-tracked memory, evolution pipeline — are either unimplemented or untested.

### Missing Evidence
- A specific capability WabbleSpec provides that neither oh-my-claudecode nor GSD can provide
- Evidence that the existing frameworks are failing in ways WabbleSpec specifically addresses
- Any comparison of WabbleSpec's actual outputs vs. GSD or OMC outputs for the same task

### Consequence If Ignored
Three frameworks, none mastered. The user switches between them, context-mixes their conventions, and achieves worse outcomes than committing to one.

### Validation Test
Take three real development tasks. Run one through GSD, one through oh-my-claudecode, one through WabbleSpec v5.3 (the "working" version). Compare outcomes, overhead, and satisfaction. If WabbleSpec does not clearly win, the project premise is broken.

### Action
**Research first.** Identify the specific failure mode in existing frameworks that WabbleSpec uniquely solves. If you cannot identify it precisely, the project should not be built.

---

## Problem 8: The Evolution Pipeline Is a Golden Egg Fantasy

### Problem
L8 (Instinct → Synth → Blueprint → Factory → Augment → Benchmark → Forge) describes a self-improving AI framework: execution patterns are observed, synthesized into proposals, spec'd, scaffolded, tested, and promoted back into the live framework — all gated by human attestation but driven by AI.

### Wrong Assumption
A framework can observe its own execution patterns, derive meaningful improvements, and reliably promote those improvements into better framework files.

### Why It May Be False

**Pattern extraction via EMA on receipts.** Receipts are self-reported by Claude. Patterns extracted from self-reported data inherit all the compliance noise and drift described in Problem 5. Garbage in, garbage out.

**"High confidence" patterns from EMA.** The confidence formula (`new = old * 0.9 + outcome * 0.1`) can only report on patterns Claude recognized and reported correctly. Systematic deviations that Claude doesn't self-report don't appear in tracker.json. The EMA will find spurious patterns in noisy self-reported data.

**Forge promoting to live framework.** This means AI-generated code (Augment-produced SKILL.md files) gets promoted into the framework that controls future AI behavior. This is recursive prompt injection with a human-attestation fig leaf.

**This feature has never shipped in a real AI framework.** Self-improving LLM-based frameworks are an active research problem at major AI labs with teams of engineers. WabbleSpec plans to solve this as a solo side project.

### Missing Evidence
- Any evidence from v5.3 that Instinct tracked meaningful patterns
- Any real improvement to the framework produced by the Evolution pipeline vs. manual editing
- Any evidence that Benchmark can reliably distinguish a better module from a worse one
- Any prior art of a working self-improving LLM framework at this level of detail

### Consequence If Ignored
Enormous implementation investment in the most technically ambitious, least validated part of the framework. L8 will be built last (Priority 14 of 15) and will likely never be reached.

### Validation Test
Skip building L8. Build L1-L7. Run 10 projects. Manually do what L8 would do: review patterns, write improvements, update module files. If you do this manually and find it valuable, then build L8 to automate it.

### Action
**Delete** L8 from v1 scope entirely. It is a later-phase experiment, not a core feature.

---

## Problem 9: I12 (Spec Quality Over Volume) Is Violated by the Spec Itself

### Problem
Invariant I12 states: "Specification depth and precision matter more than coverage breadth. A short, testable, unambiguous spec is better than a long, comprehensive, untestable one. Spec bloat is a first-class defect."

WabbleSpec v6.1 has 15+ long-form documents, 50+ module planning files, ~1,179 lines in Core.md alone, ~1,292 lines in Manual.md, 12 invariants, 9 layers, 145 modules.

### Wrong Assumption
I12 applies to product specs written using WabbleSpec. It does not apply to WabbleSpec itself.

### Why It May Be False
I12 is a framework-level principle. If spec bloat is a defect in products, it is also a defect in the framework. The WabbleSpec spec fails its own quality test: there are duplicate requirements across Core.md and Manual.md, requirements written as implementation instructions rather than behavioral constraints, and sections that exist to demonstrate thoroughness rather than constrain behavior.

More damaging: the framework is so large that no developer can hold it in their head. A framework that cannot be internalized is not followed consistently — which directly undermines the compliance foundation.

### Missing Evidence
- Any reader who navigated the full WabbleSpec v6.1 spec and accurately recalled the activation conditions for 20 arbitrary modules
- Any test showing that a developer can use the framework without constantly consulting the documents

### Consequence If Ignored
The framework spec grows with every version. Each version adds modules, invariants, build targets, and new concepts. The cognitive load compounds. Usage approaches zero.

### Validation Test
Give the Core.md to a developer unfamiliar with WabbleSpec. Ask them to use it to run one project. Measure time spent consulting docs vs. time producing output. If doc-consult time exceeds productive time, the spec is too heavy.

### Action
**Cut.** Target 25 modules maximum for v1. One document, under 50 pages total. Everything else is future scope.

---

## Problem 10: "No External Dependencies" Removes the Tools That Would Make This Work

### Problem
The spec states: "No external MCPs. No telemetry. No data export. All storage is plain files. The framework operates entirely offline with zero external dependencies."

### Wrong Assumption
Removing external dependencies makes the framework more reliable and portable.

### Why It May Be False
The features WabbleSpec wants — reliable receipt chain enforcement, atomic memory writes, staleness tracking, entity graph with query capability, deterministic pattern extraction — all require exactly what MCPs and external tools provide: persistent state, atomic operations, query engines, and execution outside the LLM context.

By banning MCPs, WabbleSpec forces all of these features to be simulated by LLM behavior against plain files. LLM-simulated database operations are unreliable. LLM-simulated enforcement is theater (Problem 2). The "no dependencies" constraint is what makes the framework's ambitions technically infeasible.

The constraint was probably chosen for portability and simplicity. But portability of a broken system is not valuable.

### Missing Evidence
- Evidence that "plain files + LLM behavior" is sufficient for reliable staleness enforcement across sessions
- Evidence that this design was preferred over MCP-backed alternatives after actual testing

### Consequence If Ignored
All the complex features (memory, receipts, entity graph, provenance) remain aspirational. You build a framework whose most distinctive features do not work reliably because you removed the only infrastructure that would make them work.

### Validation Test
Build the memory system as designed (plain files). Run 10 sessions. Measure drift in staleness states. Then build the same system backed by a simple SQLite MCP. Compare reliability. The comparison will answer whether the constraint should be lifted.

### Action
**Reconsider.** The "no external dependencies" constraint is compatible with simplicity, not with the ambitions described. Either accept a simpler framework, or accept external dependencies. You cannot have both.

---

## Problem 11: Version Numbering Implies Maturity That Does Not Exist

### Problem
"WabbleSpec v6.1" implies six major versions of a working system. The planning notes explicitly state: "v6 was treated as AI-generated hallucination. v5.3 is base."

### Wrong Assumption
v6.1 builds on a proven v5.3 foundation with selective integration of validated v6 features.

### Why It May Be False
If v6 was AI-generated hallucination that had to be scrapped, v5.3 may itself be a framework that was heavily planned and minimally used. There is no evidence that v5.3 reliably produced the outcomes it promised. The "ground truth" designation of v5.3 is self-declared, not validated by external use. Version 6.1 may be v6.0 hallucination (rejected) + v5.3 (unvalidated) + new hallucination classified as "planning sessions."

### Missing Evidence
- Completed projects built with v5.3 showing measurable improvement over unassisted Claude Code
- A log of what v5.3 got wrong that v6.1 explicitly fixes
- Any evidence that v5.3 was used by anyone other than the spec author

### Consequence If Ignored
v6.1 inherits all v5.3 problems plus adds new ones. The framing of "building on v5.3" provides false confidence.

### Validation Test
List 5 concrete failures observed in v5.3 use. For each, identify the specific v6.1 change that addresses it. If you cannot list 5 concrete failures with specific fixes, v6.1 is not evolution — it is inflation.

### Action
**Document failures first.** The changelog from v5.3 to v6.1 should be a list of solved problems, not a list of added features.

---

## Brutal Cut List

Everything that should be removed before a line of implementation is written:

1. **L8 Evolution pipeline** (Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge) — entire layer. Technically speculative. Unvalidated premise. Not needed for v1 value delivery.
2. **EntityGraph** (nodes.json, edges.json, entity extraction) — deterministic LLM extraction is not deterministic. Complexity without reliability.
3. **Dream** — background consolidation by an LLM "at zero active-session cost" is not a real background process. Fake daemon.
4. **MemoryMine** — deep pattern mining is downstream of a working memory system. No working memory system exists yet.
5. **Provenance ledger** — append-only ledger maintained by LLM in a markdown file is not an append-only ledger.
6. **Staleness states beyond FRESH/EXPIRED** — AGING, STALE, NEEDS_REVERIFICATION, SUPERSEDED add complexity without adding reliability. Binary is enough for v1.
7. **The full vendor-neutral runtime layer** (RuntimeProbe, ModelRouter capability descriptors, Ensemble multi-lane routing) — you are always on Claude. Delete the abstraction.
8. **TeamPlan** — multi-agent coordination is future scope. No evidence it's needed before a single-agent flow works.
9. **All 11 platform packages in full** — pick 2 (Web, API/Service). Ship those. Add others when there's demand.
10. **Homowabian as a separate module** — voice register is 4 words in CLAUDE.md. It does not need a module, activation rules, or receipt schema.
11. **Economy as a separate module** — hedge removal is one CLAUDE.md instruction. It does not need a module.
12. **ResearchLog as a separate module** — this is taking notes. It does not need a module.
13. **All L4 Capability Gateways for v1** — Security and Engineering only. Aesthetic, Design, Experience are future scope.
14. **The five-factor complexity scoring formula** in Decompose — this produces a fake precision score from LLM-estimated inputs. Simplify to Low/Medium/High.
15. **EARS syntax enforcement** — mandating a niche formal requirements syntax (Easy Approach to Requirements Syntax) for all specs adds overhead with no evidence of improved LLM output quality.

---

## MVP Reality Check

The smallest version that could prove the idea is worth building:

**WabbleSpec MVP (v0.1) — 8 modules, 2 targets, 1 invariant chain:**

| Module | Why it's in MVP |
|---|---|
| Recipe | Target detection is necessary. |
| Specify | Writing a spec is the core claim. |
| Decompose | Breaking work into waves is the core execution claim. |
| Executor | Running waves is the core execution claim. |
| Verifier | Completion with evidence is the core quality claim. |
| Archive | Receipt persistence is the core auditability claim. |
| Memory (simple) | FRESH/EXPIRED only. Two staleness states. |
| Reviewer | Adversarial gate on plan and output. |

**Build targets in MVP:** Web and API/Service only.

**One invariant chain to enforce:** Research receipt → Plan receipt → Execute receipt → Verifier PASS.

**Success criteria:** 3 real projects built end-to-end. Receipt chains intact without manual intervention. Verifier blocks at least one bad completion per project. Output quality measurably better than unassisted Claude Code (ask an independent developer to judge blind).

---

## Validation Plan

Ten tests to run before writing serious code:

1. **Compliance test.** Give an LLM the 12 invariants and run a 10-wave session. Count invariant violations without prompting the LLM to check them. Establish a baseline compliance rate. If below 80%, the enforcement model is broken.

2. **Receipt chain survival test.** Run a project. At wave 5, corrupt one receipt file. Do not tell Claude. See if subsequent waves detect and block. This tests whether the chain is a real gate or theater.

3. **Competing framework comparison.** Build the same project with GSD, with oh-my-claudecode, and with vanilla Claude Code + a well-written CLAUDE.md. Measure output quality, time, and overhead. WabbleSpec needs to win this comparison to justify building it.

4. **Developer demand interview.** Talk to 5 developers who use Claude Code professionally. Ask what frustrates them most. Ask if "structured spec-driven receipts and verification gates" would solve their frustration. Do not lead. Measure fit.

5. **Memory staleness reliability test.** Create 30 drawers across 5 sessions. Deliberately allow some to go stale. At session 6, query staleness states without prompting. Compare declared states to expected states. Measure accuracy.

6. **Scope inflation measurement.** Count the word count of v5.3 planning documents. Count the word count of v6.1. If v6.1 is more than 50% larger, identify what was added and whether each addition is validated by a problem. If additions are purely anticipatory, they violate I12.

7. **Single-module usability test.** Pick Specify. Write a complete, standalone SKILL.md for it. Give it to a developer unfamiliar with WabbleSpec. Ask them to use it to specify a real project. Measure deviation from expected behavior. This tests whether the module design is usable without the full framework.

8. **"No MCP" vs. "with MCP" reliability test.** Build the receipt chain enforcement twice: once as plain-file + LLM behavior, once backed by a simple file-watcher script that checks receipt presence before allowing the next command. Measure how often each approach catches missing receipts. This tests whether the "no external dependencies" constraint is viable.

9. **v5.3 failure audit.** Review the last 5 projects attempted with v5.3 (if any). For each, identify what the framework failed to prevent or enable. If no v5.3 projects exist, this is critical evidence that the framework has never been used in production.

10. **Minimum viable spec test.** Write a 1-page version of WabbleSpec (the absolute minimum: one invariant, one module, one receipt type). Use it on a real project. Compare outcome to using full v6.1. If the 1-page version delivers 80% of the value, the complexity of v6.1 is unjustified.

---

## Kill Criteria

Stop working on this idea if any of the following are true:

1. LLM compliance rate with the receipt chain invariant is below 70% in unassisted sessions.
2. The competing framework comparison (GSD, OMC, vanilla CLAUDE.md) shows no meaningful quality improvement from WabbleSpec.
3. Five developer interviews produce zero genuine demand for structured spec-driven frameworks in Claude Code.
4. Memory staleness state accuracy is below 80% across a 5-session test.
5. The v5.3 failure audit reveals no completed projects (meaning the framework has never been used end-to-end).
6. Module count required to deliver v0.1 value exceeds 30 (framework overhead exceeds deliverable value).
7. The "no external dependencies" constraint means the three most distinctive features (memory staleness, receipt enforcement, entity graph) cannot be made reliable.
8. You cannot explain the specific failure mode of GSD and oh-my-claudecode that WabbleSpec uniquely fixes in one sentence.

---

## Final Verdict

**SHRINK**

The core idea — structured, spec-driven, receipt-chained AI-assisted development — is not irrational. Discipline in AI-assisted development is a real need.

But the current scope is catastrophically inflated. 145 modules. 9 layers. 6 gateways. 11 build targets. 12 invariants. A self-evolving pipeline. Vendor-neutral runtime abstraction for a single-vendor deployment target. Sophisticated memory with staleness states that are maintained by the same LLM they are supposed to constrain. Version 6.1 of something that has never shipped.

Every additional module you spec is debt you carry before writing a line of code.

The idea earns a SHRINK, not a KILL, because:
- Receipt-chain discipline is a genuine gap in how most people use Claude Code
- Evidence-tracked decisions across a project is a genuine problem
- Structured verification gates are genuinely useful

But you cannot get to those benefits through 145 modules. You can get there through 8.

Build 8 modules. Run 3 real projects. If it works, add more.

Everything else in this spec is a golden egg you are carrying instead of walking.
