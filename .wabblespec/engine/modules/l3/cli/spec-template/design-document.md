# CLI Design Document Template (P1)

> **Platform:** CLI
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-cli activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this CLI tool does, who runs it, and the primary workflow it replaces or enables.

---

## Command Structure [REQUIRED]

Top-level command name and all subcommands. Every subcommand must be named here before any Executor wave begins.

```
<tool-name>
  <subcommand>          [description]
  <subcommand>          [description]
    <nested-subcommand> [description]
```

**Aliases:** List any shorthand aliases declared (e.g., `wbs` for `wabble-spec`).

**Global flags:** Flags that apply to all subcommands (--verbose, --quiet, --json, --config, --help, --version).

---

## Subcommand Hierarchy

[REQUIRED] Maximum subcommand depth: ___
Rationale for depth beyond 1 level (if applicable): ___

For each subcommand:

| Subcommand | Args | Required flags | Optional flags | Side effects |
|---|---|---|---|---|
| `<name>` | positional args | flags | flags | files written / network calls / state changed |

---

## Config File Schema [REQUIRED]

Does this CLI use a config file? [ ] Yes  [ ] No

If yes:
- Location convention: [ ] XDG (`~/.config/<tool>/config.toml`) [ ] Home dir (`~/.<tool>rc`) [ ] CWD (`.toolrc`) [ ] Custom: ___
- Format: [ ] TOML [ ] YAML [ ] JSON [ ] INI
- Env var override: Does each config key have an env var override? [ ] Yes [ ] No (required: yes)
- Schema (list all keys, types, defaults, env var overrides):

```toml
# Example — replace with actual schema
[section]
key = "default"   # env: TOOL_SECTION_KEY
```

---

## Output Modes [REQUIRED]

[REQUIRED] Declare which output modes are supported:

| Mode | Flag | Behavior |
|---|---|---|
| Human-readable | (default) | Formatted text to stdout, progress/errors to stderr |
| Machine-readable | `--json` | JSON object to stdout, no decorators, no ANSI codes |
| Quiet | `--quiet` | No stdout output, only exit code communicates result |
| Verbose | `--verbose` | Additional diagnostic output to stderr |

**ANSI colors:** [ ] Supported (auto-detect TTY, strip when piped) [ ] Not supported
**Terminal width detection:** [ ] Used [ ] Fixed at 80 [ ] Not applicable

---

## Stdin / Stdout / Stderr Contract [REQUIRED]

This contract is binding. Verifier checks it.

| Stream | What goes here |
|---|---|
| **stdin** | [Describe: piped input accepted? What format? EOF behavior?] |
| **stdout** | [Describe: primary output data only. No progress messages. No log lines.] |
| **stderr** | [Describe: errors, progress, log output, spinner. Everything non-data.] |

**Pipe-safety:** [ ] This CLI is safe to pipe (stdout is data-only, stderr is user-facing)

---

## Exit Code Registry [REQUIRED]

Zero exit codes and incomplete registries are not acceptable.

| Code | Meaning | When |
|---|---|---|
| 0 | Success | Command completed as expected |
| 1 | General error | Unclassified failure |
| 2 | Misuse | Invalid arguments, unknown command |
| [3+] | [Define per tool] | [Specific error conditions] |

---

## Credential Handling Strategy [REQUIRED]

[REQUIRED] This section is non-negotiable. Credentials must never appear as positional arguments.

| Credential type | Accepted via | Explicitly forbidden via |
|---|---|---|
| API keys | Env var (`TOOL_API_KEY`) or config file | Positional arg, `--flag value` |
| Passwords | Stdin prompt (masked) or env var | Any argument |
| Tokens | Env var or config file | Positional arg |

**Rationale:** Positional args appear in `ps aux`, shell history (`~/.bash_history`), and CI logs. Env vars do not.

---

## Distribution Strategy [REQUIRED]

Primary distribution channel:
[ ] npm global (`npm install -g <tool>`)
[ ] PyPI (`pip install <tool>`)
[ ] Homebrew tap (`brew install <org>/<tap>/<tool>`)
[ ] Binary release (GitHub Releases, direct download)
[ ] Multiple — list primary: ___

**Version management:** How does the user know what version they have? (`--version` flag required.)

---

## Shell Completion [REQUIRED]

[ ] Supported — generation command: `<tool> completion <shell>`
[ ] Not supported — reason: ___

If supported, declare target shells: [ ] bash [ ] zsh [ ] fish [ ] PowerShell

---

## GWT Acceptance Scenarios (CLI-specific)

These are the platform-specific gate tests that Verifier runs. Generic templates do not include these.

```
Given: a subcommand that accepts credentials
When: the subcommand is invoked
Then: credentials are accepted only via env var or stdin (never positional arg or --flag)
      AND help text documents the env var name
      AND no credential value appears in error messages or logs

Given: a command that produces data output
When: the output is piped to another command (stdout is not a TTY)
Then: no ANSI escape codes appear in stdout
      AND exit code is 0 on success regardless of TTY state
      AND data format matches the declared stdout contract

Given: an invalid argument is passed
When: any subcommand is invoked with unrecognized args
Then: exit code is 2 (not 1)
      AND error message goes to stderr (not stdout)
      AND --help suggestion is included in stderr output

Given: a command that makes network calls
When: --help is invoked on that subcommand
Then: help text explicitly discloses that a network call will be made
      AND the destination is named

Given: the CLI is run for the first time with no config
When: required config is absent
Then: CLI does not silently use defaults that could surprise the user
      AND a clear message to stderr names what is missing
      AND exit code is non-zero

Given: a file path argument is accepted
When: a path with `../` traversal is passed
Then: the CLI validates the resolved path stays within intended scope
      AND returns a clear error if traversal is detected
```

---

## Open Questions

List any unresolved design decisions here. Specify module will block receipt until all REQUIRED sections are complete and no blocking open questions remain.
