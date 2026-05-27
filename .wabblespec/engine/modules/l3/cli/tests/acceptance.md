# Platform CLI — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified CLI as the primary target,
When platform-cli is invoked,
Then it surfaces: "platform-cli requires Recipe to have identified CLI as the primary target first."
Then no platform activation receipt is written.
Then no files are loaded into Specify context.

## Happy path: activation sequence

Given Recipe has identified CLI as the primary target,
When platform-cli activates,
Then the activation sequence completes in order: spec-template load → language detection → language module load → engineering load → security load → Verifier gate registration → receipt write.
Then no step is skipped.

## Language routing: Node.js

Given the project contains `bin` in package.json or `#!/usr/bin/env node` shebang,
When platform-cli detects the language stack,
Then `.wabblespec/engine/shared/dev/languages/node/` is loaded.
Then no other language module is loaded for a single-language project.

## Language routing: Python

Given the project contains `cli.py`, `__main__.py`, or imports `typer` or `click`,
When platform-cli detects the language stack,
Then `.wabblespec/engine/shared/dev/languages/python/` is loaded.

## Language routing: Go

Given the project contains a `cmd/` directory, `cobra` import, or `go.mod`,
When platform-cli detects the language stack,
Then `.wabblespec/engine/shared/dev/languages/go/` is loaded.

## Language routing: Rust

Given the project contains `clap` in Cargo.toml or a Rust `main.rs` with arg parsing,
When platform-cli detects the language stack,
Then `.wabblespec/engine/shared/dev/languages/rust/` is loaded.

## Platform-specific spec template loaded

Given CLI is the active platform,
When Specify runs,
Then `spec-template/design-document.md` (P1), `spec-template/systems-design.md` (P2), and `spec-template/technical-spec.md` (P3) are the active templates.
Then generic WabbleSpec templates are not used in place of CLI templates.

## CLI-specific concerns injected into spec

Given platform-cli is active,
When spec context is assembled,
Then exit code contracts are present in the spec.
Then stdout (data) vs stderr (errors/logs) separation is declared.
Then cold start < 100ms performance budget is declared.
Then credentials are required to use env vars or stdin — never positional args.
Then shell completion declaration is included.

## Framework capability handoff

Given platform-cli has activated,
When the capability handoff is declared in the receipt,
Then `.wabblespec/engine/shared/dev/frameworks/cli/core.md` is always loaded.
Then framework-specific files (cobra.md, click.md, clap.md) are loaded only when the corresponding signal is detected.
Then gateway references include gateway-security/references/ and gateway-engineering/references/.

## Absent language signal

Given no recognized language signal is present in the project,
When platform-cli attempts language detection,
Then platform-cli logs a warning: "No recognized language stack detected — language module not loaded."
Then platform-cli proceeds without a language module rather than blocking.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-cli attempts to register gates with Verifier,
Then platform-cli logs: "verification/gates.md absent — Verifier registration skipped."
Then the platform activation proceeds with a warning recorded in the receipt.

## Do NOT

Given any platform-cli run,
Then platform-cli does not execute tasks — Executor handles execution.
Then platform-cli does not use Web or API spec templates for a CLI target.
Then platform-cli does not load gateway-aesthetic/references/ (CLI is non-visual).

## Receipt fields

Given any successful platform-cli activation,
Then a receipt is written to `.wabblespec/receipts/platform-cli-<timestamp>.json`.
Then the receipt contains: platform, language_module_loaded, framework_loaded, templates_activated, engineering_files_loaded, security_files_loaded, gates_registered, capability_handoff.
