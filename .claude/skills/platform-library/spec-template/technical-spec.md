# Library Technical Spec Template (P3)

> **Platform:** Library/Package
> **Template version:** 1.0
> **Populated by:** Specify module after P2 systems-design.md is complete.
> **Prerequisite:** systems-design.md complete and receipt written.

---

## Implementation Scope

This spec covers implementation of the public API surface declared in design-document.md. Each function/class/export gets one entry below.

---

## API Implementation Specs

### `<FunctionName>`

**Signature:**
```typescript
function <name>(param: Type, options?: Options): ReturnType
```

**Behavior:**
- [describe what it does for valid input]
- [describe what it returns]
- [describe any state changes]

**Edge cases:**
- Empty input: [behavior]
- Null/undefined: [behavior — throw or return null?]
- Invalid type: [throw TypeError or return error object?]

**Error strategy:** [ ] Throw [ ] Return null/undefined [ ] Return Result type [ ] Emit event

**GWT acceptance scenarios:**
```
Given: [precondition]
When: [action]
Then: [expected outcome]
      AND [secondary assertion]

Given: [edge case precondition]
When: [action with edge case input]
Then: [expected error behavior]
```

---

## Type Contract

Every public type exported by the library:

```typescript
export interface Options {
  timeout?: number    // milliseconds, default: 5000
  retries?: number    // default: 3
}

export type Result<T> = { ok: true; value: T } | { ok: false; error: Error }
```

**No `any` allowed in public API.** If a type cannot be expressed precisely, use `unknown` with a type guard.

---

## Error Taxonomy

| Error class | When thrown | Properties |
|---|---|---|
| `<LibraryName>Error` | Base class for all library errors | `code: string`, `message: string` |
| `ValidationError` | Invalid input | extends `<LibraryName>Error`, `field: string` |
| `TimeoutError` | Operation exceeded timeout | extends `<LibraryName>Error`, `timeoutMs: number` |

**Consumer handling:** Consumers should `catch (e)` and check `instanceof <LibraryName>Error` for recoverable errors.

---

## Performance Targets

| Operation | Target | Measurement method |
|---|---|---|
| `<fn>()` cold call | < ___ ms | `performance.now()` before/after |
| `<fn>()` warm call | < ___ ms | Average of 100 iterations |
| Bundle size (minified+gzipped) | < ___ KB | `bundlephobia` or `size-limit` |

---

## Test Coverage Requirements

Every public API export must have:
- [ ] Happy path test
- [ ] Edge case tests (empty input, boundary values)
- [ ] Error path test (each error type thrown)
- [ ] TypeScript type test (via `tsd` or `expect-type`)

**Minimum coverage threshold:** ___ % (enforce via `c8` / `nyc` / `cargo-tarpaulin`)

---

## Backward Compatibility Checklist

Before any release:
- [ ] No exported name removed or renamed (PATCH/MINOR only)
- [ ] No required parameter added to existing function (MINOR or MAJOR)
- [ ] No return type narrowed in a breaking way
- [ ] No previously-optional parameter made required
- [ ] `@deprecated` added to any export scheduled for removal
- [ ] CHANGELOG.md updated with version entry

**Breaking change review gate:** If any checkbox above is unchecked, version must be MAJOR.
