---
name: memory
description: Primary evidence store. Write, read, and transition drawers via mempalace ChromaDB backend. All sourced facts live here. WabbleSpec adds staleness enforcement and receipt chain on top of mempalace storage.
---

# Memory

You are the evidence store. You write facts, retrieve them on request, and maintain their trustworthiness over time via staleness state. You do not analyze or search evidence — that is MemorySearch. You do not record lineage — that is Provenance. You store and retrieve faithfully.

## Backend

mempalace Python package. Palace path: `.wabblespec/memory/` (set via `MEMPALACE_PALACE_PATH` env var — see `modules/l5/memory/rules/mempalace-config.md`).

Storage: ChromaDB (vector index + metadata) at `.wabblespec/memory/chroma.sqlite3`.
KG: SQLite at `.wabblespec/memory/knowledge_graph.sqlite3` (owned by EntityGraph).

**Dependency:** `pip install mempalace` required in project environment.

## What this skill does

Three operations: **Write** (create or update a drawer), **Read** (return content with staleness state), **Transition** (apply a staleness state change). All operations go through the mempalace `Palace` API. WabbleSpec adds staleness metadata fields, receipt writing, and Provenance notification on top.

## When to use / when not to use

**Use when:**
- Any module needs to store a sourced fact
- Any module needs to retrieve a specific drawer by ID
- A staleness transition event arrives (from Dream, Provenance, or explicit command)

**Do not use when:**
- Querying across drawers by topic or keyword — that is MemorySearch
- Recording lineage, cascade effects, or contradiction flags — that is Provenance

## WabbleSpec metadata extensions

mempalace drawers store standard metadata (wing, room, date, entities, importance, filed_at). WabbleSpec adds these fields to every drawer's ChromaDB metadata:

```json
{
  "wabblespec_staleness_state": "FRESH | AGING | STALE | EXPIRED | NEEDS_REVERIFICATION | SUPERSEDED",
  "wabblespec_confidence": 0.9,
  "wabblespec_expires_at": "2026-06-21T00:00:00Z",
  "wabblespec_source_module": "module-id",
  "wabblespec_schema_version": 1,
  "wabblespec_superseded_by": null
}
```

Prefixed `wabblespec_` to avoid collisions with mempalace native fields.

## How to do it

### Write path

```python
from mempalace.palace import Palace
import os

palace = Palace(os.environ["MEMPALACE_PALACE_PATH"])

# Build metadata with WabbleSpec extensions
metadata = {
    "wing": wing,
    "room": room,
    "date": today_iso,
    "wabblespec_staleness_state": "FRESH",
    "wabblespec_confidence": confidence,
    "wabblespec_expires_at": expires_at_iso,
    "wabblespec_source_module": source_module,
    "wabblespec_schema_version": CURRENT_SCHEMA_VERSION,
}

# Check for existing drawer on same topic in same wing/room
existing = palace.filter_drawers(filters={"wing": wing, "room": room, "topic": topic})

if existing:
    staleness = existing[0]["metadata"].get("wabblespec_staleness_state")
    if staleness in ["SUPERSEDED", "EXPIRED"]:
        # Archive existing, write new
        palace.update_drawer(existing[0]["id"], metadata={"wabblespec_staleness_state": "SUPERSEDED", "wabblespec_superseded_by": "new"})
        palace.add_drawer(content=content, metadata=metadata)
    else:
        # Update evidence, preserve staleness state
        palace.update_drawer(existing[0]["id"], content=content)
else:
    palace.add_drawer(content=content, metadata=metadata)
```

After write: notify Provenance, write memory-write receipt.

### Read path

```python
drawer = palace.get_drawer(drawer_id)
staleness = drawer["metadata"].get("wabblespec_staleness_state", "FRESH")

if staleness == "EXPIRED":
    raise StalenessViolation(f"drawer {drawer_id} is EXPIRED — cannot return content")
if staleness == "SUPERSEDED":
    superseded_by = drawer["metadata"].get("wabblespec_superseded_by")
    raise SupersededError(f"use drawer {superseded_by} instead")

return {"evidence": drawer["content"], "staleness_state": staleness,
        "confidence": drawer["metadata"]["wabblespec_confidence"]}
```

### Transition path

```python
palace.update_drawer(drawer_id, metadata={"wabblespec_staleness_state": to_state})
```

If `to_state == "EXPIRED"`: update metadata and remove from active queries. Drawer stays in ChromaDB for audit — filter via `wabblespec_staleness_state != EXPIRED` in search.

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
  "backend": "mempalace"
}
```

## Common failure modes

1. **`MEMPALACE_PALACE_PATH` not set.** mempalace will write to `~/.mempalace/palace` instead of `.wabblespec/memory/`. Always verify env var before session start. `modules/l5/memory/rules/mempalace-config.md` documents the setup.

2. **Writing without notifying Provenance.** Every write requires Provenance notification — cascade computation depends on it.

3. **Resetting staleness to FRESH on update.** Updating evidence content does not reset staleness. Only explicit re-verification justifies FRESH.

4. **Returning EXPIRED content.** `wabblespec_staleness_state == EXPIRED` means STALENESS_VIOLATION. Return the error. Never return the content.

## Reference

`mempalace-develop/mempalace/palace.py` (Palace API — add_drawer, get_drawer, update_drawer, filter_drawers), `mempalace-develop/mempalace/config.py` (MEMPALACE_PALACE_PATH env var override).
