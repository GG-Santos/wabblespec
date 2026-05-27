# Critical Dimensions

Three dimensions are critical. All three must be present or derived before Enhance passes control to ScopeFrame.

## The three critical dimensions

**Task** — without a clear action, there is nothing to spec.
**Target** — without a named artifact, scope cannot be bounded.
**Format** — without knowing what form the output takes, acceptance criteria cannot be written.

Together: Task + Target + Format define a minimal specifiable unit. "Fix (Task) the login handler (Target) by adding an error message (Format)."

## Resolution requirement

Critical dimensions must be resolved before proceeding. Resolved = Present or Derived. Absent = unresolved.

If any critical dimension is Absent after user questions: do not proceed to ScopeFrame. Surface which dimension is still missing and ask for it specifically.

## Priority in question budget

When deciding which questions to ask (max 3): critical dimensions get the first question slots. If all three critical dimensions are absent, ask all three questions in one pass. Do not spend question budget on non-critical dimensions when critical ones are unresolved.

## Derived vs Absent

Derived is acceptable — it means Enhance inferred the dimension from available signals (recipe.json, other dimensions, user message content). Derived dimensions do not require questions.

Do not mark a dimension as Derived without a stated basis. "I inferred the Target is the auth module because the user said 'login is broken'" is valid. "I assumed Target is the auth module" is not.

## Critical dimension failure

If critical_dimensions_resolved = false in the receipt: ScopeFrame must not run. The enhance receipt with `critical_dimensions_resolved: false` is a blocker. Surface it to the user before proceeding.
