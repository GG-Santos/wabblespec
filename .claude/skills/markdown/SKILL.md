---
name: markdown
description: Obsidian-compatible markdown output formatter. Converts raw content into structured, link-rich, frontmatter-correct markdown.
layer: L6
---

# Markdown

You format. The content already exists. Your job is to make it navigable, linkable, and structurally correct for the target vault or platform.

## What this skill does

Markdown takes a content artifact and applies structured formatting: frontmatter, heading hierarchy, wikilinks, callouts, and syntax that renders correctly in Obsidian and is compatible with agentskills.io output conventions. It does not edit content meaning. It applies formatting.

## When to use

Markdown is invoked:
- In the Polish pipeline: after Proofread, before delivery
- When any module produces content that will land in an Obsidian vault
- When producing output for agentskills.io or WabbleSpec's own documentation
- Explicitly by human on raw content that needs formatting

## Inputs

- **Artifact path** — path to the content file to format (required)
- **Target format** — `obsidian` | `agentskills` | `plain` (default: obsidian)
- **Note type** — for Obsidian: `spec`, `receipt`, `reference`, `log`, `decision`, `template` (determines frontmatter fields)
- **Link targets** — list of note titles or paths that this note should wikilink to (optional)
- **Vault root** — root path for resolving wikilink targets (optional; default: `.wabblespec/`)

## Output contract

**Receipt:** `.wabblespec/receipts/markdown-{timestamp}.json`

```json
{
  "source_path": "string",
  "output_path": "string",
  "target_format": "obsidian",
  "note_type": "string",
  "frontmatter_added": true,
  "links_inserted": 0,
  "callouts_added": 0,
  "heading_levels_normalized": true,
  "verdict": "PASS | FAIL",
  "formatted_at": "ISO-8601"
}
```

**Output file:** Written to the same path as the source unless `--output` is specified. Original content preserved in `.wabblespec/captures/pre-markdown-{timestamp}.txt`.

## Steps

**Step 1 — Read and classify content.**
Load the source artifact. Detect heading hierarchy, code blocks, list structures, and any existing frontmatter. If frontmatter exists, preserve its values; add missing fields.

**Step 2 — Apply frontmatter.**
Write or complete frontmatter based on note type (see `rules/obsidian-format.md`). Required frontmatter fields vary by note type.

**Step 3 — Normalize heading hierarchy.**
Document must start at H1. Sub-sections at H2. Sub-sub-sections at H3. No heading level should be skipped. If content uses H3 without H2, promote. If content uses multiple H1s, demote all but the first to H2.

**Step 4 — Insert wikilinks.**
For each declared link target: scan the document for the first mention of that title or a canonical alias. Wrap it with `[[target]]` syntax. Do not duplicate wikilinks within the same paragraph.

For agentskills format: convert wikilinks to markdown hyperlinks with relative paths.

**Step 5 — Apply callouts.**
Identify content blocks that match callout patterns (notes, warnings, tips, examples). Format using Obsidian callout syntax: `> [!TYPE]`. See `rules/obsidian-format.md` for type mapping.

**Step 6 — Write output.**
Save formatted file. Write receipt.

## Failure modes

**Overwriting custom frontmatter:** If the source already has frontmatter fields with valid values, preserve them. Only add missing fields.

**Breaking code blocks:** Heading normalization must not modify content inside fenced code blocks. Always detect ` ``` ` fences before applying heading transformations.

**Incorrect wikilink scope:** Only link to declared targets. Do not speculatively add links to terms that happen to match file names.
