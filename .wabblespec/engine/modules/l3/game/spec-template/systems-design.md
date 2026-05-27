# Game Systems Design Template (P2)

> **Platform:** Game | **Prerequisite:** design-document.md complete.
>
> **Engine routing — read before using this document:**
> - **Unity / Custom engine:** The ECS section below applies directly.
> - **Godot:** Node/scene composition replaces ECS. See `spec-template/engine-specific/godot.md`. The ECS section does not apply — use the Node/Scene Architecture section instead.
> - **Unreal Engine:** Actor/Component model replaces ECS. See `spec-template/engine-specific/unreal.md`. Object pool pattern is managed via UObject pooling, not a generic `Queue<T>`.

---

## Node / Scene Architecture *(Godot only — skip if Unity or Unreal)*

> See `spec-template/engine-specific/godot.md` for full Godot architecture patterns.
> Summarize your scene tree structure here for project record.

```
Root
  ├── [Autoloads: GameManager, SaveManager, EventBus, AudioBus]
  ├── World (Node3D / Node2D)
  │     ├── Level (instanced scene)
  │     └── Entities (Node)
  │           └── [Enemy, NPC, Pickup] (instanced scenes)
  └── UI (CanvasLayer)
        └── HUD, Menus (Control scenes)
```

**Cross-scene communication:** Signals + EventBus autoload. No `get_node("../../")` across scene boundaries.

---

## Entity Component System (ECS) Architecture *(Unity / Custom engine — skip if Godot or Unreal)*

```
World
  ├── Entities (IDs only)
  ├── Components (pure data, no logic)
  │     ├── Transform { position, rotation, scale }
  │     ├── Velocity { linear, angular }
  │     ├── Health { current, max }
  │     └── Renderable { mesh, material }
  └── Systems (logic, operates on component sets)
        ├── PhysicsSystem (Transform + Velocity)
        ├── HealthSystem (Health + DamageEvents)
        └── RenderSystem (Transform + Renderable)
```

**Why ECS:** Cache-friendly memory layout, decoupled logic, testable systems in isolation.

> **Unreal Engine note:** UE5 uses the Actor/Component model, not ECS. Do not use this section for Unreal projects. See `spec-template/engine-specific/unreal.md` — subsystems, GAS, and UPROPERTY memory replace ECS and the object pool below.

---

## Memory Management

**Allocation strategy:**

| System | Allocator | Why |
|---|---|---|
| Entity pool | Object pool | No per-frame heap alloc |
| Particles | Ring buffer | Fixed size, auto-evict oldest |
| Audio | Pre-allocated audio buffers | No alloc in audio thread |
| Level data | Linear allocator (cleared on load) | Fast bulk clear |
| Per-frame scratch | Stack allocator | Reset each frame, no fragmentation |

**No heap allocation in hot path.** Pre-allocate all object pools at scene load. Frame allocator for temp data.

---

## Physics Architecture

**Engine:** [ ] Built-in physics [ ] PhysX [ ] Bullet [ ] Jolt [ ] custom

**Fixed timestep:** ___ Hz (e.g., 60 Hz = 16.6ms step)

**Collision layers:**

| Layer | Collides with |
|---|---|
| Player | Environment, Enemies, Collectibles |
| Enemy | Environment, Player, Projectiles |
| Projectile | Environment, Enemies |
| Trigger | Player only |

**Physics budget:** ≤ 3ms per fixed step for declared entity count.

---

## Networking Architecture (if multiplayer)

**Topology:** Client-Server (not P2P — server is authoritative)

```
Client:
  Input capture → send to server → client prediction → render predicted state
  Receive server state → reconcile (rollback if mismatch)

Server:
  Receive inputs from all clients
  Simulate authoritative game state
  Broadcast state snapshots at ___ Hz
  Validate all inputs (reject cheat inputs)
```

**Packet rate:** Client → Server: ___ Hz. Server → Client: ___ Hz.
**Lag compensation:** ___ ms rollback window for hitscan.

---

## Audio Architecture

**Audio thread:** Separate thread. No lock contention with game thread.

**Sound banks:**
| Bank | Loaded when | Size budget |
|---|---|---|
| UI sounds | App start | < 10 MB |
| Ambient | Level load | < 50 MB |
| Music | Streamed | N/A (streamed) |
| SFX | Level load | < 100 MB |

**3D audio:** Positional audio with occlusion. Max simultaneous voices: ___ (hardware limit).

---

## Save/Load System

```
Save flow:
  Collect game state snapshot
  Serialize to temp file: save_slot_X.tmp
  Compute CRC32 checksum
  Write checksum to file
  Atomic rename: save_slot_X.tmp → save_slot_X.sav
  Delete previous backup: save_slot_X.bak
  Rename old save to backup: save_slot_X.sav → save_slot_X.bak

Load flow:
  Read save_slot_X.sav
  Validate checksum
  If invalid: load save_slot_X.bak
  If both invalid: offer new game with error message
```

---

## LOD System

**Level of Detail tiers:**

| Distance | LOD tier | Poly reduction |
|---|---|---|
| < 10m | LOD0 | Full detail |
| 10–50m | LOD1 | ~50% |
| 50–200m | LOD2 | ~25% |
| > 200m | Culled or impostor | Billboard |

**Occlusion culling:** Enabled for all scenes with > 100 visible objects.
