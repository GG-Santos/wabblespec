---
name: explore
description: Graph-first codebase discovery. Traverses from high-value nodes (entry points, config files, test files, dependency manifests) to produce project-map.md. Writes findings to Memory as FRESH drawers. Notifies EntityGraph for entity extraction. Per-target traversal order follows platform conventions from the active L3 package.
---

# Explore

You build a structured map of the codebase before spec work or execution that depends on codebase understanding. You start at high-value nodes and traverse outward — you do not scan the entire repo blindly.

## What this skill does

Graph-first codebase discovery. Traverses from high-value nodes (entry points, config files, test files, dependency manifests) to produce project-map.md. Writes findings to Memory as FRESH drawers. Notifies EntityGraph for entity extraction. Per-target traversal order follows platform conventions from the active L3 package.

## When to use

- Research phase at session start for any execution involving existing code
- After Scaffold generates initial project structure
- When Autopilot detects project-map.md is STALE or EXPIRED
- Explicit `/explore` command

Active during Research phase only; invoke before execution waves begin.

## Traversal order

Start from high-value nodes. Per-target traversal order from the active L3 platform package. Default order when no platform package is active:

1. Dependency manifests (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `pom.xml`, etc.)
2. Entry points (main files, index files, app entry, server root)
3. Configuration files (env templates, build config, CI config)
4. Test files (test directory root, first test file as pattern signal)
5. High-churn files (git log: most frequently modified in last 30 commits)
6. Files referenced in spec artifacts (if P1–P4 exist)

Stop when: project-map.md captures enough to answer the current research question, OR all high-value nodes exhausted, OR Memory drawer count limit reached (default: 50 new drawers per Explore session).

## Freshness policy

Every project-map.md carries a `freshness_state` and `valid_until`. Explore sets these at write time. Downstream modules (ReferenceLoad, Decompose, Guard) check `freshness_state` before consuming the map.

| State | Condition | Consumer action |
|---|---|---|
| `FRESH` | Within `valid_until` window (default 24h from `explored_at`) | Load and use |
| `AGING` | 24–72h past `explored_at`, no structural change detected | Load with staleness noted |
| `STALE` | 72h+ elapsed, OR new packages added, OR entry-points changed | Trigger Explore re-run before planning |
| `EXPIRED` | Entry-points or tech-stack changed in git since last map | Block consumption — Explore re-run required |

Set `valid_until` to `explored_at + 24h` for most targets. High-churn projects (over 5 commits per day) may use 8h. Explore re-runs always write a new map and reset `freshness_state` to `FRESH`.

## Serena Semantic Enrichment (optional — when serena MCP is active)

When the `serena` MCP server is active, use its semantic navigation tools as the primary traversal mechanism for high-value node discovery — faster and more precise than grep-based traversal:

| Tool | Replaces | Use for |
|---|---|---|
| `serena_find_references <symbol>` | grep/Grep | Locating all callers of an entry point |
| `serena_go_to_definition <symbol>` | Manual import tracing | Resolving cross-module dependencies |
| `serena_list_symbols <file>` | Full file read | Extracting public API surface |
| `serena_search_codebase <query>` | Multi-grep passes | Semantic pattern discovery |

**When serena is active:** use these tools first for Steps 2 (entry points), 5 (high-churn files cross-reference), and 6 (spec-referenced files). Fall back to file reads when serena returns no results for a query.

**Traversal order change:** with serena, high-churn detection (Step 5) can use `serena_search_codebase` with an edit-frequency signal instead of `git log`. Report the method used in the project-map.md `conventions_observed` list.

**Record in project-map.md:**
- `serena_available: true` in the header block
- Add a `semantic_nav` entry to Impact Slices listing symbols discovered via serena with their reference counts

When serena is not active: proceed with standard Glob/Grep/Read traversal. Never block on serena availability.

## Reference Routing

| Situation | Reference |
|---|---|
| Explore receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |
| Serena MCP call patterns and tool list | `engine/shared/references/mcp-servers-integration.md` → Serena section |
| LSP availability by language | `engine/shared/references/lsp-integration.md` |

## Output contract

Write to `.wabblespec/state/plans/project-map.md`. Schema contract: `.wabblespec/engine/shared/schemas/project-map.schema.json`.

```markdown
# Project Map

**Explored at:** ISO 8601
**Build target:** string (from Recipe)
**Freshness state:** FRESH|AGING|STALE|EXPIRED
**Valid until:** ISO 8601 (explored_at + 24h default)
**Entry points:** [list]

## Tech Stack

| Area | Technology | Version | Confidence |
|---|---|---|---|
| runtime | Node.js | 20.x | exact |

## Spec Artifacts Found

| File | Artifact Type | Status |
|---|---|---|

## Conventions Observed

- <naming convention>
- <project structure pattern>
- <notable architectural pattern>

## Risk Files

| Path | Risk Reason | Notes |
|---|---|---|
| <path> | high-churn | <N> changes in last 30 commits |
| <path> | edit-warning | <annotation note> |
| <path> | no-tests | no test file references this path |
| <path> | cross-cutting | imported by >5 modules |

## Impact Slices

Named slices of this map. ReferenceLoad consumes these instead of raw file trees.

### Slice: entry-points
**Primary paths:** <ranked list of entry-point files>
**Test paths:** <test files covering entry points>
**Reason:** main application entry — read first for any execution-path question

### Slice: api-surface
**Primary paths:** <ranked list of public API/interface files>
**Test paths:** <test files covering API surface>
**Reason:** external contract — read for any spec or migration question

### Slice: test-coverage
**Primary paths:** <test directory root, key test files>
**Reason:** test posture — read before declaring verification mode

### Slice: risk
**Primary paths:** <paths from Risk Files table>
**Reason:** files requiring extra care before editing — feed to Executor wave planning

### Slice: conventions
**Primary paths:** <config files, linting rules, directory structure files>
**Reason:** project conventions — read before Specify or Clean

## Git State

**Active branch:** string
**Recent changes:** <files modified in last N commits>
**Uncommitted changes:** <count>

## Gaps

- <unknown area 1 — what Explore could not determine>
- <at least one gap is required — do not claim full coverage>
```

## Memory writes

For each distinct finding, write one Memory drawer as FRESH using `drawer-writer.py` — do not construct drawer JSON inline. One drawer per tech stack component, per convention, per architectural pattern, per gap identified (not one per file).

```bash
python .wabblespec/engine/shared/scripts/drawer-writer.py \
  --topic "<OBSERVATION_TYPE>: <finding>" \
  --wing implementation \
  --room <project-slug> \
  --evidence "<finding text>" \
  --confidence <0.6-0.9> \
  --staleness-state FRESH \
  --source "<file path that surfaced this finding>" \
  --source-module explore \
  --actor explore
```

Wing `implementation` for code/architecture findings; `decisions` for observed conventions. ID and output path are auto-derived.

Notify EntityGraph after all drawers written — pass list of entity candidates (file paths, module names, technology names) for extraction.

## What not to do

- Do not scan every file — traverse from high-value nodes only
- Do not write one drawer per file — write one drawer per distinct finding
- Do not run during active execution waves
- Do not block on incomplete traversal — write what is found, declare gaps
- Do not write project-map.md without `freshness_state` and `valid_until` — a map without these fields cannot be used as a reference slice
- Do not list individual files where a named impact slice suffices — slices are the consumption unit, not raw file lists
- Do not claim zero gaps — at least one gap entry is required to prevent false completeness
