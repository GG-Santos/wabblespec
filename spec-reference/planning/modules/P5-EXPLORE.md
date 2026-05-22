# Module Plan — Explore (L1)

**Tier:** 2 — CORE
**Layer:** L1 Spec Core
**v5.3 origin:** Explore module — graph-first orientation, standards discovery

---

## Purpose

Orient to the current project state. Map what exists before any planning or execution begins. Runs in the Research phase alongside ReferenceLoad and MemorySearch. Explore discovers — it does not invent. Output is a factual project map based on what is actually present, not what is expected.

---

## Activation

`skill-rules.json` triggers:
- Research phase start (every Research phase runs Explore)
- P2 stage (architecture requires knowing current system state)
- Explicit `/explore` command
- Ground detects drift and requests re-exploration

---

## Exploration Axes

| Axis | What Explore maps |
|---|---|
| File structure | Directory layout, file types, entry points, config files |
| Technology stack | Languages, frameworks, build tools, package managers detected |
| Existing specs | Design documents, specs, standards already present |
| Conventions | Naming patterns, folder organization, comment style, test structure |
| Integration points | APIs consumed, external services, database connections evident |
| Git state | Recent commits, active branches, uncommitted changes |
| Standards | AGENT.md, CLAUDE.md, .editorconfig, linting rules, CI config |
| Known gaps | Missing specs, missing tests, incomplete scaffolding |

---

## Graph-First Traversal

Explore builds a relationship graph before reading individual files. Traversal order:

```
1. Read directory tree (structure only — no file content yet)
2. Identify high-value nodes: entry points, config files, spec files, test files
3. Read high-value nodes first
4. Follow import/dependency graph from entry points
5. Read referenced files in dependency order
6. Stop when graph is sufficiently mapped (not exhaustive)
```

Explore does not read every file. It reads enough to produce an accurate map. Deep files are only read if they are high-value nodes or directly imported by explored code.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Project map | `.wabblespec/project-map.md` | Current state summary for all modules |
| Explore receipt | `.wabblespec/receipts/explore-receipt.md` | I10 compliance |

### project-map.md structure

```markdown
# Project Map

**explored_at:** timestamp
**target:** build target from recipe.json
**confidence:** 0.0-1.0

## File Structure

<directory tree summary — not exhaustive>

## Technology Stack

| Layer | Technology | Detected From |
|---|---|---|
| Language | TypeScript | package.json, .ts files |
| Framework | Next.js | next.config.js, app/ directory |

## Existing Specs

| Spec | Location | Stage | Staleness |
|---|---|---|---|

## Conventions Detected

- Naming: <pattern>
- Test location: <pattern>
- Import style: <pattern>

## Integration Points

- <external service>: <how detected>

## Git State

- Branch: <name>
- Uncommitted changes: <count>
- Last commit: <message>

## Standards Files

| File | Purpose |
|---|---|
| AGENT.md | Project conventions |

## Known Gaps

- <missing spec or structure>
```

---

## Workflow

```
1. Read recipe.json for build target

2. Build directory tree (structure only)

3. Identify high-value nodes per target:
   -> Web: package.json, index.html, app/, pages/, src/
   -> API/Service: main entry, routes/, handlers/, openapi.yaml
   -> Game: project.godot or Assets/, GDD.md
   -> [per target — see rules/high-value-nodes.md]

4. Read high-value nodes

5. Follow import/dependency graph from entry points (bounded depth)

6. Detect technology stack from config files and imports

7. Scan for existing spec artifacts

8. Detect conventions (naming, structure, test patterns)

9. Check git state (status, recent log)

10. Identify known gaps (missing specs, missing tests)

11. Write project-map.md

12. Write Explore receipt

13. Write project map to Memory as FRESH drawer (topic: project-state)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over project-map.md |
| `scripts/graph-traverse.py` | Script | Deterministic dependency graph traversal (from _shared/scripts/) |
| `rules/high-value-nodes.md` | Rules | Per-target high-value node definitions |
| `rules/exploration-bounds.md` | Rules | When to stop — depth limits, file size limits |
| `schemas/project-map.schema.json` | Schema | project-map.md header validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | Reads build target from recipe.json to select high-value nodes |
| Memory | Writes project-map as FRESH drawer |
| MemorySearch | Later queries can retrieve project-map drawer |
| ReferenceLoad | Runs in parallel in Research phase — both feed the Research receipt |
| Specify | Reads project-map to ground spec in actual project state |
| Decompose | Reads project-map to size wave plans against actual codebase |
| Ground | Reads project-map to detect drift between map and current state |
| Scaffold | Reads project-map to avoid overwriting existing conventions |

---

## Verification Mode

**Observation** — project-map.md exists, technology stack section populated, git state present, Memory drawer written, receipt written.

---

## Receipt Extension Fields

```json
{
  "files_read": "integer",
  "directories_scanned": "integer",
  "stack_detected": "array of strings",
  "existing_specs_found": "integer",
  "known_gaps_found": "integer",
  "git_state_read": "boolean",
  "memory_drawer_written": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 Explore | v6.1 Explore |
|---|---|
| Orient to project, graph-first | Same |
| Standards discovery | Same — extended to detect more convention types |
| No project-map.md output | project-map.md produced and written to Memory |
| No per-target high-value nodes | Per-target node definitions added (11 targets) |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Exploration depth limit | 3 levels from entry point (proposed) vs. configurable | Per-module planning |
| Re-exploration trigger | Ground-only vs. any file change above threshold | Per-module planning |
| project-map.md staleness | FRESH on write, AGING after N commits | Per-module planning |
