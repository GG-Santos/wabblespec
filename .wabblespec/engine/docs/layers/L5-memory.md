# L5 — Memory

The memory and knowledge layer. L5 modules persist, retrieve, and evolve knowledge across sessions. They also manage the framework's self-reflection and structural awareness.

## Modules

| Module | Role |
|--------|------|
| `memory` | Core memory read/write. Manages the session memory store at `.wabblespec/memory/`. Writes to `index.json` and `tracker.json`. |
| `memory-search` | Semantic and keyword search over stored memory. Returns relevant entries ranked by relevance. |
| `memory-mine` | Extracts latent patterns from receipt history and session logs. Feeds candidates to Dream and Instinct. |
| `forget` | Explicit memory deletion. Requires human confirmation for CRITICAL-tier entries. Never auto-forgets. |
| `dream` | Post-wave reflection. Runs after each Executor wave. Extracts learnings, gaps, and surprises. Writes to `dream-log.json`. Feeds Instinct (L8) over time. |
| `nexus` | Cross-module coordination hub. Maintains awareness of which modules are active, what receipts are pending, and where the session currently is in the pipeline. |
| `entity-graph` | Tracks entities (people, systems, decisions) and their relationships across the project. Queryable by other modules. |
| `provenance` | Tracks the origin and transformation chain of any artifact. Answers "where did this come from?" for any output in the receipt chain. |

## Memory store layout

```
.wabblespec/memory/
  index.json          — module registry, session entry points
  tracker.json        — module performance tracking, run counts
  dream-log.json      — Dream module output across all waves
  gap-map.md          — identified gaps in spec or implementation
  staleness-map.md    — artifacts flagged as potentially stale
```

## Key behaviors

**Dream** runs automatically after each Executor wave when Autopilot is active. In manual sessions, `/dream` invokes it explicitly. Dream output is the primary source material for Instinct pattern extraction (L8).

**Provenance** maintains a cascade — every artifact can be traced to its source receipt and the module that produced it. The provenance cascade test (`.wabblespec/engine/shared/scripts/` — historical) verified the chain holds across all registered receipts.

**Memory-mine** is a batch analysis module. It processes the receipt index and dream log to find recurring patterns. Candidates surface to Dream for validation before Instinct receives them.

**Nexus** is the session coordinator. Other modules query Nexus to understand current pipeline position without re-reading all receipts. Nexus reads are cheap; direct receipt scans are expensive.

## Staleness

The staleness system flags memory entries and spec artifacts that may be outdated. `staleness-map.md` is updated by Dream after each wave. A STALENESS_VIOLATION is surfaced when a module is about to act on a flagged artifact without confirming currency.

## Layer rules

- Forget requires human confirmation for any entry tagged CRITICAL
- Dream never modifies `project/repo/` — it only writes to `.wabblespec/memory/`
- Provenance is append-only — never removes or modifies existing provenance entries
- Memory-mine is a read-only analysis module — it writes to Dream's input queue, not directly to memory
