# Engineering Gateway — Code Quality Standards

Universal floors that apply regardless of platform. Platform modules handle platform-specific linting rules.

---

## Test Coverage

**Floor:** 80% line coverage for business logic code.

This is a floor, not a target. Aiming for exactly 80% is the wrong goal — it incentivizes testing easy paths to hit the number. The floor exists to catch untested modules, not to drive coverage theater.

**What counts toward coverage:**
- Unit tests for pure logic functions
- Integration tests that exercise real code paths

**What does not count:**
- Generated code (ORMs, protobuf output, OpenAPI clients)
- Framework boilerplate (dependency injection setup, middleware wiring)
- Third-party adapters

**Measurement:**
```bash
# Node/TypeScript
npx jest --coverage --coverageThreshold='{"global":{"lines":80}}'

# Python
pytest --cov=src --cov-fail-under=80

# Go
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out | tail -1  # check total

# Rust
cargo tarpaulin --fail-under 80
```

**Coverage must be enforced in CI**, not just reported. Pipeline fails if coverage drops below floor.

---

## Linting and Type Checking

**Rule:** Zero lint errors. Zero type errors. Not "zero new errors" — zero total.

Zero-error requirement exists because teams that tolerate existing errors cannot enforce "no new errors" — reviewers cannot distinguish new from existing in diff view.

**Per language:**

| Language | Linter | Type checker |
|---|---|---|
| TypeScript | ESLint (strict) | `tsc --noEmit` (strict mode) |
| Python | Ruff (replaces flake8 + isort + pyupgrade) | mypy (strict) or pyright |
| Go | `golangci-lint` | Built-in (go vet) |
| Rust | `cargo clippy -- -D warnings` | Built-in |

**TypeScript strict mode required:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

**Python mypy strict config:**
```ini
[mypy]
strict = true
warn_return_any = true
disallow_untyped_defs = true
```

---

## Code Complexity

**Cyclomatic complexity limit:** 10 per function. Functions above 10 must be decomposed.

Why 10: above this threshold, the number of test cases required for full branch coverage grows faster than most teams maintain. Functions with complexity > 15 are consistently found to have latent bugs.

**Cognitive complexity limit:** 15 per function (measured by SonarQube, Ruff, or eslint-plugin-sonarjs).

**Measurement:**
```bash
# Python — radon
radon cc src/ -a -nc  # show functions with complexity C or higher (> 5)
radon cc src/ --max-complexity 10  # fail on any function > 10

# TypeScript — eslint rule
# "sonarjs/cognitive-complexity": ["error", 15]

# Go — gocyclo
gocyclo -over 10 .
```

**Gate behavior:** CI fails if any function exceeds complexity limit. Decompose before merging.

---

## Technical Debt Density

**TODO/FIXME limit:** Maximum 1 per 200 lines of code (non-test source).

**Rule:** Every TODO/FIXME must include:
- What needs to be done (already required by the comment itself)
- A tracking reference: issue number, ticket ID, or date

```python
# Acceptable:
# TODO(#234): replace this with streaming upload once S3 client supports it

# Not acceptable:
# TODO: fix this later
# FIXME: this is broken
```

**Measurement:**
```bash
# Count TODOs with no tracking reference
grep -rn 'TODO\|FIXME' src/ --include="*.py" --include="*.ts" --include="*.go" \
  | grep -vE 'TODO\(#[0-9]+\)|TODO\([A-Z]+-[0-9]+\)|FIXME\(#[0-9]+\)'
# Expected: zero matches
```

---

## TDD Policy

**Rule:** Production code requires a failing test first.

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

This is not advisory. Skipping it removes the proof that the test actually validates the behavior. Tests written after implementation pass immediately — which proves nothing.

### Red-Green-Refactor cycle

| Phase | Action | Required verification |
|---|---|---|
| RED | Write one minimal failing test | Run test — confirm it fails for the right reason, not a typo |
| GREEN | Write minimal code to pass the test | Run test — confirm it passes; confirm other tests still pass |
| REFACTOR | Remove duplication, improve names | Run tests — confirm still green; no new behavior added |

**Mandatory steps:** RED verification and GREEN verification cannot be skipped. A test that passes before implementation exists is testing existing behavior — fix the test.

### Test quality criteria

| Criterion | Good | Bad |
|---|---|---|
| Minimal | Tests one behavior; "and" in name = split it | `test('validates email and domain')` |
| Clear | Name describes the behavior | `test('test1')`, `test('works')` |
| Real code | Uses real dependencies (mocks only when unavoidable) | Tests mock behavior, not production behavior |
| Fails correctly | Failure message shows what was expected | Test errors on setup, not on assertion |

### TDD anti-patterns

- Code before test — delete the code, start over
- Test written after implementation — does not count as TDD; re-do in TDD order
- Test passes immediately on first run — you are testing existing behavior, not new behavior; fix the test
- Mocking everything — design is too coupled; apply dependency injection
- Test setup longer than the test itself — simplify the interface, not the setup
- "I already manually tested it" — manual testing is not systematic and cannot be re-run
- "Tests after achieve the same goals" — tests-after ask "what does this do?"; tests-first ask "what should this do?"

### Exceptions

Only with explicit human partner agreement:
- Throwaway prototypes (must be deleted before merging)
- Auto-generated code
- Configuration-only files with no logic

---

## Dead Code

**Rule:** No unreachable code, unused imports, or unused exported symbols in non-test source.

**Measurement:**
```bash
# TypeScript — tsc catches some; ts-prune for exports
npx ts-prune

# Python — vulture
vulture src/ --min-confidence 80

# Go — built-in: go vet detects unreachable; gopls for unused
staticcheck ./...

# Rust — compiler warns on dead code by default
# Add to CI: cargo build 2>&1 | grep "dead_code"
```

**Exception:** Public API symbols in libraries are not dead code — they are the product. Exclude them from dead code analysis via configuration.
