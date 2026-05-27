# CLI Technical Spec Template (P3)

> **Platform:** CLI
> **Template version:** 1.0
> **Populated by:** Specify module (P3 pass) + Decompose
> **Prerequisite:** systems-design.md complete (P2 receipt exists)

---

## Implementation Constraints

These constraints are non-negotiable for all CLI targets. Verifier checks each one.

| Constraint | Rule | Verification method |
|---|---|---|
| Credentials | Never accepted as positional args | Static analysis + GWT test |
| Exit codes | 0 = success, 2 = misuse, 1 = error (minimum) | Exit code test per subcommand |
| Stderr discipline | No data on stderr, no errors on stdout | Pipe test: stderr capture must be empty on success |
| Startup time | < 100ms cold start | `time <tool> --version` |
| Help text | Every subcommand has --help | `<tool> <cmd> --help` exits 0 and produces output |
| Pipe safety | stdout is data-only when piped | `<tool> <cmd> | cat` — no ANSI codes |
| Path validation | No path traversal | Test: pass `../../etc/passwd` as file arg |

---

## Wave Breakdown

Decompose populates this section. Shown here as the expected shape for CLI tasks.

**Wave 0 — Scaffold**
- Entry point + arg parsing setup
- Subcommand skeleton (no logic — just routing)
- --help and --version working
- Acceptance: `<tool> --help` exits 0; `<tool> --version` outputs version; unknown subcommand exits 2

**Wave 1 — Config layer**
- Config file loading (if applicable)
- Env var overrides
- First-run behavior
- Acceptance: `TOOL_KEY=value <tool> <cmd>` overrides config file; missing required config exits non-zero with clear message

**Wave 2+ — Subcommand implementations**
- One wave per major subcommand or logical group
- Each wave: implement → test exit codes → test stdout/stderr contract → test error paths

**Final wave — Distribution**
- Build (single binary / npm publish / PyPI publish)
- Shell completions (if declared)
- Cross-platform smoke test

---

## Acceptance Criteria (GWT format)

All scenarios from design-document.md reproduced here and assigned to waves. Add implementation-specific scenarios below.

### Credential security

```
Given: subcommand <name> accepts credential <type>
When: invoked as `<tool> <cmd> --secret <value>` (positional/flag form)
Then: command must reject this form with exit 2 and message directing to env var
      AND credential value must not appear in stderr output

Given: correct env var is set
When: subcommand invoked
Then: credential loaded silently, not echoed anywhere
```

### Exit code contract

```
Given: any subcommand runs successfully
When: invoked with valid args and all dependencies available
Then: exit code is exactly 0

Given: any subcommand encounters an error
When: upstream dependency is unavailable or operation fails
Then: exit code is non-zero (per exit code registry in design-document)
      AND error description is on stderr
      AND nothing is written to stdout
```

### Output contract

```
Given: stdout is piped to another process
When: any subcommand runs
Then: stdout contains only data (no ANSI codes, no spinners, no progress)
      AND output is valid in the declared format (plain text / JSON / CSV — per design-document)

Given: --json flag is set
When: any subcommand runs
Then: stdout is valid JSON matching the declared output schema
      AND exit code 0 means the JSON object is complete and correct
```

### Config loading

```
Given: TOOL_* env var is set
When: conflicting value exists in config file
Then: env var takes precedence
      AND no warning is emitted unless --verbose

Given: config file is syntactically invalid
When: any command is run
Then: exit non-zero with parse error location in stderr message
      AND config file path is named in error
```

### Path handling

```
Given: a file path argument is passed
When: path resolves outside the intended scope (path traversal attempt)
Then: command exits non-zero
      AND error message names the traversal as the rejection reason
      AND no file I/O is attempted on the resolved path
```

---

## Not Tested (explicit)

List what is out of scope for this implementation. Verifier requires this field.

- [ ] Windows batch file (.cmd) wrapper compatibility
- [ ] Shell completion correctness beyond generation (manual test only)
- [ ] Concurrent invocation locking (if not in scope — declare)
- [ ] [Other explicit exclusions]

---

## Platform Verification Gates

See `verification/gates.md`. These gates are registered with Verifier and must pass before any Delivery wave.

1. Help coverage: `<tool> <subcommand> --help` exits 0 for every declared subcommand
2. Exit code baseline: success = 0, misuse = 2
3. Credential gate: no positional credential args accepted
4. Pipe safety: `<tool> <cmd> | cat` produces clean output
5. Startup time: cold start under budget
6. Distribution: installable from declared channel
