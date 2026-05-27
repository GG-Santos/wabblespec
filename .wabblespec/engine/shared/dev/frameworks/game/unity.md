# Unity Engine

Loaded by Apply when Assets/ directory + .unity scenes are detected.

## Version baseline

Unity 2022 LTS or 6.x LTS. Declare exact version in spec — Unity versions are not backward compatible.

## Project architecture decisions spec must declare

- **Rendering pipeline**: Built-in, URP (Universal), or HDRP (High Definition)
- **Scripting backend**: IL2CPP (required for iOS; recommended for performance) or Mono
- **Code stripping**: declare strip level; test thoroughly — stripping removes code reflection depends on
- **Assembly definitions**: required for any project over 20 scripts (build time and compilation isolation)

## MonoBehaviour lifecycle (know what runs when)

```csharp
Awake()          // component initialized; object may be inactive
OnEnable()       // component becomes active
Start()          // first frame; all Awakes have run
FixedUpdate()    // physics timestep (default 50Hz / 0.02s)
Update()         // every render frame
LateUpdate()     // after all Updates (camera follow goes here)
OnDisable()      // component deactivated
OnDestroy()      // object destroyed
```

Do not do heavy work in Update() — use coroutines, Jobs, or event-driven patterns.

## Performance — Unity specific

- **Object pooling**: never Instantiate/Destroy frequently — pool and reuse GameObjects
- **GetComponent()**: cache in Awake(); do not call in Update()
- **FindObjectOfType()**: never in Update(); cache or use events
- **Physics**: set layer collision matrix; disable unnecessary collision pairs
- **Batching**: static batching for immobile objects; GPU instancing for repeated meshes; SRP batcher for materials

### C# Job System + Burst

For CPU-intensive code (pathfinding, simulation, particle systems):

```csharp
[BurstCompile]
struct ProcessDataJob : IJobParallelFor {
    [ReadOnly] public NativeArray<float3> input;
    public NativeArray<float3> output;
    
    public void Execute(int index) {
        output[index] = math.normalize(input[index]);
    }
}
```

Burst-compiled jobs run on worker threads with SIMD vectorization. Spec must declare which systems are job-ified.

## Memory management

Unity is managed code but GC still causes hitches. Rules:
- Avoid allocations in hot paths (Update, FixedUpdate, frequently-called methods)
- Use `NativeArray` / `NativeList` instead of managed arrays for job-heavy code
- Profile with Unity Memory Profiler before shipping; declare memory budget in spec

## Build pipeline

Spec must declare:
- Development vs Release build differences (debug symbols, logging, cheats)
- Addressables vs Resources for asset loading (Addressables for large projects — async, patchable)
- Build automation: Unity Cloud Build, GitHub Actions with GameCI, or local

## Testing — Unity Test Framework

```csharp
[Test]
public void Damage_ReducesHealth() {
    var health = new HealthComponent(100);
    health.TakeDamage(30);
    Assert.AreEqual(70, health.Current);
}

[UnityTest]
public IEnumerator SpawnedEnemy_MovesToPlayer() {
    var enemy = GameObject.Instantiate(enemyPrefab);
    yield return new WaitForSeconds(1f);
    Assert.Less(Vector3.Distance(enemy.transform.position, player.position), 1f);
}
```

- Edit Mode tests: pure C# tests; no Unity frame loop
- Play Mode tests: run in the game loop; use `[UnityTest]` with `yield`
