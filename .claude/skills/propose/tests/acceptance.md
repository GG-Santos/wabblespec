# Propose — Acceptance Criteria

## BLOCK: absent spec artifacts

Given `specs/` is empty or returns 404,
When Propose is invoked,
Then Propose surfaces a DEPENDENCY error naming Specify.
Then Propose does not generate proposals from the user's raw task description alone.
Then no options document is written.

## BLOCK: absent specify receipt

Given `specify-receipt.json` is absent,
When Propose is invoked,
Then Propose surfaces a DEPENDENCY error naming Specify.
Then Propose does not proceed without a confirmed spec.

## Happy path: 2–4 distinct options generated

Given a locked spec and `scope.md` exist,
When Propose runs at a branching decision point,
Then 2–4 distinct, implementable options are generated.
Then each option is assessed across 5 tradeoff dimensions: Complexity, Time, Risk, Reversibility, Fits scope.
Then one recommendation is issued with a rationale tied to scope and target.
Then the options document is written to `.wabblespec/options-<stage>-<timestamp>.md`.
Then the selected option is recorded in the receipt.
Then a receipt is written to `.wabblespec/state/receipts/`.

## Options must be distinct

Given Propose generates options,
Then each option is meaningfully different from the others — not a variation of the same approach.
Then options that are outside `scope.md` are excluded before presentation.
Then options that contradict `intent.md` are excluded before presentation.

## Maximum 4 options

Given a decision point with many possible approaches,
When Propose generates options,
Then at most 4 options are written to the options document.
Then more than 4 options are not generated.

## Tradeoffs are honest

Given any option in the options document,
Then the tradeoff assessment states downsides explicitly.
Then no option's tradeoffs are hidden or understated.

## HIGH-impact decisions routed to Reviewer

Given the decision point has HIGH impact (architectural or cross-cutting),
When Propose completes option generation,
Then Propose routes the options to Reviewer before passing the selected option to Specify.
Then Propose does not pass HIGH-impact options to selection without Reviewer.

## Propose does not decide

Given any Propose run,
Then the recommendation is explicitly labeled advisory.
Then Propose does not lock or commit the selection without human or Reviewer confirmation.

## Do NOT: activate for obvious decisions

Given a decision point with one obvious answer (no genuine branching),
Then Propose does not activate.
Then Propose surfaces: "No branching point detected — proceed directly to Specify."

## Options document location

Given any successful Propose run,
Then the options document is written inside `.wabblespec/` only.
Then no options file is written outside `.wabblespec/`.
