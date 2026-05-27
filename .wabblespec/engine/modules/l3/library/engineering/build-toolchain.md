# Library Engineering — Build Toolchain

## Node/TypeScript Library

**Preferred build tool:** tsup (wraps esbuild, handles dual ESM+CJS + types in one config)
**Alternative:** unbuild (unjs), rollup + @rollup/plugin-typescript

**tsup config (`tsup.config.ts`):**
```typescript
import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  clean: true,
  splitting: false,
  sourcemap: true,
  minify: false,   // consumers/bundlers minify — don't double-minify
  external: ['react', 'react-dom'],  // peer deps must be external
})
```

**`package.json` required fields:**
```json
{
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  },
  "files": ["dist/"],
  "sideEffects": false
}
```

**`files` field:** Must be explicit. Never publish `src/`, `node_modules/`, test files, or build scripts.

**Postinstall scripts:** Prohibited. No arbitrary code execution at install time.

---

## Python Library

**Packaging:** `pyproject.toml` (PEP 621). No `setup.py`.

**No `[project.scripts]`** — this is a library, not a CLI.

**Build backend:** `hatchling` (modern) or `flit` (simple). Avoid `setuptools` for new projects.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "<library>"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = []  # minimize; declare peers as optional extras

[project.optional-dependencies]
dev = ["pytest", "mypy", "ruff"]
```

**Version:** Single source of truth via `importlib.metadata.version("<package>")` or `__version__` in `__init__.py` — not duplicated across files.

**Type stubs:** Provide `py.typed` marker file in package root for PEP 561 compliance.

---

## Rust Library (Crate)

**Cargo.toml:**
```toml
[lib]
name = "<crate>"
crate-type = ["lib"]  # not "cdylib" unless FFI; not "bin"

[package]
edition = "2021"
```

**Cargo.lock:** Committed for binary packages. **Not** committed for library crates — consumers resolve dependency graph.

**Feature flags:** Minimize. Each feature must be independently documented. Default features should work for 90%+ of use cases.

```toml
[features]
default = []
async = ["tokio"]
serde = ["dep:serde"]
```

**`no_std` compatibility:** Declare in lib.rs and document if applicable.

---

## Go Module (Library)

**go.mod:** Module path must be canonical import path. No `main` package at root.

```
module github.com/<org>/<lib>

go 1.22
```

**Package structure:** One package per top-level directory. Internal packages under `internal/` are unexported to consumers.

**go.sum:** Committed. Provides reproducible dependency resolution for consumers building from source.

---

## Versioning and Tagging

### Semver tag convention
```
v1.2.3        # standard
v1.2.3-beta.1 # pre-release
v1.2.3-rc.1   # release candidate
```

### Release checklist
1. CHANGELOG.md updated with version and date
2. Version bumped in package manifest
3. `npm pack --dry-run` / `python -m build --check` / `cargo package` — verify dist contents
4. Tag pushed: `git tag v<semver> && git push origin v<semver>`
5. Package published from tagged commit, not from working directory

---

## CI Build Gates

Before any release:
1. Type check: `tsc --noEmit` / `mypy` / `cargo check` — zero errors
2. Tests pass at minimum coverage threshold
3. Lint: `ruff` / `eslint` / `clippy --deny warnings` — zero errors
4. Build succeeds and produces expected output files
5. Bundle size within declared budget (checked via `size-limit` or `bundlephobia`)
6. Type tests pass (via `tsd` / `expect-type` / `cargo test`)
7. `npm pack --dry-run` / `cargo package` — verify no unexpected files included
8. Dependency audit: `npm audit` / `pip-audit` / `cargo audit` — zero critical/high
