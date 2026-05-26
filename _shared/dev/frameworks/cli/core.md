# CLI Framework Core

Cross-framework knowledge for command-line tools. Loaded by Apply for every CLI platform task.

## CLI contract

A CLI tool is a contract between the tool author and shell scripts that call it. Breaking that contract silently is a critical bug.

### Exit codes

| Exit code | Meaning |
|---|---|
| 0 | Success — command completed, result available |
| 1 | General error — operation failed; message on stderr |
| 2 | Misuse — bad arguments, unknown flags; print usage |
| 3-127 | Tool-defined; must be declared in spec |
| 130 | SIGINT (Ctrl+C) — user interrupted |

Exit codes must be declared in spec. Scripts rely on `$?` being predictable.

### Output contract

- **stdout**: data only — output that will be piped, redirected, or parsed
- **stderr**: messages only — errors, warnings, progress, informational text
- Never mix data and messages on stdout
- JSON output: use `--json` flag pattern; never output JSON by default unless the tool is data-oriented
- Human-readable default: assume a terminal; respect `NO_COLOR` and `--no-color`

### Pipe compatibility

```bash
tool | jq .         # stdout must be valid JSON if --json mode
tool | head -n 5    # stdout must be line-oriented for text mode
tool 2>/dev/null    # stderr can be suppressed without breaking stdout
```

## Argument and flag design

### Conventions

- Short flags: single character (`-v`, `-o FILE`)
- Long flags: `--verbose`, `--output FILE`
- Boolean flags: `--flag` to set true; `--no-flag` to set false
- Positional args: use sparingly; maximum 2 positional args before requiring flags

### Argument security

Shell injection risk: never interpolate user-provided arguments into shell commands.

```python
# WRONG: shell injection
subprocess.run(f"git log {branch}", shell=True)

# RIGHT: argument list
subprocess.run(["git", "log", branch])
```

Never accept credentials as positional arguments — they appear in `ps` output and shell history. Use environment variables or stdin.

## Configuration

Priority order (highest wins):
1. Command-line flags
2. Environment variables
3. Config file (project-level)
4. Config file (user-level XDG)
5. Built-in defaults

Config file location: XDG conventions:
- `$XDG_CONFIG_HOME/{tool}/config.toml` (or `~/.config/{tool}/config.toml`)
- Project-level: `.{tool}rc` or `.{tool}/config.toml` in working directory

## Help text requirements

Every command must have:
- Short description (one line)
- Usage line with all arguments and flags
- Description of each flag
- At least one example
- Exit code table if non-standard

`--help` must exit 0. `--version` must exit 0 and print `{name} {semver}` to stdout.

## Error messages

```
Error: {what went wrong}
  {context: which file, which value, which operation}
  {how to fix it}

Run '{tool} help {subcommand}' for usage.
```

- Errors go to stderr
- Include the value that caused the error
- Suggest the fix when possible
- Never print a stack trace to users in production mode (use `--debug` / `DEBUG=1`)

## Testing

- Unit test: argument parsing, flag defaults, config loading
- Integration test: spawn the CLI process; assert exit code and stdout/stderr
- Table-driven tests: test boundary cases for all flag combinations
- Do not test implementation internals — test the CLI's observable behavior
