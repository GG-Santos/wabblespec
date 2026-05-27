# Performance Budgets — IoT / Embedded

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/iot`.
> Reference: `.wabblespec/engine/shared/references/performance-budgets.md`.
> Note: IoT performance budgets are resource budgets, not latency SLOs.

---

## Flash (storage)

### Flash occupancy

**Target:** ≤ 80% of available flash for application code + data
**Rationale:** Flash above 80% leaves insufficient headroom for OTA updates and runtime wear leveling; 80% is the industry-standard ceiling
**Measurement:** linker map analysis at build time; fail CI if binary + data exceeds threshold
**PII impact:** none

### OTA update package size

**Target:** OTA update ≤ 50% of total flash capacity (enables A/B partition scheme)
**Rationale:** A/B OTA requires space for two firmware images; updates larger than half the flash prevent A/B and require risky in-place updates
**Measurement:** build output; enforce in CI
**PII impact:** none

---

## RAM

### Peak RAM at runtime

**Target:** ≤ 75% of available RAM under maximum concurrent load
**Rationale:** RAM above 75% at peak leaves insufficient headroom for stack growth and interrupt handlers; overflow causes hard fault
**Measurement:** worst-case static analysis (MISRA tooling) + runtime high-water mark via `uxTaskGetStackHighWaterMark()` (FreeRTOS) or equivalent
**PII impact:** none

### Stack depth per task

**Target:** Each task must have ≥ 20% stack headroom under worst-case execution path
**Rationale:** Stack overflow in an embedded system causes silent memory corruption, not a clean crash
**Measurement:** `uxTaskGetStackHighWaterMark()` sampled under load; declare per-task in code review
**PII impact:** none

---

## Timing

### Watchdog window

**Target:** ___ ms (required — declare the watchdog timer period for this firmware)
**Rationale:** Watchdog timer is the last line of defense against hangs; period must be declared and enforced at system level — not optional
**Measurement:** hardware timer configuration; code audit verifies watchdog kick is called within every code path that could reach the window boundary
**PII impact:** none

### Startup time (time to first ready signal)

**Target:** ≤ ___ ms from power-on / reset to first operational ready signal
**Rationale:** System startup time affects host system initialization sequences; undeclared startup time causes integration timing bugs
**Measurement:** GPIO toggle at start and at ready; measure with logic analyzer
**PII impact:** none

### Real-time deadline (if applicable)

**Target:** ___ UNDECLARED — declare if any task has a hard real-time deadline
**Rationale:** Hard deadlines require worst-case execution time (WCET) analysis; missing them silently is the primary real-time failure mode
**Measurement:** WCET analysis tool or manual worst-case path tracing; verify with logic analyzer
**PII impact:** none

---

## Power

### Sleep current

**Target:** ≤ ___ µA in deep sleep (declare based on battery capacity and target operational life)
**Rationale:** Battery life is determined by the sleep current integral; undeclared sleep budget makes lifetime guarantees impossible
**Measurement:** µCurrent / Nordic PPK2 or equivalent current probe; measure at stable temperature
**PII impact:** none

### Active current (peak)

**Target:** ≤ ___ mA during peak transmission / computation
**Rationale:** Peak current determines minimum battery capacity and regulator sizing; exceeding peak causes brownout
**Measurement:** current probe during worst-case RF transmission + computation burst
**PII impact:** none

---

## Reliability

### MTBF target

**Target:** ___ UNDECLARED — declare mean time between failures if product has an uptime SLA
**Rationale:** MTBF declaration drives reliability testing duration and failure mode analysis scope
**Measurement:** accelerated life testing or field failure rate from deployed fleet
**PII impact:** none

### Power-loss safety

**Target:** Device must reach a safe, consistent state within 100ms of power loss detection; no data corruption on unclean shutdown
**Rationale:** Power loss is the most common unexpected event in IoT; corrupted state on power loss requires factory reset — catastrophic for deployed devices
**Measurement:** power-cycle integration test: 1000 random-point power cuts during active write operations; verify clean state on each restart
**PII impact:** none

---

## OTA integrity

### Signed OTA required

**Target:** 100% of OTA packages verified against firmware signing key before flash; unsigned images rejected unconditionally
**Rationale:** Unsigned OTA is a remote code execution vector; enforced in `l3/iot` acceptance tests (AT-IOT-06)
**Measurement:** OTA stack code audit + integration test: flash attempt with tampered signature must be rejected
**PII impact:** signing keys must be stored in hardware secure element or provisioned key vault, not in source

---

## PII fields (excluded from log schema)

<!-- IoT devices may log sensor data that constitutes PII under GDPR (location, health, home occupancy) -->
<!-- Example:
- gps_coordinates
- accelerometer_data (can infer health/activity)
- presence_detection (home occupancy)
- voice_wakeword_buffer
-->
___ UNDECLARED — populate during GDPR/CCPA compliance review
