# Ref-Comp: andrej-karpathy-skills-main

**Date:** 2026-05-31
**Source plan:** `research/ref-plan/andrej-karpathy-skills-main.md`

---

## Literal Fidelity Pre-Check

| Item | Planned literal value | Location in implementation | Status |
|---|---|---|---|
| K1 | "If multiple interpretations exist, present them; don't pick silently." | `~/.claude/CLAUDE.md` line 4 | Exact |
| K2 | "If a simpler approach exists, say so before implementing." | `~/.claude/CLAUDE.md` line 5 | Exact |
| K3 | "If you notice unrelated dead code, mention it — don't delete it." | `~/.claude/CLAUDE.md` line 10 | Exact |
| K4 | "Every changed line should trace directly to the user's request." | `~/.claude/CLAUDE.md` line 11 | Exact |

All four literals: Exact. Zero Corrupted or Absent.

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| K1 — present-multiple-interpretations | Implemented |
| K2 — push-back-when-simpler | Implemented |
| K3 — mention-not-delete dead code | Implemented |
| K4 — every-changed-line governing test | Implemented |

4 of 4 planned items implemented. Coverage: 100%.

---

## Section 2 — Execution Gaps

None. All items implemented with exact literal values.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| Placement of K1/K2 | Reference had these under "Think Before Coding" heading | Placed immediately after "Thorough in reasoning, concise in output" — the most adjacent existing rule | Logical grouping without creating new headers; stays consistent with CLAUDE.md's flat-bullet format | None |
| Placement of K3/K4 | Reference had these under "Surgical Changes" heading | Placed at end of Approach section after the verification/accuracy rules | Surgical-changes rules pair naturally with accuracy discipline | None |

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| File target | Reference encodes in CLAUDE.md per-project | Adopted into `~/.claude/CLAUDE.md` (global user CLAUDE.md) | Yes — global application preferred over per-project | Rules apply across all projects, not just WabbleSpec |
| No section headers | Reference groups under named sections (Think Before Coding, Surgical Changes) | Flat bullets in Approach section — no sub-headers | Yes — matches existing CLAUDE.md format convention | Marginally less structured, but consistent with existing style |

Both divergences intentional. No unintended divergence.

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Completeness | 8 | 8 | 0 | Both capture the same four rules at equivalent precision |
| Naming clarity | 8 | 8 | 0 | Identical verbatim text for K1–K4 |
| Integration fit | 5 | 9 | +4 | Reference was per-project; ours is global — higher leverage |
| Documentation | 7 | 7 | 0 | Equivalent; CLAUDE.md is self-documenting |
| Scope discipline | N/A | 10 | — | K5 (Watch Only) correctly excluded |

---

## Section 6 — Verdict

- Coverage rate: 4 of 4 (100%)
- Gap counts: 0 critical, 0 major, 0 minor
- Improvements beyond plan: 2 (placement choices that improve coherence)
- Execution classification: **complete**
- Top 3 wins to protect:
  1. `~/.claude/CLAUDE.md` line 4 — K1 multi-interpretation rule (global scope)
  2. `~/.claude/CLAUDE.md` line 10 — K3 mention-not-delete rule (sharpens backwards-compat guidance)
  3. `~/.claude/CLAUDE.md` line 5 — K2 push-back-when-simpler rule (licenses pre-implementation pushback)
- Recommended next action: Archive

---

## Section 7 — Synthesis Coverage

Ref-plan had no Tier 6 synthesis items. Ref-eval Section 8 identified one synthesis idea (disambiguation nudge in prompt-guard hook) but assessed it as Watch Only pending a concrete agent failure observation. No synthesis items to audit.

---

## Section 8 — Expansion Handoff Audit

Ref-eval Section 9 identified zero Tier 7 candidates. Ref-plan had no Tier 7 items. No drawers required beyond the reference-card drawer already written.

Status: No expansion opportunities identified — explicitly confirmed, not left blank.
