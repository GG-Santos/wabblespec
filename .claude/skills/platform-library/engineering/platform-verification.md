# Library Engineering — Platform Verification

How to run and interpret the library verification gates in `verification/gates.md`.

---

## Running All Gates

```bash
# From project root, after build:
python scripts/run-platform-gates.py --platform library

# Or run each gate manually (examples for Node/TypeScript library):
npm run build
npm run test
npm run type-check
npx size-limit
```

---

## Per-Language Verification Commands

### Node/TypeScript Library
```bash
# Build
npm run build

# Type check (must be zero errors)
npx tsc --noEmit

# Type tests (public API contract)
npx tsd   # or: npx expect-type

# Bundle size gate
npx size-limit

# Tree-shaking test
node scripts/tree-shake-test.mjs

# Dry-run publish (verify files included)
npm pack --dry-run

# Dependency audit
npm audit --audit-level=high
```

### Python Library
```bash
# Build
python -m build

# Type check
mypy src/<package>/ --strict

# Verify py.typed present
ls src/<package>/py.typed

# Dry-run publish
twine check dist/*

# Dependency audit
pip-audit
```

### Rust Library
```bash
# Build
cargo build

# Type tests + unit tests
cargo test

# Lint
cargo clippy -- -D warnings

# Package verification (check included files)
cargo package --list

# Audit
cargo audit
```

### Go Module
```bash
# Build check
go build ./...

# Tests
go test ./...

# Vet
go vet ./...

# Module verification
go mod verify
```

---

## Interpreting Results

**Gate FAIL — bundle too large:**
- Run `npx source-map-explorer dist/index.mjs` to visualize what's large
- Check for accidentally bundled peer dependencies (should be `external`)
- Check for duplicate code from barrel imports
- Check if a heavy dependency has a lighter alternative

**Gate FAIL — tree-shaking broken:**
- Find all barrel files (`export * from './something'`)
- Check for side effects at module top level (`console.log`, `Array.prototype.extend =`)
- Verify `"sideEffects": false` in package.json
- Use `rollup-plugin-visualizer` to identify the import pulling everything in

**Gate FAIL — type errors:**
- Run `tsc --noEmit --strict` and address each error
- `any` in public API is a gate failure — use `unknown` + type guards
- Missing return type annotation on public function — add explicit type

**Gate FAIL — breaking change without MAJOR bump:**
- Run `npm diff <prev-version> <current>` to compare exports
- Use `api-extractor` to detect public API surface changes
- Check: removed export? renamed? changed required param? → bump MAJOR

---

## Regression Prevention

After gates pass once:
1. Record gate results in platform activation receipt
2. Add gate checks to CI (see build-toolchain.md)
3. Add `size-limit` to `package.json` scripts to block bundle regressions
4. Any change to public exports or types requires re-running all gates
5. Gate results are not cached — run fresh on each release candidate
