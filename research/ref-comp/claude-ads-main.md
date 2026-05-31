# Ref-Comp: claude-ads-main

**Reference**: claude-ads-main (supporting-reference, 6/10)
**Session**: tier7-expansions-20260530
**Audited**: 2026-05-31
**Execution classification**: complete

---

## Literal Fidelity Pre-Check

| Item | Ref-plan literal values | Status |
|---|---|---|
| Quick Wins IF/SORT | `IF severity == Critical/High AND estimated_wave_count_to_fix <= 1 THEN flag as Quick Win` + `SORT BY (severity_multiplier × estimated_scope_impact) DESC` | Exact |
| Severity multipliers | 5.0x (I-class), 3.0x (H-class), 1.0x (M/L-class) | Exact |
| Evidence hierarchy tier labels | Tier 1 (Ultimate Truth), Tier 2 (Macro View), Tier 3 (Optimization View) | Exact — in table row format |
| Hypothesis template | `IF we [change/action] THEN [metric] will [direction] by [estimated %] BECAUSE [reasoning]` | Adapted — benchmark-loop and skill-tdd use context-appropriate variants |
| Hypothesis quality checklist | 5 items: single variable, specific metric, estimated effect size, timeframe, success/failure criteria | Exact |
| Outcome classifications | Confirmed / Refuted / Inconclusive | Exact |
| Negative eval entry schema | `{ id, prompt, expected_skill, should_trigger: false, notes }` | Exact |

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| T1-A: Evidence Hierarchy → verifier/SKILL.md | Implemented |
| T1-B: Quick Wins Filter → guard/SKILL.md | Implemented |
| T1-E: Severity Multipliers + Critical-first → guard/SKILL.md | Implemented |
| T1-C: Hard Gates Block → executor/SKILL.md | Implemented |
| T1-D: Hypothesis Framework → benchmark-loop/SKILL.md | Implemented |
| T1-D: Hypothesis Framework → skill-tdd/SKILL.md | Implemented |
| T1-G: Output Suppression → archive/SKILL.md | Implemented |
| T1-G: Output Suppression → executor/SKILL.md | Implemented |
| T2-F: Negative Eval Guidance → CLAUDE.md | Implemented |
| Sync to .claude/skills/ (6 files) | Implemented |

---

## Section 2 — Execution Gaps

None. All 9 planned changes implemented and verified.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk |
|---|---|---|---|---|
| Evidence Hierarchy placement | Standalone section | Added alongside existing "Agent Disagreement Resolution" section, which covers the related but distinct case of module-to-module disagreements | The two sections are complementary rather than redundant — Evidence Hierarchy covers source of truth, Agent Disagreement covers module conflicts | Low |
| Hypothesis template variants | Single generic template | benchmark-loop uses "IF we [change to framework artifact X]" and skill-tdd uses "IF we load [candidate SKILL.md path]" — context-appropriate variants | More likely to be followed correctly when the template matches the actual use case | None |
| Hard Gates table format | Prose "never violate" list | Structured table with named columns (Gate, Condition, Action on violation) | Machine-readable; easier to scan during fast execution | None |

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Hypothesis section level | Standalone `##` level section | `###` step-level sub-section inside `## How to do it` | Yes | Fits the existing structure of both benchmark-loop and skill-tdd which organize all procedural steps under `## How to do it`. A `##`-level section would appear outside the procedural flow and be skippable. |
| Tier label format | "Tier 1 (Ultimate Truth)" as prose | `| 1 (Ultimate Truth) |` as table row | Incidental | Same information; table format is more scannable and consistent with the rest of the Verifier SKILL.md which uses tables for its verification mode dispatch. |

---

## Section 5 — Quality Delta

| Dimension | Reference (1-10) | Ours (1-10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 5 | 7 | +2 | Ref has evals/creative-evals.json but no automated runner. Our gate verification script achieved 28/28 PASS coverage. |
| Error handling | 6 | 7 | +1 | Hard Gates block adds explicit error actions for 4 invariant violation types. |
| Documentation | 8 | 8 | 0 | Both clear and actionable. |
| Naming clarity | 8 | 8 | 0 | Consistent naming; tier labels and gate names are unambiguous. |
| Dependency hygiene | 9 | 10 | +1 | No new dependencies introduced. All implementations are pure SKILL.md text additions. |

---

## Section 6 — Verdict

- **Coverage rate**: 9/9 planned items (100%)
- **Gap counts**: 0 critical, 0 major, 0 minor
- **Improvements beyond plan**: 3
- **Execution classification**: `complete`
- **Top 3 wins to protect**:
  1. `guard/SKILL.md ## Severity Scoring + ## Quick Wins Filter` — first time Guard has machine-readable priority output; future integrations should not flatten or remove these sections
  2. `verifier/SKILL.md ## Evidence Hierarchy` — complements, not replaces, Agent Disagreement Resolution; both sections must remain distinct
  3. `benchmark-loop/SKILL.md ### Step 0` — the `hypothesis_confirmed` TSV column addition is a schema change; any script reading the TSV log must handle this new column
- **Recommended next action**: Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| T6-1: Weighted Guard scoring with Quick Wins triage | Deferred | `guard/SKILL.md` (partial) | T1-B+E implemented the SKILL.md rules. Full scoring integration with receipt-writer.py is Watch Only — Tier 5 risk deferred |
| T6-2: Hypothesis-Gated Benchmark Loop with outcome classification | Implemented | `benchmark-loop/SKILL.md` | T1-D fully implemented; TSV column added |
| T6-3: Evidence Hierarchy for Verifier (Phase 1 seed) | Implemented | `verifier/SKILL.md` | Fully realized as T1-A |
| T6-4: Negative Routing Eval Fixture (Phase 1 seed) | Implemented | `CLAUDE.md` | T2-F provides the requirement; fixture creation is per-skill work |

3/4 synthesis ideas implemented or seeded. T6-1 deferred appropriately — the Guard scoring system needs its own spec card for receipt-writer.py integration.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Skill Eval Runner | Yes — `tier7-skill-eval-runner-20260531.json` | Yes — `skill-eval-runner.py` spec + Gate 3 integration | Handed off |
| Deliverable Quality Score | Yes — `tier7-deliverable-quality-score-20260531.json` | Yes — `wave-score.py` spec + weighted formula | Handed off |
