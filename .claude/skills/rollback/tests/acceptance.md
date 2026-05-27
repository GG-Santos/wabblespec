# Rollback — Acceptance Criteria

## BLOCK: absent rollback target declaration

Given Rollback is invoked without a declared target type or source path,
Then Rollback surfaces: "Rollback requires a declared target. Specify: wave checkpoint, deploy snapshot, Forge pre-promotion, or worktree isolation."
Then Rollback does not attempt any restoration.
Then no receipt is written.

## BLOCK: Attestation absent

Given a valid rollback target is declared,
When Rollback is invoked,
Then Rollback does not execute any restoration without first receiving Attestation.
Then Rollback states what will be restored and what will be lost since the checkpoint.
Then only after human confirmation does restoration proceed.

## Wave checkpoint rollback

Given a wave checkpoint at `.wabblespec/state/checkpoints/<wave-id>/` is the declared target,
When Rollback executes with Attestation received,
Then Rollback restores the project to the state snapshotted before that wave.
Then hash verification is performed on all restored files against the checkpoint manifest.
Then the rollback receipt records: target type, timestamp, files restored, hash verification result.

## Deploy snapshot rollback

Given the Deploy receipt `rollback_to` field is the declared target,
When Rollback executes with Attestation received,
Then Rollback restores to the prior deployment state using the Deploy receipt source.
Then hash verification is performed on restored files.
Then the rollback receipt is written.

## Forge pre-promotion rollback

Given a Forge pre-promotion snapshot at `.wabblespec/state/experiments/rollback-<timestamp>/` is the declared target,
When Rollback executes with Attestation received,
Then Rollback restores framework files to the pre-promotion state.
Then hash verification is performed.
Then the rollback receipt is written.

## Worktree isolation rollback

Given an isolated git worktree branch at `.worktrees/<wave-id>/` is the declared target,
When Rollback handles this type,
Then no file restoration is required — the work was never merged to main.
Then Rollback discards the worktree branch.
Then if git worktree is unavailable, the fallback is a Type 1 wave checkpoint.

## Hash verification required

Given any restoration completes,
When Rollback performs post-restoration verification,
Then hash verification is run against the checkpoint manifest for all restored files.
Then the receipt records the hash verification result.
Then Rollback does not mark restoration complete without a passing hash check.

## Release rollback: commands provided, not executed

Given a git tag revert is needed as part of release rollback,
When Rollback handles the release type,
Then Rollback provides the exact commands (`git tag -d <version>`, `git push origin :refs/tags/<version>`) to the human.
Then Rollback does not execute these commands itself.
Then the human performs the git operations manually.

## Do NOT

Given any Rollback run,
Then Rollback does not execute any restoration without Attestation.
Then Rollback does not skip hash verification after restoration.
Then Rollback does not execute git tag operations for release rollback — it provides commands only.
Then Rollback does not decide to restore — Executor or Deploy detects the rollback condition and triggers.

## Receipt fields

Given any successful Rollback run,
Then the receipt is written to `.wabblespec/state/receipts/`.
Then the receipt contains: rollback target type, target path, timestamp, files restored, hash verification result.
