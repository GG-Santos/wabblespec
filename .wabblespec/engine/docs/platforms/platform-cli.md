# Platform: CLI

Command-line tool target. Activates when Recipe identifies a CLI application as the primary build target.

**Skill:** `modules/l3/cli/SKILL.md`
**Spec templates:** `modules/l3/cli/spec-template/`
**Engineering rules:** `modules/l3/cli/engineering/`
**Security controls:** `modules/l3/cli/security/`
**Verification gates:** `modules/l3/cli/verification/`

## What makes CLI different

| Concern | CLI approach |
|---------|-------------|
| Interface contract | Argument flags, stdin/stdout, exit codes — not HTTP or UI |
| Error reporting | stderr for errors, stdout for output — never mixed |
| User feedback | Progress to stderr or TTY-detected spinner — never clutters piped output |
| Config | XDG base directory or `~/.toolrc` — not `.env` files |
| Security | Shell injection via user-supplied arguments, PATH manipulation |
| Testing | Integration tests via subprocess — unit tests for business logic |
| Distribution | Single binary, pip install, npm global — platform declares which |

## Platform-specific spec template sections

When Specify runs for a CLI target, the spec includes:
- Command interface: all flags, subcommands, positional arguments
- Exit code contract: 0 = success, 1 = user error, 2 = internal error (or platform-specific convention)
- stdin/stdout contract: what goes where and in what format
- Configuration resolution order: flags > env vars > config file > defaults
- Help text requirements: `--help` on every subcommand

## Security controls loaded

- Argument injection: validate all user-supplied strings before shell interpolation
- PATH manipulation: declare expected executables explicitly, do not resolve from PATH in sensitive operations
- Privilege escalation: document any operation requiring elevated permissions
- Temp file handling: use OS-provided temp dirs, clean up on exit and signal

## Gateway interaction

CLI targets typically activate:
- `gateway-security` — always (shell injection surface)
- `gateway-engineering` — for Medium/High complexity CLIs

CLI targets do not activate: aesthetic, design, experience gateways.
