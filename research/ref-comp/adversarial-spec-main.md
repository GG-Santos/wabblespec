# Ref-Comp: adversarial-spec-main

**Date:** 2026-05-31
**Slug:** adversarial-spec-main
**Source plan:** `research/ref-plan/adversarial-spec-main.md`

---

## Literal Fidelity Pre-Check

| Item | Required literal values | Status |
|---|---|---|
| A1 | "ERRORS: Factually wrong, contradictory, or technically broken", "RISKS: Security holes, scalability issues, missing error handling", "PREFERENCES: Different style, structure, or approach", "additions are cheap, deletions require justification" | Exact — all 4 present in adversary SKILL.md `## Preserve Intent Mode` |
| A2 | 4-step verification: (1) confirm entire doc read, (2) list 3 sections + what verified, (3) explain why strong output, (4) identify remaining concerns however minor | Exact — all 4 steps present in `## Shallow-Analysis Detection` |
| A3 | Prior-failure probing ("What prior attempts... Why did they fail"), tradeoffs axis ("If we can't have everything, what gets cut first?"), risk grounding ("What keeps you up at night") | Exact — all 3 probing angles present |
| A4 | Product: numeric success metrics, scope OUT listed, no tech details, As/I want/So that; Framework: interface shape, security covers auth+authz+data+input, no implementer ambiguity | Exact — both typed blocks present in specify Step 4 |
| A5 | "Do not converge early", 2–3 revision cycles, "Specificity produced under pressure tends toward the vague" | Exact — present in `## Pitfalls` |
| A6 | All 10 personas: security-engineer, oncall-engineer, junior-developer, qa-engineer, site-reliability, product-manager, data-engineer, mobile-developer, accessibility-specialist, legal-compliance | Exact — all 10 present in `## Caller-Specified Persona Mode` with descriptions |

All literal values: **EXACT** — no Corrupted or Absent items.

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| A1: Preserve-intent taxonomy → adversary SKILL.md | Implemented |
| A2: Press protocol (shallow-analysis detection) → adversary SKILL.md | Implemented |
| A3: Deep interview probing additions → interview SKILL.md | Implemented |
| A4: Typed PRD/tech-spec criteria → specify SKILL.md | Implemented |
| A5: Quality-over-speed pitfall → specify SKILL.md | Implemented |
| A6: Persona reference table → adversary SKILL.md | Implemented |
| Engine module mirrors (adversary, interview, specify) | Implemented — all 3 engine paths updated identically |

**All 6 Phase 1+2 items: Implemented. All 3 engine mirrors: Implemented.**

---

## Section 2 — Execution Gaps

None. All 6 items implemented with exact literal values.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| Preserve Intent placement | Reference has a global `--preserve-intent` flag that wraps all critique | Placed inside `## Preserve Intent Mode` section scoped to `challenger_mode: "spec-bound"` — only activates when reviewing a spec artifact | Narrower activation avoids preserve-intent confusion when reviewing implementation code (wrong context) | Minimal — spec-bound is the right trigger |
| Shallow-analysis detection trigger | Reference triggers press when model agrees in rounds 1-2 | Adversary's trigger is `strong_output_acknowledged: true` with < 3 domains engaged | More precise condition — domain coverage is a structural signal, not a round-count heuristic | None |
| Persona mode scoping | Reference allows persona to replace the entire system prompt | Persona mode added as "filters which findings are most relevant" with explicit note that it does NOT override claim confidence thresholds or two-pass audit rule | Prevents persona from bypassing WabbleSpec's core quality gates | None |

Protect: the narrower activation trigger for preserve-intent (spec-bound only, not all modes) — future integration could accidentally expand it to open mode, which would degrade adversary's signal on implementation code.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Convergence mechanism | Multi-model loop with [AGREE] token until all agree | Single-adversary challenge per invocation with receipt chain | Yes — WabbleSpec uses receipt-gated sequential execution, not autonomous loops | Adversary challenges once; repeat invocations are caller-driven, not built into adversary |
| Interview mode scope | Full interview embedded in adversarial debate flow | Interview mode added as `## Deep Probing Sub-Questions` — standalone enrichment | Yes — WabbleSpec's Interview is a separate module | Clean separation maintained |
| Typed spec criteria | PRD vs. tech-spec as primary document-type split | Product vs. Framework as the split (matching WabbleSpec's `target:` field values) | Yes — adapted vocabulary to match existing recipe.json `target` field | No divergence — vocabularies aligned |

No unintentional divergences identified.

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 9 (90% mandate, mutation tests) | 6 (no new tests added — SKILL.md edits) | -3 | SKILL.md changes are prose; no programmatic test required. Quality floor Gate 2 covers behavioral spec completeness. |
| Error handling | 8 | 8 | 0 | Same — both handle the "no findings" case explicitly |
| Documentation | 8 | 8 | 0 | Additions are self-documenting; literal values present |
| Naming clarity | 8 | 9 | +1 | "Preserve Intent Mode" and "Shallow-Analysis Detection" are clearer section names than reference's --flags |
| Dependency hygiene | 6 (litellm required) | 10 (no new dependencies) | +4 | Reference requires pip install litellm; our adoption is zero-dependency behavioral text |

The -3 on test coverage reflects that we did not add tests for the new SKILL.md sections — this is intentional and consistent with how all other ref-adopt integrations have been handled (SKILL.md behavioral specs are tested by the quality floor Gate 1 structural check, not unit tests).

---

## Section 6 — Verdict

- **Coverage rate:** 6 of 6 planned items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 3 (narrower preserve-intent trigger, domain-count trigger for shallow-analysis, persona scoping)
- **Execution classification:** `complete`
- **Top 3 wins to protect:**
  1. `adversary/SKILL.md ## Preserve Intent Mode` — the ERROR/RISK/PREFERENCE taxonomy with "additions are cheap" rule. Protect from being widened to `challenger_mode: open` in future edits.
  2. `adversary/SKILL.md ## Shallow-Analysis Detection` — the 4-step verification that prevents false-positive PASS. Protect the `< 3 domains engaged` trigger condition.
  3. `adversary/SKILL.md ## Caller-Specified Persona Mode` — 10-persona table with explicit note not to override claim confidence or two-pass audit rule. Protect that override note.
- **Recommended next action:** complete → Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| Preserve-intent + BREAKING delta classification (adversary activates preserve-intent when delta = BREAKING) | Deferred | `specify/SKILL.md` Step 3.6 | Step 3.6 already invokes adversary for BREAKING+tagged tasks; adding automatic preserve-intent pass-through requires a field in the adversary invocation contract — left for a follow-up spec |
| Press protocol + adversary two-pass audit (unified claim verification) | Partial | `adversary/SKILL.md` | Two-pass audit and shallow-analysis detection are now both present as distinct protocols in the same file. Full unification into a single verification pass is a future cleanup, not a gap. |
| Typed document review + target-typed specify criteria | Implemented | `specify/SKILL.md` Step 4 | Product vs. Framework split added using WabbleSpec's existing `target:` vocabulary |

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Multi-persona task card review | Yes — `open-thread-tier-7-expansion-multi-20260531.json` | Yes — in drawer evidence field | Handed off |
| PRD document type generation | Yes — `open-thread-tier-7-expansion-prd-20260531.json` | Yes — in drawer evidence field | Handed off |

Both Tier 7 items handed off cleanly. Gateway bundling recommendation (gateway-spec) noted in drawer for PRD item.

---

*Execution classification: complete. All 6 items implemented. 2 Tier 7 items handed off with drawers.*
