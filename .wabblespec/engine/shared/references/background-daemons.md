---
name: background-daemons
description: Background daemon architecture for WabbleSpec. Defines trigger events, daemon configuration, and the stop-hook integration pattern.
---

# Background Daemons

Background daemons are maintenance scripts that run automatically at session boundaries without blocking the main session. They are configured in `state/daemons/daemon-config.json` and fired by `stop-hook.py`.

---

## Trigger Events

| Trigger | When it fires | What runs |
|---|---|---|
| `on_stop` | Every session end (via Stop hook) | Dream, memory-mine (when enabled), entity-graph (when enabled) |
| `on_archive` | Session end when a delivery receipt was written | quality-floor, index-update |

---

## daemon-config.json

Location: `.wabblespec/state/daemons/daemon-config.json`

```json
{
  "schema_version": 1,
  "daemons": [
    {
      "id": "quality-floor",
      "script": ".wabblespec/engine/shared/scripts/quality-floor-check.py",
      "trigger": "on_archive",
      "enabled": true,
      "timeout_seconds": 60
    }
  ]
}
```

Fields:
- `id` — unique daemon name for log identification
- `script` — path relative to repo root
- `trigger` — `on_stop` or `on_archive`
- `enabled` — set `false` to suspend without removing the entry
- `timeout_seconds` — daemon is killed after this many seconds

---

## Silent-fail contract

All daemons follow the same contract as the Stop hook: failures emit a warning to stdout but never cause the Stop hook to exit non-zero. A failing daemon must not interrupt the session.

---

## Enabling memory-mine and entity-graph

These are disabled by default because they require the ChromaDB closet index (gate: 50+ drawers). To enable:

1. Confirm `guard-check.py` Layer 3 passes `CLOSET_INDEX_GATE` (drawer count ≥ 50)
2. Edit `state/daemons/daemon-config.json` → set `"enabled": true` for `memory-mine` and `entity-graph`

---

## File-watch pattern (future)

Claude Code does not currently provide a native file-watch trigger. The `on_archive` trigger approximates file-watch by detecting delivery receipt creation. A true file-watch implementation would require:
1. An OS-level watcher (inotify/FSEvents/ReadDirectoryChanges)
2. A separate daemon process (outside Claude Code scope)

Until then, `on_archive` + Stop hook covers the most common case.

---

## Cross-references

- Daemon config: `.wabblespec/state/daemons/daemon-config.json`
- Stop hook: `.wabblespec/engine/scripts/stop-hook.py`
- Dream: `.wabblespec/engine/modules/l5/dream/scripts/dream.py`
- Quality floor: `.wabblespec/engine/shared/scripts/quality-floor-check.py`
- Index update: `.wabblespec/engine/shared/scripts/index-update.py`
