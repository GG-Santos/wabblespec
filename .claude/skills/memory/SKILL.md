---
name: memory
description: Primary evidence store. Write, read, and transition drawers in the WabbleSpec memory store (ChromaDB). All sourced facts live here. WabbleSpec adds staleness enforcement and receipt chain on top of the storage backend.
---

# Memory

You are the evidence store. You write facts, retrieve them on request, and maintain their trustworthiness over time via staleness state. You do not analyze or search evidence — that is MemorySearch. You do not record lineage — that is Provenance. You store and retrieve faithfully.

## Backend

WabbleSpec memory store — ChromaDB vector index + SQLite metadata. Memory path: `.wabblespec/memory/` (set via `WABBLESPEC_MEMORY_PATH` env var — see `modules/l5/memory/rules/memory-backend-config.md`).

Storage: ChromaDB at `.wabblespec/memory/chroma.sqlite3`.
KG: SQLite at `.wabblespec/memory/knowledge_graph.sqlite3` (owned by EntityGraph).

**Dependency:** shared internal package at `packages/memory/`. WabbleSpec modules must import through `_shared.memory_backend`, which configures the package before storage access.

## What this skill does

Three operations: **Write** (create or update a drawer), **Read** (return content with staleness state), **Transition** (apply a staleness state change). All operations go through `get_collection()`. WabbleSpec adds staleness metadata fields, receipt writing, and Provenance notification on top.

## When to use / when not to use

**Use when:**
- Any module needs to store a sourced fact
- Any module needs to retrieve a specific drawer by ID
- A staleness transition event arrives (from Dream, Provenance, or explicit command)

**Do not use when:**
- Querying across drawers by topic or keyword — that is MemorySearch
- Recording lineage, cascade effects, or contradiction flags — that is Provenance

## WabbleSpec metadata extensions

Each drawer in ChromaDB carries these WabbleSpec-specific metadata fields:

```json
{
  "wabblespec_staleness_state": "FRESH | AGING | STALE | EXPIRED | NEEDS_REVERIFICATION | SUPERSEDED",
  "wabblespec_confidence": 0.9,
  "wabblespec_expires_at": "2026-06-21T00:00:00Z",
  "wabblespec_source_module": "module-id",
  "wabblespec_schema_version": 1,
  "wabblespec_superseded_by": null,
  "wabblespec_drawer_id": "drawer_{wing}_{room}_{slug}_{timestamp}",
  "wabblespec_topic": "string"
}
```

Prefixed `wabblespec_` to avoid collisions with ChromaDB native fields (`wing`, `room`, `filed_at`).

## How to do it

### Write path

```python
from _shared.memory_backend import get_collection
import os

col = get_collection()

# Build metadata with WabbleSpec extensions
drawer_id = f"drawer_{wing}_{room}_{topic_slug}_{timestamp_compact}"
metadata = {
    "wing": wing,
    "room": room,
    "wabblespec_drawer_id": drawer_id,
    "wabblespec_topic": topic,
    "wabblespec_staleness_state": "FRESH",
    "wabblespec_confidence": confidence,
    "wabblespec_expires_at": expires_at_iso,
    "wabblespec_source_module": source_module,
    "wabblespec_schema_version": CURRENT_SCHEMA_VERSION,
    "filed_at": datetime.now(timezone.utc).isoformat(),
}

# Check for existing drawer on same topic in same wing/room
existing = col.get(where={"wing": wing, "room": room}, limit=50)
existing_ids = existing.ids if hasattr(existing, "ids") else existing.get("ids", [])
existing_metas = existing.metadatas if hasattr(existing, "metadatas") else existing.get("metadatas", [])

match_id = None
for i, m in enumerate(existing_metas):
    if m.get("wabblespec_topic", "").lower() == topic.lower():
        match_id = existing_ids[i]
        break

if match_id:
    staleness = existing_metas[i].get("wabblespec_staleness_state")
    if staleness in ("SUPERSEDED", "EXPIRED"):
        # Mark old as SUPERSEDED, write new
        col.update(ids=[match_id], metadatas=[{
            "wabblespec_staleness_state": "SUPERSEDED",
            "wabblespec_superseded_by": drawer_id,
        }])
        col.add(ids=[drawer_id], documents=[content], metadatas=[metadata])
    else:
        # Update content only — preserve staleness state
        col.update(ids=[match_id], documents=[content])
else:
    col.add(ids=[drawer_id], documents=[content], metadatas=[metadata])
```

After write: notify Provenance, write memory-write receipt.

### Read path

```python
r = col.get(where={"wabblespec_drawer_id": drawer_id})
if not (r.ids if hasattr(r, "ids") else r.get("ids", [])):
    raise DrawerNotFound(drawer_id)

meta = r.metadatas[0] if hasattr(r, "metadatas") else r["metadatas"][0]
content = r.documents[0] if hasattr(r, "documents") else r["documents"][0]
staleness = meta.get("wabblespec_staleness_state", "FRESH")

if staleness == "EXPIRED":
    raise StalenessViolation(f"drawer {drawer_id} is EXPIRED — cannot return content")
if staleness == "SUPERSEDED":
    superseded_by = meta.get("wabblespec_superseded_by")
    raise SupersededError(f"use drawer {superseded_by} instead")

return {"evidence": content, "staleness_state": staleness,
        "confidence": meta.get("wabblespec_confidence", 1.0)}
```

### Transition path

```python
col.update(ids=[drawer_id], metadatas=[{"wabblespec_staleness_state": to_state}])
```

If `to_state == "EXPIRED"`: update metadata. Drawer stays in ChromaDB for audit — search filters via `wabblespec_staleness_state != EXPIRED`.

## Output contract

**memory-write receipt** (`.wabblespec/receipts/memory-write-{timestamp}.json`):

```json
{
  "drawer_id": "string",
  "operation": "write | update | read | transition",
  "topic": "string",
  "wing": "string",
  "room": "string",
  "staleness_before": "string or null",
  "staleness_after": "string",
  "provenance_notified": true,
  "backend": "memory/chromadb"
}
```

## Common failure modes

1. **`WABBLESPEC_MEMORY_PATH` not set.** The memory store may write outside `.wabblespec/memory/`. Import `_shared.memory_backend` before storage access, or run `scripts/memory-bootstrap.py` for compatibility entry points. See `modules/l5/memory/rules/memory-backend-config.md`.

2. **Writing without notifying Provenance.** Every write requires Provenance notification — cascade computation depends on it.

3. **Resetting staleness to FRESH on update.** Updating evidence content does not reset staleness. Only explicit re-verification justifies FRESH.

4. **Returning EXPIRED content.** `wabblespec_staleness_state == EXPIRED` means STALENESS_VIOLATION. Return the error. Never return the content.

## Runtime memory retrieval (how CLAUDE.md memories are loaded)

The runtime separately manages a `memdir` system that loads files from the project's memory directory into the context window each turn. This is distinct from WabbleSpec's ChromaDB drawer store — it operates on flat files, not vectors.

**Retrieval algorithm (derived from production source, 2026-05-26):**

1. Scan memory file headers from the memory directory. Read filename and description (frontmatter) from each file. MEMORY.md (the index) is excluded — it is already in the system prompt.
2. Filter out files already surfaced in prior turns of the current session (`alreadySurfaced` set).
3. Send the remaining file manifest plus the user's query to a side-query model call (Sonnet). Ask the model to select up to 5 files that are clearly relevant.
4. Selection criteria: only files where relevance to the query is certain. Uncertain relevance → do not include.
5. Suppress reference/API documentation files for tools that were recently used (the conversation already contains working usage). Exception: always include warnings, gotchas, and known-issues files even for recently-used tools.
6. On error or abort: return empty set (fail-open, not fail-closed).
7. Thread `mtime` through with each result so callers can display freshness.

**Implications for drawer content design:**

- MEMORY.md descriptions are the primary retrieval signal. A file with a vague description is less likely to be selected. Write descriptions as precise retrieval keys: "Auth token refresh failure patterns in the WabbleSpec hook system" beats "Notes on hooks".
- The selector has a 5-file budget per turn. Files compete. High-specificity descriptions win over general ones.
- Reference/API docs that duplicate active tool schema are suppressed when that tool is in use. Design general reference docs to focus on gotchas and edge cases that are most useful when the tool is already being exercised.
- WabbleSpec drawer IDs (`drawer_{wing}_{room}_{slug}_{timestamp}`) are stored in ChromaDB, not in the memdir system. The two systems serve different retrieval patterns: memdir selects context-relevant files per turn; ChromaDB enables semantic search across all stored evidence.

## Reference

`modules/l5/memory/rules/memory-backend-config.md` (setup + bootstrap), `modules/l5/memory/rules/staleness-thresholds.md` (state transition rules), `modules/l5/memory/rules/schema-version.md` (current schema version), `_shared/references/compaction-behavior.md` (CLAUDE.md files excluded from post-compact file re-injection — memory is handled separately).
