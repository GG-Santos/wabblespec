# Retro — Acceptance Criteria

## L8 corpus gate

Given receipt count in .wabblespec/receipts/ is fewer than 100 PASS,
When Retro is invoked,
Then Retro exits and outputs "GATE_NOT_MET" with the current count.
Then no retro file is written.

## Activation gate

Given Executor PID lock is active at .wabblespec/memory/.executor.pid,
When Retro is invoked,
Then Retro exits and names the active lock without writing any file.

Given no complete receipt chain (no delivery receipt) exists in .wabblespec/receipts/,
When Retro is invoked,
Then Retro exits and reports "no complete chain found."
Then no retro file is written.

## Period declaration

Given Retro is invoked with no --period flag,
Then the retrospective covers the last 10 complete receipt chains by default.
Then the retro document states "Period: last 10 runs" or equivalent.

Given Retro is invoked with --period 5,
Then the retrospective covers the last 5 complete receipt chains only.
Then chains outside that window are not mentioned.

Given Retro is invoked with --since 2026-05-01,
Then only chains with archived_at >= 2026-05-01 are included.

## Required document structure

Given a complete Recipe → Archive receipt chain,
When Retro runs,
Then retro-{timestamp}.md is written to .wabblespec/memory/retro/.
Then the file contains all required sections: Date, Period covered, Modules in chain, Receipt chain health status, Wave Summary table, Receipt Chain section, Patterns Observed section, Unresolved Gaps section, Not Tested section.
Then Date matches the run timestamp to within 1 minute.
Then "Modules in chain" count matches the number of distinct module IDs in the receipt chain.

## Chain health classification

Given all expected module receipts are present and linked in sequence,
Then chain_health in the retro document is "INTACT".
Then missing_receipts section is absent or empty.

Given one or more expected module receipts are absent from the chain,
Then chain_health is "BROKEN".
Then missing_receipts lists each absent module ID by name.
Then no assumption is made about what the absent receipt would have contained.

Given a receipt exists but its status is FAIL,
Then chain_health is "BROKEN".
Then the failing module is listed in the retro's broken chain section.

## Observation-only language constraint

Given any retro document written,
Then the document contains no prescriptive language: "should", "must", "recommend", "fix", "improve", "need to".
Then the document uses observational language: "observed", "occurred", "was present", "was absent", "was not found".
Then the Patterns Observed section states what happened, not what should happen next.

## Wave summary accuracy

Given a receipt chain with 3 waves where wave 2 had 2 FAIL modules,
When Retro writes the Wave Summary table,
Then wave 2 row shows status "PARTIAL" or "FAIL" (not "PASS").
Then the table includes one row per wave in the chain.

## Memory enrichment

Given .wabblespec/memory/wings/ contains drawers relevant to modules in the chain,
When Retro runs,
Then the Patterns Observed section references at least one drawer by topic if a relevant match exists.
Then the drawer reference includes the drawer's staleness_state.

Given memory store is empty,
When Retro runs,
Then the retro document notes "Memory store empty — no drawer context available."
Then the document is still written successfully.

## Recurring pattern detection

Given a module has appeared with FAIL status in 3 or more separate retro documents,
When Retro runs for the current chain and that module fails again,
Then the Patterns Observed section flags "recurring failure" for that module.
Then the flag includes the occurrence count across known retro documents.

Given a module has failed in only 2 prior retro documents,
When Retro runs and that module fails again,
Then no "recurring failure" flag is written (minimum 3 occurrences).

## Unresolved gaps

Given the prior retro's Unresolved Gaps section named gap X,
When the current chain does not close gap X,
Then the current retro's Unresolved Gaps section includes gap X again.
Then the entry notes it was first observed in the prior retro (carry-forward).

## Not Tested section

Given any retro document,
Then the Not Tested section is present.
Then it explicitly lists items in the chain that could not be verified from receipts alone (e.g., actual execution correctness, human review steps).
Then the section is not empty — at minimum it names "actual behavioral correctness of wave outputs."

## Boundary enforcement

Given any Retro invocation,
Then no receipt in .wabblespec/receipts/ is created or modified.
Then no file in modules/ is created or modified.
Then no Synth candidate is written by Retro.
Then no feedback item is written by Retro.
Then only .wabblespec/memory/retro/ receives new files.
Then tracker.json is not modified.

## Idempotency

Given Retro is invoked twice for the same period with the same input receipts,
Then two retro files are written (one per invocation) with different timestamps.
Then the content of both files is identical except for the timestamp fields.
Then the second invocation does not modify the first retro file.

## Dry-run

Given --dry-run flag,
Then Retro prints the chain health, module count, and pattern count to stdout.
Then no retro file is written to .wabblespec/memory/retro/.
