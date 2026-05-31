---
name: platform-desktop
description: Desktop platform. Activates when Recipe detects an Electron, Tauri, or native desktop application target. Loads desktop spec templates, engineering rules, security controls, and verification gates specific to desktop app concerns. Produces a materially different spec from Web or CLI — focused on code signing, auto-updater, IPC security, OS integration, and native distribution.
---

# Platform: Desktop

You are the Desktop platform layer. You activate when Recipe identifies a desktop application target (Electron, Tauri, or native) and load the constraints, templates, and verification gates specific to that environment.

## What this skill does

Loads desktop-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## When to use

Recipe must have already run and identified Desktop as the primary target. Activation signals in `skill-rules.json`.

## What makes Desktop different from other targets

| Concern | Desktop | Web | CLI |
|---|---|---|---|
| Distribution | Installer (DMG, MSI, AppImage, .exe, .deb) | CDN | Binary/registry |
| Code signing | Required (macOS Gatekeeper, Windows SmartScreen) | N/A | Optional but recommended |
| Auto-updater | Electron-updater / Tauri updater — signed delta updates | Server deploy | None |
| IPC | Main/renderer process boundary (Electron) or backend/frontend (Tauri) | N/A | N/A |
| OS integration | File associations, system tray, notifications, global shortcuts | Sandboxed browser | Shell only |
| Node access | Main process has full Node; renderer should be sandboxed | None | Full |
| Privilege model | Runs as user, elevated ops via explicit escalation | Browser sandbox | User context |
| Offline capability | Must declare offline behavior explicitly | Optional | Usually yes |

A spec written without this platform context will miss: code signing requirements (Gatekeeper rejection without it), IPC security (renderer should not have Node access), auto-updater signature verification, OS permission requests (camera, microphone, file system on macOS/Windows), and installer/uninstaller behavior.

## Activation sequence

```
1. Recipe identifies Desktop target and signals platform-desktop activation
2. Load spec-template variant
3. Detect framework (Electron/Tauri/native) via skill-rules.json signals
4. Load engineering/build-toolchain.md and engineering/performance-budgets.md
5. Load security/threat-model.md and security/platform-controls.md
6. Register verification/gates.md with Verifier
7. Write platform activation receipt
```

## Framework routing

| Detected signal | Framework |
|---|---|
| `electron` in package.json dependencies | Electron |
| `src-tauri/tauri.conf.json` | Tauri |
| `.xcodeproj` or `Package.swift` | Swift/native macOS |
| `.sln` with WinUI/WPF | .NET Windows native |
| `CMakeLists.txt` with Qt | Qt/C++ |

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `.wabblespec/engine/shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - .wabblespec/engine/shared/dev/frameworks/desktop/core.md
  conditional_load:
    - signal: "electron in package.json"
      load: .wabblespec/engine/shared/dev/frameworks/desktop/electron.md
    - signal: "src-tauri/tauri.conf.json"
      load: .wabblespec/engine/shared/dev/frameworks/desktop/tauri.md
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
    - gateway-experience/references/     # if experience gateway active
    - gateway-aesthetic/references/      # if aesthetic gateway active
```

## Reference Routing

| Situation | Reference |
|---|---|
| desktop receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type platform-activation` |

## Output contract

**Platform activation receipt** (`.wabblespec/state/receipts/platform-desktop-{timestamp}.json`)

## Files loaded by this module

```
modules/l3/desktop/
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```
