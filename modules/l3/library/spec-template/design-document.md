# Library Design Document Template (P1)

> **Platform:** Library/Package
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-library activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this library does, who imports it, and what problem it solves for its consumers. Include the primary language/runtime target.

---

## Consumer Personas [REQUIRED]

Who imports this library and in what context?

| Persona | Environment | How they use it |
|---|---|---|
| [e.g. "Frontend developer"] | [e.g. "React app, webpack"] | [e.g. "imports named utility functions"] |

---

## Public API Surface [REQUIRED]

Every export declared here is a public contract. Removing or renaming any of these requires a MAJOR version bump.

**Named exports:**

| Export name | Type | Description | Stable since |
|---|---|---|---|
| `<name>` | function / class / type / constant | what it does | v___ |

**Default export:** [ ] Yes — name: ___ [ ] No

**Internal modules (NOT public API):** List paths that are implementation details consumers must not import directly:
- `src/internal/`
- `src/utils/`
- _(list any others)_

**Re-exports from dependencies:** [ ] None [ ] List: ___

---

## Versioning Policy [REQUIRED]

Semver definitions for this library:

| Version bump | When | Example |
|---|---|---|
| **PATCH** | Bug fixes with no API change | Fix return value of `parse()` when input is empty string |
| **MINOR** | New exports, new optional params, new optional config fields | Add `parseAsync()` function |
| **MAJOR** | Remove export, rename export, change required param, change return type | Remove `parse()`, rename to `decode()` |

**Current version:** ___

**Deprecation process:**
1. Mark deprecated in JSDoc/docstring with `@deprecated` + version introduced + replacement
2. Keep deprecated export for ___ minor versions minimum
3. Remove in next MAJOR with migration note in CHANGELOG

---

## Peer Dependencies [REQUIRED]

Does this library have peer dependencies?

[ ] No peer dependencies
[ ] Yes — list all:

| Package | Version range | Why peer (not bundled) |
|---|---|---|
| `react` | `>=17.0.0` | Consumer controls React version — bundling two copies breaks hooks |

**Bundled dependencies:** List dependencies that ARE bundled (included in dist):

| Package | Reason for bundling |
|---|---|
| `<dep>` | [standalone utility, no consumer conflict risk] |

---

## Distribution [REQUIRED]

Primary registry:
[ ] npm (`npm publish`)
[ ] PyPI (`twine upload`)
[ ] crates.io (`cargo publish`)
[ ] pkg.go.dev (auto-indexed from VCS tag)
[ ] NuGet (`dotnet nuget push`)
[ ] Multiple — primary: ___

**Package name:** `<name>`

**Namespace/scope:** `@<scope>/<name>` or `<org>.<name>` (if applicable)

**Access:** [ ] Public [ ] Private (org-scoped)

---

## Module Format [REQUIRED]

| Format | File | Consumers |
|---|---|---|
| ESM | `dist/index.mjs` | Bundlers, modern Node (type: module) |
| CJS | `dist/index.cjs` | CommonJS Node, older tooling |
| Types | `dist/index.d.ts` | TypeScript consumers |
| UMD | `dist/index.umd.js` | CDN, browser globals |

**`exports` field (package.json):** Required for dual ESM/CJS packages. Declare here:

```json
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  }
}
```

---

## Tree-Shaking Contract [REQUIRED]

[ ] This library is tree-shakeable

Requirements for tree-shaking:
- All exports are named (no side-effectful default export)
- No top-level side effects in entry point
- `"sideEffects": false` declared in `package.json` (or list files with side effects)
- No barrel re-exports that force full bundle import

**Files with side effects** (if any):
- `src/polyfills.js` — [reason]

---

## GWT Acceptance Scenarios (Library-specific)

These are the platform-specific gate tests that Verifier runs. Generic templates do not include these.

```
Given: a consumer imports only one named export from the library
When: their bundler performs tree-shaking
Then: only the code for that export (and its transitive deps) is included
      AND the bundle does not include code for unused exports
      AND no top-level side effects execute on import

Given: a consumer uses the library with TypeScript strict mode
When: they call any public API function
Then: TypeScript provides accurate parameter types and return types
      AND no `any` types appear in the public API signature
      AND generic types are correctly inferred from usage

Given: a new minor version is published
When: a consumer upgrades from the previous minor version
Then: no existing code requires modification
      AND no previously-working call sites produce type errors
      AND no previously-working call sites throw at runtime

Given: a consumer declares the library as a peer dependency
When: the peer dependency version range is satisfied
Then: the library works correctly with the declared version range
      AND does not bundle a duplicate copy of peer dependencies

Given: a consumer installs the library in a project with no bundler
When: they import via require() or import in Node.js directly
Then: the correct module format is resolved automatically
      AND no SyntaxError or format mismatch occurs
```

---

## Open Questions

List any unresolved design decisions here. Specify module will block receipt until all REQUIRED sections are complete and no blocking open questions remain.
