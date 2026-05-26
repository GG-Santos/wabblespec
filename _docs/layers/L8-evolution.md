# L8 — Evolution

The self-improvement layer. L8 modules use accumulated run history to improve the framework itself — promoting better module versions, discovering patterns, and building instinct from experience.

**L8 is gated.** It does not activate until the L8 evolution gate is cleared.

## Gate requirements (current status: NOT cleared)

1. **100+ PASS receipts** across real pipeline runs — current: 19/100
2. **3 human-validated Instinct patterns** — current: 0/3
3. **Benchmark schema** at `_shared/schemas/benchmark.schema.json` — must be present and valid

## Modules

| Module | Role |
|--------|------|
| `instinct` | Extracts recurring patterns from Dream log and receipt history. Human validates candidates before they become instinct entries. |
| `synth` | Identifies a module behavior that could be improved based on run history. Produces a Synth candidate. |
| `blueprint` | Converts a Synth candidate into a formal promotion proposal. Names before/after behavior, defines benchmark gates, lists affected targets. Requires human Attestation (sign-off) before Augment or Factory may proceed. |
| `benchmark` | Runs the proposed implementation against a fixture set. Computes held-out metric. Compares against blueprint threshold. AUGMENT type requires ≥ 80% parity; NEW type requires ≥ 60% improvement over baseline. Failure halts promotion. |
| `augment` | Applies a blueprint-approved module improvement. Requires Benchmark PASS and human Attestation. |
| `factory` | Generates new module variants from a blueprint. Requires Benchmark PASS and Attestation. |
| `forge` | Hardens a module — stress-tests edge cases, improves error handling, tightens invariants. |
| `feedback` | Structured feedback capture from run outcomes. Feeds into Synth and Instinct. Supports `--metrics` flag for quantitative capture. |
| `retro` | Retrospective analysis of a completed pipeline run or session. Identifies what worked, what didn't, and what to carry forward. |

## Promotion pipeline

```
Synth (identifies candidate)
  → Blueprint (formal proposal + benchmark gate definition)
    → human Attestation (required)
      → Benchmark (validates improvement)
        → Augment or Factory (applies promotion)
```

No step may be skipped. Blueprint without Attestation does not advance to Benchmark.

## Key behaviors

**Instinct** builds from Dream log entries that recur across 3+ sessions. Human validation is required before an instinct entry is written — Instinct never auto-promotes a pattern without sign-off.

**Blueprint** is the commitment point. Once Blueprint is written and attested, the promotion is formally proposed and Benchmark is authorized to run. Blueprint can be revoked by human before Benchmark completes.

**Benchmark** failure halts promotion and appends to `_shared/references/benchmark-tracker.json`. The promotion does not retry automatically — a new Synth-Blueprint cycle is required.

**Feedback** is not a pipeline module — it can be invoked at any point to capture structured feedback about a completed task. The `--metrics` flag enables quantitative metric capture alongside qualitative notes.

## Layer rules

- No L8 module runs before the L8 gate is cleared
- Blueprint requires human Attestation — no Attestation, no Benchmark
- Augment and Factory both require Benchmark PASS, not just Blueprint approval
- Instinct patterns require human validation before being written to the instinct store
- Benchmark appends failures to tracker — never silently discards them
