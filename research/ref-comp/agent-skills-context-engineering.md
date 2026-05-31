# Ref-Comp: Agent Skills for Context Engineering

**Slug:** `agent-skills-context-engineering`
**Audit date:** 2026-05-31
**Based on:** `research/ref-plan/agent-skills-context-engineering.md`

---

## Literal Fidelity Pre-Check

| Item | Literal Values | Status |
|---|---|---|
| C1 | "Session Intent", "Files Modified", "Decisions Made", "Current State", "Next Steps" | EXACT — all 5 appear verbatim in executor SKILL.md |
| C3 | "Accuracy", "Context Awareness", "Artifact Trail", "Completeness", "Continuity", "Instruction Following", "Recall", "Artifact", "Continuation", "Decision" | EXACT — all 10 appear verbatim in executor SKILL.md |
| C5 | 60-70%, 70-80%, 2-3x, ~84% | ADAPTED — values present as "60–70%", "70–80%", "2–3x" (en-dashes) and "~84%". Values are semantically identical; formatting uses typographic dashes. Not corrupted. |
| C6 | "G1", "G2", "G3", "G4", "Mechanism Specificity", "Implementable Artifacts", "Beyond Basics", "Source Verifiability" | EXACT — all appear verbatim in ref-eval SKILL.md |
| C7 | "0.5 confidence", "15-25%" | EXACT — "confidence 0.5" and "15–25%" appear in adversary SKILL.md |
| C8 | "40-60%", five component names | ADAPTED — "40–60%" with en-dash; all five component names present verbatim |

---

## Section 1 — Implementation Coverage

| Item | Status | Notes |
|---|---|---|
| C1 — Anchored iterative summarization | **Implemented** | Five mandatory sections + domain variant instruction in executor CONTEXT_EXHAUSTION block |
| C2 — Artifact trail receipt validation note | **Implemented** | Note with 2.2–2.5/5.0 score range and architectural explanation in executor |
| C3 — Six compression dimensions + probe types | **Implemented** | Table of 6 dimensions + 4 probe types with descriptions in executor |
| C4 — Four-Bucket trigger conditions | **Implemented** | Trigger condition column added to existing four-bucket table in economy |
| C5 — Context budget thresholds | **Implemented** | "Context Budget Reference" callout with 4 quantitative thresholds in executor Inputs section |
| C6 — Four-gate gatekeeper criteria | **Implemented** | Step 0b pre-screening gate with G1-G4 pass/fail table before Step 1a in ref-eval |
| C7 — Position bias mitigation | **Implemented** | Comparative evaluation section with position-swap protocol, TIE/0.5 confidence, justification-before rule in adversary |
| C8 — Rubric generation template | **Implemented** | "Rubric Construction" section with 5 components + strictness calibration in skill-tdd |
| C9 — KV-cache stability rule | **Implemented** | Three-paragraph convention in CLAUDE.md skill authoring section |
| C10 — Telephone game anti-pattern | **Implemented** | "Supervisor paraphrase degradation" note with ~50% statistic in executor subagent section |
| C11 — BrowseComp 95% variance finding | **Implemented** | "Token budget vs capability upgrade tradeoff" section in model-router |
| C12 — Freedom calibration | **Implemented** | Three-level calibration (high/medium/low) with examples in CLAUDE.md |
| C13 — Nested reference anti-pattern | **Implemented** | 1-level depth rule in CLAUDE.md |

**Coverage: 13 of 13 planned items (100%)**

---

## Section 2 — Execution Gaps

No missed items. No partial items. All 13 planned Tier 1–2 items fully implemented.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk |
|---|---|---|---|---|
| C4 four-bucket (economy) | Reference provides four buckets with trigger conditions | WabbleSpec economy already had the four-bucket vocabulary; we added trigger conditions to an **existing** well-structured table rather than inserting a new section | Integration is more cohesive — trigger conditions appear as a natural column extension of the existing framework rather than a separate section competing with it | None |
| C6 gatekeeper (ref-eval) | Reference uses 4-gate screening without a WabbleSpec receipt fallback | Our implementation adds "On 2+ failures: write receipt with status SKIP" — this fits I10 (no implied completion) and closes a gap the reference didn't need (it wasn't receipt-gated) | Prevents ref-eval from silently aborting without a paper trail | None |

**Protect:** The receipt-status SKIP behavior in C6 — if this were removed, ref-eval would have a silent failure path that violates I10.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Model names in rubric thresholds | Reference uses "GPT-5.2" as LLM judge label throughout | Adopted rubric structure with all model names removed; thresholds retained | Yes — I6 requirement | Rubric is portable across capabilities; no scores tied to a specific vendor |
| BDI mental states | Reference includes full BDI ontology skill (RDF/SPARQL/Turtle) | Not adopted | Yes — domain-specific, no WabbleSpec relevance | No impact; correctly excluded |
| interleaved-thinking | Reference includes reasoning trace optimizer (MiniMax M2.1 + rto binary) | Not adopted | Yes — I6 violation + external binary dependency | Correctly excluded |
| Numeric benchmark thresholds | Reference treats 3.70/3.44/3.35 quality scores as absolute | Adopted structural patterns; noted thresholds as point-in-time signals | Yes — staleness concern | Framework is robust to model updates; thresholds won't become stale specifications |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 5 | 6 | +1 | Reference has no formal test suite; quality floor passes for all 4 primary modified modules |
| Error handling | 6 | 8 | +2 | Our implementation adds receipt-status SKIP to gatekeeper failure path — reference had no equivalent |
| Documentation | 8 | 8 | 0 | Both are well-documented; ours integrates into existing skill vocabulary |
| Naming clarity | 8 | 8 | 0 | Reference bucket/dimension names adopted verbatim where I6-clean |
| Dependency hygiene | 9 | 10 | +1 | Reference has external binary (rto) and model-specific API calls we excluded entirely |

---

## Section 6 — Verdict

- **Coverage rate:** 13 of 13 planned items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 2 (receipt-SKIP in C6, trigger-condition column integration in C4)
- **Execution classification:** `complete`
- **Top 3 wins to protect:**
  1. Anchored iterative summarization template in executor (C1) — five mandatory sections prevent silent artifact loss during compaction
  2. Four-gate gatekeeper in ref-eval (C6) with I10-compliant SKIP receipt — prevents silent abort path
  3. Artifact trail validation note in executor (C2) — formally explains why WabbleSpec's receipt chain is architecturally superior to compression-only approaches
- **Recommended next action:** Archive

---

## Section 7 — Synthesis Coverage

No Tier 6 synthesis items were in the ref-plan (all items were Tier 1–2). Section 7 is inapplicable.

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Compaction quality evaluator | `open-thread-tier-7-compaction-quality-20260531.json` | Yes | **Handed off** |
| Memory framework selection guide | `open-thread-tier-7-memory-framework-20260531.json` | Yes | **Handed off** |
