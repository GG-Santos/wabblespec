# Memory Framework Selection Guide

WabbleSpec's default memory layer is proprietary drawer-based storage (`state/memory/wings/`). This reference covers when and how to add external memory infrastructure when the drawer system reaches its retrieval limits.

## When to load this reference

Load when any of these conditions hold:
- Drawer count exceeds 50 per room and memory-search returns empty on queries known to match existing drawers
- Cross-drawer synthesis queries are needed (e.g., "what are all WORKING_SOLUTION drawers related to executor across all rooms?")
- Temporal queries are needed (e.g., "what was the state of module X before the portability migration?")
- Entity consistency is needed across sessions (e.g., tracking a specific module through multiple evolution cycles)

Do not load for routine drawer read/write operations — the drawer system handles these well.

## Escalation Path

Start at the lowest layer that satisfies the retrieval need. Each deeper layer adds infrastructure cost.

```
Layer 0 (Default)
  WabbleSpec proprietary drawers
  └─ File-based JSON with metadata (wing/room/topic/staleness_state)
  └─ memory-search.py for keyword/metadata lookup
  └─ memory-mine.py for closet indexing (enabled at 50+ drawers)
  └─ WHEN TO ESCALATE: memory-search returns empty on known drawers; cross-room
     synthesis queries take more than 3 manual searches

Layer 1 (Add-on: semantic search)
  External vector store (e.g., ChromaDB — already integrated for mempalace)
  └─ Semantic similarity retrieval for conceptual queries
  └─ WHEN TO ESCALATE: temporal queries needed; relationship traversal needed
  └─ NOTE: mempalace integration is COMPLETE but Phase 5 is deferred (gate: 50+ curated drawers)

Layer 2 (Add-on: relationship graph)
  Temporal knowledge graph (e.g., Zep/Graphiti)
  └─ Bi-temporal model (when events occurred + when ingested)
  └─ Relationship traversal ("all items related to executor")
  └─ WHEN TO ESCALATE: agent needs to introspect and self-manage its own memory

Layer 3 (Full control)
  Self-managing memory agent (e.g., Letta, Cognee)
  └─ Agent directly manipulates memory as first-class actions
  └─ Only justified when deep introspection and self-improvement via memory is the core capability
```

## Decision Table

| Query type | WabbleSpec drawers | Layer 1 (vector) | Layer 2 (graph) | Layer 3 (full) |
|---|---|---|---|---|
| "What did we decide about X?" | Keyword search → WORKING_SOLUTION drawer | Semantic search if keyword fails | — | — |
| "All items related to executor" | Manual cross-room search | Semantic search across all rooms | Graph traversal | — |
| "State of X before migration Y" | Staleness_state + provenance | — | Bi-temporal query | — |
| "What changed between v0.46 and v0.51?" | Git log + receipt-index | — | Graph diff | — |
| "Agent improves its own recall strategy" | Not applicable | — | — | Self-managing agent |

## Benchmark Signals

These benchmarks reflect point-in-time evaluations and will age as models update:
- Filesystem-based memory scored 74% on LoCoMo vs. managed vector tools at 68.5% — simpler wins until retrieval quality demonstrably degrades
- Temporal knowledge graphs achieve up to 90% latency reduction over naive graph retrieval by querying only relevant subgraphs
- Multi-hop reasoning tasks (cross-session synthesis) favor graph approaches over pure vector retrieval

**Implication for WabbleSpec:** The drawer system's metadata structure (wing/room/topic/staleness_state) provides more precise filtering than embedding similarity for structured queries. Add vector search only when unstructured conceptual queries fail on known-populated drawers.

## WabbleSpec-Specific Integration Notes

**ChromaDB (mempalace — already integrated, Phase 5 deferred):**
- Integration exists at `.wabblespec/engine/modules/l5/memory/`
- Phase 5 gate: 50+ curated drawers before activation
- Check current drawer count: `python .wabblespec/engine/shared/scripts/drawer-writer.py --count` (if supported) or `find .wabblespec/state/memory/wings -name "*.json" | wc -l`

**Before adding any external framework:**
1. Verify the mempalace Phase 5 gate is not already met — if 50+ curated drawers exist, ChromaDB layer should be activated first (it's already built)
2. Run `wabblespec-doctor.py` after any memory layer addition to check for D1 drift
3. memory-mine.py daemon runs on_stop and handles closet indexing — external frameworks must not duplicate this pipeline

**Adding a new memory backend:**
- Declare it in `engine/modules/l5/memory/rules/memory-backend-config.md`
- Add staleness-state mapping in `engine/modules/l5/memory/rules/staleness-thresholds.md`
- Memory module owns all writes to `state/memory/` — external frameworks write to their own stores, not to drawer JSON files

## Failure Modes to Avoid

1. **Adding graph infrastructure before 50 curated drawers**: Before that volume, the overhead exceeds the benefit. Index quality is too low for graph relationships to carry signal.

2. **Duplicating drawer content in the vector store**: Drawers and vector embeddings serve different query shapes. Drawers answer "what decision was made about X" (structured lookup). Vector stores answer "what is semantically related to X" (conceptual similarity). They complement rather than replace each other.

3. **Letting temporal queries drive architecture over-engineering**: Most temporal queries ("what was the state before the migration?") are answerable by combining staleness_state fields with git log. Only add temporal knowledge graph infrastructure when this combination fails.

4. **Breaking the memory-mine closet index**: memory-mine.py builds a structured index of drawers for fast lookup. External vector stores must be kept in sync with drawer mutations — if a drawer is modified or garbage-collected, the vector embedding for that drawer must be updated or removed.
