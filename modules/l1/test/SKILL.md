---
name: test
description: Generates test stubs and test strategy from spec acceptance criteria. Every EARS requirement in a P4 spec maps to at least one test case. Untestable requirements are flagged, not silently skipped. Does not execute tests — produces stubs and test plan that Verifier's Test mode uses.
---

# Test

You translate EARS requirements into test stubs. You do not execute tests — that is Verifier's job. You generate the map that Verifier follows. Every requirement gets at least one stub. Untestable requirements are flagged explicitly — never silently skipped.

## When to activate

- P4 spec stage completion (test stubs generated from feature specs)
- Explicit `/test <spec-artifact>` command
- Verifier Test mode (reads Test module output for coverage check)
- Executor wave producing new functionality (stubs generated for new code)

## Requirement-to-test mapping

| EARS pattern | Test case types generated |
|---|---|
| WHEN \<trigger\> THEN \<behavior\> | Positive case + boundary case |
| IF \<condition\> WHEN \<trigger\> THEN \<behavior\> | Positive case + condition-not-met case |
| WHILE \<state\> THEN \<behavior\> | State-entry test + state-exit test |
| WHERE \<feature\> SHALL \<property\> | Property assertion test |
| THE \<system\> SHALL \<capability\> | Capability smoke test |

Untestable requirement: flag with `<!-- UNTESTABLE: <reason> -->` and write to not-tested compilation.

## Workflow

1. Read spec artifact (P4 feature spec or technical spec)
2. Extract all EARS requirements
3. For each requirement:
   - Map to test case types per EARS pattern table
   - Generate test stub
   - Flag untestable requirements
4. Read platform package testing conventions for framework selection
5. Write test stubs to `project/repo/tests/` (I11 — test files are product files)
6. Write test plan to `.wabblespec/plans/test-plan-<spec-id>.md`
7. Write Test receipt

## Test stub format

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

## Test plan format

Write to `.wabblespec/plans/test-plan-<spec-id>.md`:

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

## Test Framework

<platform-appropriate test runner and structure>
```

## What not to do

- Do not execute tests — generate stubs only
- Do not skip untestable requirements — flag them explicitly
- Do not write test stubs outside `project/repo/tests/`
- Do not infer test framework — read it from the active platform package
- Do not generate stubs without reading the spec artifact first
