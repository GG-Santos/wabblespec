---
name: platform-cli
description: CLI platform package. Activates when Recipe detects a command-line tool target. Loads CLI spec templates, engineering rules, security controls, and routes to language modules. Produces a materially different spec from Web or API targets for the same task.
---

# Platform: CLI

You are the CLI platform layer. You activate when Recipe identifies a command-line tool and you load the constraints, templates, and verification gates that are specific to that target. You do not execute tasks — Executor does. You provide the platform-specific frame that shapes how those tasks are specified and verified.

## What this skill does

Loads CLI-specific spec templates, engineering standards, security controls, and verification gates into the active WabbleSpec context. Routes to language modules based on detected tech stack. Writes a platform activation receipt.

## When to use

Recipe must have already run and identified CLI as the primary target. Activation signals in `skill-rules.json`.

## What makes CLI different from other targets

| Concern | CLI | Web | API/Service |
|---|---|---|---|
| Primary user interface | Terminal args, stdin, stdout | Browser DOM | HTTP endpoints |
| Success signal | Exit code 0 | HTTP 200 / UI state | HTTP 2xx |
| Credentials | Env vars or stdin — never positional args | Session cookies / tokens | Auth headers |
| Output contract | stdout (data), stderr (errors/logs) | HTML/JSON body | Response body |
| Performance budget | Cold start < 100ms | LCP < 2.5s | p99 latency < 200ms |
| Distribution | Binary, npm global, PyPI, Homebrew | CDN / hosting | Container registry |
| Security primary concern | Shell injection via args, path traversal | XSS, CSRF | Auth, injection |
| Config location | XDG conventions, env vars | localStorage, cookies | Env vars, secrets manager |

A spec written without this platform context will miss: exit code contracts, shell injection risk from arg interpolation, credential-in-args antipattern, startup time budget, stdin pipe behavior, and shell completion declaration.

## Activation sequence

```
1. Recipe identifies CLI target and signals platform-cli activation
2. Load spec-template variant (design-document.md, systems-design.md, technical-spec.md)
3. Detect language stack (Node/Python/Go/Rust) via skill-rules.json signals
4. Load matched language module(s) from .wabblespec/engine/shared/dev/languages/
5. Load engineering/build-toolchain.md and engineering/performance-budgets.md
6. Load security/threat-model.md and security/platform-controls.md
7. Register verification/gates.md with Verifier
8. Write platform activation receipt
```

## Language routing

| Detected signal | Language module loaded |
|---|---|
| `bin` in package.json, `#!/usr/bin/env node` | `.wabblespec/engine/shared/dev/languages/node/` |
| `cli.py`, `__main__.py`, `typer`/`click` import | `.wabblespec/engine/shared/dev/languages/python/` |
| `cmd/` directory, `cobra` import, `go.mod` | `.wabblespec/engine/shared/dev/languages/go/` |
| `clap` in Cargo.toml, Rust `main.rs` with arg parsing | `.wabblespec/engine/shared/dev/languages/rust/` |

## Spec template variant

- `spec-template/design-document.md` — P1: Command structure, output modes, distribution strategy
- `spec-template/systems-design.md` — P2: Arg parsing, config loading, output pipeline
- `spec-template/technical-spec.md` — P3: Implementation spec with GWT acceptance scenarios

Use these templates instead of generic WabbleSpec templates when CLI is the active platform.

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `.wabblespec/engine/shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - .wabblespec/engine/shared/dev/frameworks/cli/core.md
  conditional_load:
    - signal: "cobra import or go.mod"
      load: .wabblespec/engine/shared/dev/frameworks/cli/cobra.md
    - signal: "click or typer import"
      load: .wabblespec/engine/shared/dev/frameworks/cli/click.md
    - signal: "clap in Cargo.toml"
      load: .wabblespec/engine/shared/dev/frameworks/cli/clap.md
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
    - gateway-experience/references/     # if experience gateway active
```

## Reference Routing

| Situation | Reference |
|---|---|
| cli receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type platform-activation` |

## Output contract

**Platform activation receipt** (`.wabblespec/state/receipts/platform-cli-{timestamp}.json`):

Base receipt schema with CLI extension fields (see `schemas/receipt.schema.json`).

## Files loaded by this module

```
modules/l3/cli/
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```
