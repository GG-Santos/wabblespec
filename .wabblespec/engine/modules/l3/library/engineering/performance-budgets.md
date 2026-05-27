# Library Engineering — Performance Budgets

## Bundle Size Budgets

Bundle size is a consumer concern — every byte added to a library is paid by every consumer's users.

| Metric | Default budget | Override in design-document if justified |
|---|---|---|
| Minified + gzipped (ESM) | < 10 KB | Declare if library is inherently large (e.g. parser) |
| Minified + gzipped (CJS) | < 12 KB | CJS slightly larger due to wrapper |
| Type declaration file | < 50 KB | Large types slow TypeScript compilation |
| Uncompressed ESM | < 50 KB | Signals potential for code reduction |

**Measurement:** `size-limit` package for Node libraries. `bundlephobia` for verification.

```json
// package.json
{
  "size-limit": [
    { "path": "dist/index.mjs", "limit": "10 KB" }
  ]
}
```

---

## Tree-Shaking Effectiveness

**Target:** Importing one named export should not include more than 20% of total library code.

**Measurement:**
```bash
# Use rollup to measure what gets included for a single import
rollup --input test-import.js --output.format esm | wc -c
```

**Failure mode:** A barrel file that re-exports everything forces bundlers to include the full library even when one function is used.

---

## API Call Performance Targets

For any synchronous operation:

| Operation type | Target | Notes |
|---|---|---|
| Pure transformation (parse, format, validate) | < 1 ms per call | For typical inputs |
| Heavy computation (compile, encode, diff) | Document specific budget | Use benchmarks |
| Async I/O (if library does I/O) | Declare timeout contract | Per API function |

**Measurement:** `tinybench` / `vitest bench` / `criterion` (Rust) / `testing.B` (Go).

---

## Install Size Budget

Consumer pays this on `npm install`:

| Metric | Budget |
|---|---|
| `node_modules/<lib>` directory | < 500 KB |
| Number of transitive dependencies added | < 5 |
| Total transitive install size | < 2 MB |

**Enforcement:** `bundlephobia` install size tab. `npm pack --dry-run` to verify files included.

---

## TypeScript Compilation Impact

Large `.d.ts` files slow `tsc` across all consumer projects:

| Metric | Budget |
|---|---|
| Type declaration file size | < 50 KB |
| Number of exported generic types | < 20 (complex generics multiply check time) |
| Barrel re-export depth | ≤ 2 levels |

---

## Runtime Memory

For libraries that hold state:

| Resource | Budget | Notes |
|---|---|---|
| Module-level singleton state | Document explicitly | Consumers may bundle multiple versions |
| Per-instance overhead | < 1 KB | For factory/constructor patterns |
| Cache size (if library caches) | Bounded — declare max | Unbounded caches are a memory leak |

**No unbounded caches.** If the library caches parsed/compiled results, the cache must have a maximum size with LRU eviction or explicit clear API.
