# Extension Engineering — Build Toolchain

## Browser Extension Build

**Preferred tool:** WXT (wxt.dev) — handles multi-browser output, HMR in dev, MV2/MV3 target switching, `.zip` packaging for store submission.

**Alternative:** Plasmo, or Vite + `vite-plugin-web-extension`.

**Manual alternative:** webpack with `copy-webpack-plugin` for manifest + assets.

### WXT config (`wxt.config.ts`)
```typescript
import { defineConfig } from 'wxt'

export default defineConfig({
  manifest: {
    name: '<Extension Name>',
    permissions: ['storage', 'activeTab'],
  },
  browser: 'chrome',   // or 'firefox', 'edge', 'safari'
  manifestVersion: 3,
})
```

### Output structure
```
dist/chrome-mv3/
  manifest.json
  background.js
  content.js
  popup.html
  popup.js
  icons/
```

---

## Build Commands

```bash
# Development with HMR
npx wxt dev

# Production build
npx wxt build

# Build for Firefox
npx wxt build -b firefox

# Package for store submission (.zip)
npx wxt zip

# Run extension in browser (loads dist/)
npx wxt open
```

---

## TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "WebWorker"],
    "strict": true,
    "moduleResolution": "bundler"
  }
}
```

**Chrome types:** `@types/chrome` package. Required for all `chrome.*` API calls.

**WebWorker lib:** Required for service worker context — includes `ServiceWorkerGlobalScope`.

---

## Cross-Browser Build Matrix

| Browser | Manifest version | Build target | Package format |
|---|---|---|---|
| Chrome | MV3 | `chrome-mv3` | `.zip` for CWS |
| Firefox | MV3 (FF 109+) | `firefox-mv3` | `.zip` for AMO |
| Edge | MV3 | `edge-mv3` | `.zip` for Edge Add-ons |
| Safari | MV3 | Xcode project | `.xcarchive` |

**webextension-polyfill:** Add if targeting Firefox + Chrome with `browser.*` unified API.

---

## VS Code Extension Build

**Build tool:** `vscode`'s built-in `esbuild` via `@vscode/vsce`.

**Entry point:** `src/extension.ts` → compiled to `dist/extension.js`.

```json
// package.json scripts
{
  "scripts": {
    "compile": "tsc -p ./",
    "vscode:prepublish": "npm run compile",
    "package": "vsce package",
    "publish": "vsce publish"
  }
}
```

**`.vscodeignore`:** Exclude source files, test files, node_modules from `.vsix`:
```
src/
test/
.vscode-test/
node_modules/
```

---

## CI Build Gates

Before any store submission:
1. TypeScript: `tsc --noEmit` — zero errors
2. Lint: `eslint src/` — zero errors
3. Tests pass (unit + integration with `@playwright/test` for browser extension E2E)
4. `npm audit` — zero high/critical findings
5. Build succeeds for all target browsers
6. Manifest validation: `web-ext lint` (Firefox) or Chrome's `manifest_version: 3` validator
7. Package size within store limits (Chrome: 128MB total, Firefox: 200MB)
8. No remote code execution in CSP
9. All permissions used (unused permissions flagged)
