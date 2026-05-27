# Desktop Engineering — Performance Budgets

## Startup Time

Users compare desktop apps to native apps. Electron's reputation for slowness makes this critical.

| Metric | Budget | Notes |
|---|---|---|
| Cold start to interactive | < 3s | Time from launch to user can interact |
| Warm start (app already in memory) | < 1s | |
| Splash screen display | < 500ms | Show splash immediately; load in background |
| First meaningful paint | < 2s | |

**Measurement:**
```bash
# macOS
time open -W /Applications/AppName.app

# Windows PowerShell
Measure-Command { Start-Process "AppName.exe" -Wait }
```

**Techniques to hit budget:**
- Lazy-load heavy modules (don't `require` everything at startup)
- Show splash/skeleton immediately, load data asynchronously
- Use `app.whenReady()` efficiently — defer non-critical init
- Tauri: Rust startup is fast by default; webview loading is the bottleneck

---

## Memory Usage

| Metric | Budget | Notes |
|---|---|---|
| Idle memory (app open, no active work) | < 200 MB | Electron baseline ~100MB; app code adds to this |
| Active memory (typical workflow) | < 500 MB | |
| Memory after 4 hours of use | < 800 MB | Detect memory leaks |

**Measurement:** Activity Monitor (macOS) / Task Manager (Windows) / `ps aux` (Linux).

**Renderer process memory:** Each BrowserWindow is a Chromium process. Minimize window count. Destroy windows when not needed (don't just hide).

---

## App Size

| Metric | Budget |
|---|---|
| Installed app size | < 300 MB (Electron); < 10 MB (Tauri) |
| Installer/DMG download | < 150 MB (Electron); < 5 MB (Tauri) |
| Update delta | < 50 MB (declare if larger) |

**Electron size reduction:**
- `electron-builder` pruning: exclude dev dependencies, test files, source maps from packaged app
- Avoid shipping entire `node_modules` — use ASAR archive with only production deps
- Use `--inspect` and `@electron/asar` to audit what's inside the app package

**Tauri size advantage:** Tauri uses OS WebView (no bundled Chromium) — typical installer 3–10 MB.

---

## CPU Usage

| State | Budget |
|---|---|
| Idle (app open, no activity) | < 1% CPU |
| Active (user interaction) | < 30% CPU sustained |
| Background (no windows focused) | < 0.5% CPU |

**No polling loops.** Use event-driven patterns, `setInterval` only where necessary with minimum 1s interval.

**Renderer animations:** Use CSS animations (GPU-accelerated) not JavaScript `requestAnimationFrame` loops for purely visual effects.

---

## UI Responsiveness

| Event | Budget |
|---|---|
| Click response | < 100ms |
| File open dialog → file loaded | < 500ms for small files (< 10MB) |
| Keyboard input → UI update | < 16ms (60fps) |
| IPC round trip (renderer → main → renderer) | < 50ms for non-I/O operations |

**Heavy work off main process:** CPU-intensive operations go in a background worker or Electron utility process, never blocking the main or renderer process.
