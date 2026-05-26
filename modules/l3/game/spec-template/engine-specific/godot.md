# Engine-Specific Architecture: Godot 4

> **Applies when:** `project.godot` detected in project root.
> **Replaces:** The generic ECS section in systems-design.md. Godot does not use ECS. Node/scene composition is the native architecture.
> **Engine authority:** Godot 4.x. Patterns here match Godot 4 API. If using Godot 3.x, signal syntax and some node names differ — declare version in technical-spec.md.

---

## Node / Scene Architecture

Godot's primary architecture unit is the **scene** — a tree of **nodes**. Scenes compose into larger scenes. There are no entities or components in the Unity/ECS sense.

```
Root (Node)
  ├── GameManager (Node)          ← autoload, not in scene tree directly
  ├── World (Node3D)
  │     ├── Level (Node3D)        ← instanced scene
  │     │     ├── Terrain (StaticBody3D)
  │     │     └── Enemies (Node3D)
  │     │           └── Enemy (CharacterBody3D) ← instanced scene, multiple
  └── UI (CanvasLayer)
        ├── HUD (Control)
        └── PauseMenu (Control)
```

**Scene composition rules:**
- Each scene owns its subtree. A scene does not reach into another scene's children directly.
- Cross-scene communication uses signals or autoloads — never `get_node("../../OtherScene/Child")`.
- Instanced scenes are the unit of reuse (not prefabs, not components).

---

## Node Type Selection

| Use case | Node type | Notes |
|---|---|---|
| 2D game entity | `CharacterBody2D` | Use for player, enemies with movement |
| 3D game entity | `CharacterBody3D` | `move_and_slide()` handles physics |
| Static geometry | `StaticBody2D` / `StaticBody3D` | Terrain, walls — no movement |
| Trigger zones | `Area2D` / `Area3D` | Detection only, no physics response |
| UI screens | `Control` (subclasses) | `VBoxContainer`, `GridContainer`, etc. |
| Layer overlay | `CanvasLayer` | HUD, menus — always on top of world |
| Particle effects | `GPUParticles2D` / `GPUParticles3D` | GPU-accelerated |
| Audio playback | `AudioStreamPlayer` / `AudioStreamPlayer3D` | 3D: positional audio |

---

## Signals — Typed Declarations

All signals must be typed in Godot 4. Untyped signals (`signal foo`) are permitted but produce warnings in strict mode and break static analysis.

```gdscript
# Correct — typed signal
signal health_changed(new_health: int, max_health: int)
signal enemy_died(enemy: Enemy, position: Vector3)
signal item_collected(item_id: String, quantity: int)

# Incorrect — untyped
signal health_changed   # ← avoid
```

**Connection patterns:**

```gdscript
# Direct connection (same scene)
health_component.health_changed.connect(_on_health_changed)

# Deferred (physics callbacks — prevents re-entrant physics)
physics_area.body_entered.connect(_on_body_entered, CONNECT_DEFERRED)

# One-shot (fires once then disconnects)
animation_player.animation_finished.connect(_on_intro_done, CONNECT_ONE_SHOT)

# Disconnect on node free — use Callable with target
enemy.died.connect(on_enemy_died.bind(enemy_id))
```

**Rule:** Signals emitted from physics callbacks (`_physics_process`, `body_entered`) must use `CONNECT_DEFERRED` on any receiver that modifies the scene tree. Direct connection from physics = re-entrant physics = crash.

---

## Autoloads (Global Singletons)

Autoloads are scenes or scripts that load before any other scene and persist for the application lifetime.

**What belongs in autoloads:**

| Autoload | Responsibility |
|---|---|
| `GameManager` | Game state (current level, session data, phase) |
| `SaveManager` | Save/load API — reads and writes save files |
| `AudioBus` | Music and ambient audio — cross-scene continuity |
| `EventBus` | Global signal relay for cross-system events |
| `SettingsManager` | User preferences (volume, graphics, remapping) |

**What does not belong in autoloads:**
- Level-specific logic (use the level scene's root node)
- Player state (use the Player node or a resource attached to it)
- UI state (use the active UI scene)

**EventBus pattern** (decoupled cross-scene events):
```gdscript
# EventBus.gd (autoload)
signal quest_completed(quest_id: String)
signal player_level_up(new_level: int)
signal scene_transition_requested(target_scene: String)

# Emitter (any scene)
EventBus.quest_completed.emit("main_quest_01")

# Receiver (any other scene)
EventBus.quest_completed.connect(_on_quest_completed)
```

---

## Static Typing — Enforcement

All variables, parameters, and return types must be declared. Static typing in Godot 4 enables:
- Editor autocompletion on custom types
- Compile-time error detection (not just runtime)
- LSP support in external editors

```gdscript
# Correct
var health: int = 100
var speed: float = 5.0
var player: Player  # typed node reference
@onready var sprite: Sprite2D = $Sprite2D

func take_damage(amount: int) -> void:
    health = max(0, health - amount)
    health_changed.emit(health, max_health)

func get_position() -> Vector3:
    return global_position

# Incorrect — untyped
var health = 100          # ← avoid
func take_damage(amount): # ← avoid
    health -= amount
```

**`@onready` declarations:** All node references obtained via `$NodePath` must use `@onready`. Never assign node references in `_init()` — the scene tree is not ready.

---

## Resource System — Data Objects

Godot Resources (`.tres` / `.res`) are the equivalent of ScriptableObjects (Unity) or DataAssets (Unreal). Use them for data that designers edit.

```gdscript
# ItemData.gd — a Resource subclass
class_name ItemData extends Resource

@export var item_id: String = ""
@export var display_name: String = ""
@export var base_damage: int = 0
@export var icon: Texture2D

# Usage
var sword: ItemData = preload("res://data/items/sword.tres")
player.equip(sword)
```

**`preload` vs `load`:**
- `preload("res://path")` — compile-time, path must exist, fast
- `load("res://path")` — runtime, can fail, returns null on missing file
- Use `preload` for fixed assets. Use `load` for dynamic or user-generated paths with null check.

---

## Memory and Object Lifecycle

Godot manages memory via reference counting (`RefCounted`) and scene tree ownership (`Node`).

**Node lifecycle rules:**
- Nodes added to the scene tree are owned by their parent.
- `queue_free()` is safe and deferred — node frees at end of frame.
- Never call `free()` on a node still in the scene tree — use `queue_free()`.
- Orphan nodes (instantiated but never added to tree) must be explicitly freed or they leak.

**Object pooling in Godot:**
```gdscript
# BulletPool.gd
class_name BulletPool extends Node

var _pool: Array[Bullet] = []
const POOL_SIZE: int = 64

func _ready() -> void:
    for i in POOL_SIZE:
        var b: Bullet = BULLET_SCENE.instantiate()
        b.visible = false
        add_child(b)
        _pool.append(b)

func get() -> Bullet:
    for bullet in _pool:
        if not bullet.visible:
            return bullet
    return null  # pool exhausted

func release(bullet: Bullet) -> void:
    bullet.visible = false
    bullet.set_physics_process(false)
```

**Common leak sources:**
- Signals connected but never disconnected when node is freed — use `connect` on nodes that outlive the receiver, or disconnect in `_exit_tree()`
- Resources `load()`ed in a loop without caching
- Orphan nodes created via `instantiate()` without `add_child()` or `free()`

---

## GDScript Patterns for Game Logic

```gdscript
# State machine — enum-based (simple, no library needed)
enum State { IDLE, RUNNING, JUMPING, ATTACKING, DEAD }
var state: State = State.IDLE

func _physics_process(delta: float) -> void:
    match state:
        State.IDLE:    _process_idle(delta)
        State.RUNNING: _process_running(delta)
        State.JUMPING: _process_jumping(delta)
        State.DEAD:    pass  # no processing when dead

# Coroutine for timed sequences
func play_death_sequence() -> void:
    state = State.DEAD
    animation_player.play("die")
    await animation_player.animation_finished
    await get_tree().create_timer(1.5).timeout
    queue_free()
```

---

## GWT Acceptance Scenarios

```
Given: a signal is emitted from a physics callback (_physics_process or body_entered)
When: a connected node receives it and modifies the scene tree
Then: the connection uses CONNECT_DEFERRED
      AND no re-entrant physics crash occurs

Given: a node reference is declared with @onready
When: the scene is instantiated and _ready() is called
Then: the reference is valid and non-null
      AND no null reference error occurs during first frame

Given: a bullet is returned to the object pool
When: pool.release(bullet) is called
Then: bullet.visible is false
      AND bullet.set_physics_process(false) is called
      AND the bullet remains in the scene tree (not freed)
      AND it is available for pool.get() on next request

Given: an EventBus signal is emitted
When: a receiver node has been freed from the scene tree
Then: no error occurs (Godot 4 auto-disconnects freed nodes from signals)
      AND the emission does not crash the emitter
```
