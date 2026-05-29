---
name: economy
description: Token density enforcement. Ensures WabbleSpec output stays within declared token budgets. Currently covered by invariant I12 (no redundant output). Separate module not yet justified — activate if I12 enforcement proves insufficient.
---

# Economy

Token density enforcement for WabbleSpec output. The goal: every token in every module output carries information. No padding, no repetition, no summary-of-summary.

## What this skill does

Token density enforcement. Ensures WabbleSpec output stays within declared token budgets. Currently covered by invariant I12 (no redundant output). Separate module not yet justified — activate if I12 enforcement proves insufficient.

## When to use

Invoked per activators declared in `skill-rules.json`.

## Current status

Invariant I12 in `.wabblespec/engine/shared/references/invariants.md` covers token density: "Output contains no redundant information. Each sentence adds a fact not present in any prior sentence."

I12 is enforced by Guard on every receipt. A separate Economy module would duplicate this enforcement.

**Economy module activates if:** I12 enforcement is found insufficient after 50+ real executions, OR if token budget tracking (per-wave budgets with hard caps) becomes necessary.

## Mechanical rules (active now)

These rules apply to all WabbleSpec module output regardless of the 50-execution activation gate. They address a specific failure mode: reference loading, search results, and large command outputs flooding context and hiding actionable signal.

### Rule 1 — Output size thresholds

| Output size | Action |
|---|---|
| < 500 tokens | Paste inline. No capture needed. |
| 500–2000 tokens | Paste inline with compression: drop prose padding, keep technical substance. Preserve: identifiers, paths, code blocks, error text, schema fields, exact values. Drop: explanation of what a tool does, transition sentences, restated context already in the conversation. |
| > 2000 tokens | Capture to file. Paste only a summary (first 200 tokens + citation). See Rule 2. |

Token estimate: 1 token ≈ 4 characters of English prose, ≈ 3 characters of code. When uncertain, err toward capture.

### Rule 2 — Capture policy

Large outputs (> 2000 tokens) write to `.wabblespec/captures/<module>-<timestamp>.txt`.

**In-context reference format:**
```
[captured: .wabblespec/captures/<module>-<timestamp>.txt — <N> tokens — <one-line summary>]
```

Modules cite the capture path in their receipt (`evidence` field or `captures[]` array). Reviewer and Verifier read captures on demand — they are not pasted back unless explicitly needed.

**Capture is not lossy.** The full content is on disk. Nothing is discarded. The capture marker tells downstream modules where to find it.

### Rule 3 — Exact-error preservation

Stack traces, compiler errors, test failure output, hook exit messages, and schema validation errors are **always pasted verbatim** — never compressed, never summarized.

Rationale: compressing errors hides the exact token that identifies the root cause. A 3000-token stack trace is better inline than a 50-token summary that omits the frame.

**If an error output exceeds 2000 tokens:** capture the full output AND paste it inline. Do not apply the size threshold to error output. Error text is always inline AND on disk.

### Rule 4 — Reference loading discipline

When ReferenceLoad or MemorySearch loads external content:

1. Load the project-map card or summary first (if one exists)
2. Load raw file content only if the card is insufficient for the current decision
3. If raw load exceeds 2000 tokens: apply Rule 2 (capture + cite)
4. Never load more than 3 raw reference files per wave without a capture citation for each

This prevents the "load the whole repo" failure mode that buries actionable context under reference noise.

### Rule 5 — Compression boundaries

When compressing output under Rule 1 (500–2000 token range), preserve exactly:

- Code blocks (unchanged — no reformatting, no shortening)
- File paths and identifiers
- Exact numeric values (counts, sizes, thresholds, timestamps)
- Error messages and exception text
- Schema field names and enum values
- Any string the user or a prior module declared as a requirement

Drop:

- Sentences that restate context already in the conversation
- "This means that..." transition prose
- Explanations of what a built-in tool does
- Hedging and uncertainty qualifiers on facts that are certain

## What Economy would add (if activated at 50-execution gate)

- Per-wave token budget declaration in task card
- Verifier check: estimated output tokens vs declared budget
- Receipt field: `token_budget_declared`, `tokens_used`, `budget_exceeded`
- Automatic compression pass when budget is exceeded before Executor proceeds

## Decision gate

After 50 real task executions: measure average receipt size and module output size. If average exceeds 2x the information-minimal baseline, activate Economy with token caps. If within 2x, I12 + the mechanical rules above are sufficient.

## --budget mode

`--budget` activates proactive token cost projection before a task wave begins. The purpose is to surface budget overrun risk before tokens are spent, not after.

### Budget ceiling source

Budget ceiling is declared in `AGENT.md` as:

```yaml
economy:
  budget_ceiling: <integer>   # max tokens for this task (all waves combined)
  per_wave_ceiling: <integer> # max tokens per wave (optional)
```

If neither field is present in `AGENT.md`, `--budget` is a no-op (emits a warning, does not block).

### What --budget does

**Step 1 — Read ceiling.** Load `AGENT.md`. Extract `economy.budget_ceiling` (and `per_wave_ceiling` if present). If absent: warn and exit cleanly.

**Step 2 — Project cost.** Estimate token cost of the current wave plan:

| Cost component | Estimate method |
|---|---|
| Task card | character count ÷ 4 |
| Wave plan | character count ÷ 4 |
| Reference files declared in wave | sum of file sizes ÷ 4 |
| Expected module outputs | use prior receipt sizes for same module (if available), else apply module tier: L1–L2 = 800 tokens, L3–L5 = 1200 tokens, L6–L8 = 600 tokens |
| Tool call overhead | +200 tokens per tool call in wave plan |

Sum all components. This is `projected_tokens`.

**Step 3 — Emit advisory if projected > ceiling.**

If `projected_tokens > budget_ceiling` (task-level) or `projected_tokens > per_wave_ceiling` (wave-level):

Write a budget advisory to `.wabblespec/advisories/budget-{timestamp}.json`:

```json
{
  "advisory_id": "budget-{timestamp}",
  "type": "budget-overrun-risk",
  "budget_ceiling": <integer>,
  "projected_tokens": <integer>,
  "overage": <projected - ceiling>,
  "overage_pct": <overage / ceiling * 100>,
  "wave_index": <integer>,
  "recommendation": "Reduce reference loads or split wave before proceeding.",
  "blocking": false
}
```

Advisory is non-blocking by default. Executor reads it and surfaces it to human. Human decides whether to proceed.

**Step 4 — Write projection to receipt.**

Whether or not ceiling is exceeded, append to the current wave receipt:

```json
{
  "token_budget_declared": <ceiling or null>,
  "tokens_projected": <projected_tokens>,
  "budget_exceeded": <true|false>
}
```

### --budget does not block execution

Advisory emission is informational. Economy does not refuse to run a wave. The decision to split, defer, or proceed belongs to the human or Executor, not Economy.

### Real context pressure boundary

Economy's `--budget` mode projects token cost before a wave begins. The actual risk boundary is the runtime auto-compact threshold, not the raw model context window:

```
effectiveContextWindow = modelContextWindow - min(maxOutputTokensForModel, 20,000)
autoCompactThreshold = effectiveContextWindow - 13,000
```

A projected cost approaching `autoCompactThreshold` means the session is likely to compact mid-wave. Compaction is transparent to the receipt chain (receipts live on disk) but introduces latency and may lose fine-grained file context. When `projected_tokens` crosses 80% of `autoCompactThreshold`, Economy should note this in the advisory.

The blocking limit (hard stop) is `effectiveContextWindow - 3,000`. A session at the blocking limit cannot issue further requests without compaction.

Full compaction threshold math and process: `.wabblespec/engine/shared/references/compaction-behavior.md`.

### --budget accuracy

Projection accuracy degrades when:
- Wave plan references files not yet written (cost unknown — use module tier estimate)
- A module produces a large artifact not predictable from prior receipts

After the wave completes, Verifier may compare `tokens_projected` against actual receipt size. Accuracy data feeds the per-module tier estimates in future projections.

## Reference Routing

| Situation | Reference |
|---|---|
| Economy receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## Output contract

Writes a receipt to `.wabblespec/state/receipts/` on successful completion. In `--budget` mode, also writes to `.wabblespec/advisories/` when projected tokens exceed ceiling.
