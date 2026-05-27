# Mobile Engineering — Performance Budgets

## App Launch Time

| Metric | Budget | Notes |
|---|---|---|
| Cold start to interactive (iOS) | < 3s | Measured from tap to first interactive frame |
| Cold start to interactive (Android) | < 3s | Measured on mid-range device (not flagship) |
| Warm start | < 1s | App already in memory |
| Splash to first screen | < 500ms | App icon tap to any app UI visible |

**Measurement:** Xcode Instruments (iOS), Android Studio Profiler (Android), or Detox / Maestro test timing.

**Test device:** Always measure on a mid-range target device, not a development machine or flagship phone.

---

## UI Rendering

| Metric | Budget |
|---|---|
| Frame rate (animations, scrolling) | 60fps sustained (90/120fps if device supports) |
| Dropped frames in list scroll | < 1% |
| Screen transition animation | < 300ms |
| Keyboard appearance | < 100ms before text field responds |

**React Native:** All animations must use `useNativeDriver: true` where supported. Never animate with `setState` for performance-critical transitions.

**Flutter:** Avoid `setState` on high-frequency events. Use `AnimationController` + `Tween` with vsync.

---

## Network Performance

| Metric | Budget |
|---|---|
| API response (p50) | < 500ms |
| API response (p95) | < 2s |
| Image load (cached) | < 100ms |
| Image load (network, < 500KB) | < 1s on 4G |
| App usable while loading | Always — skeleton UI, not blocking spinner |

**Cellular optimization:**
- Compress images aggressively (WebP preferred)
- Batch API requests where possible
- Cache aggressively with declared TTL
- Do not make network requests on every keystroke

---

## Memory Usage

| Metric | Budget | Notes |
|---|---|---|
| Baseline memory (home screen) | < 150 MB | |
| Active use memory | < 300 MB | |
| After 30-minute session | < 400 MB | Detect leaks |
| Image cache size | < 100 MB | LRU eviction |

**Memory pressure:** Handle `UIApplicationDidReceiveMemoryWarningNotification` (iOS) / `onTrimMemory` (Android). Clear image caches on memory warning.

---

## Battery Impact

| State | CPU budget |
|---|---|
| Foreground idle (no user activity) | < 2% CPU |
| Background (if any background mode declared) | < 0.5% CPU |
| Location updates (if declared) | Use significant-change API unless real-time required |

**No continuous polling.** Background tasks use OS scheduling (`BGAppRefreshTask`, WorkManager) — not `setInterval`.

---

## App Size

| Metric | Budget |
|---|---|
| iOS IPA download size | < 50 MB (above 200 MB requires WiFi install) |
| Android APK download (split) | < 30 MB per ABI |
| Android AAB total | < 150 MB |
| On-device installed size | < 200 MB |

**React Native size reduction:**
- Enable Hermes JS engine
- Enable ProGuard/R8 for Android
- Use dynamic imports for large optional features
- Compress and lazy-load assets

**Flutter size reduction:**
- `flutter build ipa --split-debug-info`
- `flutter build appbundle --obfuscate --split-debug-info`
- Use deferred loading for large features (`deferred as`)
