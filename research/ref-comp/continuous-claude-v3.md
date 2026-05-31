# Ref-Comp: continuous-claude-v3

**Based on:** `research/ref-plan/continuous-claude-v3.md`
**Audited:** 2026-05-30

---

## Literal Fidelity Pre-Check

| Item | Literal Values Required | Status |
|---|---|---|
| T1-A claim markers | `✓ VERIFIED`, `? INFERRED`, `✗ UNCERTAIN` | Exact — 6 occurrences in adversary/SKILL.md |
| T1-B state symbols | `○ PENDING`, `→ IN_PROGRESS`, `✓ VALIDATED`, `✗ FAILED` | Exact — 2 occurrences in executor/SKILL.md (table row + transition rule) |
| T1-C erotetic frame | `E(X,Q)` | Exact — 1 occurrence in guard/SKILL.md |
| T2-B taxonomy types | All 7 type names | Exact — 8 occurrences in memory/SKILL.md (table + format example) |

All literal values: **Exact**.

---

## Section 1 — Implementation Coverage

| Item | Status | Notes |
|---|---|---|
| T1-A: Claim verification markers → adversary/SKILL.md | Implemented | `## Claim Confidence Protocol` section added between Step 2 and Step 3; engine + skills copies synced |
| T1-B: Checkpoint state symbols → executor/SKILL.md | Implemented | `## Wave State Symbols` section added before Error routing; engine + skills copies synced |
| T1-C: Erotetic Check E(X,Q) → guard/SKILL.md | Implemented | `### Pre-Check Question Frame` added at start of How to do it; engine + skills copies synced |
| T2-A: Delegation thresholds → autopilot/SKILL.md | Implemented | `## Delegation Thresholds` table added before Phase transitions; engine + skills copies synced |
| T2-B: 7-type memory taxonomy → memory/SKILL.md | Implemented | `## Observation Types` section added before Common failure modes; engine + skills copies synced |

---

## Section 2 — Execution Gaps

None. All 5 planned items implemented. No PARTIAL or MISSED items.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| Guard E(X,Q) question frame | Reference uses E(X,Q) generically before "acting" | WabbleSpec implementation maps each Q explicitly to a WabbleSpec invariant (I10, I5, I6/I9/I11, Layer 5, I12/Layer 2) | The reference E(X,Q) is abstract; our implementation ties each question to a specific guard layer, making it actionable rather than decorative | None — purely additive context |
| Claim markers in adversary | Reference tracks markers per-claim in output | Added `## Claim Confidence Protocol` section with explicit two-pass audit and false-claim taxonomy drawn directly from reference | More complete than reference — added the "common false-claim patterns" list which was in a separate rule file in the reference | None |
| Delegation thresholds in autopilot | Reference uses generic delegation table | Added explicit "Do not over-delegate" rule — absent from reference | Prevents regression where the threshold table is misread as "always spawn" | None |

**Protect:** The explicit invariant-to-question mapping in Guard's E(X,Q) frame is a WabbleSpec-specific improvement over the generic reference approach. Future edits to Guard should preserve this mapping rather than replacing it with a generic list.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Claim markers scope | Reference applies markers to any agent output | We apply only to adversary findings | Yes — targeted to highest-value use case | Markers will not appear in other modules' outputs; Verifier is a Tier 6 deferred item |
| State symbols scope | Reference uses symbols in agent handoff files | We use symbols in executor wave loop and receipts | Yes — WabbleSpec's receipt model is the handoff mechanism | No divergence — our receipts serve the same persistence function |
| Memory taxonomy storage | Reference stores in PostgreSQL archival_memory table | We apply as topic-prefix convention for ChromaDB wabblespec_topic field | Intentional — no PostgreSQL dependency | Taxonomy is advisory (prefix convention) not enforced; MemorySearch filtering is a future concern |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 7 | 7 | 0 | Both rely on behavioral specification; no automated unit tests for skill content |
| Error handling | 6 | 8 | +2 | Our Guard E(X,Q) adds explicit unanswerable-question handling that the reference lacks |
| Documentation | 8 | 8 | 0 | Both are well-documented behavioral specs |
| Naming clarity | 8 | 9 | +1 | Our state symbol section uses `## Wave State Symbols` which is more precise than reference's implicit symbols in checkpoint sections |
| Dependency hygiene | 5 | 9 | +4 | Reference has rp-cli, PostgreSQL, CLAUDE_OPC_DIR dependencies; we adopted zero new dependencies |

---

## Section 6 — Verdict

- Coverage rate: 5 of 5 planned items (100%)
- Gap counts: 0 critical, 0 major, 0 minor
- Improvements beyond plan: 3
- Execution classification: `complete`
- Top 3 gaps to close: none — all items complete
- Top 3 wins to protect:
  1. Guard `E(X,Q)` with invariant mapping — `guard/SKILL.md:Pre-Check Question Frame`
  2. Claim Confidence Protocol two-pass audit — `adversary/SKILL.md:Claim Confidence Protocol`
  3. Wave State Symbols advance rule — `executor/SKILL.md:Wave State Symbols`
- Recommended next action: Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| T6-A: E(X,Q) + Guard Receipt Output | Deferred | guard/SKILL.md has E(X,Q) frame but no receipt schema extension | Receipt schema extension is Tier 5; the behavioral addition (T1-C) covers the primary value |
| T6-B: Checkpoint State Symbols + Wave Plan Receipts | Partial | executor/SKILL.md has state symbols; receipt JSON schema not extended | Symbol surfacing in receipts requires receipt-writer.py schema change; deferred per plan |
| T6-C: Claim Markers + Verifier Receipt | Deferred | adversary/SKILL.md has claim markers; verifier receipt schema not extended | Verifier extension is Tier 5; adversary coverage is the primary integration surface |

All Tier 6 items correctly deferred — none marked Missed.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Epistemic reminder hook (PostToolUse/Grep) | `expansion-epistemic-reminder-hook.json` | Yes | Handed off |
| Transcript-based auto-handoff (PreCompact) | `expansion-transcript-auto-handoff.json` | Yes | Handed off |
| Pattern inference module | `expansion-pattern-inference-module.json` | Yes | Handed off |

All 3 Tier 7 items handed off cleanly.
