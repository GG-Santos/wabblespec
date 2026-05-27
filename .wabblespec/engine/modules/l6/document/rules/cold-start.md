# Cold-Start Behavior — Document

Defines what Document does when its Archive receipt or source content are absent.

## Absent: Archive receipt

Condition: Document invoked but no archive receipt exists in `.wabblespec/state/receipts/`.
Detection: `archive-receipt.json` absent.
Action: BLOCK Document run. Surface: "Document activates only after an Archive receipt exists. Complete the task archive first."
Do NOT: Document in-progress or unarchived work. Document operates on completed, archived work only.

## Absent: source content to document

Condition: Archive receipt exists but the declared source files are missing.
Detection: File paths in archive receipt resolve to absent files.
Action: Surface: "Declared source files missing: [paths]. Cannot document absent content."
Do NOT: Generate documentation without reading the actual source.

## Absent: documentation target declaration

Condition: Document invoked without specifying what output to produce.
Action: Surface: "Document requires a target: README, inline comments, CHANGELOG entry, API reference, or other."

## Absent: CHANGELOG.md (for CHANGELOG target)

Condition: Document is writing a CHANGELOG entry but `CHANGELOG.md` does not exist.
Detection: File read returns 404.
Action: Create CHANGELOG.md with initial structure before writing the entry.

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | Archive receipt required — no exceptions |
| `content_source` | Verified from source files only — no speculation |
| `review_required` | true — Document output is a draft |
| `auto_trigger` | false — Document requires explicit invocation |
| `future_state` | Not documented — Document records what is true, not what is planned |
