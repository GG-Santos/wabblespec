# Gateway Engineering — Code Quality Policy

Rules enforced by gateway-engineering Phase B verdict. Any spec at Medium complexity or above, or any target approaching production deployment, must satisfy all applicable rules below. Violations produce FLAG or BLOCK verdicts.

---

## Rule Q1: Test Coverage Floor

**Requirement:** Every production target must declare a test coverage target in the spec (task card or technical-spec.md). Minimum floors by scope:

| Coverage type | Minimum floor | Notes |
|---|---|---|
| Unit coverage (statements) | 80% | Enforced by CI; pipeline fails below floor |
| Integration coverage (critical paths) | One test per declared user flow or API endpoint | Not a percentage — must be enumerable |
| End-to-end | One scenario per P0 user flow | P0 = core happy path that earns product value |

**Failure modes:**
- No coverage target declared in spec = FLAG
- CI pipeline not configured to fail on coverage drop below floor = FLAG
- Coverage target declared but not enforced in CI = BLOCK (unenforced targets provide no quality signal)

**Exception:** Library targets (no runtime execution path) may substitute mutation testing score (>= 70%) for statement coverage.

---

## Rule Q2: Cyclomatic Complexity Limits

**Requirement:** Cyclomatic complexity is enforced at the function level by a linter rule, not by convention.

| Complexity threshold | Action |
|---|---|
| <= 10 per function | Permitted |
| 11–15 per function | FLAG — document rationale in spec; refactor recommended |
| > 15 per function | BLOCK — must refactor before promotion |

Cognitive complexity limit: <= 15 per function. Measured by tools capable of cognitive complexity scoring (SonarQube, CodeClimate, or language-native linter rules where available).

**Failure modes:**
- No linter rule enforcing complexity = FLAG
- Functions exceeding BLOCK threshold present in PR = BLOCK
- Linter configured to warn-only on complexity violations = FLAG (must be error-level)

---

## Rule Q3: Technical Debt Density Limits

**Requirement:** TODO and FIXME comments are tracked as technical debt. The spec must declare a debt policy.

| Debt type | Threshold | Action |
|---|---|---|
| TODO without ticket reference | Any | FLAG — every TODO must reference a ticket ID |
| FIXME without ticket reference | Any | BLOCK — FIXME indicates known defect; must be tracked |
| Total TODO+FIXME per 1000 lines of code | > 5 | FLAG |
| TODOs older than 90 days (git blame) | Any | FLAG with staleness warning |

**Failure modes:**
- FIXME present without referenced ticket = BLOCK
- No tooling to track or count debt comments = FLAG
- Debt density exceeding 5/1000 LoC with no remediation plan = FLAG

---

## Rule Q4: Documentation Completeness

**Requirement:** Every production target must have a README satisfying all of:

| Section | Required content |
|---|---|
| Overview | One-paragraph description of what the project does and who it is for |
| Setup | Steps to get a development environment running from scratch (reproducible) |
| Usage | How to run the primary workflow; at minimum one complete example |
| Testing | How to run the test suite |
| Contributing | Branching convention, PR requirements, and reviewer count |

**Failure modes:**
- README absent = BLOCK
- README missing Setup or Usage = FLAG
- Setup steps not reproducible (references "your local config") = FLAG

Public-facing libraries additionally require: API reference or link to generated docs, changelog reference, license declaration.

---

## Rule Q5: CI Pipeline Requirements

**Requirement:** Every production target must have a CI pipeline that runs on every PR and on merge to main.

**Required CI steps (all must pass before merge):**

| Step | Requirement |
|---|---|
| Lint | All declared linting rules pass; no warning-only mode for error-class rules |
| Test suite | All tests pass; coverage floor enforced |
| Dependency audit | `npm audit` / `pip audit` / `cargo audit` (or equivalent); CRITICAL findings block merge |
| Build | Clean build from source; no cached artifacts bypassing build |
| Type check | If typed language: type checker passes with no suppressed errors |

**Failure modes:**
- No CI pipeline = BLOCK
- CI runs but does not enforce passing (green-only theater) = BLOCK
- Dependency audit step absent = FLAG
- Manual bypass of CI required for any production merge = BLOCK

---

## Rule Q6: Code Review Standards

**Requirement:** Every production PR requires review before merge.

| Criterion | Requirement |
|---|---|
| Minimum reviewer count | 1 for Low, 2 for Medium+, 2 with security reviewer for auth/crypto changes |
| Self-merge | Not permitted for production branches |
| Stale review invalidation | Any new push after approval invalidates prior approval |
| What reviewers check | Spec compliance, test coverage delta, complexity delta, breaking changes |

**Failure modes:**
- No branch protection requiring review = BLOCK
- Self-merge permitted on main/production = BLOCK
- Auth/crypto changes reviewed without security reviewer = FLAG
