# WabbleSpec v6.1 — Final Judge Ruling

**Date:** 2026-05-21
**Reviewed:** claude-project.md, codex-project.md, copilot-project.md, gemini-project.md, defense-project.md
**Final Verdict:** SHRINK

---

## 1. Critic Claims That Are Valid

**Unanimous — all four critics correct:**
- 145 modules is catastrophically overscoped before a single module runs
- L8 Evolution (Instinct, Synth, Blueprint, Forge) is unvalidated, speculative, should not be in v1 scope
- 11 platform targets are unjustified breadth; ship one
- No baseline comparison exists; "better than baseline" is asserted, never measured
- No implementation files exist at all — confirmed by Codex's file scan (zero `.ps1`, `.js`, `.py`, no `.wabblespec/` directory)

**Claude critique correct:**
- Dream is not a background daemon; it runs when Claude runs it — fake daemon, delete
- EntityGraph's "deterministic extraction" is Claude extraction, which is not deterministic — same input does not guarantee same output
- Provenance ledger maintained by an LLM in a markdown file is not an append-only ledger
- Staleness states beyond FRESH/EXPIRED add complexity without reliability — AGING, STALE, NEEDS_REVERIFICATION, SUPERSEDED all collapse in practice
- Version 6.1 implies six shipped versions; planning docs state v6 was "treated as AI-generated hallucination" — false maturity signal
- Progressive loading means modules not in context will not be followed — real behavioral gap that must be tested, not assumed to work
- Homowabian, Economy, ResearchLog do not need modules — one CLAUDE.md line each
- TeamPlan is future scope; no evidence single-agent flow works yet
- EARS syntax enforcement has no evidence of improving LLM output quality
- Five-factor complexity scoring produces fake precision from LLM-estimated inputs

**Codex critique correct:**
- Path contradictions exist and block implementation: docs reference `.wabblespec/plans/v61/` but actual docs live in `planning/`; docs reference `../canonical/` but no `canonical/` directory exists — spec cannot serve as source of truth
- Process is too heavy for small tasks; gate collapsing admission is a symptom the default flow fails small tasks
- Receipt validation is unimplemented: no schema parser, no chain validator, no enforcement that blocks without human prompting

**Gemini critique correct:**
- Token overhead of receipts for every phase transition has not been measured; context exhaustion is a real risk that must be tested before expanding
- Vendor-neutral claim is false given runtime = Claude Code Terminal — claim should be dropped, not decorated

---

## 2. Critic Claims That Are Too Harsh

**Copilot critique — mostly category error:**
Copilot applied a standard startup product critique (TAM/SAM/SOM, paying customers, monetization runway, legal compliance). WabbleSpec shows no evidence of being a commercial product. Critiques about LTV/CAC, pre-orders, and raising money are irrelevant unless the builder explicitly targets a market. These critiques are not wrong in principle but wrong in category. Do not act on them unless you decide this is a product.

**Claude critique overstates on receipts:**
"Receipts are theater" is too absolute. The defense correctly identifies that `pre-tool-use` hooks can enforce receipt existence mechanically — a 30-line script checking `.wabblespec/receipts/` before allowing the next phase command is not LLM self-attestation. None of the four critics addressed this. The theater verdict depends entirely on whether enforcement stays inside Claude or moves outside it.

**Codex critique overstates on differentiation:**
"Renamed project rules, renamed workflow orchestration" understates the specific combination. No existing tool provides all of: structured task cards + machine-enforced receipt gates + local-first storage + Claude Code-native operation. The gap is real. The critique is that the gap may not be big enough to justify 145 modules — that is valid. The claim that there is no gap at all is too strong.

**Gemini critique on routing:**
"11 predefined buckets limit the model's natural ability to infer context" is partly wrong. Target-specific context injection is a valid pattern that can improve output, not constrain it. The flaw is 11 buckets before proving one works, not the routing concept itself.

---

## 3. Defense Claims That Are Valid

**Hook enforcement is a real answer to the theater critique:**
This is the defense's strongest point and it is genuinely correct. Pre-tool-use hooks already run in this project (caveman mode, GSD). A receipt validator hook is implementable, exists outside Claude's compliance model, and directly answers the strongest critique. No critic addressed this. The hook path must be prototyped before writing any SKILL.md files.

**"No external dependencies" was misread:**
Critics read it as "no code runs except Claude." The more reasonable reading is "no cloud services, no API keys, no vendor SaaS lock-in." A local PowerShell script is not an external dependency. The spec needs to clarify this, but the critics attacked a stricter reading than the constraint likely intended.

**Progressive loading is correct design:**
Loading 145 modules simultaneously is impossible. Loading only phase-relevant modules is correct. The critique is valid that transitions must be implemented well — but the architecture direction is right. Abandon it only if testing shows transitions fail in practice.

**Problem is real:**
All four critics confirmed it. False completions, context drift, repeated instruction loss, weak verification — these are real pain points in agentic coding. The defense is right to protect this.

**Personal infrastructure vs product changes which critiques apply:**
If this is personal tooling, market validation critiques are premature. The builder must decide: personal tool or product. That decision gates which critics are relevant.

**L8 deferred, not killed:**
All four critics say "delete from MVP," not "delete forever." The defense is correct that this is a build-order dispute, not a concept condemnation.

---

## 4. Defense Claims That Are Weak

**"v5.3 represents real iteration history":**
The defense asserts this without producing any v5.3 outputs. No completed projects, no session logs, no receipt chains from v5.3 are cited. If v5.3 produced nothing, the "ground truth" designation is hollow and the version progression is pure planning inflation. Wishful until v5.3 outputs are audited.

**"Planning has value":**
True in general. Not true when 112,960 words of spec exist with zero implementation and the builder's own planning docs acknowledge v6 was hallucination. At this ratio, more planning is negative value. The defense undersells this problem.

**"Novelty justifies building":**
The gap is real. Whether the gap justifies 145 modules vs. a CLAUDE.md + one verification script is not answered. Novelty of combination is not sufficient justification for scope.

**Compliance rate assumption:**
The defense never addresses the core behavioral question: will Claude follow even a 7-module framework consistently without drift across 15+ wave sessions? The hook enforces receipt existence. It does not enforce receipt quality. A Claude that writes PASS receipts for work it did not do still breaks the framework. The defense is silent on this.

---

## 5. Features to Cut

Remove before implementation begins:

| Cut | Reason |
|---|---|
| L8: Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge | Unvalidated. No baseline suite, no regression corpus. Defer until 100+ real executions exist. |
| EntityGraph | LLM extraction is not deterministic. Same input, different outputs. Not a database. |
| Dream | Not a daemon. Fake background process. |
| MemoryMine | Downstream of a working memory system. No working memory system exists. |
| Provenance ledger | LLM-maintained append-only ledger is not append-only. |
| AGING / STALE / NEEDS_REVERIFICATION / SUPERSEDED staleness states | FRESH / EXPIRED is sufficient for MVP. |
| RuntimeProbe, ModelRouter, vendor-neutral capability layer, Ensemble | Always Claude. Abstraction for one thing. |
| TeamPlan | Multi-agent coordination is future scope. |
| 10 of 11 platform targets | Pick Web or CLI. Validate one before adding more. |
| Homowabian module | One CLAUDE.md line. |
| Economy module | One CLAUDE.md line. |
| ResearchLog module | Taking notes. Not a module. |
| L7 Delivery: Deploy, Package, Release, Monitor | Use existing CI/CD. Do not build what exists. |
| All L4 Capability Gateways for MVP | Add after core loop works. |
| EARS syntax enforcement | No evidence it improves output. |
| Five-factor complexity scoring formula | Fake precision from LLM estimates. Low/Medium/High is enough. |
| All "complete software lifecycle" language | No complete software lifecycle exists yet. |
| All vendor-neutral claims | False claim. Drop it or earn it with two working adapters. |

---

## 6. Features to Keep

| Keep | Why |
|---|---|
| Receipt schema | Core differentiator. Without it, this is just project rules. |
| `pre-tool-use` hook for receipt enforcement | Converts theater into real gates. Answerable to strongest critique. Must be built first. |
| Recipe (target + complexity detection) | Necessary entry point. Keep simple. |
| ScopeFrame / Specify (one-page task card with verification criteria) | The specific gap other tools leave open. Explicit criteria before execution. |
| Decompose (wave breakdown) | Core execution claim. |
| Executor (wave execution) | Core execution claim. |
| Verifier (runs declared checks, writes receipt) | Without declared checks, "done" is always LLM self-report. |
| Archive (flat receipt index / proof log) | Auditability of what was actually verified is absent from competing tools. |
| Memory: FRESH/EXPIRED, flat files only | Keep the concept, kill the complexity. |
| Reviewer (adversarial gate on plan/output) | One good adversarial check is more valuable than 20 compliance receipts. |
| Progressive loading design principle | Correct architecture. Implement transitions carefully. |

---

## 7. MVP to Build

**Hook-enforced, receipt-gated task runner. One target. One runtime.**

**Target:** CLI (simplest verification loop)
**Runtime:** Claude Code only. No vendor-neutral claims.
**Timeline:** 2 weeks max to working end-to-end

**7 modules + 1 hook:**

| # | Module | What it does |
|---|---|---|
| 1 | Recipe | Detect target type and task complexity |
| 2 | Specify | Write one-page task card: goal, non-goals, assumptions, verification criteria |
| 3 | Decompose | Break task into waves with wave-level acceptance criteria |
| 4 | Executor | Execute one wave, produce artifacts |
| 5 | Verifier | Run declared checks, write machine-parseable receipt |
| 6 | Archive | Append receipt to flat index; task is "done" only when receipt exists |
| 7 | Memory | FRESH/EXPIRED only; flat files |
| + | Hook | `pre-tool-use` script: check upstream receipt exists before next phase executes; block if absent |

**Build the hook first. Not the SKILL.md files. The hook.**

**Success criteria:**
- Hook blocks at least one deliberately skipped receipt without prompting
- False-completion rate on 10 tasks lower than baseline (AGENTS.md)
- One developer unfamiliar with WabbleSpec completes one task without coaching

---

## 8. Validation Tests

Run in this order before expanding scope:

1. **v5.3 audit first.** List every project v5.3 completed. If zero: treat v6.1 as a fresh start, not an evolution. Do not carry forward false maturity.

2. **Path consistency linter.** Script that checks every referenced path, required artifact, and directory claim in current spec docs. Fix all failures before writing any implementation. Spec cannot serve as source of truth while it references nonexistent paths.

3. **Hook proof-of-concept.** Build one `pre-tool-use` hook that reads `.wabblespec/receipts/` and blocks execution when upstream receipt is absent. Deliberately skip a receipt. Hook must block without human prompting. If hook fails, receipts remain theater and the core differentiator does not work.

4. **Baseline measurement.** 10 tasks using plain `AGENTS.md`. Record: false-completion claims, missed tests, times Claude said "done" without running declared checks. This is the number you need to beat.

5. **MVP benchmark.** Same 10 tasks through the 7-module MVP. Compare false-completion rate. If no improvement, the added overhead is not justified.

6. **Competing framework test.** Same real task through GSD, OMC, and WabbleSpec MVP. Compare whether receipt chain catches anything GSD's verification misses. If outcomes are equivalent, differentiation claim is false.

7. **Compliance rate test.** 10-wave session. Count how many times Claude deviates from the receipt chain invariant without being prompted to check. Below 70% unassisted = enforcement model is broken.

8. **Usability test.** Give MVP to one developer unfamiliar with WabbleSpec. No coaching. Measure: time to first successful task, number of doc consultations, whether module roles were naturally understood.

---

## 9. Kill Criteria

Stop if any of these are true:

1. Hook proof-of-concept fails: cannot reliably block a deliberately skipped receipt
2. Before/after on 10 tasks shows no reduction in false-completion rate vs AGENTS.md baseline
3. GSD + a simple verification checklist produces equivalent outcomes (no differentiation value)
4. v5.3 audit reveals zero completed projects (framework never ran end-to-end; calling v6.1 an evolution is dishonest)
5. Unassisted LLM compliance rate with receipt chain invariant is below 70%
6. Usability test: unfamiliar developer cannot complete one task without coaching after reasonable onboarding
7. 2-week MVP development requires expanding beyond 10 modules before reaching working end-to-end
8. Cannot state in one sentence the specific failure mode of GSD that WabbleSpec's receipt gate uniquely prevents

---

## 10. Final Verdict: SHRINK

**Not PIVOT.** The framing — evidence-gated completion, hook-enforced phase gates, local-first receipt storage — is the right framing. Pivoting implies the direction is wrong. The direction is correct.

**Not KILL.** No execution test has been run. Killing on spec alone when the core mechanism (hook-enforced receipts) has not been tested is premature. The defense is correct on this.

**SHRINK.** Hard.

What survives: 7 modules, 1 hook, 1 target, 1 runtime, FRESH/EXPIRED memory only.

What dies now: 138 modules, L5 memory graph, L6 expression stack, L7 delivery pipeline, L8 evolution pipeline, vendor-neutral runtime, 10 platform targets, EntityGraph, Dream, MemoryMine, Provenance, staleness complexity, Homowabian, Economy, ResearchLog, TeamPlan, EARS enforcement, five-factor scoring.

**One decision to make before touching code:**
Personal tool or product? If personal tool: market critiques are irrelevant, build the hook, measure your own false-completion rate. If product: interviews before code, no exceptions. This single decision determines which 40% of the critique applies.

**First action:**
Audit v5.3. If it produced nothing, name this v1.0 and start honest. Then write the hook. Not a SKILL.md. The hook.
