# Grader — Cold-Start Behavior

Defines what Grader does when expected inputs (Adversary receipt, spec artifact, primary output) are absent.

## Absent: Adversary receipt

Condition: Grader invoked but no Adversary receipt present in task context.
Detection: No `adversary-receipt-<id>.json` linked in task card or passed as argument.
Action: BLOCK. Surface: "Grader requires an Adversary receipt. Invoke Adversary first — counter-analysis is required input."
Do NOT: Run evaluation without counter-analysis. Do NOT accept caller assertion that Adversary was "run informally."

## Absent: Adversary receipt with status = FAIL

Condition: Adversary receipt is present but status field is FAIL.
Detection: Receipt parsed; status != PASS.
Action: BLOCK. Surface: "Adversary receipt status is FAIL — Adversary did not complete successfully. Resolve Adversary failure before invoking Grader."
Do NOT: Treat a FAIL receipt as acceptable input. Do NOT proceed with evaluation.

## Absent: spec artifact

Condition: Grader invoked but no spec artifact declared in task card.
Detection: No `spec_artifact` reference in task card or invocation.
Action: BLOCK. Surface: "Grader requires a spec artifact to evaluate against. Declare the spec artifact (Propose receipt, PRD, or contract file)."
Do NOT: Infer spec requirements from primary output alone.

## Absent: primary output

Condition: No primary output artifact referenced for evaluation.
Detection: No `primary_output` field in task card or invocation argument.
Action: BLOCK. Surface: "Grader requires a primary output to evaluate. Specify the artifact under review."
Do NOT: Evaluate the task card or spec artifact itself as if it were the output.

## Absent: score thresholds reference

Condition: `modules/l2/grader/rules/score-thresholds.md` absent.
Detection: File read returns 404.
Action: Apply built-in defaults from SKILL.md knowledge:
- 0.9 - 1.0: ACCEPT — meets all criteria; Adversary concerns minor or addressed
- 0.7 - 0.89: ACCEPT with notes — meets most criteria; one or two addressable gaps noted
- 0.5 - 0.69: REVISE — meaningful gaps or unresolved Adversary concerns
- < 0.5: ESCALATE — fundamental issues; human review required before re-evaluation
Log: "score-thresholds.md absent — using SKILL.md built-in thresholds."
Do NOT: Omit a numeric score from the verdict.

## Absent: prior Grader receipt for this scope

Condition: No prior `grader-receipt-<id>.json` for this output artifact.
Action: Treat as first evaluation. No prior verdict to compare against. Issue verdict without delta commentary.

## Absent: grader receipt output directory

Condition: `.wabblespec/grader/` directory does not exist.
Action: Create directory before writing receipt. This is normal on first run.

## Default state on cold start

| Field | Default |
|---|---|
| `adversary_receipt_required` | true — hard block if absent or FAIL |
| `spec_artifact_required` | true — hard block if absent |
| `score_range` | 0.0 - 1.0 |
| `accept_threshold` | 0.90 (ACCEPT), 0.70 (ACCEPT with notes) |
| `revise_threshold` | 0.50 - 0.69 |
| `escalate_threshold` | < 0.50 |
| `verdict_options` | ACCEPT, ACCEPT_WITH_NOTES, REVISE, ESCALATE |
| `fix_mode` | false — Grader issues verdicts; does not rewrite output |
| `receipt_path` | `.wabblespec/grader/grader-receipt-<timestamp>.json` |
