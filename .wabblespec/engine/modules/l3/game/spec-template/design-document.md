# Game Design Document Template (P1)

> **Platform:** Game | Sections marked `[REQUIRED]` must be filled before Specify receipt.

---

## Overview [REQUIRED]

One paragraph: genre, core loop, target platforms, player count (single/multi), monetization model.

---

## Game Pillars Reference [REQUIRED]

> Full pillar definitions live in `game-concept.md`. Summarize here for quick cross-reference during implementation.

| Pillar | Name | Falsifiability test (one line) |
|---|---|---|
| 1 | [Name] | This design fails Pillar 1 if... |
| 2 | [Name] | This design fails Pillar 2 if... |

Any implementation decision that conflicts with a pillar must be escalated before proceeding. Do not silently override a pillar.

---

## Accessibility Requirements [REQUIRED]

Declare accessibility tier from `ui-spec.md`. Minimum requirements must be met before Gate 7 (platform certification) and Gate 11 (accessibility minimum compliance).

| Feature | Status | Notes |
|---|---|---|
| Full action remapping | [ ] Planned [ ] Implemented | All gameplay inputs, not just presets |
| Colorblind mode | [ ] Planned [ ] Implemented | Deuteranopia minimum |
| Text scaling | [ ] Planned [ ] Implemented | 100%–150% minimum |
| Subtitles / captions | [ ] Planned [ ] Implemented | All voiced content |
| Motion sensitivity | [ ] Planned [ ] N/A | Camera shake / screen flash sliders |

**Accessibility tier declared in ui-spec.md:** [ ] Basic [ ] Standard [ ] Comprehensive

---

## Content Inventory [REQUIRED]

Declare expected content counts before Executor wave begins. These counts are the baseline for Gate 12 (content completeness). A count of `0` means "not in scope" — omitting a row means "unknown" which blocks Specify receipt.

| Content type | MVP count | Vertical Slice count | Full Vision count | Notes |
|---|---|---|---|---|
| Levels / scenes | ___ | ___ | ___ | |
| Enemy types | ___ | ___ | ___ | |
| NPC types | ___ | ___ | ___ | |
| Item types | ___ | ___ | ___ | Weapons, armor, consumables |
| Dialogue lines | ___ | ___ | ___ | Approximate |
| Quests / missions | ___ | ___ | ___ | |
| Music tracks | ___ | ___ | ___ | |
| [Other] | ___ | ___ | ___ | |

---

## Difficulty Curve [REQUIRED if difficulty system declared]

**Onboarding ramp (first ___ minutes):**
- Mechanics introduced one at a time
- Failure punished lightly (no progress loss in first ___ minutes)
- First combat encounter: ___ enemies, ___ threat level

**Mid-game skill ceiling:**
- Core mechanics mastered by hour ___
- Advanced mechanics unlocked at ___
- Target player frustration rate: ___ (declare: acceptable vs. unacceptable failure cadence)

**Difficulty settings:**

| Setting | Label | Parameters that change |
|---|---|---|
| Easy | ___ | [Parameters] |
| Normal | ___ | Baseline |
| Hard | ___ | [Parameters] |

**Dynamic difficulty adjustment:** [ ] None [ ] Present — declare adjustment trigger and parameters:

---

## Platform Targets [REQUIRED]

| Platform | Min spec | Distribution | Certification required |
|---|---|---|---|
| [ ] PC (Windows) | CPU: ___ GPU: ___ RAM: ___ | Steam / EGS / itch.io | No |
| [ ] macOS | ___ | App Store / direct | App Store review |
| [ ] iOS | iPhone ___ | App Store | App Store review |
| [ ] Android | API ___ | Google Play | Play review |
| [ ] PS5 | — | PlayStation Store | Sony TRC certification |
| [ ] Xbox | — | Microsoft Store | Microsoft XR certification |
| [ ] Nintendo Switch | — | Nintendo eShop | Lot Check certification |
| [ ] Web | Browser: ___ | itch.io / own site | No |

---

## Frame Budget [REQUIRED]

| Target | Frame time | Notes |
|---|---|---|
| 60fps | 16.6ms total | Standard |
| 90fps | 11.1ms total | VR required |
| 120fps | 8.3ms total | High-refresh displays |

**Budget allocation:**
```
Total frame budget: 16.6ms
  ├── Physics/simulation:  ~3ms
  ├── Game logic/AI:       ~3ms
  ├── Rendering (CPU):     ~4ms
  └── Rendering (GPU):     ~6ms
  (remaining: buffer for spikes)
```

---

## Game Loop Architecture [REQUIRED]

**Physics timestep:** Fixed (___ Hz) — decoupled from render rate.

**Render:** Variable — interpolates between physics steps.

```
while running:
  accumulator += deltaTime
  while accumulator >= FIXED_STEP:
    physics_update(FIXED_STEP)
    accumulator -= FIXED_STEP
  alpha = accumulator / FIXED_STEP
  render(interpolate(prev_state, curr_state, alpha))
```

**Why fixed timestep:** Determinism for replay, network rollback, consistent physics behavior across frame rates.

---

## Multiplayer Authority Model [REQUIRED if multiplayer]

[ ] Not applicable — single player

[ ] **Server-authoritative:** Server owns all game state. Client sends inputs only. Client prediction + server reconciliation for responsiveness.

[ ] **Peer-to-peer with lockstep:** All peers simulate identically. Any peer drop pauses game.

[ ] **Client-authoritative (local only):** No networked play. Single-player or local co-op.

**Anti-cheat scope:** Server-authoritative = server validates all inputs (speed, position, damage). Client-authoritative = anti-cheat is theater — document this explicitly.

---

## Save System [REQUIRED]

| Property | Decision |
|---|---|
| Save format | Binary (compact) / JSON (debuggable) / custom |
| Save location | Platform save directory (not working dir) |
| Auto-save | Every ___ minutes / on scene transition / manual only |
| Save slots | ___ slots |
| Corruption handling | Checksum validation; restore from backup slot on failure |
| Cloud save | [ ] Yes (platform cloud) [ ] No |

**Corrupt save is unacceptable.** Write to temp file → validate checksum → atomic replace. Never write directly to save file.

---

## Asset Pipeline [REQUIRED]

| Asset type | Source format | Runtime format | Streaming |
|---|---|---|---|
| Textures | PSD/PNG | Compressed (BC7/ASTC/ETC2) | MIP streaming |
| Audio | WAV/FLAC | Compressed (Ogg/Opus/ADPCM) | Streaming for music |
| 3D meshes | FBX/GLTF | Engine mesh format | LOD system |
| Animations | FBX | Engine anim format | No streaming |

**Platform texture compression:** Different per platform. BC7 (PC), ASTC (iOS/Android), BC7 (PS5/Xbox). Build system compresses per target.

---

## GWT Acceptance Scenarios (Game-specific)

```
Given: the game runs at 60fps target
When: the scene is at maximum expected entity count
Then: frame time stays below 16.6ms (no frame drops)
      AND no garbage collection pauses cause visible hitches

Given: player save file is corrupted (simulated)
When: game attempts to load the save
Then: corruption is detected via checksum
      AND game loads last valid backup save
      AND player is notified of the recovery

Given: multiplayer client predicts a movement (client prediction)
When: server sends authoritative position that differs
Then: client smoothly reconciles to server position
      AND no visible rubber-banding occurs for small discrepancies

Given: player attempts a known cheat (speed hack, teleport)
When: server validates the input
Then: invalid input is rejected
      AND player position is corrected to last valid server position
      AND cheat attempt is logged
```

---

## Open Questions

Specify blocks receipt until REQUIRED sections complete.
