# Unreal Engine

Loaded by Apply when Source/ directory + .uproject file are detected.

## Version baseline

Unreal Engine 5.x. Declare exact version — UE5 features (Lumen, Nanite, PCG) are version-specific.

## Architecture decisions spec must declare

- **Gameplay framework**: Actor + Component model; GameMode, GameState, PlayerController, Pawn hierarchy
- **Blueprints vs C++**: C++ for performance-critical logic and base classes; Blueprints for iteration and designer-facing content
- **Build configuration**: Development (debugging), Shipping (optimized, no debug info)
- **Target platforms**: PC, console(s), mobile — each has different renderer settings

## Gameplay framework

```
GameMode        — rules of the game (server only)
GameState       — replicated state (all clients see it)
PlayerController — player's interface to the game (one per player, client + server)
Pawn            — the entity the player controls
PlayerState     — per-player persistent data (score, team)
```

Spec must declare how each piece of the gameplay framework is used.

## C++ and Blueprints

```cpp
// Actor declaration
UCLASS()
class MYGAME_API AMyActor : public AActor
{
    GENERATED_BODY()
    
public:
    // Exposed to Blueprints — designers can set this
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Actor")
    float Speed = 300.0f;

    // Callable from Blueprints
    UFUNCTION(BlueprintCallable, Category = "My Actor")
    void ApplyEffect(EEffectType Effect);
    
    // Override in Blueprints — C++ provides base behavior
    UFUNCTION(BlueprintNativeEvent, Category = "My Actor")
    void OnHit(AActor* HitActor);
};
```

Spec must declare: which classes are C++ base classes with Blueprint subclasses vs pure C++ vs pure Blueprint.

## Networking — Unreal replication

```cpp
// Property replication
UPROPERTY(Replicated)
int32 Health;

// RepNotify — called on clients when value changes
UPROPERTY(ReplicatedUsing = OnRep_Health)
int32 Health;

UFUNCTION()
void OnRep_Health();

// Server RPC — client calls this, runs on server
UFUNCTION(Server, Reliable)
void ServerRequestJump();

// NetMulticast — runs on all clients
UFUNCTION(NetMulticast, Unreliable)
void MulticastPlayEffect();
```

Spec must declare: which properties are replicated, which RPCs are used, and reliability settings.

## Performance — UE5 specific

- **Nanite**: virtualized geometry for high-poly static meshes; not for skeletal meshes or translucency
- **Lumen**: dynamic global illumination; high GPU cost on older hardware; declare if enabled
- **Profiling**: Unreal Insights for CPU/GPU; `stat unit` / `stat fps` for quick checks
- **GC**: Unreal's garbage collector runs periodically; `ForceGarbageCollect()` in loading screens
- **Tick**: disable `PrimaryActorTick.bCanEverTick` when not needed; expensive actors tick every frame

## Build and packaging

- **UnrealBuildTool (UBT)**: handles C++ compilation; `Build.cs` files declare modules and dependencies
- **Packaging**: File → Package Project; produces a cooked, optimized build
- **Console certification**: requires working with platform SDKs (GDK for Xbox, PlayStation SDK for PS5, Nintendo SDK for Switch)

## Testing

- **Automation Tests**: `IMPLEMENT_SIMPLE_AUTOMATION_TEST` — unit-style tests within the engine
- **Gauntlet**: integration/functional test framework; drives the game and checks behavior
- **Blueprint Testing**: limited; prefer C++ for testable logic
