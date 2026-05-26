# Reverse Drift Detection Policy

Reverse drift occurs when implementation files are edited AFTER the spec that governs them was last updated. This is a signal that spec and implementation have diverged — the implementation may have drifted ahead of what the spec describes, meaning the spec no longer reflects reality.

## Definition

**Reverse drift:** A condition where `mtime(implementation_file) > mtime(spec_artifact)` for a file governed by a locked spec.

This is the opposite of the normal drift direction (spec ahead of implementation). Reverse drift means code changed without the spec being updated first, violating I1 (spec is single source of truth).

## Detection Scope

The detector compares:
- Source: spec artifacts in `.wabblespec/plans/`, `.wabblespec/specs/`, task-card.md
- Target: implementation files in `project/repo/` declared in the wave plan

Files outside the wave plan's declared write targets are excluded.

## Severity Levels

| Condition | Severity | Action |
|---|---|---|
| Implementation newer than spec by < 1 hour | WARNING | Log to receipt, continue |
| Implementation newer than spec by 1-24 hours | STALENESS_VIOLATION | Flag in receipt, notify Provenance |
| Implementation newer than spec by > 24 hours | SPEC_VIOLATION | Block wave, require Specify re-run or `--patch` |
| Implementation newer than spec, spec contains BREAKING delta class | HARD error | Block immediately, halt pipeline |

## Exemptions

Reverse drift is expected and acceptable in these cases:
- `COSMETIC` changes (formatting, comment updates, dead code removal) — file mtime updated but no behavioral change
- Files explicitly declared as `auto-generated` in the wave plan
- Test files when changes are test additions only (no production behavior change)

Exemptions must be declared in the wave plan or receipt. No silent exemptions.

## State Emitted

When reverse drift is detected:
- Affected drawer: staleness transitions to `NEEDS_REVERIFICATION`
- Provenance cascade triggered for all specs citing affected drawers
- Receipt field `reverse_drift_detected: true` set with evidence list

## Recovery

| Severity | Recovery action |
|---|---|
| WARNING | Acknowledge in receipt, continue |
| STALENESS_VIOLATION | Run Specify `--patch` to update spec to reflect actual changes, or revert implementation |
| SPEC_VIOLATION | Run Specify full re-run, or revert implementation to match spec |
| HARD error | Human decision required — revert or re-spec before proceeding |
