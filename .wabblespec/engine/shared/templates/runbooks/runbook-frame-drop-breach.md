# Runbook: Frame Drop Breach

**Alert:** `FrameDropBreach`  
**Severity:** warning (> ___ % drop rate) | critical (sustained frame drops, unplayable)  
**SLO:** Frame drop rate < ___ % at declared target fps — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
**Applies to:** Game platform  

---

## Symptoms

- Frame time regression test failing in CI (build-time signal)
- Live telemetry showing `frame_drop_rate` above declared threshold
- Player-reported stutter, hitching, or "lag" in specific scenes or actions
- Frame time histogram showing spikes above frame budget (`___ ms` at target `___ fps`)
- GPU or CPU frame time profiler showing hot frame outliers

---

## Immediate triage

1. Distinguish: is this a CI regression (build-time — specific commit introduced it) or a live production report (runtime — specific player hardware/scene)?
2. **CI regression:** Which commit introduced the regression? Run frame-time test on the last known-good commit.
3. **Live production:** Is the drop rate elevated across all hardware tiers or only a specific GPU/CPU tier?
4. Is it a specific scene, level, or game action triggering the drop, or systemic across all gameplay?
5. Is it CPU-bound or GPU-bound? Check CPU vs. GPU frame time split in telemetry.

---

## Diagnosis

**CI frame-time regression:** `___ UNDECLARED` (insert frame-time test invocation and output location)

**Live telemetry — frame time distribution:**
```
___ UNDECLARED  # insert telemetry query for p95/p99 frame time by hardware tier
```

**Profiler invocation (CPU):** `___ UNDECLARED` (insert CPU profiler command for the affected scene)

**Profiler invocation (GPU):** `___ UNDECLARED` (insert GPU profiler command — RenderDoc, Nsight, Instruments, etc.)

**Common causes (CPU-bound):**
- New game logic added with O(n²) or worse complexity in update loop
- Garbage collection pause in managed runtime (Unity/Unreal GC, Mono, .NET)
- Physics simulation overbudget (too many bodies, complex collision geometry)
- AI pathfinding not budgeted (running every frame instead of time-sliced)
- Asset streaming stall on main thread (synchronous file I/O in update loop)

**Common causes (GPU-bound):**
- New visual effect overdrawing budget (particle system, post-processing pass)
- Draw call count increase exceeding GPU driver batch limit
- Texture memory thrashing causing GPU cache misses
- Shadow map resolution or distance increased in new build
- Shader complexity increase (no LOD reduction at distance)

**Common causes (both):**
- Physics determinism test failing — simulation is diverging, causing extra reconciliation work
- Audio buffer underrun causing main thread stall

---

## Remediation

### CI regression (known commit)
1. Revert the offending commit if the feature is not critical path.
2. If the feature must ship: profile and optimize before re-merging; add frame-time budget enforcement to the feature's code path.

### CPU-bound (live)
1. Identify the hot function from CPU profiler: `___ UNDECLARED`.
2. Common fixes: convert O(n²) loops to spatial hash lookups; budget AI pathfinding to ___ ms/frame using a job queue; move asset streaming to async thread; add GC.Collect() scheduling to off-peak frames.
3. Frame budget enforcement: set per-system CPU time limits in `___ UNDECLARED` (game loop scheduler).

### GPU-bound (live)
1. Reduce draw calls via batching/instancing in `___ UNDECLARED`.
2. Add LOD (Level of Detail) transitions for new effect at `___ UNDECLARED` distance threshold.
3. Cap particle system max count in `___ UNDECLARED` to `___ UNDECLARED`.
4. Reduce shadow map distance/resolution in low-end hardware tier config at `___ UNDECLARED`.

---

## Escalation

- Frame drop rate > ___ % sustained in production: page ___ UNDECLARED (game director + engineering lead)
- Frame drop rendering game unplayable on a supported hardware tier: emergency hotfix process at `___ UNDECLARED`
- Physics determinism test also failing: page ___ UNDECLARED (multiplayer sync is compromised)

---

## Post-incident

- [ ] Root cause documented (CPU system / GPU effect / GC / physics)
- [ ] Frame-time regression test updated with the new scenario as a fixture
- [ ] Per-system CPU/GPU budget limits reviewed and tightened if needed
- [ ] CI gate threshold confirmed still meaningful (not too loose)
- [ ] Hardware tier matrix updated if new min-spec findings emerged
- [ ] Runbook updated with game-specific profiler paths

---

*Generated from `.wabblespec/engine/shared/templates/runbooks/runbook-frame-drop-breach.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
