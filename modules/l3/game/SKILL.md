---
name: platform-game
description: Game platform. Activates when Recipe detects a game project (Unity, Unreal, Godot, web game, or custom engine). Loads game-specific spec templates focused on frame budget, game loop architecture, asset pipeline, input handling, save/load, anti-cheat scope, and platform certification requirements. Produces a materially different spec from Web or CLI — game failure modes (frame drops, desyncs, memory spikes, cheat vectors) are absent from generic templates.
---

# Platform: Game

You are the Game platform layer. You activate when Recipe identifies a game project.

## What this skill does

Loads game-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## What makes Game different from other targets

| Concern | Game | Web | Desktop |
|---|---|---|---|
| Frame budget | 16.6ms (60fps) or 11.1ms (90fps) — hard deadline | N/A | N/A |
| Update loop | Fixed timestep game loop (physics) + variable render | Event-driven | Event-driven |
| Asset pipeline | Textures, meshes, audio, animations — compressed + streamed | Static assets | Static assets |
| State | Deterministic simulation (for replay/rollback) | Stateless | Stateful |
| Memory | Pool allocators, no GC pauses in hot path | GC acceptable | GC acceptable |
| Networking | Authoritative server + client prediction + rollback | Request/response | N/A |
| Cheating | Client-side validation is theater — server must be authoritative | N/A | N/A |
| Platform cert | Console certification requirements (Sony/Microsoft/Nintendo) | App store | Code signing |
| Save system | Corrupt save = player rage | N/A | File I/O |

A spec without this context misses: fixed timestep physics, asset streaming budget, server authority for multiplayer, anti-cheat architecture, frame budget allocation, and platform certification checklist.

## Activation sequence

```
1. Recipe identifies Game target
2. Detect engine (Unity/Unreal/Godot/custom) via skill-rules.json
3. Load spec-template variant, engineering, security, verification
4. Write platform activation receipt
```

## Engine routing

| Signal | Engine |
|---|---|
| `Assets/` + `.unity` scenes | Unity |
| `Source/` + `.uproject` | Unreal Engine |
| `project.godot` | Godot |
| `index.html` + canvas + game loop | Web game |

## Files loaded by this module

```
modules/l3/game/
  spec-template/ engineering/ security/ verification/ schemas/
```
