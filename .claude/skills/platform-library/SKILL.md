---
name: platform-library
description: Library/Package platform. Activates when Recipe detects a distributable library target. Loads library spec templates, engineering rules, security controls, and routes to language modules. Produces a materially different spec from CLI or Web targets — focused on API stability, semver, consumer ergonomics, and supply chain integrity.
---

# Platform: Library/Package

You are the Library platform layer. You activate when Recipe identifies a distributable library or package and you load the constraints, templates, and verification gates specific to that target. You do not execute tasks — Executor does. You provide the platform-specific frame that shapes how those tasks are specified and verified.

## What this skill does

Loads library-specific spec templates, engineering standards, security controls, and verification gates into the active WabbleSpec context. Routes to language modules based on detected tech stack. Writes a platform activation receipt.

## When to use

Recipe must have already run and identified Library/Package as the primary target. Activation signals in `skill-rules.json`.

## What makes Library different from other targets

| Concern | Library | CLI | Web | API/Service |
|---|---|---|---|---|
| Primary consumer | Developers (import, require, use) | End users (run) | Browser users | HTTP clients |
| Success signal | Correct types, expected return values | Exit code 0 | HTTP 200 / UI state | HTTP 2xx |
| Versioning contract | Semver — breaking changes require major bump | Tag + release notes | Deploy artifact | Tag + changelog |
| Distribution | npm/PyPI/crates.io/NuGet/Maven | npm global/binary/PyPI | CDN/hosting | Container registry |
| API surface | Public exports must be stable across minors | Commands/flags/config | Routes/DOM | Endpoints/schemas |
| Tree-shaking | Side-effect-free, named exports, no barrel antipatterns | N/A | Partial (component libs) | N/A |
| Peer dependencies | Declared — not bundled | Bundled | Bundled | N/A |
| Bundle size | Critical — consumers pay the cost | Not a consumer concern | CDN-served | N/A |
| Breaking change process | Deprecation → major version → migration guide | Changelog + major version | None (routes change) | Versioned endpoints |

A spec written without this platform context will miss: semver discipline, peer dependency declaration strategy, tree-shaking safety, API stability commitments across minor versions, supply chain audit requirements, and the distinction between internal and public API surface.

## Activation sequence

```
1. Recipe identifies Library/Package target and signals platform-library activation
2. Load spec-template variant (design-document.md, systems-design.md, technical-spec.md)
3. Detect language stack via skill-rules.json signals
4. Load matched language module(s) from .wabblespec/engine/shared/dev/languages/
5. Load engineering/build-toolchain.md and engineering/performance-budgets.md
6. Load security/threat-model.md and security/platform-controls.md
7. Register verification/gates.md with Verifier
8. Write platform activation receipt
```

## Language routing

| Detected signal | Language module loaded |
|---|---|
| `package.json` without `bin`, `exports` field, `main`/`module` fields | `.wabblespec/engine/shared/dev/languages/node/` |
| `pyproject.toml` with `[build-system]`, no `[project.scripts]` | `.wabblespec/engine/shared/dev/languages/python/` |
| `lib.rs` or `[lib]` in Cargo.toml | `.wabblespec/engine/shared/dev/languages/rust/` |
| `go.mod`, no `main` package at root | `.wabblespec/engine/shared/dev/languages/go/` |

## Spec template variant

- `spec-template/design-document.md` — P1: Public API surface, versioning policy, consumer personas
- `spec-template/systems-design.md` — P2: Build pipeline, exports map, peer dep strategy, bundle architecture
- `spec-template/technical-spec.md` — P3: Implementation spec with GWT acceptance scenarios (API contract tests)

Use these templates instead of generic WabbleSpec templates when Library is the active platform.

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `.wabblespec/engine/shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - .wabblespec/engine/shared/dev/frameworks/library/core.md
  conditional_load: []
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
```

## Output contract

**Platform activation receipt** (`.wabblespec/state/receipts/platform-library-{timestamp}.json`):

Base receipt schema with Library extension fields (see `schemas/receipt.schema.json`).

## Files loaded by this module

```
modules/l3/library/
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
