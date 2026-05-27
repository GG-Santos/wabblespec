# Node.js / TypeScript Reference

> **Type:** Language reference | Loaded by platform packages on demand.

---

## Toolchain

| Tool | Decision | Notes |
|---|---|---|
| Runtime | Node.js LTS (current: 22.x) | Never pin to odd (non-LTS) versions |
| Language | TypeScript | `strict: true` always — no exceptions |
| Package manager | pnpm (preferred) / npm / yarn | Lockfile committed — never `.gitignore` lockfile |
| Bundler | tsup / esbuild / rollup | Per platform: library→tsup, app→vite/next |
| Lint | ESLint + `@typescript-eslint` | Errors not warnings — lint failures block CI |
| Format | Prettier | Config committed, `--check` in CI |
| Test | Vitest (preferred) / Jest | |

---

## Module System

**ESM preferred.** Use `"type": "module"` in `package.json`. Avoid CommonJS in new code.

```json
{
  "type": "module",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  }
}
```

**Never mix ESM and CJS** in the same package without explicit dual build config.

---

## TypeScript Config

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

`noUncheckedIndexedAccess` catches array index errors at compile time — always enable.

---

## Non-Negotiable Rules

1. `strict: true` — no `any` types unless behind an explicit escape hatch with comment.
2. Lockfile committed and up to date — `pnpm install --frozen-lockfile` in CI.
3. No `require()` in new ESM code. No `.js` extension omissions in ESM imports.
4. `package.json` engines field set: `"node": ">=20"`.
5. No `process.exit()` without flushing async work — use `process.exitCode` instead.
6. Environment variables read at startup, not scattered through code — validate with zod or similar.

---

## Error Handling

```typescript
// Never swallow errors
try {
  await doThing();
} catch (err) {
  // Log and re-throw, or handle specifically — never just `catch (err) {}`
  throw new AppError("doThing failed", { cause: err });
}

// Async: always await or explicitly handle the promise
// Bad: doThing();  ← fire-and-forget, uncaught rejection
// Good: await doThing();  OR  void doThing().catch(handleError);
```

**Unhandled promise rejections crash the process in Node 15+.** Every promise needs `.catch()` or `await`.

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Type errors at runtime | `any` type or missing `strict` | Enable `strict`, audit `any` usages |
| Import fails in ESM | Missing `.js` extension | Add `.js` to relative imports (even for `.ts` source) |
| CI fails on clean install | Lockfile not committed or out of sync | Run `pnpm install` locally, commit lockfile |
| Memory leak in long-running process | Event listener not removed | Always pair `on` with `off` in cleanup |
| Circular dependency | Deep import chains | Restructure — use dependency injection |
