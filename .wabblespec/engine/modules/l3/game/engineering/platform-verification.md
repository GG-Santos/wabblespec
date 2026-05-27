# Game Engineering — Platform Verification

## Frame Rate Verification

```bash
# Unity: use Performance Testing Package
# Run benchmark scene and log frame times:
using UnityEngine.TestTools.Profiling;

[Performance]
public IEnumerator BenchmarkMainScene() {
    using (Measure.Frames().WarmupCount(10).MeasurementCount(100).Run()) {
        yield return null;
    }
}
# Assert median frame time < 16.6ms
```

**Manual check:** Unity Profiler → Deep Profile → check worst frame in representative gameplay.

---

## Memory Leak Detection

```
1. Start profiler
2. Play for 30 minutes (all major areas, spawn/despawn heavily)
3. Force GC collection
4. Compare memory before vs after
5. Growth > 50MB → investigate object pool leak or event listener leak
```

**Common Unity leaks:** Event listeners not unsubscribed, static references to scene objects, Addressables not released.

---

## Save System Verification

```bash
# Automated:
1. Save game at known state
2. Corrupt save file bytes (simulate disk error)
3. Load game
4. Expected: backup loaded, player notified
5. Check: no crash, no data from corrupted file used

# Cross-version:
1. Save with v1 of game
2. Load with v2 (after schema change)
3. Expected: migration runs, game loads correctly
```

---

## Anti-Cheat Verification (Multiplayer)

```
Speed hack test:
  Client sends position update implying 5× max speed
  Server: rejects input, corrects client position, logs attempt

Teleport test:
  Client sends position 500 units away from last known position
  Server: rejects, snaps client back

Duplicate input test:
  Same input timestamp sent twice
  Server: second is ignored (idempotent input processing)
```

---

## Console Certification Pre-Check

Before submitting to Sony/Microsoft/Nintendo:
- [ ] All required features implemented (trophy/achievement system, accessibility options)
- [ ] No prohibited content (platform-specific content guidelines)
- [ ] Age ratings submitted and approved
- [ ] Network features comply with platform online requirements
- [ ] Save data uses platform save API correctly
- [ ] Suspend/resume handling correct (console sleep mode)
- [ ] Crash testing: 24-hour soak test, no hangs
- [ ] Controller input only (no keyboard/mouse assumption on console)
