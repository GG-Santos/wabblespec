# Observation Merge Guide

**Purpose**: Reference for merging WabbleSpec Instinct observations across
execution runs before synthesis. Used by the L8 chain (Instinct → Synth →
Blueprint) when multiple runs have produced overlapping observations.

Adapted from cross-device memory merge principles. No LLM required —
these rules are applied deterministically by the analyst reviewing the
observation set before feeding it to Synth.

---

## The 7 Rules

### Rule 1 — DEDUPLICATE
If two runs report the same pattern in different words, keep the more
specific formulation. Log what was dropped in the observation merge receipt.

> Before: "Model tends to skip receipts on simple tasks" (run 12)
> Before: "Receipt writes are being omitted on low-complexity waves" (run 15)
> After:  "Receipt writes are omitted on low-complexity waves" [run: 12, 15]

### Rule 2 — RESOLVE CONTRADICTIONS
If two runs disagree on a behavioral pattern:
- If one is more recent and the other is older than 14 days (`AGING`/`STALE`): prefer the newer
- If both are recent and genuinely contradict: assign a confidence score
  - `0.9+` → auto-promote to Synth candidate, note the contradiction in reason field
  - `0.7–0.89` → present to human for attestation before Synth
  - `< 0.7` → flag as NEEDS_REVERIFICATION; do not promote

### Rule 3 — PRESERVE UNIQUE
If a pattern appears in only one run but is specific and actionable, keep it.
Single-run evidence is valid — do not require N+1 confirmation for promotion.
The Blueprint attestation gate is the human check, not the observation count.

### Rule 4 — TAG RUN-SPECIFIC
If an observation clearly applies only to one run's context (e.g., references
a specific task card ID, a one-off error, or a temporary module state), tag it:

> `[run: forge-executor-checkpoint-v1]` Guard emitted false STALENESS_VIOLATION on pre-wave files

Do not promote tagged observations to CLAUDE.md or rules without stripping
and generalizing the tag first.

### Rule 5 — MAINTAIN STRUCTURE
Keep the drawer heading hierarchy intact when merging observations from
multiple run receipts into a single drawer file. Group related patterns
under the same heading. Do not flatten everything into a single list.

### Rule 6 — EVIDENCE LIMIT
Each drawer `MEMORY.md` must stay under 200 lines. When merging would
exceed this, prioritize:
1. Universal patterns over run-specific notes
2. Patterns with higher run frequency
3. Actionable instructions over passive observations
4. Recent evidence over stale evidence (`FRESH` > `AGING` > `STALE`)

### Rule 7 — DO NOT INVENT
Only include patterns that appear in at least one execution receipt.
Do not add inferences, predictions, or "likely" patterns not evidenced
by an actual run. The receipt chain is the source of truth (I1, I10).

---

## Confidence Score Reference

| Score | Meaning | Action |
|---|---|---|
| 0.95–1.0 | Pattern is unambiguous; consistent across 3+ runs | Auto-promote to Synth |
| 0.85–0.94 | Strong signal; consistent across 2 runs | Promote to Synth, note in reason |
| 0.70–0.84 | Moderate signal; single run or partial consistency | Queue for Attestation |
| 0.50–0.69 | Weak signal; contradicted or ambiguous | NEEDS_REVERIFICATION |
| < 0.50 | Noise; contradicted by more recent evidence | Drop; log in merge receipt |

---

## Output Format (Synth Candidate)

When merging produces a promotable pattern, record it as:

```json
{
  "pattern": "<concise description of the behavioral pattern>",
  "evidence_runs": ["run-id-1", "run-id-2"],
  "confidence": 0.92,
  "contradiction_note": "<if Rule 2 applied, describe what was contradicted>",
  "run_specific_tags": [],
  "staleness_state": "FRESH",
  "proposed_target": "CLAUDE.md | rules/<name>.md | skill:<name>"
}
```

---

## What This Guide Does NOT Cover

- LLM-powered merge (not used in WabbleSpec — all merges are deterministic)
- Cross-device CLAUDE.md sync (handled by `scripts/sync-merge.py` via git)
- Blueprint promotion logic (see `modules/l8/blueprint/SKILL.md`)
- Attestation workflow (see `.wabblespec/engine/shared/references/invariants.md` I8)
