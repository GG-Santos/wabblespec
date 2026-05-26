# Desktop Security — Platform Controls

These controls apply to all Desktop targets. Enforced by Verifier via `verification/gates.md`.

---

## Control 1: Electron Security Settings (Mandatory)

**Rule:** All BrowserWindow instances must have the following webPreferences:

```javascript
new BrowserWindow({
  webPreferences: {
    nodeIntegration: false,      // REQUIRED
    contextIsolation: true,      // REQUIRED
    sandbox: true,               // REQUIRED
    webSecurity: true,           // default — never set to false
    allowRunningInsecureContent: false,  // default — never set to true
    experimentalFeatures: false, // default
  }
})
```

**Enforcement:** Code review + grep for `nodeIntegration: true`, `contextIsolation: false`, `sandbox: false`, `webSecurity: false`.

**Exception process:** None for nodeIntegration and contextIsolation. Sandbox exceptions require written justification and architectural review.

---

## Control 2: contextBridge Minimal Exposure

**Rule:** Preload script must expose only the minimum API surface needed by the renderer. Never expose `ipcRenderer` directly.

**Prohibited:**
```javascript
contextBridge.exposeInMainWorld('ipc', ipcRenderer)  // forbidden
contextBridge.exposeInMainWorld('require', require)  // forbidden
```

**Required:** Expose only specific, typed functions:
```javascript
contextBridge.exposeInMainWorld('app', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  // only what renderer actually uses
})
```

---

## Control 3: IPC Input Validation

**Rule:** Every IPC handler in the main process must validate:
1. Sender frame URL is from the app's own origin
2. All input fields conform to declared types and constraints
3. Unknown or unexpected message types are rejected

**Pattern:**
```javascript
ipcMain.handle('write-file', async (event, { path, content }) => {
  // Validate sender
  if (!event.senderFrame.url.startsWith('app://')) throw new Error('unauthorized')
  // Validate input
  if (typeof path !== 'string' || !path) throw new Error('invalid path')
  if (typeof content !== 'string') throw new Error('invalid content')
  // Validate path scope
  const resolved = resolve(path)
  if (!resolved.startsWith(allowedRoot)) throw new Error('path traversal')
  // Execute
  await fs.writeFile(resolved, content)
})
```

---

## Control 4: Code Signing Required

**Rule:** All distributed binaries must be code-signed with a valid, non-expired certificate.

- macOS: Developer ID Application certificate. Must be notarized and stapled.
- Windows: EV or Standard code signing certificate with timestamp.
- Linux: GPG signature alongside binary (AppImage); or Flatpak/Snap with store signing.

**Enforcement:** CI build fails if signing step fails. Gate 4 verifies signature post-build.

---

## Control 5: Auto-Updater Signature Verification

**Rule:** Auto-updater must verify the signature of the update package before applying. Silent installs of unsigned updates are prohibited.

**electron-updater:** `verifyUpdateCodeSignature` must not be disabled.
**Tauri:** `updater.pubkey` must be set to the public key corresponding to the signing key.

**Enforcement:** Code review verifies no `verifyUpdateCodeSignature: false` or equivalent bypass.

---

## Control 6: Credential Storage in OS Keychain

**Rule:** Tokens, passwords, and API keys must be stored in the OS keychain, not in plain files.

**Acceptable storage:**
- macOS: Keychain via `keytar` or `@electron/keytar`
- Windows: Credential Manager via `keytar`
- Linux: Secret Service API (libsecret) via `keytar`
- Tauri: `tauri-plugin-stronghold`

**Unacceptable storage:** `localStorage`, plain JSON files in userData, `electron-store` without encryption for sensitive values.

---

## Control 7: No Remote URL in BrowserWindow

**Rule:** BrowserWindow instances must not load content from remote HTTP/HTTPS URLs except via a declared, controlled mechanism.

**Acceptable:** `app://` or `file://` protocol handlers pointing to bundled app resources.
**Unacceptable:** `win.loadURL('https://app.example.com')` — loads remote content in a privileged window.

**For remote content:** Use `shell.openExternal()` to open in the user's browser, not in a BrowserWindow with elevated privileges.

**Exception:** Apps that are explicitly wrappers for a web application must document this in design-document.md and apply strict CSP on the loaded URL.

---

## Control 8: File Path Validation Before I/O

**Rule:** All file paths supplied by users, IPC messages, or URL handlers must be resolved and validated before any I/O operation.

```javascript
import { resolve } from 'path'
import { existsSync } from 'fs'

function safePath(userPath: string, allowedRoot: string): string {
  const resolved = resolve(userPath)
  if (!resolved.startsWith(resolve(allowedRoot))) {
    throw new Error('Path traversal detected')
  }
  return resolved
}
```
