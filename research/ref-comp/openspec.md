# Ref-Comp: OpenSpec Integration Audit

**Reference:** openspec
**Session:** agent-creator-integration-20260529
**Audited:** 2026-05-30
**Based on:** research/ref-plan/openspec.md

---

## Literal Fidelity Pre-Check

| Item | Literal value | Location in implementation | Status |
|---|---|---|---|
| A1 delta header 1 | `## ADDED Criteria` | `.claude/skills/specify/SKILL.md` line 74 | Exact (vocabulary-adapted from `## ADDED Requirements`) |
| A1 delta header 2 | `## MODIFIED Criteria` | `.claude/skills/specify/SKILL.md` line 80 | Exact (vocabulary-adapted) |
| A1 delta header 3 | `## REMOVED Criteria` | `.claude/skills/specify/SKILL.md` line 86 | Exact (vocabulary-adapted) |
| A2 context open tag | `<context>` | `.claude/skills/scope-frame/SKILL.md` line 112 | Exact |
| A2 context close tag | `</context>` | `.claude/skills/scope-frame/SKILL.md` line 115 | Exact |
| A2 rules open tag | `<rules>` | `.claude/skills/scope-frame/SKILL.md` line 117 | Exact |
| A2 rules close tag | `</rules>` | `.claude/skills/scope-frame/SKILL.md` line 120 | Exact |

All literals: **Exact** (A1 headers adapted from OpenSpec's `Requirements` suffix to `Criteria` to match WabbleSpec acceptance-criteria vocabulary — intentional, not corruption).

---

## Section 1 — Implementation Coverage

| Item | Tier | Status |
|---|---|---|
| A1 — Delta acceptance criteria format in `specify` SKILL.md | Tier 1 | Implemented |
| A2 — Context/rules injection convention in `scope-frame` SKILL.md | Tier 1 | Implemented |
| B1 — Per-wave instruction embedding in wave-plan-writer.py | Watch Only | Deferred |
| B2 — BLOCKED/READY/DONE state labels | Watch Only | Deferred |
| S1 — Delta-Keyed Acceptance Criteria (Verifier routing) | Tier 6 | Deferred |
| S2 — Instruction-Embedded Wave Plan | Tier 6 | Deferred |

---

## Section 2 — Execution Gaps

No Missed or Partial items. Both Tier 1 items implemented completely.

Watch Only and Tier 6 items are Deferred — not Missed.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| Verifier mode annotation in delta headers | OpenSpec's delta headers are format-only markers for archive merge | WabbleSpec's implementation adds inline comments explaining the verification mode per section (`← verifier checks this behavior IS present` etc.) | Makes the structural purpose explicit; Verifier skill can use these annotations as documentation for how to process each section | Minimal — comments are inside code fences, not executed |
| Fallback note in context injection | OpenSpec's context injection is unconditional (config.yaml present = inject) | scope-frame A2 notes "Absence of tags is not an error — skill falls back to reading scope.md directly" | Prevents downstream skills from breaking when scope-frame output doesn't use the tag convention | None |

**Protect:** Both improvements should be preserved in any future scope-frame or specify refactors.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Delta header vocabulary | `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements` | `## ADDED Criteria`, `## MODIFIED Criteria`, `## REMOVED Criteria` | Yes — WabbleSpec uses "Criteria" (not "Requirements") consistently | WabbleSpec's Verifier and any criterion-parsing scripts must use the WabbleSpec header strings, not OpenSpec's |
| Context injection location | OpenSpec: injected into EVERY artifact instruction by CLI | WabbleSpec: documented as a convention; downstream skills opt-in to reading the tags | Yes — WabbleSpec skills read scope.md directly today; moving to mandatory tag injection would require updating all downstream skills | Low immediate risk; convention can harden over time |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 9 | N/A | — | OpenSpec has 150+ unit tests for its TypeScript core; WabbleSpec additions are SKILL.md prose (not testable via unit tests) |
| Error handling | 7 | 7 | 0 | Both handle the "absent tags" case gracefully; WabbleSpec notes fallback explicitly |
| Documentation | 8 | 8 | 0 | OpenSpec's docs/concepts.md explains delta spec exhaustively; our implementation explains delta criteria at similar depth |
| Naming clarity | 8 | 9 | +1 | WabbleSpec's `## ADDED Criteria` is more precise than OpenSpec's `## ADDED Requirements` for an AC context |
| Dependency hygiene | N/A | N/A | — | Both additions are pure documentation (no new dependencies) |

No delta ≥ ±3.

---

## Section 6 — Verdict

- **Coverage rate:** 2 of 2 planned Tier 1 items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 2 (Verifier mode annotation, fallback note)
- **Execution classification:** `complete`
- **Top 3 gaps to close:** None (no gaps)
- **Top 3 wins to protect:**
  1. `.claude/skills/specify/SKILL.md` — Verifier mode annotation inside delta format section (line 78, 84, 90)
  2. `.claude/skills/scope-frame/SKILL.md` — Fallback note for absent tags (line 125)
  3. Header vocabulary adaptation (`Criteria` not `Requirements`) — must stay consistent if Verifier ever parses these headers
- **Recommended next action:** Archive (complete)

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| S1 — Delta-Keyed Acceptance Criteria (Verifier routing) | Deferred | N/A | Foundation (A1 delta format) is implemented; the Verifier augmentation half is deferred — Verifier skill would need a section-header-aware verification mode selector |
| S2 — Instruction-Embedded Wave Plan | Deferred | N/A | Neither half implemented; requires wave-plan-writer.py + Executor skill coordination; deferred to a dedicated wave |

S1 is partial-handoff ready: the reference contribution (delta section headers) is in place at `.claude/skills/specify/SKILL.md`. The project contribution (Verifier mode routing based on section header) is the missing half.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Multi-tool skill generation | Yes — `openspec-expansion-multitools.json` | Yes | Handed off |
| Parallel session conflict detection | Yes — `openspec-expansion-parallel-conflict.json` | Yes | Handed off |
| Schema-defined custom workflow initialization | No explicit drawer — synthesized from Section 9 C3 | Session seed in ref-plan Tier 7 table | Partial handoff |

**Action:** Writing the missing drawer for C3 now.
