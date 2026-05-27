# Desktop Framework Core

Cross-framework knowledge for desktop application targets. Loaded by Apply for every Desktop platform task.

## Desktop constraints

Every desktop spec must declare:
- **Target OS**: Windows, macOS, Linux — or all three; behavior differences per OS noted
- **Distribution**: installer type (DMG, MSI, AppImage, deb/rpm, Homebrew), signing, auto-updater
- **Code signing**: required (macOS Gatekeeper, Windows SmartScreen); declare certificate type and provisioning
- **Minimum OS version**: Windows 10+, macOS 12+, etc.

## Process model

Desktop apps typically have a privileged process + renderer/UI process boundary:

| Framework | Privileged process | UI process |
|---|---|---|
| Electron | Main process (Node.js, full OS access) | Renderer process (Chromium, sandboxed) |
| Tauri | Core process (Rust, restricted by capability system) | WebView (OS webview, sandboxed) |
| Native | OS process (full access) | Same process |

Spec must declare: what runs in each process and why.

## IPC security

For Electron and Tauri, IPC is the bridge between privileged code and UI code. Rules:

- **Electron**: use contextBridge to expose a minimal API to the renderer; do not expose `require` or Node APIs directly; `nodeIntegration: false` and `contextIsolation: true` required
- **Tauri**: declare all commands in `tauri.conf.json` capabilities; default-deny model; only declare what the frontend needs

## Code signing requirements

### macOS

- Developer ID certificate for distribution outside App Store
- Notarization required (Apple servers scan the binary; Gatekeeper checks notarization)
- Hardened runtime required for notarization
- Declare any entitlements needed (microphone, camera, network client, etc.)

### Windows

- EV or OV certificate for SmartScreen trust
- Authenticode signing with timestamp
- SmartScreen builds reputation over time — new certificates trigger warnings

## Auto-updater

Spec must declare:
- **Update channel**: stable, beta, canary
- **Update check frequency**: on launch, background polling
- **User prompt**: silent install or user-prompted
- **Rollback**: can the user roll back? how?
- **Delta updates**: full binary or differential patch
- **Signature verification**: update payload must be signed; verified before install

## Offline capability

Desktop apps can function offline by default — they are installed locally. Spec must declare:
- Which features require network connectivity
- What the user sees when network is unavailable
- Whether offline data is cached (and for how long)

## OS integration

Declare which OS APIs are used:
- System tray / menu bar icon
- File associations (open .myformat files with this app)
- Global keyboard shortcuts
- Notifications (OS notification center)
- Deep links (custom URL scheme)
- Startup at login

## Performance budget

| Metric | Target |
|---|---|
| Cold start to interactive | < 3s (installer builds); < 1s (subsequent launches) |
| Memory (idle) | Declare baseline; alert if significantly exceeded |
| CPU (idle) | Near zero; background tasks must not peg CPU |
| Installer size | Declare; large installers affect download conversion |
