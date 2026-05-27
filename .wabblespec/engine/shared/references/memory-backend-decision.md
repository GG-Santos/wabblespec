---
name: memory-backend-decision
description: Formal decision record for WabbleSpec memory storage backend. Approved 2026-05-22: WabbleSpec Memory/ChromaDB IS the backend. Documents alternatives considered, rationale, dependency contract, and rollback path.
decision_date: 2026-05-22
status: LOCKED
---

# Memory Backend Decision Record

**Decision:** WabbleSpec Memory Python package with ChromaDB vector index as the WabbleSpec evidence storage backend.  
**Status:** LOCKED — approved 2026-05-22.  
**Authority:** BUILD-PLAN.md Gap 2 resolution; modules/l5/memory/SKILL.md; modules/l5/memory-search/SKILL.md.

## Decision

The shared internal `memory` package is the storage backend. WabbleSpec modules call `_shared.memory_backend`, which configures the package for project-local runtime behavior. WabbleSpec adds staleness enforcement, receipt chain, and single-project isolation on top of storage.

**Stack:**
```
WabbleSpec enforcement (hooks, receipts, phase gates, staleness states)
        ↓
memory Python API  (collection facade, KnowledgeGraph, Miner)
        ↓
ChromaDB (semantic vector search) + SQLite (temporal KG)
```

## Alternatives Considered

### Option A: Flat-JSON drawers (original WabbleSpec Phase 3 approach)

Drawer files at `.wabblespec/memory/wings/{wing}/rooms/{room}/drawers/{id}.json`. Index at `.wabblespec/memory/index.json`.

**Pros:** Zero dependency, fully portable, human-readable, no install step.  
**Cons:** Search requires full-index scan or separate FTS index. No semantic recall — can only find drawers with exact keyword matches. As drawer count grows, scan performance degrades. MemorySearch built on this approach was replaced during BUILD-PLAN P1 because topic/staleness filters were slow and keyword-only.  
**Verdict:** Rejected. Insufficient for semantic evidence retrieval. Retained as the underlying file format WabbleSpec Memory writes to — not the query interface.

### Option B: SQLite FTS5 (context-mode-main approach)

SQLite FTS5 BM25-ranked search, chunked by markdown headings, stored in local `.sqlite` file.

**Pros:** No embeddings required, exact-text recall, BM25 ranking is deterministic and explainable, single-file database, no external service.  
**Cons:** Keyword-only — "authentication flow" does not find a drawer about "OAuth token handling" unless those exact words appear. Requires separate index management from the raw drawer files. Context-mode-main uses this for documentation and API references where exact text is the retrieval goal. WabbleSpec drawers contain conceptual evidence where semantic similarity matters more than exact keyword match.  
**Verdict:** Rejected as primary backend. FTS5 approach is appropriate for exact-text documentation retrieval, not conceptual evidence search. Retained as a reference for future fallback design if ChromaDB proves unavailable.

### Option C: WabbleSpec Memory/ChromaDB (SELECTED)

WabbleSpec Memory facade with ChromaDB vector index for semantic search. SQLite for entity knowledge graph.

**Pros:** Semantic search finds conceptually related drawers even when exact keywords don't match. Drawer hierarchy (wings/rooms) maps directly to WabbleSpec's evidence taxonomy. WabbleSpec Memory is already running in this workspace via the session MCP server. Single-project isolation achieved by redirecting all memory paths to `.wabblespec/memory/`. Staleness metadata stored as `wabblespec_*` fields in ChromaDB metadata.  
**Cons:** ChromaDB embeds locally via sentence-transformers on first use (one-time download). Adds a local Python runtime dependency.  
**Verdict:** Selected.

## Dependency Contract

**Package:** `packages/memory/`  
**Python:** 3.10+  
**Memory path:** `.wabblespec/memory/` — set via `WABBLESPEC_MEMORY_PATH` environment variable  
**Config reference:** `modules/l5/memory/rules/memory-backend-config.md`  
**Initialisation:** `_shared.memory_backend` adds `packages/memory/src/`, calls `memory.runtime.configure_project()`, sets `WABBLESPEC_MEMORY_PATH`, and redirects runtime state to `.wabblespec/memory/.runtime/` for single-project isolation  
**Checkout launchers:** `scripts/memory.py` and `scripts/memory-mcp.py` run the CLI/MCP server without requiring editable install or console-script PATH setup.  
**MCP compatibility:** Tool identifiers remain `wabblespec_memory_*` even though the package and command surface are named `memory`.  

**Single-project isolation patches:**
- `hallways._HALLWAY_FILE` → `.wabblespec/memory/hallways.json`
- `palace_graph._TUNNEL_FILE` → `.wabblespec/memory/tunnels.json`
- PID files → `.wabblespec/memory/.runtime/hook_state/`
- ConvoMiner scoped to current project's Claude Code sessions only

**WabbleSpec metadata extensions** (prefixed to avoid collision with WabbleSpec Memory native fields):
```json
{
  "wabblespec_staleness_state": "FRESH | AGING | STALE | EXPIRED | NEEDS_REVERIFICATION | SUPERSEDED",
  "wabblespec_confidence": 0.9,
  "wabblespec_expires_at": "ISO-8601",
  "wabblespec_source_module": "module-id",
  "wabblespec_schema_version": 1,
  "wabblespec_superseded_by": null
}
```

## Rollback Path

If WabbleSpec Memory/ChromaDB becomes unavailable or breaks:

1. **Immediate fallback:** All drawer content is written to `.wabblespec/memory/` as files by WabbleSpec Memory — these exist regardless of whether ChromaDB is queryable. Drawers can be read by ID from the filesystem without WabbleSpec Memory.
2. **Search fallback:** Add a `grep`-based staleness-aware search script over drawer files. No semantic ranking — keyword match only. Acceptable for emergency retrieval.
3. **Full migration:** Port to SQLite FTS5 (context-mode-main pattern) if semantic search requirements change. Schema is stable — `wabblespec_*` metadata fields translate to SQLite columns. Migration script path: `project/repo/scripts/migrate/memory-to-fts5.py`.

Rollback does not require changing module SKILL.md files. Only the bootstrap script and MemorySearch query execution change.

## What This Decision Does NOT Cover

- L8 Evolution modules (Instinct, Synth, Benchmark) — gated on 100+ real receipts, separate decision required
- Embedding model selection — WabbleSpec Memory handles internally; WabbleSpec does not pin a model
- WabbleSpec Memory version pinning — use latest stable; pin if a breaking change forces it
- EntityGraph schema — covered by EntityGraph module; uses WabbleSpec Memory KnowledgeGraph API but has separate decision authority

## Stale References to Update

The following references in planning documents used early-phase language ("adapt without ChromaDB") that predates this decision. They are informational artifacts, not authority:

- `BUILD-PLAN.md` Reference Material table: "Drawer hierarchy, SQLite entity pattern (adapt without ChromaDB)" → updated to reflect approved integration
- `spec-reference/planning/modules/P2-MEMORY.md` if it contains flat-JSON-only design (informational only — SKILL.md is authority)
