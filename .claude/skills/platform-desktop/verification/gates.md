# Desktop Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

---

## Gate 1: Electron Security Settings

**Check:** All BrowserWindow instances have required security settings.

**Method:**
```bash
grep -rn "nodeIntegration" src/main/
# Must not contain: nodeIntegration: true

grep -rn "contextIsolation" src/main/
# Must contain: contextIsolation: true (not false)

grep -rn "sandbox" src/main/
# Must contain: sandbox: true (not false)

grep -rn "webSecurity" src/main/
# Must not contain: webSecurity: false
```

**Pass:** Zero instances of prohibited settings. All required settings present.
**Fail:** Any prohibited setting found, or any required setting absent from a BrowserWindow.

---

## Gate 2: IPC Channel Audit

**Check:** All IPC channels are declared. All handlers validate input and sender.

**Method:**
```bash
# List all channels registered in main
grep -rn "ipcMain.handle\|ipcMain.on" src/main/

# List all channels called in preload
grep -rn "ipcRenderer.invoke\|ipcRenderer.send" src/preload.ts

# Compare — every preload channel must have a main handler and vice versa
```

**Manual check:** Each handler reviewed for sender validation and input validation.

**Pass:** Every channel has a handler. Every handler validates sender origin and input. No unhandled channels.
**Fail:** Orphan channels, or handlers without input validation.

---

## Gate 3: contextBridge Audit

**Check:** Preload does not expose ipcRenderer, require, or Node.js modules directly.

**Method:**
```bash
grep -n "exposeInMainWorld" src/preload.ts
# Review each — must expose typed functions, not raw ipcRenderer/require
```

**Pass:** Only typed API functions exposed. No raw ipcRenderer, require, or fs exposed.
**Fail:** Any direct exposure of ipcRenderer, require, fs, or other Node.js APIs.

---

## Gate 4: Code Signing Verified

**Check:** Built binaries are properly signed.

**Method (macOS):**
```bash
codesign -dv --verbose=4 dist/mac/AppName.app
spctl -a -t exec -vv dist/mac/AppName.app
# Expected: "accepted" with "source=Notarized Developer ID"
stapler validate dist/mac/AppName.app
```

**Method (Windows):**
```bash
signtool verify /pa dist/win-unpacked/AppName.exe
# Expected: "Successfully verified"
```

**Pass:** Signature valid. Notarized (macOS). Timestamp present (Windows).
**Fail:** Unsigned, invalid signature, not notarized (macOS), or no timestamp (Windows).

---

## Gate 5: Auto-Updater Configuration

**Check:** Auto-updater is configured to verify signatures. Update server URL is HTTPS. No bypass flags.

**Method:**
```bash
# Verify no signature verification bypass:
grep -rn "verifyUpdateCodeSignature" src/
# Must not be set to false

# Verify update server URL is HTTPS:
grep -rn "publisherName\|updateServer\|endpoint" electron-builder.yml tauri.conf.json

# Verify latest.yml generated after build:
ls dist/latest.yml dist/latest-mac.yml
cat dist/latest.yml | grep sha512
```

**Pass:** Signature verification enabled. HTTPS endpoint. SHA-512 hash present in manifest.
**Fail:** Signature bypass, HTTP endpoint, or missing hash.

---

## Gate 6: No Remote URL in Privileged Window

**Check:** BrowserWindow instances load only local app resources (app:// or file://).

**Method:**
```bash
grep -rn "loadURL.*http" src/main/
# Review each — only acceptable if app is explicitly a web wrapper (documented in design-doc)

grep -rn "loadFile" src/main/
# These are correct — local file loading
```

**Pass:** No remote HTTP/HTTPS URLs loaded in BrowserWindow (or documented web-wrapper exception).
**Fail:** Remote URL loaded in BrowserWindow without documented justification.

---

## Gate 7: Startup Time Within Budget

**Check:** Cold start to interactive within declared budget.

**Method:**
```bash
# macOS
time open -W /Applications/AppName.app

# Or with Playwright Electron testing:
const startTime = Date.now()
const app = await electron.launch({ args: ['dist/main.js'] })
await app.firstWindow()
console.log('Startup:', Date.now() - startTime, 'ms')
```

**Pass:** Cold start within declared budget (default: 3s).
**Fail:** Cold start exceeds budget.

---

## Gate 8: Installer Smoke Test

**Check:** App installs cleanly, launches, and uninstalls without residue.

**Method:**
- Install from generated installer (DMG/MSI/AppImage)
- Launch app: verify opens without error
- Verify basic functionality (at minimum: main window appears, no crash)
- Uninstall: verify app directory removed (Windows: check for leftover files in Program Files)

**Pass:** Install succeeds. App launches. Basic function verified. Uninstall clean.
**Fail:** Install failure, launch crash, or uninstall leaves residue.

---

## Gate 9: OS Permission Handling

**Check:** App handles permission denial gracefully.

**Method (manual):**
- Block each OS permission the app requests (in System Settings)
- Launch app and trigger the feature that requires the permission
- Verify app does not crash
- Verify user sees a clear error/guidance message
- Verify app does not repeatedly re-request the permission

**Pass:** Graceful degradation for every declared OS permission on denial.
**Fail:** Crash on permission denial, or repeated permission prompts.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Electron security settings | Yes |
| 2 | IPC channel audit | Yes |
| 3 | contextBridge audit | Yes |
| 4 | Code signing verified | Yes |
| 5 | Auto-updater configuration | Yes |
| 6 | No remote URL in privileged window | Yes |
| 7 | Startup time within budget | Yes |
| 8 | Installer smoke test | Yes |
| 9 | OS permission handling | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
