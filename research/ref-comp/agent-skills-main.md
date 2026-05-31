# Ref-Comp: agent-skills-main

**Reference:** agent-skills-main
**Date:** 2026-05-31
**Based on:** research/ref-plan/agent-skills-main.md

---

## Literal Fidelity Pre-Check

| Item | Planned literal values | Status |
|---|---|---|
| A1 label pair | `**Incorrect:**` and `**Correct:**` | EXACT — CLAUDE.md line 202 contains both strings verbatim |
| A2 matrix columns | Priority, Category, Impact, Gate condition | EXACT — matrix has all four columns |
| A2 Impact values | HIGH, MEDIUM-HIGH, MEDIUM | EXACT — all three impact tiers present in table |

---

## Section 1 — Implementation Coverage

| Item | Status | Notes |
|---|---|---|
| A1: Incorrect/Correct label convention → CLAUDE.md | Implemented | Added as last bullet in skill authoring section |
| A2: Category×Impact matrix → gateway-aesthetic SKILL.md | Implemented | Both engine module + .claude/skills/ copy updated |
| A3: Rule authoring template → shared/references/rule-template.md | Implemented | New file at .wabblespec/engine/shared/references/rule-template.md |
| T7-1: Rule compiler (Python) | Deferred (Tier 7) | Correct — not in scope for this pipeline |
| T7-2: platform-web-react reference | Deferred (Tier 7) | Correct — memory drawer seeded |
| T7-3: platform-mobile-rn reference | Deferred (Tier 7) | Correct — memory drawer seeded |
| T7-4: view-transitions reference | Deferred (Tier 7) | Correct — memory drawer seeded |

---

## Section 2 — Execution Gaps

None. All three Tier 1-3 items implemented. Tier 7 items correctly deferred.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| A2 matrix gate column | Reference uses "Prefix" (e.g. `async-`) | We use "Gate condition" (one-line pass condition per category) | "Gate condition" is more actionable for audit work — tells agent what PASS looks like, not just what category prefix to use | None |
| A3 rule template | Reference _template.md is a skeleton in rules/ subdirectory | We placed it in shared/references/ with full schema documentation including ImpactLevel description and naming conventions | Shared location makes it available to all skill authors, not just the one module that defined it | None |

**Protect:** The "Gate condition" column in the A2 matrix is a deliberate improvement over the reference. Future sync of gateway-aesthetic should preserve this column choice.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Label placement | Reference uses `## Incorrect:` as markdown headings | We specify `**Incorrect:**` as bold inline headings | Yes — WabbleSpec SKILL.md uses bold inline headers; markdown H2 headings would exceed section budget | None; both are valid Markdown |
| Matrix location | Reference puts matrix at top of SKILL.md body | We put it before `## Phase B audit gates` (not at top) | Yes — gateway-aesthetic's top section is the `## What this skill does` table, which must remain first | None |
| Template location | Reference _template.md lives in rules/ of the skill | We placed it in engine/shared/references/ | Yes — WabbleSpec's shared references directory is the correct cross-skill infrastructure location | None |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 7 (test-cases.json per skill) | N/A | N/A | Label convention and matrix are authoring guides, not code |
| Documentation | 7 | 8 | +1 | rule-template.md is more comprehensive than reference's _template.md |
| Naming clarity | 8 | 8 | 0 | Both consistent |
| Dependency hygiene | 9 (MIT, no ext deps) | 9 | 0 | Additions use no external dependencies |

---

## Section 6 — Verdict

- Coverage rate: 3 of 3 planned Tier 1-3 items (100%)
- Gap counts: 0 critical, 0 major, 0 minor
- Improvements beyond plan: 2 (Gate condition column, shared template location)
- Execution classification: **complete**
- Top 3 wins to protect:
  1. `**Incorrect:**` / `**Correct:**` label convention in CLAUDE.md (line 202-203) — affects all future skill authoring
  2. Priority matrix in gateway-aesthetic engine + skills copies — improves agent prioritization for visual audits
  3. rule-template.md at shared/references — shared infrastructure, referenced from any skill authoring session

---

## Section 7 — Synthesis Coverage

No Tier 6 synthesis items were in ref-plan. N/A.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Rule compiler (Python) | Yes — pattern-rule-compiler-build-system-for-20260531.json | Yes — in drawer evidence field | Handed off |
| platform-web React reference | Yes — expansion-platform-web-tier-3-reference-20260531.json | Yes | Handed off |
| platform-mobile RN reference | Yes — expansion-platform-mobile-tier-3-20260531.json | Yes | Handed off |
| gateway-aesthetic View Transitions reference | Yes — expansion-gateway-aesthetic-tier-3-20260531.json | Yes | Handed off |
