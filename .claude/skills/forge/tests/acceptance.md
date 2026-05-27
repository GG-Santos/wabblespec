# Forge — Acceptance Criteria

## Gate enforcement (all must pass before any file write)

Given blueprint status is approved (not benchmark-passed),
When Forge is invoked,
Then Forge exits FORGE_BLOCKED and names the unmet gate.

Given tracker.json has a FAIL entry for the blueprint ID with requeue_decision: null,
When Forge is invoked,
Then Forge exits FORGE_BLOCKED and surfaces the open contradiction.

Given promoted module is L8 and no Attestation receipt exists,
When Forge is invoked,
Then Forge exits FORGE_BLOCKED and names the missing Attestation.

## Promotion workflow

Given all gates pass,
When Forge executes,
Then experiment files are written to modules/{layer}/{module}/.
Then framework.yaml last_validated is updated for the promoted module.
Then experiment is moved from augments/ to archive/ before receipt is written.
Then provenance.json is updated with the promotion record.

## Downstream propagation

Given promoted module has downstream dependents in framework.yaml depends_on graph,
When Forge completes,
Then each dependent module has a NEEDS_REVERIFICATION note in its receipt.
Then downstream_reverification_notified in Forge receipt lists all affected IDs.

## Self-modification rule

Given promoted module path starts with modules/l8/,
Then attestation_verified in receipt is true.
Then an Attestation receipt for this blueprint ID exists in .wabblespec/receipts/.

## Boundary enforcement

Given any Forge invocation,
Then no file under  is created or modified.
Then tracker.json is appended, not overwritten.
Then experiment_archived is true in receipt before promotion is recorded.

## Atomic receipt requirement

Given promotion files are written but archive step fails,
Then Forge receipt is not written.
Then the failed state is surfaced to human for manual resolution.
