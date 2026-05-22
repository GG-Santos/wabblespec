# Technical-Domain Overlay

Extends `templates/skill/base-universal.md`. Use for code, security, data,
infrastructure, and deterministic workflows.

## Domain Operating Model

Name inputs, environment, constraints, ownership boundaries, and what must stay
untouched.

## Request Triage

Check authorization, reproducibility inputs, risky side effects, missing logs,
and whether verification can run locally.

## Workflow

1. Inspect before editing.
2. Make the smallest scoped change.
3. Use structured parsers or APIs when available.
4. Run a proof check and report residual risk.

## Output Contract

Include `changed_files`, `behavior_change`, `verification`, and
`remaining_risk`.

## Examples And Edge Cases

Cover read-only analysis, code edit, failing verification, and unavailable
dependencies.

## Failure Modes

Speculative fixes, unverified claims, unrelated refactors, unsafe file writes,
and tool-specific coupling.
