# Game Engineering — Performance Budgets

## Frame Time Budget

| Target | Frame budget | GPU budget | CPU budget |
|---|---|---|---|
| 60fps | 16.6ms | ~6ms | ~10ms |
| 30fps | 33.3ms | ~13ms | ~20ms |
| 90fps (VR) | 11.1ms | ~4ms | ~7ms |

**CPU breakdown (60fps example):**
```
Physics:     ≤ 3ms
Game logic:  ≤ 3ms
AI:          ≤ 2ms
Render prep: ≤ 2ms
```

**Measurement:** Unity Profiler, Unreal Insights, Godot Profiler. Test on minimum spec hardware — not development machine.

**Hitching:** p99 frame time ≤ 2× frame budget. No single frame > 50ms (visible stutter).

---

## Memory Budgets

| Platform | Total RAM | Game budget | OS reserve |
|---|---|---|---|
| PC (min spec) | 8 GB | 4 GB | 4 GB |
| PC (recommended) | 16 GB | 8 GB | 8 GB |
| iOS (min) | 3 GB | 1.5 GB | OS uses rest |
| Android (min) | 4 GB | 2 GB | OS uses rest |
| PS5 | 16 GB unified | 13.5 GB | 2.5 GB OS |

**Textures:** Largest single contributor. Declare per-scene texture memory budget.
**Audio:** Decompressed audio buffers. Declare max simultaneous voices × buffer size.
**Objects:** Object pools pre-allocated at scene load. No growth during play.

---

## Load Time Budgets

| Event | Budget |
|---|---|
| Cold start to main menu | < 15s |
| Level load (first play) | < 30s |
| Level load (subsequent) | < 15s |
| Respawn (in-level) | < 3s |

**Streaming:** Content that exceeds load budget must be streamed during gameplay. Declare streaming strategy.

---

## Build Size Budgets

| Platform | Download size | Installed size |
|---|---|---|
| PC | < ___ GB | < ___ GB |
| iOS | < 2 GB initial (App Store limit for cellular) | < ___ GB |
| Android | < 1 GB APK; expansions via Play Asset Delivery | < ___ GB |
| Console | < ___ GB (declare; each platform has limits) | < ___ GB |

**Compression:** Use build-time asset compression. Audio: Ogg/Opus. Textures: platform BC/ASTC. Meshes: Draco.

---

## Network Budgets (Multiplayer)

| Metric | Budget |
|---|---|
| Server tick rate | ___ Hz |
| Client → Server bandwidth | < ___ KB/s per player |
| Server → Client bandwidth | < ___ KB/s per player |
| Max players per server | ___ |
| Acceptable latency (playable) | < 150ms RTT |
| Lag compensation window | ___ ms |
