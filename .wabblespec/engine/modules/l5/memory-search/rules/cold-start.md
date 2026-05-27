# Cold-Start Behavior — Memory Search

Defines what Memory Search does when memory or index artifacts are absent.

## Absent: memory store (no drawers)

Condition: `memory/` directory is empty or does not exist.
Detection: Index read returns empty drawer list.
Action: Return empty result set for all queries. Log: "Memory store empty — no search results possible." Do NOT error.
Do NOT: Synthesize results from training data to fill an empty memory.

## Absent: index.json

Condition: `memory/index.json` missing.
Detection: File read returns 404.
Action: Attempt directory scan to reconstruct. If directory also missing, return empty result. Log: "Search index missing."

## Absent: bm25.py script

Condition: `.wabblespec/engine/shared/scripts/bm25.py` not found.
Detection: Script import/read returns 404.
Action: Fall back to keyword matching without BM25 scoring. Log: "bm25.py unavailable — using keyword fallback." Results may be less ranked but not empty.
Do NOT: Block the search entirely. Return keyword-matched drawers with no relevance score.

## Absent: progressive-disclosure reference

Condition: `.wabblespec/engine/shared/references/progressive-disclosure.md` missing.
Detection: File read returns 404.
Action: Apply default disclosure: return first 3 results without excerpt preview; offer full read on request. Log: "Progressive disclosure reference missing — applying defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `result_limit` | 5 results per query (default) |
| `scoring` | BM25 if available; keyword fallback otherwise |
| `disclosure_mode` | Progressive — summary first, full on request |
| `staleness_filter` | Include all drawers; annotate STALE/ANCIENT status |
| `empty_palace_behavior` | Return empty result, do not error |
