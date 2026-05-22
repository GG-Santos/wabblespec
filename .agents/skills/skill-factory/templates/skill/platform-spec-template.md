---
name: {{ platform_id }}-spec
description: Spec template for {{ platform_name }} build target. Adjusts verification gates, security requirements, and acceptance criteria for {{ platform_name }}-specific concerns.
target: {{ platform_id }}
---

# {{ platform_name }} Spec Template

> Build target: {{ platform_id }}
> Applies when Recipe detects target = {{ platform_id }}

## Target-Specific Context

{{ platform_context }}

**Key constraints for {{ platform_name }}:**
{{ platform_constraints }}

**Verification tools available on this target:**
{{ verification_tools }}

## Spec Structure

### Goal

One sentence. What this task produces, measured by observable outcome.

### Non-Goals

Explicit exclusions. What this task will not do or change.

### Assumptions

Facts taken as true. If any assumption is wrong, the spec is invalid.

### Acceptance Criteria

Each criterion is Given/When/Then format and is independently verifiable.

```
Given [precondition]
When [action]
Then [observable outcome]
```

**{{ platform_name }}-specific required criteria:**
{{ required_criteria }}

### {{ platform_name }} Verification Gates

These checks must appear in the Verifier receipt for this target:

{{ verification_gates }}

### Security Requirements

{{ security_requirements }}

### Performance Budget

{{ performance_budget }}

## Wave Breakdown Template

Decompose tasks for {{ platform_name }} targets using these natural wave boundaries:

{{ wave_boundaries }}

## Common Failure Modes on {{ platform_name }}

{{ platform_failure_modes }}

## References

Load when needed:
- `references/{{ platform_id }}-conventions.md` — coding standards, naming, patterns
- `references/{{ platform_id }}-toolchain.md` — build, test, lint, deploy commands
- `references/{{ platform_id }}-security.md` — platform-specific threat model
