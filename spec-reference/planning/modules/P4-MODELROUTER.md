# Module Plan — ModelRouter (L2)

**Tier:** 2 — CORE
**Layer:** L2 Orchestration
**v5.3 origin:** model-routing.md shared reference — formalized as standalone module in v6.1

---

## Purpose

Route each task to the best available runtime lane. Reads capability map from RuntimeProbe. Reads context-type classification from Economy. Enforces vendor-neutral routing (I6) — decisions are based on capability descriptors, never model names. Declares selection in runtime receipt. Triggers Ensemble when single-lane coverage is insufficient.

---

## Activation

`skill-rules.json` triggers:
- After RuntimeProbe (every session)
- Before each task execution (Executor requests routing)
- Ensemble evaluation request
- Confidence-below-threshold re-route

---

## Routing Logic

### Inputs

1. Capability map from RuntimeProbe (what is available)
2. Context-type classification from Economy (what the task needs)
3. Task shape (derived from current stage, phase, and module)
4. Verification mode of target module (from `skill-rules.json`)

### Context-Type to Capability Mapping

| Context Type | Required Capabilities | Preferred |
|---|---|---|
| creative | synthesis, long-context | synthesis |
| analytical | analysis, long-context | analysis |
| code | code-generation, tool-use | code-generation |
| conversational | conversational, fast | conversational |
| technical | analysis, tool-use | analysis |

### Routing Decision

```
1. Read task context-type from Economy
2. Map context-type to required capabilities
3. Check capability map from RuntimeProbe
   -> IF all required capabilities available in single lane: route single lane
   -> IF gap: check Ensemble trigger conditions
4. Ensemble trigger conditions:
   -> Task spans multiple build targets simultaneously
   -> No single lane covers all required capabilities
   -> Verification mode is Attestation or Audit
   -> Confidence below threshold after single-lane attempt
5. IF Ensemble triggered: coordinate lanes, write combined receipt
6. IF single lane: write runtime receipt
```

### Fallback

If preferred lane unavailable: use fallback from `runtime-state.json`. Fallback is always a single capability descriptor. If fallback also unavailable: emit HARD error, halt.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Routing decision | Passed to Executor (in-context) | Execution lane selection |
| Runtime receipt | `.wabblespec/receipts/runtime-<timestamp>.md` | I10 compliance |

Runtime receipt required fields (from I6):
```json
{
  "selected": "capability descriptor",
  "reason": "why this lane was chosen",
  "task_shape": "creative|analytical|code|conversational|technical",
  "available_tools": ["list of available tools"],
  "fallback": "fallback capability descriptor",
  "verification_mode": "mode from target module skill-rules.json"
}
```

---

## Workflow

```
1. Receive task from Executor (stage, phase, module, verification mode)

2. Request context-type classification from Economy

3. Map context-type to required capabilities

4. Read capability map from RuntimeProbe (runtime-state.json)

5. Check single-lane coverage:
   -> All required capabilities available? -> single lane
   -> Gap detected? -> evaluate Ensemble conditions

6. Evaluate Ensemble conditions (if gap):
   -> Multi-target span? -> Ensemble
   -> Attestation/Audit mode? -> Ensemble
   -> Below confidence threshold? -> Ensemble
   -> Otherwise: use closest single lane with noted gap

7. Write runtime receipt

8. Pass selection to Executor
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over routing decisions |
| `references/capability-descriptors.md` | Reference | Canonical capability descriptor definitions (shared with RuntimeProbe) |
| `rules/routing-policy.md` | Rules | Context-type to capability mapping; Ensemble trigger thresholds |
| `rules/fallback-policy.md` | Rules | Fallback selection when preferred lane unavailable |
| `schemas/runtime-receipt.schema.json` | Schema | Runtime receipt validation (extends base receipt) |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| RuntimeProbe | Reads capability map from runtime-state.json |
| Economy | Reads context-type classification |
| Ensemble | ModelRouter triggers Ensemble when conditions met |
| Executor | ModelRouter passes routing decision to Executor before each task |
| Verifier | Reads verification_mode from routing decision to select gate |

---

## Verification Mode

**Observation** — routing decision made, runtime receipt written, selected capability present in available capabilities, fallback declared.

---

## Receipt Extension Fields

```json
{
  "context_type": "string",
  "required_capabilities": "array",
  "selected_capability": "string",
  "ensemble_triggered": "boolean",
  "ensemble_lanes": "array",
  "gap_noted": "boolean",
  "gap_description": "string",
  "fallback_used": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 model-routing.md | v6.1 ModelRouter |
|---|---|
| Shared reference — advisory only | Standalone module — enforced |
| Context-type classification (enriched v5.3) | Same — 5 types |
| Sampling parameter profiles | Moved to Economy |
| No Ensemble concept | Ensemble trigger conditions added |
| No runtime receipt | Runtime receipt required (I10) |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Confidence threshold for re-route | 0.7 (proposed) vs. configurable | Per-module planning |
| Ensemble coordination mechanism | ModelRouter orchestrates vs. Ensemble module takes over fully | Resolve during Ensemble planning |
| Gap handling | Route with noted gap (current) vs. always Ensemble on gap | Per-module planning |
