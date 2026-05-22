# CLI Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

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

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
