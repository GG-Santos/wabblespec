# Build Toolchain — Game

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Engine and language

**Engine:** [ ] Unity  [ ] Godot  [ ] Unreal Engine  [ ] Custom  [ ] Other: ___
**Primary language:** [ ] C# (Unity)  [ ] GDScript/C++ (Godot)  [ ] C++/Blueprints (Unreal)  [ ] Other: ___
**Engine version:** `___ UNDECLARED` _(pin exact version — engine upgrades are breaking changes)_
**Target platforms:** [ ] PC (Windows/macOS/Linux)  [ ] Console (PS5/Xbox/Switch)  [ ] Mobile (iOS/Android)  [ ] Web (WebGL)

---

## Build

**Build tool:** [ ] Unity Build System  [ ] Godot export  [ ] Unreal Automation Tool (UAT)  [ ] Other: ___
**CI build machine:** [ ] self-hosted runner (GPU required)  [ ] cloud GPU (specify)  [ ] Other: ___
**Output format:** [ ] executable  [ ] store submission package  [ ] WebGL bundle  [ ] Other: ___

---

## Test runner

**Unit:** [ ] Unity Test Framework (EditMode)  [ ] GUT (Godot)  [ ] Catch2 (Unreal/custom)  [ ] Other: ___
**PlayMode / integration:** [ ] Unity Test Framework (PlayMode)  [ ] Godot scene runner  [ ] Other: ___
**Performance regression:** [ ] Unity Performance Testing  [ ] custom frame-time tracker  [ ] Other: ___

---

## CI system

**Platform:** [ ] GitHub Actions (self-hosted GPU runner)  [ ] GameCI  [ ] Unreal Build System cloud  [ ] Other: ___

**Required CI gates:**
- [ ] Compile (no errors)
- [ ] Unit tests (EditMode)
- [ ] PlayMode smoke tests
- [ ] Frame time regression test (p99 frame time vs declared budget)
- [ ] Build size check
- [ ] Asset import validation (no broken references)
- [ ] Physics determinism test (if multiplayer/replay)
- [ ] Platform-specific build (all target platforms)

---

## Platform certification

**Console certification:** [ ] TRC (PlayStation)  [ ] XR (Xbox)  [ ] Lot Check (Nintendo)  [ ] N/A
**Store submission:** [ ] Steam  [ ] Epic Games Store  [ ] App Store  [ ] Google Play  [ ] itch.io  [ ] Other: ___
**Age rating:** [ ] PEGI  [ ] ESRB  [ ] CERO  [ ] N/A (declare if not applicable)

---

## Multiplayer (if applicable)

**Netcode:** [ ] Unity Netcode for GameObjects  [ ] Mirror  [ ] Photon  [ ] Epic Online Services  [ ] Custom  [ ] N/A
**Server architecture:** [ ] dedicated servers  [ ] peer-to-peer  [ ] relay  [ ] N/A
**Matchmaking:** [ ] PlayFab  [ ] Nakama  [ ] Custom  [ ] N/A

---

## Observability

**Crash reporting:** [ ] Unity Cloud Diagnostics  [ ] Sentry  [ ] Bugsnag  [ ] Backtrace  [ ] Other: ___
**Analytics:** [ ] Unity Analytics  [ ] GameAnalytics  [ ] Custom  [ ] None
**Performance telemetry:** [ ] Unity Performance Reporting  [ ] Custom frame-time telemetry  [ ] None
**Server monitoring (if applicable):** [ ] Datadog  [ ] Grafana  [ ] Other: ___

_(Monitor generates frame-time, crash-rate, and server-side alerts if multiplayer infrastructure is declared.)_

---

## Notes

_Platform-specific SDK versions, certification contacts, live-ops infrastructure:_
