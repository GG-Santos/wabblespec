# Desktop Technical Spec Template (P3)

> **Platform:** Desktop
> **Template version:** 1.0
> **Prerequisite:** systems-design.md complete.

---

## IPC Handler Specs

Each IPC channel declared in design-document.md gets one entry.

### Channel: `<channel-name>`

**Direction:** renderer → main / main → renderer / bidirectional

**Input:**
```typescript
type Input = { field: string; count: number }
```

**Validation:** (what main process checks before acting)
- `field` must be non-empty string
- `count` must be positive integer
- Caller frame URL must match `app://` origin

**Output:**
```typescript
type Output = { success: true; data: ResultType } | { success: false; error: string }
```

**GWT scenarios:**
```
Given: renderer calls channel with valid input
When: main process receives the IPC call
Then: handler validates input, executes operation, returns typed output
      AND no Node.js API is accessible from renderer directly

Given: renderer calls channel with malformed input
When: main process validates the input
Then: handler returns { success: false, error: "validation error message" }
      AND no operation is performed
      AND no uncaught exception propagates
```

---

## Auto-Updater Implementation

```typescript
// In main process, after app ready:
import { autoUpdater } from 'electron-updater'

autoUpdater.autoDownload = false   // download only after user confirms
autoUpdater.autoInstallOnAppQuit = true

autoUpdater.on('update-available', (info) => {
  // Prompt user: "Version X.Y.Z available. Download now?"
})

autoUpdater.on('update-downloaded', () => {
  // Prompt user: "Update ready. Restart now?"
})

autoUpdater.on('error', (err) => {
  // Log error, do not crash app
})
```

**Signature verification:** electron-updater verifies package signature automatically when `publish.provider` is configured with code signing cert hash.

---

## Code Signing CI Integration

### macOS (GitHub Actions)
```yaml
- name: Sign and notarize
  env:
    APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
    APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
  run: npm run dist -- --mac
```

### Windows (GitHub Actions)
```yaml
- name: Sign Windows build
  env:
    WIN_CSC_LINK: ${{ secrets.WIN_CSC_LINK }}
    WIN_CSC_KEY_PASSWORD: ${{ secrets.WIN_CSC_KEY_PASSWORD }}
  run: npm run dist -- --win
```

**Never commit certificates or passwords.** All signing credentials in CI secrets only.

---

## Error Handling Strategy

| Error type | Context | Handling |
|---|---|---|
| IPC input validation failure | Main process | Return error object to renderer, log, do not throw |
| Auto-updater network error | Main process | Log, show non-blocking notification, retry next launch |
| File I/O error | Main process | Surface to renderer via IPC error response |
| Renderer crash | Main process | `app.on('render-process-gone')` — log, optionally reload renderer |
| Unhandled main process exception | Main process | `process.on('uncaughtException')` — log to file, restart gracefully |

**Crash logs:** Write to `app.getPath('crashDumps')`. Do not send without explicit user consent.

---

## Packaging Checklist

Before release:
- [ ] Code signed (macOS + Windows)
- [ ] macOS: notarized + stapled
- [ ] Auto-updater configured with correct update server URL
- [ ] Auto-updater signature verification enabled
- [ ] `nodeIntegration: false` in all BrowserWindow configurations
- [ ] `contextIsolation: true` in all BrowserWindow configurations
- [ ] `sandbox: true` in all BrowserWindow configurations
- [ ] All IPC channels listed in preload are used; no dead channels
- [ ] Startup time within declared budget
- [ ] App size within declared budget
