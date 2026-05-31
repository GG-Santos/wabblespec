# Ref-Plan: agent-os Integration

**Reference:** agent-os (v3.0)
**Session:** agent-creator-integration-20260529
**Planned:** 2026-05-30
**Based on:** research/ref-eval/agent-os.md

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Ask-why probe questions for elicitation (discover-standards Step 3) | Behavioral | Low | Low (active task = guard/verifier hardening, not interview) | Low |
| A2 | Spec artifact bundle: shape.md + references.md schemas | Format | Low | Low (active task doesn't touch task-card-writer) | Low |

---

## Exclusion Filter

| Item | Excluded | Reason |
|---|---|---|
| agent-os/standards/ product-space directory model | EXCLUDED | I11: framework modules cannot write product-space paths |
| AskUserQuestion tool dependency | EXCLUDED | WabbleSpec does not use this tool in its command model |
| "Retire orchestration to frontier models" philosophy | EXCLUDED | I1: every execution must be spec-grounded |
| Profile inheritance + install scripts | EXCLUDED | Architecture mismatch; no analogous system in WabbleSpec |
| index.yml format | EXCLUDED | wabblespec.yaml already serves module registry function |
| Three-scenario injection detection | EXCLUDED | WabbleSpec's recipe+preloading handles this differently |
| shape-spec plan mode gate | EXCLUDED | WabbleSpec has no plan mode concept |
| "root" keyword routing | EXCLUDED | No analogous problem in WabbleSpec |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
Map: High=3, Medium=2, Low=1
```

| ID | impact×2 | fit | risk | score | Tier |
|---|---|---|---|---|---|
| A1 | 2 | 1 | 1 | 2 | Watch Only |
| A2 | 2 | 1 | 1 | 2 | Watch Only |

No item scores above 3. No Tier 1-2 items for immediate implementation.

---

## Tier Assignments

### Watch Only

**A1 — Ask-Why Probe Questions**

`discover-standards.md Step 3`. Three canonical probes: "What problem does this pattern solve?", "Are there exceptions?", "What is the most common mistake?"

Promote when: interview SKILL.md or ground SKILL.md is up for a revision wave, and the active task includes elicitation pattern improvement.

**A2 — Spec Artifact Bundle (shape.md + references.md)**

`shape-spec.md Steps 6-7`. shape.md schema (Scope / Decisions / Context / Standards Applied) + references.md schema (Location / Relevance / Key patterns per studied code section).

Promote when: task-card-writer.py or specify SKILL.md is being revised; or when an Executor wave-research gap is identified that a references artifact would close.

---

### Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| agent-os/standards/ product-space writes | I11: framework space / product space boundary |
| AskUserQuestion tool in command model | WabbleSpec interaction model does not use this tool |
| "Retire orchestration to frontier models" (CHANGELOG v3.0) | I1: spec-first mandate; no autonomous execution |
| Profile inheritance + install scripts | Architecture mismatch; no equivalent in WabbleSpec |

---

### Tier 6 — Synthesis Items

**S1 — Internal Reference Capture + Wave Research Integration**

Per-wave artifact recording which existing code was studied (Location / Relevance / Key patterns) before implementation begins. Reference contribution: references.md schema from shape-spec. Project contribution: Executor SKILL.md pre-implementation exploration step + research-artifact-writer.py.

Watch Only in this session. Promote when: Executor SKILL.md is up for augmentation and a wave-research gap has been documented in receipts.

**S2 — Spec Shape Artifact + Scoping Decision Capture**

shape.md artifact written after scope lock capturing scoping decisions (what was considered, rejected, why). Reference contribution: shape.md schema from shape-spec. Project contribution: scope-writer.py / task-card-writer.py extension.

Watch Only in this session. Promote when: specify SKILL.md or task-card-writer.py is being revised.

---

### Tier 7 — Expansion Roadmap

| Effort | Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Session seed |
|---|---|---|---|---|---|---|
| days | Internal reference capture artifact | shape-spec.md — references.md schema | Executor research is ephemeral; no artifact type for studied code | Prevents re-exploration across waves; Adversary can challenge research inputs | session-registry.py, Executor SKILL.md, new research-artifact-writer.py | "Build internal reference capture: add research-artifact-writer.py to shared/scripts/; extend Executor SKILL.md with optional research-capture step after exploration; wire on_archive to index into entity-graph." |
| days | Spec shape artifact | shape-spec.md — shape.md schema | task-card.md captures requirements; scope.md captures boundaries; no artifact for scoping decisions | Faster resumption after compaction; prevents re-litigating scope decisions | task-card-writer.py (extend) or new shape-writer.py | "Build spec shape artifact: add shape-writer.py to shared/scripts/ writing state/plans/shape.md with: Scope, Decisions (bulleted with rationale), Context (references/constraints), Standards Applied; extend Specify SKILL.md to call after scope lock; wire on_archive to include shape.md path in delivery receipt." |

---

## Priority Implementation Order

No Tier 1-4 items. Nothing to implement in Phase 3. Pipeline proceeds directly to Phase 4 (ref-comp).

---

## Execution Notes

- This is an inspiration-only reference (4/10). No Tier 1-2 items cleared the bar.
- Watch Only items (A1, A2) require reading interview/ground/specify SKILL.md to verify they are not already covered before promoting.
- Both Tier 7 items are handed off via memory drawers. No implementation this session.
- Gate B: autonomous mode — no user confirmation needed; skip directly to ref-comp.
