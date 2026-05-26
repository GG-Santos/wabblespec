# Electron Framework

Loaded by Apply when electron is detected in package.json.

## Version baseline

Electron 28+ (follows Chromium cadence). Always use the latest stable release — older versions have known security vulnerabilities.

## Security configuration — required

```javascript
// main.js — required security settings
const win = new BrowserWindow({
  webPreferences: {
    nodeIntegration: false,        // REQUIRED: no Node in renderer
    contextIsolation: true,        // REQUIRED: separate contexts
    sandbox: true,                 // recommended: OS sandbox on renderer
    preload: path.join(__dirname, 'preload.js'),
  },
})
```

Any deviation from `nodeIntegration: false` + `contextIsolation: true` must be declared in spec with justification. These are security requirements, not preferences.

## Context bridge

```javascript
// preload.js — only way to expose APIs to renderer
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('api', {
  // Expose only what the renderer needs
  readFile: (path) => ipcRenderer.invoke('read-file', path),
  saveFile: (path, content) => ipcRenderer.invoke('save-file', path, content),
})

// renderer.js — use via window.api
window.api.readFile('/path/to/file').then(content => ...)
```

The preload bridge is the security boundary. Declare every method exposed in spec.

## IPC patterns

```javascript
// main process — handle IPC calls
ipcMain.handle('read-file', async (event, filePath) => {
  // Validate filePath before using it
  if (!isAllowedPath(filePath)) throw new Error('Access denied')
  return fs.readFile(filePath, 'utf-8')
})
```

- `ipcMain.handle` / `ipcRenderer.invoke` — async request/response (preferred)
- `ipcMain.on` / `webContents.send` — one-way events

Always validate inputs in the main process — the renderer is untrusted.

## Auto-updater

```javascript
const { autoUpdater } = require('electron-updater')

autoUpdater.checkForUpdatesAndNotify()
autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall()
})
```

- electron-updater handles GitHub Releases, S3, and custom servers
- Code sign the release artifacts before publishing — electron-updater verifies signatures
- Spec must declare: update server, release channel, install behavior (prompt vs silent)

## Packaging and signing

```
electron-builder      — packaging, installer creation, code signing
electron-forge        — alternative toolchain (simpler for small projects)
```

```yaml
# electron-builder.yml
appId: com.example.app
mac:
  category: public.app-category.productivity
  hardenedRuntime: true
  entitlements: build/entitlements.mac.plist
  notarize: true
win:
  target: nsis
  signingHashAlgorithms: [sha256]
```

Spec must include signing configuration for each target OS.

## Performance

- Renderer startup: avoid heavy computation in the renderer thread; use worker threads or main process
- Memory: each BrowserWindow has its own V8 heap; minimize open windows
- Bundle size: use webpack or Vite to bundle renderer; tree-shake unused Node modules
- WebContents: `win.webContents.openDevTools()` must be disabled in production
