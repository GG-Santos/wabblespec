# Ref-Comp: claude-code-security-review-main

**Date:** 2026-05-31  
**Session:** tier7-expansions-20260530  
**Based on:** `research/ref-plan/claude-code-security-review-main.md`

---

## Literal Fidelity Pre-Check

| Item | Literal values | Status |
|---|---|---|
| T1-1 hard exclusion count | 17 items | Exact — verified by script count: 17 |
| T1-1 precedents count | 12 items | Exact — verified by script count: 12 |
| T1-2 field name | `exploit_scenario` | Exact — present in both `.claude/skills/` and engine module |
| T1-3 threshold | 0.7 non-report boundary | Exact — "Below 0.7: Do not report" |
| T1-3 tier labels | Certain / Clear / Suspicious / Speculative | Exact |
| T1-4 dispatch threshold | "3 or more candidate findings" | Exact |
| T1-4 drop condition | "confidence below 0.7 is dropped" | Exact |
| T1-5 phase names | "Context Research / Comparative Analysis / Vulnerability Assessment" | Exact |

No corrupted or absent literal values.

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| T1-1: 17-item hard exclusion list in gateway-security SKILL.md | Implemented |
| T1-1: 12-item precedents in gateway-security SKILL.md | Implemented |
| T1-1: Engine sync (l4/security/SKILL.md) | Implemented |
| T1-2: `exploit_scenario` field in adversary output schema | Implemented |
| T1-2: Prose rule requiring exploit_scenario for HIGH/CRITICAL | Implemented |
| T1-2: Engine sync (l2/adversary/SKILL.md) | Implemented |
| T1-3: Reporting Confidence Thresholds table | Implemented |
| T1-3: 0.7 non-report floor prose rule | Implemented |
| T1-3: Engine sync | Implemented |
| T1-4: Multi-Finding Security Audit Mode section | Implemented |
| T1-4: 4-step dispatch pattern with 0.7 drop condition | Implemented |
| T1-4: Engine sync | Implemented |
| T1-5: 3-phase methodology in gateway-security Phase B | Implemented |
| T1-5: Engine sync | Implemented |
| T6-1 (synthesis): Confidence-gated escalation | Deferred — T1-3+T1-4 form the prerequisite; synthesis validates once those are in use |
| T6-2 (synthesis): Guard OPSEC × security precedents dual-axis | Deferred — requires adversarial review of guard/skill-rules.json interaction |
| Tier 7: PR security eval harness | Handed off (drawer written) |

**5 of 5 Tier 1 items implemented (100%).** Tier 6 and Tier 7 correctly deferred.

---

## Section 2 — Execution Gaps

No Missed or Partial items. All 5 Tier 1 items are Implemented. Tier 6 items are Deferred (not Missed — they have explicit deferral conditions in the plan).

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| T1-5 placement | Reference places methodology as free-standing section | Added directly after Phase B code block with explicit call-out "Apply the Hard Exclusions and Precedents from ## False-Positive Filtering before issuing any verdict" | Cross-links the 3-phase methodology to the filtering rules — a security engineer running Phase B has both a process and a filter checklist visible from the same section | None — additive cross-reference only |
| T1-3 prose rule | Reference states "below 0.7: don't report" with no elaboration | Added "The 0.7 boundary is the non-report floor. A finding sitting at 0.65 that 'feels significant' is still dropped — specificity, not intuition, earns inclusion." | Addresses the most common edge case (a finding that almost reaches threshold) by explicitly naming why intuition is not a valid override | None |
| T1-4 rationale | Reference states the parallel pattern without explaining why | Added "This preserves the anchoring-prevention invariant across findings: a false positive in finding #1 cannot bias the severity assessment of finding #3." | Makes the philosophical alignment with adversary's existing anchoring-prevention mechanism explicit — future editors understand why this pattern exists | None |

Mark all three as "protect" — they are non-obvious additions that encode reasoning; future edits might strip them as "extra prose."

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| False-positive filter location | Separate `findings_filter.py` module + slash command | Integrated as a `## False-Positive Filtering` section directly in gateway-security SKILL.md | Yes — WabbleSpec is a skill-based framework, not a Python application | No consequence; the behavioral content is identical, only the delivery mechanism differs |
| Confidence scoring scope | Applied per-finding during Claude API call (findingsfilter.py) | Placed in adversary's Claim Confidence Protocol — applies during the adversarial challenge phase | Yes — in WabbleSpec, adversary does the analytical work that the Claude API filter does in the reference | No consequence; same cutoff logic, different execution context |
| Parallel dispatch | Realized as actual parallel Claude Code sub-tasks in a GitHub Actions workflow | Documented as a dispatch pattern in adversary SKILL.md (behavioral spec, not wired automation) | Yes — WabbleSpec executes patterns via skill instructions, not GitHub Actions automation | Agent must read and follow the section; no automated enforcement. Acceptable for the current framework level. |

No unintentional divergences.

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 9 | 6 | -3 | Reference has dedicated test_hard_exclusion_rules.py with boundary tests (N-1/N/N+1 for each pattern). Our implementation adds behavioral rules to SKILL.md — no automated test harness exists for SKILL.md content. Acceptable gap: SKILL.md content is verified by quality-floor-check.py Gate 1, not by unit tests. |
| Error handling | 8 | 7 | -1 | Reference has explicit fail-open (API failure → keep finding) and PROMPT_TOO_LONG fallback. Our SKILL.md rules don't specify what to do if confidence is ambiguous. Minor gap — adversary's existing two-pass rule handles ambiguity. |
| Documentation | 7 | 8 | +1 | Our implementation adds the "why" behind the 0.7 floor and the anchoring rationale for parallel dispatch — the reference has neither. |
| Naming clarity | 8 | 8 | 0 | Section names are clear; field name `exploit_scenario` is unambiguous. |
| Dependency hygiene | 7 | 9 | +2 | Reference has hardcoded model names (I6); our implementation has no external dependencies. |

The -3 test coverage delta is the one meaningful gap. The existing WabbleSpec quality-floor-check.py validates SKILL.md structure but not behavioral rule content.

---

## Section 6 — Verdict

- **Coverage rate:** 5 of 5 Tier 1 items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 3
- **Execution classification:** `complete`
- **Top 3 wins to protect:**
  1. `## False-Positive Filtering` section in gateway-security — 17+12 items with language-specific precision (`gateway-security/SKILL.md`, engine `l4/security/SKILL.md`)
  2. `### Reporting Confidence Thresholds` table in adversary with the 0.7 floor rationale (`adversary/SKILL.md`, engine `l2/adversary/SKILL.md`)
  3. `## Multi-Finding Security Audit Mode` with anchoring rationale (`adversary/SKILL.md`, engine `l2/adversary/SKILL.md`)
- **Top 3 gaps to close (future work):**
  1. (Minor) No automated test for SKILL.md hard exclusion rule content — a future skill-tdd fixture could verify that a DOS-type finding is correctly excluded
  2. (Deferred) T6-2: Guard OPSEC × security precedents dual-axis filter
  3. (Tier 7) PR security eval harness — `pr-security-eval.py` script
- **Recommended next action:** Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| T6-1: Confidence-gated adversarial escalation | Deferred | T1-3 + T1-4 form the prerequisite building blocks | Missing: the explicit gateway-security → adversary dispatch routing that gates which findings get DREAD scoring. Deferred by plan — both halves need real-world exercise before synthesis is validated. |
| T6-2: Guard OPSEC × security precedents dual-axis | Deferred | Not in this pipeline | Requires adversarial review of guard/skill-rules.json; appropriately deferred. |
| T6-3 (wave-review false-positive pre-filter) | Deferred | Not in this pipeline | Was proposed in Section 8 of ref-eval but not assigned a Tier in ref-plan; correctly left out of implementation scope. |

No synthesis items were dropped — all are Deferred with explicit conditions.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| PR security eval harness | Yes — `claude-code-security-review-main/exploit-scenario-and-parallel-filter.json` contains session seed | Yes — "Build a PR security eval harness at `.wabblespec/engine/shared/scripts/pr-security-eval.py` that clones a GitHub repo, checks out a PR via git worktree, runs gateway-security analysis, and writes an EvalResult JSON to `.wabblespec/state/receipts/`; ref: `claudecode/evals/eval_engine.py` lines 56-465" | Handed off |

Note: The Tier 7 PR eval harness session seed is in the `exploit-scenario-and-parallel-filter.json` drawer, not in a dedicated Tier 7 drawer. A dedicated drawer should be written for cleaner handoff — doing that now.
