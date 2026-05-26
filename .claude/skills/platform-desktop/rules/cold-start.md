# Cold-Start Behavior — Platform Desktop

Defines how the desktop platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `_shared/dev/frameworks/desktop/core.md` missing.
Detection: File read returns 404.
Action: Log warning. Apply continues without process model table (Electron/Tauri/native), IPC security rules, and code signing requirements. Decompose proceeds.
Do NOT: Fail the session.

## Absent: conditional framework files

Condition: `_shared/dev/frameworks/desktop/electron.md` or `desktop/tauri.md` absent when framework is detected.
Detection: Detected via `electron` in package.json / `tauri.conf.json` / `Cargo.toml` (tauri dependency) but file not found.
Action: Proceed without file. Log: "Desktop framework file not found: [path]."

## Absent: security reference files

Condition: `modules/l3/desktop/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security uses generic controls. IPC security invariants still enforced.

## Absent: spec-template files

Condition: `modules/l3/desktop/spec-template/design-document.md` absent.
Action: Specify uses generic structure.

## Default state on cold start

| Field | Default |
|---|---|
| `framework` | Not declared — Apply detects from repo signals |
| `target_os` | Not declared — Specify must elicit (Windows / macOS / Linux / All) |
| `ipc_security` | Enforce: contextIsolation=true, nodeIntegration=false (Electron); deny-by-default (Tauri) |
| `code_signing` | Not declared — Specify must elicit; distribution without signing is a FLAG |
| `auto_updater` | Not declared — Specify must elicit; if present, signature verification required |
| `offline_capable` | Not declared — Specify must elicit; desktop default assumption: offline-capable |

IPC security defaults (contextIsolation, deny-by-default) are platform invariants enforced even without framework files.
