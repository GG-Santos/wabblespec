# Desktop Design Document Template (P1)

> **Platform:** Desktop
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-desktop activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this desktop application does, who uses it, which OS(es) it targets, and the primary workflow it enables.

---

## Framework [REQUIRED]

[ ] Electron (Node.js + Chromium)
[ ] Tauri (Rust backend + WebView)
[ ] Swift/SwiftUI (macOS/iOS native)
[ ] .NET WinUI / WPF (Windows native)
[ ] Qt/C++ (cross-platform native)
[ ] Other: ___

**Reasoning for framework choice:**

---

## OS Targets [REQUIRED]

| OS | Min version | Distribution format |
|---|---|---|
| [ ] macOS | ___ | DMG + notarized PKG |
| [ ] Windows | ___ | MSI / NSIS installer / MSIX |
| [ ] Linux | ___ | AppImage / .deb / .rpm / Flatpak |

**Architecture targets:** [ ] x64 [ ] arm64 (Apple Silicon) [ ] Universal Binary (macOS)

---

## Code Signing Strategy [REQUIRED]

Code signing is not optional. Unsigned apps are blocked by macOS Gatekeeper and flagged by Windows SmartScreen.

### macOS
- [ ] Developer ID Application certificate (App Store distribution)
- [ ] Apple Developer Program membership required
- Notarization: `xcrun notarytool submit` after signing
- Stapling: `xcrun stapler staple` for offline verification

### Windows
- [ ] EV Code Signing Certificate (from DigiCert, Sectigo, etc.)
- [ ] Standard Code Signing Certificate
- Timestamping: required — signatures expire without it
- SmartScreen reputation: new certificates show warning until sufficient download volume

### Linux
- [ ] AppImage signing (GPG signature alongside binary)
- [ ] Flatpak (signed by Flathub or self-hosted OSTree repo)
- [ ] .deb with GPG-signed apt repo

**Certificate storage:** Certificates stored in CI secrets (never committed to repo).

---

## Auto-Updater Strategy [REQUIRED]

| Property | Decision |
|---|---|
| Update mechanism | [ ] electron-updater [ ] Tauri updater [ ] Sparkle (macOS) [ ] None — manual |
| Update server | [ ] GitHub Releases [ ] S3 + CloudFront [ ] Custom server |
| Update channel | [ ] stable only [ ] stable + beta |
| Update check frequency | On launch + every ___ hours |
| User control | [ ] Auto-download + prompt to restart [ ] Prompt before download [ ] Silent |
| Update signature verification | Required — updater must verify signature before applying |
| Rollback capability | [ ] Yes [ ] No |

**Update files are signed.** Updater rejects unsigned or tampered update payloads.

---

## IPC Architecture [REQUIRED] (Electron)

Electron's security model: renderer process must not have direct Node.js access.

| Setting | Required value | Reason |
|---|---|---|
| `nodeIntegration` | `false` | Prevents renderer from running Node.js |
| `contextIsolation` | `true` | Isolates preload script from renderer |
| `sandbox` | `true` | OS-level sandbox for renderer |
| `webSecurity` | `true` | Never disable |

**Preload script:** Exposes only the APIs the renderer needs via `contextBridge.exposeInMainWorld`.

**IPC channels declared:**

| Channel name | Direction | Purpose | Sensitive? |
|---|---|---|---|
| `get-config` | renderer → main | Read app config | No |
| `open-file` | renderer → main | Open file dialog | No |
| [list all] | | | |

---

## OS Permissions [REQUIRED]

| Permission | Requested | When/Why |
|---|---|---|
| Camera | [ ] Yes [ ] No | [purpose] |
| Microphone | [ ] Yes [ ] No | [purpose] |
| Full disk access | [ ] Yes [ ] No | [purpose — avoid if possible] |
| Notifications | [ ] Yes [ ] No | [purpose] |
| Accessibility | [ ] Yes [ ] No | [purpose — high privilege, justify carefully] |

---

## OS Integration Features

| Feature | Implemented | Notes |
|---|---|---|
| System tray | [ ] Yes [ ] No | |
| File associations | [ ] Yes [ ] No | File extensions: ___ |
| Global keyboard shortcuts | [ ] Yes [ ] No | Declare shortcuts |
| Drag and drop (file) | [ ] Yes [ ] No | |
| Native notifications | [ ] Yes [ ] No | |
| Deep links / custom URL scheme | [ ] Yes [ ] No | Scheme: `<app>://` |
| Login item (launch at startup) | [ ] Yes [ ] No | User opt-in required |

---

## GWT Acceptance Scenarios (Desktop-specific)

```
Given: the app is downloaded and run on macOS for the first time
When: the user double-clicks the .app or .dmg
Then: macOS Gatekeeper does not block launch
      AND the app is properly signed and notarized
      AND no "unidentified developer" warning appears

Given: an update is available
When: the auto-updater downloads the update
Then: the update signature is verified before applying
      AND a tampered update is rejected with an error
      AND the user is prompted before restart (not silently restarted)

Given: the renderer process receives IPC messages
When: the main process handles an IPC call from renderer
Then: the main process validates the channel name is in the declared allowlist
      AND the main process validates input before acting
      AND the renderer cannot access Node.js APIs directly

Given: the app requests an OS permission (camera, microphone)
When: the user denies the permission
Then: the app degrades gracefully without crashing
      AND the user is shown a clear message explaining how to grant it later
      AND the app does not re-request the permission on every launch
```

---

## Open Questions

List unresolved design decisions. Specify blocks receipt until REQUIRED sections complete.
