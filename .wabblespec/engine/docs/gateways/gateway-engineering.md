# Gateway: Engineering

Build quality and standards gate. Activates before any engineering execution at Medium/High complexity. Checks that the wave plan meets engineering standards before Executor runs.

**Skill:** `modules/l4/engineering/SKILL.md`
**Rules files:** `modules/l4/engineering/`

## What this gateway checks

- Architecture decisions align with declared constraints from ScopeFrame
- Wave plan does not introduce patterns flagged as anti-patterns for the active platform
- Test strategy is declared (not necessarily complete, but present)
- Breaking changes are identified and flagged for consumer notification
- Dependency additions are justified and within declared version constraints
- No circular dependencies introduced by the proposed changes
- API contract changes (if any) are versioned correctly

## When this gateway activates

- Any engineering execution at Medium or High complexity
- Any wave plan that modifies product space at more than 3 files
- Any wave plan that adds or removes dependencies
- Explicit invocation: `/gateway-engineering`

## Sequencing

Runs second in the gateway chain (after security). A BLOCK here stops Executor but does not prevent remaining domain gateways (aesthetic, design, experience) from running their checks — though in practice, an engineering BLOCK typically means the wave plan needs revision before any gateway is meaningful.

## Verdict rules

**BLOCK** on:
- Wave plan contradicts a declared ScopeFrame constraint
- Breaking API change with no versioning or consumer notification declared
- Test strategy entirely absent for a non-trivial execution
- Circular dependency introduced

**FLAG** on:
- Test coverage declared but not tied to a specific verification checkpoint
- Dependency version range too broad (e.g., `*` or `>=1.0.0`)
- Architecture decision not documented when a significant pattern is introduced

**PASS** when no BLOCK conditions are present.
