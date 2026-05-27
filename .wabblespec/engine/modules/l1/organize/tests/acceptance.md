# Organize — Acceptance Criteria

## BLOCK: absent scope declaration

Given Organize is invoked without declaring what to organize,
Then Organize surfaces: "Organize requires a scope. Specify: directory path, module set, or 'project' for full project scan."
Then Organize does not scan the entire project without explicit scope declaration.
Then no receipt is written.

## Happy path: audit produces action list

Given a scope is declared and Organize has read permission,
When Organize runs,
Then all 5 audit dimensions are checked: Naming, Depth, Orphans, Duplicates, Structure.
Then each finding is classified as AUTO or CONFIRM.
Then an organize report is written to `.wabblespec/organize/report-<timestamp>.md`.
Then an organize receipt is written to `.wabblespec/state/receipts/organize-receipt-<timestamp>.json`.

## AUTO actions: taken immediately

Given findings are classified AUTO (unambiguous destination, no external references, fully reversible),
When Organize runs with write authorization,
Then all AUTO actions are taken without waiting for user input.
Then each AUTO action is recorded in the receipt.
Then `actions_taken_auto` in the receipt reflects the count of AUTO actions taken.

## CONFIRM actions: require human approval

Given a finding is classified CONFIRM (potential data loss, external references, or ambiguous destination),
When Organize runs,
Then the CONFIRM action is presented to the user as a numbered item.
Then Organize waits for explicit user approval before acting.
Then no CONFIRM action is taken without approval.
Then `actions_requiring_confirmation` in the receipt lists affected paths.

## No write authorization: audit only

Given Organize is invoked in read-only mode or without explicit write confirmation,
When Organize finds issues to repair,
Then Organize produces an audit report only.
Then all repair actions are surfaced as proposals.
Then no AUTO repairs are taken even when repair-policy.md would permit them.

## Depth violation detection

Given a directory exceeds 5 levels of nesting,
When Organize audits Depth,
Then that directory is flagged as a depth violation.
Then `depth_violations` in the receipt is incremented.

## Orphan detection

Given a file has no imports, no receipts, and no framework.yaml references,
When Organize audits Orphans,
Then the file is flagged as an orphan candidate.
Then `orphans_found` in the receipt is incremented.

## Do NOT: auto-act on ambiguous moves

Given a file could be moved to multiple plausible destinations,
Then Organize classifies the move as CONFIRM, not AUTO.
Then Organize does not guess the correct destination.

## Absent rules files: fallback

Given `rules/audit-dimensions.md` is missing,
When Organize runs,
Then Organize applies SKILL.md audit dimension defaults.
Then the receipt logs: "audit-dimensions.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Organize run,
Then the receipt contains: `files_audited`, `orphans_found`, `naming_violations`, `depth_violations`, `duplicates_found`, `actions_taken_auto`, `actions_requiring_confirmation`, `organize_report_path`.
