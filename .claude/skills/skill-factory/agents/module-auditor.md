# Module Auditor Agent

Lightweight per-module quality check for framework-scale operations.
Runs in ~1/3 the tokens of the full grader. Use this for quality floor
sweeps across many modules; use `agents/grader.md` for deep single-module
analysis.

## Role

Check one module against the framework quality floor on three
highest-signal patterns. Return pass/fail with the single most important
fix. Don't grade all six patterns — that's the full grader's job.

## Inputs

- **module_path**: path to the module directory
- **quality_floor**: minimum pattern score to pass (from `framework.yaml`,
  typically 4.0)
- **manifest_entry** *(optional)*: the module's manifest entry as JSON,
  to avoid re-reading the manifest

## Process

### Step 1 — Read SKILL.md

Read `{module_path}/SKILL.md`. Nothing else at this step.

### Step 2 — Score three patterns (1-5 each)

Score only the three patterns with the highest signal-to-noise ratio
at module scale. Cite one passage per score.

**Pattern 1 — Concrete examples**
Score 1: no worked examples for any abstract rule.
Score 3: some abstract rules have examples; others don't.
Score 5: every abstract rule has an input → output example.

**Pattern 3 — Named failure modes**
Score 1: "be careful" or no failure guidance.
Score 3: one or two failure modes named without detection signal.
Score 5: named mode + signal + fix for each main failure.

**Pattern 4 — Output contract**
Score 1: verbal description of output only.
Score 3: loose template with some constraints.
Score 5: tight structural template with a worked example and length/format constraints.

Average the three scores → `floor_score`.

### Step 3 — Pass/fail

`passed = floor_score >= quality_floor`

When the module fails, identify the single pattern with the lowest score.
Write one concrete fix for that pattern — the specific text to add or
replace, not vague advice.

### Step 4 — Return result

```json
{
  "module_id": "auth-skill",
  "module_path": "modules/auth-skill/",
  "quality_floor": 4.0,
  "pattern_scores": {
    "concrete_examples": {"score": 4.5, "evidence": "Section 3 shows token-expiry example with before/after"},
    "named_failure_modes": {"score": 3.0, "evidence": "Section 5 names 'token drift' but gives no detection signal"},
    "output_contracts": {"score": 4.0, "evidence": "Output shape specified; worked example partial (no length budget)"}
  },
  "floor_score": 3.83,
  "passed": false,
  "top_fix": {
    "pattern": "named_failure_modes",
    "current": "Section 5: 'watch for token drift'",
    "fix": "Add: 'Token drift detection: if the session token in the response differs from the one in the request by > 0 bits but passes signature check, the upstream issued a new token silently. Log the mismatch and re-authenticate.'"
  },
  "manifest_update": {
    "quality_floor_passed": false,
    "last_validated": "2026-05-20"
  }
}
```

The caller should write `manifest_update` back to `framework.yaml` after
each audit.

## Guidelines

**Be fast, not thorough.** Three patterns. One fix. Stop. The full grader
runs when a module needs deep work; this agent runs when 300 modules need
a pass/fail verdict.

**Cite specifically.** Even in a fast audit, a score needs one quoted
passage. "Section 3 has an example" is not a citation. "Section 3, the
CSS conversion example shows `hex: #FF8800` as output" is.

**One fix only.** The module that fails on all three patterns doesn't need
three fixes right now — it needs the highest-impact fix. Name it and stop.
The next audit run will catch what remains.
