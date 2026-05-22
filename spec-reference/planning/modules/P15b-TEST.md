# Module Plan — Test (L1)

**Tier:** 2 — FOUNDATION
**Layer:** L1 Spec Core
**v5.3 origin:** Test module — spec-driven test generation and test strategy

---

## Purpose

Generate test stubs and test strategy from spec acceptance criteria. Every EARS requirement in a P4 spec maps to at least one test case. Test does not execute tests — it generates stubs and a test plan that Verifier's Test mode uses for verification. Untestable requirements are flagged as gaps, not silently skipped.

---

## Activation

`skill-rules.json` triggers:
- P4 spec stage completion (test stubs generated from feature specs)
- Explicit `/test <spec-artifact>` command
- Verifier Test mode (Verifier reads Test module output for coverage check)
- Executor wave producing new functionality (Test stubs generated for new code)

---

## Requirement-to-Test Mapping

Each EARS requirement produces at least one test case:

| EARS pattern | Test case types generated |
|---|---|
| WHEN <trigger> THEN <behavior> | Positive case (trigger fires, behavior observed) + boundary case |
| IF <condition> WHEN <trigger> THEN <behavior> | Positive case + condition-not-met case |
| WHILE <state> THEN <behavior> | State-entry test + state-exit test |
| WHERE <feature> SHALL <property> | Property assertion test |
| THE <system> SHALL <capability> | Capability smoke test |

Untestable requirement: flagged with marker `<!-- UNTESTABLE: <reason> -->` and written to not-tested compilation.

---

## Test Stub Format

```markdown
## Test: <requirement-id> — <test name>

**requirement_ref:** EARS requirement text
**type:** unit|integration|e2e|acceptance
**framework:** <from platform package testing conventions>
**input:** <declared input>
**expected:** <declared expected behavior>
**setup:** <any preconditions>
**teardown:** <any cleanup>

<!-- STUB: replace with implementation -->
```

---

## Test Plan Structure

```markdown
# Test Plan — <spec artifact>

**generated_from:** spec artifact path
**generated_at:** timestamp
**requirements_covered:** integer
**requirements_untestable:** integer

## Coverage Matrix

| Requirement ID | EARS Pattern | Test Cases | Status |
|---|---|---|---|
| REQ-001 | WHEN/THEN | 2 | STUB |

## Untestable Requirements

| Requirement ID | Reason |
|---|---|
| REQ-042 | Requires physical hardware not available in CI |

## Test Framework

<platform-appropriate test runner and structure>
```

---

## Workflow

```
1. Read spec artifact (P4 feature spec or technical spec)

2. Extract all EARS requirements

3. For each requirement:
   -> Map to test case types (per EARS pattern table)
   -> Generate test stub
   -> Flag untestable requirements

4. Read platform package testing conventions for framework selection

5. Write test stubs to project/repo/tests/ (I11 — test files are product files)

6. Write test plan to .wabblespec/plans/test-plan-<spec-id>.md

7. Write Test receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — P4 stage, Verifier consultation |
| `rules/requirement-mapping.md` | Rules | EARS pattern to test type mapping |
| `rules/coverage-floor.md` | Rules | Every requirement has at least one test case |
| `rules/untestable-policy.md` | Rules | Untestable requirements flagged, not skipped |
| `templates/test-stub.md` | Template | Stub format per test type |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Specify | Test reads Specify's EARS requirements from P4 spec artifacts |
| Verifier | Verifier Test mode reads Test plan for coverage check |
| Platform packages (L3) | Platform testing conventions (framework, runner) inform stub generation |
| Engineering gateway | Coverage floor policy set by Engineering gateway |
| Archive | Archive reads not-tested compilation (untestable requirements) |

---

## Verification Mode

**Observation** — all EARS requirements have at least one stub, untestable requirements flagged and documented, test plan written, receipt written.

---

## Receipt Extension Fields

```json
{
  "spec_artifact": "string",
  "requirements_total": "integer",
  "requirements_covered": "integer",
  "requirements_untestable": "integer",
  "stubs_generated": "integer",
  "test_plan_path": "string"
}
```
