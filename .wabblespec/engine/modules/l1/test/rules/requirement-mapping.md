# Requirement Mapping Rules — Test

## EARS pattern to test type mapping

Every EARS requirement maps to at least one test case. Use the pattern table to determine which test types to generate.

| EARS pattern | Test case types | Notes |
|---|---|---|
| WHEN \<trigger\> THEN \<behavior\> | Positive case + boundary case | Boundary: trigger at edge of valid input range |
| IF \<condition\> WHEN \<trigger\> THEN \<behavior\> | Positive case + condition-not-met case | Condition-not-met: trigger fires but condition is false |
| WHILE \<state\> THEN \<behavior\> | State-entry test + state-exit test | State-exit: verify behavior stops when state exits |
| WHERE \<feature\> SHALL \<property\> | Property assertion test | Assert the property holds under representative inputs |
| THE \<system\> SHALL \<capability\> | Capability smoke test | Verify capability is reachable and produces output |

## Test type selection

| Test type | When to use |
|---|---|
| unit | Single function or method, no I/O, no external dependencies |
| integration | Two or more modules interacting, or a module + one external dependency |
| e2e | Full user-facing flow from input to observable output |
| acceptance | Maps directly to an acceptance criterion in the spec — validates spec promise, not implementation |

Select the lowest-cost type that meaningfully covers the requirement. Use unit when the behavior is contained. Use e2e only when the requirement describes a full flow.

## Multiple requirements per test

A single test may cover multiple requirements only when:
- Requirements are logically coupled (one is a precondition of the other)
- They are in the same EARS clause group

When a test covers multiple requirements, list all requirement IDs in `requirement_ref`.

## Requirement ID format

Reference requirements by their spec artifact ID: `<spec-id>-REQ-<number>`. Example: `feat-auth-REQ-003`. IDs are assigned by Specify in the P4 artifact.
