# Test Stub Template — Test

One stub file per spec artifact, containing all stubs for that artifact. Write to `project/repo/tests/<spec-id>/`.

## Stub format

```markdown
## Test: <requirement-id> — <test name>

**requirement_ref:** <EARS requirement text — quoted exactly from spec>
**type:** unit|integration|e2e|acceptance
**framework:** <framework name from platform package — e.g. Jest, pytest, Go test, RSpec>
**input:** <declared input — be specific about type and representative value>
**expected:** <declared expected behavior — observable outcome, not internal state>
**setup:** <any preconditions — state that must be true before the test runs>
**teardown:** <any cleanup — state to restore after the test runs>

<!-- STUB: replace with implementation -->
```

## Multiple test cases per requirement

When a requirement produces multiple test cases (e.g. positive + boundary), write each as a separate stub block with a disambiguating name:

```markdown
## Test: feat-auth-REQ-003 — token accepted when valid

## Test: feat-auth-REQ-003 — token rejected at boundary (expiry = now)
```

## Untestable stub

```markdown
## Test: <requirement-id> — <requirement name>

<!-- UNTESTABLE: <specific reason> -->
```

## Naming convention

`<requirement-id> — <short description of what is being tested>`

Description should complete the sentence "This test verifies that..." without the prefix. Example: `token is accepted when valid` not `verify token accepted`.
