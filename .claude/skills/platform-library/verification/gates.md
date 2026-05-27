# Library Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

---

## Gate 1: Public API Surface Declaration

**Check:** Every exported name is declared in design-document.md public API surface table.

**Method:**
```bash
# Extract actual exports from build output
node -e "console.log(Object.keys(require('./dist/index.cjs')))"
# or for ESM:
node --input-type=module -e "import * as m from './dist/index.mjs'; console.log(Object.keys(m))"
```

Compare output against design-document.md export table.

**Pass:** All actual exports listed in design-document.md. No undocumented exports.
**Fail:** Any export present in build output that is not in design-document.md, or any documented export missing from build.

---

## Gate 2: Semver Compliance Check

**Check:** No breaking changes introduced in a MINOR or PATCH version.

**Method:**
```bash
# Compare public API between current and previous published version
npx @arethetypeswrong/cli <package>@<prev-version>
npx api-extractor run --local

# Or for TypeScript:
npx tsd --files 'test/types/*.test-d.ts'
```

**Pass:** No removed/renamed exports. No changed required parameters. No changed return types.
**Fail:** Any breaking change detected in a non-MAJOR version bump.

---

## Gate 3: Type Correctness

**Check:** TypeScript consumers receive accurate types. No `any` in public API.

**Method:**
```bash
npx tsc --noEmit --strict
npx tsd
```

**Pass:** Zero type errors. No `any` in exported function signatures. Generic types infer correctly.
**Fail:** Any type error, any `any` in public API, any type test failure.

---

## Gate 4: Tree-Shaking Safety

**Check:** Named imports do not pull in unused code. No top-level side effects.

**Method:**
```javascript
// tree-shake-test.mjs — import only one export, measure output size
import { rollup } from 'rollup'
const bundle = await rollup({ input: 'test/import-one.mjs', external: [] })
const { output } = await bundle.generate({ format: 'esm' })
console.log('Single-export bundle size:', output[0].code.length)
```

Also verify `"sideEffects": false` in `package.json`.

**Pass:** Single-export bundle size < 150% of that export's estimated code size. No side effects on import.
**Fail:** Importing one export pulls in clearly unrelated code. Side effects detected at module top level.

---

## Gate 5: Bundle Size Within Budget

**Check:** Minified+gzipped bundle within declared budget.

**Method:**
```bash
npx size-limit
# or:
npx bundlesize
```

**Pass:** All entries within their declared size limit in package.json `size-limit` config.
**Fail:** Any entry exceeds its declared limit.

---

## Gate 6: Peer Dependency Declaration

**Check:** All peer dependencies declared. None bundled that should be external.

**Method:**
```bash
# Check for peer deps bundled in output (should not be present)
node -e "
const pkg = require('./package.json')
const peers = Object.keys(pkg.peerDependencies || {})
peers.forEach(p => {
  const found = require('fs').readFileSync('dist/index.cjs', 'utf8').includes(p)
  if (found) console.error('FAIL: peer dep bundled:', p)
})
"
```

**Pass:** No peer dependency code present in dist output.
**Fail:** Any peer dependency bundled into dist.

---

## Gate 7: Supply Chain Audit

**Check:** Zero high/critical vulnerabilities in dependency tree.

**Method:**
```bash
npm audit --audit-level=high
# or:
cargo audit
pip-audit
```

**Pass:** Zero critical or high severity findings.
**Fail:** Any critical or high finding. (Medium findings: document in SECURITY.md, do not block release if no fix available.)

---

## Gate 8: Registry Publish Dry Run

**Check:** Published artifact contains only intended files. No source, no secrets, no test fixtures.

**Method:**
```bash
npm pack --dry-run
# Review file list — must not include:
# - src/ (source files)
# - test/ or __tests__/
# - .env files
# - *.key, *.pem, credentials*
# - node_modules/
```

**Pass:** File list contains only: `dist/`, `package.json`, `README.md`, `CHANGELOG.md`, `SECURITY.md`, `LICENSE`.
**Fail:** Any unexpected file in the packed artifact.

---

## Gate 9: No Postinstall Scripts

**Check:** Published package.json contains no lifecycle scripts that execute at install time.

**Method:**
```bash
node -e "
const pkg = require('./package.json')
const banned = ['preinstall', 'install', 'postinstall', 'prepare']
banned.forEach(s => {
  if (pkg.scripts?.[s]) console.error('FAIL: lifecycle script present:', s)
})
"
```

**Pass:** No postinstall, preinstall, install, or prepare scripts in published package.json.
**Fail:** Any banned lifecycle script present.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Public API surface declaration complete | Yes |
| 2 | Semver compliance — no breaking changes in MINOR/PATCH | Yes |
| 3 | Type correctness — no `any` in public API | Yes |
| 4 | Tree-shaking safety — no unintended side effects | Yes |
| 5 | Bundle size within declared budget | Yes |
| 6 | Peer dependencies declared and not bundled | Yes |
| 7 | Supply chain audit — zero high/critical CVEs | Yes |
| 8 | Registry publish dry run — no unexpected files | Yes |
| 9 | No postinstall lifecycle scripts | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
