# Economy — Acceptance Criteria

## Mechanical rules active now

Given any WabbleSpec module produces output,
Then Economy mechanical rules (Rules 1–5) apply regardless of the 50-execution activation gate.
Then these rules are not optional.

## Rule 1 — Output size threshold: < 500 tokens

Given a module output is estimated at fewer than 500 tokens,
When the output is produced,
Then it is pasted inline.
Then no capture file is written.

## Rule 1 — Output size threshold: 500–2000 tokens

Given a module output is estimated at 500–2000 tokens,
When the output is produced,
Then it is pasted inline with compression: prose padding dropped, technical substance kept.
Then code blocks, file paths, exact numeric values, error messages, and schema field names are preserved.
Then sentences that restate prior context, transition prose, tool explanations, and hedging on certain facts are dropped.

## Rule 1 — Output size threshold: > 2000 tokens

Given a module output exceeds 2000 tokens,
When the output is captured,
Then the full content is written to `.wabblespec/captures/<module>-<timestamp>.txt`.
Then only a summary (first 200 tokens + citation) is pasted inline.
Then the in-context reference format is: `[captured: <path> — <N> tokens — <one-line summary>]`.
Then capture is not lossy — the full content is on disk.

## Rule 3 — Exact-error preservation

Given a stack trace, compiler error, test failure output, hook exit message, or schema validation error is produced,
Then it is always pasted verbatim — never compressed, never summarized.
Then if the error output exceeds 2000 tokens, it is both captured to disk AND pasted inline.
Then the 2000-token threshold does not apply to error output.

## Rule 4 — Reference loading discipline

Given ReferenceLoad or MemorySearch loads external content,
When the content is incorporated,
Then the project-map card or summary is loaded first.
Then raw file content is loaded only if the card is insufficient for the current decision.
Then raw loads exceeding 2000 tokens are captured and cited.
Then no more than 3 raw reference files are loaded per wave without a capture citation for each.

## --budget mode: AGENT.md ceiling absent

Given `AGENT.md` does not declare `economy.budget_ceiling` or `per_wave_ceiling`,
When Economy is invoked in `--budget` mode,
Then Economy emits a warning and exits cleanly.
Then no budget advisory is written.
Then execution is not blocked.

## --budget mode: projection under ceiling

Given `economy.budget_ceiling` is declared and projected tokens are within the ceiling,
When Economy runs `--budget`,
Then no advisory is written to `.wabblespec/advisories/`.
Then the receipt is updated with `token_budget_declared`, `tokens_projected`, and `budget_exceeded: false`.

## --budget mode: projected overrun

Given `economy.budget_ceiling` is declared and projected tokens exceed the ceiling,
When Economy runs `--budget`,
Then a budget advisory is written to `.wabblespec/advisories/budget-<timestamp>.json`.
Then the advisory contains: `advisory_id`, `type: "budget-overrun-risk"`, `budget_ceiling`, `projected_tokens`, `overage`, `overage_pct`, `wave_index`, `recommendation`, `blocking: false`.
Then the advisory is non-blocking — Executor surfaces it to the human, who decides.
Then `budget_exceeded: true` is recorded in the wave receipt.

## --budget does not block execution

Given a budget advisory is emitted,
When Executor reads the advisory,
Then Economy does not refuse to run the wave.
Then the decision to split, defer, or proceed belongs to the human or Executor.

## Economy module activation gate

Given fewer than 50 real task executions have completed,
When the Economy module is evaluated for full activation,
Then the full Economy module (with per-wave token caps and automatic compression pass) remains inactive.
Then I12 + mechanical rules are sufficient.

Given 50+ real executions have completed and average output exceeds 2x the information-minimal baseline,
Then Economy activates with token caps.

## Do NOT

Given any Economy run,
Then Economy does not discard captured content — full content is always on disk.
Then Economy does not compress error output — errors are always pasted verbatim.
Then Economy does not block waves based on advisory alone — advisory is non-blocking.

## Receipt fields

Given any Economy `--budget` run,
Then the wave receipt is updated with: `token_budget_declared`, `tokens_projected`, `budget_exceeded`.
Given a budget advisory is emitted,
Then the advisory file contains: `advisory_id`, `type`, `budget_ceiling`, `projected_tokens`, `overage`, `overage_pct`, `wave_index`, `recommendation`, `blocking`.
