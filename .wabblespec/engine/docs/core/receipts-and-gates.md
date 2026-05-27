# Receipts and Gates

Receipts are the enforcement mechanism. Every module that does meaningful work writes a receipt. The pipeline does not advance without a PASS receipt from the previous stage.

## Receipt anatomy

All receipts follow the base schema at `.wabblespec/engine/shared/schemas/receipt.base.schema.json`.

Required fields in every receipt:
```json
{
  "receipt_type": "string — module name (executor, verifier, delivery, etc.)",
  "run_id": "string — identifies the pipeline run",
  "status": "PASS | FAIL | PARTIAL | BLOCKED",
  "timestamp": "ISO 8601 UTC"
}
```

Additional fields are module-specific. Receipt schemas live at `modules/l{N}/{name}/schemas/`.

## Receipt naming

```
{module}-receipt-{run-id}.json
```

Examples:
- `executor-receipt-seed-run-20260524c.json`
- `delivery-receipt-seed-run-20260524a.json`
- `gateway-security-receipt-20260525a.json`

All receipts land in `.wabblespec/state/receipts/`. Archived runs are indexed in `.wabblespec/state/archive/receipt-index.json`.

## Receipt authority

Each module may only write receipts for itself (`authority.owns` in `skill-rules.json`). Writing to another module's receipt namespace is an invariant violation (I3).

## Status semantics

| Status | Meaning | Pipeline behavior |
|--------|---------|-------------------|
| PASS | Module completed successfully, all checks passed | Next stage runs |
| FAIL | Module failed, documented reason | Pipeline halts. Do not proceed. |
| PARTIAL | Partial completion — not all outcomes achieved | Escalate to human. Do not auto-advance. |
| BLOCKED | Module blocked by a guard or gateway | Halt. Surface block reason. Require human resolution. |

## Quality floor gates

The quality floor is a pre-execution gate. Run before any pipeline that modifies modules.

**Gate 1 — quick_validate** (8 checks):

| Check | What it tests |
|-------|--------------|
| SKILL_EXISTS | `SKILL.md` file is present |
| RULES_EXISTS | `skill-rules.json` is present |
| RULES_PARSE | `skill-rules.json` is valid JSON |
| REQUIRED_FIELDS | All 7 required fields present: `module`, `layer`, `tier`, `activators`, `authority.owns`, `verification_mode`, `receipt_required` |
| AUTHORITY_OWNS | `authority.owns` is non-empty array |
| AUTHORITY_READS | `authority.reads` exists (may be empty) |
| RECEIPT_BOOL | `receipt_required` is a boolean |
| ACTIVATORS_VALID | `activators` is non-empty OR `loading_gate` is set OR `commands` is non-empty |

**Gate 2 — lint_prompts** (6 checks):

| Check | What it tests |
|-------|--------------|
| FRONTMATTER | SKILL.md has valid YAML frontmatter with `name:` and `description:` |
| DESCRIPTION_LEN | `description:` field is at least 20 characters |
| SECTION_WHAT | Contains `## What this skill does` heading |
| SECTION_WHEN | Contains `## When to use` heading |
| SECTION_OUTPUT | Contains an output signal (`## Output`, `## What this produces`, `## Produces`, `## Receipt`, `## Writes`) |
| MIN_LENGTH | Body content is at least 200 characters |

**Run:** `python .wabblespec/engine/shared/scripts/quality-floor-check.py --framework framework.yaml`
**Current status:** 96/96 modules PASS (as of VERSION 0.3.6).

## L8 evolution gate

The L8 gate unlocks the Evolution layer (Benchmark, Blueprint, Augment, Synth, Instinct, Factory).

Requirements:
1. **100+ PASS receipts** across real pipeline runs
2. **3 human-validated Instinct patterns** — patterns extracted from run history and confirmed by human
3. **Benchmark schema** — `.wabblespec/engine/shared/schemas/benchmark.schema.json` must be present and valid

**Current status (VERSION 0.3.6):** 19/100 PASS receipts. Gate NOT cleared.

## Integration gate (Phases 5-6)

Integration phases 5-6 are gated on 10+ complete pipeline runs (Recipe through Archive). Not the same as 10+ receipts — 10 full end-to-end runs.

**Current status:** 3 complete runs. Gate NOT cleared.

## Validate-graph tool

Validates that all `depends_on` and shared file `consumers` in `framework.yaml` reference valid module IDs (A7 rule — no script paths, no generic descriptions).

**Run:** `python .wabblespec/engine/shared/scripts/validate-graph.py --framework framework.yaml`
**Current status:** 0 violations.
