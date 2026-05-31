# Ref-Eval: oh-my-claudecode

**Reference:** oh-my-claudecode (v4.14.4)
**Session:** agent-creator-integration-20260529
**Evaluated:** 2026-05-30
**Reference path:** C:\Users\Kirsten\Downloads\Orchestrator\oh-my-claudecode

---

## File Inventory

| File | Purpose | Status | Key content |
|---|---|---|---|
| README.md | Overview, quick start, team mode docs, feature table | Read | Orchestration modes table, OMC vs omc team distinction, plugin install flow |
| CLAUDE.md | Session prompt — all operational rules | Read | Commit protocol with trailers, model routing tiers, skill/agent catalog |
| AGENTS.md | Full agent protocol, delegation rules, keyword detection, state management | Read | child_agent_protocol (read prompt → spawn_agent), one-at-a-time question rule |
| docs/ARCHITECTURE.md | Complete architecture: agents/skills/hooks/state | Read | 4-layer system, 19 agents in 4 lanes, skill layer composition, hook events, state model |
| agents/verifier.md | Verification agent prompt | Read | Independent-reviewer constraint, VERIFIED/PARTIAL/MISSING vocab, evidence table format |
| agents/planner.md | Planning agent prompt with ralplan-DR consensus | Read | One-question-at-a-time rule, never ask codebase facts, ≥2 viable options, ADR required |
| agents/analyst.md | Requirements gap analysis | Read | Testability focus, Open Questions output format |
| agents/critic.md | 5-phase adversarial review agent | Read | Pre-commitment, multi-perspective, self-audit, realist check, ADVERSARIAL escalation |
| agents/executor.md | Implementation agent | Read | Trivial/Scoped/Complex classification, 3-failure escalation, learnings notepad |
| benchmarks/harsh-critic/prompts/harsh-critic.md | Standalone harsh-critic prompt | Read | I6 violation: `model: claude-opus-4-6` hardcoded; same protocol as critic.md |
| src/ralphthon/deep-interview-prompt.ts | Deep interview prompt builder | Read | Weakest-dimension targeting, brownfield evidence citation, ralphthon-prd.json output |
| README.{de,es,fr,...}.md (×11) | Translations | Skipped | Same content as README.md |
| agents/{designer,writer,qa-tester,...}.md (×9) | Remaining agent prompts | Skipped | Same XML structure as read agents; content derivable from ARCHITECTURE.md |
| benchmarks/ (fixtures, evaluate.py) | Benchmark fixtures | Skipped | Agent quality evaluation data; not relevant to ref-adopt |
| commands/*.md (most) | Slash command thin-wrappers | Skipped | Dispatch-only; read SKILL.md and delegate |
| src/**, dist/** | TypeScript implementation | Skipped | Runtime code; behavioral patterns captured in agents/*.md |
| .github/workflows/** | CI workflows | Skipped | Not relevant |
| .omx/plans/** | Internal OMC planning docs | Skipped | Project-specific |

---

## Connection Map

```
CLAUDE.md ──model-routing──> agents/*.md : capability tier (haiku/sonnet/opus)
AGENTS.md ──spawn protocol──> ~/.codex/prompts/{role}.md : parent reads, embeds in spawn_agent message
agents/planner.md ──consult before plan──> agents/analyst.md : gap analysis before generation
agents/planner.md ──review via ralplan──> agents/critic.md : critic reviews plan; 3 perspectives
agents/executor.md ──escalate at 3 failures──> agents/architect.md : full context handoff
agents/verifier.md ──PASS/FAIL signal──> team pipeline : advance vs. team-fix stage transition
hooks/hooks.json ──event dispatch──> scripts/*.mjs : keyword-detector, persistent-mode, pre-compact
```

---

## Three Dimensions

### Dimension 1 — Behavior (operational detail)

**Critic protocol (5 phases):**
1. Pre-commitment: predict 3-5 most likely problem areas before reading — activates deliberate search
2. Verification: read work + verify every file reference against actual source; plan-specific sub-steps: assumptions extraction (VERIFIED/REASONABLE/FRAGILE), pre-mortem (5-7 failure scenarios), dependency audit, ambiguity scan, feasibility check, rollback analysis
3. Multi-perspective: code = security/new-hire/ops; plans = executor/stakeholder/skeptic
4. Gap analysis: explicitly ask "what is MISSING?" vs. what is wrong
4.5 Self-audit (mandatory): for each CRITICAL/MAJOR — confidence level, author-refutable check, flaw vs. preference; LOW confidence → move to Open Questions
4.75 Realist Check (mandatory): 4 pressure-test questions; downgrades require explicit "Mitigated by:" statement; NEVER downgrade data loss/security/financial findings
5. Synthesis: compare against pre-commitment predictions

Escalation: if 1 CRITICAL or 3+ MAJOR → ADVERSARIAL mode (assume more hidden problems, expand scope, "guilty until proven innocent")

Verdicts: REJECT / REVISE / ACCEPT-WITH-RESERVATIONS / ACCEPT

**Verifier constraints:**
- "Verification is a separate reviewer pass, not the same pass that authored the change."
- "Never self-approve or bless work produced in the same active context"
- Reject without fresh evidence if: "should/probably/seems to" language used, no fresh test output, claims without results, no type check for TS, no build check for compiled languages
- Per-criterion status: VERIFIED / PARTIAL / MISSING (with evidence requirement)

**Planner constraints:**
- "Ask ONE question at a time using AskUserQuestion tool. Never batch multiple questions."
- "Never ask the user about codebase facts (use explore agent to look them up)"
- Plans: 3-6 steps with acceptance criteria (not 30 micro-steps)
- ralplan-DR consensus: ≥2 viable options; explicit invalidation rationale if only 1 survives; ADR required in final plan
- Deliberate mode: pre-mortem (3 failure scenarios) + expanded test plan (unit/integration/e2e/observability)
- Plan generation only on explicit user trigger ("make it a work plan") — not on request classification alone

**Executor constraints:**
- Classify first: Trivial / Scoped / Complex
- After 3 failed attempts → escalate to architect with full context
- Append learnings to `.omc/notepads/{plan-name}/` after completing work
- Smallest viable change; no scope broadening; no new abstractions for single-use logic

### Dimension 2 — Format (identifier level)

**Agent file structure (XML wrapping):**
`<Agent_Prompt>` → `<Role>`, `<Why_This_Matters>`, `<Success_Criteria>`, `<Constraints>`, `<Investigation_Protocol>`, `<Tool_Usage>`, `<Execution_Policy>`, `<Output_Format>`, `<Failure_Modes_To_Avoid>`, `<Examples>`, `<Final_Checklist>`

**Verifier evidence table:**
```
| Check | Result | Command/Source | Output |
```

**Verifier acceptance criteria table:**
```
| # | Criterion | Status | Evidence |
```
Status values: VERIFIED / PARTIAL / MISSING

**Critic output format:**
```
**VERDICT: [REJECT / REVISE / ACCEPT-WITH-RESERVATIONS / ACCEPT]**
**Critical Findings**: finding + file:line evidence + Confidence + Why this matters + Fix
**Major Findings**: same structure
**Minor Findings**: less structure
**What's Missing**: explicit gap list
**Ambiguity Risks**: quote → Interpretation A / B + risk
**Multi-Perspective Notes**: Security/New-hire/Ops or Executor/Stakeholder/Skeptic
**Open Questions (unscored)**: low-confidence findings moved here by self-audit
```

**Git commit trailer format:**
```
Constraint: <active constraint that shaped this decision>
Rejected: <alternative> | <reason for rejection>
Directive: <warning for future modifiers>
Confidence: high | medium | low
Scope-risk: narrow | moderate | broad
Not-tested: <edge case or scenario not covered>
```

**State directory structure:**
```
.omc/
  state/                    # per-mode control plane
  notepad.md                # compaction-resistant memo
  project-memory.json       # cross-session knowledge
  plans/*.md                # execution plans
  notepads/{plan-name}/     # per-plan knowledge capture
    learnings.md, decisions.md, issues.md, problems.md
```

**Artifact descriptor shape:**
`kind`, `path`, `contentHash?`, `createdAt`, `producer`, `sizeBytes?`, `retention`, `expiresAt?`

### Dimension 3 — Interactions (contract level)

**Planner → Analyst:** before generating plan, planner consults analyst; analyst's `### Open Questions` output is extracted and written to `.omc/plans/open-questions.md` by planner

**Executor → Architect:** after 3 failed attempts on same issue, executor escalates with full context; architect performs architectural cross-check; result informs next executor attempt

**Verifier → Team pipeline:** PASS = advance to next stage; FAIL = enter team-fix loop; loop is bounded by max attempts; after bound → `failed` terminal state

**Writer/Reviewer separation:** "Keep authoring and review as separate passes: writer pass creates or revises content, reviewer/verifier pass evaluates it later in a separate lane. Never self-approve in the same active context."

**Planner → `.omc/plans/open-questions.md`:** append format with `## [Plan Name] - [Date]` + `- [ ] [Question] — [Why it matters]`; analyst's open questions are also persisted here

---

## Section 1 — Reference Summary

oh-my-claudecode (OMC) is a production multi-agent orchestration framework for Claude Code. Active npm package (v4.14.4, branded oh-my-claude-sisyphus), GitHub community with Discord, real-world usage signals.

**Behavioral content:** 19 specialized agents organized in 4 lanes (build/analysis, review, domain, coordination). Agent prompts encode sophisticated behavioral protocols: critic's 5-phase adversarial review with realist check and adversarial escalation; verifier's independent-reviewer constraint; planner's one-question-at-a-time rule; executor's scope classification and escalation threshold.

**Structural content:** Agent files use XML-wrapped sections (`<Role>`, `<Why_This_Matters>`, etc.) providing explicit rationale for each rule. Git commit protocol encodes decision context via structured trailers (Constraint/Rejected/Directive). State directory separates control plane (`.omc/state/`) from data plane (`.omc/plans/`, `.omc/notepads/`).

**Interaction content:** Writer/reviewer separation is enforced at architecture level — same context cannot author and approve. Planner consults analyst before plan generation. Executor escalates after 3 failures. Verifier signals pipeline stage transitions.

**Mature:** Active release cadence, CI, npm, Discord. Agent prompt files are well-structured with evidence-backed rationale. Harsh-critic benchmark fixture has active benchmarking infrastructure.

**Experimental/unclear:** MCP server dependencies (omc-state, notepad tools) require setup before full feature set works. ralphthon PRD format is OMC-specific. Plugin marketplace distribution adds deployment complexity.

**Red flag:** `harsh-critic.md` line 2 hardcodes `model: claude-opus-4-6` — direct I6 violation if copied.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `agents/critic.md` → `agents/verifier.md` | **Severity vocabulary** CRITICAL/MAJOR/MINOR for findings | Adversary currently produces flat challenge lists; severity enables grader to triage and route | Add severity rating requirement to adversary SKILL.md challenge domains | High |
| `agents/critic.md` phases 4.5 + 4.75 | **Self-audit + Realist Check** steps with mandatory "Mitigated by:" for downgrades | Prevents false positives from low-confidence adversary findings; calibrates severity | Add Step 3.5 (self-audit) and Step 3.75 (realist check) to adversary SKILL.md | High |
| `agents/critic.md` escalation rule | **ADVERSARIAL mode condition**: 1 CRITICAL or 3+ MAJOR → escalate | Explicit threshold prevents reviewer drift from THOROUGH to ADVERSARIAL without triggering | Add escalation condition to adversary SKILL.md with ADVERSARIAL mode behavior description | High |
| `agents/verifier.md` constraints | **Independent reviewer constraint**: never self-approve same context | WabbleSpec verifier SKILL.md lacks this explicit rule; it's the most commonly violated constraint | Add to verifier SKILL.md `## When to use / when not to use` section | High |
| `agents/verifier.md` output format | **VERIFIED/PARTIAL/MISSING** per-criterion status vocabulary | Wave verifier uses PASS/FAIL/BLOCKED for wave verdicts, but no per-criterion status granularity | Add per-criterion status table to verifier output contract | High |
| `CLAUDE.md` commit_protocol section | **Git decision trailers**: Constraint/Rejected/Directive/Confidence/Scope-risk/Not-tested | Decision context in commits enables future agents to understand WHY a choice was made | Add trailer convention to commit SKILL.md as optional footer extension | Medium |
| `agents/critic.md` Phase 1 | **Pre-commitment predictions** before reading the artifact | Activates deliberate search vs. passive reading; surfaces issues earlier in review | Add as Step 0 to adversary SKILL.md | Medium |
| `agents/planner.md` constraints | **Never ask codebase facts** of user — spawn explore agent instead | WabbleSpec interview already limits batching; this companion rule makes the boundary explicit | Add to interview SKILL.md as a rule alongside existing "no leading questions" | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `benchmarks/harsh-critic/prompts/harsh-critic.md:2` | `model: claude-opus-4-6` hardcoded | Direct I6 violation if this file is copied verbatim | Never copy this file; extract behavioral pattern only | High |
| `CLAUDE.md` model tiers | haiku/sonnet/opus tier names embedded throughout | These are model-family names, not pure capability descriptors | Replace with capability descriptors when adapting; do not copy tier alias names | Medium |
| `AGENTS.md` child_agent_protocol | Requires reading `~/.codex/prompts/{role}.md` before spawn | Codex-specific path; not portable to WabbleSpec | Extract the behavioral pattern (pre-read role prompt), not the path | Low |
| `.omc/` state directory model | Flat JSON state files per mode | Conflicts with WabbleSpec's receipt-chain model; importing OMC's state model would undermine I10 | Do not adopt OMC's state model; keep WabbleSpec receipt chain | High |
| Magic keyword detection | ralph/ultrawork/ralplan triggers are OMC-branded | No value outside OMC; would conflict with WabbleSpec's `/recipe`-first invariant (I1) | Do not adopt magic keywords | Low |
| MCP server dependencies | omc-state, notepad, project-memory tools require external setup | Hard binary dependency; not portable | Do not adopt MCP-dependent patterns |  Medium |
| "Zero learning curve" / "just describe what you want" | Marketing framing conflicts with WabbleSpec's spec-first discipline | WabbleSpec requires spec before execution (I1) | Do not adopt OMC's user-facing framing | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Critic severity vocabulary (CRITICAL/MAJOR/MINOR) | Adapt | No severity in adversary currently | adversary SKILL.md | P1 |
| Critic self-audit + realist check | Adapt | Prevents false positives and severity inflation | adversary SKILL.md | P1 |
| Critic adversarial escalation condition | Adapt | Makes escalation threshold explicit | adversary SKILL.md | P1 |
| Critic pre-commitment predictions | Adapt | Activates deliberate search | adversary SKILL.md | P2 |
| Verifier independent-reviewer constraint | Adapt | Missing in WabbleSpec verifier | verifier SKILL.md | P1 |
| Verifier VERIFIED/PARTIAL/MISSING vocab | Adapt | No per-criterion status today | verifier SKILL.md | P1 |
| Git decision trailers | Adapt | Adds decision context to commit history | commit SKILL.md | P3 |
| Planner "never ask codebase facts" rule | Adapt | Useful companion to interview's no-leading-questions | interview SKILL.md | P4 |
| `harsh-critic.md` with `model: claude-opus-4-6` | Avoid | I6 violation | — | — |
| OMC haiku/sonnet/opus tier names | Avoid | Model-family names violate I6 | — | — |
| `.omc/` state directory model | Avoid | Conflicts with receipt chain (I10) | — | — |
| Magic keywords (ralph/ultrawork) | Avoid | OMC-branded; conflicts with I1 | — | — |
| MCP tool dependencies (omc-state, notepad) | Avoid | Hard binary dependency | — | — |
| ralphthon PRD JSON format | Study Only | OMC-specific execution format | — | — |
| Per-plan notepads | Study Only → Tier 7 | No hook point in WabbleSpec; weeks of effort | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 8 | Same domain: spec-first multi-agent orchestration with specialized roles and verification gates |
| Architecture fit | 5 | OMC uses flat CLAUDE.md injection + hooks; WabbleSpec uses layered modules + receipt chain — different models, but agent prompt patterns transfer cleanly |
| Implementation fit | 7 | Agents-as-Markdown maps well; behavioral additions are additive to existing SKILL.md files |
| Maintenance fit | 8 | Active project, well-documented, evidence-backed rationale in each agent file |
| Risk level | 4 | Main risk: model names in critic/harsh-critic; OMC-specific vocabulary; MCP dependencies — all avoidable by selective extraction |
| Overall usefulness | 7 | Three high-impact adversary/verifier behavioral additions; one medium-impact commit convention |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Behavioral Additions):**
- Adversary SKILL.md: add severity vocabulary, self-audit, realist check, adversarial escalation
- Verifier SKILL.md: add independent-reviewer constraint and VERIFIED/PARTIAL/MISSING vocabulary
- Target: 2 existing SKILL.md files; additive only

**Phase 2 (Low-Risk Additions):**
- Commit SKILL.md: add optional decision trailer convention
- Interview SKILL.md: add "never ask codebase facts" companion rule

**Phase 3 (Watch Only):**
- Planner one-question rule: WabbleSpec interview already has max-3-per-batch; tightening to 1 risks over-slowing discovery sessions
- Writer/reviewer separation: already present in WabbleSpec's I4 (max 3 REVISE) and Verifier design; reinforce rather than re-state

**Phase 4 (Do Not Cross):**
- Model names (I6)
- OMC state model (I10 conflict)
- Magic keyword detection (I1 conflict)
- MCP dependencies

---

## Section 7 — Final Verdict

**Best 3 to adapt:**
1. Critic's self-audit + realist check protocol (`agents/critic.md` phases 4.5–4.75): adds mandatory severity pressure-testing with "Mitigated by:" requirement; directly improves adversary quality
2. Verifier independent-reviewer constraint (`agents/verifier.md` constraints block): "Never self-approve or bless work produced in the same active context" — explicit rule currently absent from WabbleSpec verifier
3. Critic ADVERSARIAL mode escalation (`agents/critic.md` escalation section): explicit condition (1 CRITICAL or 3+ MAJOR) makes escalation deterministic rather than discretionary

**Worst 3 to avoid:**
1. `benchmarks/harsh-critic/prompts/harsh-critic.md:2` — `model: claude-opus-4-6` hardcoded; I6 violation
2. OMC state directory model (`.omc/state/`) — conflicts with WabbleSpec's receipt chain model (I10)
3. haiku/sonnet/opus tier aliases — model-family names throughout CLAUDE.md; I6 if copied

**Classification:** supporting-reference (7/10)

**Recommended next action:** Proceed to ref-plan; extract Phase 1 adversary/verifier improvements; defer git trailers to Phase 2 implementation.

---

## Section 8 — Project Synthesis

### S1 — Receipt-gated adversarial protocol with severity receipts

**What:** Adversary produces findings with CRITICAL/MAJOR/MINOR severity; Grader reads severity distribution from adversary receipt to route verdict — 1 CRITICAL → ADVERSARIAL, 3+ MAJOR → re-challenge, else ACCEPT-WITH-RESERVATIONS

**Reference contribution:** Critic's adversarial escalation threshold + severity vocabulary (`agents/critic.md`)

**Project contribution:** WabbleSpec's adversary receipt schema (`adversary-receipt.schema.json`) + Grader module that already reads `counter_analysis` from adversary receipt

**Target:** `.claude/skills/adversary/SKILL.md` + `.claude/skills/grader/SKILL.md` + `engine/shared/schemas/adversary-receipt.extension.schema.json`

**Gap closed:** Currently adversary produces flat challenge lists; grader has no severity signal from adversary receipt; escalation to ADVERSARIAL mode is undeclared

### S2 — Verifier: delta-format criterion status tracking

**What:** Verifier reads task card's delta format section headers (ADDED/MODIFIED/REMOVED — from OpenSpec ref-adopt) and maps OMC's VERIFIED/PARTIAL/MISSING status per criterion to the correct verification mode (presence/replacement/absence check)

**Reference contribution:** VERIFIED/PARTIAL/MISSING per-criterion vocabulary (`agents/verifier.md`)

**Project contribution:** Delta format section headers in specify SKILL.md (added in previous openspec ref-adopt)

**Target:** `.claude/skills/verifier/SKILL.md`

**Gap closed:** Verifier currently has no per-criterion status vocabulary; delta format headers from openspec are structural but verifier has no instruction to consume them differently per section

---

## Section 9 — Expansion Opportunities

| Capability | Reference location | Why the project lacks it | What it would unlock | Dependencies | Effort | Tier 7? |
|---|---|---|---|---|---|---|
| Per-plan knowledge notebooks | `docs/ARCHITECTURE.md` §Plan Notepad, `.omc/notepads/{plan-name}/learnings.md,decisions.md,issues.md` | WabbleSpec drawers are wing/room scoped, not plan-scoped; no per-execution capture of discovered patterns | Task-scoped learnings that persist across compaction; auto-inject into next session's recipe | session-registry.py already exists; need plan-scoped drawer writer | weeks | Yes |
| Compaction-resistant session memo | `docs/ARCHITECTURE.md` §Notepad, `scripts/pre-compact.*` hook | WabbleSpec's PreCompact hook fires the dream daemon but has no session memo pad that survives compaction and re-injects on resume | Critical session state survives context compaction without relying on user re-stating context | stop-hook.py already fires on_stop events; need notepad writer + on_precompact injection | days | Yes |
