# Acceptance Tests — Commit (L7)

## AT-COMMIT-01: Subject line enforces 72-character limit

**Given** a Commit invocation generating or validating a commit message
**When** the subject line exceeds 72 characters
**Then** Commit flags this as a violation and requires the subject to be shortened before proceeding

---

## AT-COMMIT-02: Body must explain WHY, not WHAT

**Given** a commit with a non-trivial changeset requiring a body
**When** the body describes what was changed (the mechanism) rather than why
**Then** Commit flags the body as a "what" and requires a "why" explanation instead

---

## AT-COMMIT-03: Mixed-concern changesets require split

**Given** staged changes that span multiple logical concerns (e.g., a bug fix and a new feature)
**When** Commit analyzes the staged changes
**Then** Commit proposes a split and does not commit mixed concerns under one message — split must be confirmed before applying

---

## AT-COMMIT-04: No-verify never used

**Given** any Commit invocation regardless of mode or context
**When** a hook failure occurs
**Then** Commit never passes `--no-verify`; hook failures are surfaced to human for investigation

---

## AT-COMMIT-05: Scope inferred from changed files when not declared

**Given** a Commit invocation without an explicit scope
**When** scope inference runs
**Then** scope is derived from the primary directory or module of changed files (e.g., files in `modules/l6/copy/` -> scope `copy`)

---

## AT-COMMIT-06: BREAKING CHANGE footer required when breaking is true

**Given** a Commit invocation with `breaking: true`
**When** the commit message is produced
**Then** a `BREAKING CHANGE:` footer is included describing what breaks and what consumers must do

---

## AT-COMMIT-07: Split and stage modes require human confirmation before applying

**Given** a `split` or `stage` mode Commit invocation
**When** a proposed grouping or split is generated
**Then** the proposal is presented for human confirmation; Commit does not auto-apply without confirmation

---

## AT-COMMIT-08: Receipt contains commits produced with per-commit details

**Given** a completed Commit run
**Then** the receipt at `.wabblespec/state/receipts/commit-{timestamp}.json` contains:
- `mode`
- `commits_produced` (each with type, scope, breaking, subject, body, files_included, applied)
- `total_commits`
- `dry_run`
- `verdict`
