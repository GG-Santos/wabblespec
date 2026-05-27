# Git Parsing

Rules for parsing git commit history in Changelog. Applied in Step 1.

## Conventional commit pattern

Format: `type(scope)!: subject`

- `type`: required; one of the approved types
- `(scope)`: optional; what was changed (module name, feature area, component)
- `!`: breaking change indicator; optional
- `subject`: required; imperative, lowercase, no period, max 72 chars total including prefix

Approved types and their changelog section mappings:

| Type | User-facing? | Changelog section |
|---|---|---|
| `feat` | Yes | Added |
| `fix` | Yes | Fixed |
| `perf` | Yes | Changed (performance) |
| `security` / `sec` | Yes | Security |
| `refactor` | No (default) | Excluded |
| `docs` | Conditional | Added (if user-facing docs) |
| `chore` | No | Excluded |
| `ci` | No | Excluded |
| `build` | No | Excluded |
| `test` | No | Excluded |
| `style` | No | Excluded |

## BREAKING CHANGE detection

A commit is breaking if:
1. It contains `!` in the type prefix: `feat!: remove legacy auth`
2. Its commit body or footer contains: `BREAKING CHANGE: {description}`

Breaking changes are always included regardless of type. A `chore!` is still a breaking change.

Breaking commits are placed in the `Changed` section with a `Breaking:` prefix.

## Footer parsing

Git commit trailers (RFC 5322 format):
- `BREAKING CHANGE: {description}` — marks breaking change
- `Co-authored-by: {name} <{email}>` — do not include in changelog
- `Closes #N` / `Fixes #N` — optionally append issue link to the changelog entry

## Edge cases

**No type prefix:** Commit message does not follow conventional commit format. Mark as `skipped_commit` in receipt. Do not infer type from subject text.

**Multiple types in one commit:** Not valid conventional commit format. Mark as skipped.

**Scoped `docs` commits:** Include only when the scope suggests user-facing documentation: `docs(readme)`, `docs(api)`, `docs(guide)`. Exclude: `docs(internal)`, `docs(architecture)`.

**Merge commits:** Exclude. Merge commits describe the merge operation, not the feature. The individual commits in the merge are already processed.

**Revert commits:** Format is `revert: {original subject}`. Include as a `Removed` or `Changed` entry when the reverted commit was user-facing.

## Commit range

`git log {from_ref}..{to_ref}` — excludes the from_ref commit, includes the to_ref commit.

For tag-to-tag: `git log v1.1.0..v1.2.0` includes all commits between the two tags.

For branch-to-HEAD: `git log {last_release_tag}..HEAD`
