---
name: instinct
description: Passive receipt pattern observer. Reads execution receipts and entity graph to surface recurring patterns. Read-only — no writes, no Synth invocation, no auto-promotion. Deferred until 100+ verified receipts exist.
---

# Instinct

You observe. You do not act.

Instinct reads the receipt corpus, entity graph, and dream gap-map to detect patterns that repeat across multiple executions. You write an observation log. You do not write receipts, do not modify modules, do not invoke Synth, and do not promote any finding to production.

## What this skill does

Passive receipt pattern observer. Reads execution receipts and entity graph to surface recurring patterns. Read-only — no writes, no Synth invocation, no auto-promotion. Deferred until 100+ verified receipts exist.

## When to use

**Do not activate until ALL of the following are true:**

1. `≥ 100` verified receipts exist in `.wabblespec/receipts/` (across all module types)
2. EntityGraph has run at least once with ≥ 50 drawers (produces `entity-graph.json`)
3. A human has explicitly invoked Instinct with `--activate` after confirming gate conditions are met

Gate is enforced by the script. If receipt count < 100, Instinct exits with `GATE_NOT_MET` and prints the current count. It does not produce partial observations on sub-gate data.

## What Instinct observes

Instinct reads three inputs and nothing else:

| Input | Location | What it looks for |
|---|---|---|
| Receipts | `.wabblespec/receipts/*.json` | Recurring verdict patterns, modules that frequently REVISE or ESCALATE, co-occurrence of module failures |
| Entity graph | `.wabblespec/memory/entity-graph.json` | High-degree entities (god nodes), entity pairs that co-occur across many receipts |
| Dream gap-map | `.wabblespec/memory/gap-map.md` | Topics flagged repeatedly across sessions as gaps or low-confidence |

## Pattern types (adapted from graphify-7 analyze.py)

Instinct looks for three pattern types only. No other pattern types are added without evidence from a real failure case.

### Type 1: High-frequency module failure

A module that produces REVISE or ESCALATE verdicts in ≥ 20% of its receipts across the observed corpus. Indicates a systematic weakness, not a one-time error.

Threshold: observed in ≥ 5 distinct receipts (not just one receipt with multiple cycles).

### Type 2: Co-occurrence cluster (from graphify-7 community detection)

Two or more modules whose failures co-occur in the same execution wave at a rate above chance. Indicates coupling that the spec did not anticipate.

Adapted from graphify-7's `surprising_connections(G, communities)` — entity pairs that cross community boundaries unexpectedly. Applied here to module-pair failure co-occurrence.

Threshold: co-occurrence in ≥ 3 distinct execution waves, p < expected by module frequency alone.

### Type 3: Recurring gap topic (from Dream gap-map)

A topic appearing in Dream's gap-map across ≥ 3 distinct sessions with confidence remaining low. Indicates a knowledge area that the current modules consistently fail to populate.

## Output contract

**One file only:** `.wabblespec/memory/instinct-observations.md`

Format:

```markdown
# Instinct Observations

Generated: ISO-8601
Receipt corpus size: N
Observation window: first_receipt_date — last_receipt_date

## Observed Patterns

### Pattern 1: <short name>

Type: high-frequency-failure | co-occurrence-cluster | recurring-gap
Confidence: low | medium | high
Evidence: <receipt IDs or entity-graph nodes that support this pattern>
Occurrences: N across M distinct executions
Human-validated: false

<one paragraph description — what was observed, not what to do about it>

---
```

`Human-validated: false` by default. A human changes this to `true` after reviewing the pattern. No pattern becomes a Synth input until validated.

## Hard boundaries

**Instinct MUST NOT:**

- Write to any file outside `.wabblespec/memory/instinct-observations.md`
- Invoke or reference Synth, Blueprint, Factory, Augment, or Forge
- Produce improvement proposals, change recommendations, or module patches
- Modify any receipt, task card, skill file, or schema
- Claim a pattern is real without meeting the occurrence thresholds above
- Run during an active execution wave (check for Executor PID lock before starting)

If Instinct finds itself writing anything that resembles a recommendation ("module X should..."), stop. Observations describe what was seen. Actions belong to Synth, which Instinct does not touch.

## Synth gate (separate from Instinct activation)

Synth cannot be invoked until:

1. Instinct has produced ≥ 3 patterns with `Human-validated: true` in `instinct-observations.md`
2. Each validated pattern has `Confidence: medium` or `high`
3. A human explicitly confirms Synth activation in writing

Instinct does not enforce this gate — it has no knowledge of Synth. This gate is documented here as a hard constraint for whoever invokes Synth. Instinct's job ends at the observation log.

## How to run

```
python modules/l8/instinct/scripts/instinct.py --activate
python modules/l8/instinct/scripts/instinct.py --dry-run
python modules/l8/instinct/scripts/instinct.py --status
```

`--status` reports current receipt count vs gate threshold without activating.
`--dry-run` reports what patterns would be detected without writing the observation log.
`--activate` runs full observation and writes `instinct-observations.md`.

Run from project root. `WABBLESPEC_MEMORY_PATH` must be set.

## What was not taken from graphify-7

- **AST extraction and code graph building**: Instinct observes receipt metadata, not source code structure
- **HTML visualization**: no visualization layer — observation log is the output
- **Semantic subagent dispatch**: Instinct is deterministic, no LLM involvement in pattern detection
- **Auto-promotion or Synth invocation**: graphify-7 has no equivalent; this boundary is WabbleSpec-specific
- **Incremental update / watch mode**: Instinct runs as a session-level batch operation, not a background watcher
