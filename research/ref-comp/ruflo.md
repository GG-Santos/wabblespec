# Ref-Comp: ruflo

**Audited:** 2026-05-30  
**Slug:** ruflo  
**Source plan:** `research/ref-plan/ruflo.md`  
**Execution classification:** complete

---

## Section 1 — Implementation Coverage

| Item | Status | Notes |
|---|---|---|
| R1 — Task profile assessment in Decompose Step 3 | Implemented | Step 3a block inserted; 5-dimension table; execution_mode mapping; wave plan header extended |
| R2a — Rollback trigger thresholds in Decompose Rollback Map | Implemented | 4th column `Metric threshold` added; `error_rate > 0.15 OR blockers_consecutive >= 3` |
| R2b — Rollback trigger thresholds in Rollback skill | Implemented | Metric-based trigger bullet added to `## When to use` |
| R3 — Gate name field in wave plan template | Implemented | `gate_name:` added to both Wave 1 and Wave 2 templates in output contract |
| R4 — Temporal tier labels in staleness-states.md | Implemented | `## Temporal Tiers` section appended with 4-tier table and `expires_at` guidance |

**Coverage: 5 of 5 items (100%)**

---

## Section 2 — Execution Gaps

None. All planned items implemented and gate-verified.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| execution_mode in wave plan header | Reference only used topology as runtime routing | Added `execution_mode` as a declared field in the wave plan header, not just an internal step label | Makes the topology assessment auditable in receipts and queryable by downstream tools (queue-orchestrator.py, receipt-db.py) | Executor must not treat `parallel-eligible` as a mandate — it is informational. Wave plan clearly states "Executor decides". |
| Rollback Map trigger column named `Metric threshold` rather than just `trigger_condition` | Reference used a Python dict with float values | Split into two columns: `Trigger condition` (qualitative) + `Metric threshold` (quantitative) | Preserves backward compatibility with existing qualitative triggers while adding numeric layer | None — additive column |

**Protect:** execution_mode as declared field in wave plan header — future decompose changes should preserve this field and not collapse it to a note.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| execution_mode scope | Reference: full runtime topology selector (hierarchical/mesh/ring) | Ours: simplified to sequential/parallel-eligible/sequential-pipeline — a 3-value label, not a topology system | Intentional — WabbleSpec is single-agent; full topology routing would require queue-orchestrator.py integration as a first-class path | Consequence: `parallel-eligible` is advisory. A future topology-planner module (Tier 7) would promote this to actionable. |
| Rollback thresholds | Reference: Python floats in a monitoring class (`performance_degradation: 0.25`) | Ours: example values in a Markdown table — not a runtime monitoring check | Intentional — WabbleSpec has no runtime metrics collection; thresholds are documentation guidance, not enforcement | Consequence: thresholds are human-readable policy, not machine-enforced triggers. Machine enforcement would require a metrics-collection step in Executor. |
| Temporal tiers | Reference: hierarchy diagram only | Ours: full table with `expires_at` guidance | Intentional improvement | None |

No unintentional divergences.

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 2 | 2 | 0 | Neither has automated tests for skill content; gate verification was manual script |
| Error handling | 5 | 5 | 0 | Reference has no error handling in skill prose; our additions are also additive prose |
| Documentation | 6 | 8 | +2 | execution_mode mapping table and temporal tier table are clearer than reference's Python class |
| Naming clarity | 5 | 8 | +3 | "execution_mode" and "gate_name" are more descriptive than reference's topology names |
| Dependency hygiene | N/A | N/A | N/A | Pure skill content changes, no dependencies |

---

## Section 6 — Verdict

- **Coverage rate:** 5 of 5 planned items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 2 (execution_mode as declared header field; split Rollback Map columns)
- **Execution classification:** complete
- **Top 3 wins to protect:**
  1. `execution_mode` field in wave plan header — declarative topology label for Executor routing
  2. Rollback Map `Metric threshold` column — quantitative trigger conditions alongside qualitative ones
  3. Temporal Tiers section in staleness-states.md — first explicit mapping from drawer type to expected decay horizon
- **Recommended next action:** Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| Topology-scored execution_mode in Decompose (Tier 6) | Implemented | `.claude/skills/decompose/SKILL.md` Step 3a + wave plan header | execution_mode field declared; advisory pending queue-orchestrator.py integration (Tier 7 item) |

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Parallel topology planner (days) | `.wabblespec/state/memory/wings/references/rooms/ruflo/parallel-topology-planner-expansion.md` | Yes — "Add topology-scored execution_mode to Decompose wave plan Step 3b; Executor routes parallel-eligible wave groups to queue-orchestrator.py" | Handed off |
| CRDT-based parallel wave merge (weeks) | `.wabblespec/state/memory/wings/references/rooms/ruflo/crdt-parallel-wave-merge-expansion.md` | Yes — "Build wave-merge module using LWW/OR-Set/RGA for parallel wave output convergence, integrated into queue-orchestrator.py advance step" | Handed off |
