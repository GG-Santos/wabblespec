# Ref-Comp: hermes-agent-main

**Reference slug:** hermes-agent-main
**Date:** 2026-05-30
**Based on:** `research/ref-plan/hermes-agent-main.md`
**Execution classification:** complete

---

## Literal Fidelity Pre-Check

| Item | Literal values required | Status |
|---|---|---|
| T1.1 category names | "Environment-dependent failures", "Negative tool claims", "Transient errors that resolved", "One-off task narratives" | Exact — all four present |
| T2.1 routing phrase | "first-class Instinct candidate" | Exact — present |
| T1.3 section name | `## Pitfalls` | Exact — present |

No corrupted or absent literals.

---

## Section 1 — Implementation Coverage

| Item | Status | Notes |
|---|---|---|
| T1.1 Dream signal anti-patterns | Implemented | `## Signal Anti-Patterns` with all 4 named categories in engine + synced to `.claude/skills/dream/SKILL.md` |
| T1.2 CLAUDE.md "both dimensions" intro note | Implemented | "Skill intro must state both dimensions" paragraph with "does AND what it explicitly does not do" language |
| T1.3 CLAUDE.md `## Pitfalls` section | Implemented | Recognized as optional section with target of 3–6 bullets |
| T2.1 Dream Instinct signal routing | Implemented | `## Instinct Signal Routing` with memory vs Instinct routing rules and "first-class Instinct candidate" |

4 of 4 planned items: 100% coverage.

---

## Section 2 — Execution Gaps

None. All four planned items implemented and gate-verified.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk |
|---|---|---|---|---|
| Instinct routing rules | Hermes encodes frustration signals as skill-update triggers only | WabbleSpec version distinguishes memory drawer vs Instinct routing with specific routing conditions | More precise than hermes — WabbleSpec's Instinct chain has explicit promotion gates that a simple "update skill" instruction wouldn't capture | Low — additive only |
| Anti-pattern section | Hermes lists in a long review prompt string | WabbleSpec version uses four bold-headed paragraphs, each with a one-sentence rationale | Scannable; the rationale for each ban prevents the rule from being discarded when the agent reasons about edge cases | None |

**Protect:** The "Frustration signals always route to Instinct" closing sentence in `## Instinct Signal Routing` — this is the highest-signal rule and the most likely to be weakened by future edits that add nuance.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Description length limit | Hermes: ≤60 chars enforced by CI assertion | WabbleSpec: period-ending only; no character limit | Yes — WabbleSpec descriptions are richer | WabbleSpec descriptions remain longer than 60 chars; that's correct |
| Curator "agent-created" provenance | Hermes: explicit provenance field gates lifecycle | WabbleSpec: not adopted | Yes — architectural mismatch | No consequence; WabbleSpec has no runtime-created modules |
| Background review fork | Hermes: daemon thread spawned after every turn | WabbleSpec: not adopted | Yes — architectural mismatch | No consequence |

No unintentional divergences.

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Signal discrimination guidance | 9 | 8 | -1 | Hermes has exhaustive prompt strings; WabbleSpec has concise section headers — less comprehensive but more scannable |
| Authoring standard completeness | 8 | 7 | -1 | Hermes enforces via CI; WabbleSpec enforces via CLAUDE.md convention + Gate 2 (period check not yet in Gate 2) |
| Naming clarity | 8 | 9 | +1 | WabbleSpec section names (`## Signal Anti-Patterns`, `## Instinct Signal Routing`) are more precise than hermes' implicit prompt structure |

No delta of ±3 or greater.

---

## Section 6 — Verdict

- Coverage rate: 4 of 4 planned items (100%)
- Gap counts: 0 critical, 0 major, 0 minor
- Improvements beyond plan: 2
- Execution classification: **complete**
- Top 3 wins to protect:
  1. "Frustration signals always route to Instinct" — closing sentence of `## Instinct Signal Routing` in Dream SKILL.md
  2. Four named anti-pattern categories in `## Signal Anti-Patterns` — these must stay named (not prose) for scanability
  3. `## Pitfalls` documentation in CLAUDE.md — first time this optional section is formally recognized
- Recommended next action: **Archive** — complete coverage, no critical gaps.

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| S1: Frustration = Instinct signal heuristic | Implemented | `## Instinct Signal Routing` in Dream SKILL.md | Merged into T2.1; routing rules fully articulated |
| S2: Priority-ordered error taxonomy for wave-fix | Deferred | — | Deferred to Tier 3 (Watch Only) — requires reading wave-fix SKILL.md in full; not a Phase 1 item |
