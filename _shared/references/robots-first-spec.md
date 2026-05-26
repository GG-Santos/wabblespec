# Robots-First Spec

Spec-as-lookup-table guide and Robot-Centric-Code principles. Specs are written for agents, not humans. Consumers: specify, executor, decompose.

## Core principle

A spec is a lookup table, not an essay. The agent reading it must be able to:
1. Find the relevant section in O(1) — scan headings, not prose
2. Extract the exact value, condition, or constraint without inference
3. Verify a behavior by checking a single section, not synthesizing across paragraphs

## Robot-Centric-Code principles

### RCC-1 — Scannable over readable
Structure before narrative. Headings, tables, and bullet lists over prose paragraphs. An agent finding the answer in the third paragraph of the third section is a spec failure.

### RCC-2 — Explicit over implicit
State every constraint explicitly. Never rely on "it's obvious that...". An agent that reads the spec must not need prior knowledge to apply it.

Example of implicit (bad): "Use the standard error format."
Example of explicit (good): `{ "error": "string", "code": "integer" }` — always this shape.

### RCC-3 — Values over descriptions
Give the exact value, not a description of it. Agents execute on values, not descriptions.

Bad: "The timeout should be reasonable."
Good: "Timeout: 5000ms. No exceptions for this endpoint."

### RCC-4 — Conditions as decision trees
If a behavior varies by condition, write it as a decision tree, not a conditional sentence.

Bad: "If the user is authenticated, return X, but if they are not, unless the endpoint is public, return Y."
Good:
```
authenticated + any endpoint → return X
unauthenticated + public endpoint → return X
unauthenticated + private endpoint → return 401
```

### RCC-5 — One fact per line
Each list item, table row, or bullet states one fact. No compound facts in a single item.

Bad: "The module validates input and logs errors and emits a receipt."
Good:
```
- Validates input
- Logs errors on validation failure
- Emits receipt on completion
```

## Spec folder structure (robot-navigable)

```
spec/
  task-card.md       — What is being built (EARS requirements, acceptance criteria)
  scope.md           — What is in scope and what is excluded
  constraints.md     — Hard limits (performance, security, compatibility)
  decisions.md       — Architectural decisions and rationale (locked)
  not-tested.md      — Known gaps in test coverage for this execution
```

Each file answers exactly one question. An agent navigates to the right file without reading all of them.

## Anti-patterns for agent-unfriendly specs

| Anti-pattern | Problem |
|---|---|
| Requirements buried in prose | Agent must parse English to extract constraints |
| Conditions embedded in footnotes | Agent misses conditions; conditions are facts |
| "See above" references | Non-local — forces re-read of prior sections |
| Ambiguous scope ("mostly", "generally") | Agent cannot produce a binary pass/fail check |
| Missing success criteria | Agent cannot determine when to stop |
