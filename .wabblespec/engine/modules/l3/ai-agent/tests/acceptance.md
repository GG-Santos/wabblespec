# Platform AI/Agent — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified AI/Agent as the primary target,
When platform-ai-agent is invoked,
Then it surfaces: "platform-ai-agent requires Recipe to have identified AI/Agent as the primary target first."
Then no platform activation receipt is written.

## L4 AI gateway mandatory

Given Recipe has identified AI/Agent as the primary target,
When platform-ai-agent activates,
Then `modules/l4/ai/` is loaded before any other spec files.
Then the L4 AI gateway is not optional — it cannot be skipped.
Then the activation receipt records `ai_gateway_loaded: true`.

## Happy path: activation sequence

Given L4 AI gateway is loaded,
When platform-ai-agent continues activation,
Then the sequence completes: AI gateway → spec-template → engineering → security → Verifier gate registration → receipt write.
Then no step is skipped.

## AI-specific concerns injected into spec

Given platform-ai-agent is active,
When spec context is assembled,
Then model pinning is declared — no `latest` identifiers permitted.
Then eval harness is declared: at minimum 10 golden fixtures per capability.
Then prompt versioning is addressed: system prompts version-controlled.
Then cost safeguards are declared: token budgets per call and per session.
Then failure modes are enumerated: hallucination, prompt injection, refusal, cost explosion.
Then safety boundaries are declared.
Then non-determinism is acknowledged: eval pass rate is the success signal, not HTTP status.

## Framework routing: LangChain

Given `langchain` is in dependencies,
When platform-ai-agent detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/ai/langchain.md` is loaded.

## Framework routing: OpenAI SDK

Given `openai` is in dependencies,
When platform-ai-agent detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/ai/openai-sdk.md` is loaded.

## Agent loop bounds declared

Given the spec includes an agent loop (LLM invoking tools across multiple turns),
When spec context is assembled,
Then maximum iteration count is declared.
Then irreversible tool call Attestation gate is declared.
Then cycle detection mechanism is declared.

## Eval suite declared before deploy

Given platform-ai-agent is active,
When the spec is assembled,
Then the spec declares that model version bumps and prompt changes require eval suite re-run before deployment.
Then the spec declares adversarial fixture coverage (at minimum one injection attempt per input surface).

## Capability handoff

Given platform-ai-agent has activated,
When the capability handoff is declared in the receipt,
Then `.wabblespec/engine/shared/dev/frameworks/ai/core.md` and `.wabblespec/engine/shared/dev/frameworks/ai/safety.md` are always loaded.
Then gateway-ai/references/ is always included.
Then gateway-security/references/ is included.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-ai-agent attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-ai-agent run,
Then platform-ai-agent does not skip the L4 AI gateway.
Then platform-ai-agent does not allow model identifiers without explicit version pinning.
Then platform-ai-agent does not treat AI success signal as HTTP 200 — eval pass rate is the signal.

## Receipt fields

Given any successful platform-ai-agent activation,
Then a receipt is written to `.wabblespec/state/receipts/platform-ai-agent-<timestamp>.json`.
Then the receipt contains: platform, ai_gateway_loaded, model_pinning_declared, eval_harness_declared, cost_safeguards_declared, safety_boundaries_declared, gates_registered, capability_handoff.
