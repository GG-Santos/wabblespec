---
name: dream
description: EMA confidence decay and gap detection. Reads all curated drawer JSON files, applies deterministic decay, writes gap-map.md and staleness-map.md. Zero LLM involvement — script only. Triggered by session-end hook or manually.
---

# Dream

You run the Dream script. You do not interpret its output — you surface it.

## What this skill does

Invokes `modules/l5/dream/scripts/dream.py`. The script reads all curated drawer JSON files from `.wabblespec/memory/wings/`, applies EMA decay to confidence scores, detects coverage gaps and abandoned knowledge, and writes output files to `.wabblespec/memory/`.

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
```

Run from the project root.

Dream reads drawer JSON files directly from `.wabblespec/memory/wings/**/*.json` — not via ChromaDB. It reads `staleness_state`, `confidence`, `expires_at`, and `schema_version` from each JSON file's fields, applies EMA, and writes the updated confidence back to both the JSON file and `index.json`.

Note: dream.py does not update ChromaDB metadata. If you need ChromaDB to reflect updated confidence values, run `scripts/migrate-json-drawers.py` to re-sync after Dream applies changes.

## Concurrency guard

Dream uses a PID lock file at `.wabblespec/memory/.dream.pid` before starting. If the PID file exists and the process is alive, the script exits immediately ("Dream already running — skipping"). The PID file is removed on clean exit or crash (via `atexit`). This prevents overlapping runs when the Stop hook fires repeatedly in a session.

```
.wabblespec/memory/.dream.pid   — lock file, contains PID + start timestamp
```

## Hook wiring (session-end auto-trigger)

Two hooks registered in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python \"C:\\Vaults\\WabbleSpec v6.1\\scripts\\memory-bootstrap.py\" && python \"C:\\Vaults\\WabbleSpec v6.1\\modules\\l5\\dream\\scripts\\dream.py\"",
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
            "command": "python \"C:\\Vaults\\WabbleSpec v6.1\\scripts\\run-convo-miner.py\" --urgent",
            "timeout": 90
          }
        ]
      }
    ]
  }
}
```

**Stop hook:** Bootstrap first (sets env vars), then Dream (EMA decay + gap-map). ConvoMiner runs as a separate hook.

**PreCompact hook:** ConvoMiner only — urgent save before context compaction, 90s cap. Dream skipped (not time-critical at compaction). ConvoMiner ensures current session knowledge survives compaction via `--urgent` (mines newest JSONL only).

ConvoMiner is project-scoped via `scripts/memory-bootstrap.py`. It does NOT mine all `~/.claude/projects/` — only the current project's session directory.

**All paths project-local:** hook_state PID files all write to `.wabblespec/memory/.hook_state/`. Nothing written to user home directories.

## Staleness triggers

Two distinct staleness triggers — Dream handles one:

1. **EMA confidence decay** (WabbleSpec-native): applies time-based decay to confidence scores based on current staleness state
2. **Schema-version mismatch**: if a drawer's `schema_version` field is below the current declared version in `modules/l5/memory/rules/schema-version.md`, Dream flags it as `NEEDS_REBUILD` in gap-map.md regardless of confidence score

State transitions (FRESH → AGING → STALE → EXPIRED) are handled by `staleness-checker.py`, not Dream. Dream only decays confidence values.

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

`modules/l5/dream/scripts/dream.py` (implementation), `modules/l5/memory/scripts/staleness-checker.py` (state transitions — separate from Dream).
