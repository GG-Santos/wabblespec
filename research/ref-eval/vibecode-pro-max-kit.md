# Ref-Eval: vibecode-pro-max-kit

**Reference path:** `C:\Users\Kirsten\Downloads\Orchestrator\vibecode-pro-max-kit`
**Slug:** `vibecode-pro-max-kit`
**Eval date:** 2026-05-30
**Trust level:** MEDIUM (public OSS, active CI, contributors visible, no production receipts)

---

## Step 1b — File Inventory

| Path | Purpose | Size | Status |
|---|---|---|---|
| `README.md` | Full product description, feature table, comparison matrix | large | Read |
| `CLAUDE.md` | Orchestrator routing rules, RIPER-5 protocol, skill registry | large | Read |
| `AGENTS.md` | Codex compat layer, mirrors CLAUDE.md with Codex adaptations | large | Read |
| `process/development-protocols/orchestration.md` | Subagent status codes, context isolation, phase program rules, closeout packet | medium | Read |
| `process/development-protocols/parallel-fan-out.md` | Signal scoring, 5 checkpoints, synthesis protocol, Tier 1/2 tiers | medium | Read |
| `process/development-protocols/intent-clarification.md` | 4-signal ambiguity scoring, 3 tiers, auto-skip conditions, autonomy mode | medium | Read |
| `.claude/agents/vc-execute-agent.md` | EXECUTE mode agent: plan verification, 50% check-in, deviation protocol, closeout | medium | Read |
| `.claude/hooks/session-init.cjs` | Project detection, env var injection, compaction recovery warning, coding level | large | Read |
| `.claude/skills/vc-autoresearch/SKILL.md` | Autonomous metric optimization loop with stuck detection | small | Read |
| `.claude/skills/vc-watzup/SKILL.md` | Read-only repo state handoff scanner | small | Read |
| `.claude/hooks/lib/project-detector.cjs` | Stack/framework detection logic | medium | Skipped — implementation detail, patterns captured from session-init |
| `.claude/hooks/lib/session-state-manager.cjs` | Session state read/write | small | Skipped — plumbing, patterns captured from session-init |
| `.claude/hooks/scout-block.cjs` | Path blocking hook | small | Skipped — hook implementation, pattern understood from README |
| `.claude/hooks/privacy-block.cjs` | Credential blocking hook | small | Skipped — hook implementation, pattern understood from README |
| `.claude/skills/vc-*` (28 remaining) | Individual skill specs | varies | Skipped — representative samples read; skill routing table read from CLAUDE.md |
| `.codex/` | Mirrored agents in TOML format | varies | Skipped — compatibility mirror, no new behavioral content |
| `docs/`, `assets/`, `.github/` | Docs, GitHub config | varies | Skipped — not behavioral content |
| `process/_seeds/` | Scaffold templates | small | Skipped — product-space templates, not framework patterns |

---

## Step 1c — Connection Map

```
CLAUDE.md --[routes]--> .claude/agents/*.md : intent + plan file path
CLAUDE.md --[loads]--> process/context/all-context.md : via @ syntax
CLAUDE.md --[reads]--> process/development-protocols/*.md : referenced inline
AGENTS.md --[mirrors]--> CLAUDE.md : same protocol, Codex adaptations
orchestration.md --[defines]--> subagent status codes : DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT
orchestration.md --[governs]--> vc-execute-agent.md : closeout packet format, risk gate
parallel-fan-out.md --[checkpoints]--> orchestration.md : 5 named lifecycle positions
intent-clarification.md --[scores before]--> routing : pre-delegation ambiguity gate
vc-execute-agent.md --[delegates to]--> vc-tester/vc-debugger/vc-code-reviewer/vc-code-simplifier : quality pipeline
session-init.cjs --[reads]--> lib/project-detector.cjs : stack detection
session-init.cjs --[reads]--> lib/vc-config-utils.cjs : config, plan resolution
session-init.cjs --[writes]--> CLAUDE_ENV_FILE : CK_* env vars consumed by all hooks
session-init.cjs --[reads]--> lib/session-state-manager.cjs : post-compaction state recovery
process/general-plans/active/ --[consumed by]--> vc-execute-agent.md : exact plan file path required
process/context/all-context.md --[routed by]--> domain all-*.md files : routing depth rule
vc-autoresearch --[uses]--> git : atomic commit + revert as memory
vc-watzup --[reads]--> watzup-scan.cjs : local scanner script
```

**Interface contracts:**
- `vc-execute-agent` requires an explicit plan file path from orchestrator — if absent, STOP.
- `session-init` writes `CK_ACTIVE_PLAN` and `CK_SUGGESTED_PLAN` as separate env vars (not merged).
- `all-*.md` router files must be followed to their routing targets; reading only the router is a documented violation.
- Parallel agent per-output format must be `Dimension/Status/Findings/Confidence/Notes` — free-form essays are rejected by the synthesis protocol.

---

## Section 1 — Reference Summary

**Type:** Production-grade AI coding agent harness (behavioral spec + hook infrastructure + multi-agent orchestration protocol). This is not a tutorial or boilerplate — it has active CI, a test suite for hooks, GitHub contributors, and version history.

**Behavioral content:** RIPER-5 lifecycle (Research/Innovate/Plan/Execute/Update-Process) with explicit phase-locking. Intent disambiguation (4-signal scoring, 3-tier clarification). Parallel fan-out checkpoints (5 named positions, signal-count scoring). Post-execute closeout packet with 8-point format. High-risk evidence pack (6 risk classes, 5-JSON schema). Subagent status codes (4 named states). Drift signal scoring (3 levels). Autonomous optimization loop with stuck detection thresholds.

**Structural content:** `.claude/` directory as canonical skill/agent/hook container. `process/` as the product-space knowledge store. Domain-based context routing via `all-{domain}.md` routers. Feature folder lifecycle (5+ artifact promotion). Plan lifecycle (active → completed, date-stamp naming). Development protocols as separate files under `process/development-protocols/`.

**Interaction content:** Orchestrator → subagent delegation via Agent tool with explicit context isolation template. Hooks → env vars → agents (CK_* channel). Session-init → plan resolution → all downstream agents. Execute agent → quality pipeline (tester → code-reviewer → code-simplifier). Parallel agents → per-agent structured output → orchestrator synthesis.

**Maturity:** Active CI (validate.yml), hook unit tests, multiple contributors, i18n translations, issue templates. Core behavioral protocols are well-specified. Hook library is complex but tested.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `orchestration.md:38-57` | Subagent status protocol: DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT | WabbleSpec verifier/executor already has PASS/FAIL/BLOCKED — DONE_WITH_CONCERNS is a missing middle state that captures partial success cleanly | Add DONE_WITH_CONCERNS as a receipt status and verifier verdict option; define handling rules (correctness concerns = action items, not just notes) | High |
| `orchestration.md:165-208` | Post-execute closeout packet: 8-point structured format with plan classification | Executor SKILL.md has no standardized closeout format — this prevents vague completion reporting | Add `## Closeout Packet` section to executor SKILL.md with the 3 classification labels and 8 content fields | High |
| `orchestration.md:211-217` | Drift signal scoring: LOW/MEDIUM/HIGH with explicit conditions | Archive SKILL.md has no urgency scoring for when to capture learnings — this adds a mechanical decision rule | Add drift signal scoring block to archive SKILL.md; drives "Archive urgency" language | High |
| `parallel-fan-out.md` | Fan-out signal scoring: 5 signals, 3 thresholds, per-agent structured output format | Decompose already creates wave plans — fan-out scoring would surface when parallel agents add value vs. adding cost | Add fan-out checkpoint language to decompose SKILL.md; per-agent output format to verifier | Medium |
| `intent-clarification.md` | 4-signal ambiguity scoring + 3 tiers + auto-skip conditions | Recipe skill has no tiered clarification — currently all-or-nothing. This prevents over-asking on clear requests and under-asking on vague ones | Add intent clarification tier protocol as a reference doc; wire into recipe cold-start | Medium |
| `vc-execute-agent.md:79-85` | 50% mid-implementation check-in: explicit pause with status update + "continue or return to PLAN?" | Executor SKILL.md has no mid-wave check-in gate. Long waves can drift silently. | Add mid-wave check-in instruction to executor SKILL.md at ~50% completion milestone | Medium |
| `vc-autoresearch/SKILL.md` | Autonomous loop: ONE atomic change, commit before verify, 5-discard strategy shift, 10-discard stop | Benchmark skill exists but lacks the autonomous iteration discipline — stuck detection thresholds and atomic-change rule are precise | Enhance benchmark SKILL.md with stuck detection thresholds (5/10 consecutive discards → strategy shift / stop) and atomicity rule | Medium |
| `orchestration.md:243-265` | High-risk evidence pack: 6 risk classes + 5-JSON schema (risk-gate.json, context-snippets.json, etc.) | Guard already checks authority and command risk — but has no structured evidence pack requirement for high-risk classes | Add high-risk evidence pack schema to guard SKILL.md invariant checklist | Medium |
| `session-init.cjs:339-347` | Compaction recovery warning: explicit re-confirm gate with exact wording | WabbleSpec session-start hook doesn't have a compaction-specific approval gate reminder | Add compaction recovery warning block to wabblespec-session-start.js | Medium |
| `parallel-fan-out.md:183-205` | Per-agent output format for parallel synthesis: `Dimension / Status: PASS\|CONCERN\|FAIL / Findings / Confidence / Notes` | WabbleSpec uses subagents but has no contract for structured parallel output — this prevents synthesis from being vague | Add per-agent output format to wabblespec-guard.md and wabblespec-verifier.md agent specs | Low |
| `intent-clarification.md:141-143` | Autonomy mode boundaries: autonomy phrases do NOT override EXECUTE gate or plan review | WabbleSpec has no autonomy phrase detection — useful to define what "just do it" grants and what it cannot override | Add autonomy mode boundary table to executor SKILL.md or recipe SKILL.md | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `CLAUDE.md` (RIPER-5 framing) | Importing RIPER-5 as a named methodology conflicts with I1 | WabbleSpec's spec system is the single source of truth; an alternate lifecycle framework would split authority | Extract behavioral patterns only; never import RIPER-5 as a concept or name | High |
| `vc-autoresearch/SKILL.md` | `AskUserQuestion` tool call in skill — I6 violation if ported literally | WabbleSpec uses `~~` capability placeholders, not tool names | Replace with capability placeholder form `~~structured-question` or with prose instruction | Medium |
| `CLAUDE.md` (orchestrator does no work itself) | Strict delegation-only orchestrator conflicts with WabbleSpec's Executor model | In WabbleSpec, the Executor reads and acts — it is not a pure router. Importing the no-work-orchestrator rule would break existing module behavior | Do not import the RIPER-5 orchestrator philosophy; extract only protocol-level rules | Medium |
| `process/` directory conventions | Product-space process/ folder is for users' projects, not framework | WabbleSpec's product space is the project root; importing process/ conventions would create user-facing collisions | Frame any adapted patterns as WabbleSpec framework-space equivalents, not direct copies | Medium |
| `CLAUDE.md:46-48` (trivial fix threshold: single-file, <15 lines, no schema/API/auth) | Exact thresholds may not translate to WabbleSpec's complexity scoring | Locking to specific line-count thresholds can create gaming behavior | Use as an example of a trivial-fix decision rule; do not copy literal thresholds | Low |

---

## Section 4 — Adapt vs. Avoid

| Reference Part | Action | Reason | Target Area | Priority |
|---|---|---|---|---|
| Subagent status codes (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT) | Adapt | Fills missing middle state in WabbleSpec verifier | executor SKILL.md, verifier SKILL.md | P1 |
| Post-execute closeout packet (8-point format, 3 classifications) | Adapt | Standardizes execution completion reporting | executor SKILL.md | P1 |
| Drift signal scoring (LOW/MEDIUM/HIGH) | Adapt | Adds mechanical archive urgency decision | archive SKILL.md | P1 |
| 50% mid-implementation check-in | Adapt | Adds mid-wave drift gate | executor SKILL.md | P1 |
| High-risk evidence pack (6 classes, 5-JSON schema) | Adapt | Strengthens guard for high-risk waves | guard SKILL.md | P2 |
| Compaction recovery warning | Adapt | Closes approval gate bypass on compact | wabblespec-session-start.js | P2 |
| Parallel fan-out signal scoring + per-agent output format | Adapt | Improves parallel wave planning and synthesis | decompose SKILL.md | P2 |
| Intent clarification tiered protocol | Adapt (as reference doc) | Pre-task ambiguity gate for recipe | .wabblespec/engine/shared/references/ | P2 |
| Autonomy mode boundary definition | Adapt | Clarifies what "just do it" grants and cannot override | executor SKILL.md | P3 |
| RIPER-5 as a named methodology | Avoid | I1 — WabbleSpec is the spec system | — | — |
| AskUserQuestion tool name in SKILL.md | Avoid | I6 — use capability placeholder | — | — |
| Delegation-only orchestrator philosophy | Avoid | Conflicts with WabbleSpec Executor model | — | — |
| `process/` directory conventions | Avoid | Product-space collisions | — | — |
| Literal trivial-fix thresholds (15 lines) | Study only | May inform complexity scoring calibration | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 8 | Both are spec-driven, receipt-gated, phase-locked agent harnesses. High conceptual overlap. |
| Architecture fit | 6 | WabbleSpec uses waves/receipts/guard; vibecode uses RIPER-5/plans/hooks. Different execution models but shared principles. |
| Implementation fit | 7 | Behavioral protocols (status codes, scoring, formats) map cleanly to WabbleSpec SKILL.md additions. Hook patterns are CJS — WabbleSpec hooks are also JS. |
| Maintenance fit | 8 | Additive changes only. No framework restructuring required. |
| Risk level | 3 | Low risk — adapting protocols, not replacing architecture. Main risk is RIPER-5 philosophy bleed. |
| Overall usefulness | 8 | Supporting reference — several high-value behavioral patterns not present in WabbleSpec. |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — additive protocol rules):**
1. Subagent status codes → executor SKILL.md + verifier SKILL.md (`orchestration.md:38-57`)
2. Post-execute closeout packet format → executor SKILL.md (`orchestration.md:165-208`)
3. Drift signal scoring → archive SKILL.md (`orchestration.md:211-217`)
4. 50% mid-wave check-in → executor SKILL.md (`vc-execute-agent.md:79-85`)

**Phase 2 (Low-Risk Adaptation — reference docs and module augmentation):**
5. High-risk evidence pack schema → guard SKILL.md (`orchestration.md:243-265`)
6. Compaction recovery warning → wabblespec-session-start.js (`session-init.cjs:339-347`)
7. Fan-out signal scoring → decompose SKILL.md (`parallel-fan-out.md`)
8. Per-agent output format → wabblespec-verifier.md agent spec (`parallel-fan-out.md:183-205`)
9. Intent clarification tiered protocol → new reference doc (`intent-clarification.md`)

**Phase 3 (Deeper Integration — synthesis):**
10. Autonomous optimization loop discipline → benchmark SKILL.md
11. Autonomy mode boundary table → executor or recipe SKILL.md

**Phase 4 (Do Not Cross):**
- RIPER-5 philosophy, RIPER-5 lifecycle names, delegation-only orchestrator rule, product-space process/ conventions, AskUserQuestion tool calls

---

## Section 7 — Final Verdict

**Best 3 to steal:**
1. **Subagent status codes** (`orchestration.md:38-57`) — DONE_WITH_CONCERNS fills a real gap in WabbleSpec's PASS/FAIL binary. The handling rules (correctness concerns = action items; never retry same blocked approach 3x) are operationally precise.
2. **Post-execute closeout packet** (`orchestration.md:165-208`) — The 8-point format with 3 classification labels (Ready/Keep/Reconcile) is exactly what WabbleSpec's executor closing section lacks. Prevents vague "done" declarations.
3. **Parallel fan-out signal scoring** (`parallel-fan-out.md`) — The signal-count table (5 signals → LOW/MEDIUM/HIGH) with per-agent structured output format gives decompose and the verifier a mechanical basis for parallel agent recommendations. Currently absent from WabbleSpec.

**Worst 3 to avoid:**
1. **RIPER-5 as a named framework** (`CLAUDE.md` throughout) — Directly conflicts with I1. WabbleSpec owns the spec lifecycle.
2. **AskUserQuestion tool calls in SKILL.md** (`vc-autoresearch/SKILL.md`) — I6 violation if copied literally. Must be converted to capability placeholder form.
3. **Delegation-only orchestrator rule** (`CLAUDE.md:38-43`) — "You do NOT perform research yourself" conflicts with WabbleSpec's Executor model where the active agent does the work, not just routes.

**Classification: supporting-reference (8/10)**

**Recommended next action:** Proceed to Phase 1 implementation — four executor/verifier/archive additions. These are additive, non-breaking, and address real gaps.

---

## Section 8 — Project Synthesis

| Synthesis Idea | Reference Contribution | Project Contribution | Target | Gap Closed |
|---|---|---|---|---|
| Receipt-aware closeout classification | 3-state classification (Ready/Keep/Reconcile) + closeout packet format | Receipt chain: each phase writes a receipt read by the next | executor SKILL.md | Executor currently has no structured way to express "code done but evidence incomplete" — a receipt can carry closeout-state as a field |
| Guard-as-risk-gatekeeper | 6 risk classes + 5-JSON evidence pack schema | Guard already checks authority/command-risk/receipt chain | guard SKILL.md + guard/skill-rules.json | Guard currently has no high-risk class taxonomy — adding it closes the gap where auth/billing waves proceed without structured evidence |
| Drift-scored archive urgency | Drift signal scoring (LOW/MEDIUM/HIGH) | Archive already writes receipts and bumps version | archive SKILL.md | Archive has no urgency signal — adding drift scoring ties archive priority to actual change magnitude |

---

## Section 9 — Expansion Opportunities

| Capability | Reference Location | Why WabbleSpec Lacks It | What It Would Unlock | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| Autonomous metric optimization loop | `vc-autoresearch/SKILL.md` + `references/autonomous-loop-protocol.md` | WabbleSpec has benchmark but no autonomous iteration loop with git-backed rollback | Would enable WabbleSpec to self-optimize measurable framework quality metrics (quality-floor gate scores, test pass rates, receipt chain coverage) without human-per-iteration approval | Active git repo, mechanical verify command, benchmark skill | weeks | Yes |
| Session handoff scanner (watzup) | `vc-watzup/SKILL.md` + `scripts/watzup-scan.cjs` | WabbleSpec has no cross-session state inspector that summarizes active tasks, waves, and receipts into a handoff report | Would give any session a read-only snapshot of where work stands without reading every state file | session-state.py, wave-plan-writer.py | days | Yes |
| Context router with routing depth enforcement | `CLAUDE.md:69`, `orchestration.md:72` (routing depth rule) | WabbleSpec's scope.md is a boundary file, not a knowledge router; no depth rule enforces loading deeper docs | Would structure WabbleSpec's knowledge base (references/, rules/) into a queryable routing tree | scope-frame SKILL.md, reference infrastructure | weeks | No (partial — routing depth rule is Tier 1) |
