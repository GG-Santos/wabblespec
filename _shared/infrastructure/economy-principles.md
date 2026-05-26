# Economy Principles

Framework-level token economy rules. Every module reads these to govern its output density. Invariant I12 in `_shared/references/invariants.md` is the enforcement hook; these principles are the specification I12 enforces.

## Core rule

Every token in every output carries information. No token is decorative, transitional, or redundant.

## Output size thresholds

| Size | Action |
|---|---|
| < 500 tokens | Paste inline. No capture. |
| 500–2000 tokens | Paste inline with compression: preserve technical substance, drop prose padding. |
| > 2000 tokens | Capture to file. Paste summary (first 200 tokens + citation path). |

Token estimate: 1 token ≈ 4 chars English prose, ≈ 3 chars code. When uncertain, capture.

## Capture policy

Large outputs write to `.wabblespec/captures/<module>-<timestamp>.txt`. In-context marker:

```
[captured: .wabblespec/captures/<module>-<timestamp>.txt — <N> tokens — <one-line summary>]
```

Capture is not lossy. Full content on disk. Downstream modules read captures on demand.

## Compression boundaries

**Preserve always:**
- Code blocks (verbatim — no reformatting)
- File paths and identifiers
- Exact numeric values (counts, thresholds, timestamps)
- Error messages and exception text (always verbatim — see Rule 3 below)
- Schema field names and enum values
- Any string declared as a requirement

**Drop always:**
- Sentences restating context already in the conversation
- "This means that..." transition prose
- Explanations of what a built-in tool does
- Hedging on facts that are certain

## Error output rule

Stack traces, compiler errors, test failure output, and schema validation errors are **always pasted verbatim** — never compressed, never summarized. If error output exceeds 2000 tokens: capture AND paste inline. Both.

## Reference loading discipline

1. Load project-map card or summary first
2. Load raw file content only if card is insufficient
3. If raw load exceeds 2000 tokens: apply capture policy
4. Never load more than 3 raw reference files per wave without a capture citation for each

## Context placement (by output type)

| Content type | Placement |
|---|---|
| Receipts | File only — cite path in context |
| Error text | Inline always |
| Code changes | Inline (< 2000 tokens) or captured |
| Reference docs | Captured; cite on demand |
| Spec artifacts | File only — cite path |

## Budget ceiling (--budget mode in Economy module)

When `budget_ceiling` is declared in AGENT.md: Economy projects total pipeline token cost at planning time. If projected > ceiling, emit an advisory with breakdown before Executor runs. Advisory is non-blocking — human decides whether to proceed.

Projection formula: `model_tier_cost_per_token × estimated_task_count × avg_tokens_per_task`

If no budget_ceiling declared: economy-principles apply but no ceiling advisory is emitted.
