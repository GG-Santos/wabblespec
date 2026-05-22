# Desktop Engineering — Platform Verification

How to run and interpret the desktop verification gates in `verification/gates.md`.

---

## Running All Gates

```bash
# Gate 1-3: TypeScript, security settings, IPC
tsc --noEmit
grep -rn "nodeIntegration" src/main/
grep -rn "contextIsolation" src/main/

# Gate 4: Code signing (macOS)
codesign -dv --verbose=4 dist/mac/AppName.app
spctl -a -t exec -vv dist/mac/AppName.app

# Gate 5: Code signing (Windows)
signtool verify /pa dist/win-unpacked/AppName.exe

# Gate 7: Startup time
time open -W /Applications/AppName.app
```

---

## Verifying Electron Security Settings

```typescript
// Grep for required settings in BrowserWindow creation:
// nodeIntegration: false
// contextIsolation: true
// sandbox: true
// webSecurity: true (or absent — defaults to true)

// Grep for prohibited settings:
// nodeIntegration: true   → FAIL
// contextIsolation: false → FAIL
// sandbox: false          → WARN (justify if present)
// webSecurity: false      → FAIL
```

---

## Verifying IPC Security

```typescript
// Check preload.ts — only allowlisted channels exposed
// Check ipcMain handlers — sender URL validated
// Check that ipcRenderer itself is NOT exposed via contextBridge

grep -n "exposeInMainWorld" src/preload.ts
# Review: only specific APIs exposed, not ipcRenderer itself

grep -n "ipcMain.handle" src/main/ipc.ts
# Review: each handler validates input before acting
```

---

## macOS Notarization Verification

```bash
# After build:
spctl -a -t exec -vv dist/mac/AppName.app
# Expected output: "accepted" with "source=Notarized Developer ID"

# Check stapling:
stapler validate dist/mac/AppName.app
# Expected: "The validate action worked!"

# Verify entitlements:
codesign -d --entitlements - dist/mac/AppName.app
```

---

## Auto-Updater Verification

```bash
# Verify update manifest exists and is signed
ls dist/latest.yml dist/latest-mac.yml

# Verify latest.yml contains sha512 hash
cat dist/latest.yml | grep sha512

# Simulate update check (point to local server)
UPDATE_SERVER_URL=http://localhost:9000 ./AppName --check-for-updates
```

---

## Interpreting Gate Failures

**Gate FAIL — nodeIntegration not false:**
- Find all `new BrowserWindow({...})` calls
- Add `nodeIntegration: false` to each webPreferences
- Verify renderer code doesn't use Node.js directly — move to preload/main

**Gate FAIL — code signing rejected:**
- macOS: verify certificate is "Developer ID Application" not "Development"
- macOS: check entitlements include `com.apple.security.cs.allow-jit` if using V8
- Windows: verify timestamp server was used (signatures without timestamp expire)

**Gate FAIL — startup over budget:**
- Profile: `electron --inspect src/main.js` then Chrome DevTools timeline
- Find heaviest `require()` calls in main process startup
- Move non-critical requires inside the handlers that need them

**Gate FAIL — auto-updater not signing:**
- Verify `publish` config in electron-builder references correct GitHub org/repo
- Verify code signing cert is same cert used for build
- Check `latest.yml` contains `sha512` field after build
