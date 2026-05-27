# Instinct — Acceptance Criteria

## Gate enforcement

Given receipt count < 100 in .wabblespec/state/receipts/,
When --activate is run,
Then exit code is 1 and output contains "GATE_NOT_MET" with current count.

Given entity-graph.json absent from .wabblespec/state/memory/,
When --activate is run,
Then exit code is 1 and output names the missing file.

Given an Executor PID lock at .wabblespec/state/memory/.executor.pid,
When --activate is run,
Then exit code is 1 and output names the active lock.

Given all gate conditions met,
When --status is run,
Then output prints "Gate: MET" without writing any files.

## Pattern detection: Type 1 (high-frequency failure)

Given a module with FAIL status in 6 of 10 receipts (60%),
When --activate runs,
Then instinct-observations.md contains a high-frequency-failure pattern for that module with confidence medium or high.

Given a module with FAIL status in 3 of 10 receipts (30%) but only 2 distinct receipt files,
When --activate runs,
Then no high-frequency-failure pattern is written (min 5 distinct receipts not met).

## Pattern detection: Type 2 (co-occurrence)

Given modules A and B with co-occurring FAIL in 3 distinct waves,
When --activate runs,
Then a co-occurrence-cluster pattern is recorded for A+B.

Given modules A and B co-failing in only 2 waves,
When --activate runs,
Then no co-occurrence-cluster pattern for A+B.

## Pattern detection: Type 3 (recurring gap)

Given gap-map.md with topic X mentioned across 3+ sessions,
When --activate runs,
Then a recurring-gap pattern is written for topic X.

## Hard boundaries

Given any --activate run,
Then instinct-observations.md is the only file written.
Then no file under modules/ is modified.
Then no file in .wabblespec/state/receipts/ is modified.
Then no file in .wabblespec/state/experiments/ is created or modified.

## Human-validated default

Given any pattern written to instinct-observations.md,
Then the entry contains "Human-validated: false".
Then no pattern entry contains "Human-validated: true" (Instinct never self-validates).

## Dry-run

Given --dry-run flag with detectable patterns,
Then pattern count is printed to stdout.
Then instinct-observations.md is not written or modified.

## Output completeness

Given --activate produces patterns,
Then each pattern entry contains: Type, Confidence, Evidence, Occurrences, Human-validated.
Then each pattern entry contains a description paragraph.
