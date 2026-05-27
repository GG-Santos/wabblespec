# Performance Budgets — Desktop

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/desktop`.
> Reference: `.wabblespec/engine/shared/references/performance-budgets.md`.

---

## Startup

### Cold start (window visible)

**Target:** ≤ 3s from launch to first visible window on a modern consumer machine (8GB RAM, SSD)
**Rationale:** Desktop users compare against native apps; Electron/Tauri apps above 3s cold start face negative perception
**Measurement:** `process.hrtime()` from main process entry to `BrowserWindow.loadURL` complete (Electron) / Tauri equivalent; average across 5 cold runs
**PII impact:** none

### Cold start (interactive)

**Target:** ≤ 5s from launch to fully interactive (all critical data loaded, no loading spinners)
**Rationale:** Window visible ≠ interactive; users attempt to click within 1-2s of seeing the window
**Measurement:** timing from window-show event to last loading indicator dismissed; measure on minimum spec machine
**PII impact:** none

---

## Memory

### Steady-state memory (idle)

**Target:** ≤ 300MB resident memory with application idle and no open documents/projects
**Rationale:** Desktop apps run alongside many other apps; persistent high memory usage causes system slowdowns and user complaints
**Measurement:** Task Manager / Activity Monitor resident set size; 10-minute idle soak
**PII impact:** none

### Peak memory (active use)

**Target:** ≤ ___ MB during normal active use (declare based on application type)
**Rationale:** Declare based on expected workload; editor-class apps may need 1GB+; productivity tools should stay under 500MB
**Measurement:** peak RSS during representative use scenario on minimum spec machine
**PII impact:** none

### Memory growth (no-leak check)

**Target:** < 5% memory growth per hour of continuous use without explicit large data operations
**Rationale:** Slow memory leaks in long-running apps cause degraded performance and eventual OOM
**Measurement:** automated 1-hour soak test measuring RSS at 5-minute intervals
**PII impact:** none

---

## CPU

### Idle CPU

**Target:** < 1% CPU utilization when application is in focus but idle (no active user input for 5s)
**Rationale:** Spinning CPU when idle drains laptop battery and causes fan noise — immediate negative signal to users
**Measurement:** Task Manager / `top` sampling during idle soak; fail if above threshold for > 10% of samples
**PII impact:** none

### UI thread responsiveness

**Target:** < 100ms response time for any synchronous UI action (click, keystroke); operations > 100ms must move off the main thread
**Rationale:** Main thread blocking causes frozen windows and "not responding" OS labels
**Measurement:** Performance profiler during common user actions; flag any main-thread operations > 100ms
**PII impact:** none

---

## Update

### Update package size

**Target:** ≤ ___ MB for delta update (not full reinstall); full installer ≤ ___ MB
**Rationale:** Large updates over slow or metered connections cause update abandonment; users on old versions are a support burden
**Measurement:** build output; compare package size across consecutive releases
**PII impact:** none

### Auto-updater reliability

**Target:** ≥ 99% of initiated updates complete successfully; failed updates must preserve the previous working version
**Rationale:** An update that breaks the app and loses the previous version is catastrophic for desktop users
**Measurement:** staged rollout monitoring; track update success/failure events
**PII impact:** update events must not include usage data without consent

---

## IPC / Renderer (Electron/Tauri)

### IPC round-trip latency

**Target:** ≤ 50ms for main↔renderer IPC calls for user-triggered operations
**Rationale:** IPC calls above 50ms on user-triggered actions produce visible lag in the renderer
**Measurement:** performance.mark() around ipcRenderer.invoke() calls; alert on p99 breach
**PII impact:** IPC payloads must not include credentials or tokens

---

## Error rate

### Crash-free sessions

**Target:** ≥ 99.9% crash-free sessions
**Rationale:** Desktop users expect higher reliability than mobile; a 0.1% crash rate is noticeable in a day's work
**Measurement:** Sentry / Bugsnag crash-free rate; monitor per release
**PII impact:** crash dumps must not capture process memory containing user data

---

## PII fields (excluded from log schema)

<!-- Desktop apps may log file paths, which can contain usernames and reveal private directories -->
<!-- Example:
- file_paths (contain OS username in path)
- clipboard_contents
- recently_opened_documents
- window_titles (may contain document names)
-->
___ UNDECLARED — populate before enabling any telemetry or crash reporting
