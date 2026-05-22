# Module Plan — Autopilot (L2)

**Tier:** 3 — SUPPORTING
**Layer:** L2 Orchestration
**v5.3 origin:** Autopilot module — --route flag, scale-adaptive L0-L4, exclusive counter state owner

---

## Purpose

Full lifecycle meta-orchestrator. Manages multi-stage runs from intake through delivery. Exclusively owns `.wabblespec/meta.md` — all other modules submit change requests rather than writing directly. Scale-adaptive: adjusts orchestration depth based on task complexity score from Decompose. Single-agent runs use Executor directly; Autopilot adds value for multi-stage, multi-wave, full lifecycle coordination.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/autopilot` command
- Multi-stage run declared (more than one spec stage required)
- Complexity score above high-autonomy threshold
- Full lifecycle run (P1 through Delivery in one session)

Single-wave, single-stage tasks: use Executor directly. Autopilot is not required for routine execution.

---

## Exclusive Ownership: meta.md

`.wabblespec/meta.md` is Autopilot's sole domain. No other module writes to it directly.

```markdown
# Framework Meta State

**session_id:** string
**active_stage:** P1|P2|P3|P4|Execution|Delivery
**active_wave:** integer
**lifecycle_phase:** Research|Plan|Execute
**complexity_score:** 0.0-1.0
**autonomy_level:** L0|L1|L2|L3|L4
**counter_state:**
  revise_cycles: 0
  waves_completed: 0
  stages_completed: 0
**last_updated:** timestamp
```

Other modules submit change requests to Autopilot:
- `Archive`: "increment stages_completed"
- `Executor`: "set active_wave to N"
- `Verifier`: "increment revise_cycles"

Autopilot validates and applies. Prevents concurrent write contention on shared state.

---

## Scale-Adaptive Autonomy

Autopilot selects autonomy level based on complexity score from Decompose:

| Complexity Score | Autonomy Level | Behavior |
|---|---|---|
| < 0.3 | L0 | Collapse-eligible. Minimal orchestration. |
| 0.3-0.5 | L1 | Single-stage run. Executor manages waves. |
| 0.5-0.7 | L2 | Multi-stage. Autopilot routes between stages. |
| 0.7-0.9 | L3 | Full lifecycle. Autopilot manages all phases. |
| > 0.9 | L4 | Complex multi-stage. TeamPlan may be needed. |

Autonomy level written to meta.md. Executor reads autonomy level to know how much independent action to take.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| meta.md | `.wabblespec/meta.md` | Shared framework state (exclusive ownership) |
| Autopilot receipt | `.wabblespec/receipts/autopilot-receipt.md` | I10 compliance |

---

## Workflow

```
1. Read recipe.json, scope.md, complexity score from Decompose

2. Set autonomy level in meta.md

3. Begin lifecycle orchestration:
   -> Research phase: trigger ReferenceLoad, MemorySearch, Explore
   -> Plan phase: trigger Interview, Specify, Propose, Decompose (per stage)
   -> Execute phase: trigger Executor (wave loop)

4. After each stage completes:
   -> Update meta.md (active_stage, stages_completed)
   -> Verify stage receipts present before advancing
   -> Gate next stage open

5. Process change requests from other modules:
   -> Validate request
   -> Apply to meta.md atomically
   -> Confirm to requesting module

6. On full lifecycle complete:
   -> Trigger Archive
   -> Write Autopilot receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + exclusive authority over meta.md |
| `schemas/meta.schema.json` | Schema | meta.md validation |
| `rules/autonomy-levels.md` | Rules | Complexity score to autonomy level mapping |
| `rules/change-request-policy.md` | Rules | Which modules may submit requests, valid request types |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Decompose | Reads complexity score to set autonomy level |
| Executor | Autopilot manages Executor across multi-stage runs |
| Archive | Archive submits stage_completed increment requests |
| Verifier | Verifier submits revise_cycle increment requests |
| TeamPlan | Autopilot triggers TeamPlan at L4 autonomy |
| All modules | All submit meta.md change requests through Autopilot |

---

## Verification Mode

**Observation** — meta.md exists and is consistent, autonomy level set, all stage receipts present before stage advance, no concurrent writes to meta.md detected.

---

## Receipt Extension Fields

```json
{
  "autonomy_level": "L0|L1|L2|L3|L4",
  "stages_orchestrated": "integer",
  "waves_orchestrated": "integer",
  "change_requests_processed": "integer",
  "teamplan_triggered": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 Autopilot | v6.1 Autopilot |
|---|---|
| Full lifecycle meta-orchestrator | Same |
| --route flag for model tier selection | Moved to ModelRouter |
| Scale-adaptive L0-L4 | Same — complexity score drives level |
| Counter state owner (meta.md) | Same — exclusive ownership |
| Change request model | Same |
