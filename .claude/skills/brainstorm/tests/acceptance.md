# Brainstorm — Acceptance Criteria

## BLOCK: absent problem statement

Given Brainstorm is invoked without a declared problem, question, or prompt,
Then Brainstorm surfaces: "Brainstorm requires a declared problem or question. State what you are generating ideas for."
Then no brainstorm receipt is written.
Then no options file is written.

## Happy path: divergent generation

Given a problem statement is provided with a genuinely open solution space,
When Brainstorm runs,
Then options are generated without evaluation or filtering during the generation phase.
Then at least 3 distinct options are generated before the convergence gate is evaluated.
Then a top options file is written to `.wabblespec/brainstorm/options-<timestamp>.md`.
Then a brainstorm receipt is written to `.wabblespec/state/receipts/brainstorm-receipt-<timestamp>.json`.

## evaluation_deferred invariant

Given any Brainstorm run,
Then `evaluation_deferred` in the receipt is true.
Then the receipt does not contain comparative judgments, rankings, or arguments for any specific option during the generation phase.
Then if evaluation occurred during generation, `evaluation_deferred` is recorded as false and this is surfaced as a process failure.

## Convergence gate

Given Brainstorm has generated options and a convergence signal fires (volume cap, diminishing returns, user signal, or time budget),
Then Brainstorm stops generating and moves to surface top options.
Then `convergence_trigger` in the receipt records which signal fired.
Then `options_generated` in the receipt records total ideas generated before convergence.

## Top options: breadth requirement

Given a generated option set,
When Brainstorm surfaces top options,
Then 3–5 options are selected.
Then options represent genuinely different approaches (not rewordings of the same approach).
Then no option is argued for — options are described neutrally.

## Do NOT: invoke when solution is clear

Given Brainstorm is invoked but the solution is already identified and agreed upon,
Then Brainstorm surfaces: "Solution space is not open — proceed to Propose or Specify."
Then Brainstorm does not generate alternatives for a closed decision.

## Do NOT: re-invoke without new information

Given Brainstorm was already run this session for the same problem with no new information provided,
Then Brainstorm surfaces that it was already run and asks for new information or constraints before proceeding.

## Absent rules files: fallback

Given `rules/divergence-rules.md` is missing,
When Brainstorm runs,
Then Brainstorm applies SKILL.md divergence rules.
Then the receipt logs: "divergence-rules.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Brainstorm run,
Then the receipt contains: `options_generated`, `convergence_trigger`, `options`, `evaluation_deferred`, `top_options_path`.
Then `top_options_path` matches the path of the written options file.
