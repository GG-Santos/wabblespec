# Specify — Acceptance Criteria

## BLOCK: absent scope.md

Given `scope.md` does not exist,
When Specify is invoked,
Then Specify surfaces a DEPENDENCY error: "ScopeFrame must run before Specify."
Then Specify does not infer scope from the user message alone.
Then no task card is written.

## BLOCK: absent upstream receipts

Given `recipe-receipt.json` or `scopeframe-receipt.json` is absent,
When Specify is invoked,
Then Specify surfaces a DEPENDENCY error naming the missing upstream module.
Then Specify does not proceed without recipe.json and scope.md confirmed.

## Happy path: task card with GWT criteria

Given `scope.md` and `recipe.json` exist with valid targets,
When Specify runs,
Then the goal statement is one sentence and falsifiable.
Then acceptance criteria are written in GWT format (Given/When/Then).
Then each "Then" clause is observable and testable.
Then non-goals and assumptions are copied verbatim from scope.md.
Then `change_class` is declared as BREAKING, ADDITIVE, or COSMETIC.
Then the task card is written to `.wabblespec/state/plans/task-card.md`.
Then the user is asked to confirm before the task card is locked.
Then a receipt is written to `.wabblespec/state/receipts/specify-receipt.json`.

## GWT criteria count by complexity

Given complexity = Low,
Then 2–4 acceptance criteria are written.

Given complexity = Medium,
Then 4–8 acceptance criteria are written.
Then at least one failure-path criterion is present.

Given complexity = High,
Then 8–12 acceptance criteria are written.
Then at least one failure-path criterion is present.

## BREAKING delta: adversarial gate

Given `delta_class = BREAKING` AND the task's tags intersect `adversarial_required_for_tags` (security, enforcement, receipt, gate),
When Specify evaluates the adversarial spec gate,
Then the task card is NOT locked before Adversary runs.
Then Adversary is invoked in `challenger_mode: "spec-bound"` with the draft task card.
Then Grader is invoked with the draft task card and Adversary's counter_analysis.
Then the task card is locked only after Grader issues ACCEPT or ESCALATE.
Then `adversarial_spec_gate_triggered: true` is recorded in the receipt.

## BREAKING delta: change_summary and affected_specs

Given `delta_class = BREAKING`,
Then `change_summary` is populated (one line per changed item, prefixed "BREAKING: ...").
Then `affected_specs` lists all spec artifact paths or capability areas being changed.
Then these fields are used by Migrate and Provenance cascade.

## --patch mode: LOCAL scope continues wave

Given Apply emits an ADDITIVE LOCAL delta proposal,
When Specify runs in `--patch` mode,
Then Specify applies the delta inline to the locked task card.
Then the task card version is bumped.
Then `patch_mode: true`, `scope_class: LOCAL`, `delta_applied`, and `task_card_version` are recorded in the receipt.
Then the wave continues.

## --patch mode: BOUNDARY halts wave

Given Apply emits an ADDITIVE BOUNDARY delta proposal,
When Specify runs in `--patch` mode,
Then Specify halts and surfaces the boundary change to the user.
Then `boundary_halt: true` is recorded in the receipt.
Then the wave does not continue until the user resolves the boundary issue.

## Validation before write

Given any Specify run before writing the task card,
Then all of the following are checked: goal is one sentence and falsifiable; every "Then" clause is observable; no duplicate criteria; at least one failure-path criterion for Medium/High; non-goals explicitly stated; no open questions remain; change_class declared.
Then any check failure is fixed before the task card is written.

## decisions.md written after lock

Given the user confirms the task card is locked,
When Step 5b runs,
Then `.wabblespec/state/plans/decisions.md` is written with the goal statement and locked_at timestamp.
Then at least one populated section (Key Decisions, Alternatives Rejected, Constraints Discovered, or Open Questions Resolved) is present.
Then decisions.md is not written before lock confirmation.

## decisions.md omits empty sections

Given a Specify run where no Interview ran and no alternatives were considered,
When decisions.md is written,
Then sections with no content are omitted entirely — no empty headings, no placeholder text.

## decisions.md is not a receipt

Given any Specify run that produces decisions.md,
Then decisions.md is not listed in the receipt chain.
Then Guard does not check for decisions.md as a required artifact.
Then the absence of decisions.md does not block any downstream module.

## --patch mode appends, does not rewrite

Given Specify runs in `--patch` mode and decisions.md already exists,
When Step 5b runs,
Then a `## Patch [timestamp]` section is appended to the existing decisions.md.
Then the original decisions content is preserved.

## Receipt fields

Given any successful Specify run,
Then the receipt contains: `criteria_count`, `gwt_violations`, `open_questions_resolved`, `delta_class`, `adversarial_spec_gate_checked`, `adversarial_spec_gate_triggered`.
Then `gwt_violations` is 0 for PASS status.
Then `open_questions_resolved` is true for PASS status.
