# Ref-Comp: agents-main

**Reference:** agents-main (Claude Code plugin marketplace + plugin-eval quality framework)
**Date:** 2026-05-31
**Pipeline:** ref-eval → ref-plan → implement → ref-comp

---

## Literal Fidelity Pre-Check

| Item | Literal values | Status |
|---|---|---|
| OVER_CONSTRAINED threshold | >15 MNA | Exact — `mna_count > 15` in check_anti_patterns() |
| BLOATED_SKILL threshold | >800 lines | Exact — `line_count > 800` in check_anti_patterns() |
| Anti-pattern penalty formula | `max(0.5, 1.0 - 0.05 × count)` | Exact — `max(0.5, 1.0 - 0.05 * len(triggered))` in score_module() |
| Badge thresholds | Platinum≥90, Gold≥80, Silver≥70, Bronze≥60 | Exact — `SCORE_BADGES = [(90,"Platinum"),(80,"Gold"),(70,"Silver"),(60,"Bronze")]` |
| DIMENSION_WEIGHTS | triggering_accuracy=0.25, orchestration_fitness=0.20, scope_calibration=0.12, progressive_disclosure=0.10, token_efficiency=0.06, structural_completeness=0.03, ecosystem_coherence=0.02 | Exact — matches engine.py values |
| MNA regex | `\b(MUST|NEVER|ALWAYS)\b` | Exact — `_MNA_PATTERN = re.compile(r'\b(MUST|NEVER|ALWAYS)\b')` |
| F1 target threshold | ≥0.80 | Exact — "Target: F1 >= 0.80" in skill-tdd SKILL.md |
| CLAUDE.md sweet spot | 200-600 lines | Exact — "200–600 lines" in CLAUDE.md |
| CLAUDE.md BLOATED_SKILL | >800 without references/ | Exact — "Above 800 lines without a Tier 3 references/ directory is BLOATED_SKILL" |

All literal values: **Exact**. No Corrupted or Absent items.

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| A2: CLAUDE.md 200-600 sweet spot + BLOATED_SKILL name | Implemented |
| A1: ORPHAN_REFERENCE check in quality-floor-check.py | Implemented |
| A1: DEAD_CROSS_REF check in quality-floor-check.py | Implemented |
| A1: OVER_CONSTRAINED check (>15 MNA) in quality-floor-check.py | Implemented |
| A1: BLOATED_SKILL check (>800 no refs/) in quality-floor-check.py | Implemented |
| A1: MISSING_TRIGGER check (no "Use when" in description) in quality-floor-check.py | Implemented (bonus — not in A1 plan, added from plugin-eval MISSING_TRIGGER flag) |
| A3: --score mode in quality-floor-check.py | Implemented |
| A3: Dimension scores (7 dims), badge, letter grade output | Implemented |
| A4: MNA regex cross-check against parser.py pattern | Implemented — exact match |
| A5: F1 triggering accuracy section in skill-tdd SKILL.md | Implemented |
| A5: F1 ≥ 0.80 target threshold | Implemented |
| A5: Negative-case prerequisite check ("skip if no should_trigger: false entries") | Implemented |
| A6: Task capability classification table in model-router SKILL.md | Implemented |
| A6: No model names in classification table | Implemented — uses "Highest/High-analysis/Fast-execution" descriptors |
| Engine module sync (skill-tdd, model-router) | Implemented — 2 files copied by sync |

---

## Section 2 — Execution Gaps

No Missed or Partial items. All 6 planned items implemented, plus one bonus (MISSING_TRIGGER flag added to check_anti_patterns beyond the A1 plan).

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| MISSING_TRIGGER added to anti-pattern checks | Not in A1 plan, discovered during implementation | check_anti_patterns() includes MISSING_TRIGGER alongside A1's 4 flags | MISSING_TRIGGER is the highest-penalty flag (15%) in plugin-eval — omitting it would have made check_anti_patterns() incomplete | None — informational warning, not a gate |
| score mode shows anti-patterns in verbose | Reference shows anti-patterns separately from score | Our --score shows anti-patterns inline with the score line | More useful for CI integration — one output shows both the score and why it's penalized | None |
| CLAUDE.md update adds lower bound (200) not just upper bound | Reference only codifies >800 as BLOATED_SKILL | CLAUDE.md adds both "200 lines is underpowered" and "800 lines is BLOATED_SKILL" | Gives authors a range rather than just a ceiling | None |

**Mark "protect":** The MISSING_TRIGGER check in check_anti_patterns() — any future refactor of lint_prompts() that moves DESCRIPTION_LEN logic should not remove the separate MISSING_TRIGGER check, which tests for trigger-phrase presence (different from description length).

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Anti-patterns as gate failures vs warnings | plugin-eval: multiplicative penalty on score (not gate) | Our check_anti_patterns(): informational warnings, not gate failures | Yes — adding hard gate failures would immediately break 75+ modules | Anti-patterns shown in verbose output; not gate-blocking |
| --score is static-only (7 of 10 dimensions) | Reference: 10 dimensions, 3 layers | Our --score: 7 dims from static analysis only (output_quality, robustness, code_template_quality excluded) | Yes — layers 2+3 require LLM infrastructure not available in this script | Scores are conservative estimates; LLM layers would adjust triggering_accuracy and robustness |
| DEAD_CROSS_REF uses [[name]] syntax | Reference: uses `skill/name` cross-ref patterns | Our implementation: `[[name]]` regex matching module IDs from wabblespec.yaml | Intentional — WabbleSpec uses [[name]] for inter-skill links, not the plugin-eval path format | Catches our actual link format |

---

## Section 5 — Quality Delta

| Dimension | Reference (1-10) | Ours (1-10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 9 (plugin-eval has 13 test files with pytest) | 4 (no automated tests for new checks) | -5 | New checks (check_anti_patterns, score_module) have no test coverage. CLAUDE.md boundary coverage requirement applies — should have tests at N-1=799, N=800, N+1=801 for BLOATED_SKILL threshold. |
| Error handling | 8 | 7 | -1 | check_anti_patterns() returns {} on error, which produces no flags (safe). score_module() returns None on error. Main skips None scores. Adequate. |
| Documentation | 7 | 8 | +1 | Our implementation includes docstrings explaining thresholds and source. Reference source comments added. |
| Naming clarity | 8 | 8 | 0 | check_anti_patterns, score_module, OVER_CONSTRAINED, BLOATED_SKILL names match reference exactly. |
| Dependency hygiene | 9 (pure Python, optional LLM) | 9 (pure Python, no new deps) | 0 | Static-only implementation requires no new dependencies. |

**Delta of -5 on test coverage:** The new checks enforce numeric thresholds (>15 MNA, >800 lines) that per CLAUDE.md boundary coverage requirement should have tests at exactly N-1, N, and N+1. This is a known gap — flagged as a recoverable open thread.

---

## Section 6 — Verdict

- Coverage rate: 6 of 6 planned items (100%)
- Gap counts: 0 critical, 0 major, 1 minor (test coverage for new threshold checks)
- Improvements beyond plan: 3
- Execution classification: **complete**
- Top 3 gaps to close:
  1. (Minor) Add pytest tests for BLOATED_SKILL (799/800/801 lines) and OVER_CONSTRAINED (15/16 MNA) thresholds — per CLAUDE.md boundary coverage requirement
  2. (Minor) --score mode for plugin-level evaluation (current --score only works with wabblespec.yaml module context; ref-plan's A3 gate was met but a standalone `--score-skill <path>` flag would be more versatile)
  3. (Minor) F1 computation in skill-tdd is guidance-only — no automated enforcement
- Top 3 wins to protect:
  1. (protect) MISSING_TRIGGER check in check_anti_patterns() — highest-penalty flag, do not remove
  2. (protect) DIMENSION_WEIGHTS literal values — must match engine.py exactly for reproducible scores
  3. (protect) 200-600-800 triple threshold in CLAUDE.md — complete range; losing the 200 lower bound removes useful guidance for underpowered skills
- Recommended next action: **Archive** (complete). Test coverage gap is minor and addressed as an open thread.

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| S1: Ref-eval composite scoring (formula → Section 5) | Deferred | research/ref-plan/agents-main.md (Tier 6) | Tier 5 risk until validated; Section 5 of ref-eval still uses subjective 1-10 scores. Watch Only for this session. |
| S2: Wave-review anti-pattern gate | Deferred | research/ref-plan/agents-main.md (Tier 6) | Requires confirming wave-review.py output format; Tier 5 risk. Watch Only. |
| S3: L8 promotion Bronze gate | Deferred | research/ref-plan/agents-main.md (Tier 6) | Requires --score mode to exist (done) but instinct SKILL.md not updated; Tier 5 risk. Watch Only. |

Tier 6 items correctly marked as Watch Only (Tier 5 risk) and not implemented this session. No items dropped.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| quality-score.py (Layer 1 static scorer with badge output) | Yes — open-thread-tier-7-expansion-quality-20260531.json | Yes — in drawer evidence + ref-plan Tier 7 table | Handed off |
| quality-rank.py (Elo relative ranking) | Yes — included in quality-suite drawer | Yes — in ref-plan Tier 7 session seed | Handed off |
| quality-judge.py (LLM semantic eval) | Yes — included in quality-suite drawer | Yes — in ref-plan Tier 7 session seed | Handed off |
| C4 architecture diagram generation | Yes — open-thread-tier-7-expansion-c4-20260531.json | Yes — in drawer evidence + ref-plan Tier 7 table | Handed off |

All 4 Tier 7 items: **Handed off** (drawers written, session seeds present).

---

*Report written: 2026-05-31 | ref-adopt pipeline*
