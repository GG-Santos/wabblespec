# Grader Verdict Matrix

## Primary decision table

| Score | Adversary concerns | Verdict |
|---|---|---|
| ≥ 0.7 | Addressed or outside current spec scope | ACCEPT |
| ≥ 0.7 | Within-scope concern that output should address | REVISE |
| 0.5–0.69 | Any | REVISE |
| < 0.5 | Any | ESCALATE |
| Any | Requires human judgment or authority beyond current session | ESCALATE |

## Verdict definitions

**ACCEPT**

Score ≥ 0.7 AND all within-scope Adversary concerns are either:
- Addressed in the primary output, OR
- Outside the current spec scope (acceptable given declared constraints)

Output meets spec well enough. Do not ACCEPT an output that has real within-scope Adversary concerns unaddressed, regardless of score.

**REVISE**

Score 0.5–0.69, OR score ≥ 0.7 but Adversary raised a real within-scope concern the output should address.

Output has addressable gaps. Revision guidance is required — see rules/revision-guidance.md. The originating module must be able to act on the guidance without asking for clarification. "Improve quality" is not guidance.

**ESCALATE**

Score < 0.5, OR Adversary raised a concern that:
- Requires human judgment to resolve
- Requires authority beyond the current session
- Cannot be resolved by the originating module alone

ESCALATE is not a stronger REVISE. Use it when human judgment is genuinely required, not when the output is hard to evaluate.

## Max REVISE cycles

After 3 REVISE cycles (managed by the caller — Reviewer or direct invoker), force ESCALATE regardless of current verdict. Grader does not track cycle count — the caller provides this context. If caller signals max cycles reached, Grader issues ESCALATE with reason: "Max REVISE cycles reached — human judgment required."

## Adversary concern handling

Every Adversary point must be assessed. Do not ignore points because they are inconvenient. Record total points assessed in `adversary_concerns_assessed` and points within current spec scope in `adversary_concerns_within_scope`.

A point is "outside current spec scope" only if the spec explicitly excludes that area or declares it a non-goal. Declaring something outside scope without spec evidence is score inflation (see rules/anti-inflation.md).
