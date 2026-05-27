# Sync — Acceptance Criteria

## BLOCK: absent sync target

Given Sync is invoked without declaring what to synchronize,
Then Sync surfaces: "Sync requires a declared target: two spec versions, a spec and implementation, or two module states."
Then Sync does not infer what to sync from context.
Then no receipt is written.

## BLOCK: one side of pair missing

Given `spec_a` exists but `spec_b` is absent or returns 404,
When Sync is invoked,
Then Sync blocks and surfaces: "Sync requires both targets. [B] not found at declared path."
Then Sync does not proceed with a one-sided sync.
Then no receipt is written.

## Happy path: MINOR divergence — auto merge

Given two spec artifacts derived from the same base with only additive differences (one adds criteria not in the other),
When Sync runs,
Then divergence severity is classified as MINOR.
Then `merge_strategy` is `auto`.
Then both additive change sets are merged.
Then the merged spec is written to `.wabblespec/sync/result-<timestamp>.md`.
Then `auto_merged` in the receipt is true.
Then `human_review_required` is false.

## MAJOR divergence: escalate when no priority signal

Given two spec artifacts have the same criterion defined differently (conflicting) and no declared priority signal,
When Sync runs,
Then divergence severity is classified as MAJOR.
Then `merge_strategy` is `escalated`.
Then Sync does NOT produce a partial merged spec.
Then exact conflict locations are surfaced to the user.
Then `human_review_required` in the receipt is true.
Then `conflicts_escalated` reflects the count of unresolved conflicts.

## MAJOR divergence: manual merge with priority signal

Given MAJOR divergence exists and a clear priority signal is declared,
When Sync runs,
Then `merge_strategy` is `manual`.
Then the priority is applied and the decision is documented.
Then `conflicts_resolved` in the receipt reflects the count resolved.

## Do NOT: auto-resolve MAJOR conflicts without signal

Given MAJOR conflicting declarations with no resolution rule,
When Sync encounters each conflict,
Then Sync surfaces each conflict individually for human resolution.
Then Sync does not silently prefer one side.

## Three-way diff with base

Given `spec_base` (common ancestor) is provided alongside `spec_a` and `spec_b`,
When Sync runs,
Then changes in A but not base AND changes in B but not base are both captured.
Then conflicts are identified only where the same section changed differently in A and B.

## Idempotency

Given Sync is run on two spec artifacts that are already identical (previously synced),
When Sync runs,
Then no changes are made.
Then the receipt reflects 0 conflicts and 0 merges.
Then no merged artifact overwrites an existing identical result.

## Absent rules files: fallback

Given `rules/divergence-detection.md` is missing,
When Sync runs,
Then Sync applies SKILL.md divergence detection rules.
Then the receipt logs: "divergence-detection.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Sync run,
Then the receipt contains: `specs_reconciled`, `divergence_severity`, `auto_merged`, `human_review_required`, `merge_strategy`, `conflicts_resolved`, `conflicts_escalated`, `sync_result_path`.
Then `sync_result_path` is absent or null when merge_strategy is `escalated`.
