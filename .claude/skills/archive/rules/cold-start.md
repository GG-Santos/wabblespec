# Cold-Start Behavior — Archive

Defines what Archive does when its upstream receipts or storage artifacts are absent.

## Absent: verifier receipt

Condition: No `verifier-receipt.json` (or delivery-receipt) in `.wabblespec/state/receipts/` for the current task.
Detection: Receipt scan finds no PASS verifier receipt.
Action: BLOCK Archive. Surface: "Archive requires a Verifier PASS receipt. The task must pass verification before archiving."
Do NOT: Archive unverified work.

## Absent: archive/ directory

Condition: `.wabblespec/state/archive/` does not exist.
Detection: Directory read returns 404.
Action: Create `.wabblespec/state/archive/` and `receipt-index.json` with empty entries. This is normal on first archive.

## Absent: receipt-index.json

Condition: `archive/receipt-index.json` missing.
Detection: File read returns 404.
Action: Create with empty index: `{"entries": [], "version": 1}`. Log: "Archive index initialized."

## Absent: git commit (for tasks involving code changes)

Condition: Task involved file changes but no commit was made.
Detection: `git status` shows unstaged or uncommitted changes.
Action: Block archive. Surface: "Uncommitted changes detected. Commit before archiving."
Do NOT: Archive a task where code changes were made but not committed.

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | Verifier PASS receipt required |
| `git_committed` | Required for code tasks; N/A for document-only tasks |
| `archive_index` | Created if absent |
| `receipt_format` | Append to receipt-index.json; write individual archive entry |
| `immutable` | true — archived receipts are not modified after writing |
