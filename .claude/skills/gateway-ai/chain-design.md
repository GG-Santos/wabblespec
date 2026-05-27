# Chain Design Standards

## Step Contracts

Each step in a chain declares:
- **Input schema:** what the step expects (JSON Schema or equivalent)
- **Output schema:** what the step produces
- **Validation:** output validated against schema before passed to next step

No implicit data passing between steps. No step assumes the previous step's output format without a declared contract.

## Branching

Conditional routing declared explicitly. No implicit branching based on model output parsing. Branch conditions declared as deterministic logic (regex, schema check, confidence threshold) — not "the model decides."

## Error Recovery

Fallback declared per step — not per chain. Chain-level error handling cannot mask step-level failures.

Per-step fallback options:
- Retry with modified input
- Return structured error to caller
- Route to human review

## Context Passing

Explicit — no global state between chain steps. Each step receives only what it needs. Shared context passed as declared parameter, not through a shared mutable object.

## Audit Gates

- [ ] Every chain step has declared input schema and output schema
- [ ] Output validated against schema before passing to next step
- [ ] Branch conditions are deterministic (not model-resolved)
- [ ] Per-step fallback declared (not chain-level blanket handler)
- [ ] No shared mutable context object between steps
