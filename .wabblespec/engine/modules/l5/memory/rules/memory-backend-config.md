# WabbleSpec Memory Backend Configuration

## Design Constraint

WabbleSpec is single-project. All memory store state lives under `.wabblespec/memory/`; nothing in the backend runtime should write to user home directories. ConvoMiner scopes to the current project's sessions only.

## Runtime Configuration

All scripts that use the memory store import `_shared.memory_backend` before backend access. The facade adds the shared package source path, calls `memory.runtime.configure_project()`, and sets runtime env vars before importing storage primitives.

```python
from _shared.memory_backend import get_collection
```

Runtime configuration does:

- Sets `WABBLESPEC_MEMORY_PATH` to `.wabblespec/memory/`
- Prepends the repo root and `packages/memory/src/` to `sys.path`
- Sets `WABBLESPEC_MEMORY_STATE_DIR` to `.wabblespec/memory/.runtime/hook_state/`
- Sets `WABBLESPEC_MEMORY_LOCK_DIR` to `.wabblespec/memory/.runtime/locks/`
- Sets `WABBLESPEC_MEMORY_WAL_DIR` to `.wabblespec/memory/.runtime/wal/`
- Creates `.wabblespec/memory/` and `.wabblespec/memory/.runtime/` if absent
- Uses `wabblespec_drawers` and `wabblespec_closets` as collection names

Optional graph helpers such as hallways are backend capabilities. Use `_shared.memory_backend.has_hallways()` before calling them.

## Backend Package

The backend is a shared internal Python package at `packages/memory/`. WabbleSpec modules load it through `_shared.memory_backend`; they do not import backend internals directly.

## Directory Structure

```text
.wabblespec/memory/
  chroma.sqlite3
  chroma/
  knowledge_graph.sqlite3
  entity-registry.json
  entity-graph.json
  entity-report.md
  gap-map.md
  staleness-map.md
  dream-log.json
  index.json
  wings/
  mine/
  .runtime/
    hook_state/
    locks/
    wal/
```

Verify setup with:

```bash
python scripts/memory-bootstrap.py
python scripts/memory.py --help
```

## Hook Wiring

`.claude/settings.json` runs:

```json
{
  "Stop": "python scripts/memory-bootstrap.py && python modules/l5/dream/scripts/dream.py",
  "PreCompact": "python scripts/run-convo-miner.py --urgent"
}
```

`scripts/run-convo-miner.py` imports `_shared.memory_backend` and handles project-scoped session directory resolution internally.

For MCP setup from a checkout, run `python scripts/memory.py mcp`; it prints
`claude mcp add` / `codex mcp add` commands that call `scripts/memory-mcp.py`
directly, so an editable install is not required. MCP tool identifiers remain
`wabblespec_memory_*` for compatibility.

## WabbleSpec Facade

All WabbleSpec modules use `_shared.memory_backend` rather than importing backend internals directly:

- `get_collection()` for drawer read/write
- `get_closets_collection()` for closet access
- `get_knowledge_graph()` for EntityGraph KG writes
- `search_memories()` for backend hybrid retrieval when MemorySearch needs it
- `mine_sessions()` for ConvoMiner ingest
- `backend_health()` for diagnostics

Memory owns read/write/transition policy, MemorySearch owns query policy, and MemoryMine owns offline analysis. The shared `memory` package powers those layers without replacing their authority boundaries.
