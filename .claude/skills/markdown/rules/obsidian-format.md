# Obsidian Format

Obsidian-compatible markdown formatting rules.

## Frontmatter

All notes in an Obsidian vault require YAML frontmatter. Required fields by note type:

| Note type | Required fields |
|---|---|
| `spec` | `name`, `status`, `created`, `layer` |
| `receipt` | `module`, `status`, `created`, `task_id` |
| `reference` | `title`, `domain`, `consumers` |
| `log` | `type`, `created`, `session_id` |
| `decision` | `title`, `status`, `created`, `tags` |
| `template` | `name`, `version`, `applies_to` |

Status values: `draft`, `active`, `archived`, `superseded`.

## Heading hierarchy

- H1 (`#`): document title — exactly one per document
- H2 (`##`): major sections
- H3 (`###`): sub-sections
- H4 (`####`): used sparingly for deep nesting; never H5 or H6 in normal documents

No heading level may be skipped. H3 may not appear without a parent H2.

## Wikilinks

- Wikilinks: `[[Note Title]]`
- Wikilinks with display text: `[[Note Title|display text]]`
- Wikilinks to headers: `[[Note Title#Section Header]]`
- Link on first mention per section only — do not repeat wikilinks within the same paragraph

## Callout syntax

Obsidian callout format: `> [!TYPE] Optional Title`

| Content pattern | Callout type |
|---|---|
| Important note, must-read | `NOTE` |
| Best practice, recommendation | `TIP` |
| Risk, caution, potential issue | `WARNING` |
| Error, required action | `DANGER` |
| Example, illustration | `EXAMPLE` |
| Quote attribution | `QUOTE` |

## Code blocks

Always use fenced code blocks with language specifier:
````
```python
code here
```
````

Never use indented code blocks (4 spaces) — Obsidian renders them inconsistently.

## Tables

Tables require a header row and alignment row. Cell padding is optional but consistent:
```
| Column A | Column B |
|---|---|
| value | value |
```

## Line breaks

Obsidian renders single newlines as spaces (CommonMark). To force a line break within a paragraph: two trailing spaces or a backslash `\` at the end of the line.
