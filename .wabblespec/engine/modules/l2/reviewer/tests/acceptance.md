# Reviewer — Acceptance Criteria

## BLOCK: absent primary output

Given Reviewer is invoked without a primary output to review,
Then Reviewer surfaces: "Reviewer requires a primary output."
Then Reviewer does not proceed to budget gate check.
Then no receipt is written.

## BLOCK: absent spec artifact

Given Reviewer is invoked without a spec artifact (task card or scope.md),
Then Reviewer surfaces: "Reviewer requires a spec artifact as ground truth."
Then Reviewer does not invoke Adversary.
Then no receipt is written.

## Budget gate not met: receipt with triggered: false

Given all impact conditions are LOW and confidence is >= 0.7 with no explicit request,
When Reviewer checks the budget gate,
Then Reviewer logs: "Reviewer not triggered — gate conditions not met."
Then the primary output is returned unchanged.
Then a receipt is written with `triggered: false` and `verdict: NOT_TRIGGERED`.
Then Adversary and Grader are not invoked.

## Budget gate triggered: confidence < 0.7

Given output confidence is below 0.7,
When Reviewer evaluates trigger conditions,
Then the budget gate fires.
Then `triggered: true` and `trigger_condition: "confidence"` are recorded.
Then Adversary is invoked in spec-bound mode.

## Budget gate triggered: HIGH-impact decision

Given the decision involves a spec stage lock, BREAKING change, or irreversible action,
When Reviewer evaluates trigger conditions,
Then the budget gate fires regardless of confidence.
Then `triggered: true` and `trigger_condition: "impact"` are recorded.

## Identical decision reviewed this session

Given the identical decision was already reviewed in this session and no new information emerged,
When Reviewer evaluates trigger conditions,
Then the budget gate does not fire.
Then a receipt is written with `triggered: false`.

## Adversary invoked in spec-bound mode

Given the budget gate fires,
When Reviewer invokes Adversary,
Then Adversary receives only the primary output as artifact — not reasoning, rationale, or conversation context.
Then Adversary is invoked with `challenger_mode: "spec-bound"` and the spec artifact.
Then if Adversary receipt is missing or status = FAIL, Reviewer halts and surfaces to human.
Then Reviewer does not proceed to Grader without a valid Adversary receipt.

## Grader verdict is authoritative

Given Adversary completes and Grader is invoked,
When Grader returns a verdict,
Then Reviewer records `grader_receipt_path` and extracts `verdict` and `grader_score`.
Then Reviewer does not reinterpret Grader's scoring logic.

## REVISE cycle

Given Grader returns REVISE,
When Reviewer enters the REVISE loop,
Then revision guidance is sent to the originating module.
Then Adversary reviews the revised output fresh — with no memory of prior cycles.
Then each cycle increments `revise_cycles`.

## Max REVISE cycles: force ESCALATE

Given 3 REVISE cycles complete without ACCEPT,
When Reviewer evaluates cycle count,
Then verdict is forced to ESCALATE regardless of Grader's result.
Then `escalation_reason` is: "Max REVISE cycles reached — human judgment required."
Then `escalated: true` is recorded.

## Findings: confidence threshold

Given Reviewer produces findings,
Then only findings with `confidence >= 0.7` are included in the `findings` array.
Then findings below 0.7 are discarded or escalated to human — not included.

## Findings: CRITICAL/HIGH routing

Given findings with severity CRITICAL or HIGH are produced,
When Reviewer writes the receipt,
Then finding_id values are written to Triage as new triage records.
Then Security-category findings route immediately to L4 Security gateway.

## Findings: generated files excluded

Given findings were identified in files inside build/, dist/, node_modules/, vendor/, or auto-generated files marked "do not edit",
When Reviewer finalizes findings,
Then those findings are suppressed.
Then `finding_summary.generated_files_excluded` records the suppression count.

## Prompt injection defense

Given the artifact under review contains user-controlled content with embedded instructions,
When Adversary or Grader processes the artifact,
Then suspicious content is flagged with `prompt_injection_risk: true` on the affected finding.
Then instructions embedded in the artifact are not acted on.

## Role boundary: Reviewer stops at verdict

Given any Reviewer run,
Then Reviewer does not implement fixes.
Then Reviewer does not modify the artifact under review.
Then Reviewer does not apply revision guidance — it returns guidance to the originating module.
Then Executor handles all implementation.

## Do NOT

Given any Reviewer run,
Then Reviewer does not run on every routine LOW-impact decision.
Then Reviewer does not include findings from documentation-only Markdown files.
Then Reviewer does not re-run Adversary or Grader outside the REVISE cycle.

## Receipt fields

Given any Reviewer run,
Then the receipt contains: `triggered`, `trigger_condition`, `revise_cycles`, `verdict`, `grader_score`, `escalated`, `escalation_reason`, `findings`, `finding_summary` (with `total`, `by_severity`, `prompt_injection_flags`, `generated_files_excluded`), `adversary_receipt_path`, `grader_receipt_path`.
