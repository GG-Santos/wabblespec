# Cold-Start Behavior — Reference Load (L1)

Defines what the L1 Reference Load module does when its expected upstream artifacts are absent.

## Absent: reference files

Condition: One or more references requested by the current session are absent from `_shared/references/`.
Detection: File read returns 404 for a referenced path.
Action: Surface DEPENDENCY error naming the specific missing reference file. Do not substitute defaults — references are authoritative.
Do NOT: Proceed with partial loading if a required reference is absent.

## Absent: prior receipts

Condition: `recipe-receipt.json` absent when Reference Load is called.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Recipe. References are target-dependent; loading without a target wastes context.
Do NOT: Load all references speculatively.

## Default state on cold start

| Field | Default |
|---|---|
| `loaded_references` | empty — populated only by explicit load requests |
| `load_status` | PENDING until all required references confirmed present |

L1 Reference Load operates identically to L0 but is invoked mid-session when additional references are needed after Recipe has run.
