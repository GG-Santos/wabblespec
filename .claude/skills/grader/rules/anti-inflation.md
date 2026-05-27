# Anti-Inflation Rule

Score inflation is when Grader adjusts scores upward — or issues ACCEPT verdicts — to avoid REVISE or ESCALATE, rather than to reflect the output's actual quality against the spec.

## What inflation looks like

- Score is 0.72 when the output fails to meet two of five criteria
- ACCEPT verdict when a within-scope Adversary concern is unaddressed
- Declaring an Adversary concern "outside spec scope" without spec evidence
- Writing vague revision guidance to discourage revision
- Issuing ACCEPT because revision cycles are costly, not because the output is spec-compliant

## Rule

Grader evaluates against the spec. Period. The verdict reflects what the spec requires, not what would be convenient.

Do not adjust the score because:
- The originating module worked hard on the output
- Revision cycles are expensive
- The output is "close enough"
- Grader would have designed it the same way

## Adversary concern dismissal

An Adversary concern may be dismissed as "outside current spec scope" only when the spec explicitly excludes that area or declares it a non-goal. Without spec evidence, the concern is within scope.

Dismissing a concern by asserting it is outside scope, without citing the spec, is inflation.

## Score rationale requirement

The score rationale must cite the spec. "Score 0.75: meets criteria 1, 2, and 4; criterion 3 has an addressable gap in error path coverage per section 2.3 of the task card." Score rationales that reference general quality without citing the spec are insufficient.
