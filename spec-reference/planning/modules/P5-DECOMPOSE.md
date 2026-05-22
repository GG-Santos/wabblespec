# Module Plan — Decompose (L1)

**Tier:** 2 — CORE
**Layer:** L1 Spec Core
**v5.3 origin:** Decompose module — step-files, wave execution, rollback checkpoints

---

## Purpose

Break a locked spec into an ordered wave plan for Executor. Each wave is a discrete, verifiable unit of work with a rollback checkpoint. Decompose produces the execution contract — Executor runs it but does not modify it. Decompose also scores task complexity and declares gate-collapsing eligibility for Recipe.

---

## Activation

`skill-rules.json` triggers:
- Spec stage locks (P1, P2, P3, P4 each trigger Decompose for that stage)
- Explicit `/decompose` command
- Apply detects BREAKING deviation mid-execution (re-decompose required for affected stage)

---

## Wave Plan Structure

```markdown
# Wave Plan

**spec:** <path to locked spec artifact>
**stage:** P1|P2|P3|P4
**target:** build target
**complexity_score:** 0.0-1.0
**collapse_eligible:** true|false
**generated_at:** timestamp

## Waves

### Wave 1: <name>

**modules:** [list of modules to activate]
**inputs:** [spec sections, prior wave outputs]
**outputs:** [expected artifacts]
**checkpoint:** <what must be true before Wave 2 begins>
**rollback_to:** null (Wave 1 has no prior checkpoint)
**verification_mode:** Test|Review|Audit|Measurement|Observation|Attestation|Demonstration

---

### Wave 2: <name>

**modules:** [list]
**inputs:** [Wave 1 outputs + spec sections]
**outputs:** [expected artifacts]
**checkpoint:** <what must be true before Wave 3 begins>
**rollback_to:** Wave 1 checkpoint state
**verification_mode:** <mode>

---

[... per wave ...]

## Rollback Map

| Wave | Rollback target | Condition |
|---|---|---|
| Wave 2 fails | Wave 1 checkpoint | HARD error or verification FAIL after 3 cycles |
```

---

## Complexity Scoring

Decompose scores task complexity before producing wave plan. Score drives gate-collapsing eligibility.

| Factor | Weight |
|---|---|
| Spec depth (P1 only vs. P1-P4) | 30% |
| Number of affected modules | 25% |
| Number of integration points | 20% |
| Presence of BREAKING spec changes | 15% |
| New vs. existing code ratio | 10% |

Score range 0.0-1.0. Score < 0.3 AND spec depth = P1 only = collapse_eligible: true.

---

## Rollback Checkpoints

Every wave (except Wave 1) declares a rollback target. Rollback rules:

- Rollback is always to the last successful wave checkpoint
- Rollback never skips checkpoints
- Rollback is always human-confirmed (Attestation required)
- Partial wave output is not preserved — rollback restores full prior checkpoint state

Checkpoint state is declared in wave plan. Executor is responsible for saving checkpoint state before beginning each wave.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Wave plan | `.wabblespec/plans/current-wave-plan.md` | Executor input |
| Complexity score | Embedded in wave plan + reported to Recipe | Gate collapsing eligibility |
| Decompose receipt | `.wabblespec/receipts/decompose-receipt.md` | I10 compliance |

---

## Workflow

```
1. Read locked spec artifact for current stage

2. Read scope.md (boundary enforcement)

3. Read project-map.md (size waves against actual codebase)

4. Score task complexity across 5 factors

5. Declare collapse_eligible (complexity < 0.3 AND P1 only)

6. Identify required modules per wave:
   -> Platform modules for target
   -> Capability gateways required
   -> _shared/dev/ references needed

7. Sequence waves:
   -> Each wave must be independently verifiable
   -> No wave depends on partial output of another wave
   -> Integration waves come after component waves

8. Assign rollback targets:
   -> Wave 1: null
   -> Wave N: Wave N-1 checkpoint

9. Assign verification mode per wave from module skill-rules.json

10. Write wave plan

11. Route to Reviewer (adversarial review of wave plan — budget-gated)

12. Write Decompose receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over wave plan |
| `scripts/complexity-scorer.py` | Script | Deterministic complexity scoring (from _shared/scripts/) |
| `rules/wave-sequencing.md` | Rules | How to order waves, integration wave rules |
| `rules/rollback-policy.md` | Rules | Rollback trigger conditions, human confirmation requirement |
| `schemas/wave-plan.schema.json` | Schema | Wave plan validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Specify | Reads locked spec. Cannot run until spec is LOCKED. |
| Recipe | Reports collapse_eligible to recipe.json |
| Executor | Reads wave plan — primary consumer |
| Reviewer | Wave plan routed for adversarial review (budget-gated) |
| Apply | Apply executes within each wave. Reports deviations back to Decompose trigger. |
| Verifier | Verifier runs at each wave checkpoint using declared verification_mode |
| project-map.md | Sizes waves against actual codebase complexity |

---

## Verification Mode

**Review** — wave plan reviewed by Reviewer before Executor runs. Wave sequence is verifiable. Each wave has declared checkpoint and rollback target.

---

## Receipt Extension Fields

```json
{
  "spec_stage": "P1|P2|P3|P4",
  "wave_count": "integer",
  "complexity_score": "number",
  "collapse_eligible": "boolean",
  "modules_required": "array",
  "rollback_checkpoints": "integer",
  "reviewer_triggered": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 Decompose | v6.1 Decompose |
|---|---|
| Step-files, sub-task chains | Wave plan with rollback checkpoints |
| Wave rollback checkpoints (v5.2+) | Same — extended with human-confirmation requirement |
| No complexity scoring | Complexity score added, drives collapse_eligible |
| No gate collapsing concept | collapse_eligible declared here |
| Routes to Apply | Routes to Executor (which manages Apply) |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Max waves per plan | Unlimited vs. soft limit (e.g., 10) requiring human review | Per-module planning |
| Wave granularity | File-level vs. feature-level vs. module-level | Per-target decision during platform planning |
| Complexity score calibration | 5 factors (current) vs. calibrated against real project data | After first real project run |
