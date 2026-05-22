# WabbleSpec v6.1 — Defense Brief

**Date:** 2026-05-21  
**Reviewed:** codex-project.md, gemini-project.md, copilot-project.md, claude-project.md  
**Verdicts received:** Codex: PIVOT | Gemini: SHRINK | Copilot: SHRINK | Claude: SHRINK

Four independent evaluations reviewed. All four agree on the core problem's reality. All four attack scope, not premise. This distinction is the foundation of the defense.

---

## Defense Point 1: The Core Problem Is Real

State what deserves protection: the problem — AI coding agents produce false completions, lose context, repeat drift, and cannot be made to prove they verified what they claimed — is acknowledged as real by all four judges. None said the pain is imaginary.

## Why The Harsh Critique May Be Wrong

Critics conflate "the problem is real" with "this solution is sized correctly." Those are separate questions. Attacking scope is not attacking premise. A correct diagnosis with an oversized treatment plan is not a hoax — it is an overbuilt prototype.

## Evidence Needed

One concrete before/after: task run with baseline Claude Code, same task with minimal WabbleSpec slice, measurable difference in false-completion rate.

## Risk

If the before/after shows no meaningful difference, premise collapses regardless of problem being real.

## Practical Move

Run the baseline test first. Pick 10 tasks. Baseline with `AGENTS.md`. Don't build anything else until you have baseline numbers.

---

## Defense Point 2: Receipt Chain Is Not Inherently Theater

The Claude judge's most damaging attack: "receipts are written by Claude, verified by Claude, enforced by Claude — it's one LLM checking its own work." This is devastating IF enforcement requires LLM compliance. It isn't necessarily true.

## Why The Harsh Critique May Be Wrong

Claude Code has `pre-tool-use` hooks. A receipt validator does not need to be Claude. It can be a 30-line PowerShell script that checks whether a receipt file exists before allowing the next phase command to execute. The user already has hook infrastructure running in this project (caveman mode hooks, GSD hooks). The "theater" critique assumes enforcement = LLM behavior. It doesn't.

A hook-backed receipt gate is not self-attestation. It is machine enforcement. None of the four judges addressed this.

## Evidence Needed

Proof-of-concept: one `pre-tool-use` hook that reads `.wabblespec/receipts/` and blocks execution if the required upstream receipt is absent. Run it. Show it blocking a deliberate skip.

## Risk

Hook architecture adds implementation complexity and couples framework to Claude Code specifically — which undercuts vendor-neutral claims further. But vendor neutrality was already a fake claim; this just makes the Claude-specific design explicit and leverages it.

## Practical Move

Write the receipt validator hook before writing any SKILL.md files. If the hook can reliably enforce one gate, the anti-theater critique is answered. If the hook proves unreliable, receipts are theater and you kill that branch.

---

## Defense Point 3: "No External Dependencies" Was Misread by Critics

Critics say: no MCP = cannot enforce anything = the ambitions are technically infeasible. But critics conflated "no MCP" with "no external process."

## Why The Harsh Critique May Be Wrong

"No external dependencies" was probably meant as "no cloud services, no API keys, no vendor lock-in to third-party SaaS." A local PowerShell/bash script is not an external dependency. A SQLite file is not an external dependency. The critics applied a stricter reading than the constraint requires.

The useful version of the constraint: "framework state lives in the repo, not in a cloud service." That is a valid and defensible portability principle.

## Evidence Needed

Clarified definition of "external dependency" in the spec. Is SQLite allowed? Local scripts? File-watcher? The current spec bans MCPs but doesn't address local scripts.

## Risk

If the spec genuinely means "no code runs except Claude," then the critique is 100% fair and the most ambitious features are structurally impossible.

## Practical Move

Rewrite the constraint. "No cloud dependencies. No MCP servers. Local scripts and file checks are permitted." This preserves the portability intent while enabling real enforcement.

---

## Defense Point 4: The Recombination Is Novel in Its Specific Target Context

The Codex judge listed six existing tools that cover overlapping territory. This is the most superficially damaging attack. But the mapping is shallow.

## Why The Harsh Critique May Be Wrong

| Tool | What It Does | What It Lacks |
|---|---|---|
| Claude Code Skills | Behavioral instructions | No receipt enforcement, no phase gates |
| Cursor/Continue rules | Context injection | No execution tracking, no completion verification |
| AGENTS.md | Project instructions | No structure, no enforcement, no receipts |
| OpenAI Agents SDK | Agents, handoffs, guardrails | Python SDK, not Claude Code-native, not local-first |
| LangGraph | Durable execution, memory | Python SDK, requires infrastructure |
| CrewAI | Multi-agent crews | Python SDK, not Claude Code-native |

No existing tool provides: structured task cards + machine-enforced receipt gates + local-first storage + Claude Code-native operation. The recombination is genuinely novel in the Claude Code native context.

## Evidence Needed

A specific task where existing tools fail in the specific way WabbleSpec claims to fix. Example: "used GSD on task X, it marked done, tests were missing, here is the log."

## Risk

If GSD + a simple verification checklist produces the same outcomes as WabbleSpec MVP, the novelty doesn't create user value — it creates maintenance overhead.

## Practical Move

The Claude judge recommends comparing WabbleSpec vs GSD vs OMC on three real tasks. Do this. It's the fastest way to prove or disprove the differentiation claim.

---

## Defense Point 5: Progressive Loading Is Smart, Not Broken

The Claude judge attacks progressive loading (I4/I5): "modules not in context cannot be followed." This is framed as a flaw.

## Why The Harsh Critique May Be Wrong

Progressive loading is the correct design response to LLM context limits. Loading 145 modules simultaneously is impossible. Loading only the modules relevant to the current phase is the right architecture. The critique is: "this creates gaps." The defense is: "the alternative — loading everything — also creates gaps, and they're worse because context overflow degrades everything."

The real question is whether the progressive loading design is implemented well, not whether progressive loading is inherently broken.

## Evidence Needed

Compliance test: does Claude follow phase-appropriate modules better when loaded progressively vs. when given all instructions at once? This is testable in one session.

## Risk

If transition protocols fail — modules not loading correctly at phase boundaries — the design degrades in practice. But this is an implementation quality problem, not a design flaw.

## Practical Move

Test module transition explicitly. Build the Recipe → Specify transition. Verify Specify's module loads correctly and previous phase context is cleanly handed off.

---

## Defense Point 6: v5.3 as "Ground Truth" Is a Reasonable Starting Point

The Claude judge attacks the version number: "v6.1 implies maturity that doesn't exist." True. But the critique then extends to: "v5.3 may also be unvalidated."

## Why The Harsh Critique May Be Wrong

Calling v5.3 "ground truth" doesn't claim it's production-grade. It means: "this is the version we have highest confidence in, relative to v6 which was rejected as hallucination." The critique is fair that this baseline is weak. But the attack implies you should throw out v5.3 as unvalidated. That's too far. v5.3 represents real iteration history. The fact that v6 was rejected and the builder returned to v5.3 shows judgment, not confusion.

## Evidence Needed

Document 5 concrete things v5.3 got right (even informally). What did it produce? What worked? This doesn't need to be rigorous — it needs to be honest.

## Risk

If there are genuinely no v5.3 outputs (no completed projects, no session logs), the "ground truth" claim is hollow and the critique fully applies.

## Practical Move

Audit v5.3 honestly. List what it produced. If it produced nothing, say so and treat v6.1 as a fresh start rather than an evolution.

---

## Defense Point 7: Personal Infrastructure Has Legitimate Value Without Market Validation

The Copilot and Claude judges attack lack of user demand: "no interviews, no buyers, no market signals."

## Why The Harsh Critique May Be Wrong

WabbleSpec may be personal infrastructure. Personal infrastructure doesn't need market validation to be worth building. The criteria for "worth building" differs between:
- A product seeking adoption: requires market validation
- Personal infrastructure: requires only that it improves your own outcomes

If the creator uses Claude Code daily and this framework reduces their false-completion rate, it has value regardless of whether anyone else uses it. The market-validation critique is valid for a product roadmap. It is premature for a personal tool.

## Evidence Needed

Explicit declaration: is this a product or personal infrastructure? That question determines which criticisms apply.

## Risk

If the intent IS a product or research contribution, market validation critiques are fully valid and blocking.

## Practical Move

Decide now: personal tool or product. If personal tool, cut all product language and market claims. Scope becomes "does it improve my own workflow." If product, run the interviews before touching code.

---

## Defense Point 8: The Evolution Pipeline Is Worth Deferring, Not Killing

L8 (Instinct, Synth, Blueprint, Forge, etc.) is attacked by all four judges as "golden egg fantasy."

## Why The Harsh Critique May Be Wrong

All four judges say to delete L8 for MVP. None say it's conceptually wrong forever. The critique is about build order and resource allocation, not about the concept being impossible in principle. Self-improving AI frameworks are a real research area. The WabbleSpec version is speculative, but that's an implementation timing problem.

## Evidence Needed

None. This defense only needs the critics' own words: they say delete for MVP, not delete forever.

## Risk

None. All critics agree: defer L8. This defense point is uncontested.

## Practical Move

Remove L8 from all active scope. Archive the planning documents. Revisit after 100 real executions with the MVP.

---

## Salvageable Core

Smallest surviving version of the idea:

**Hook-enforced, receipt-gated task runner for Claude Code, CLI or Web target only.**

Components:
1. Recipe: target + complexity detection
2. Specify: one-page task card (goal, non-goals, assumptions, verification criteria)
3. Decompose: wave breakdown
4. Executor: wave execution
5. Verifier: runs declared checks, writes machine-parseable receipt
6. Archive: flat receipt index
7. Receipt validator: `pre-tool-use` hook, checks upstream receipt exists before phase proceeds
8. Memory: FRESH/EXPIRED only, flat files

This is 7 modules + 1 hook. No L5-L8. No vendor neutrality. No platform matrix. No self-improvement.

---

## Protected Features

Features that should not be deleted yet, and why:

| Feature | Why Protect |
|---|---|
| Receipt schema | Core differentiator. Without it, framework is just project rules. |
| `pre-tool-use` hook enforcer | Converts theater into real gates. Answerable to the strongest critique. |
| ScopeFrame / Specify | Explicit verification criteria before execution is the specific gap other tools leave open. |
| Verifier with explicit check list | Without declared checks, "done" is always LLM self-report. |
| Archive as proof log | Auditability of what was actually verified is genuinely absent from all competing tools. |
| Progressive loading design | Correct architecture for LLM context. Don't abandon it; implement it correctly. |

---

## Fair Criticism vs Premature Criticism

**Fair (apply now):**
- 145 modules is catastrophically overscoped for a first build
- L8 Evolution should not be in MVP scope
- Vendor-neutral claim is false given Claude Code Terminal target
- v6.1 version number implies maturity that doesn't exist
- Memory system beyond FRESH/EXPIRED is overengineered
- 11 platform targets is unvalidated breadth
- No baseline benchmark exists
- Path/directory contradictions must be fixed before implementation

**Premature (don't kill over these):**
- "No users" — premature if this is personal infrastructure
- "Receipt chain is theater" — premature until hook-enforced alternative is tested
- "Competes with GSD/OMC" — premature until head-to-head comparison run
- "No implementation = worthless planning" — planning has value; the question is whether implementation matches planning
- "Problem is not unique enough" — no existing tool provides this exact combination natively in Claude Code

---

## MVP Defense

Smallest build that fairly tests the idea:

**Target:** CLI projects only  
**Runtime:** Claude Code only  
**Modules:** 7 (Recipe, Specify, Decompose, Executor, Verifier, Archive, simple Memory)  
**Enforcement:** One `pre-tool-use` hook checking receipt existence  
**Duration:** 2 weeks max to working end-to-end  

**Test:**
- 10 tasks baseline (AGENTS.md only), record false-completion rate
- 10 same tasks via MVP, same metric
- Deliberately skip one receipt mid-run; hook must block it
- Give MVP to one other developer, watch them use it without coaching

**Pass condition:** Hook blocks at least one false completion. Other developer can complete one task without explanation. False-completion rate lower than baseline (even marginally).

---

## Continue Criteria

Signs this idea deserves more work:

1. Hook-enforced receipt gate blocks a false completion in live testing
2. Before/after on 10 tasks shows any reduction in missed verification
3. Head-to-head with GSD shows at least one task where receipt chain caught something GSD didn't
4. Another Claude Code user confirms they have the same pain point unprompted
5. 2-week MVP produces working end-to-end without expanding module scope
6. Maintenance after first 5 tasks requires updating fewer than 5 documents

---

## Final Verdict

**SHRINK**

The core idea is defensible: hook-enforced, receipt-gated, locally-stored task execution with explicit verification criteria. That combination is genuinely absent from all competing tools in the Claude Code native context.

The current build is not defensible: 145 modules, 9 layers, fake vendor neutrality, memory graph, self-improvement pipeline, and 11 platform targets have no validated foundation.

The critics who said PIVOT overstated their case. Pivoting implies the current framing is wrong. The framing — evidence-gated completion — is the right framing. The scope is wrong, not the frame.

Build the 7-module hook-enforced MVP. Run it for 2 weeks on real tasks. If the hook blocks one real false completion and the workflow doesn't collapse under its own weight, SHRINK was the right call. If it collapses, KILL is justified at that point — not before.

The project should not be killed on spec alone. It should be tested on execution.
