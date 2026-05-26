# Grader — Acceptance Criteria

## BLOCK: absent Adversary receipt

Given no Adversary receipt is present in task context,
When Grader is invoked,
Then Grader blocks and surfaces: "Grader requires an Adversary receipt. Invoke Adversary first."
Then Grader does not accept a caller assertion that Adversary was "run informally."
Then no grader receipt is written.

## BLOCK: Adversary receipt with status FAIL

Given an Adversary receipt exists but its `status` field is FAIL,
When Grader is invoked,
Then Grader blocks and surfaces: "Adversary receipt status is FAIL — resolve Adversary failure before invoking Grader."
Then Grader does not proceed with a FAIL receipt as input.

## BLOCK: absent spec artifact

Given no spec artifact is declared,
When Grader is invoked,
Then Grader blocks and surfaces: "Grader requires a spec artifact to evaluate against."
Then Grader does not infer spec requirements from the primary output alone.

## BLOCK: absent primary output

Given no primary output artifact is referenced for evaluation,
When Grader is invoked,
Then Grader blocks and surfaces: "Grader requires a primary output to evaluate."
Then Grader does not evaluate the spec artifact itself as if it were the output.

## Happy path: ACCEPT verdict

Given a primary output, a valid Adversary receipt, and a spec artifact where the output scores >= 0.7 and Adversary concerns are addressed or out of scope,
When Grader runs,
Then verdict is ACCEPT.
Then `score` is >= 0.7.
Then `score_rationale` references the spec (not aesthetics).
Then `revision_guidance` is null.
Then `escalation_reason` is null.
Then a grader receipt is written to `.wabblespec/receipts/grader-receipt-<timestamp>.json`.

## REVISE verdict

Given the primary output scores 0.5–0.69 or has within-scope Adversary concerns the output should address,
When Grader runs,
Then verdict is REVISE.
Then `revision_guidance` is specific and actionable — the originating module can act without asking for clarification.
Then revision guidance is not vague (e.g., "the output needs improvement" is not acceptable).

## ESCALATE verdict

Given the primary output scores < 0.5 or Adversary raised a concern requiring human judgment or authority,
When Grader runs,
Then verdict is ESCALATE.
Then `escalation_reason` states what question cannot be answered by the originating module alone.
Then `revision_guidance` is null.

## Score rationale references spec

Given any Grader run,
Then `score_rationale` is one sentence and references the spec criteria.
Then the score is not adjusted upward to avoid REVISE or ESCALATE.
Then evaluating against personal preference rather than spec criteria is not permitted.

## Adversary concerns assessed

Given Adversary provided counter_analysis with multiple points,
When Grader evaluates,
Then `adversary_concerns_assessed` counts total Adversary points evaluated.
Then `adversary_concerns_within_scope` counts points applicable to the current spec.
Then out-of-scope Adversary points do not reduce the score.

## Role boundary: no implementation

Given any Grader run,
Then Grader does not implement revision guidance.
Then Grader does not produce alternative outputs.
Then Grader does not modify the artifact under review.
Then revision guidance is written as instruction to the originating module only.

## Absent score-thresholds.md: fallback

Given `rules/score-thresholds.md` is absent,
When Grader runs,
Then Grader applies SKILL.md built-in thresholds.
Then the receipt logs: "score-thresholds.md absent — using SKILL.md built-in thresholds."
Then a numeric score is always present in the verdict.

## Receipt fields

Given any successful Grader run,
Then the receipt contains: `verdict`, `score`, `score_rationale`, `spec_artifact_path`, `adversary_receipt_path`, `revision_guidance`, `escalation_reason`, `adversary_concerns_assessed`, `adversary_concerns_within_scope`.
