# Engine-Specific Architecture: Unreal Engine 5

> **Applies when:** `Source/` directory + `.uproject` file detected.
> **Replaces:** The generic ECS section in systems-design.md. Unreal uses the Actor/Component model, not ECS. DOTS-style ECS is Unity-specific.
> **Engine authority:** Unreal Engine 5.x. Patterns match UE5 API. If using UE4, subsystem names and some plugin APIs differ — declare version in technical-spec.md.

---

## Actor / Component Model

Unreal's primary architecture unit is the **Actor** — an object that can exist in the world. Actors own **Components** that provide behavior. This is not ECS: Components here contain both data and logic (unlike pure ECS components).

```
AGameMode (world rules, server-only)
AGameState (replicated world state)
  └── APlayerState (per-player replicated state)
      └── APawn / ACharacter (player-controlled actor)
            ├── UCapsuleComponent (collision, root)
            ├── USkeletalMeshComponent (visual)
            ├── UCameraComponent (view)
            ├── UCharacterMovementComponent (physics movement)
            └── UAbilitySystemComponent (if using GAS)
```

**Actor placement rules:**
- Actors exist in the world. Pure data objects use `UObject` subclasses, not Actors.
- Components are attached to Actors — they do not exist independently.
- `ACharacter` = `APawn` + `UCapsuleComponent` + `USkeletalMeshComponent` + `UCharacterMovementComponent`. Use it for all humanoid characters.
- `APawn` = base player-controlled or AI-controlled actor. Use it for vehicles, non-humanoid agents.

---

## Blueprint vs. C++ Boundary

**Rule:** Logic in C++. Data exposure in Blueprint. Interface via `BlueprintImplementableEvent` and `BlueprintNativeEvent`.

| What goes in C++ | What goes in Blueprint |
|---|---|
| Gameplay logic, math, state machines | Designer-tweakable values (`UPROPERTY(EditAnywhere)`) |
| Performance-critical systems | Visual scripting for one-off level events |
| Replication logic | Animation state machine (AnimBP) |
| GAS Abilities, Effects, Attributes | UI widget layout (UMG) |
| All network RPCs | VFX trigger hooks |

```cpp
// C++ declares the interface
UFUNCTION(BlueprintImplementableEvent, Category="Combat")
void OnDamageTaken(float DamageAmount, AActor* DamageSource);

// Blueprint implements the visual response (flash, sound, camera shake)
// C++ calls it after applying damage math

UFUNCTION(BlueprintNativeEvent, Category="Interaction")
bool CanInteract(APawn* InstigatingPawn);
// C++ provides default implementation; Blueprint can override
```

**Blueprint optimization:** Avoid Blueprint-only hot-path logic (called every tick). Blueprint has ~10× overhead vs C++ in tight loops. If a Blueprint node runs > 100× per frame, move it to C++.

---

## UPROPERTY — Memory Safety

All `UObject`-derived pointers **must** be declared with `UPROPERTY()`. Without it, the garbage collector cannot see the reference and will collect the object even while you hold a pointer.

```cpp
// Correct — GC can track this
UPROPERTY()
TObjectPtr<UStaticMeshComponent> MeshComponent;

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
float MaxHealth = 100.f;

UPROPERTY(Transient)  // runtime-only, not serialized
TObjectPtr<AActor> CurrentTarget;

// Incorrect — GC-invisible, dangling pointer risk
UStaticMeshComponent* MeshComponent;  // ← missing UPROPERTY
```

**TObjectPtr vs raw pointer:** Prefer `TObjectPtr<T>` over `T*` for all UPROPERTY-marked object references in UE5. It adds access tracking in editor builds and null safety.

**Weak references:**
```cpp
TWeakObjectPtr<AActor> WeakTarget;  // does not prevent GC
if (WeakTarget.IsValid()) { WeakTarget->DoSomething(); }
```

---

## Gameplay Ability System (GAS)

Use GAS when the project has: abilities with costs/cooldowns, gameplay effects that modify attributes, ability targeting, or network replication of abilities.

**Do not use GAS for:** simple singleplayer games without ability systems — setup cost is high for minimal gain.

**Core GAS components:**

| Component | Purpose |
|---|---|
| `UAbilitySystemComponent` (ASC) | Attached to Actor. Manages all abilities and effects for that actor. |
| `UAttributeSet` | Data container for numeric attributes (Health, Mana, Speed). Subclass per actor type. |
| `UGameplayAbility` | One discrete ability (attack, dash, heal). Contains cost, cooldown, execution logic. |
| `UGameplayEffect` | Stateless modifier applied to AttributeSets (damage, buff, debuff). Instant or duration. |
| `FGameplayTag` | Hierarchical tag used for ability activation conditions, blocking, and cancellation. |

```cpp
// Attribute declaration
UPROPERTY(BlueprintReadOnly, Category="Attributes", ReplicatedUsing=OnRep_Health)
FGameplayAttributeData Health;
ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)  // generates getter/setter/initter

// Ability activation
AbilitySystemComponent->TryActivateAbilitiesByTag(
    FGameplayTagContainer(TAG_Ability_Attack)
);
```

**GAS replication:** ASC must be on a replicated Actor. The owner of the ASC handles prediction. Client predicts ability activation; server confirms. Use `FGameplayAbilitySpec::InputPressed` for input binding, not direct key checks.

---

## Subsystems — Cross-Cutting Services

UE5 Subsystems replace singletons. They are automatically created, garbage-collected, and scoped to their lifetime class.

| Subsystem type | Lifetime | Use for |
|---|---|---|
| `UGameInstanceSubsystem` | Application lifetime | Cross-level state (inventory, progression, settings) |
| `UWorldSubsystem` | Per-world (level) | Level-specific services (AI director, event manager) |
| `ULocalPlayerSubsystem` | Per local player | Input handling, UI state |
| `UEngineSubsystem` | Engine lifetime | Developer tools only |

```cpp
// Access pattern — no singleton needed
UInventorySubsystem* Inventory = GetGameInstance()->GetSubsystem<UInventorySubsystem>();
Inventory->AddItem(ItemId, Quantity);
```

---

## Replication — Authoritative Server

**Rule:** Server owns all game state. Client predicts for responsiveness, reconciles with server.

```cpp
// Property replication
UPROPERTY(ReplicatedUsing=OnRep_Health)
float Health;

void AMyCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutProps) const
{
    Super::GetLifetimeReplicatedProps(OutProps);
    DOREPLIFETIME(AMyCharacter, Health);
    DOREPLIFETIME_CONDITION(AMyCharacter, CurrentTarget, COND_OwnerOnly);
}

// RPC declarations
UFUNCTION(Server, Reliable)
void ServerRequestAttack(FVector TargetLocation);  // client → server

UFUNCTION(NetMulticast, Unreliable)
void MulticastPlayHitEffect(FVector ImpactPoint);  // server → all clients
```

**Replication relevancy:** Actors outside a client's relevancy radius stop replicating to that client. Configure `NetCullDistanceSquared` per actor class. High-frequency actors (projectiles) need large relevancy or custom relevancy logic.

**Bandwidth budget:** Declare in `performance-budgets.md`. Every new replicated property increases server → client bandwidth. Audit replication cost with `net.Stats` console command.

---

## Unreal Build System

**Module declaration** (`MyGame.Build.cs`):
```csharp
public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "InputCore",
            "GameplayAbilities", "GameplayTags", "GameplayTasks"  // GAS
        });
    }
}
```

**Naming conventions (Unreal mandatory):**
- `A` prefix: Actor subclasses (`AMyCharacter`, `AMyGameMode`)
- `U` prefix: UObject subclasses, Components (`UMyComponent`, `UMyAttributeSet`)
- `F` prefix: Structs (`FMyStruct`, `FGameplayAttribute`)
- `E` prefix: Enums (`EMyState`)
- `I` prefix: Interface classes (`IInteractable`)
- `T` prefix: Templates (`TArray`, `TMap`, `TObjectPtr`)

---

## GWT Acceptance Scenarios

```
Given: a UObject-derived pointer is used across frames
When: the GC runs between frames
Then: all UObject pointers marked UPROPERTY() remain valid
      AND any unmarked pointer is caught by engine access tracking in Editor builds

Given: a Blueprint script runs logic on every tick
When: the logic runs more than 100 times per frame
Then: the logic is moved to C++ with a BlueprintCallable wrapper
      AND the Blueprint calls the C++ function

Given: a server RPC is received by the server
When: the server validates the requested action
Then: the action is only applied if it passes server-side validation
      AND the client is corrected via RepNotify if state diverges

Given: a Gameplay Effect is applied to a character
When: the character's Health attribute changes
Then: all registered Attribute Change Delegates fire
      AND the OnRep_Health function is called on all clients
      AND the UI reflects the new value within one frame of replication
```
