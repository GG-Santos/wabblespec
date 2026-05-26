# QA Pipeline Template (Platform-Agnostic)

> **Usage:** Copy into `modules/l3/[platform]/engineering/qa-pipeline.md`.
> Fill in the [PLATFORM-SPECIFIC] sections with framework-appropriate test tooling.
> The structure (test types, smoke protocol, regression strategy, evidence format) is identical across all platforms. Only the tooling sections vary.

---

## Test Classification

Every test belongs to exactly one type. Type determines automation potential, CI placement, and what counts as passing evidence.

| Type | Automation | Runs in CI | Evidence |
|---|---|---|---|
| **Logic** | Required | Yes — on every commit | Unit test passes; deterministic |
| **Integration** | Required | Yes — on every PR | Integration test passes in isolated environment |
| **End-to-End** | Required for critical paths | Yes — before any release | E2E test suite passes on representative environment |
| **Visual / Manual** | Not automatable | No | Written evidence record (see format below) |
| **Performance** | Required | Yes — nightly or pre-release | Profiler output within declared budget |
| **Config / Data** | Required | Yes | Schema validation passes; no malformed data |

**Logic tests:** State machines, business logic formulas, data transformations, edge case arithmetic. No network, no filesystem, no framework.

**Integration tests:** Two or more real systems interacting. Database queries, API calls to test instances, inter-service calls. Not mocked.

**E2E tests:** User-facing critical paths exercised from outside the system. Browser automation, device automation, or API client against a running instance.

**Visual / Manual tests:** Anything requiring human perception: "does this look right?", "does this feel responsive?", "is the animation smooth?". These cannot be automated — they require a written evidence record.

---

## [PLATFORM-SPECIFIC] Test Framework Scaffolding

> Replace this section with the platform's specific test tooling. See platform-specific files in each module's `engineering/qa-pipeline.md`.

---

## Smoke Test Protocol

The smoke test runs before any QA handoff or release candidate build. Must complete in ≤ 10 minutes. PASS/FAIL only — no partial credit.

**Critical path** (declare the exact steps):
1. [System starts / app launches]
2. [Primary authentication or entry flow]
3. [Core use case #1 — the most important thing the product does]
4. [Core use case #2 — the second most important thing]
5. [Exit / shutdown / logout — clean exit with no errors]

**Smoke test automation target:** Steps 1, 4, 5 are automatable for most platforms. Steps 2–3 may require human execution depending on platform.

**Smoke FAIL definition:** Any of the 5 steps fails, crashes, or produces an unhandled error. A failing smoke test blocks the build from reaching QA — do not proceed.

**Smoke test evidence:** For manual steps, record: tester, date, build version, pass/fail per step.

---

## Regression Suite Strategy

Every fixed bug produces one test that would have caught it. No exceptions.

**Rule:** Before a bug fix is merged, a test demonstrating the fixed behavior must exist and pass. The test must have failed before the fix.

**Test naming:**
```
[framework-test-prefix]_bug_[ID]_[short_description]
```

**Regression test structure:**
```
1. Reproduce the exact precondition that caused the bug
2. Execute the action that triggered the bug
3. Assert the correct post-fix behavior
```

**Suite maintenance:**
- Regression tests are never deleted.
- If a test becomes obsolete (feature removed), mark it `[SKIP reason="feature removed YYYY-MM-DD"]` — do not delete.
- QA lead reviews the regression suite before each release: any test marked SKIP for > 90 days requires a deletion review.

---

## Nightly vs. Commit CI Strategy

| When | What runs | Target duration |
|---|---|---|
| Every commit to any branch | Logic tests + Config/Data tests | < 2 minutes |
| Every PR | Logic + Integration + E2E critical path | < 15 minutes |
| Before release candidate | Full test suite + Performance + Smoke | < 45 minutes |
| Nightly | Full suite + extended soak/load tests | No limit — runs overnight |

If any step in the PR gate fails, the PR is blocked from merging. Performance and soak tests run nightly only — they are too slow for per-commit execution.

---

## Manual Test Evidence Format

For Visual/Manual tests that cannot be automated. One record per test. Stored in `tests/evidence/manual/` under version control.

```
Test ID:        [manual-NNN]
Type:           Visual / Manual
Name:           [What is being tested]
Tester:         [Name]
Date:           [YYYY-MM-DD]
Build/version:  [Commit hash or version string]
Environment:    [Device/browser/OS]

Precondition:   [Starting state]
Steps:
  1. [Step]
  2. [Step]
Expected:       [Correct behavior]
Actual:         [Observed behavior]
Result:         PASS / FAIL / NEEDS REVISION

Notes:          [Observations, edge cases seen]
Evidence path:  [Screenshot or recording file path]
```

Evidence records are linked from the relevant verification gate entry. Gate sign-off requires evidence records for all declared Visual/Manual tests in that gate's scope.

---

## Test Coverage Policy

Minimum coverage is not a percentage — it is a declaration of which behaviors are tested.

**Required coverage:**
- Every declared acceptance criteria in every spec has at least one test
- Every declared error case (400/500 responses, permission denied, invalid input) has a test
- Every fixed bug has a regression test
- Every critical path has an E2E test

**Coverage gaps are tracked explicitly:**
- Open a `COVERAGE_GAP` issue for any required coverage that does not yet exist
- Coverage gaps do not block feature merges, but they do block release candidates

---

## CI Pipeline Gates (pre-release)

Before any release build reaches QA:

| Step | Blocking | Notes |
|---|---|---|
| Build succeeds | Yes | Zero compile errors |
| Logic tests pass | Yes | Zero failures |
| Integration tests pass | Yes | Zero failures |
| Config/Data schema validation | Yes | Zero malformed files |
| E2E critical path passes | Yes | Zero failures on declared critical paths |
| Performance gates pass | Yes | All declared budgets met |
| Smoke test PASS | Yes | Run by human against release candidate |
| No secrets in build output | Yes | Automated scan |
