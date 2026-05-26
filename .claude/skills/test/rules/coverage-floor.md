# Coverage Floor — Test

## Every requirement has at least one stub

No EARS requirement in the spec artifact is skipped. Every requirement produces at least one test stub. This is a hard floor — not a target to optimize toward.

## Counting

Requirements covered = EARS requirements with at least one stub generated.
Requirements untestable = EARS requirements flagged with UNTESTABLE marker.

Coverage floor: `requirements_covered + requirements_untestable = requirements_total`

If this equation does not hold, a requirement was silently dropped — that is a violation.

## Engineering gateway floor

The Engineering gateway sets the minimum acceptable test coverage percentage for the platform. Test reads this floor from the active Engineering gateway receipt and records it in the test plan.

If the Engineering gateway has not set a floor: default to 100% of EARS requirements covered (stubs or explicitly flagged as untestable).

## What counts as covered

A requirement is covered when:
- At least one stub exists that references it by requirement ID
- The stub has a declared expected behavior (not an empty placeholder)

A stub with `expected: TBD` does not count as covered — it is an incomplete stub and must be flagged.

## Stub completeness check

Before writing the test plan, verify every stub has:
- `requirement_ref` populated
- `type` populated
- `expected` populated (not TBD, not empty)

Incomplete stubs are flagged in the test plan as `INCOMPLETE` in the Status column.
