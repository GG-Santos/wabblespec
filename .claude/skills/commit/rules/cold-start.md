# Cold-Start Behavior — Commit

Defines what Commit does when its staged changes or rule files are absent.

## Absent: staged changes

Condition: `git diff --cached` returns empty — nothing staged.
Detection: Staged diff is empty.
Action: Surface: "Nothing staged for commit. Stage changes with git add before invoking Commit."
Do NOT: Stage files automatically without explicit user instruction.

## Absent: verifier receipt (for task commits)

Condition: Commit is for a WabbleSpec task but no verifier receipt exists.
Detection: Task context present but `.wabblespec/receipts/verifier-receipt.json` absent.
Action: Surface warning: "No verifier receipt found for this task. Committing without verified output is discouraged." Do NOT block — Commit proceeds on user confirmation.

## Absent: rule files

Condition: `rules/conventional-commits.md`, `rules/message-quality.md`, or `rules/staging-policy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md commit rules. Log: "Commit rule file missing — using SKILL.md defaults."

## Absent: commit message from user

Condition: Commit invoked without a user-provided message and no context to derive from.
Action: Derive from staged diff + task context. Surface derived message for user confirmation before committing.
Do NOT: Commit without the user seeing the message.

## Default state on cold start

| Field | Default |
|---|---|
| `message_format` | Conventional commits (type(scope): description) |
| `co_author` | Appended per CLAUDE.md co-author rule |
| `pre_commit_hooks` | Run — do not skip with --no-verify unless user explicitly requests |
| `signing` | Do not add --no-gpg-sign; if signing is configured, it runs |
| `amend` | Not default — new commit preferred over amend |
