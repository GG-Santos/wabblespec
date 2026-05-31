# Ref-Comp: hyperframes-main

**Date:** 2026-05-31
**Session:** tier7-expansions-20260530
**Slug:** hyperframes-main

---

## Literal Fidelity Pre-Check

| Item | Source (ref-plan) | Status | Notes |
|---|---|---|---|
| Pattern 1: backtick-`!` regex | `lint-skills.ts` line 30: `` /`[^`]*![^`]*`/ `` | **Adapted** | Python uses `[^`\n]*` (newline-excluded) because Python applies regex to full file content; JS applies per-line. Semantically equivalent, avoids false positives. |
| Pattern 2: backtick-`>word` regex | `lint-skills.ts` line 39: `` /`[^`]*>\w[^`]*`/ `` | **Adapted** | Same `\n` exclusion fix applied. |
| Fenced-block stripping | `lint-skills.ts` lines 60-66: `` /^```[\s\S]*?^```/gm `` | **Implemented** | Python: `re.sub(r'^```[\s\S]*?^```', ..., flags=re.MULTILINE)`. Correct line-count preservation via `'\n' * count`. |

One adaptation from literal: `[^`\n]*` instead of `[^`]*`. Rationale: lint-skills.ts processes the file line-by-line before applying regex. The Python port applies regex to full content. Without `\n` exclusion, the pattern matches across line boundaries, producing false positives (confirmed: optimize and ref-eval were initially flagged incorrectly). The adaptation is correct and faithful to the original intent.

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| Tier 1a: INLINE_DANGER check in quality-floor-check.py | **Implemented** |
| Tier 1b: HARD-GATE + inline danger conventions in CLAUDE.md | **Implemented** |
| Tier 1c: Fast/Slow checklist split (Watch Only in ref-plan) | Deferred — Watch Only, not in scope |

---

## Section 2 — Execution Gaps

No items Missed. No items Partial beyond the adaptation noted in the fidelity pre-check (which is a correct adaptation, not a gap).

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| Newline exclusion in inline patterns | Line-by-line processing (implicit newline barrier) | `[^`\n]*` character class (explicit newline exclusion) | Single regex over full content is faster; the explicit exclusion is clearer about intent and easier to reason about than implicit line-split behavior | None — semantically equivalent |
| Fenced block stripping | TypeScript lambda + split/join | Python `re.sub` with lambda counting `\n` | More compact; same semantics | None |

Both improvements are **protect** — future edits to the patterns should preserve the `\n` exclusion.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Execution model | Per-line regex application | Whole-file with `\n` exclusion | Yes | Functionally equivalent; Python port of line-by-line would be verbose |
| Integration point | Standalone CI script | Integrated into existing quality-floor check as `lint_prompts.INLINE_DANGER` | Yes | Reduces script count; check fires in every quality floor run |
| Error output | Console.error with line number | PASS/FAIL check result (no line number) | Intentional | `--verbose` shows FAIL; exact line not reported. Acceptable for a quality gate — developer will grep the file to find the violation. |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 5 | 4 | -1 | Neither has automated tests for the lint check itself; our integration runs on 108 modules at every quality floor invocation, providing broad empirical coverage |
| Error handling | 8 | 8 | 0 | Both handle missing files gracefully |
| Documentation | 7 | 8 | +1 | In-file comments cite the source reference and explain the `\n` adaptation |
| Naming clarity | 8 | 9 | +1 | `INLINE_DANGER` name makes the check's purpose clear; `_strip_fenced_blocks` is self-documenting |
| Dependency hygiene | 10 | 10 | 0 | Python stdlib `re` only; no new dependencies |

---

## Section 6 — Verdict

**Coverage rate:** 2 of 2 planned Tier 1 items (100%)

**Gap counts:** 0 critical, 0 major, 0 minor

**Improvements beyond plan:** 2 (newline exclusion fix, integration into existing infrastructure)

**Execution classification:** `complete`

**Wins to protect:**
1. `quality-floor-check.py` `[^`\n]*` pattern — the `\n` exclusion is non-obvious; removing it reintroduces false positives.
2. `CLAUDE.md` inline-danger rule — now documents why inline backtick `!` and `>word` must be avoided, surfacing the quality floor check as the enforcement mechanism.
3. `_strip_fenced_blocks` placement before INLINE_DANGER check — ensures code examples with `!` or `>` don't trigger false positives.

**Recommended next action:** Archive. The 7 INLINE_DANGER violations confirmed in existing SKILL.md files (test, explore, platform-cli, memory, markdown, changelog, commit) will now surface in every quality floor run — they can be addressed in a follow-on session.

---

## Section 7 — Synthesis Coverage

No Tier 6 (synthesis) items were identified in ref-plan. Section 8 of ref-eval produced one synthesis idea (already implemented as Tier 1a). Status: Implemented.

---

## Section 8 — Expansion Handoff Audit

ref-plan had no Tier 7 items. The one expansion opportunity (skill content safety lint) was small enough for Phase 1 implementation. No drawers missing.

**Expansion items:** 1 capability identified → implemented in Phase 1 (not deferred). No session seeds needed.
