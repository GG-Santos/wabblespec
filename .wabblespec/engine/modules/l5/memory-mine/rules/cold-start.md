# Cold-Start Behavior — Memory Mine

Defines what Memory Mine does when session receipts or memory artifacts are absent.

## Absent: session receipts to mine

Condition: `.wabblespec/state/receipts/` is empty or contains no completed run receipts.
Detection: Receipt directory scan returns empty or only in-progress entries.
Action: Return empty mining result. Log: "No completed receipts to mine — memory store will not be updated."
Do NOT: Mine from in-progress or failed receipts. Mining is a post-completion operation.

## Absent: memory store to write into

Condition: `memory/` directory does not exist.
Detection: Directory read returns 404.
Action: Log: "Memory store absent — Mine will initialize it." Create `memory/` and `memory/index.json` before writing mined drawers.
Do NOT: Fail because the memory store doesn't exist. Mine creates it if absent.

## Absent: prior mining receipt

Condition: No `memory-mine-receipt.json` from a prior session.
Detection: Receipt file absent.
Action: Treat as first mining run. Mine all available completed receipts. There is no cursor to resume from — process everything.

## Absent: entity-graph.json

Condition: `entity-graph.json` not found when Mine attempts to update graph entries.
Detection: File read returns 404.
Action: Skip entity graph update. Log: "entity-graph.json absent — skipping graph enrichment."
Do NOT: Block the mining run. Graph enrichment is additive, not required.

## Default state on cold start

| Field | Default |
|---|---|
| `mining_cursor` | null — mine all receipts on first run |
| `drawers_created` | 0 |
| `drawers_updated` | 0 |
| `palace_initialized` | false until first write |
| `min_receipt_status` | PASS only — failed and pending receipts not mined |
