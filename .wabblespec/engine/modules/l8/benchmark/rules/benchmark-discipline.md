# Benchmark Discipline Rules

Source patterns: `WabbleSpec Memory-develop/benchmarks/BENCHMARKS.md` (integrity warning), `codeflow-main/tests/codeflow-golden.test.mjs` (golden test pattern).

---

## Rule 1: Developer outcome required

Every benchmark must link to one of four real failure modes:

| Outcome | What it means |
|---|---|
| `false_completion` | Task marked done by a module but was not actually complete |
| `missed_test` | Test or acceptance criterion was missing — defect reached next wave |
| `stale_evidence` | Module used outdated memory or stale receipt evidence |
| `rework` | Output had to be redone because module produced wrong result |

A benchmark that improves an abstract score without tying to one of these outcomes MUST be rejected. "Better quality" is not a developer outcome.

---

## Rule 2: Held-out split is the only reportable number

Adapted from WabbleSpec Memory integrity warning (BENCHMARKS.md):

> The 99.4%→100% step tuned on 3 specific wrong answers. Held-out 450q is 98.4%.

The score achieved on examples used during development is not a benchmark result. It is an overfitting measurement. Only the held-out split result is valid.

Enforcement:
- `held_out_split.held_out_cases` must be ≥ 30% of `total_cases`
- `run_history` records `held_out_value` only — tuning-set values are not persisted
- Any claim that "module X improved" must cite a held-out run, not a tuning run

---

## Rule 3: Metric type must be declared and consistent

Adapted from WabbleSpec Memory comparison table caveat:

> R@5 retrieval recall and QA accuracy are not comparable.

WabbleSpec benchmark metrics:
- `rate`: a fraction (0.0–1.0) — e.g. false-completion rate, miss rate
- `count`: an integer — e.g. number of REVISE cycles triggered
- `latency_ms`: wall-clock milliseconds
- `boolean`: pass/fail on a single criterion

Cross-benchmark comparison is only valid when `metric.type` and `metric.name` match exactly. Benchmarks with different metric types MUST NOT be compared in a single table.

---

## Rule 4: Fixtures must be committed, deterministic, and golden-tested

Adapted from codeflow `codeflow-golden.test.mjs` pattern:

- Fixture set committed to the project — no runtime data fetch
- Run command produces identical output on identical fixtures
- `expected_output_path` holds the golden output for comparison
- A benchmark run that does not match its golden output FAILS, even if the metric value improved

Golden output is updated only by deliberate human action, not automatically.

---

## Rule 5: Rejection criteria must be explicit

Each benchmark defines `rejection_criteria` — the conditions under which a proposed module improvement is blocked. Minimum required criterion:

```json
{
  "condition": "held_out metric value regresses below baseline.value",
  "verdict": "REJECT"
}
```

A benchmark with no rejection criteria cannot reject anything and provides no quality gate. It is invalid.

---

---

## Rule 6: Composite blueprints require axis decomposition

Every blueprint that defines a composite quality metric (any metric with multiple contributing dimensions) must declare a named-axis decomposition. The decomposition is declared in the blueprint artifact before Augment may proceed. Benchmarks that use a single scalar score without axis decomposition are valid only for atomic/deterministic modules (e.g. receipt field presence checks).

### WabbleSpec standard scoring axes

| Axis | Points | Operationalization |
|---|---|---|
| Spec-compliance | 0–25 | Output fulfills declared EARS requirements in task card |
| Receipt completeness | 0–20 | All schema-required fields present and non-empty |
| Invariant adherence | 0–20 | Output avoids I1/I4/I6/I10/I11 violations |
| Verification gate pass | 0–20 | Output would pass Verifier without REVISE cycle |
| Language precision | 0–15 | Modals correct (SHALL/SHOULD/MAY), hedging absent |

These axes total 100 points. Blueprint authors may adjust weights for specific module contexts; any deviation from defaults must be documented with rationale.

**G0DM0D3 axes NOT adopted:**
- Length bias (46.7% effective weight in G0DM0D3) — WabbleSpec values concision, not verbosity
- Anti-refusal axis (26.1% in G0DM0D3) — jailbreak metric; has no place in SDLC evaluation

---

## Rule 7: Degradation analysis required before composite gate acceptance

Before any composite blueprint gate is accepted into `.wabblespec/experiments/`, run a degradation analysis to verify axis weight ordering is calibrated correctly.

### Protocol

1. Run candidate against full fixture set; record total score and per-axis scores
2. Zero each axis contribution one at a time; record total score drop
3. Confirm hierarchy: spec-compliance drop > receipt-completeness drop and so on per weight table
4. If ordering is violated: adjust axis weights and repeat from step 1
5. Document in blueprint artifact as `axis_calibration_run: true` with per-axis delta table:

```json
{
  "axis_calibration_run": true,
  "axis_deltas": [
    { "axis": "spec-compliance", "weight": 25, "score_drop": 22.4 },
    { "axis": "receipt-completeness", "weight": 20, "score_drop": 18.1 },
    { "axis": "invariant-adherence", "weight": 20, "score_drop": 19.7 },
    { "axis": "verification-gate-pass", "weight": 20, "score_drop": 17.8 },
    { "axis": "language-precision", "weight": 15, "score_drop": 13.2 }
  ],
  "ordering_confirmed": true
}
```

Degradation analysis is a one-time pre-acceptance gate, not a recurring benchmark run.

---

## What was not taken from references

- **R@5 retrieval recall**: memory retrieval metric irrelevant to WabbleSpec module evaluation
- **LongMemEval, LoCoMo, ConvoMem**: external benchmarks for conversational memory systems — not applicable
- **QA accuracy**: WabbleSpec does not generate answers to questions; it produces receipts and artifacts
- **Scale benchmark suite** (WabbleSpec Memory 106-test scale suite): WabbleSpec modules are not database operations
- **Telegram notifications** and **cost tracking** from convomem_bench.py runner: infrastructure concerns
- **G0DM0D3 length bias axis** (46.7% effective weight): verbosity is not a quality signal in WabbleSpec
- **G0DM0D3 anti-refusal axis** (26.1%): jailbreak metric, excluded by design
