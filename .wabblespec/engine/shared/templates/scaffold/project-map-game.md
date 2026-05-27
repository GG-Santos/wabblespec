# Project Map

**Project:** ___ UNDECLARED  
**Platform:** Game  
**Language:** ___ UNDECLARED (C# / C++ / GDScript / Lua)  
**Scaffolded:** ___ UNDECLARED  
**explored_at:** ___ UNDECLARED  
**build_target:** game  
**freshness_state:** FRESH  
**valid_until:** ___ UNDECLARED (24h from explored_at)  
**WabbleSpec version:** ___ UNDECLARED  

---

## Entry Points

_Fill in the engine-appropriate entry point:_

- **Unity:** `Assets/Scripts/GameManager.cs` (or main scene bootstrap MonoBehaviour)
- **Unreal Engine:** `Source/{ProjectName}/{ProjectName}GameMode.cpp`
- **Godot:** `scenes/main.tscn` + `scripts/main.gd`
- **Custom/other:** `src/main.{ext}` — update to actual entry

## Tech Stack

| Area | Technology | Version (pinned) | Confidence |
|---|---|---|---|
| engine | ___ UNDECLARED (Unity / Unreal / Godot / custom) | ___ UNDECLARED | exact |
| language | ___ UNDECLARED (C# / C++ / GDScript) | ___ UNDECLARED | exact |
| physics | ___ UNDECLARED (engine built-in / Bullet / Box2D) | ___ UNDECLARED | exact |
| audio | ___ UNDECLARED (FMOD / Wwise / engine built-in) | ___ UNDECLARED | inferred |
| test | ___ UNDECLARED (NUnit / GTest / GUT / custom) | ___ UNDECLARED | exact |
| ci | ___ UNDECLARED (requires GPU runner — see build-toolchain.md) | n/a | inferred |
| profiler | ___ UNDECLARED (Unity Profiler / Unreal Insights / RenderDoc) | n/a | assumed |
| certification | ___ UNDECLARED (Steam / PlayStation / Xbox / Nintendo — see build-toolchain.md) | n/a | assumed |

_Engine version must be pinned — unpinned engine upgrades cause undocumented behavior changes._

## Risk Files

| Path | Risk reason | Churn count | Note |
|---|---|---|---|
| `Assets/Scripts/GameManager.cs` (or engine entry) | cross-cutting | 0 | Game state machine — scene transitions, win/lose conditions |
| `Assets/Scripts/Physics/` (or equivalent) | cross-cutting | 0 | Physics logic — changes affect determinism; multiplayer sync depends on this |
| `Assets/Scripts/NetworkManager.cs` (or equivalent, if multiplayer) | cross-cutting | 0 | Network sync — determinism and latency budget |
| `ProjectSettings/` (or equivalent engine project config) | cross-cutting | 0 | Engine config — quality settings, physics fixed timestep, layer matrix |

## Impact Slices

### entry-points
**Reason:** Game bootstrap and main game loop — all state and scene changes flow through here.

- Main scene / entry script (update to actual)
- `ProjectSettings/` (engine-level config)
- Game state machine (update to actual path)

### api-surface
**Reason:** Public game systems interface — how game objects communicate with core systems.

- `Assets/Scripts/Events/` (event system — update)
- `Assets/Scripts/Interfaces/` (public interfaces / ABCs — update)
- Network message schemas (if multiplayer — update)

**Test paths:**
- `Assets/Tests/` (NUnit / engine test runner)
- `tests/` (update to actual test directory)

### test-coverage
**Reason:** Unit + physics determinism + frame-time regression test locations.

- `Assets/Tests/` (engine test runner tests)
- `tests/frame-time/` (frame-time regression fixtures — required per build-toolchain.md)
- `tests/physics/` (physics determinism tests — required for multiplayer)

### risk
**Reason:** Files from Risk Files table above.

- Engine entry / GameManager
- Physics scripts
- NetworkManager (if multiplayer)
- ProjectSettings

### conventions
**Reason:** Script naming, event system patterns, and performance-sensitive code markers.

- _See Conventions section below_

## Spec Artifacts

| Path | Artifact type | Status |
|---|---|---|
| `.wabblespec/receipts/scaffold-receipt-{timestamp}.json` | scaffold-receipt | LOCKED |

## Conventions

- Script naming: PascalCase (e.g. `PlayerController.cs`, `EnemySpawner.cs`)
- Event system: centralized event bus or ScriptableObject events (not direct references between unrelated systems)
- Physics: always use fixed timestep (`Time.fixedDeltaTime` / engine equivalent) — never frame-rate-dependent physics
- Performance-sensitive paths: marked with `// PERF:` comment for profiler identification
- Asset naming: lowercase hyphen-separated (e.g. `player-idle.png`, `bgm-main-theme.wav`)
- Determinism: physics calculations must produce identical results given the same seed — required for multiplayer replay and test
- ___ UNDECLARED — add project-specific conventions after first Explore run

## Git State

- **Active branch:** ___ UNDECLARED
- **Recent changes:** (none — fresh scaffold)
- **Uncommitted count:** ___ UNDECLARED

## Gaps

- Target fps declared in performance-budgets.md — frame budget derived from it; not yet validated against real rendering
- Platform certification targets: declared in build-toolchain.md — submission requirements not yet reviewed
- GPU runner availability for CI: required by build-toolchain.md — not yet confirmed
- Physics determinism: not yet tested (no test fixtures yet)
- Frame-time regression baseline: no baseline yet (requires first playable build)
- Audio integration: assumed from build-toolchain.md — not yet confirmed
- Multiplayer: not determined (stateless / server-authoritative / peer-to-peer)
- Save system: not yet defined
- Localization: not yet scoped

---

*Generated by Scaffold from `.wabblespec/engine/shared/templates/scaffold/project-map-game.md`. Replace all `___ UNDECLARED` with actual values. Explore updates this file after generation. GPU runner is required for CI per build-toolchain.md.*
