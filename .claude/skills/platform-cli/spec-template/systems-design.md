# CLI Systems Design Template (P2)

> **Platform:** CLI
> **Template version:** 1.0
> **Populated by:** Specify module (P2 pass)
> **Prerequisite:** design-document.md complete (P1 receipt exists)

---

## Arg Parsing Architecture

**Parser library:** [from language module routing — Commander/Yargs for Node, Click/Typer for Python, Cobra for Go, Clap for Rust]

**Arg validation strategy:**
- Where does validation happen? [ ] Library-level (declare schema, library validates) [ ] Application-level (manual checks) [ ] Both
- Required vs. optional args enforced by: [ ] Library schema [ ] Runtime guard [ ] Both
- Unknown args: [ ] Error with exit 2 [ ] Pass-through to sub-process [ ] Warn and continue (declare)

**Subcommand dispatch:**
```
main()
  └─ parse args (library)
  └─ route to subcommand handler
        └─ validate subcommand-specific args
        └─ load config
        └─ execute
        └─ write to stdout/stderr per contract
        └─ exit with declared code
```

---

## Config Loading Pipeline

Order of precedence (highest to lowest):

1. CLI flags (runtime, session-scoped)
2. Env vars (`TOOL_*` prefix — one per config key)
3. Config file (XDG / home dir — as declared in design-document)
4. Built-in defaults (all defaults documented, none silent)

**Config file parsing:** Library used: ___. Error behavior when config is malformed: exit non-zero with specific error to stderr.

**First-run behavior:** When config file is absent:
[ ] Create default config file and inform user
[ ] Operate on built-in defaults and inform user
[ ] Error and exit with instructions

---

## Output Pipeline

```
Subcommand handler
  ├─ Data output → stdout
  │     ├─ TTY detected → formatted, colored, with headers
  │     └─ Pipe detected → plain data, no ANSI, no decorators
  └─ Diagnostic output → stderr
        ├─ Errors → stderr always
        ├─ Progress spinners → stderr, only when TTY
        └─ Log lines → stderr (--verbose only)
```

**TTY detection:** `process.stdout.isTTY` (Node) / `sys.stdout.isatty()` (Python) / `isatty(STDOUT_FILENO)` (C/Go) / `std::io::stdout().is_terminal()` (Rust)

**JSON output mode (`--json`):** When active: no ANSI, no spinners, no progress — stdout is valid JSON only. Schema of JSON output declared here.

---

## State Management

Does this CLI maintain local state between invocations?
[ ] Yes — state location: ___, format: ___
[ ] No

If yes:
- State file path: ___
- Locking mechanism (prevent concurrent writes): ___
- State migration strategy (when schema changes): ___
- State corruption behavior: ___

---

## Error Handling Model

**Error propagation:**
```
Operation errors → wrap with context → write message to stderr → exit with declared code
```

**Error message format:**
```
error: <short description>       (always present)
  cause: <root cause>            (when known)
  hint: <recovery suggestion>    (when actionable)
```

**Never expose:**
- Stack traces to end users (write to debug log file only, never stderr by default)
- Internal paths, URLs, or connection strings in error messages
- Credential values in any output

---

## Startup Sequence

```
1. Parse top-level args (no I/O at this point)
2. Detect TTY state
3. Load config (config file + env vars)
4. Validate required config is present
5. Route to subcommand handler
6. Execute
7. Exit with declared code
```

**Startup time target:** < 100ms cold start (see engineering/performance-budgets.md)

**Lazy loading principle:** Do not load subcommand dependencies until that subcommand is invoked. Startup must not import the full dependency tree.

---

## Signal Handling

| Signal | Behavior |
|---|---|
| SIGINT (Ctrl+C) | Clean up in-progress work, exit non-zero |
| SIGTERM | Same as SIGINT |
| SIGPIPE | Handle gracefully — do not crash when stdout pipe closes |

**Cleanup on interrupt:** List any files, locks, or temp state that must be cleaned up before exit.

---

## Update / Version Check

Does this CLI check for updates?
[ ] Yes — mechanism: ___, frequency: ___, opt-out env var: ___
[ ] No

If yes: update check must be async, must not block command execution, must respect `--quiet` / `--json` mode.

---

## Logging

**Log destination:** [ ] Stderr only [ ] Log file at `~/.local/share/<tool>/log` (XDG) [ ] No logging
**Default log level:** [ ] ERROR [ ] WARN [ ] INFO (with --verbose)
**Log format:** [ ] Human-readable [ ] JSON (for --json mode or log file)

Logs must never contain: credentials, full file contents, or values that appear in `ps aux`.
