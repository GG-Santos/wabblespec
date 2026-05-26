# Godot Engine

Loaded by Apply when project.godot is detected.

## Version baseline

Godot 4.x (GDScript 2.0). Declare exact minor version — APIs changed significantly between 4.0 and 4.2+.

## Language choice

| Language | When |
|---|---|
| GDScript | Default; rapid iteration; tight engine integration |
| C# (.NET) | Team has C# background; performance-sensitive non-critical paths |
| C++ (GDExtension) | Performance-critical systems; third-party library integration |

Spec must declare language choice per module/system.

## Node architecture

Godot uses a tree of Nodes. Every scene is a tree; scenes can instance other scenes.

```
Main (Node)
├── World (Node3D)
│   ├── Player (CharacterBody3D)
│   │   ├── Camera3D
│   │   └── CollisionShape3D
│   └── Enemies (Node)
│       └── Enemy (CharacterBody3D)  ← instanced scene
└── UI (CanvasLayer)
    └── HUD (Control)
```

Rules:
- Scenes are the unit of composition — one scene per reusable entity
- Nodes own their children — parent freed = children freed
- Use signals for child-to-parent communication (not `get_parent()`)
- Use `@export` for configuration; do not hardcode values in scripts

## Signals (event system)

```gdscript
# Define
signal health_changed(old_value: int, new_value: int)

# Emit
health_changed.emit(old_hp, current_hp)

# Connect
player.health_changed.connect(_on_player_health_changed)

func _on_player_health_changed(old: int, new: int) -> void:
    hud.update_health(new)
```

Prefer signals over direct node references for loose coupling. Spec must declare signal connections for cross-node communication.

## Physics and movement

```gdscript
extends CharacterBody3D

const SPEED = 5.0
const JUMP_VELOCITY = 4.5

func _physics_process(delta: float) -> void:
    # Add gravity
    if not is_on_floor():
        velocity += get_gravity() * delta
    
    # Handle jump
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP_VELOCITY
    
    # Move and slide
    move_and_slide()
```

`_physics_process` runs at the physics tick rate (default 60Hz). Keep it lean.

## Performance — Godot specific

- `_process` vs `_physics_process`: use `_physics_process` for physics/movement; `_process` for visual updates
- Avoid `get_node()` in `_process` — cache node references in `_ready()`
- Large scenes: use `Node.process_mode = PROCESS_MODE_DISABLED` for inactive nodes; do not delete/recreate
- LOD: `GeometryInstance3D.lod_bias` for 3D; manual 2D LOD via visibility detection
- Culling: Godot does frustum culling automatically; use occlusion culling for complex scenes

## Resource system

```gdscript
# Preload (compile-time path validation)
const BULLET_SCENE = preload("res://scenes/bullet.tscn")

# Load (runtime, async possible)
var texture = load("res://assets/player.png")

# ResourceLoader (async)
ResourceLoader.load_threaded_request("res://big_scene.tscn")
```

Spec must declare: which resources are preloaded vs loaded on demand; memory budget for loaded resources.

## Testing — GUT (Godot Unit Test)

```gdscript
extends GutTest

func test_player_takes_damage() -> void:
    var player = PlayerScene.instantiate()
    add_child(player)
    player.take_damage(30)
    assert_eq(player.health, 70)
    player.queue_free()
```

GUT runs inside the Godot editor. Write tests for: game logic, state machines, signal emissions, scene instantiation contracts.
