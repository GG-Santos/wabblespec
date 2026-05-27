# Cold-Start Behavior — Platform Mobile

Defines how the mobile platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/mobile/core.md` missing.
Detection: File read returns 404 during Apply routing phase.
Action: Log warning. Apply continues without offline-first, permissions model, and Keychain/Keystore rules. Decompose proceeds.
Do NOT: Fail the session.

## Absent: conditional framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/mobile/react-native.md` (or flutter/swift-uikit/kotlin-compose) absent when framework is detected.
Detection: Detected via `react-native` in package.json / `pubspec.yaml` / `.xcodeproj` / `build.gradle` but file not found.
Action: Proceed without file. Log: "Mobile framework file not found: [path]."

## Absent: security reference files

Condition: `modules/l3/mobile/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security uses generic mobile controls. Keychain/Keystore requirement is still enforced as a platform invariant.

## Absent: spec-template files

Condition: `modules/l3/mobile/spec-template/design-document.md` absent.
Action: Specify uses generic structure. Log: "Mobile spec-template not found."

## Default state on cold start

| Field | Default |
|---|---|
| `target_os` | Not declared — Specify must elicit (iOS / Android / Both) |
| `framework` | Not declared — Apply detects from repo signals |
| `offline_support` | Not declared — Specify must elicit; default assumption: no offline support |
| `credential_storage` | Keychain (iOS) / Keystore (Android) enforced — localStorage/SharedPreferences for credentials forbidden |
| `minimum_os` | Not declared — Specify must elicit |
| `distribution` | Not declared — Specify must elicit (App Store / Play Store / Enterprise / TestFlight) |

Credential storage enforcement (Keychain/Keystore) is a platform invariant — applies even without framework files.
