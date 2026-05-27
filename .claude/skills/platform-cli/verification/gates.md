# CLI Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

## Standards Basis

Each gate derives from a named standard. This is the reference index.

| Gate | Standard | Source |
|---|---|---|
| 1 | `--help` required per subcommand | POSIX Utility Conventions §12.2; GNU coding standards |
| 2 | Exit 0 = success, exit 2 = misuse, exit 1 = error | POSIX §2.8.2; sysexits.h EX_USAGE=64 (mapped to 2) |
| 3 | Credentials via env vars, not flags | OWASP Secrets Management; 12-Factor App §III |
| 4 | ANSI codes only when stdout is a TTY | POSIX isatty(3); No-Color standard (no-color.org) |
| 5 | Cold start budget 100ms default | Google CLI UX guidelines; Measured as p99 |
| 6 | stdout = data, stderr = diagnostics | POSIX §2.1; GNU Coding Standards §4.7 |
| 7 | Path traversal must be rejected | OWASP Path Traversal (A01:2021) |
| 8 | Installable from declared channel | Distribution contract — no implicit assumptions |
| 9 | `--help`/`--version` offline-capable | No network dependency for discovery commands |
| 10 | Config follows XDG + env var precedence | XDG Base Directory Specification r0.8; 12-Factor App §III |
| 11 | CLI behaviors have targeted tests | Test coverage contract — exit codes, pipes, args each need a test |

---

## Gate 1: Help Coverage

**Check:** Every declared subcommand has --help output.

**Method:**
```bash
for cmd in <all declared subcommands>; do
  <tool> $cmd --help
  # must exit 0 and produce non-empty output
done
```

**Pass:** Exit 0 + non-empty output for every subcommand.
**Fail:** Any subcommand exits non-zero on --help, or produces empty output.

---

## Gate 2: Exit Code Baseline

**Check:** Success = exit 0. Misuse = exit 2. Error = non-zero.

**Method:**
```bash
<tool> <valid_cmd>              # exit 0
<tool> unknown-subcommand       # exit 2
<tool> <cmd> --unknown-flag     # exit 2
<tool> <cmd> <invalid args>     # exit 2
# Induce a runtime error:
<tool> <cmd> --config /nonexistent  # exit 1 or declared error code
```

**Pass:** All exit codes match declared registry.
**Fail:** Any mismatch between declared exit code and actual.

---

## Gate 3: Credential Argument Rejection

**Check:** No subcommand accepts credentials as positional args or `--flag value`.

**Method:**
```bash
# For each credential-accepting subcommand:
<tool> <cmd> --api-key sk-test-123
# must exit 2 with message directing to env var
# must NOT execute the command with the credential

<TOOL>_API_KEY=sk-test-123 <tool> <cmd>
# must succeed (or fail for other reasons, not credential format)
```

**Pass:** `--api-key` form rejected with exit 2. Env var form accepted.
**Fail:** Any credential accepted as a flag or positional arg.

---

## Gate 4: Pipe Safety

**Check:** stdout contains only data when piped. No ANSI codes, no progress output.

**Method:**
```bash
<tool> <cmd> | cat | grep -P '\x1b'
# must produce no output (no ANSI escape sequences in stdout)

<tool> <cmd> | od -c | grep -E 'ESC|\^['
# alternative ANSI detection
```

**Pass:** Zero ANSI escape sequences in stdout when piped.
**Fail:** Any ANSI code detected in piped stdout.

---

## Gate 5: Startup Time

**Check:** Cold start under declared budget (default: 100ms).

**Method:**
```bash
time <tool> --version
# real time must be under budget
# for statistical measurement:
hyperfine --warmup 3 '<tool> --version'
```

**Pass:** p99 cold start ≤ declared budget.
**Fail:** Median startup exceeds declared budget.

**Note:** Declared budget overrides 100ms default if set in design-document.md performance budget field.

---

## Gate 6: Stderr Discipline

**Check:** No data on stderr on success. No errors on stdout.

**Method:**
```bash
<tool> <valid_cmd> 2>/dev/null | <validate output>   # stdout-only check
<tool> <valid_cmd> 2>&1 1>/dev/null                  # stderr must be empty on success
```

**Pass:** stderr empty on success. stdout empty on error.
**Fail:** Any data on wrong stream.

---

## Gate 7: Path Traversal Rejection

**Check:** File path args with `../` traversal are rejected.

**Method:**
```bash
# For each subcommand that accepts a file path:
<tool> <cmd> --file "../../etc/passwd"
# must exit non-zero
# must emit error message mentioning traversal or invalid path
# must NOT attempt to read/write the traversal target
```

**Pass:** Non-zero exit + error message. No file I/O on traversal path.
**Fail:** Command proceeds, or exits 0, or no error message.

---

## Gate 8: Distribution Smoke Test

**Check:** Tool is installable and functional from declared distribution channel.

**Method (npm global):**
```bash
npm pack
npm install -g ./<packed>.tgz
<tool> --version   # must work from global install
npm uninstall -g <tool>
```

**Method (binary release):**
```bash
./dist/<tool>-<platform>-<arch> --version
```

**Pass:** `--version` works from clean install.
**Fail:** Installation fails or `--version` errors after install.

---

## Gate 9: Network Non-Disclosure (for help/version)

**Check:** `--help` and `--version` make no network calls.

**Method:**
```bash
# Block network and verify help/version still work:
unshare -n <tool> --help    # Linux network namespace isolation
unshare -n <tool> --version
```

**Pass:** Both exit 0 with no network errors.
**Fail:** Either errors or hangs when network is unavailable.

---

---

## Gate 10: Config Discovery

**Check:** Config loads from correct locations in precedence order. No config required for basic operation.

**Precedence (highest to lowest):**
1. CLI flag (e.g., `--config <path>`)
2. Environment variable (e.g., `<TOOL>_CONFIG`)
3. Project-local config (`./<toolrc>` or `.config/<tool>/config`)
4. XDG user config (`$XDG_CONFIG_HOME/<tool>/config` — default `~/.config/<tool>/config`)
5. Built-in defaults

**Method:**
```bash
# No config — must work with defaults:
unset <TOOL>_CONFIG
<tool> <cmd>   # must not error on missing config

# Env var override:
<TOOL>_CONFIG=/tmp/test-config.yaml <tool> <cmd>   # must load that file

# XDG path:
mkdir -p ~/.config/<tool>
cp test-config.yaml ~/.config/<tool>/config
<tool> <cmd>   # must load XDG path when no env var set

# Flag takes precedence over env var:
<TOOL>_CONFIG=/tmp/lower.yaml <tool> <cmd> --config /tmp/higher.yaml
# must load higher.yaml, not lower.yaml
```

**Pass:** Precedence order verified. Tool starts without any config present.
**Fail:** Tool requires config to start. Precedence violated. Non-XDG path used as default.

**Note:** If tool has no persistent config (stateless CLI), mark this gate SKIP and document why.

---

## Gate 11: Test Coverage for CLI Behaviors

**Check:** Test suite contains targeted tests for CLI-specific behaviors. Generic unit tests do not satisfy this gate.

**Required test categories:**

| Behavior | Minimum coverage |
|---|---|
| Exit codes | One test per declared exit code value (0, 1, 2, any custom) |
| Stdout/stderr split | One test asserting data on stdout and nothing on stderr for happy path |
| Pipe safety | One test running output through `cat` and asserting no ANSI codes |
| Arg validation | One test per required arg missing → exit 2 |
| Config precedence | One test per precedence level (env var, flag, XDG) |
| Credential rejection | One test asserting `--api-key` form exits 2 |

**Method:**
```bash
# Verify test files exist for CLI behaviors:
grep -r "exit.*code\|exitCode\|sys.exit\|os.Exit" tests/
grep -r "stderr\|stdout" tests/
grep -r "pipe\|isTTY\|isatty" tests/

# Run CLI-specific test suite:
<language-test-runner> tests/cli/   # or equivalent path
```

**Pass:** Every category in the table above has at least one test. All tests pass.
**Fail:** Any category missing. Tests exist but cover implementation internals rather than CLI contract.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Help coverage | Yes |
| 2 | Exit code baseline | Yes |
| 3 | Credential arg rejection | Yes |
| 4 | Pipe safety | Yes |
| 5 | Startup time | Yes |
| 6 | Stderr discipline | Yes |
| 7 | Path traversal rejection | Yes |
| 8 | Distribution smoke test | Yes |
| 9 | Network non-disclosure | Yes |
| 10 | Config discovery | Yes (SKIP if stateless) |
| 11 | Test coverage for CLI behaviors | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
