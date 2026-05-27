# Performance Budgets — Game

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/game`.
> Reference: `.wabblespec/engine/shared/references/performance-budgets.md`.

---

## Frame rate

### Target frame rate

**Target:** ___ fps (declare one: 30 / 60 / 90 / 120 fps)
**Rationale:** Frame rate target drives all downstream budgets (CPU, GPU, memory bandwidth); undeclared target makes all other measurements meaningless
**Measurement:** GPU profiler (RenderDoc / Xcode GPU Frame Capture / PIX); measure on minimum-spec target hardware
**PII impact:** none

### Frame time budget (derived from target)

| Target fps | Frame budget |
|---|---|
| 30 fps | 33.3ms |
| 60 fps | 16.6ms |
| 90 fps | 11.1ms |
| 120 fps | 8.3ms |

**Target:** ≤ ___ ms per frame (fill in from table above)
**Measurement:** GPU profiler frame time; fail if p99 frame time exceeds budget
**PII impact:** none

### Frame drop threshold

**Target:** < 1% of frames exceed 2× the declared frame budget (i.e., < 1% frames dropped)
**Rationale:** Intermittent drops are more disorienting than a stable lower frame rate; 2× budget drops cause visible stutter
**Measurement:** frame time histogram over 5-minute gameplay session on minimum-spec hardware
**PII impact:** none

---

## CPU

### Game loop CPU budget

**Target:** ≤ 60% of frame budget allocated to game logic (AI, physics, input); remaining 40% for render and overhead
**Rationale:** Over-allocating game logic leaves insufficient headroom for render commands and driver overhead
**Measurement:** CPU profiler with frame markers; alert when game logic thread exceeds 60% of frame budget in p95
**PII impact:** none

### Physics tick (fixed timestep)

**Target:** Fixed timestep declared and enforced; physics tick ≤ ___ ms (typically 16.6ms at 60Hz or 33.3ms at 30Hz)
**Rationale:** Variable-timestep physics produces non-deterministic behavior and replay desync; fixed timestep is required (enforced in `l3/game` acceptance tests AT-GAME-03)
**Measurement:** assert in physics update that delta time == declared fixed step; CI test with simulated variable frame rate
**PII impact:** none

---

## GPU

### GPU frame time

**Target:** ≤ 70% of total frame budget allocated to GPU work (geometry + shading + post-processing)
**Rationale:** Leaving 30% headroom absorbs scene complexity spikes without dropping frames
**Measurement:** GPU profiler timeline per frame; measure on minimum-spec GPU
**PII impact:** none

### Draw call ceiling

**Target:** ≤ ___ draw calls per frame on minimum-spec hardware (declare based on target platform)
**Rationale:** Excessive draw calls are the most common GPU bottleneck on mobile and low-end PC; declare ceiling in spec to catch regressions
**Measurement:** RenderDoc / Xcode GPU Frame Capture draw call count in representative scene
**PII impact:** none

---

## Memory

### VRAM budget

**Target:** ≤ ___ MB VRAM (declare based on minimum GPU VRAM on target platform × 0.75)
**Rationale:** VRAM overflow causes assets to swap to system RAM, causing massive frame time spikes
**Measurement:** GPU profiler VRAM usage in most asset-heavy scene; monitor per build
**PII impact:** none

### System RAM

**Target:** ≤ ___ MB system RAM (declare based on minimum-spec platform RAM × 0.5)
**Rationale:** Games consuming > 50% of system RAM cause OS to background swap, destroying frame time
**Measurement:** process RSS at peak scene load; measure on minimum-spec machine
**PII impact:** none

---

## Load times

### Initial load (game launch to main menu)

**Target:** ≤ ___ s with progress indicator displayed within 500ms of launch
**Rationale:** Load times above 30s cause abandonment; first-frame latency with no indicator causes perceived freezes
**Measurement:** timer from launch to interactive main menu; CI integration test
**PII impact:** none

### Level / scene load

**Target:** ≤ ___ s for scene transitions; async load with loading screen if > 500ms
**Rationale:** Synchronous loads that stall the main thread create frozen frames; async loading with a screen is mandatory above 500ms
**Measurement:** load time profiler; CI integration test with representative scene
**PII impact:** none

---

## Multiplayer (if applicable)

### Network tick rate

**Target:** ___ Hz server tick rate declared (typically 20–128 Hz depending on game type)
**Rationale:** Tick rate determines input latency and movement smoothness; undeclared tick rate makes latency guarantees impossible
**Measurement:** server-side tick timing logged; alert on tick rate drift
**PII impact:** none

### Tolerable latency

**Target:** Playable at ≤ ___ ms round-trip latency (declare based on game genre: FPS ≤ 80ms, strategy ≤ 300ms)
**Rationale:** Latency tolerance is genre-dependent; declare to drive network code compensation design (lag compensation, rollback netcode)
**Measurement:** simulated latency injection tests using netem or equivalent
**PII impact:** none

---

## PII fields (excluded from log schema)

<!-- Game analytics may constitute PII (play patterns, purchase history, social graph) -->
<!-- Example:
- player_id (if linkable to identity)
- purchase_history
- voice_chat_data
- friend_list
-->
___ UNDECLARED — populate before enabling analytics or telemetry
