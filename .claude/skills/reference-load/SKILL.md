---
name: reference-load
description: Bounded reference loader. Produces a trust-rated, staleness-tagged reference card for one external or internal source before any module uses it as evidence. Prevents raw repo dumping into context.
---

# ReferenceLoad

You are the intake gate for external and internal references. No module reads a reference without going through you first. You produce a bounded reference card — not a raw file dump. Your output lives as a FRESH memory drawer and a reference receipt.

## What this skill does

Takes one reference source (path, URL, or known reference id). Reads the project map or directory structure first to understand scope. Extracts only the concepts, contracts, or evidence relevant to the named purpose. Writes a reference card drawer to Memory. Returns the drawer id and path. Writes a receipt.

## When to use / when not to use

**Use when:**
- Any module needs to load an external or internal reference before planning or executing
- Explicit `/reference-load <source> <purpose>` command
- Explore or Recipe identify a reference that needs trust-rating before use

**Do not use when:**
- Reference was already loaded this session and drawer staleness is FRESH (check index first)
- Source is a live runtime system — use RuntimeProbe instead
- Source is project memory — use MemorySearch instead

## Inputs

- `source`: path or known reference id (e.g. `C:\Vaults\references\Core Project References\cartographer-main`)
- `purpose`: one sentence — what concept or contract to extract
- `trust_level`: `HIGH` | `MEDIUM` | `LOW` (default: `MEDIUM`)
  - HIGH: canonical, stable, authored by known authority
  - MEDIUM: useful but may be opinionated or partially stale
  - LOW: exploratory, possibly outdated, external origin unknown
- Optional: `map_first: true` — read project-map or directory listing before any file (default: true)
- Optional: `output_mode: "inline" | "pointer"` (default: `"inline"`)
  - `inline` — existing behavior: extract concepts, load content into context, write drawer
  - `pointer` — write drawer (evidence chain preserved) but do not inject drawer content into current context; return `@<drawer_path>` citation instead. Use when building a spec artifact that needs to cite a reference without consuming context budget for the full content.

## How to do it

### Step 1 — Deduplicate check

Read `.wabblespec/state/memory/index.json`. Search for an existing FRESH drawer whose topic matches this source + purpose combination. If found: return that drawer id. Do not load again. Write a receipt noting dedup hit.

### Step 2 — Map the source

If `map_first: true` (default):
- For a local path: list the top-level directory. Read any `README.md`, `project-map.md`, or `CLAUDE.md` present. Do not read raw source files yet.
- For a URL: fetch the landing page or index only.

Record: confirmed path, top-level structure, any project-map or summary doc found.

Do not read more than 3 files at this stage.

### Step 3 — Extract concepts (bounded read)

Navigate to the exact paths relevant to `purpose`. Read only those files. Maximum 5 files per reference-load invocation.

If more than 5 files are needed to answer `purpose`: scope down. A single reference-load must produce one reference card, not a whole-repo survey. Call reference-load again for additional concepts.

Concepts to extract:
- Core contract, schema, or API surface relevant to purpose
- Assumptions and constraints that affect WabbleSpec integration
- Known risks or stale areas
- Exact file paths used as evidence

Concepts to exclude:
- Generated artifacts (dist/, build/, .npmrc, eval-workspace, private journals)
- Content unrelated to `purpose`
- Duplicate signal from a reference already loaded

### Step 4 — Write reference card to Memory

Write a memory drawer to `.wabblespec/state/memory/` with:
```json
{
  "id": "<source-slug>-<purpose-slug>-<YYYYMMDD>",
  "topic": "<source> — <purpose>",
  "wing": "references",
  "room": "<source-slug>",
  "staleness_state": "FRESH",
  "trust_level": "<HIGH|MEDIUM|LOW>",
  "source_path": "<exact path or URL>",
  "purpose": "<purpose statement>",
  "evidence_files": ["<path1>", "<path2>"],
  "concepts": [
    {
      "name": "<concept name>",
      "summary": "<one paragraph>",
      "wabble_adaptation": "<how WabbleSpec uses this — not copies this>"
    }
  ],
  "risks": ["<risk 1>", "<risk 2>"],
  "do_not_copy": ["<pattern or content to exclude>"],
  "confidence": 0.0,
  "written_at": "<ISO-8601>"
}
```

Confidence scoring:
- 1.0: source is canonical, all relevant files read, no ambiguity
- 0.8–0.9: source is good, minor gaps or one uncertain file
- 0.6–0.7: source useful but clearly partial or possibly stale
- Below 0.6: flag LOW trust, note what is missing

Notify Provenance of the write.

### Step 4b — Pointer mode output

If `output_mode` is `"pointer"`:
- Do not surface drawer content into current context
- Return: `Reference loaded. Cite as: @<drawer_path> — <one-sentence summary of what the drawer contains>`
- Proceed to Step 5

If `output_mode` is `"inline"` (default): proceed to Step 5 normally — drawer content has already been loaded into context via Steps 3-4.

Pointer mode use cases:
- Specify building a task card that cites multiple references — register evidence without consuming context per file
- Decompose building a wave plan that references standards — cite for Executor to load on-demand
- Any module in GOOD or DEGRADING context budget tier that needs to register evidence without expanding the window

### Step 5 — Write receipt

```json
{
  "module": "reference-load",
  "layer": "L1",
  "source": "<source path or id>",
  "purpose": "<purpose>",
  "trust_level": "<HIGH|MEDIUM|LOW>",
  "drawer_id": "<id written>",
  "drawer_path": "<relative path>",
  "files_read": ["<list>"],
  "dedup_hit": false,
  "output_mode": "inline",
  "cited_as": null,
  "status": "PASS",
  "not_tested": ["<anything not read due to scope limit>"],
  "confidence": 0.0
}
```

## Output contract

**Reference card drawer** in `.wabblespec/state/memory/wings/references/rooms/<source-slug>/drawers/<id>.json`

**Memory index** updated: `index.json` entry added.

**Reference receipt** at `.wabblespec/state/receipts/reference-load-<source-slug>-<timestamp>.json`

## Common failure modes

1. **Loading full repo instead of named paths.** Step 2 reads the map. Step 3 reads exact files. Never `ls -r` an entire reference repo into context. If the purpose cannot be satisfied in 5 files, the purpose is too broad — split it.

2. **Skipping dedup check.** If reference-load ran for the same source + purpose this session, the drawer already exists. Re-loading wastes context and creates duplicate drawers that provenance must mark SUPERSEDED.

3. **Trust level inflation.** A reference from an external repo is MEDIUM at best unless it is explicitly canonical (Anthropic docs, IETF spec, official SDK). Do not mark community projects HIGH without rationale.

4. **Mixing concepts from multiple sources into one card.** One reference-load = one source + one purpose = one drawer. Cross-source synthesis is Recipe or Explore's job, not ReferenceLoad.

5. **Reading `.npmrc`, private journals, eval workspaces, or generated bundles.** These are explicitly out of scope for all reference loads. If a reference path leads there: stop, note it in `do_not_copy`, proceed without reading.
