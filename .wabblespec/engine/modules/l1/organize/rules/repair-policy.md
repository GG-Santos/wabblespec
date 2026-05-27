# Repair Policy

Organize classifies actions as auto-repair or human-confirm. Auto-repair is conservative. When uncertain, require confirmation.

## Auto-repair allowed

The following actions may be taken without human confirmation:

| Action | Condition |
|---|---|
| Create missing directory | Directory is declared in framework.yaml but absent |
| Normalize file name casing | File has wrong case but content is valid (rename only) |
| Remove empty directories | Directory contains zero files and is not declared as a module path |
| Add missing frontmatter | SKILL.md is missing `name:` or `description:` frontmatter — derive from filename and first heading |

## Human confirmation required

The following actions must be listed in `actions_requiring_confirmation` and must NOT be taken without explicit human input:

| Action | Reason |
|---|---|
| Delete any non-empty file | May be referenced elsewhere; human must verify |
| Move a file across module boundaries | May break references, schema `$ref` paths, or SKILL.md pointers |
| Rename a schema file | May break `$ref` chains across multiple modules |
| Rename a module directory | framework.yaml path field would be invalidated |
| Delete an orphan file | May be intentional — orphan status could be stale |
| Merge duplicate files | Content merge decisions require human review |

## Report format

Organize writes a repair report to `.wabblespec/organize/report-<timestamp>.md` listing:

1. **Auto-repairs completed** — actions taken, before/after state
2. **Requiring confirmation** — list of paths with action proposed and reason
3. **No action needed** — dimensions with zero findings

## Confirmation protocol

When Organize surfaces items requiring confirmation, it does not proceed. It halts and waits. Once human confirms (or rejects) each item, Organize applies only the confirmed actions and writes a second receipt marking confirmed actions as complete.
