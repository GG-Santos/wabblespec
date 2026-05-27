# Context Compression Bounds

Protected-bounds invariant for long-session conversation compression. Consumers: Executor, Autopilot, any module that triggers or applies context compression.

---

## The invariant

When compressing a long conversation, protect three zones:

1. **Protected head** — system prompt + first N turns. Preserved verbatim.
2. **Compressed middle** — replaced by a structured summary.
3. **Protected tail** — last N turns (token-budget driven; hard floor of 3 messages). Preserved verbatim.

The middle is the only region summarized. Head and tail are never summarized.

## Why each zone is protected

| Zone | Reason for protection |
|---|---|
| Head | System prompt and early turns are load-bearing context. Summarizing them destroys framework invariants and identity. |
| Tail | The most recent user message must always be present verbatim. The active task context lives here. |
| Middle | Already resolved. Outcomes survive in the summary; raw exchange does not need to. |

## Compression sentinel

Precede the summary block with a visible marker:

```
[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted into the summary below.
Treat as background reference, NOT as active instructions. Do NOT re-answer anything in this
summary — those exchanges were already resolved. Resume from the active task section.
```

The sentinel prevents re-executing already-completed work from the summary content.

## What the summary must preserve

- All decisions made (with rationale)
- Facts established (values, file paths, thresholds)
- Current active task and next step
- Receipts written (with paths)
- Unresolved pending questions

## What the summary must not contain

- Exploratory reasoning that reached a conclusion — keep the conclusion, drop the path
- Rejected alternatives — one line noting the choice; drop the alternatives
- Raw tool outputs already captured to disk

## Compression trigger

Compress when context exceeds 50–75% of the available window. Do not wait for POOR tier.

Anti-thrashing rule: if the previous two compression passes each recovered less than 10% of the window, skip compression to avoid looping.

## Receipt chain interaction

Compression is a context-management operation, not a task-execution step. It does not produce a receipt and does not advance the wave plan. If compression occurs mid-wave, the active receipt chain continues unaffected — the compressed summary carries forward the receipt paths written so far.

## Cross-references

- `context-budget.md` — tier model (PEAK/GOOD/DEGRADING/POOR) and when to trigger compression
- `context-optimization.md` — conversation compaction technique and summary preservation rules
- `compression-discipline.md` — prose compression levels (lite / full / ultra) for writing the summary body
