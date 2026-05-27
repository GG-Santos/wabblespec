# InferenceGuard Activation Policy

## Gateway conditions

InferenceGuard activates when **at least one** of the following holds:
- Active gateway is `gateway-security` (gateway-security spec receipt present in session)
- `task_type` in task card is one of: `security`, `pentest`, `red-team`, `vulnerability-analysis`, `threat-model`, `security-audit`

Neither condition alone triggers a receipt — both gateway check and trigger detection must pass before a transformation receipt is written.

## Suppression flag

`inference_guard: false` in task card suppresses InferenceGuard unconditionally.

**Required for Blue protocol.** Blue works with explicit vulnerability names and cannot function with transforms applied. The task card for any Blue phase MUST declare `inference_guard: false`.

Suppression receipt is written when this flag is present:
```json
{ "module": "inference-guard", "activated": false, "reason": "suppressed" }
```

## Tier selection

| Context | Default tier |
|---|---|
| Red protocol task | `standard` |
| General security task (not Red) | `light` |
| Explicit declaration in task card | Overrides default |

`inference_guard_tier: heavy` in task card enables Tier 3 triggers. No other mechanism enables Tier 3.

## Technique selection

Default technique: `leetspeak`.

Override in task card: `inference_guard_technique: unicode | mixedcase | random`

## Intensity levels

Intensity controls transform density within a trigger word:
- `low` — single character substitution per word
- `medium` — up to half of eligible characters (default)
- `high` — all eligible characters substituted

Default intensity: `medium`.

## What does NOT trigger activation

- `inference_guard: false` is present
- Gateway is inactive and task_type is not security-typed
- No triggers detected in input (module runs, detects nothing, writes non-activation receipt)
- Task type is: code-generation, spec-authoring, planning, administrative, documentation, synthesis

## Edge cases

**Mixed-context task** (code generation + security review): use the dominant task shape from model-router classification. If security is declared in task_type, InferenceGuard activates regardless of code content.

**Tier 3 without explicit flag**: Tier 3 terms in input are NOT matched unless `inference_guard_tier: heavy` is declared. This prevents accidental heavy-tier activation from general vocabulary overlap.
