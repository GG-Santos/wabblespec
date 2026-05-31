# Ref-Plan: hyperframes-main

**Date:** 2026-05-31
**Session:** tier7-expansions-20260530
**Slug:** hyperframes-main

---

## Candidate Extraction Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A | INLINE_DANGER check + fenced-block stripping | Behavioral | High | High | Low |
| B | `<HARD-GATE>` convention in CLAUDE.md | Format | Medium | High | Low |
| C | Fast/Slow checklist split convention | Format | Low | Medium | Low |

---

## Exclusion Filter

No items excluded. No "Avoid" or `do_not_copy` entries from ref-eval apply. No task-card non-goals conflict (all items are additive, framework-space only, Python/docs only).

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Score | Tier |
|---|---|---|
| A | (3×2)+3-1 = 8 | Tier 1 |
| B | (2×2)+3-1 = 6 | Tier 1 |
| C | (1×2)+2-1 = 3 | Watch Only |

Item C deferred: useful but not high enough priority for this pipeline run. No Tier 5/6/7 items.

---

## Integration Plan

### Tier 1a — INLINE_DANGER Check in quality-floor-check.py

**What:** Add a new `lint_prompts.INLINE_DANGER` check to `quality-floor-check.py` Gate 2 that detects backtick-wrapped prose spans (not inside fenced code blocks) containing `!` or `>word`. These patterns cause Claude Code's bash permission scanner to trigger false positives, which can prevent skills from loading.

**Where:** `.wabblespec/engine/shared/scripts/quality-floor-check.py` — in the `lint_prompts` check section alongside `SECTION_WHAT`, `SECTION_WHEN`, `DESCRIPTION_LEN` etc.

**How:**
1. In the file-reading step for each SKILL.md, strip fenced blocks: replace ` ```...``` ` spans with blank lines (preserving line count so reported line numbers remain accurate). Use `re.sub(r'```[\s\S]*?```', ...)`.
2. After stripping, scan for inline backtick spans: find all `` `...` `` occurrences.
3. For each span: flag if it contains `!`. Flag if it contains `>` followed by a word character (`\w`).
4. Emit `lint_prompts.INLINE_DANGER: FAIL` with a message quoting the offending span if any violation found; `PASS` otherwise.

**Literal values (from `scripts/lint-skills.ts` lines 30-43):**
- Pattern 1: `` /`[^`]*![^`]*`/ `` (any backtick span containing `!`)
- Pattern 2: `` /`[^`]*>\w[^`]*`/ `` (any backtick span containing `>` followed by a word char)
- Fenced stripping: ``re.sub(r'```[\s\S]*?```', ...)`` replacing with blank lines

**Gate:** Running `python quality-floor-check.py --verbose` shows `lint_prompts.INLINE_DANGER: +` for all 108 modules. The 6 known violating modules show `FAIL` before the fix, `PASS` after.

**Reference location:** `hyperframes-main/scripts/lint-skills.ts` lines 9-66.

---

### Tier 1b — `<HARD-GATE>` Convention in CLAUDE.md

**What:** Add a note to the Skill Authoring Conventions section of `CLAUDE.md` documenting `<HARD-GATE>` as a recognized optional annotation for non-negotiable inline verification checkpoints within a skill body.

**Where:** `CLAUDE.md` — in the `## Skill Authoring Conventions` section, after the existing convention bullets.

**How:** Add one bullet point:
```
**`<HARD-GATE>` is a recognized optional inline marker.** Use `<HARD-GATE>...</HARD-GATE>` to wrap a verification requirement that is non-negotiable before the agent may proceed past that point. Similar to a `MUST NOT` rule but scoped to the exact step in the skill flow where it applies. Do not use for general guidance — only for checkpoints where proceeding without verification would produce a guaranteed defect.
```

**Gate:** CLAUDE.md diff shows the addition. No quality-floor checks are affected (CLAUDE.md is not scanned by quality-floor-check.py).

**Reference location:** `hyperframes-main/skills/hyperframes/SKILL.md` lines 60-62 (`<HARD-GATE>` block example).

---

## Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| All video/animation domain content (GSAP, HTML compositions, Frame Adapters) | Out of scope — product domain |
| JavaScript/TypeScript tooling (bun, oxlint, oxfmt) | I6-adjacent: wrong ecosystem; introduces external binary dependency |
| `window.__timelines` registration pattern | Product-specific; no applicability |
| Discovery question pattern (audience/platform/priority) | Redundant with existing Guard/Specify pipeline |

---

## Priority Implementation Order

| Order | Item | Why first |
|---|---|---|
| 1 | Tier 1a: INLINE_DANGER check | Fixes a confirmed active gap (6 violations); higher impact; prerequisite is just Python stdlib re |
| 2 | Tier 1b: HARD-GATE convention | Documentation only; zero regression risk |

---

## Execution Notes

- Tier 1a and Tier 1b are independent; both can be implemented in the same response turn.
- Tier 1a must NOT add external dependencies — Python `re` (stdlib) only.
- Fenced-block stripping in Tier 1a must use a multiline-compatible regex (DOTALL flag) to handle multi-line fenced blocks.
- After adding INLINE_DANGER, run `quality-floor-check.py --verbose` to confirm the 6 known violations are caught and no false positives appear on the 100+ currently-passing modules.
