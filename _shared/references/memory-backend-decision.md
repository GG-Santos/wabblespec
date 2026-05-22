---
name: memory-backend-decision
description: Formal decision record for WabbleSpec memory storage backend. Approved 2026-05-22: mempalace/ChromaDB IS the backend. Documents alternatives considered, rationale, dependency contract, and rollback path.
decision_date: 2026-05-22
status: LOCKED
---

# Memory Backend Decision Record

**Decision:** mempalace Python package with ChromaDB vector index as the WabbleSpec evidence storage backend.  
**Status:** LOCKED — approved 2026-05-22.  
**Authority:** BUILD-PLAN.md Gap 2 resolution; modules/l5/memory/SKILL.md; modules/l5/memory-search/SKILL.md.

## Decision

mempalace IS the storage backend. This is not an adaptation of mempalace patterns — the mempalace `Palace` API is called directly. WabbleSpec adds staleness enforcement, receipt chain, and single-project isolation on top of mempalace storage.

**Stack:**
```
WabbleSpec enforcement (hooks, receipts, phase gates, staleness states)
        ↓
mempalace Python API  (Palace, KnowledgeGraph, Miner)
        ↓
ChromaDB (semantic vector search) + SQLite (temporal KG)
```

## Alternatives Considered

### Option A: Flat-JSON drawers (original WabbleSpec Phase 3 approach)

Drawer files at `.wabblespec/memory/wings/{wing}/rooms/{room}/drawers/{id}.json`. Index at `.wabblespec/memory/index.json`.

**Pros:** Zero dependency, fully portable, human-readable, no install step.  
**Cons:** Search requires full-index scan or separate FTS index. No semantic recall — can only find drawers with exact keyword matches. As drawer count grows, scan performance degrades. MemorySearch built on this approach was replaced during BUILD-PLAN P1 because topic/staleness filters were slow and keyword-only.  
**Verdict:** Rejected. Insufficient for semantic evidence retrieval. Retained as the underlying file format mempalace writes to — not the query interface.

### Option B: SQLite FTS5 (context-mode-main approach)

SQLite FTS5 BM25-ranked search, chunked by markdown headings, stored in local `.sqlite` file.

**Pros:** No embeddings required, exact-text recall, BM25 ranking is deterministic and explainable, single-file database, no external service.  
**Cons:** Keyword-only — "authentication flow" does not find a drawer about "OAuth token handling" unless those exact words appear. Requires separate index management from the raw drawer files. Context-mode-main uses this for documentation and API references where exact text is the retrieval goal. WabbleSpec drawers contain conceptual evidence where semantic similarity matters more than exact keyword match.  
**Verdict:** Rejected as primary backend. FTS5 approach is appropriate for exact-text documentation retrieval, not conceptual evidence search. Retained as a reference for future fallback design if ChromaDB proves unavailable.

### Option C: mempalace/ChromaDB (SELECTED)

mempalace `Palace` API with ChromaDB vector index for semantic search. SQLite for entity knowledge graph.

**Pros:** Semantic search finds conceptually related drawers even when exact keywords don't match. Drawer hierarchy (wings/rooms) maps directly to WabbleSpec's evidence taxonomy. mempalace is already running in this workspace via the session MCP server. Single-project isolation achieved by redirecting all palace paths to `.wabblespec/memory/`. Staleness metadata stored as `wabblespec_*` fields in ChromaDB metadata.  
**Cons:** Requires `pip install mempalace`. ChromaDB embeds locally via sentence-transformers on first use (one-time download). Adds a Python dependency.  
**Verdict:** Selected.

## Dependency Contract

**Package:** `pip install mempalace`  
**Python:** 3.10+  
**Palace path:** `.wabblespec/memory/` — set via `MEMPALACE_PALACE_PATH` environment variable  
**Config reference:** `modules/l5/memory/rules/mempalace-config.md`  
**Initialisation:** `scripts/wabblespec-mempalace-bootstrap.py` redirects all global `~/.mempalace/` paths to `.wabblespec/memory/` for single-project isolation  

**Single-project isolation patches:**
- `hallways._HALLWAY_FILE` → `.wabblespec/memory/hallways.json`
- `palace_graph._TUNNEL_FILE` → `.wabblespec/memory/tunnels.json`
- PID files → `.wabblespec/memory/.hook_state/`
- ConvoMiner scoped to current project's Claude Code sessions only

**WabbleSpec metadata extensions** (prefixed to avoid collision with mempalace native fields):
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

If mempalace/ChromaDB becomes unavailable or breaks:

1. **Immediate fallback:** All drawer content is written to `.wabblespec/memory/` as files by mempalace — these exist regardless of whether ChromaDB is queryable. Drawers can be read by ID from the filesystem without mempalace.
2. **Search fallback:** Add a `grep`-based staleness-aware search script over drawer files. No semantic ranking — keyword match only. Acceptable for emergency retrieval.
3. **Full migration:** Port to SQLite FTS5 (context-mode-main pattern) if semantic search requirements change. Schema is stable — `wabblespec_*` metadata fields translate to SQLite columns. Migration script path: `project/repo/scripts/migrate/memory-to-fts5.py`.

Rollback does not require changing module SKILL.md files. Only the bootstrap script and MemorySearch query execution change.

## What This Decision Does NOT Cover

- L8 Evolution modules (Instinct, Synth, Benchmark) — gated on 100+ real receipts, separate decision required
- Embedding model selection — mempalace handles internally; WabbleSpec does not pin a model
- MemPalace version pinning — use latest stable; pin if a breaking change forces it
- EntityGraph schema — covered by EntityGraph module; uses mempalace KnowledgeGraph API but has separate decision authority

## Stale References to Update

The following references in planning documents used early-phase language ("adapt without ChromaDB") that predates this decision. They are informational artifacts, not authority:

- `BUILD-PLAN.md` Reference Material table: "Drawer hierarchy, SQLite entity pattern (adapt without ChromaDB)" → updated to reflect approved integration
- `spec-reference/planning/modules/P2-MEMORY.md` if it contains flat-JSON-only design (informational only — SKILL.md is authority)
