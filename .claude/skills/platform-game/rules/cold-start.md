# Cold-Start Behavior — Platform Game

Defines how the game platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `_shared/dev/frameworks/game/core.md` missing.
Detection: File read returns 404.
Action: Log warning. Apply continues without game loop timing, frame budget table, and server-authoritative networking rules. Decompose proceeds.
Do NOT: Fail the session.

## Absent: conditional framework files

Condition: `_shared/dev/frameworks/game/unity.md` (or unreal/godot) absent when engine is detected.
Detection: Detected via `*.unity` project files / `uproject` / `project.godot` but file not found.
Action: Proceed without file. Log: "Game framework file not found: [path]."

## Absent: security reference files

Condition: `modules/l3/game/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security applies generic controls. Anti-cheat architecture requirement is still enforced for multiplayer targets.

## Absent: spec-template files

Condition: `modules/l3/game/spec-template/design-document.md` absent.
Action: Specify uses generic structure.

## Default state on cold start

| Field | Default |
|---|---|
| `engine` | Not declared — Apply detects from repo signals |
| `game_loop` | Not declared — Specify must elicit (fixed timestep / variable timestep) |
| `multiplayer` | Not declared — Specify must elicit; if yes, server-authoritative architecture required |
| `target_platform` | Not declared — Specify must elicit (PC / Console / Mobile / WebGL) |
| `frame_budget` | 16.6ms (60fps) assumed; Specify must declare if different target |
| `anti_cheat` | Not declared — required if multiplayer=true; Specify must elicit approach |
| `save_system` | Not declared — Specify must elicit; corruption recovery required |

Server-authoritative requirement for multiplayer is a platform invariant — applies even without framework files.
