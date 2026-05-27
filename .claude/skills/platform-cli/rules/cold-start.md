# Cold-Start Behavior — Platform CLI

Defines how the CLI platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/cli/core.md` missing from the repository.
Detection: File read returns 404 during Apply routing phase.
Action: Log warning — "CLI framework file missing: cli/core.md". Apply continues without exit-code contract and pipe-compatibility rules. Decompose proceeds.
Do NOT: Fail the session. Execution continues; Verifier gates may catch missing conventions.

## Absent: conditional framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/cli/cobra.md` (or click/clap) missing when the framework is detected.
Detection: Signal found (e.g., `import cobra` / `import click` / `clap` in Cargo.toml) but file absent.
Action: Proceed without framework-specific file. Log: "CLI framework file not found: [path]."

## Absent: security reference files

Condition: `modules/l3/cli/security/threat-model.md` or `security/platform-controls.md` absent.
Detection: File read returns 404.
Action: Gateway-security falls back to generic controls. Log: "CLI security files missing — using gateway-security defaults."

## Absent: spec-template files

Condition: `modules/l3/cli/spec-template/design-document.md` absent.
Detection: Specify requests template, file not found.
Action: Specify uses generic structure. Log: "CLI spec-template not found."

## Default state on cold start

| Field | Default |
|---|---|
| `exit_codes` | 0=success, 1=general error, 2=misuse, 130=SIGINT — enforced as defaults |
| `stdout_contract` | Not declared — Specify must elicit (machine-parseable / human-readable) |
| `credential_strategy` | Not declared — Specify must elicit |
| `shell_exec` | Forbidden (string concatenation + shell=True) — enforced unconditionally |
| `update_check` | Disabled — must be opt-in with env var escape hatch |

Exit code defaults are enforced even without framework files — they are CLI platform invariants.
