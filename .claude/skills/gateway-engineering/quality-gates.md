# Engineering Gateway — Quality Gates

Registered with Verifier at gateway activation. Supplement platform gates — do not replace them. All gates blocking before Delivery wave.

---

## Gate 1: Type Check and Lint — Zero Errors

**Check:** Zero type errors. Zero lint errors. Not warnings — errors.

**Method:**
```bash
# TypeScript
npx tsc --noEmit
npx eslint src/ --max-warnings 0

# Python
mypy src/ --strict
ruff check src/

# Go
go vet ./...
golangci-lint run ./...

# Rust
cargo clippy -- -D warnings
```

**Pass:** All commands exit 0 with zero error output.
**Fail:** Any error. Each error must be fixed — not suppressed with inline ignore comments unless accompanied by documented justification.

**Inline suppression policy:**
- Allowed: `// eslint-disable-next-line rule-name -- reason`
- Banned: `// eslint-disable-file` or blanket disable without reason
- Every suppression is a code review item

---

## Gate 2: Test Coverage Floor

**Check:** Line coverage for business logic code meets declared floor (default: 80%).

**Method:**
```bash
# TypeScript/JavaScript
npx jest --coverage \
  --coverageThreshold='{"global":{"lines":80,"branches":70,"functions":80}}'

# Python
pytest --cov=src --cov-fail-under=80 --cov-report=term-missing

# Go
go test ./... -coverprofile=coverage.out
COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | tr -d '%')
[ "${COVERAGE%.*}" -ge 80 ] || { echo "FAIL: coverage ${COVERAGE}% < 80%"; exit 1; }

# Rust
cargo tarpaulin --fail-under 80 --exclude-files "src/main.rs"
```

**Pass:** Coverage at or above declared floor.
**Fail:** Coverage below floor. Action: write tests for uncovered paths — do not exclude files to inflate the number.

**Exclusion policy:** Generated code, framework boilerplate, and third-party adapters may be excluded. Exclusions must be declared in coverage config (not inline `// istanbul ignore`).

---

## Gate 3: Code Complexity

**Check:** No function exceeds declared complexity limits (cyclomatic ≤ 10, cognitive ≤ 15).

**Method:**
```bash
# Python — radon
radon cc src/ --max-complexity 10 -n C  # fail on any function rated C or higher

# TypeScript — eslint rule (must be configured in .eslintrc):
# "complexity": ["error", 10]
# "sonarjs/cognitive-complexity": ["error", 15]
npx eslint src/ --rule 'complexity: ["error", 10]'

# Go — gocyclo
gocyclo -over 10 .

# Rust — (no standard tool; enforce via code review)
```

**Pass:** Zero functions exceed limit.
**Fail:** Any function over limit. Action: decompose before merging. No complexity-limit waiver without written justification and team agreement.

---

## Gate 4: Unused Code

**Check:** No unused imports, dead code, or unreachable branches in non-test source.

**Method:**
```bash
# TypeScript — ts-prune (unused exports)
npx ts-prune | grep -v "used in module"

# Python — vulture
vulture src/ --min-confidence 80

# Go
staticcheck -checks="U*" ./...  # unused checks

# Rust — compiler enforces this; ensure no #[allow(dead_code)] in production code
grep -rn '#\[allow(dead_code)\]' src/ --include="*.rs" | grep -v test
```

**Pass:** Zero unused symbols in non-test source (beyond declared exclusions).
**Fail:** Any finding. Remove dead code before merging — do not suppress.

---

## Gate 5: Dependency Freshness

**Check:** No direct dependency more than 2 major versions behind current stable.

**Method:**
```bash
# Node
npm outdated  # review Major column — flag any where "Wanted" major < "Latest" major by 2+

# Python
pip list --outdated --format=columns

# Go
go list -u -m all | grep '\[' | awk '{print $1, $2, $3}'  # shows available upgrades

# Rust
cargo outdated --root-deps-only  # direct deps only
```

**Pass:** No direct dependency 2+ major versions behind.
**Fail:** Any direct dependency 2+ major versions behind. Action: open upgrade ticket — do not block indefinitely. Gate blocks release until ticket is created and assigned.

---

## Gate 6: README Accuracy

**Check:** README "how to run locally" commands work on a clean environment.

**Method:**
```bash
# In a fresh directory or container with only declared prerequisites installed:
git clone <repo>
cd <repo>
# Follow README step by step — no tribal knowledge allowed
# Document any step that fails
```

**Pass:** Every step in README works exactly as written.
**Fail:** Any step fails, requires knowledge not in README, or is out of date. Action: update README before marking Delivery wave complete.

**Automated check (partial):**
```bash
# Verify declared commands exist
grep -oE '`[a-z].*`' README.md | tr -d '`' | while read cmd; do
  BINARY=$(echo "$cmd" | cut -d' ' -f1)
  command -v "$BINARY" > /dev/null 2>&1 || echo "WARNING: $BINARY not found"
done
```

---

## Gate 7: CI Pipeline Compliance

**Check:** CI pipeline includes all required stages (type check, tests, security audit, build, smoke test).

**Method (manual checklist):**
- [ ] Type check / lint stage present and required to pass
- [ ] Unit tests stage present and required to pass
- [ ] Dependency audit stage present (npm audit / pip-audit / cargo audit)
- [ ] Build stage produces deployable artifact
- [ ] Smoke test stage runs built artifact and checks it starts
- [ ] No "merge anyway" override without documented approval

**Pass:** All 6 items checked.
**Fail:** Any item unchecked. Action: add missing stage before Delivery wave.

---

## Gate 8: TDD Compliance

**Check:** New production code has corresponding tests; completion claims are backed by command evidence.

**Method — test existence check:**
```bash
# For each new non-test file added in this wave, confirm a test file exists:
git diff --name-only HEAD~1 | grep -v test | grep -v spec \
  | grep -E '\.(py|ts|js|go|rs)$'
# For each path returned, a corresponding test file must exist in the test tree.

# Confirm tests actually ran (not just that they exist):
# Include full test command output in the wave receipt — not a summary, the actual output.
```

**Method — verification checklist (must be completed before PASS claim):**
- [ ] Every new public function or method has at least one test
- [ ] Each test was watched to fail before the implementation was written (or explicitly noted as exception)
- [ ] Each test failed for the expected reason (missing feature, not setup error or typo)
- [ ] Minimal code was written to pass each test (no feature-flag pre-loading)
- [ ] All tests pass after implementation
- [ ] Test output is clean — no errors, no skipped tests without documented reason
- [ ] No inline mock replacing real behavior unless documented
- [ ] Edge cases covered or explicitly noted in `not_tested`

**Pass:** All checklist items confirmed. Full test command output present in wave receipt.
**Fail:** Any item unchecked without documented exception. Completion claim without fresh test output. New module with no test file.

**Evidence requirement:** "Tests pass" is not a valid claim unless the test command output for this session appears in the wave receipt. Partial checks ("linter passed so tests should pass") do not qualify.

**Exceptions:** Same as TDD policy in code-quality.md — only with explicit human agreement: throwaway prototypes (deleted before merge), generated code, config-only files.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Zero type errors + zero lint errors | Yes |
| 2 | Test coverage ≥ declared floor (default 80%) | Yes |
| 3 | Cyclomatic complexity ≤ 10 per function | Yes |
| 4 | No unused code in non-test source | Yes |
| 5 | No direct dependency 2+ major versions behind | Yes |
| 6 | README "how to run locally" works on clean environment | Yes |
| 7 | CI pipeline includes all required stages | Yes |
| 8 | TDD compliance: test existence + completion evidence | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.

These gates run in addition to L3 platform gates, not instead of them.
