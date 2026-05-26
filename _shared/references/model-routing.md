# Model Routing

Model tier routing by task shape and context type. ModelRouter reads runtime-state.json (written by runtime-probe) and selects capability descriptors. Never routes by model name — capability-first.

## Capability descriptors (from runtime-state.json)

| Descriptor | Meaning |
|---|---|
| `extended_thinking` | Supports deep reasoning passes before output |
| `large_context` | Context window > 100K tokens |
| `fast_output` | Low latency, optimized for interactive tasks |
| `multimodal` | Supports image/audio input |
| `code_execution` | Can run code in a sandbox |
| `tool_use` | Supports structured tool calls |
| `batch_processing` | Supports async batch API |
| `prompt_caching` | Supports KV-cache prefix caching |

## Task shape → capability mapping

| Task shape | Required capabilities | Optional |
|---|---|---|
| Complex reasoning / architecture | `extended_thinking`, `large_context` | `tool_use` |
| Code generation | `tool_use`, `code_execution` | `extended_thinking` |
| Fast interactive | `fast_output` | `tool_use` |
| Long document analysis | `large_context`, `prompt_caching` | `extended_thinking` |
| Multi-modal review | `multimodal` | `large_context` |
| Batch evaluation | `batch_processing` | `prompt_caching` |

## Context type profiles (5 types × 6 parameters)

### Type 1 — Spec/reasoning context
Temperature: low (0.2–0.4). Max tokens: high. Stop sequences: none. Top-p: 0.9. System prompt: full framework context. Cache: system prompt + framework files.

### Type 2 — Code generation context
Temperature: 0.1–0.3. Max tokens: medium-high. Stop sequences: code block markers. Top-p: 0.95. System prompt: language + platform context. Cache: system prompt.

### Type 3 — Interactive/clarification context
Temperature: 0.5–0.7. Max tokens: low-medium. Stop sequences: question marks (optional). Top-p: 0.9. System prompt: minimal. Cache: none (short lived).

### Type 4 — Evaluation/grading context
Temperature: 0.1. Max tokens: medium. Stop sequences: verdict tokens. Top-p: 0.85. System prompt: spec + rubric. Cache: spec + rubric.

### Type 5 — Creative/expression context
Temperature: 0.7–0.9. Max tokens: high. Stop sequences: none. Top-p: 0.95. System prompt: style + audience. Cache: style guide.

## Routing fallback

If runtime-state.json is absent or capability is UNKNOWN: route to the most capable available option. Log the fallback in the model-router receipt. Do not fail — degrade gracefully.

## Override

User override via `runtime.json` in project root takes precedence over runtime-state.json. Format: `{ "capability_overrides": { "extended_thinking": true } }`.
