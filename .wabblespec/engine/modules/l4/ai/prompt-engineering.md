# Prompt Engineering Standards

## System Prompt

- Declarative — describes behavior and constraints, does not narrate a persona
- Versioned — committed to source control alongside the code that uses it
- Tested — eval suite covers system prompt behavior, not just user inputs
- Not ad hoc — no system prompts written inline at runtime without a declared template

## Few-Shot Examples

- Curated: examples selected for representativeness, not convenience
- Updated: failure cases observed in production added to few-shot set on regular cadence
- Separate: stored separately from system prompt (not inline)
- Annotated: each example includes a rationale note for why it was included

## Temperature Declaration

| Task type | Temperature guidance |
|---|---|
| Deterministic (classification, structured extraction) | 0 or near-0 |
| Balanced (summarization, Q&A) | 0.3–0.5 |
| Creative (generation, ideation) | 0.7–1.0 |

Temperature declared per task type in spec. Undeclared = 0 (deterministic) as safe default.

## Token Budget

Declared in spec for each LLM call:

```markdown
## Token Budget — <call name>

**system_prompt:** N tokens (measured)
**few_shot_examples:** N tokens (measured)
**user_input_max:** N tokens
**output_max:** N tokens
**total_budget:** N tokens
**model_context_window:** N tokens
**headroom:** N tokens
```

Total budget must not exceed model context window minus declared headroom. No implicit assumptions about token counts.

## Audit Gates

- [ ] System prompt committed to source control
- [ ] Temperature declared per call type (not defaulted silently)
- [ ] Token budget declared and within context window minus headroom
- [ ] Few-shot examples stored separately from system prompt
- [ ] No inline ad hoc system prompts in runtime code
