# Platform Library/Package — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified Library/Package as the primary target,
When platform-library is invoked,
Then it surfaces: "platform-library requires Recipe to have identified Library/Package as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified Library/Package as the primary target,
When platform-library activates,
Then the activation sequence completes in order: spec-template load → language detection → language module load → engineering load → security load → Verifier gate registration → receipt write.

## Language routing: Node.js library

Given `package.json` without `bin` field but with `exports`, `main`, or `module` fields,
When platform-library detects the language stack,
Then `_shared/dev/languages/node/` is loaded.

## Language routing: Python library

Given `pyproject.toml` with `[build-system]` and no `[project.scripts]`,
When platform-library detects the language stack,
Then `_shared/dev/languages/python/` is loaded.

## Language routing: Rust crate

Given `lib.rs` or `[lib]` section in Cargo.toml,
When platform-library detects the language stack,
Then `_shared/dev/languages/rust/` is loaded.

## Language routing: Go module

Given `go.mod` exists with no `main` package at root,
When platform-library detects the language stack,
Then `_shared/dev/languages/go/` is loaded.

## Library-specific concerns injected into spec

Given platform-library is active,
When spec context is assembled,
Then semver discipline is declared: breaking changes require a major version bump.
Then the public API surface is declared and separated from internal implementation.
Then peer dependencies are declared (not bundled).
Then tree-shaking safety is addressed: side-effect-free, named exports, no barrel antipatterns.
Then bundle size impact on consumers is declared.
Then migration guide requirement for breaking changes is present.
Then supply chain audit requirements are present.

## Breaking change deprecation process

Given the spec includes a breaking change,
When spec context is assembled,
Then the deprecation path is declared: deprecation notice in minor version → breaking change in next major.
Then a migration guide is required before the major version is released.

## Public vs internal API boundary declared

Given platform-library is active,
When spec context is assembled,
Then the public API surface (what consumers can import) is explicitly enumerated.
Then internal modules are marked as not part of the public API.
Then the spec declares that internal module paths are not considered stable.

## Capability handoff

Given platform-library has activated,
When the capability handoff is declared in the receipt,
Then `_shared/dev/frameworks/library/core.md` is always loaded.
Then gateway references include gateway-security/references/ and gateway-engineering/references/.
Then no visual gateway references are included (library is non-visual).

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-library attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-library run,
Then platform-library does not treat a library target as equivalent to a CLI or Web target.
Then platform-library does not allow breaking API changes without a major version bump.
Then platform-library does not bundle peer dependencies.

## Receipt fields

Given any successful platform-library activation,
Then a receipt is written to `.wabblespec/receipts/platform-library-<timestamp>.json`.
Then the receipt contains: platform, language_module_loaded, templates_activated, semver_policy_declared, public_api_surface_declared, peer_deps_declared, gates_registered, capability_handoff.
