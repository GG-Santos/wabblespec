# Staging Policy

What to include in a single commit and when to split.

## Atomic commit definition

A commit is atomic when:
1. It does exactly one thing
2. The codebase is in a working state before and after the commit
3. Its commit message can be written in one sentence without "and"

If the message requires "and" to be complete, the commit should be split.

## What belongs in one commit

A single commit includes all changes required for exactly one logical change. A "logical change" means:
- One bug fix (including tests for that fix and documentation if changed)
- One new feature (including its tests, schema, and documentation)
- One refactor of one module or function
- One dependency version bump (may group minor bumps in one chore commit if they are unrelated to any feature)

Related files always go together: if a schema change is required for a feature, they are one commit, not two.

## When to split

Split when staged changes contain:
- Changes to files in unrelated feature areas
- A bug fix alongside a new feature
- A refactor alongside a behavior change
- Changes that would require different commit types (e.g., a `feat` and a `fix` in the same stage)

## Splitting process

1. Identify logical groupings in the diff
2. Stage only the first group
3. Commit with appropriate message
4. Stage the second group
5. Commit
6. Repeat until all changes are committed

When splitting is required: present the proposed grouping for human confirmation before applying. Never auto-split without confirmation.

## Files that cross commit boundaries

Some files legitimately appear in multiple commits (e.g., `package.json` updated for a new dependency AND a version bump in the same session). These must be in separate commits — the changes to the shared file are staged selectively (`git add -p`).

## Excluded from commits

Never commit:
- `.env` files or any file matching `*.env`, `*.env.*`
- Credential files, key files, secret files
- Build artifacts (`dist/`, `build/`, `*.pyc`, `*.class`)
- Editor configuration files unless they are project-standard (`.editorconfig` is fine; `.vscode/settings.json` is project-specific and may be excluded by convention)
- Files already in `.gitignore`
