# Cold-Start Behavior — Analyze

Defines what Analyze does when its expected evidence sources or upstream artifacts are absent.

## Absent: problem statement

Condition: Analyze invoked without a problem statement (no symptom description provided).
Action: Surface: "Analyze requires a problem statement. Describe the symptom, failure, or unexpected behavior."
Do NOT: Begin an RCA without a declared problem.

## Absent: Nexus / entity-graph.json

Condition: Nexus unavailable or entity-graph.json missing when Analyze attempts cross-session context query.
Detection: Nexus returns empty or entity-graph.json not found.
Action: Proceed without Nexus enrichment. Set `nexus_queried: false` in receipt. Log: "Nexus unavailable — analysis proceeds without cross-session pattern context."
Do NOT: Block analysis. Nexus enrichment is additive.

## Absent: evidence sources

Condition: No logs, receipts, test output, or user reports provided alongside the problem statement.
Detection: Evidence source list in invocation is empty.
Action: Surface: "Evidence improves RCA confidence. Attach logs, receipts, or test output if available. Proceeding with symptom description only — root cause confidence will be speculative (< 0.4) without evidence."
Do NOT: Refuse to run. Analyze may proceed on symptom alone; confidence is declared accordingly.

## Absent: analysis/ output directory

Condition: `.wabblespec/analysis/` directory does not exist.
Detection: Directory read returns 404.
Action: Create the directory before writing the RCA report. This is normal on first run.

## Absent: prior analyze receipt for this problem

Condition: No prior `analyze-receipt-<timestamp>.json` for this problem domain.
Action: Treat as first investigation. No prior root cause to compare against.

## Default state on cold start

| Field | Default |
|---|---|
| `method_selected` | Not declared — Analyze selects from: 5-whys (linear), fishbone (multi-factor), fault-tree (multi-path), timeline (unknown sequence) |
| `nexus_queried` | false — unless Nexus is available |
| `root_cause_confidence` | speculative (< 0.4) without evidence; probable (0.4–0.69) with partial evidence; confident (≥ 0.7) with verifiable evidence |
| `rca_output_path` | `.wabblespec/analysis/rca-<timestamp>.md` |
| `contributing_factors_count` | 0 on start; populated during analysis |
