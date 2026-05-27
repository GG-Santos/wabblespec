---
name: platform-game
description: Game platform. Activates when Recipe detects a game project (Unity, Unreal, Godot, web game, or custom engine). Loads game-specific spec templates focused on frame budget, game loop architecture, asset pipeline, input handling, save/load, anti-cheat scope, and platform certification requirements. Produces a materially different spec from Web or CLI — game failure modes (frame drops, desyncs, memory spikes, cheat vectors) are absent from generic templates.
---

# Platform: Game

You are the Game platform layer. You activate when Recipe identifies a game project.

## What this skill does

Loads game-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## When to use

Invoked per activators declared in `skill-rules.json`.

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
| Design authority | Pillar-anchored — every decision tested against declared pillars | User stories | Requirements doc |
| Economy | Virtual economy with declared sinks/faucets, loot tables | N/A | N/A |
| AI | Behavior trees, FSMs, pathfinding — frame-budgeted | N/A | N/A |
| Accessibility | Colorblind modes, full remapping, text scaling — cert required | WCAG | OS accessibility |

A spec without this context misses: game pillars (design authority for conflicts), fixed timestep physics, asset streaming budget, server authority for multiplayer, anti-cheat architecture, frame budget allocation, platform certification checklist, and accessibility requirements that block console cert.

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

## Design phase sequence

Documents must be completed in this order. Specify receipt blocked until P0 and P1 complete. Executor wave blocked until P1.5 complete.

```
P0  game-concept.md          ← pillars, player fantasy, core loop, scope tiers [REQUIRED FIRST]
P1  systems-index.md         ← system list, dependency order, pillar coverage check
P1.5 design-document.md      ← platform targets, frame budget, save, asset pipeline, accessibility, content inventory
    [conditional]
    economy-model.md         ← if virtual economy or monetization declared
    ui-spec.md               ← if HUD or non-trivial UI declared
    [engine-specific]
    engine-specific/godot.md   ← if project.godot detected
    engine-specific/unreal.md  ← if .uproject detected
P2  systems-design.md        ← ECS/Node/Actor architecture, memory, physics, audio, networking
    ai-architecture.md       ← if AI agents declared
P3  technical-spec.md        ← implementation specs, object pools, anti-cheat, profiling gates
```

## Files loaded by this module

**Always loaded:**
```
modules/l3/game/
  spec-template/game-concept.md
  spec-template/systems-index.md
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/qa-pipeline.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
  schemas/
```

**Conditionally loaded (signal → file):**
```
project.godot detected         → spec-template/engine-specific/godot.md
Source/ + .uproject detected   → spec-template/engine-specific/unreal.md
Economy / monetization signal  → spec-template/economy-model.md
HUD / UI signal                → spec-template/ui-spec.md
AI agents declared             → spec-template/ai-architecture.md
```

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `.wabblespec/engine/shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - .wabblespec/engine/shared/dev/frameworks/game/core.md
  conditional_load:
    - signal: "Assets/ + .unity scenes"
      load: .wabblespec/engine/shared/dev/frameworks/game/unity.md
    - signal: "Source/ + .uproject"
      load:
        - .wabblespec/engine/shared/dev/frameworks/game/unreal.md
        - modules/l3/game/spec-template/engine-specific/unreal.md
    - signal: "project.godot"
      load:
        - .wabblespec/engine/shared/dev/frameworks/game/godot.md
        - modules/l3/game/spec-template/engine-specific/godot.md
    - signal: "monetization OR virtual_economy OR currency"
      load: modules/l3/game/spec-template/economy-model.md
    - signal: "hud OR inventory OR menu OR ui"
      load: modules/l3/game/spec-template/ui-spec.md
    - signal: "ai_enemies OR npc OR behavior_tree OR pathfinding"
      load: modules/l3/game/spec-template/ai-architecture.md
  gateway_references:
    - gateway-engineering/references/
    - gateway-security/references/       # if online features active
    - gateway-experience/references/     # if experience gateway active
    - gateway-aesthetic/references/      # if aesthetic gateway active
```

## Output contract

Writes a receipt to `.wabblespec/state/receipts/` on successful completion.
