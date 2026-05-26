# Cold-Start Behavior — Reference Load (L0)

Defines what Reference Load does when its expected upstream artifacts are absent.

## Absent: reference files

Condition: One or more `_shared/references/` files requested by the session are absent.
Detection: File read returns 404 for a referenced path.
Action: Surface DEPENDENCY error naming the specific missing reference file. Do not substitute defaults — reference files are authoritative and cannot be inferred.
Do NOT: Proceed with partial reference loading if a required file is absent.

## Absent: prior receipts

Condition: No recipe receipt when Reference Load is called.
Detection: `recipe-receipt.json` absent.
Action: Surface DEPENDENCY error — Recipe must run first to declare the build target before references are loaded.
Do NOT: Load all references speculatively without a declared target.

## Default state on cold start

| Field | Default |
|---|---|
| `loaded_references` | empty list |
| `load_status` | PENDING until all required references confirmed present |

Reference Load is a utility module. On cold start it loads nothing and waits for the session to declare which references are needed.
