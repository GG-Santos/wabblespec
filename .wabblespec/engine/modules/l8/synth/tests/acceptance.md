# Synth — Acceptance Criteria

## Activation gate

Given instinct-observations.md with fewer than 3 Human-validated: true patterns,
When Synth is invoked,
Then Synth stops and surfaces the gap count to the human without writing any file.

Given a pattern with Human-validated: false,
When Synth is invoked on that pattern,
Then Synth refuses, names the unvalidated pattern, and writes nothing.

Given a pattern with Confidence: low,
When Synth is invoked on that pattern,
Then Synth refuses and surfaces the confidence level.

## Candidate production

Given a validated pattern with real evidence receipt paths,
When Synth produces a candidate.json,
Then all required fields are present: candidate_id, source_pattern, affected_module, behavior_change, evidence, risk, rollback_condition, created_at, status.

Given a pattern that implies two distinct behavior changes,
When Synth evaluates it,
Then Synth surfaces a decomposition note to the human instead of writing a multi-change candidate.

## behavior_change constraint

Given any candidate.json written by Synth,
Then behavior_change is a single sentence (contains one period, no semicolons joining clauses).

## rollback_condition constraint

Given any candidate.json written by Synth,
Then rollback_condition names a specific metric and threshold, not a general quality statement.

## Evidence validity

Given a candidate citing receipt paths,
When the receipt paths are checked,
Then each path exists in .wabblespec/receipts/.

## Boundary enforcement

Given any Synth invocation,
Then no file is written under modules/.
Then no existing receipt is modified.
Then no instinct-observations.md content is changed.
Then exactly one .candidate.json is written per invocation.
