# Performance Budgets — Library

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/library`.
> Reference: `.wabblespec/engine/shared/references/performance-budgets.md`.
> Note: Libraries have no runtime SLOs. Their performance budgets are build-time and API-surface contracts.

---

## Bundle size

### Published bundle size (minified + gzipped)

**Target:** ≤ ___ KB minified + gzipped for the full library
**Rationale:** Library bundle size is a direct cost to every consumer's users; size regressions are a breaking change for consumers with size budgets
**Measurement:** bundlephobia or `size-limit` in CI; fail on regression above declared ceiling
**PII impact:** none

### Tree-shakeable module ceiling

**Target:** Each importable module ≤ ___ KB minified + gzipped when imported individually
**Rationale:** Libraries that cannot be tree-shaken force consumers to import the full bundle; per-module size caps enforce tree-shakeability
**Measurement:** rollup bundle analysis per export path; `size-limit` with per-module entries
**PII impact:** none

### Side-effect declaration

**Target:** All modules with side effects declared in `sideEffects` field in package.json; modules with no side effects declared as `sideEffects: false`
**Rationale:** Incorrect `sideEffects` declarations prevent bundlers from tree-shaking; must be explicit
**Measurement:** automated check that `sideEffects` field is present and accurate; test with build on a consuming project
**PII impact:** none

---

## Runtime performance (per declared operation)

### Synchronous operation latency

**Target:** ___ UNDECLARED — declare per critical operation if the library performs non-trivial computation
**Rationale:** Libraries that consume significant CPU in synchronous operations block consumers' main threads; declare ceiling if operation > 1ms expected
**Measurement:** benchmark.js or Vitest bench; measure on minimum-spec hardware; track across versions
**PII impact:** none

### Memory allocation per operation

**Target:** ___ UNDECLARED — declare if library is called in tight loops (e.g., parsers, transformers, validators)
**Rationale:** Libraries called millions of times per second must minimize allocations; GC pressure from allocations is invisible until scale
**Measurement:** V8 heap profiler allocation flamegraph during benchmark; track retained bytes per operation
**PII impact:** none

---

## API surface

### Exported symbol count

**Target:** ≤ ___ top-level exports (declare ceiling to prevent API sprawl)
**Rationale:** API surface growth is effectively irreversible under semver; each added export is a long-term maintenance commitment
**Measurement:** CI check on exported symbol count; diff on every PR
**PII impact:** none

### Deprecated symbol removal policy

**Target:** Deprecated symbols removed in next major version only; ≥ 1 minor version with deprecation warning before removal
**Rationale:** Required by `l3/library` acceptance tests; consumers need at least one release cycle to migrate
**Measurement:** deprecation warnings present in minor release; removal blocked until major bump
**PII impact:** none

---

## Dependencies

### Zero runtime dependencies (preferred)

**Target:** ___ runtime dependencies (declare zero if achievable; if > 0, justify each)
**Rationale:** Each runtime dependency is a supply chain risk and a version conflict risk for consumers; prefer zero
**Measurement:** `npm ls --depth=0 --prod` or equivalent; alert on any new runtime dep added
**PII impact:** none

### Peer dependency version range

**Target:** Peer dependency ranges declared as broadly as defensibly correct (e.g., `"react": ">=17"` not `"react": "18.2.0"`)
**Rationale:** Overly tight peer dep ranges force consumers to maintain multiple library versions; declared in `l3/library` acceptance tests AT-LIB-03
**Measurement:** semver range analysis; verify range is ≥ 2 major versions wide where the API contract is stable
**PII impact:** none

---

## Type coverage

### TypeScript declaration coverage

**Target:** 100% of public API has TypeScript declarations; zero `any` types in public API surface
**Rationale:** `any` in public API exports type safety problems to consumers
**Measurement:** `tsc --strict --noEmit` on declaration files; `ts-prune` or equivalent for unused exports
**PII impact:** none

---

## PII fields (excluded from log schema)

<!-- Libraries generally do not log. If yours does (e.g., analytics SDK, logging library): -->
___ UNDECLARED — populate only if the library writes to any persistent log
