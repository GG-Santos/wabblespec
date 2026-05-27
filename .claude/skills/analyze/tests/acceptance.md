# Analyze — Acceptance Criteria

## BLOCK: absent problem statement

Given Analyze is invoked without a problem statement,
Then Analyze surfaces: "Analyze requires a problem statement. Describe the symptom, failure, or unexpected behavior."
Then no RCA report is written.
Then no analyze receipt is written.

## Happy path: structured RCA with evidence

Given a problem statement is provided with at least one evidence source (logs, test output, or receipts),
When Analyze runs,
Then a method is selected (5-whys, fishbone, fault-tree, or timeline) and the selection rationale is recorded in the receipt.
Then the RCA report is written to `.wabblespec/analysis/rca-<timestamp>.md`.
Then the analyze receipt is written to `.wabblespec/receipts/analyze-receipt-<timestamp>.json`.
Then `root_cause_confidence` is >= 0.4 when evidence supports a probable root cause.
Then `root_cause_identified` is true when confidence >= 0.4.

## Confidence levels reflect evidence

Given a problem statement is provided with no evidence sources,
When Analyze runs,
Then Analyze surfaces a warning that confidence will be speculative without evidence.
Then Analyze proceeds (does not block).
Then `root_cause_confidence` in the receipt is < 0.4 (speculative).
Then the RCA report is written regardless.

Given a problem statement with verifiable, reproducible evidence,
When Analyze runs,
Then `root_cause_confidence` is >= 0.7 (confident).

## Nexus unavailable: proceed without enrichment

Given Nexus is unavailable or entity-graph.json is missing,
When Analyze runs,
Then Analyze proceeds without Nexus enrichment.
Then `nexus_queried` in the receipt is false.
Then the RCA report is written successfully.
Then no error is raised for Nexus absence.

## Method selection

Given a problem with a single linear failure chain,
When Analyze selects a method,
Then 5-whys is selected and rationale is recorded.

Given a problem with multiple contributing factors across categories,
When Analyze selects a method,
Then fishbone (Ishikawa) is selected and rationale is recorded.

## Output directory absent: auto-create

Given `.wabblespec/analysis/` does not exist,
When Analyze runs,
Then Analyze creates the directory before writing the RCA report.
Then no error is raised for absent directory.

## Do NOT: begin without declared problem

Given Analyze is invoked with only evidence files and no problem statement,
Then Analyze does not begin analysis.
Then Analyze surfaces the requirement for a problem statement.

## Receipt fields

Given any successful Analyze run,
Then the receipt contains: `method_used`, `root_cause_identified`, `root_cause_confidence`, `root_cause_summary`, `contributing_factors_count`, `evidence_sources`, `rca_report_path`, `nexus_queried`.
Then `rca_report_path` matches the path of the written RCA report.
