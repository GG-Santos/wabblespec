# Gateway: AI

LLM safety and evaluation gate. Activates before any execution that produces AI/LLM output, integrates an LLM, or deploys an AI-backed feature.

**Skill:** `modules/l4/ai/SKILL.md`
**Rules files:** `modules/l4/ai/`

## What this gateway checks

- Prompt injection surface: are user inputs sanitized before reaching the LLM?
- Output validation: is LLM output validated before being used in downstream operations?
- Hallucination handling: is there a declared strategy for handling incorrect LLM output?
- Tool-use safety: if the LLM has tool access, are tool permissions minimized?
- Eval harness: is there a declared evaluation strategy (not necessarily running — declared)?
- Bias and fairness: does the task involve decisions affecting people? Is bias mitigation declared?
- Model dependency: is the implementation model-agnostic or does it hard-code a specific model?

## When this gateway activates

- Any target tagged `ai`, `llm`, `ml`, `agent`, `embedding`, `rag`
- Any platform-ai-agent target
- Any wave that adds an LLM API call to product space
- Explicit invocation: `/gateway-ai`

## Sequencing

Runs third in the gateway chain (after security, after engineering). Parallel with aesthetic/design/experience.

## Verdict rules

**BLOCK** on:
- User input passed directly to LLM prompt without sanitization
- LLM output used in a shell command, SQL query, or file write without validation
- No hallucination handling declared for a factual/retrieval task

**FLAG** on:
- Eval harness not declared
- Hard-coded model name in implementation (should use capability descriptor via model-router)
- No bias mitigation declared for a decision-affecting task
- Output token limit not declared

**PASS** when no BLOCK conditions are present.
