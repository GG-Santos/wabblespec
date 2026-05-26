# Performance Budgets — CLI

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/cli`.
> Reference: `_shared/references/performance-budgets.md`.

---

## Startup

### Cold start (time to first output)

**Target:** ≤ 100ms from invocation to first byte of output for any command
**Rationale:** Users invoke CLI tools in loops, scripts, and pre-commit hooks; startup above 100ms is perceptibly slow and compounds in pipelines
**Measurement:** `time <tool> --version` averaged across 10 runs on a clean shell; exclude OS disk cache warm-up
**PII impact:** none

### Help command response

**Target:** ≤ 50ms for `--help` on any subcommand
**Rationale:** Help is the first interaction for new users; latency here damages first impressions
**Measurement:** same as cold start measurement
**PII impact:** none

---

## Interactive command execution

### Synchronous command (non-I/O-bound)

**Target:** ≤ 500ms for commands performing local computation without network or disk I/O
**Rationale:** Interactive commands above 500ms break the conversational model; user expects immediate feedback
**Measurement:** test fixture timing in CI; exclude I/O wait
**PII impact:** none

### Commands with I/O

**Target:** display progress indicator when estimated duration > 1s
**Rationale:** Silent delay above 1s makes users uncertain whether the command is running; progress output is required, not optional
**Measurement:** code audit — every codepath with I/O > 1s estimated duration must emit a progress signal
**PII impact:** none

---

## Memory

### Steady-state memory ceiling

**Target:** ≤ 100MB resident memory during standard operation
**Rationale:** CLI tools run alongside editors and other tools; consuming more than 100MB in a shared terminal session is poor citizenship
**Measurement:** `valgrind --tool=massif` or `/usr/bin/time -v` peak memory; alternatively process RSS during integration tests
**PII impact:** none

### Peak memory (batch operations)

**Target:** ≤ 500MB during batch file processing operations
**Rationale:** Batch operations may need more headroom; above 500MB risks OOM on developer laptops
**Measurement:** integration test peak RSS during maximum-sized fixture
**PII impact:** none

---

## Exit code contract (required — not a performance budget, but Monitor enforces declaration)

All CLI tools must declare their exit code contract. Undeclared exit codes make scripts brittle.

| Exit code | Meaning |
|---|---|
| 0 | Success |
| 1 | User error (invalid arguments, missing input, expected failure) |
| 2 | System error (network failure, filesystem error, unexpected exception) |
| 3–127 | Tool-specific (declare each one used) |
| 128+ | Signal termination (reserved; do not use for application errors) |

**Declaration:** ___ UNDECLARED — populate the table above before first release

---

## Output volume

### Standard output size ceiling

**Target:** No single command produces > 10MB of stdout without a `--no-pager` flag explicitly set
**Rationale:** Terminal emulators become unresponsive with large stdout dumps; large output implies the tool should support structured output (--json) and paging
**Measurement:** CI integration tests assert stdout size for worst-case fixture
**PII impact:** none

---

## Reliability

### Error message quality

**Target:** 100% of user-error exits (exit 1) include: what went wrong, why, and how to fix it
**Rationale:** Error messages that say only what failed (not why or how to recover) force users to search docs or source code
**Measurement:** code review gate; all `sys.exit(1)` / `os.Exit(1)` calls must have a three-part error message
**PII impact:** error messages must not include secrets, tokens, or credentials passed as arguments

---

## PII fields (excluded from log schema)

<!-- CLI tools rarely have persistent logs, but if yours does: -->
<!-- Example:
- Command-line arguments (may contain credentials passed via --token flag)
- Environment variable values (may contain API keys)
-->
___ UNDECLARED — populate if tool writes any persistent log files
