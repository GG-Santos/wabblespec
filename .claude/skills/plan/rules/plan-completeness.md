# Plan Completeness

A complete plan contains all of the following. Incomplete plans must not receive GO verdicts.

## Required components

**1. Chosen approach (one sentence)**
States what will be built and how. Must be traceable to Propose's recommendation.

**2. Expert perspectives applied (minimum 2)**
Documents which expert lenses were applied and what each found. Even a "no concerns" finding is worth recording — it shows the lens was applied, not skipped.

**3. Open risks (zero or more)**
Every concern raised by any expert perspective that is not resolved by the plan. Risk entries must include: name, consequence if materializes, status (BLOCKING or ACCEPTABLE).

A plan with zero open risks and zero expert perspectives is not complete — it has not been reviewed.

**4. Go/no-go verdict**
One of GO / NO_GO / CONDITIONAL. Required. No plan exits without a verdict.

**5. Conditions (if CONDITIONAL)**
Explicit list of what must be true before execution starts. Each condition must be verifiable.

## Risk status definitions

**BLOCKING:** This risk must be resolved before execution starts. A GO verdict with any BLOCKING risk is invalid (PLN-3 invariant violation).

**ACCEPTABLE:** Risk is acknowledged but does not prevent execution. Document mitigation if one exists.

## What a plan does NOT need to contain

- Wave structure — Decompose owns that
- Implementation steps — Executor owns that
- Test strategy — Verifier owns that
- File-level changes — Executor owns that

A plan that contains wave structure or implementation steps has overreached. Remove them and leave them for the module that owns them.
