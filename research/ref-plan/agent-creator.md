# Integration Plan -- agent-creator

**generated_at:** 2026-05-29T14:43:53Z
**ref_eval_report:** research/ref-eval/agent-creator.md
**risk_appetite:** balanced
**integration_goal:** Tighten WabbleSpec's subagent and skill-authoring hygiene — scope subagent toolsets to minimal viable sets, disambiguate overlapping skill triggers, and document the subagent-vs-skill rationale — without importing any I6-violating model guidance.

## Signal Summary

ref-eval classified `agent-creator` as a **supporting reference** (overall 6/10): a sound guidance skill whose most copyable specifics (model names, token figures, the `skills:` field) collide with WabbleSpec invariants or are unverified, but whose *principles* expose real hygiene gaps in WabbleSpec's own subagents. Five benefits were found (B1-B5); three survive the exclusion filter as actionable backlog items, and four ref-eval "Avoid"/study-only items are excluded outright.

## Exclusion List

| Item | Source in ref-eval | Reason Excluded |
|---|---|---|
| Hardcoded `model:` names / model-selection guidance | Sec 3 R1, Sec 4 "Avoid" (`SKILL.md:50,65,103-108,282`) | Direct I6 violation (no model names in framework files). Hard stop. |
| Per-tool token-budget numbers | Sec 3 R2, Sec 4 "Avoid" (`SKILL.md:98-101`) | Unsourced; conflicts with the evidence ethos (I8). Adopt the principle (B1), not the figures. |
| `skills:` auto-load frontmatter field | Sec 3 R3, Sec 4 "Avoid" (`SKILL.md:52,246-251`) | Unverified against the agent schema; WabbleSpec already controls skill availability via recipe.json `active_skills` + sync `--filter-recipe`. |
| Verbatim reference prose | Sec 3 R4, Sec 4 "Avoid" (whole ref) | Unknown license (no LICENSE in folder). Adapt ideas only. |
| Token-discipline heuristic (B4) | Sec 2 B4, Sec 4 "Study only" (`SKILL.md:235-240`) | No artifact to integrate — corroborates existing I12 + Reference Routing convention. Citation only, not backlog work. |
| Boundary/Handoff templates (B5) | Sec 2 B5, Sec 4 "Study only" (`prompt-patterns.md:173-217`) | WabbleSpec's receipt chain already encodes handoffs; nothing concrete to add. |

## Integration Backlog (ranked)

| Rank | ID | Item | Type | Phase | Impact | Risk | Score |
|---|---|---|---|---|---|---|---|
| 1 | B1 | Scope `wabblespec-guard` / `wabblespec-verifier` toolsets to minimal viable sets | config | 1 | High | Medium | 7 |
| 2 | B2 | Add negative triggers to overlapping skill descriptions (ref-* trio, review trio) | docs/config | 1 | Medium | Low | 5 |
| 3 | B3 | Document subagent-vs-skill decision rubric in authoring conventions | docs | 2 | Medium | Medium | 4 |

Score = (impact×2) + project_fit − risk; High=3, Medium=2, Low=1. Project fit: B1=High, B2=Medium, B3=Medium.

## Phase 1 -- Safe Wins

**B1 — Scope Guard/Verifier subagent toolsets**
- **What:** Replace the `All tools` grant on the `wabblespec-guard` and `wabblespec-verifier` subagents with an explicit minimal toolset that matches what each actually invokes.
- **Where:** The two agent definitions under `.claude/agents/` (`wabblespec-guard`, `wabblespec-verifier`) and their source-of-truth definitions in `.wabblespec/engine/` if the `.claude/agents/` copies are sync-generated.
- **How:** (1) Read each agent's prompt body and enumerate every tool it actually calls (Guard: reads task card/scope/skill-rules, runs `guard-check.py` → Read, Grep, Glob, Bash; Verifier: reads wave artifacts, runs verification scripts/receipt-writer → Read, Grep, Glob, Bash). (2) Replace `tools: *` / "All tools" with that explicit comma-separated list. (3) Do NOT use the reference's token-count justification — justify by actual invocation only.
- **Gate:** Run each subagent against a representative wave (or its `tests/acceptance.md` if present) and confirm it still returns a valid JSON guard/verification receipt and passes. A removed-tool regression manifests as a tool-call failure inside the subagent — that gate catches it. This becomes a ref-comp checkpoint.
- **Reference location:** `SKILL.md:90-101` (Minimal Viable Toolset); anti-pattern at `prompt-patterns.md:333-343`.

**B2 — Negative triggers on overlapping skill descriptions**
- **What:** Add a one-line negative trigger to skills whose trigger surfaces overlap, pointing at the sibling skill that owns the adjacent case.
- **Where:** SKILL.md description frontmatter for the ref-* trio (`ref-eval`, `ref-plan`, `ref-comp`) and the review trio (`reviewer`, `adversary`, `grader`).
- **How:** For each, append a `NOT for [adjacent case] — use [sibling] instead` clause. Example: ref-eval gets "NOT for turning findings into a work plan — use ref-plan"; ref-plan gets "NOT for evaluating a reference — use ref-eval; NOT for auditing built work — use ref-comp". Additive edit to the description string only; no logic change.
- **Gate:** Each edited description still parses (skill loads) and the new clause names a real sibling skill. ref-comp checkpoint: descriptions contain mutually consistent negative triggers.
- **Reference location:** `prompt-patterns.md:241-245` (Negative Trigger Pattern).

## Phase 2 -- Targeted Integration

**B3 — Subagent-vs-skill decision rubric**
- **What:** Add a short "subagent vs skill" rubric to the framework authoring conventions, lifting the reference's four criteria (isolation / different capability lane / restricted tools / parallelism) and extending with WabbleSpec's fifth axis: receipt + authority boundaries.
- **Where:** `CLAUDE.md` (Skill Authoring Conventions section) or a dedicated `engine/shared/references/` authoring doc — shared framework infrastructure.
- **How:** Write 5 bullet criteria; replace the reference's `model:` axis with WabbleSpec's capability-descriptor routing (I6). Route from CLAUDE.md to the reference doc rather than inlining (existing Reference Routing convention).
- **Specify required:** yes
- **Breaking change risk:** none (additive documentation)
- **Gate:** The rubric names capability descriptors, not model names (I6 clean); doctor run shows no new drift. ref-comp checkpoint.
- **Reference location:** `SKILL.md:16-22` (Agents vs Skills table).
- **Authority note:** Writes to shared framework infra (`CLAUDE.md` / `engine/shared/**`) — must go through the framework-maintenance authority owner (active task card finding #29), so this is correctly deferred behind a Specify cycle rather than a Phase 1 quick edit.

## Phase 3 -- Considered Integration

None. No Risk=High items survived the exclusion filter.

## Phase 4 -- Watch Only

None. The two study-only items (B4 token-discipline, B5 boundary/handoff templates) are recorded in the Exclusion List as corroborating-only; they have no promotion path because there is no concrete artifact to integrate — they reinforce conventions WabbleSpec already enforces.

## Execution Notes

- **Sequencing:** B1 and B2 are independent and may proceed in parallel — different files, no shared edits. B3 depends on nothing but is gated behind the framework-maintenance authority owner and a Specify cycle, so it runs after Phase 1.
- **B1 is the critical item.** Treat the gate as mandatory: stripping a tool the subagent silently relies on degrades Guard/Verifier without an obvious error. Verify against a real wave before committing.
- **I6 guardrail across all phases:** none of these items may introduce a model name. B3 in particular must express the "different model" axis as a capability descriptor (`code-generation`/`analysis`/`synthesis`/`long-context`).
- **Authority (finding #29):** B3 touches shared-infra; route through the established framework-maintenance owner. B1/B2 touch `.claude/agents/` and SKILL.md descriptions — confirm whether those are sync-generated from `engine/` before editing the wrong copy.
- After implementation is complete, run `/ref-comp agent-creator` to audit execution fidelity against this plan and the ref-eval report.
