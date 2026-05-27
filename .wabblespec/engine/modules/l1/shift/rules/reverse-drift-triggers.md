# Reverse Drift Triggers

Reverse drift occurs when implementation diverges from spec — the spec says X but the code does Y. Shift detects this direction (spec → impl) as well as forward change (old spec → new spec).

## What triggers a reverse drift check

Run `scripts/reverse-drift-detector.py --spec <path> --impl <path>` when:

- A SKILL.md file was modified in this execution (spec changed)
- A schema file was modified in this execution (contract changed)
- Explicit `/shift --check-drift` command
- Archive post-hook runs after a session that touched spec artifacts

## Drift categories

### Field mismatch
Spec declares a required field in a receipt or schema. Implementation does not write that field. Severity: HIGH — causes validation failures downstream.

### Mode gap
Spec declares a module mode (e.g., `--sweep`). Implementation does not handle that mode path. Severity: HIGH — silent no-op when mode is invoked.

### Rule violation
Module SKILL.md states a rule (e.g., "always check graph freshness before querying"). Evidence in receipts shows the check is skipped. Severity: MEDIUM.

### Ordering violation
SKILL.md declares a step order. Implementation executes steps in a different order. Severity: MEDIUM if observable, LOW if purely documentary.

### Description drift
SKILL.md description no longer matches what the module does. Severity: LOW — documentation debt, not behavioral.

## Drift response

| Severity | Action |
|---|---|
| HIGH | Block archive. Surface drift to human. Do not proceed until resolved. |
| MEDIUM | Record in receipt. Flag in shift report. Proceed but note. |
| LOW | Record in receipt only. Document as future cleanup scope. |

## What is NOT drift

- Implementation adds behavior not in spec (this is spec lag, not drift — update spec)
- Implementation omits optional behavior from spec (check if optional or required first)
- Spec has not-yet-implemented features clearly marked as deferred (not drift — intentional)
