# Shift — Acceptance Criteria

## BLOCK: absent spec artifact

Given Shift is invoked without a declared target spec artifact,
Then Shift surfaces: "Shift requires a target spec artifact. Specify the spec file to update."
Then no compatibility report is written.
Then no receipt is written.

## BLOCK: absent change description

Given Shift is invoked with a target spec but no description of what changed,
Then Shift surfaces: "Shift requires a change description. What changed, and why does the spec need updating?"
Then Shift does not infer the change from the spec diff alone without declared intent.
Then no compatibility report is written.

## Happy path: semantic diff + reverse drift check

Given `spec_before` and `spec_after` are provided,
When Shift runs,
Then the semantic diff classifies the change as BREAKING, DEPRECATION, ADDITIVE, or COSMETIC.
Then `reverse_drift_detected` is evaluated by comparing spec_after against the implementation path.
Then a compatibility report is written to `.wabblespec/shift/compat-<timestamp>.md`.
Then a semantic diff is written to `.wabblespec/shift/diff-<timestamp>.md`.
Then a shift receipt is written to `.wabblespec/state/receipts/shift-receipt-<timestamp>.json`.

## Multiple classifications

Given a single spec change removes an old function and adds a replacement with a different signature,
When Shift classifies the change,
Then both BREAKING and ADDITIVE classifications are recorded (one change may produce multiple classes).

## Loop-back required: BREAKING + downstream consumers

Given the change_class is BREAKING and at least one downstream consumer is affected,
When Shift evaluates loop-back,
Then `loop_back_required` in the receipt is true.
Then the originating pipeline is signaled to surface to the user before proceeding.
Then Shift does not suppress this signal.

## No loop-back: BREAKING with no consumers

Given the change_class is BREAKING but no downstream consumers are declared or affected,
When Shift evaluates loop-back,
Then `loop_back_required` is false.

## No loop-back: COSMETIC change

Given the change_class is COSMETIC (documentation or rename with no behavior change),
When Shift evaluates loop-back,
Then `loop_back_required` is false.
Then Shift does not run for COSMETIC-only changes when triggered by Archive (Archive does not trigger Shift for COSMETIC).

## Reverse drift detection

Given the spec was updated but the implementation was not changed to match,
When Shift runs reverse drift detection,
Then `reverse_drift_detected` is true.
Then `reverse_drift_details` describes the discrepancy.

## No prior spec version

Given the target spec exists but no prior version is available in git or receipts,
When Shift runs,
Then Shift proceeds with the current content.
Then the receipt logs: "No prior version found — delta not calculable."
Then no error is raised.

## Absent scripts: fallback

Given `scripts/semantic-differ.py` is missing,
When Shift runs,
Then Shift performs a manual textual diff.
Then the receipt logs: "semantic-differ.py unavailable — delta computed by textual comparison only."

## Receipt fields

Given any successful Shift run,
Then the receipt contains: `change_class`, `reverse_drift_detected`, `reverse_drift_details`, `downstream_consumers_affected`, `affected_consumer_ids`, `compatibility_report_path`, `semantic_diff_path`, `loop_back_required`.
