---
name: commit
description: Stage, split, and write conventional git commits. Enforces type(scope): description format, 72-char subject line, why-not-what body, and coherent atomic units.
layer: L7
---

# Commit

You turn staged changes into clean, conventional, atomic commits. Not just a message — the right scope, the right type, the right split. A commit is a unit of meaning. You enforce that.

## What this skill does

Commit reviews the current git state, identifies logical groupings of changes, produces conventional commit messages for each group, and either applies them or presents them for human confirmation. It enforces: type(scope): description format, 72-char subject line limit, "why not what" body convention, and atomic commit boundaries.

## When to use

Commit activates:
- At the end of the Polish pipeline, after Changelog
- When a developer has made changes and needs clean commit messages
- When a large changeset needs to be split into logical atomic commits
- When existing commits need to be audited for convention compliance

## Inputs

- **Mode** — `stage | split | write | audit` (default: write — assumes changes already staged)
- **Message** — pre-written commit message to validate and apply (optional; if absent, Commit generates one)
- **Scope** — explicit scope to use (optional; Commit infers from changed files if absent)
- **Breaking** — boolean, whether this commit introduces a breaking change (default: false)
- **Sign** — whether to GPG-sign the commit (default: false)
- **Dry-run** — produce commit message(s) without applying (default: false; always true in audit mode)

## Output contract

**Receipt:** `.wabblespec/receipts/commit-{timestamp}.json`

```json
{
  "mode": "string",
  "commits_produced": [
    {
      "type": "string",
      "scope": "string or null",
      "breaking": false,
      "subject": "string",
      "body": "string or null",
      "footer": "string or null",
      "files_included": ["list"],
      "applied": true
    }
  ],
  "total_commits": 0,
  "dry_run": false,
  "verdict": "PASS | WARN | FAIL",
  "committed_at": "ISO-8601"
}
```

`verdict: FAIL` when the staged changes cannot be committed due to a hook failure or staged state issue. `verdict: WARN` when the changeset was split and human review is recommended before applying.

## Steps

### Mode: stage

**Step 1 — Review working tree.** Identify unstaged changes. Group by logical unit (same feature, same fix, same refactor). Stage each group separately.

**Step 2 — Report grouping.** Surface the proposed grouping for human confirmation before staging. Do not auto-stage without confirmation.

### Mode: split

**Step 1 — Analyze staged changes.** Identify whether staged changes span multiple logical concerns (e.g., a bug fix and a feature in the same diff). If they do: propose a split.

**Step 2 — Produce split plan.** List proposed commits with their file subsets. Present for confirmation. Never split and apply without human approval.

### Mode: write

**Step 1 — Infer scope.** If no scope is declared: infer from the primary directory or module of changed files (e.g., files in `modules/l6/copy/` → scope `copy`; files in `.wabblespec/engine/shared/schemas/` → scope `schemas`).

**Step 2 — Select type.** Apply `rules/conventional-commits.md` type selection. Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `style`, `ci`, `build`. When in doubt between `feat` and `refactor`: if behavior changes for users → `feat`. If behavior is unchanged → `refactor`.

**Step 3 — Write subject line.**
- Format: `type(scope): description` or `type(scope)!: description` for breaking changes
- 72 characters maximum (total including type and scope prefix)
- Description: imperative mood, lowercase, no period
- Describes what the commit does — the effect, not the mechanism

**Step 4 — Write body (if non-trivial).**
- Explain WHY this change was made
- What problem it solves or what constraint it addresses
- Do not describe WHAT — that is in the diff
- Wrap at 72 characters per line
- Separate from subject with one blank line

**Step 5 — Write breaking change footer (if applicable).**
`BREAKING CHANGE: {description of what breaks and what consumers must do}`

**Step 6 — Apply or return.**
If `dry-run`: output message(s) to receipt only.
If not dry-run and not split: apply commit.
If split: present for confirmation before applying.

### Mode: audit

Review the last N commits (default: 10) for convention compliance. Emit findings per commit: type valid, scope present, subject ≤72 chars, body present when complex diff, breaking changes flagged.

## What NEVER goes in a commit message

- Restating the file name when scope already says it (`fix(auth): fix auth.ts` — drop `auth.ts`)
- "This commit does X" — the diff says what; the body says why
- "I", "we", "now", "currently" — tense and person have no place
- "Generated with Claude Code" or any AI attribution in the body
- Emoji — unless the project's commit convention explicitly requires them
- Hedging ("might", "should", "could be") — state the fact or don't state it
- Breaking change notice buried in prose — use BREAKING CHANGE footer

## Failure modes

**Non-atomic commits:** A commit that mixes a bug fix and a feature is not atomic. Enforce split when this is detected. Do not commit mixed concerns under one message.

**"What" bodies:** A body that says "Changed the authentication handler to use PKCE" is a what. The corresponding why is "PKCE is required for public clients (mobile) per OAuth 2.0 Security BCP." Enforce why.

**Subject case:** Commit subjects are lowercase after the type prefix. No title case, no sentence case.

**Skipping hooks:** Commit never passes `--no-verify`. Hook failures are surfaced to human for investigation, not bypassed.
