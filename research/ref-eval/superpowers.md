# Ref-Eval: superpowers

**Reference:** `C:\Users\Kirsten\Downloads\Orchestrator\superpowers`
**Slug:** `superpowers`
**Type:** Production agent-workflow plugin (v5.1.0, MIT, Jesse Vincent / Prime Radiant)
**Evaluated:** 2026-05-30
**Overall verdict:** supporting-reference (8/10)

---

## Step 1b — File Inventory

| File | Purpose | Size | Key contents | Status |
|---|---|---|---|---|
| `skills/brainstorming/SKILL.md` | Socratic spec-before-code gate | medium | HARD-GATE, spec self-review 4-point, visual companion | Read |
| `skills/dispatching-parallel-agents/SKILL.md` | Domain isolation for parallel dispatch | small | When-NOT-to-parallelize decision tree, domain grouping rules | Read |
| `skills/executing-plans/SKILL.md` | Batch plan execution | small | Stop-on-blocker rule, finishing-a-development-branch terminal | Read |
| `skills/finishing-a-development-branch/SKILL.md` | Merge/PR/keep/discard lifecycle | medium | GIT_DIR!=GIT_COMMON detection, provenance-based cleanup, worktree safety | Read |
| `skills/receiving-code-review/SKILL.md` | Anti-sycophancy review reception | medium | Forbidden responses table, YAGNI check, implementation order | Read |
| `skills/requesting-code-review/SKILL.md` | Dispatch code reviewer subagent | small | SHA-based git range, mandatory/optional triggers | Read |
| `skills/subagent-driven-development/SKILL.md` | Orchestrate per-task subagents | large | Two-stage review ordering (spec first, quality second), model selection tiers, status handling | Read |
| `skills/systematic-debugging/SKILL.md` | 4-phase root cause mandate | medium | Phase 4.5 — 3-fix architectural escalation, rationalization tables, red flags | Read |
| `skills/test-driven-development/SKILL.md` | RED-GREEN-REFACTOR iron law | medium | Iron Law, rationalization table, red flags list, "spirit vs letter" close | Read |
| `skills/verification-before-completion/SKILL.md` | Evidence-before-claim gate | small | 5-step gate function (IDENTIFY→RUN→READ→VERIFY→CLAIM) | Read |
| `skills/using-git-worktrees/SKILL.md` | Isolated workspace lifecycle | medium | Step 0 detect-first, native tool preference, submodule guard | Read |
| `skills/using-superpowers/SKILL.md` | Bootstrap skill injected at session start | small | 1% invocation rule, instruction priority order, skill types (rigid/flexible) | Read |
| `skills/writing-plans/SKILL.md` | Implementation plan structure | medium | No-placeholders rule, bite-sized task granularity, self-review protocol | Read |
| `skills/writing-skills/SKILL.md` | TDD-for-documentation authoring | large | CSO description field rule, rationalization bulletproofing, RED-GREEN-REFACTOR for skills | Read |
| `skills/subagent-driven-development/implementer-prompt.md` | Implementer dispatch template | small | Status codes (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT), self-review checklist | Read |
| `skills/subagent-driven-development/spec-reviewer-prompt.md` | Spec compliance reviewer template | small | "CRITICAL: Do Not Trust the Report" skepticism block, independent code-read mandate | Read |
| `skills/subagent-driven-development/code-quality-reviewer-prompt.md` | Code quality reviewer template | small | Delegates to code-reviewer.md template, file-responsibility check | Read |
| `skills/requesting-code-review/code-reviewer.md` | Code reviewer subagent template | medium | Critical/Important/Minor taxonomy, strengths-before-issues calibration, ready-to-merge verdict | Read |
| `hooks/session-start` | Bash bootstrap injection | small | Embeds using-superpowers content; multi-harness JSON output format | Read |
| `hooks/hooks.json` | Hook config | tiny | SessionStart matcher: `startup\|clear\|compact` | Read |
| `.claude-plugin/plugin.json` | Plugin manifest | tiny | v5.1.0, MIT | Read |
| `CLAUDE.md` / `AGENTS.md` | Contributor guidelines | medium | AI-agent-specific pre-submission checklist; 94% PR rejection rate; acceptance test for new harnesses | Read |
| `README.md` | Overview and install | medium | Workflow sequence, philosophy, harness list | Read |
| `RELEASE-NOTES.md` | v5.1.0 changes | medium | Worktree rototill, code review consolidation, SDD improvements | Read |
| `docs/plans/`, `docs/superpowers/plans/` | Past feature design docs | large | superpowers-internal planning artifacts | Skipped — internal design history, not technique reference |
| `assets/`, `scripts/`, `.opencode/` | Images, sync tooling, OpenCode plugin | varies | Not technique reference | Skipped |

---

## Step 1c — Connection Map

```
hooks/session-start [bash] --injects--> using-superpowers [full content as context]
hooks/hooks.json --configures--> session-start: fires on startup|clear|compact
using-superpowers --establishes--> all skills: Skill tool invocation rule

brainstorming --invokes--> writing-plans [terminal state]
writing-plans --invokes--> subagent-driven-development OR executing-plans [user choice]
subagent-driven-development --dispatches--> implementer-prompt.md [per task]
subagent-driven-development --dispatches--> spec-reviewer-prompt.md [after implementer, BEFORE quality]
subagent-driven-development --dispatches--> code-quality-reviewer-prompt.md [after spec PASS]
code-quality-reviewer-prompt.md --uses--> requesting-code-review/code-reviewer.md [reuse]
subagent-driven-development --invokes--> finishing-a-development-branch [terminal]
executing-plans --invokes--> finishing-a-development-branch [terminal]
using-git-worktrees --precedes--> subagent-driven-development / executing-plans
requesting-code-review --dispatches--> code-reviewer.md [SHA-based diff]
receiving-code-review --governs--> response to reviewer output
test-driven-development --used by--> implementer subagents
systematic-debugging --governs--> any bug fix (Phase 1-4 mandate)
verification-before-completion --governs--> any completion claim
writing-skills --governs--> all skill authoring
```

**Critical contracts:**
- `spec-reviewer-prompt.md` → receives `[FULL TEXT of task requirements]` + `[From implementer's report]`; contract broken if implementer report is trusted without code-read
- `requesting-code-review` → `code-reviewer.md` needs exact `{BASE_SHA}`, `{HEAD_SHA}` — SHA drift breaks review range
- `finishing-a-development-branch` reads `GIT_DIR` vs `GIT_COMMON` — incorrect detection causes wrong menu presentation
- Two-stage review ordering enforced: spec compliance MUST pass before code quality review is dispatched — violation would allow over-built or under-built implementations to clear the quality gate

---

## Section 1 — Reference Summary

**Type:** Production agent workflow plugin. Active releases (v5.1.0, April 2026), real integration tests, cross-harness deployment (Claude Code, Codex, Gemini, Cursor, Copilot CLI). Not experimental.

**Behavioral content:** Workflow sequencing logic (spec-before-code gate, plan-before-execute, review-after-each-task), quality enforcement rules (TDD iron laws, verification evidence gates, root-cause investigation mandates), rationalization tables with explicit counters, Red Flags lists for self-monitoring, architectural escalation gate (3-fix threshold), code review taxonomy (Critical/Important/Minor), git worktree lifecycle management, model tier selection by task complexity.

**Structural content:** Flat `skills/` namespace, frontmatter YAML (`name` + `description`). CSO (Claude Search Optimization) principles for description fields. Graphviz dot flowcharts for decision-heavy paths. Prompt templates as separate `.md` files alongside SKILL.md.

**Interaction content:** Session-start hook injects bootstrap content via JSON `hookSpecificOutput.additionalContext`. Skill chain: brainstorming → writing-plans → subagent-driven-development → finishing-a-development-branch. Two-stage review per task (spec compliance BEFORE code quality — order enforced). Subagents isolated from orchestrator context by design.

**Maturity signals:** Integration tests (`tests/claude-code/test-requesting-code-review.sh` plants SQL injection bugs and asserts reviewer flags them), TDD-validated worktree behavior across five harnesses, active changelog with regression notes. Mature and stable.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `spec-reviewer-prompt.md` lines 28-36 | "CRITICAL: Do Not Trust the Report" — skeptical artifact reading mandate | WabbleSpec verifier reads executor receipts; if receipt is optimistic, verifier may PASS a wave it should fail | Add skepticism note before verifier Step 1: "Read actual artifact content; do not rely solely on executor wave receipt" | High |
| `systematic-debugging/SKILL.md` Phase 4.5 "3+ Fixes Failed" | Architectural escalation gate after 3 failed REVISE cycles | WabbleSpec verifier has BLOCKED at cycle 4 but no pattern-detection to distinguish implementation bugs from architectural problems | Add to verifier Step 4: when REVISE cycles = 3 AND each cycle revealed new coupling/shared-state issues, surface `ARCHITECTURE_ESCALATION` signal alongside BLOCKED | High |
| `subagent-driven-development/SKILL.md` Model Selection section | Task complexity → model tier mapping (1-2 files → cheap; multi-file integration → standard; design judgment → capable) | WabbleSpec model-router has capability descriptors and task shapes but no input-signal mapping from structural complexity | Add "Task complexity signals" subsection to model-router routing process section | High |
| `writing-skills/SKILL.md` CSO section, specifically "Description = When to Use NOT What the Skill Does" + empirical evidence | Workflow-summary descriptions cause agents to follow description instead of reading skill body | WabbleSpec's CLAUDE.md has related guidance but lacks the specific prohibition and empirical evidence | Add to CLAUDE.md skill authoring conventions: "Never summarize the skill's workflow in the description field" with rationale | High |
| `verification-before-completion/SKILL.md` 5-step gate function | IDENTIFY→RUN→READ→VERIFY→CLAIM before any completion claim | WabbleSpec executor writes execution-receipt.json after all waves; this gate prevents premature completion claims | Add to executor: before writing execution-receipt.json, explicitly run the evidence gate | Medium |
| `systematic-debugging/SKILL.md` Phase 1 multi-component diagnostic instrumentation | "For each component boundary: log what enters, what exits, verify env/config propagation" | WabbleSpec wave-fix discovers findings but has no systematic diagnostic instrumentation protocol for root cause | Add to wave-fix SKILL.md: before attempting fixes, add diagnostic instrumentation at component boundaries to find WHERE the issue is | Medium |
| `writing-skills/SKILL.md` + `test-driven-development/SKILL.md` rationalization tables | Explicit rationalization counters and Red Flags lists close bypass loopholes | WabbleSpec guard/executor state rules but don't enumerate the specific rationalizations agents use to bypass them | Add rationalization tables to guard/SKILL.md (Layer bypass rationalizations) and executor/SKILL.md (checkpoint skip rationalizations) | Medium |
| `brainstorming/SKILL.md` Spec Self-Review, 4-point | Inline spec quality check (placeholder scan, consistency, scope, ambiguity) | WabbleSpec specify has a quality gate but no structured inline self-review after writing | Add 4-point self-review to specify SKILL.md after Step 4 (write task card) | Medium |
| `dispatching-parallel-agents/SKILL.md` When NOT to use section | Domain isolation decision tree: when failures are related / need full context / shared state → don't parallelize | WabbleSpec decompose writes wave plans with parallelism topology but has no guidance for when NOT to parallelize waves | Add independence criteria to decompose SKILL.md wave design section | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `using-superpowers/SKILL.md` "even 1% chance → invoke skill" | Token overload with 108 WabbleSpec skills | Continuous skill lookups would exhaust context budget on every turn | Do not adopt; WabbleSpec uses explicit phase-gated skill invocation | Medium |
| `brainstorming/SKILL.md` + `writing-plans/SKILL.md` save paths | Hardcoded product-space paths (`docs/superpowers/specs/`) | I11 violation if applied literally | Treat as structural reference only; WabbleSpec paths are already defined | Low |
| `test-driven-development/SKILL.md` Iron Law "delete pre-test code" | Anti-pattern for framework module scaffolding | WabbleSpec scaffolds module shells (SKILL.md, receipts, schemas) before behavior tests; Iron Law would create unnecessary rework | Do not adopt the deletion mandate literally; adapt the principle (verify behavior before marking complete) | Low |
| `writing-skills/SKILL.md` agentskills.io URL | External dependency reference | URL-based spec; WabbleSpec authoring conventions are self-contained in CLAUDE.md | Extract principles only; do not reference external URL | Low |
| `subagent-driven-development/SKILL.md` model tier names ("cheap/standard/capable") | I6 violation | These are relative tier names, not model identity — but adopting them verbatim could create confusion | Map to WabbleSpec capability descriptor vocabulary (`code-generation`, `synthesis`, `analysis`) | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Spec reviewer skepticism (spec-reviewer-prompt.md) | Adapt | Closes real verifier gap | `verifier/SKILL.md` Step 1 | P1 |
| Architecture escalation gate (systematic-debugging Phase 4.5) | Adapt | No architectural pattern detection in verifier REVISE loop | `verifier/SKILL.md` Step 4 | P1 |
| Task complexity → capability signals (subagent-driven-development) | Adapt | model-router lacks input-signal side of routing | `model-router/SKILL.md` | P1 |
| CSO workflow-summary prohibition (writing-skills) | Adapt | Strengthen WabbleSpec skill authoring convention | `CLAUDE.md` | P1 |
| Evidence gate 5-step (verification-before-completion) | Adapt | Concretizes I10 with actionable sequence | `executor/SKILL.md` | P2 |
| Diagnostic instrumentation pattern (systematic-debugging Phase 1) | Adapt | Better root-cause isolation in wave-fix | `wave-fix/SKILL.md` | P2 |
| Rationalization tables (writing-skills, TDD) | Adapt | Close bypass loopholes in guard/executor | `guard/SKILL.md`, `executor/SKILL.md` | P2 |
| Spec self-review 4-point (brainstorming) | Adapt | Inline spec quality gate for specify | `specify/SKILL.md` | P2 |
| Parallel dispatch decision tree (dispatching-parallel-agents) | Adapt | Wave independence criteria for decompose | `decompose/SKILL.md` | P3 |
| 1% invocation rule (using-superpowers) | Avoid | Token overload with 108 skills | N/A | — |
| Hardcoded product-space paths | Avoid | I11 violation | N/A | — |
| Iron Law deletion mandate (TDD) | Study only | Conflicts with framework scaffolding pattern | N/A | — |
| agentskills.io external URL | Avoid | External dependency | N/A | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 9 | Both are skill-driven agent workflow systems with behavioral enforcement via structured SKILL.md files |
| Architecture fit | 7 | Skills/hooks/subagents map to WabbleSpec's modules/receipts/subagents; receipt chain has no superpowers analog |
| Implementation fit | 8 | SKILL.md format identical; hook system analogous; patterns can be ported directly as additive edits |
| Maintenance fit | 8 | Superpowers is actively maintained (v5.1.0, April 2026) with real tests; patterns are empirically validated |
| Risk level | 2 | All adoptions are additive or editorial; no architectural changes required |
| Overall usefulness | 8 | Clear high-value behavioral additions; most items are short edits to existing files |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — Additive to existing files):**
1. `spec-reviewer-prompt.md` skepticism block → `verifier/SKILL.md` Step 1
2. `systematic-debugging/SKILL.md` Phase 4.5 → `verifier/SKILL.md` Step 4 REVISE loop
3. `subagent-driven-development/SKILL.md` Model Selection → `model-router/SKILL.md`
4. `writing-skills/SKILL.md` CSO prohibition → `CLAUDE.md` skill authoring conventions

**Phase 2 (Low-Risk Augmentation):**
5. `verification-before-completion/SKILL.md` gate → `executor/SKILL.md` execution receipt
6. `systematic-debugging/SKILL.md` Phase 1 instrumentation → `wave-fix/SKILL.md`
7. Rationalization tables → `guard/SKILL.md` + `executor/SKILL.md`
8. Spec self-review 4-point → `specify/SKILL.md`

**Phase 3 (Deeper Integration):**
9. Parallel dispatch decision tree → `decompose/SKILL.md`

**Phase 4 (Do Not Cross):**
- 1% invocation rule
- Iron Law deletion mandate
- Hardcoded product paths
- agentskills.io external reference

---

## Section 7 — Final Verdict

**Classification: supporting-reference (8/10)**

**Best 3 to steal:**
1. **Spec reviewer skepticism** (`spec-reviewer-prompt.md`, lines 28-36) — "Do Not Trust the Report; read the actual code." WabbleSpec verifier currently reads executor receipts at face value. Independent artifact read mandate would close a real verification gap.
2. **Architectural escalation** (`systematic-debugging/SKILL.md`, Phase 4.5) — When REVISE cycles all fail because each fix reveals new coupling, this is an architecture problem not an implementation bug. WabbleSpec has no signal to distinguish these two failure modes.
3. **CSO description field rule** (`writing-skills/SKILL.md`, CSO section) — Empirical evidence that workflow-summarizing descriptions cause agents to follow the description instead of reading the skill body. Directly applicable to WabbleSpec's 108 skills. CLAUDE.md has related guidance but lacks this specific finding.

**Worst 3 to avoid:**
1. **1% invocation rule** (`using-superpowers/SKILL.md`) — Catastrophic with 108 skills; WabbleSpec uses phase-gated explicit invocation.
2. **Iron Law deletion mandate** (`test-driven-development/SKILL.md`) — Conflicts with framework module scaffolding patterns.
3. **External URL reference** (`writing-skills/SKILL.md`, agentskills.io) — External dependency; WabbleSpec conventions are self-contained.

**Recommended next action:** Implement Phase 1 items (4 targeted edits).

---

## Section 8 — Project Synthesis

| Synthesis Idea | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Receipt-gated spec compliance | Skeptical independent verification before marking complete (spec-reviewer-prompt.md) | Receipt chain with explicit phase receipts (research→plan→execution→verification) | `verifier/SKILL.md` | Verifier currently reads executor receipt; combining skepticism block with receipt integrity check creates a two-level fidelity gate: receipt exists AND artifact content matches receipt claims |
| Escalation receipt type | Architectural escalation after 3-fix failure (systematic-debugging Phase 4.5) | 17-type receipt system (receipt-writer.py) | `executor/SKILL.md`, `receipt-writer.py` | No architectural-escalation receipt exists; combining the escalation gate with WabbleSpec's receipt chain creates a durable audit trail when executor hits architecture limits |
| Task complexity → capability input signal | Concrete 1-2 files/multi-file/design tier mapping (subagent-driven-development Model Selection) | model-router with capability descriptor vocabulary | `model-router/SKILL.md` | model-router dispatches by capability descriptor but lacks structural complexity as an input signal; the superpowers tier mapping is the missing input-side description |

---

## Section 9 — Expansion Opportunities

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| Skill authoring TDD test harness | `writing-skills/SKILL.md` testing methodology; RED-GREEN-REFACTOR for skills | WabbleSpec has Benchmark module but no dedicated pressure-test-subagent workflow for validating new skills before deployment | Self-testing new WabbleSpec skills; empirically closing rationalization loopholes before skills go live | Subagent infrastructure (already present), Benchmark fixtures | days | Yes |
| Visual companion for brainstorming | `skills/brainstorming/visual-companion.md`, `scripts/server.cjs`, `scripts/helper.js` | WabbleSpec has brainstorm skill but no browser-based visual mockup companion; no HTTP server component | Real-time diagram and mockup display during spec conversations | Node.js server, browser environment | weeks | Yes |
