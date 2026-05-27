# Acceptance Tests — Markdown (L6)

## AT-MD-01: Three target formats supported

**Given** a Markdown invocation
**When** a target format is declared
**Then** the following are supported:
- `obsidian` — wikilinks, callouts, frontmatter
- `agentskills` — WabbleSpec module format conventions
- `plain` — standard markdown, no platform-specific extensions

---

## AT-MD-02: Existing frontmatter values preserved

**Given** a file with existing frontmatter
**When** Markdown processes the file
**Then** existing frontmatter values are preserved; Markdown only adds missing required fields, it does not overwrite existing values

---

## AT-MD-03: Processing steps run in order

**Given** a Markdown invocation
**When** execution runs
**Then** steps execute in order: classify -> frontmatter -> heading normalization -> wikilinks -> callouts -> write

---

## AT-MD-04: Receipt confirms format and output path

**Given** a completed Markdown run
**Then** the receipt at `.wabblespec/state/receipts/markdown-{timestamp}.json` contains:
- `target_format`
- `artifact_path`
- `output_path`
- `frontmatter_added`
- `headings_normalized`
- `verdict`
