# Ref-Plan: ruflo

**Planned:** 2026-05-30  
**Slug:** ruflo  
**Source eval:** `research/ref-eval/ruflo.md`  
**Overall verdict from eval:** inspiration-only (4/10)

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| R1 | Topology decision matrix → Decompose Step 3 task profile | Behavioral | Medium | High (directly serves Decompose wave strategy) | Low |
| R2 | Rollback trigger thresholds → Decompose Rollback Map + Rollback skill | Behavioral | Medium | High (fills quantitative gap in existing rollback conditions) | Low |
| R3 | Quality gate naming → wave plan checkpoint blocks | Format | Low | Medium (aesthetic improvement, self-documenting) | Low |
| R4 | Temporal tier labels → staleness-states.md | Format | Low | Medium (adds vocabulary to existing staleness model) | Low |
| R5 | Worker progress payload schema → receipt-writer.py | Behavioral | Low | Low (interesting but requires a dedicated schema task) | Medium |

---

## Exclusion List

| Item | Reason |
|---|---|
| All MCP vendor tool prefixes (`mcp__claude-flow__*`, `mcp__flow-nexus__*`) | I6 — vendor names in framework files |
| Model names in config.toml (`gpt-5.3-codex`, `claude-sonnet`, `claude-opus`) | I6 — no model names anywhere in framework files |
| Memory-as-completion-signal ("write every 30 seconds", "MANDATORY status writes") | I10 — memory writes are not receipts |
| SONA/HNSW performance benchmark claims ("+55% quality", "150x faster", "2211 ops/sec") | Unverifiable marketing numbers; would corrupt instinct observations if cited |
| CRDT implementations (G-Counter, OR-Set, LWW-Register, RGA) | Wrong runtime model — WabbleSpec is single-agent; CRDTs solve multi-node conflicts |
| Multi-agent topology as runtime infrastructure | Architecture incompatibility — WabbleSpec single-agent; swarm spawning requires a different execution model entirely |
| R5 (worker progress payload schema) | Project fit Low AND requires dedicated receipt-writer.py schema task — not appropriate for this pipeline |

---

## Scores

```
integration_score = (impact × 2) + project_fit - risk
Map: High=3, Medium=2, Low=1
```

| ID | Impact×2 | Fit | Risk | Score |
|---|---|---|---|---|
| R1 | 4 | 3 | 1 | 6 |
| R2 | 4 | 3 | 1 | 6 |
| R3 | 2 | 2 | 1 | 3 |
| R4 | 2 | 2 | 1 | 3 |

---

## Tier Assignments

**Tier 1 — Behavioral additions (additive to existing file, no new files):**
- **R1** — Add `## Task Profile` assessment block to `decompose/SKILL.md` Step 3 (before wave sequencing). The 5-dimension profile guides assignment of `execution_mode` label in wave plan output.
- **R2** — Add `rollback_triggers` block to the Rollback Map in `decompose/SKILL.md` output contract, and add a note about numeric trigger conditions to `rollback/SKILL.md`.
- **R3** — Add optional `gate_name:` field to wave plan checkpoint format in `decompose/SKILL.md` output contract.

**Tier 2 — Module-level augmentation:**
- **R4** — Add `temporal_tier` vocabulary to `engine/shared/references/staleness-states.md`.

**Tier 6 — Synthesis (both dimensions required):**
- Topology-scored execution mode in Decompose: WabbleSpec's existing complexity scoring (Recipe) + queue-orchestrator.py parallel dispatch + ruflo's 5-dimension task profile → produces `execution_mode: parallel|sequential|mixed` per wave group.

**Tier 7 — Expansion Roadmap:**

| Capability | Reference | Why project lacks it | What it unlocks | Effort | Session seed |
|---|---|---|---|---|---|
| Parallel topology planner | adaptive-coordinator lines 88-134 | queue-orchestrator.py exists but no topology analysis feeds it | execution_mode field in wave plan; reduces serialization of independent waves | days | "Add topology-scored execution_mode to Decompose wave plan Step 3b" |
| CRDT-based parallel wave merge | crdt-synchronizer full skill | No merge semantics for parallel wave file writes | True parallel execution without file conflict risk | weeks | "Build wave-merge module using LWW/OR-Set/RGA for parallel wave output convergence" |

**Do-Not-Copy List:**
- MCP vendor prefixes — I6
- Model names — I6
- Memory-as-completion — I10
- SONA benchmark claims — unverifiable
- Multi-agent topology as infrastructure — architecture incompatibility

---

## Priority Implementation Order

| ID | Item | Target | Why first | Gate |
|---|---|---|---|---|
| R1 | Task profile assessment block | `skills/decompose/SKILL.md` Step 3 | Highest integration score (6); zero risk; pure additive | Decompose Step 3 contains `## Task Profile` section with 5 dimensions |
| R2 | Rollback trigger thresholds | `skills/decompose/SKILL.md` Rollback Map + `skills/rollback/SKILL.md` | Equal score (6); fills genuine qualitative gap | Decompose output contract Rollback Map has `trigger_condition:` field; Rollback skill references numeric conditions |
| R3 | Gate naming | `skills/decompose/SKILL.md` output contract | Low score but zero-risk format improvement | Wave plan checkpoint blocks include optional `gate_name:` |
| R4 | Temporal tier labels | `engine/shared/references/staleness-states.md` | Supporting reference improvement | staleness-states.md includes `temporal_tier` vocabulary section |

---

## Phase 1 Items (Implement now)

### R1 — Task Profile Assessment in Decompose Step 3

**What:** Add a 5-dimension task profile assessment to Step 3 of Decompose, producing an `execution_mode` label for wave groups.

**Where:** `.claude/skills/decompose/SKILL.md` Step 3 (between the opening "Rules:" block and the "Rollback target selection per wave" table)

**How:** Insert a `### Step 3a — Assess task profile` sub-step:

```
Before sequencing waves, assess these 5 dimensions from the task card:
- complexity: Low/Medium/High (already scored in Recipe — confirm here)
- parallelizability: High = outputs don't depend on each other; Low = sequential dependency chain
- interdependencies: few / many / sequential
- resource_requirements: Low (single skill) / Medium (multi-file) / High (schema + impl + tests)
- time_sensitivity: Low (no deadline) / High (blocking other waves)

Map to execution_mode:
- complexity=High AND interdependencies=many → sequential (central coordination needed)
- parallelizability=High AND interdependencies=few → parallel-eligible (flag for queue-orchestrator.py)
- interdependencies=sequential → sequential-pipeline
- else → sequential (safe default)

Record execution_mode in wave plan header. A value of parallel-eligible is informational — Executor decides whether to invoke queue-orchestrator.py.
```

**Gate:** Decompose output contains `execution_mode:` field in the wave plan header.

**Reference location:** `agent-adaptive-coordinator/SKILL.md` lines 88-134

---

### R2 — Rollback Trigger Thresholds in Decompose + Rollback

**What:** Add quantitative `trigger_condition` to the Rollback Map in Decompose output contract. Add a note in Rollback skill about numeric conditions.

**Where (A):** `.claude/skills/decompose/SKILL.md` — the Rollback Map table in `## Output contract`

**How (A):** Extend the Rollback Map table header from 3 columns to 4, adding `trigger_condition`:

```markdown
| Wave | Rollback target | Trigger condition | Notes |
|---|---|---|---|
| Wave 2 fails | Wave 1 checkpoint | HARD error OR error_rate > 0.15 | |
| Wave 3 fails | Wave 2 checkpoint | HARD error OR blockers_consecutive >= 3 | |
```

**Where (B):** `.claude/skills/rollback/SKILL.md` — the `## When to use` section

**How (B):** Add one bullet to the trigger list: `- Executor reports a metric-based trigger condition from the wave plan's Rollback Map (e.g. error_rate > 0.15)`

**Gate:** Decompose Rollback Map table has 4 columns including `trigger_condition`; Rollback skill trigger list includes metric-based condition.

**Reference location:** `agent-adaptive-coordinator/SKILL.md` lines 330-358

---

### R3 — Gate Name Field in Wave Plan Checkpoint

**What:** Add optional `gate_name:` to the wave plan checkpoint block format.

**Where:** `.claude/skills/decompose/SKILL.md` — the `## Output contract` wave block template

**How:** Add one line to the wave block template:

```
**gate_name:** <optional human-readable quality gate label — e.g. "Schema Locked", "Tests Green">
```

**Gate:** Wave plan template in output contract includes `gate_name:` field.

**Reference location:** `agent-sparc-coordinator/SKILL.md` lines 69-88

---

## Phase 2 Item

### R4 — Temporal Tier Labels in Staleness Reference

**What:** Add a `Temporal Tiers` vocabulary section to staleness-states.md.

**Where:** `.wabblespec/engine/shared/references/staleness-states.md`

**How:** Append a short section that maps drawer types to temporal tier labels (Global/Long-term, Project/Medium-term, Session/Short-term, Task/Ephemeral). This supplements the existing staleness state model — not a replacement.

**Gate:** staleness-states.md contains a `## Temporal Tiers` section.

**Reference location:** `agent-memory-coordinator/SKILL.md` lines 138-145

---

## Execution Notes

- R1 and R2 both touch `decompose/SKILL.md` — apply sequentially in order R1 then R2, not in parallel.
- R3 also touches `decompose/SKILL.md` — apply after R2.
- R4 is independent — can run after R1-R3 complete.
- No Specify required for any Phase 1 item (all additive, no architectural change).
- No breaking change risk — all additions use optional fields.
- R4 touches framework space (`.wabblespec/`) — this is a reference doc update, not a product-space write. I11 permits framework docs to be updated by framework-authoring tasks; this ref-adopt pipeline is a framework-authoring operation.
