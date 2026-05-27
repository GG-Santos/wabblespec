# Platform: Desktop

Desktop GUI application target (Electron, Tauri, native, etc.). Activates when Recipe identifies a desktop application as the primary build target.

**Skill:** `modules/l3/desktop/SKILL.md`

## What makes Desktop different

| Concern | Desktop approach |
|---------|-----------------|
| OS integration | File system access, system tray, native menus — declared explicitly |
| Auto-update | Update strategy declared: silent, prompted, manual |
| Crash reporting | Crash reporter declared and privacy implications addressed |
| Distribution | Signed installer, notarized (macOS), Microsoft Store — declared |
| Native APIs | IPC boundary between renderer and main process declared (Electron) |
| Multi-window | Window management strategy declared if multi-window |
| Accessibility | Platform accessibility APIs (MSAA, NSAccessibility, ATK) — declared |

## Platform-specific spec sections

- OS targets: Windows, macOS, Linux — which are supported and to what version
- IPC contract: all messages between main and renderer processes declared (Electron/Tauri)
- File system access pattern: which paths, why, with what permissions
- Installation and update flow: user experience for install, update, and uninstall
- Native menu structure: declared for apps with non-trivial menu bars

## Security controls loaded

- Node integration: disabled in renderer by default (Electron); contextIsolation on
- IPC validation: all messages from renderer validated in main process before acting
- File path traversal: user-supplied paths sanitized before file system operations
- Keychain usage: credentials stored in OS keychain — not localStorage or config files
- CSP: Content Security Policy declared for renderer (Electron)

## Gateway interaction

Desktop targets typically activate:
- `gateway-security` — always (IPC boundary, file system access, keychain)
- `gateway-engineering` — Medium/High complexity
- `gateway-aesthetic` — platform-specific UI conventions (macOS HIG, Windows Fluent)
- `gateway-experience` — user-facing features
- `gateway-accessibility` — via experience gateway
