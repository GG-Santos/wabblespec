# Module Plan — Ensemble (L2)

**Tier:** 3 — SUPPORTING
**Layer:** L2 Orchestration
**v5.3 origin:** No equivalent — new in v6.1 (vendor-neutral runtime triad concept)

---

## Purpose

Coordinate multiple runtime lanes for tasks that no single lane can cover adequately. Triggered exclusively by ModelRouter when Ensemble conditions are met. Single-lane execution is always the default. Ensemble is the explicit exception. Writes combined receipt naming all lanes used.

---

## Activation

`skill-rules.json` triggers:
- ModelRouter evaluates Ensemble conditions and triggers Ensemble (not user-triggered directly)
- Explicit `/ensemble` command with declared task and lanes

Ensemble trigger conditions (from ModelRouter):
1. Task spans multiple build targets simultaneously
2. No single available lane covers all required capabilities
3. Verification mode is Attestation or Audit (independent confirmation needed)
4. Confidence below threshold after single-lane attempt

All four conditions must be evaluated. Any one can trigger Ensemble.

---

## Lane Coordination Model

Ensemble does not run lanes in parallel by default. Coordination modes:

| Mode | When used | How it works |
|---|---|---|
| Sequential | Lane B needs Lane A output | A completes, output passed to B |
| Independent | Lanes produce independent artifacts | Both run, outputs merged |
| Cross-check | Independent confirmation required | Both run same task, Grader compares outputs |

Cross-check mode is required for Attestation and Audit verification modes — two lanes must independently reach the same conclusion before Verifier issues PASS.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Combined receipt | `.wabblespec/receipts/ensemble-receipt-<timestamp>.md` | Names all lanes, coordination mode, outputs per lane |
| Merged output | Passed to Executor | Combined artifact from all lanes |

### Combined receipt structure

```markdown
# Ensemble Receipt

**timestamp:** datetime
**trigger_condition:** string
**coordination_mode:** sequential|independent|cross-check
**lanes_used:** [capability descriptors]

## Lane Results

| Lane | Capability | Output | Confidence |
|---|---|---|---|
| Lane 1 | code-generation | path/to/output | 0.9 |
| Lane 2 | analysis | path/to/output | 0.85 |

## Merge Strategy

<how outputs were combined>

## Cross-Check Result (if applicable)

**agreement:** true|false
**divergence_notes:** <if false>
```

---

## Workflow

```
1. Receive trigger from ModelRouter with:
   -> Trigger condition
   -> Required capabilities
   -> Available lanes from runtime-state.json

2. Select coordination mode based on task shape and trigger condition:
   -> Attestation/Audit: cross-check
   -> Capability gap: sequential or independent
   -> Multi-target span: independent with merge

3. Assign capabilities to lanes

4. Execute lanes in declared coordination mode

5. Merge or cross-check outputs:
   -> IF cross-check: route both outputs to Grader for comparison
   -> IF independent: merge outputs, note any conflicts
   -> IF sequential: pass Lane A output to Lane B as input

6. Write combined receipt

7. Pass merged output to Executor
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — triggered by ModelRouter only |
| `rules/coordination-modes.md` | Rules | When to use sequential vs. independent vs. cross-check |
| `rules/merge-policy.md` | Rules | How to merge independent outputs; conflict handling |
| `schemas/ensemble-receipt.schema.json` | Schema | Combined receipt validation |
| `schemas/receipt.schema.json` | Schema | Module receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| ModelRouter | ModelRouter is the only module that triggers Ensemble (except explicit command) |
| RuntimeProbe | Ensemble reads available lanes from runtime-state.json |
| Grader | Cross-check mode routes both outputs to Grader for comparison |
| Executor | Ensemble passes merged output to Executor after coordination |
| Verifier | Verifier receives combined receipt as part of wave verification |

---

## Verification Mode

**Observation** — all declared lanes produced output, combined receipt names all lanes, cross-check agreement recorded (if applicable).

---

## Receipt Extension Fields

```json
{
  "trigger_condition": "string",
  "coordination_mode": "sequential|independent|cross-check",
  "lanes_used": "integer",
  "cross_check_agreement": "boolean",
  "merge_conflicts": "integer"
}
```
