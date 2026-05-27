# Performance Budgets — Mobile

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/mobile`.
> Reference: `.wabblespec/engine/shared/references/performance-budgets.md`.

---

## Startup

### App cold start (time to interactive)

**Target:** ≤ 2s from process launch to first interactive frame (iOS and Android)
**Rationale:** App Store / Play Store guidance; above 2s triggers user perception of slowness; above 5s risks abandonment
**Measurement:** `os_log` (iOS Instruments) or `systrace` (Android Studio Profiler) from process start to first layout pass
**PII impact:** none

### Warm start (resume from background)

**Target:** ≤ 500ms from app foreground to interactive
**Rationale:** Users switching back to an app expect near-instant resume; anything above 500ms breaks the context-switching mental model
**Measurement:** XCTest / Espresso timing test on device (not simulator)
**PII impact:** none

---

## Frame rate

### UI thread frame time

**Target:** ≤ 16.6ms per frame (60fps) for normal interactions; ≤ 11.1ms (90fps) for declared high-refresh targets
**Rationale:** Dropped frames below 60fps are visible as jank; high-refresh displays (90/120Hz) require tighter budgets
**Measurement:** Instruments Time Profiler (iOS) / Android GPU Inspector; measure on lowest supported device
**PII impact:** none

### Scroll jank

**Target:** < 2% of frames dropped during continuous scroll on lowest supported device
**Rationale:** Scroll jank is the most viscerally noticeable performance failure on mobile
**Measurement:** `CADisplayLink` frame drop monitoring (iOS) / Choreographer jank detection (Android)
**PII impact:** none

---

## Network

### API request timeout

**Target:** 10s timeout for all network calls; display loading state after 300ms; display error after timeout
**Rationale:** Mobile network conditions vary widely; silent hangs with no timeout destroy user trust
**Measurement:** code audit — all `URLSession` / `OkHttp` calls must declare explicit timeout
**PII impact:** none

### Offline behavior

**Target:** All P0 user flows must function (read-only or queued writes) with no network connectivity
**Rationale:** Mobile users lose connectivity constantly; apps that hard-fail offline have lower ratings
**Measurement:** Airplane mode integration test covering each P0 flow
**PII impact:** none

---

## Battery

### Background CPU

**Target:** < 1% CPU utilization when app is backgrounded (no active background task declared)
**Rationale:** Apps draining battery in background are force-killed by the OS and receive App Store warnings
**Measurement:** Instruments Energy Log (iOS) / Battery Historian (Android) — 10-minute background soak
**PII impact:** none

### Background network

**Target:** Zero unsolicited network requests when app is in background without a declared background fetch registration
**Rationale:** Background network causes battery drain and may violate platform policy
**Measurement:** Charles Proxy / mitmproxy capture during 10-minute background soak
**PII impact:** none

---

## App size

### Initial download size

**Target:** ≤ 50MB over-the-air download; ≤ 150MB installed
**Rationale:** Downloads above 200MB require Wi-Fi on iOS by default; large initial sizes reduce install conversion
**Measurement:** App Store Connect (iOS) / Play Console (Android) thinned size report; monitor per release
**PII impact:** none

---

## Error rate

### Crash-free sessions

**Target:** ≥ 99.5% crash-free sessions (≤ 0.5% of sessions with a crash)
**Rationale:** App Store and Play Store surface crash rates; below 99% triggers store ranking penalties
**Measurement:** Firebase Crashlytics / Sentry crash-free rate
**PII impact:** crash reports must be anonymized before transmission — no PII in stack traces

---

## PII fields (excluded from log schema)

<!-- Mobile apps have significant PII risk in analytics and crash reports -->
<!-- Example:
- device_id (IDFA/GAID — requires consent)
- user_id
- push_token
- location_coordinates
- health_data (HealthKit / Health Connect)
-->
___ UNDECLARED — populate before configuring analytics or crash reporting SDK
