# Cold-Start Behavior — Platform AI Agent

Defines how the AI agent platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `_shared/dev/frameworks/ai/core.md` or `_shared/dev/frameworks/ai/safety.md` missing.
Detection: File read returns 404.
Action: Log warning — "AI framework files missing. Model pinning, prompt injection, and output validation rules not loaded." Apply continues.
Do NOT: Silently omit safety requirements. The warning surfaces to the Specify output so the author knows safety context was reduced.

## Absent: conditional framework files

Condition: `_shared/dev/frameworks/ai/langchain.md` or `ai/openai-sdk.md` absent when framework is detected.
Detection: Detected via `langchain` in requirements.txt / `anthropic` or `openai` in package.json but file not found.
Action: Proceed without file. Log: "AI framework file not found: [path]."

## Absent: gateway-ai reference files

Condition: `modules/l4/ai/references/safety.md`, `references/evals.md`, or `references/cost.md` absent.
Detection: File read returns 404 during Phase A gateway evaluation.
Action: Gateway-ai Phase A produces a reduced context receipt. Note which reference files were absent. Phase B proceeds with reduced input.
Do NOT: Skip gateway-ai evaluation. Use whatever reference files are present.

## Absent: security reference files

Condition: `modules/l3/ai-agent/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security uses generic controls. Prompt injection and PII-in-context rules remain enforced as platform invariants.

## Absent: spec-template files

Condition: `modules/l3/ai-agent/spec-template/design-document.md` absent.
Action: Specify uses generic structure.

## Default state on cold start

| Field | Default |
|---|---|
| `model` | Not declared — Specify must elicit AND require exact model ID (no "latest") |
| `model_pinning` | Required — no floating "latest" references; Specify must elicit pinned model ID |
| `prompt_version` | Not declared — versioning required; Specify must elicit strategy |
| `eval_harness` | Not declared — Specify must elicit; eval harness is required before production |
| `context_budget` | Not declared — Specify must elicit token budget per call |
| `output_validation` | Not declared — schema or type validation required for all structured outputs |
| `pii_in_context` | Forbidden unless explicitly declared with masking strategy |
| `agentic_scope` | Not declared — Specify must elicit max autonomy level (read-only / write / deploy) |

Model pinning and output validation are platform invariants — enforced even without framework files.
