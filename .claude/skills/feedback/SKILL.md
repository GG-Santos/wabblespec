---
name: feedback
description: Captures structured human feedback on framework behavior. One feedback item per invocation. Writes to .wabblespec/state/memory/feedback/. Becomes additional signal for Instinct on next run. Does not trigger Synth automatically.
layer: L8
---

# Feedback

You record what humans notice. You do not act on it.

## What this skill does

Feedback captures a single human observation about framework behavior — a module that behaved unexpectedly, a gate that felt wrong, a receipt that did not reflect reality. It structures the observation as a `feedback-{timestamp}.json` in `.wabblespec/state/memory/feedback/`. On the next Instinct run, Feedback items are read alongside receipts as additional signal.

Feedback does not trigger Synth. It does not modify modules or receipts. It records.

## When to use

Feedback activates when a human explicitly invokes it with an observation. There is no automatic trigger. Human provides: the observed behavior, the module involved (if known), and the expected behavior.

## Inputs

From human invocation:
- **Observed behavior** — what happened (required)
- **Module** — which module was involved (optional, fill "unknown" if unclear)
- **Expected behavior** — what should have happened (required)
- **Receipt ref** — path to a specific receipt that demonstrates the issue (optional but preferred)

## Output contract

**One file:** `.wabblespec/state/memory/feedback/feedback-{ISO-timestamp}.json`

```json
{
  "feedback_id": "feedback-{timestamp}",
  "created_at": "ISO-8601",
  "observed_behavior": "What happened, described factually.",
  "module": "module-id or unknown",
  "expected_behavior": "What should have happened.",
  "receipt_ref": "path/to/receipt.json or null",
  "instinct_signal": true,
  "status": "open"
}
```

`instinct_signal: true` marks this item for inclusion in the next Instinct run. Instinct reads all `status: open` feedback items from this directory as supplementary signal (not as primary receipt data).

## Status lifecycle

- `open` — recorded, not yet reviewed by Instinct
- `incorporated` — Instinct has run and included this item in its observations
- `closed` — human has marked this as resolved or not actionable

Status is updated by Instinct (open → incorporated) and by human decision (→ closed). Feedback does not update its own status.

## Failure modes

**Prescriptive feedback** — human provides a solution, not an observation ("module X should do Y"). Fix: Feedback records the observed and expected behaviors. What to do about it is for Synth. Rephrase prescriptions as observations before writing.

**Duplicate feedback** — same observation submitted multiple times. Fix: before writing, scan existing open feedback items for similar observed_behavior. Surface potential duplicates to human.

## --metrics mode

`--metrics <file>` activates automated ingestion of quantitative signals from a CSV or JSON file. This is separate from single-observation feedback. The input is a measurement artifact, not a human opinion.

### Accepted formats

**CSV:** First row is headers. Required columns: `metric`, `value`. Optional: `unit`, `timestamp`, `module`, `source`.

**JSON:** Array of objects with the same field names. Or a single object with a `metrics` array.

### What --metrics does

**Step 1 — Parse and validate.** Read the file. Reject rows missing `metric` or `value`. Surface parse errors to human before writing anything.

**Step 2 — Write production-evidence drawers.** For each valid metric row, write a `memory/evidence/` drawer:

```json
{
  "drawer_id": "evidence-{metric}-{timestamp}",
  "type": "evidence",
  "tags": ["evidence", "production-evidence", "{module-if-present}"],
  "content": "{metric}: {value} {unit} (source: {source}, collected: {timestamp})",
  "freshness": "FRESH",
  "instinct_signal": true
}
```

All drawers from a single `--metrics` run share a `batch_id` field for traceability.

**Step 3 — Contradict-check against Specify specs.** Scan `.wabblespec/state/receipts/` for Specify receipts containing EARS requirements with numeric thresholds. For each metric that contradicts an assumption declared in a Specify receipt (value outside stated threshold):

- Write a `memory/feedback/contradiction-{metric}-{timestamp}.json` item with `status: open`, `instinct_signal: true`, and `contradicts_spec_receipt` pointing to the Specify receipt path.
- Do not modify the spec. Do not trigger Synth. Record the contradiction as signal.

**Step 4 — Notify Product.** If any contradictions were found: write a notification stub to `.wabblespec/notifications/product-{timestamp}.json`:

```json
{
  "notification_id": "product-{timestamp}",
  "type": "metrics-contradiction",
  "summary": "N metrics contradict active Specify assumptions. Review before next spec cycle.",
  "contradiction_paths": ["list of contradiction feedback paths"],
  "created_at": "ISO-8601"
}
```

Product module reads these stubs on next invocation. Feedback does not invoke Product directly.

### --metrics output contract

Writes to:
- `.wabblespec/state/memory/evidence/` — one drawer per metric
- `.wabblespec/state/memory/feedback/` — one contradiction item per contradicting metric (may be zero)
- `.wabblespec/notifications/` — one product notification if contradictions found (may be omitted if zero)

Does not write a separate Feedback receipt. The evidence drawers are the durable output.

## --learn mode (AUGMENT: ParamLearner integration)

`feedback --learn --receipt <path> [--context-type <type>]`

Activates EMA-based parameter adaptation from a WabbleSpec receipt signal. Reads the receipt, extracts learning signal (+1 or -1) and context type, updates the learned profile for that context type.

Uses `.wabblespec/engine/shared/scripts/param-learner.py`. Feedback does not reimplement — it delegates to the script.

### Learning signal mapping

| WabbleSpec signal | EMA rating |
|---|---|
| Verifier PASS receipt | +1 |
| Verifier FAIL receipt | -1 |
| `revise_triggered: true` in receipt | -1 |
| `attestation_required: true` in receipt | -1 |
| Archive receipt written | +1 |

### EMA constants (PAPER §3.3, validated)

| Constant | Value | Meaning |
|---|---|---|
| `EMA_ALPHA` | 0.3 | Learning rate; converges within ~19 signals |
| `MIN_SAMPLES` | 3 | No adjustments until 3 receipts per context type |
| `MAX_WEIGHT` | 0.5 | Learned adjustments never exceed 50% of base profile |
| `SAMPLES_FOR_MAX` | 20 | Reach MAX_WEIGHT at 20 samples |

### Persistence

Learned profiles written to `.wabblespec/state/memory/learned-params/learned-params-{context_type}.json`.

One file per context type (six files max):
- `learned-params-spec-authoring.json`
- `learned-params-code-generation.json`
- `learned-params-security-review.json`
- `learned-params-planning.json`
- `learned-params-synthesis.json`
- `learned-params-administrative.json`

Profile format:
```json
{
  "context_type": "code-generation",
  "sample_count": 12,
  "positive_count": 9,
  "negative_count": 3,
  "positive_params": { "temperature": 0.19, "top_p": 0.79 },
  "negative_params": { "temperature": 0.23, "top_p": 0.82 },
  "adjustments": { "temperature": -0.018, "top_p": -0.014 },
  "last_updated": "ISO-8601",
  "freshness": "FRESH"
}
```

### --learn workflow

```
1. Read receipt at --receipt path
2. Extract rating (+1/-1) from receipt module + outcome fields
3. Extract context_type from receipt task_type or context_classification.detected_type
4. If --context-type provided: override extracted type
5. Call param-learner.py --learn --receipt <path> --context-type <type>
6. Script updates learned-params-{type}.json with EMA update
7. Write learn receipt to .wabblespec/state/receipts/feedback-learn-{timestamp}.json
```

### --learn output contract

```json
{
  "module": "feedback",
  "mode": "learn",
  "receipt_ref": "path/to/source-receipt.json",
  "context_type": "code-generation",
  "rating": 1,
  "sample_count_after": 12,
  "adjustments_count": 2,
  "profile_path": ".wabblespec/state/memory/learned-params/learned-params-code-generation.json",
  "timestamp": "ISO-8601"
}
```

### Stats and inspection

```bash
python .wabblespec/engine/shared/scripts/param-learner.py --stats          # all context types
python .wabblespec/engine/shared/scripts/param-learner.py --get <type>     # single profile JSON
python .wabblespec/engine/shared/scripts/param-learner.py --reset <type>   # clear a profile
```

### What --learn does NOT do

- Does not modify base parameter profiles in ContextTuner (model-router reads adjustments, not replacements)
- Does not trigger Synth or any L8 module
- Does not write to the feedback observation file (--learn is separate from human observation feedback)
- Does not apply the learned params itself — model-router applies them at routing time

## Not tested

Feedback cannot verify that the observed behavior is actually a module defect — it may be correct behavior that the human misunderstood. Instinct and human review determine significance. Feedback records the raw signal without judgment.

`--metrics` mode cannot verify that the measurement file is accurate. Garbage-in applies. The contradiction-check is syntactic (threshold comparison), not semantic (understanding whether the metric is measuring the right thing).

`--learn` mode cannot verify that the receipt accurately reflects the quality of the output. A PASS receipt on a poorly-specified task provides a misleading signal. Signal quality is bounded by spec and acceptance test quality upstream.
