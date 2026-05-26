# Library / Package Framework Core

Cross-framework knowledge for distributable libraries and packages. Loaded by Apply for every Library platform task.

## Library contract — the API stability promise

A library makes a promise to its consumers: minor and patch versions do not break existing code.

### Semantic versioning

```
MAJOR.MINOR.PATCH

MAJOR: breaking change — consumers must update their code
MINOR: new backward-compatible feature
PATCH: bug fix, no API change

0.x.y: pre-stable — breaking changes allowed in MINOR
```

Spec must declare: what constitutes a breaking change for this library. Common breaking changes:
- Removing or renaming a public export
- Changing a function signature (parameter types, order, or removing optional params)
- Changing return type
- Changing thrown exception types
- Changing behavior in a way that breaks existing correct usage

## Public API surface

Spec must declare: which exports are public (stable) vs internal (may change).

```typescript
// package.json exports map
{
  "exports": {
    ".": "./dist/index.js",           // main entry
    "./utils": "./dist/utils.js",     // named subpath
    "./internal": null                // explicitly block internal access
  }
}
```

Marking exports as `null` prevents consumers from importing internal modules. Use this for all internal code.

## Tree-shaking safety

Libraries must be tree-shakable so consumers pay only for what they use.

Rules:
- Named exports, not default export of everything
- No side effects at module import time — mark `"sideEffects": false` in package.json if true
- Barrel files (index.ts that re-exports everything) prevent tree-shaking — use named subpath exports instead
- No static class methods where standalone functions would work

## Peer dependencies

Do not bundle peer dependencies (React, Vue, lodash, etc.) — declare them:

```json
{
  "peerDependencies": {
    "react": ">=18.0.0"
  },
  "peerDependenciesMeta": {
    "react": {
      "optional": true
    }
  }
}
```

Spec must declare: which packages are peer dependencies and why.

## Deprecation policy

Before removing a feature (breaking change):
1. Add `@deprecated` JSDoc / deprecation warning in code
2. Document replacement in deprecation notice
3. Keep deprecated API for at least one major version
4. Remove in next major version

```typescript
/** @deprecated Use `newFunction()` instead. Will be removed in v3.0. */
export function oldFunction() {
  console.warn("oldFunction is deprecated. Use newFunction() instead.")
  return newFunction()
}
```

## Distribution

| Registry | Command | Config |
|---|---|---|
| npm | `npm publish` | `package.json` |
| PyPI | `python -m build && twine upload` | `pyproject.toml` |
| crates.io | `cargo publish` | `Cargo.toml` |
| Maven Central | `mvn deploy` | `pom.xml` |

Spec must declare: registry, automation (GitHub Actions on tag), and access token management.

## Security — supply chain

- Lock file committed: prevents dependency version drift
- Dependency audit in CI: `npm audit` / `pip-audit` / `cargo audit` — fail on high-severity
- Publish 2FA: npm requires 2FA for publishing; use it
- Provenance: npm supports package provenance (links package to source commit) — enable for public packages
- No install scripts: `scripts.install` / `scripts.postinstall` run arbitrary code on `npm install` — avoid unless essential

## Testing for libraries

Libraries must test their public API surface as consumers would use it:

```typescript
// Test via the public import path, not internal file paths
import { publicFunction } from '../src/index'  // WRONG if publishing from dist
import { publicFunction } from 'my-lib'         // RIGHT — test the package as installed

// Test across supported environments
// - Node.js (require + import)
// - Browser bundle (if applicable)
// - TypeScript (types must be correct)
```

Spec must declare: tested environments (Node version range, browser targets), type checking in tests.
