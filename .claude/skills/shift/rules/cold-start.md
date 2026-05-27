# Cold-Start Behavior — Shift

Defines what Shift does when its source spec or change classification inputs are absent.

## Absent: source spec artifact to update

Condition: Shift invoked without a declared target spec (no spec.md or task card path).
Action: Surface: "Shift requires a target spec artifact. Specify the spec file to update."
Do NOT: Modify an implied spec without confirmation of which file.

## Absent: change-classification.md

Condition: `rules/change-classification.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md change classification rules. Log: "change-classification.md missing — using SKILL.md defaults."

## Absent: reverse-drift-triggers.md

Condition: `rules/reverse-drift-triggers.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md reverse drift trigger rules. Log: "reverse-drift-triggers.md missing — using SKILL.md defaults."

## Absent: change description

Condition: Shift invoked with a target spec but no description of what changed.
Action: Surface: "Shift requires a change description. What changed, and why does the spec need updating?"
Do NOT: Infer the change from the spec diff alone without declared intent.

## Absent: prior spec version (for delta calculation)

Condition: Target spec exists but no prior version in git or receipt to diff against.
Detection: `git log <spec-path>` returns single commit or no history.
Action: Treat as first tracked version. Shift proceeds with current content. Log: "No prior version found — delta not calculable."

## Absent: semantic differ script

Condition: `scripts/semantic-differ.py` missing.
Detection: File read returns 404.
Action: Perform manual diff. Log: "semantic-differ.py unavailable — delta computed by textual comparison only."

## Default state on cold start

| Field | Default |
|---|---|
| `target_spec` | Not declared — must be specified |
| `change_class` | Not classified — determined during Shift (ADDITIVE / BREAKING / CORRECTIVE / REFACTOR) |
| `reverse_drift_check` | Active — checks whether spec update contradicts prior verified outputs |
| `delta_scope` | LOCAL (default); BOUNDARY if change affects external interfaces |
| `diff_required` | true — before/after shown for all spec changes |
