# Ref-Comp: agent-rules-main

**Auditing:** Phase 3 implementation against `research/ref-plan/agent-rules-main.md`
**Audited:** 2026-05-31

---

## Literal fidelity pre-check

| Item | Literal values required | Status |
|---|---|---|
| A1 — 5 constraints | Token-efficient writing, Concrete file references, No duplication, Parallel agent dispatch, Timestamp header | Exact — all 5 named in `## LLM-optimized output format` in both SKILL.md copies |
| A2 — threshold | "3+ distinct execution contexts" | Exact — `C:\Vaults\WabbleSpec v6.1\CLAUDE.md:189` |
| A3 — 6 criteria | Actionable, Specific, Tested, Complete, Current, Linked | Exact — all 6 named in CLAUDE.md:191 |
| A4 — codebase examples | "actual project artifacts, not theoretical constructs" | Exact — CLAUDE.md:193 |
| A5 — DRY cross-reference | "## Reference Routing table" named as correct location | Exact — CLAUDE.md:195 |

No Corrupted or Absent literal values.

---

## Section 1 — Implementation Coverage

| Item | Status | Location |
|---|---|---|
| A1 — LLM-optimized doc format | Implemented | `engine/modules/l6/document/SKILL.md:82` + `.claude/skills/document/SKILL.md:82` |
| A2 — "3+ files" creation threshold | Implemented | `CLAUDE.md:189` |
| A3 — Rule quality checklist (6 criteria) | Implemented | `CLAUDE.md:191` |
| A4 — Codebase examples rule | Implemented | `CLAUDE.md:193` |
| A5 — Cross-reference DRY | Implemented | `CLAUDE.md:195` |

Coverage: 5 of 5 (100%).

---

## Section 2 — Execution Gaps

None. All 5 items implemented without partial or missed status.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| A1 LLM format — concrete file ref example | Reference (`update-docs.mdc`) describes the principle abstractly | Added an explicit negative example: `"The main entry point" is not a reference. engine/shared/scripts/receipt-writer.py:42 is.` | Concrete contrast prevents the vague pattern that the rule is trying to eliminate | None |
| A4 codebase examples — added consequence | Reference says "reference actual code over theoretical examples" | Added: "Invented example paths and fake filenames teach incorrect mental models and diverge from the project as it evolves" | States WHY, consistent with CLAUDE.md convention of explaining reasoning rather than issuing MUST directives | None |

Both improvements should be protected — they follow the CLAUDE.md "prefer explaining reasoning over capitalized directives" convention.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Target file for A2-A5 | `cursor-rules-meta-guide.mdc` / `continuous-improvement.mdc` are Cursor-format `.mdc` files injected via `@path` import | Rules added to `CLAUDE.md` in the `## Skill Authoring Conventions` section | Yes — WabbleSpec uses CLAUDE.md as the canonical skill authoring authority, not `.mdc` files | None |
| A3 quality checklist — cadence omitted | Reference includes monthly/quarterly/annually review cadence | Cadence dates intentionally excluded | Yes — violates CLAUDE.md "no time-sensitive information in descriptions" rule | None |
| A1 — no `<!-- Generated: -->` enforcement mechanism | Reference expects human discipline | Added as a named constraint with no automated check | Acceptable — quality-floor-check.py could add an INLINE_DANGER-style check in future | Low: agents may omit timestamp without a gate to catch it |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 1 (no tests) | 5 (quality-floor-check.py covers CLAUDE.md format; no specific test for new rules) | +4 | Reference has no tests at all |
| Error handling | 3 | 6 | +3 | CLAUDE.md rules are enforced by quality-floor-check.py Gate 1 |
| Documentation | 6 | 8 | +2 | Our rules include WHY reasoning; reference uses bullet lists without rationale |
| Naming clarity | 7 | 8 | +1 | Our constraint names are concrete; reference uses generic "Quality Checklist" |
| Dependency hygiene | 9 (no deps) | 9 | 0 | Both are pure text rules |

---

## Section 6 — Verdict

- **Coverage rate:** 5 of 5 planned items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 2
- **Execution classification:** complete

**Top 3 wins to protect:**
1. `engine/modules/l6/document/SKILL.md:82` — `## LLM-optimized output format` section with 5 named constraints; at risk if document SKILL.md is heavily refactored
2. `CLAUDE.md:189–195` — four consecutive skill authoring rules; at risk if another ref-adopt inserts in the same area without reading context
3. Concrete negative example in A1 (`engine/shared/scripts/receipt-writer.py:42` as the positive case vs. "The main entry point") — provides unambiguous contrast that generic rule statements miss

**Recommended next action:** Archive

---

## Section 7 — Synthesis Coverage

Ref-plan had no Tier 6 synthesis items (ref-eval Section 8 identified one synthesis idea but it was deferred to Watch Only in ref-plan). No Tier 6 items to audit.

---

## Section 8 — Expansion Handoff Audit

No Tier 7 items were identified in ref-eval Section 9. This reference has no net-new capabilities absent from WabbleSpec.

Status: "No expansion opportunities identified" — explicitly confirmed in ref-eval Section 9.
