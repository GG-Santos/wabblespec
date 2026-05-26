# Outcome Requirement — Benchmark

Every eval case must declare the developer outcome being measured before any metric claim.

## Outcome declaration format

```
outcome: "Did [X] produce [Y result] for [who]?"
```

Examples:
- `outcome: "Did the auth module return a valid JWT for a well-formed login request?"`
- `outcome: "Did the code generator produce compilable output for a simple CRUD spec?"`
- `outcome: "Did the search endpoint return results within 200ms for a typical user query?"`

## Rules

1. The `outcome` field must appear in the eval case before any metric fields (`accuracy`, `latency`, `precision`, `recall`, `f1`, etc.).
2. Metric claims without an `outcome` declaration are a SPEC_VIOLATION in Benchmark.
3. The outcome statement must name: the capability being tested (X), the expected result (Y), and the affected party (who).
4. Abstract outcomes ("Did it work?") are invalid — reject with SPEC_VIOLATION and require a rewrite.

## Enforcement

**Block promotion** if any eval case in the benchmark run lacks a populated `outcome` field.

Benchmark receipt must include:
```json
{
  "outcome_compliance": "PASS|FAIL",
  "missing_outcome_cases": ["eval-case-id — list of cases missing outcome field"]
}
```

`outcome_compliance: FAIL` → `overall: FAIL`. Cannot promote to corpus.

## Rationale

Metrics without outcomes are uninterpretable. A 95% accuracy score means nothing without knowing what question it answers or for whom. Outcome declarations force the benchmark author to be explicit about what success means before measuring it.

## Reference

Defect pattern: DP-21 (Benchmark Metric Without Outcome) in `_shared/references/defect-patterns.md`.
