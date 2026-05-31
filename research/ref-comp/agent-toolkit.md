# Ref-Comp: agent-toolkit

**Reference:** agent-toolkit
**Date:** 2026-05-31
**Based on:** research/ref-plan/agent-toolkit.md
**Evaluator:** ref-adopt pipeline

---

## Literal Fidelity Pre-Check

| Item | Literal values | Status |
|---|---|---|
| A1 | "Problem", "Why", "Fix" | Exact — all three words appear in the added CLAUDE.md sentence |
| A4 | "< 5% of baseline", "< 0.5 absolute", "Confirmed", "Refuted", "Inconclusive", "last 3 iterations" | Exact — all values appear in the benchmark-loop Step 4 checklist |

---

## Section 1 — Implementation Coverage

| Item | Status | Notes |
|---|---|---|
| A1 — Pitfall format spec in CLAUDE.md | Implemented | Added Problem/Why/Fix structure to `## Pitfalls` convention line in project CLAUDE.md |
| A2 — Hypothesis template in benchmark-loop | Deferred (covered) | benchmark-loop already has a richer IF/THEN/BECAUSE template with 5-item quality checklist; adding the simpler reference template would be a regression |
| A3 — Hypothesis template in skill-tdd | Deferred (covered) | skill-tdd already has an equivalent IF/THEN/BECAUSE template; same reasoning as A2 |
| A4 — When to Trust Results checklist in benchmark-loop | Implemented | Added 4-item pre-verdict checklist to Step 4 in both engine and skills copies |

---

## Section 2 — Execution Gaps

No Missed items. A2 and A3 were deferred because the existing implementations already satisfy the behavioral goal more rigorously than the reference's simpler template. No Critical or Major gaps.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| benchmark-loop hypothesis template | "We believe [change] will [impact metric] because [reasoning]" (3 components) | IF/THEN/BECAUSE with 5-item quality checklist including single-variable constraint, estimated delta, timeframe, and success criteria | The existing template enforces measurability and falsifiability more precisely than the reference's simpler format; appropriate for a rigorous benchmark context vs. content marketing A/B tests | None — existing template predates this pipeline |

Protect: the existing IF/THEN/BECAUSE templates in both benchmark-loop and skill-tdd. Future integrations should not replace them with simpler formats.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Hypothesis format | "We believe [change] will [impact metric] because [reasoning]" | IF/THEN/BECAUSE with 5-item quality checklist | Yes — existing WabbleSpec template is more rigorous | None |
| Pitfall structure | Not defined in reference's own SKILL.md files | Added to CLAUDE.md as a format spec | Intentional divergence — WabbleSpec has a meta-layer for skill authoring conventions | None |

No unintentional divergences detected.

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 0 | 0 | 0 | Neither has tests for documentation conventions |
| Error handling | 5 | 5 | 0 | N/A for documentation changes |
| Documentation | 6 | 7 | +1 | CLAUDE.md now has clearer structure guidance for Pitfalls sections |
| Naming clarity | 6 | 8 | +2 | Problem/Why/Fix labels are clearer than the reference's implicit structure |
| Dependency hygiene | N/A | N/A | 0 | Pure documentation, no dependencies |

---

## Section 6 — Verdict

- Coverage rate: 2 of 4 planned items (50%) — but 2 items were deferred because existing implementations already satisfy the goal more rigorously; no genuine gaps
- Gap counts: 0 critical, 0 major, 0 minor
- Improvements beyond plan: 1 (existing benchmark-loop template superior to reference)
- Execution classification: **substantially-complete** (2 implemented, 2 correctly deferred)
- Top 3 gaps to close: none identified
- Top 3 wins to protect:
  1. `CLAUDE.md` line 157 — Problem/Why/Fix Pitfalls structure now explicit
  2. `benchmark-loop/SKILL.md` Step 4 — 4-item pre-verdict checklist gates early declaration
  3. Existing IF/THEN/BECAUSE hypothesis templates in both benchmark-loop and skill-tdd — superior to reference
- Recommended next action: Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| Benchmark hypothesis gate with "We believe" format + receipt chain | Partial | `.wabblespec/engine/modules/l8/benchmark-loop/SKILL.md` | The hypothesis format is already present in a richer form; the receipt chain already exists. The synthesis value (formal hypothesis receipt field with template enforcement) is deferred to Tier 7 — it requires a new receipt type, not just a SKILL.md edit |
| Pitfall section quality gate in quality-floor-check.py | Deferred | Not implemented | This is Tier 5 (cross-cutting, touches quality-floor-check.py infrastructure); was correctly classified as Watch Only in planning; not in scope for this pipeline |

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Structured L8 experiment document format | Yes — `expansion-candidate-structured-l8-20260531.json` | Yes — included in drawer evidence | Handed off |

No dropped items.
