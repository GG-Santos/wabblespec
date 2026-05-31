# Ref-Comp: superpowers

**Reference:** superpowers v5.1.0
**Slug:** `superpowers`
**Audited:** 2026-05-30
**Execution classification:** complete

---

## Literal Fidelity Pre-Check

| Item | Literal values required | Status |
|---|---|---|
| SP-01 (verifier skepticism) | "actual artifact", "do not rely solely", "ground truth" | Exact |
| SP-02 (architectural escalation) | "ARCHITECTURE_ESCALATION", "different failure location", "new shared state", "new coupling" | Exact |
| SP-03 (task complexity signals) | "1–2 files", "code-generation", "synthesis", "analysis" | Exact |
| SP-04 (CSO prohibition) | "must not summarize the skill's workflow", "shortcut", "skip reading the skill body" | Exact |
| SP-05 (evidence gate) | "IDENTIFY", "RUN", "READ", "VERIFY", "CLAIM" | Exact |
| SP-06 (diagnostic instrumentation) | "component boundary", "root location", "failing boundary" | Exact |
| SP-07 (rationalization tables) | "Guard would pass anyway", "checkpoint is slow", "state.json update" | Exact |
| SP-08 (spec self-review) | "Placeholder scan", "Consistency check", "Scope check", "Ambiguity check" | Exact |

---

## Section 1 — Implementation Coverage

| ID | Item | Status |
|---|---|---|
| SP-01 | Spec reviewer skepticism → `verifier/SKILL.md` Step 1 | Implemented |
| SP-02 | Architectural escalation → `verifier/SKILL.md` Step 4 | Implemented |
| SP-03 | Task complexity signals → `model-router/SKILL.md` | Implemented |
| SP-04 | CSO prohibition → `CLAUDE.md` | Implemented |
| SP-05 | Evidence gate → `executor/SKILL.md` | Implemented |
| SP-06 | Diagnostic instrumentation → `wave-fix/SKILL.md` | Implemented |
| SP-07 | Rationalization tables → `executor/SKILL.md` | Implemented |
| SP-08 | Spec self-review → `specify/SKILL.md` | Implemented |
| SP-09 (Tier 3) | Wave independence criteria → `decompose/SKILL.md` | Deferred (Tier 3; not in Phase 1-2 scope) |

---

## Section 2 — Execution Gaps

None. All Phase 1–2 items implemented. SP-09 is Tier 3 (Deferred), not Missed.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| SP-02 framing | superpowers says "3 fix attempts" | WabbleSpec uses "3 REVISE cycles surfacing different failure locations" | More precise trigger condition — the escalation fires on pattern evidence (coupling drift), not just a count threshold | None |
| SP-04 placement | superpowers embedded in writing-skills SKILL.md | Placed in CLAUDE.md as a framework-wide convention | Applies to all 108 skills; writing-skills placement would only inform skill authors who read that one file | None |
| SP-05 gate | superpowers: run verification command | WabbleSpec: check all wave receipts exist with status PASS | Matches WabbleSpec's receipt-chain architecture; more concrete than a generic "run command" mandate | None |

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Model tier vocabulary | "cheap/standard/capable" tier labels | `code-generation`/`synthesis`/`analysis` capability descriptors | Yes — I6 compliance | Consistent with WabbleSpec's capability descriptor system |
| Description rule location | Inside writing-skills SKILL.md | Inside CLAUDE.md | Yes — broader reach | All skill authors encounter the rule regardless of whether they read writing-skills |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Behavioral precision | 9 | 9 | 0 | Matching precision in trigger conditions and literal values |
| Naming clarity | 9 | 9 | 0 | WabbleSpec vocabulary consistently used |
| Documentation | 8 | 8 | 0 | All items documented in receipts and memory drawers |
| Integration fit | 7 | 9 | +2 | WabbleSpec-specific receipt chain terminology improves fit over generic superpowers patterns |
| Coverage | N/A | 8/8 Phase 1-2 | N/A | 100% of planned items |

---

## Section 6 — Verdict

- **Coverage rate:** 8/8 planned Phase 1–2 items (100%); SP-09 Tier 3 deferred correctly
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 3 (framing precision, placement optimization, architecture alignment)
- **Execution classification:** `complete`
- **Top 3 wins to protect:**
  1. `verifier/SKILL.md` SP-01+SP-02 — independent artifact read + architectural escalation signal (closes two verification gaps in one file)
  2. `CLAUDE.md` SP-04 — CSO workflow-summary prohibition applies framework-wide to all 108 skills
  3. `executor/SKILL.md` SP-05+SP-07 — evidence gate before execution-receipt + rationalization table (closes completion-claim and bypass-rationalization gaps)
- **Recommended next action:** Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| SYN-01: Receipt-gated spec compliance | Implemented | `verifier/SKILL.md` Step 1 | SP-01 implements the artifact-read half; receipt chain enforcement was already present |
| SYN-02: Escalation receipt type | Partial | `verifier/SKILL.md` Step 4 | ARCHITECTURE_ESCALATION signal added; new receipt type in receipt-writer.py deferred to a separate task (requires receipt schema change) |
| SYN-03: Task complexity → capability signal | Implemented | `model-router/SKILL.md` | SP-03 implements the input-signal side of the existing capability routing |

**SYN-02 partial:** The signal is in place. Adding a formal `ARCHITECTURE_ESCALATION` receipt type to `receipt-writer.py` requires a receipt schema task — tracked as a future item.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Skill authoring TDD test harness | `tier7-skill-tdd-harness.json` ✓ | Yes ✓ | Handed off |
| Visual companion for brainstorming | `tier7-visual-companion.json` ✓ | Yes ✓ | Handed off |
