# mempalace Configuration for WabbleSpec

## Design constraint

WabbleSpec is single-project. All mempalace state lives under `.wabblespec/memory/` — nothing in `~/.mempalace/`. ConvoMiner scopes to current project's sessions only.

## Bootstrap (required — import first)

All scripts that use mempalace must import the bootstrap module before any other mempalace import. The bootstrap monkey-patches global path constants and sets env vars.

```python
# FIRST line in any script using mempalace
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
import wabblespec_mempalace_bootstrap  # noqa: F401

# Now safe to import mempalace
from mempalace.palace import Palace
```

Bootstrap does:
1. Sets `MEMPALACE_PALACE_PATH` → `.wabblespec/memory/`
2. Patches `hallways._HALLWAY_FILE` → `.wabblespec/memory/hallways.json`
3. Patches `palace_graph._TUNNEL_FILE` → `.wabblespec/memory/tunnels.json`
4. Patches hook_state dir → `.wabblespec/memory/.hook_state/`
5. Detects current project's Claude Code session directory (project-scoped ConvoMiner)
6. Sets WabbleSpec wing taxonomy

## Install dependency

```bash
pip install mempalace
# or from local:
pip install "C:\Users\Kirsten\Downloads\mempalace-develop"
```

## Directory structure (all project-local)

```
.wabblespec/memory/
  chroma.sqlite3              <- ChromaDB metadata + vector index
  knowledge_graph.sqlite3     <- EntityGraph temporal KG (SQLite)
  chroma/                     <- ChromaDB HNSW segments
  hallways.json               <- Within-wing entity co-occurrence (project-local)
  tunnels.json                <- Cross-wing connectors (project-local)
  entity-registry.json        <- EntityGraph entity list
  entity-graph.json           <- EntityGraph output
  entity-report.md
  gap-map.md                  <- Dream output
  staleness-map.md            <- Dream output
  dream-log.json              <- Dream run history
  mine/                       <- MemoryMine output
    gap-map.md
    mine-clusters.md
    pattern-summary.md
    staleness-map.md
  .hook_state/                <- PID lock files (ConvoMiner, Dream)
    .dream.pid
    .mine.pid
```

Nothing written to `~/.mempalace/`. Verified by running:
```bash
python scripts/wabblespec-mempalace-bootstrap.py
```

## Wing taxonomy (WabbleSpec-specific)

| Wing | Content | ConvoMiner room detection |
|---|---|---|
| `wing_modules` | Module knowledge, SKILL.md distillations | skill, module, layer, executor, verifier |
| `wing_receipts` | Receipt schema, chain patterns, gate decisions | receipt, PASS, FAIL, chain, gate, wave |
| `wing_specs` | Task cards, spec artifacts, acceptance criteria | spec, goal, GWT, given, when, then |
| `wing_decisions` | Architecture decisions, trade-off rationale | decided, chose, trade-off, ADR, invariant |
| `wing_sessions` | Auto-mined Claude Code conversations | session, built, updated, fixed, phase |
| `wing_problems` | Failure modes, workarounds, error taxonomy | problem, error, violation, theater, gap |

## Hook wiring (.claude/settings.json)

```json
{
  "env": {
    "MEMPALACE_PALACE_PATH": "${workspaceFolder}/.wabblespec/memory"
  },
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/wabblespec-mempalace-bootstrap.py && python modules/l5/dream/scripts/dream.py --background",
            "timeout": 30
          },
          {
            "type": "command",
            "command": "python scripts/run-convo-miner.py",
            "timeout": 30
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/run-convo-miner.py --urgent",
            "timeout": 90
          }
        ]
      }
    ]
  }
}
```

`scripts/run-convo-miner.py` handles bootstrap + project-scoped session dir resolution internally.

## ConvoMiner project-scoping

ConvoMiner mines only the current project's Claude Code sessions — not all `~/.claude/projects/`. Bootstrap computes the project-specific session directory via `get_current_project_session_dir()`. Falls back to scanning for most-recently-modified JSONL directory if hash derivation fails.

Conversations route to `wing_sessions`. Room is auto-detected from content keywords (technical/architecture/planning/decisions/problems → general).

## Chunk config

Default: 800 chars, 100 overlap, 30 min (convo_miner lower floor). Do not override unless drawer content is consistently outlier-sized.

## HNSW corruption recovery

If ChromaDB fails to open: delete `.wabblespec/memory/chroma/`, re-mine. `chroma.sqlite3` metadata persists — only HNSW index rebuilds.
