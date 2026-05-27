# Cold-Start Behavior — Dream

Defines what Dream does when its expected memory or receipt inputs are absent.

## Absent: memory store (no drawers)

Condition: `memory/` is empty or has fewer than 3 drawers.
Detection: Index read returns fewer than 3 drawers.
Action: BLOCK Dream run. Surface: "Dream requires at least 3 memory drawers to synthesize from. Current: [n]. Run Memory Mine on completed sessions first."
Do NOT: Synthesize from training data to compensate for sparse memory.

## Absent: prior Dream receipt

Condition: No `dream-receipt.json` in `.wabblespec/state/receipts/`.
Detection: Receipt file absent.
Action: Treat as first Dream run. No prior patterns to compare against — fresh synthesis from current memory store state.

## Absent: specific drawer referenced in synthesis query

Condition: User queries about a topic that has no matching drawers.
Detection: Memory Search returns empty for the query term.
Action: Report: "No drawers found for '[query]'. Dream requires existing memory content to synthesize from."
Do NOT: Generate speculative content about the query topic.

## Absent: entity-graph.json (for cross-drawer synthesis)

Condition: `entity-graph.json` missing when Dream attempts relationship traversal.
Detection: File read returns 404.
Action: Fall back to unweighted drawer co-occurrence for synthesis. Log: "entity-graph.json absent — cross-drawer relationships unweighted."

## Default state on cold start

| Field | Default |
|---|---|
| `minimum_drawers` | 3 (hard minimum to run) |
| `synthesis_scope` | All FRESH + STALE drawers; ANCIENT excluded unless explicitly included |
| `pattern_confidence` | Low on first run (no prior Dream receipts to compare) |
| `behavioral_change` | Documented in Dream receipt — requires human review before actioning |
| `prior_patterns` | null on first run |
