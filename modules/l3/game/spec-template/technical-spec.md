# Game Technical Spec Template (P3)

> **Platform:** Game | **Prerequisite:** systems-design.md complete.

---

## Core System Implementation Specs

### Physics System

**Fixed timestep loop:**
```csharp
const float FIXED_STEP = 1f / 60f;
float accumulator = 0f;

void Update(float deltaTime) {
    accumulator += deltaTime;
    while (accumulator >= FIXED_STEP) {
        PhysicsUpdate(FIXED_STEP);
        accumulator -= FIXED_STEP;
    }
    float alpha = accumulator / FIXED_STEP;
    Render(Lerp(previousState, currentState, alpha));
}
```

**GWT scenarios:**
```
Given: physics step at 60Hz, render at 144Hz
When: rendering a frame between physics steps
Then: entity positions are interpolated between steps
      AND no physics jitter is visible at high frame rates

Given: frame spike causes 3 physics steps in one render frame
When: accumulator exceeds 3 × FIXED_STEP
Then: physics is capped at MAX_STEPS per frame (e.g., 3)
      AND simulation slows rather than spiral-of-death hang
```

---

### Input System

**Input buffer:** Inputs buffered for ___ frames (prevents missed inputs at low frame rate).

**Input priority:** UI > Player > Camera > World (when multiple systems consume same input).

**Platform input mapping:**

| Action | PC | Controller | Mobile |
|---|---|---|---|
| Jump | Space | A/Cross | Tap |
| Attack | Left Click | X/Square | Swipe |

---

### Save System

**Serialization:** Custom binary or `MessagePack` / `protobuf` — not JSON for production (too slow, too large).

**Checksum:** CRC32 on serialized bytes. Written as header.

**Version field:** Save version in header. On load: if save version < current: run migration function chain.

**Migration chain:**
```
save_v1 → migrate_v1_to_v2() → save_v2 → migrate_v2_to_v3() → current
```

---

### Object Pool Implementation

```csharp
public class ObjectPool<T> where T : MonoBehaviour {
    private Queue<T> pool = new Queue<T>();
    private int maxSize;

    public T Get() {
        if (pool.Count > 0) return pool.Dequeue();
        if (ActiveCount < maxSize) return CreateNew();
        return null;  // pool exhausted — caller handles gracefully
    }

    public void Return(T obj) {
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

**Never destroy/instantiate in hot path.** All gameplay objects use pools.

---

## Anti-Cheat Implementation

**Server-side validation (required for multiplayer):**

```
For each client input received:
  1. Validate input is physically possible (speed ≤ max_speed + tolerance)
  2. Validate input timestamp is within acceptable window (reject stale inputs)
  3. Validate action is possible in current state (can't shoot with no ammo)
  4. If invalid: discard input, apply correction, log with client ID
```

**Client-side (defense in depth, not primary):**
- Integrity check of game binary on launch
- Detect memory editor signatures (Cheat Engine patterns)
- Report anomalies to server — server makes enforcement decisions

---

## Performance Profiling Gates

Before each milestone build:
- [ ] Frame time: median < 13ms, p99 < 16.6ms on minimum spec hardware
- [ ] Memory: RSS < declared budget, no unbounded growth over 30-minute session
- [ ] Load time: scene loads within declared budget
- [ ] No heap allocation in Update() hot path (profiler confirms)
- [ ] Audio: no crackling or dropout under load
- [ ] Save/load: completes within 2 seconds, passes checksum validation
