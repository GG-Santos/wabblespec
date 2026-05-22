# Module Plan — RuntimeProbe (L0)

**Tier:** 2 — CORE
**Layer:** L0 Intake
**v5.3 origin:** model-routing.md (shared reference) — formalized as standalone module in v6.1

---

## Purpose

Detect active runtime environment at session start. Determine which runtime lanes are available. Pass capability map to ModelRouter. Enforces vendor-neutral runtime (I6) — no module hardcodes a runtime name. RuntimeProbe is the only module that reads environment directly.

---

## Activation

`skill-rules.json` triggers:
- Session start (after Recipe, before any execution)
- Explicit re-probe request (environment changed mid-session)
- Ensemble activation check (ModelRouter requests lane availability)

---

## Detection

RuntimeProbe reads environment signals to determine available lanes. Never hardcodes model names — describes capabilities.

### Capability Descriptors (vendor-neutral)

| Descriptor | Meaning |
|---|---|
| `code-generation` | Can write and modify code |
| `analysis` | Can reason over complex inputs |
| `synthesis` | Can produce long-form structured output |
| `conversational` | Can handle back-and-forth dialogue |
| `tool-use` | Can call tools (Read, Write, Bash, etc.) |
| `long-context` | Can handle large context windows |
| `multimodal` | Can process images/files beyond text |
| `fast` | Optimized for low-latency responses |

### Environment Signals

| Signal | What it indicates |
|---|---|
| Available tool list | `tool-use` capability confirmed |
| Context window size | `long-context` threshold met or not |
| Session type (interactive vs. batch) | Affects `conversational` vs. `synthesis` preference |
| Runtime config file (`.wabblespec/runtime/runtime.json`) | User-declared lane preferences or restrictions |

### runtime.json (user-declared overrides)

```json
{
  "preferred_lanes": ["code-generation", "analysis"],
  "restricted_lanes": [],
  "ensemble_allowed": true,
  "fallback": "code-generation"
}
```

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Capability map | Passed to ModelRouter (in-memory) | Lane selection input |
| `runtime-state.json` | `.wabblespec/runtime/runtime-state.json` | Persisted probe result for session |
| RuntimeProbe receipt | `.wabblespec/receipts/runtimeprobe-receipt.md` | I10 compliance |

### runtime-state.json structure

```json
{
  "available_capabilities": ["code-generation", "analysis", "tool-use"],
  "unavailable_capabilities": ["multimodal"],
  "ensemble_allowed": true,
  "fallback": "code-generation",
  "probed_at": "timestamp",
  "session_id": "string"
}
```

---

## Workflow

```
1. Read .wabblespec/runtime/runtime.json if exists (user overrides)

2. Probe environment:
   -> Check available tools
   -> Check context window characteristics
   -> Check session type

3. Map probed signals to capability descriptors

4. Apply user overrides from runtime.json

5. Write runtime-state.json

6. Pass capability map to ModelRouter

7. Write RuntimeProbe receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over runtime-state.json |
| `schemas/runtime-state.schema.json` | Schema | runtime-state.json validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |
| `references/capability-descriptors.md` | Reference | Canonical vendor-neutral descriptor definitions |
| `rules/probe-policy.md` | Rules | What signals map to what capabilities |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | RuntimeProbe fires after Recipe declares target |
| ModelRouter | Reads capability map from RuntimeProbe |
| Ensemble | Checks runtime-state.json for ensemble_allowed and available lanes |
| Economy | Reads runtime-state.json for context window size (informs budget advice) |

---

## Verification Mode

**Observation** — runtime-state.json exists, has at least one available capability, fallback is declared, ModelRouter has received capability map.

---

## Receipt Extension Fields

```json
{
  "available_capabilities": "array",
  "unavailable_capabilities": "array",
  "ensemble_allowed": "boolean",
  "fallback": "string",
  "user_overrides_applied": "boolean"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Re-probe trigger | Session start only vs. on capability change detection | Per-module planning |
| Capability descriptor list | Fixed 8 (current) vs. extensible | Per-module planning |
| runtime.json location | `.wabblespec/runtime/` (current) vs. project root | Per-module planning |
