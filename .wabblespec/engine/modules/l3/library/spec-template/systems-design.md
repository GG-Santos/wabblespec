# Library Systems Design Template (P2)

> **Platform:** Library/Package
> **Template version:** 1.0
> **Populated by:** Specify module after P1 design-document.md is complete.
> **Prerequisite:** design-document.md `[REQUIRED]` sections complete and receipt written.

---

## Build Pipeline Architecture

```
Source (src/)
  └── Language-specific build tool
        ├── ESM output   → dist/index.mjs
        ├── CJS output   → dist/index.cjs
        ├── Types        → dist/index.d.ts
        └── UMD (opt)    → dist/index.umd.js
```

**Build tool selected:** [ ] tsup [ ] unbuild [ ] rollup [ ] esbuild-direct [ ] Vite lib mode [ ] cargo [ ] python-build [ ] other: ___

**Reason for selection:**

---

## Exports Map Strategy

How consumers access the library:

```json
{
  "exports": {
    ".": { ... },
    "./utils": { ... },
    "./types": { "types": "./dist/types.d.ts" }
  }
}
```

**Sub-path exports declared:** [ ] None — single entry point [ ] List: ___

**Blocked deep imports:** Sub-paths NOT in the exports map are blocked by Node.js resolution. Confirm no consumer relies on deep imports to internal paths.

---

## Peer Dependency Resolution Strategy

| Peer dep | Resolved how | Consumer responsibility |
|---|---|---|
| `react` | Consumer bundles their own copy | Consumer must have react in their own deps |

**Optional peer deps:** Dependencies that enable optional features:

| Package | Feature unlocked | How detected at runtime |
|---|---|---|
| `<pkg>` | `<feature>` | `try { require('<pkg>') } catch {}` |

---

## Type Generation Strategy

**Source:** [ ] TypeScript source (types inferred from implementation) [ ] Hand-written `.d.ts` declarations

**Declaration emit:** `tsc --declaration --emitDeclarationOnly` or via build tool type output.

**`types` field in package.json:** Points to root declaration file.

**Generic constraints:** List any complex generic types that require explicit documentation:

---

## Internal Module Boundaries

Modules that must not be imported by consumers:

| Internal path | Why internal | What's exposed instead |
|---|---|---|
| `src/internal/` | Implementation details | Public API in `src/index.ts` |

**Enforcement:** `exports` map blocks deep imports. `@internal` JSDoc tags on internal functions. ESLint `import/no-internal-modules` if applicable.

---

## Side Effect Inventory

Complete list of all top-level side effects in the library:

| File | Side effect | Justification |
|---|---|---|
| `src/polyfills.js` | Modifies `globalThis` | Required for IE11 compat |
| _(none if side-effect-free)_ | | |

**`sideEffects` declaration:**
```json
{
  "sideEffects": false
}
```
or
```json
{
  "sideEffects": ["src/polyfills.js", "*.css"]
}
```

---

## Changelog Strategy

**Format:** [ ] Keep a Changelog (keepachangelog.com) [ ] Conventional Commits + auto-generate [ ] Manual

**Breaking change marker:** `### Breaking Changes` section in CHANGELOG.md under each MAJOR version entry.

**Deprecation marker:** Inline `@deprecated` + CHANGELOG entry under `### Deprecated`.

---

## Dependency Minimization Plan

Each dependency added increases consumer install size and supply chain risk. Justify every dependency:

| Dependency | Why it cannot be replaced with < 20 lines of own code | Audited? |
|---|---|---|
| `<dep>` | [justification] | [ ] |

**Target:** Zero runtime dependencies if feasible. Bundle only what cannot be avoided.
