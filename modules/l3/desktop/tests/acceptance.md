# Platform Desktop — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified Desktop as the primary target,
When platform-desktop is invoked,
Then it surfaces: "platform-desktop requires Recipe to have identified Desktop as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified Desktop as the primary target,
When platform-desktop activates,
Then the activation sequence completes in order: spec-template load → framework detection → engineering load → security load → Verifier gate registration → receipt write.

## Framework routing: Electron

Given `electron` is in package.json dependencies,
When platform-desktop detects the framework,
Then `_shared/dev/frameworks/desktop/electron.md` is loaded.
Then IPC security (renderer should not have Node access) concerns are activated.

## Framework routing: Tauri

Given `src-tauri/tauri.conf.json` is present,
When platform-desktop detects the framework,
Then `_shared/dev/frameworks/desktop/tauri.md` is loaded.

## Framework routing: Swift native macOS

Given `.xcodeproj` or `Package.swift` is present (without mobile signals),
When platform-desktop detects the framework,
Then native macOS framework context is activated.

## Framework routing: .NET Windows

Given `.sln` with WinUI or WPF is present,
When platform-desktop detects the framework,
Then .NET Windows native framework context is activated.

## Desktop-specific concerns injected into spec

Given platform-desktop is active,
When spec context is assembled,
Then code signing is declared (macOS Gatekeeper, Windows SmartScreen).
Then auto-updater is declared with signature verification for delta updates.
Then IPC security boundary is addressed: renderer process should not have full Node access.
Then OS permission requests (camera, microphone, file system on macOS/Windows) are declared.
Then offline behavior is declared explicitly.
Then installer and uninstaller behavior is specified.

## Electron IPC security

Given Electron is the detected framework,
When spec context is assembled,
Then the spec declares that the renderer process operates with contextIsolation enabled.
Then the spec declares that nodeIntegration is false in the renderer.
Then any IPC communication uses declared preload scripts with explicit channel allowlists.

## Auto-updater signature verification

Given an auto-updater is declared in the spec,
When the spec is assembled,
Then signed delta updates are required.
Then the auto-updater validates signatures before applying an update.
Then rollback is defined for a failed update.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-desktop attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-desktop run,
Then platform-desktop does not omit code signing requirements.
Then platform-desktop does not allow renderer process full Node access in Electron without declaring it as a known security risk with mitigating controls.
Then platform-desktop does not treat Desktop as equivalent to Web.

## Receipt fields

Given any successful platform-desktop activation,
Then a receipt is written to `.wabblespec/receipts/platform-desktop-<timestamp>.json`.
Then the receipt contains: platform, framework_detected, code_signing_declared, auto_updater_declared, ipc_security_addressed, offline_behavior_declared, gates_registered, capability_handoff.
