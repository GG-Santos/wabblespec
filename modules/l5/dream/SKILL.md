---
name: dream
description: EMA confidence decay and gap detection. Reads all drawers, applies deterministic decay, writes gap-map.md and staleness-map.md. Zero LLM involvement — script only. Triggered by session-end hook or manually.
---

# Dream

You run the Dream script. You do not interpret its output — you surface it.

## What this skill does

Invokes `modules/l5/dream/scripts/dream.py`. The script reads all drawers, applies EMA decay to confidence scores, detects coverage gaps and abandoned knowledge, and writes two output files to `.wabblespec/memory/`.

You do not decide what is stale. The script decides. You run the script and report what it found.

## When to use

- At session end — automatically via Stop hook (see Hook Wiring below)
- When a gap-map finding needs to be acted on
- When confidence scores feel unreliable after many receipts
- After 10 drawer writes (signals enough data for decay to matter)

**Do not use:**
- As a substitute for staleness-checker — staleness-checker handles state transitions, Dream handles confidence decay and gap reporting
- On every wave — this is a session-level operation
- If another Dream process is running (script checks PID lock and exits cleanly)

## How to run it

```
python modules/l5/dream/scripts/dream.py
python modules/l5/dream/scripts/dream.py --dry-run
python modules/l5/dream/scripts/dream.py --background
```

Run from the project root. `MEMPALACE_PALACE_PATH` must be set (see `modules/l5/memory/rules/mempalace-config.md`).

Dream reads all drawers via mempalace `Palace.filter_drawers()` — not by scanning flat JSON files. It reads `wabblespec_staleness_state`, `wabblespec_confidence`, `wabblespec_expires_at`, and `wabblespec_schema_version` from ChromaDB metadata.

## Concurrency guard (from mempalace hook pattern)

Dream uses a PID lock file at `.wabblespec/memory/.dream.pid` before starting. If the PID file exists and the process is alive, the script exits immediately with a message ("Dream already running — skipping"). The PID file is removed on clean exit or script crash (via `atexit`). This prevents overlapping runs when the Stop hook fires repeatedly in a session.

```
.wabblespec/memory/.dream.pid   — lock file, contains PID + start timestamp
```

## Hook wiring (session-end auto-trigger)

Two hooks registered in `.claude/settings.json`: Stop (session end) and PreCompact (before context compaction). Adapted from `mempalace-develop/.claude-plugin/hooks/hooks.json`.

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python modules/l5/dream/scripts/dream.py --background",
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

**Stop hook sequence:**
1. Dream runs `--background` (EMA decay + gap-map, non-blocking, PID-locked)
2. `run-convo-miner.py` mines current project's Claude Code sessions only → `wing_sessions`

ConvoMiner is project-scoped via `scripts/wabblespec-mempalace-bootstrap.py`. It does NOT mine all `~/.claude/projects/` — only the current project's session directory. Exchange-pair chunking (Q+A = one unit). Per-file locking + schema-version purge on bump.

**PreCompact hook:** urgent save before context compaction, 90s cap. Dream skipped (not time-critical). ConvoMiner only — ensures current session knowledge survives compaction.

**All paths project-local:** hallways, tunnels, hook_state PID files all write to `.wabblespec/memory/` via bootstrap. Nothing written to `~/.mempalace/`.

## Staleness triggers

Two distinct staleness triggers — Dream handles both:

1. **EMA confidence decay** (WabbleSpec-native): applies time-based decay to confidence scores
2. **Schema-version mismatch** (adapted from mempalace `normalize_version` pattern): if a drawer's `schema_version` field is below the current declared version in `modules/l5/memory/rules/schema-version.md`, Dream flags it as `NEEDS_REBUILD` in gap-map.md regardless of confidence score

## EMA formula

```
new_confidence = old_confidence * 0.9 + base_freshness * 0.1
```

base_freshness by staleness_state: FRESH=1.0, AGING=0.7, STALE=0.3, EXPIRED=0.0, NEEDS_REVERIFICATION=0.2, SUPERSEDED=0.0

Applied once per run. Deterministic — same inputs always produce same output.

## Outputs

| File | Location | Purpose |
|---|---|---|
| `gap-map.md` | `.wabblespec/memory/` | Actionable findings: EXPIRED drawers, low-confidence, coverage gaps, schema-version mismatches |
| `staleness-map.md` | `.wabblespec/memory/` | Full drawer state table sorted worst-first |
| `dream-log.json` | `.wabblespec/memory/` | Run history for Phase 4 validation gate (10 runs required) |

## After running

1. Read `gap-map.md`
2. Pick highest-severity finding
3. Follow the Action instruction in that finding
4. Update the drawer via Memory module
5. Re-run Dream to confirm finding closed

## Validation gate (Phase 4)

Dream is not proven until 10 runs exist in `dream-log.json` AND at least one gap-map finding led to a drawer update. Check `dream-log.json` `runs` array length. If zero findings ever appeared across 10 runs, the EMA formula or gap thresholds need tuning.

## Reference

Pattern source: `mempalace-develop/mempalace/hooks_cli.py` (PID slot reservation, concurrent mine guard), `mempalace-develop/hooks/mempal_save_hook.sh` (session-end Stop hook trigger, background mode).
