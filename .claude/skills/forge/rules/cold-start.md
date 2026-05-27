# Cold-Start Behavior — Forge

Defines what Forge does when its Blueprint input or write targets are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Forge requires L8 corpus gate (100+ PASS receipts)."

## Absent: Blueprint receipt

Condition: No `blueprint-receipt.json` with an approved design.
Detection: Blueprint receipt absent or status not `approved`.
Action: BLOCK Forge. Surface: "Forge requires an approved Blueprint design. Complete Blueprint → human approval first."
Do NOT: Write framework changes without an approved design.

## Absent: backup of files to be modified

Condition: Forge is about to modify framework files but no backup exists.
Detection: Backup directory absent or empty.
Action: Create backup before modifying. `.wabblespec/forge-backup/[timestamp]/` containing copies of all files to be modified.
Do NOT: Modify framework files without taking a backup first.

## Absent: post-forge validation step

Condition: Forge has written changes but validate-graph.py has not been run.
Detection: Validation receipt absent after write.
Action: Run validate-graph.py automatically after every Forge write batch. Block completion if violations found.

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate + approved Blueprint receipt |
| `backup_required` | true — backup created before any framework modification |
| `validation_required` | true — validate-graph.py must pass after Forge writes |
| `scope_lock` | Changes limited to Blueprint-specified files; no scope expansion |
| `revert_available` | true — Forge can revert to backup if validation fails |
