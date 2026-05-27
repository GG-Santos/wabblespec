# Verifier — Acceptance Criteria

## BLOCK: wave not yet complete

Given the wave implementation has not completed,
When Verifier is considered,
Then Verifier does not run during wave implementation.
Then Verifier surfaces: "Verifier runs after the wave completes, not during."
Then no verification receipt is written.

## BLOCK: absent wave plan entry

Given no wave plan entry is provided to Verifier,
When Verifier is invoked,
Then Verifier surfaces: "Verifier requires a wave plan entry with declared outputs and verification_mode."
Then Verifier does not proceed.
Then no receipt is written.

## BLOCK: absent task card

Given no task card (acceptance criteria) is provided,
When Verifier is invoked,
Then Verifier surfaces: "Verifier requires the task card as spec ground truth."
Then spec compliance check cannot run.
Then no receipt is written.

## Step 1 — Spec compliance runs first, every mode

Given any verification run regardless of declared mode,
When Verifier starts,
Then spec compliance is checked before the mode-specific check runs.
Then all four spec compliance checks run: declared outputs exist, no out-of-scope artifacts, no undocumented BREAKING changes, each "Then" clause whose artifact is declared in this wave's outputs is traceable to that artifact.
Then spec compliance failure is FAIL regardless of mode-specific result.
Then Verifier does not skip spec compliance for speed.

## Spec compliance check 4: wave-scoped acceptance tracing — post-elimination behavior

Given a multi-wave task where wave 1 declares outputs A and B, and wave 2 declares outputs C and D,
And the task card has Then clauses for all four artifacts,
When Verifier runs on wave 1,
Then check 4 verifies traceability only for clauses targeting artifacts A and B.
Then clauses targeting artifacts C and D are deferred, not failed.
Then `deferred_then_clauses` in the verification receipt lists the deferred clause IDs.
Then no `spec_compliance: "FAIL"` is issued for deferred clauses.

## Spec compliance check 4: no deferred clauses on single-wave task

Given a single-wave task where all Then clause artifacts are declared in the wave's outputs,
When Verifier runs check 4,
Then all Then clauses are verified — none are deferred.
Then `deferred_then_clauses` is an empty array `[]` in the receipt.
Then check 4 behavior is identical to pre-change behavior for single-wave tasks.

## Spec compliance: declared outputs missing

Given a wave plan declares outputs but one or more artifacts do not exist at their declared paths,
When spec compliance runs,
Then `spec_compliance: "FAIL"` is recorded.
Then the FAIL is reported before the mode check runs.

## Spec compliance: out-of-scope artifact produced

Given a wave produced an artifact that falls under scope.md Out of Scope,
When spec compliance runs,
Then `spec_compliance: "FAIL"` is recorded.
Then the out-of-scope artifact is identified in the failure report.

## Mode: Test

Given verification_mode is Test,
When Verifier runs the mode check,
Then the declared test script or assertion suite is executed.
Then PASS requires all assertions green.
Then FAIL reports which assertion failed and the exact output.

## Mode: Observation

Given verification_mode is Observation,
When Verifier runs the mode check,
Then each declared artifact is checked for existence and expected state.
Then PASS requires all conditions met.
Then FAIL reports which artifact is missing or in wrong state.

## Mode: Audit

Given verification_mode is Audit,
When Verifier runs the mode check,
Then each output artifact is systematically compared against the task card acceptance criteria.
Then FAIL lists each violation with the criterion it violates.

## Mode: Review

Given verification_mode is Review,
When Verifier runs the mode check,
Then Verifier routes to Reviewer module.
Then PASS requires Reviewer to return ACCEPT verdict.
Then FAIL uses Reviewer's revision guidance.

## Mode: Measurement

Given verification_mode is Measurement,
When Verifier runs the mode check,
Then the declared metric is read from the artifact or test output.
Then the metric is compared to the threshold declared in the wave plan.
Then PASS requires the threshold is met or exceeded.

## Mode: Attestation

Given verification_mode is Attestation,
When Verifier runs the mode check,
Then execution pauses and the wave output is surfaced to the user.
Then Verifier awaits explicit human confirmation.
Then there is no automated path to PASS for Attestation mode.

## Mode: Demonstration

Given verification_mode is Demonstration,
When Verifier runs the mode check,
Then the declared behavior is run against real conditions (not mocks).
Then PASS requires the declared behavior to be confirmed.
Then FAIL describes what happened instead of the expected behavior.

## Step 1b — Content preservation check: FAIL on structural loss

Given a wave transforms existing document content (polish, compress, translate, rewrite),
And the task card deliverable type is document, reference, changelog, or spec,
When Verifier runs the preservation check,
Then `python .wabblespec/engine/shared/scripts/markdown-extract.py --check <original> <transformed>` is executed.
Then any preservation error (dropped code block, lost URL, heading count change, lost inline code) produces verdict: FAIL.
Then the specific lost element is named in the fix_recommendation.
Then the mode-specific check does not run when preservation errors exist.

## Step 1b — Content preservation check: WARN is non-blocking

Given the preservation check produces only warnings (heading text changed, URLs added),
When Verifier processes the result,
Then the warnings are surfaced to the human as informational.
Then the wave is not blocked.
Then the warnings are recorded in the verification receipt.

## Step 1b — Preservation check skipped for non-document tasks

Given the wave produced a net-new artifact (not a transformation of existing content),
Or the task card deliverable type is not document, reference, changelog, or spec,
When Verifier runs,
Then the preservation check step is skipped entirely.
Then no `markdown-extract.py` call is made.

## REVISE loop: max 3 cycles

Given Verifier issues FAIL,
When the REVISE loop runs,
Then a specific fix recommendation is generated: which criterion failed, what the correct output should be, what needs to change and where.
Then the recommendation is returned to Executor.
Then after cycle 3: verdict is BLOCKED — a verification receipt is written and execution pauses for Attestation.
Then `revise_cycles_used` is 0 to 3.
Then cycle count resets at each new wave.

## BLOCKED conditions: immediate, no REVISE

Given a categorically unresolvable failure occurs (required hardware unavailable, irreversible action needing human judgment, dependency deadlock with no resolution),
When Verifier issues a verdict,
Then verdict is BLOCKED immediately — the REVISE loop is not entered.
Then `immediate_blocked: true` is recorded.
Then a code bug causing test failure is FAIL (not BLOCKED).

## Vague fix recommendation not permitted

Given Verifier generates a fix recommendation,
Then the recommendation must name: which criterion or artifact failed, what the correct output should be, and what needs to change and where.
Then "The output is incorrect" alone is not a valid fix recommendation.

## Evidence capture rule (I10 anti-theater)

Given a check is marked as passed in the receipt,
When Verifier writes `checks_run`,
Then every check must have a corresponding evidence record: a file path to captured output, a drawer ID, or an exact quoted excerpt (max 10 lines).
Then a check completed via visual inspection or manual confirmation appears in `not_tested` with the reason — not in `checks_passed`.
Then a receipt with `checks_passed` entries and `evidence: []` is PARTIAL, not PASS.
Then PARTIAL receipts set `status: "PARTIAL"` and `confidence` below 0.7.

## Receipt always written

Given any Verifier run regardless of verdict,
When verification completes,
Then a verification receipt is written to `.wabblespec/state/receipts/verification-wave-<N>-<timestamp>.json`.
Then this is true for PASS, FAIL, and BLOCKED verdicts.

## Do NOT

Given any Verifier run,
Then Verifier does not fix problems — it finds them and gives guidance for fixing.
Then Verifier does not skip spec compliance before the mode check.
Then Verifier does not declare BLOCKED for a failure that a code fix can resolve.

## Receipt fields

Given any Verifier run,
Then the receipt contains: `wave`, `verification_mode`, `verdict`, `spec_compliance`, `revise_cycles_used`, `immediate_blocked`, `attestation_required`, `attestation_received`, `fix_recommendation` (required when verdict is FAIL).

## Pre-archive sweep: invoked by Archive before delivery receipt

Given all waves are complete and Archive is about to write the delivery receipt,
When Archive invokes Verifier in pre-archive mode,
Then Verifier runs the three-dimension sweep: completeness, correctness, coherence.
Then findings are recorded in the Archive receipt under `pre_archive_sweep`.

## Pre-archive sweep: non-blocking — does not increment REVISE counter

Given the pre-archive sweep finds issues in any dimension,
When Verifier records the findings,
Then the REVISE counter is not incremented.
Then no FAIL verdict is issued for the pre-archive sweep.
Then findings appear as WARN in `pre_archive_sweep`.

## Pre-archive sweep: Archive proceeds regardless of findings

Given the pre-archive sweep produces WARN findings,
When Archive proceeds,
Then Archive writes the delivery receipt with `pre_archive_sweep` populated.
Then Archive does not pause or escalate due to sweep findings alone.

## Pre-archive sweep: clean sweep produces empty findings list

Given the pre-archive sweep finds no issues across all three dimensions,
When Verifier writes the sweep result,
Then all three dimensions are `"PASS"`.
Then `findings` is an empty list `[]`.
