# IoT/Embedded Design Document Template (P1)

> **Platform:** IoT/Embedded | Sections marked `[REQUIRED]` must be filled before Specify receipt.

---

## Overview [REQUIRED]

One paragraph: what this firmware does, what hardware it runs on, what it controls/monitors, and what failure looks like (stuck loop, data loss, safety hazard).

---

## Hardware Target [REQUIRED]

| Property | Value |
|---|---|
| MCU/SoC | e.g. STM32F446RE, ESP32-S3, nRF52840, RP2040 |
| Architecture | ARM Cortex-M4 / Xtensa LX7 / RISC-V / AVR |
| Flash | ___ KB/MB total |
| RAM | ___ KB/MB total |
| Clock speed | ___ MHz |
| FPU | Yes / No |
| Crypto hardware | Yes (AES/SHA/RNG) / No |
| Operating voltage | ___ V |

---

## Memory Budget [REQUIRED]

Flash and RAM are finite and hard. Overflow = won't boot or will crash.

**Flash (code + read-only data):**
```
Total flash:       ___ KB
Bootloader:        ___ KB (reserve for secure bootloader)
Application:       ___ KB (target: ≤ 80% of remaining)
OTA staging:       ___ KB (if OTA: needs space for new image)
NVS/settings:      ___ KB
Reserved/overhead: ___ KB
```

**RAM (static + stack + heap):**
```
Total RAM:         ___ KB
Static (.bss+.data): ___ KB
Stack (per task):  ___ KB × ___ tasks
Heap:              ___ KB (if dynamic alloc used — minimize)
DMA buffers:       ___ KB
Reserved:          ___ KB
```

**No dynamic allocation in interrupt handlers or time-critical paths.**

---

## RTOS / Bare Metal [REQUIRED]

[ ] Bare metal (superloop or interrupt-driven)
[ ] FreeRTOS
[ ] Zephyr RTOS
[ ] ThreadX / Azure RTOS
[ ] ESP-IDF (FreeRTOS-based)
[ ] Other: ___

**If RTOS — task list:**

| Task name | Stack size | Priority | Period | What it does |
|---|---|---|---|---|
| `sensor_task` | ___ bytes | ___ | ___ ms | Read sensors, post to queue |
| `comm_task` | ___ bytes | ___ | Event-driven | Handle network/BLE |
| `watchdog_task` | ___ bytes | Highest | ___ ms | Pet watchdog, check health |

---

## OTA Update Strategy [REQUIRED]

| Property | Decision |
|---|---|
| OTA supported | [ ] Yes [ ] No (physical flash only) |
| Transport | BLE / WiFi / cellular / UART |
| Signing | Required — image signature verified before apply |
| Rollback | [ ] Yes — revert to previous image on boot failure |
| Staging | Dual-bank (download to bank B, swap on success) |
| OTA trigger | [ ] Push (server initiates) [ ] Pull (device polls) |

**Unsigned firmware is never accepted.** OTA without signature verification is an attack vector.

---

## Watchdog Timer [REQUIRED]

**Hardware watchdog:** [ ] Enabled [ ] Not available on this MCU (document why)

| Property | Value |
|---|---|
| Timeout | ___ ms |
| Pet frequency | Every ___ ms from watchdog task |
| On timeout | Hardware reset |
| Stuck task detection | Watchdog task detects if other tasks stop petting it |

**Watchdog is the last defense against stuck code.** Must be enabled in production builds.

---

## Fail-Safe Behavior [REQUIRED]

What happens when power is lost unexpectedly, network disappears, or hardware fails?

| Scenario | Fail-safe behavior |
|---|---|
| Power loss mid-OTA write | Boot from previous image (dual-bank); never brick |
| Sensor read failure | Use last known value for ___ seconds, then alarm state |
| Network loss | Continue local operation; queue telemetry; sync when reconnected |
| Stack overflow | Watchdog resets; boot log records cause |
| Flash write failure | Retry ___ times; enter safe mode on persistent failure |

---

## GWT Acceptance Scenarios (IoT-specific)

```
Given: OTA update is downloaded and about to be applied
When: power is cut during the flash write
Then: device boots from previous working image
      AND boot log records the failed update attempt
      AND device is NOT bricked

Given: a firmware image with invalid signature is received
When: bootloader verifies signature
Then: image is rejected — not applied
      AND device continues running current firmware
      AND rejection is logged

Given: sensor task stops responding (simulated deadlock)
When: watchdog task fails to receive heartbeat from sensor task
Then: hardware watchdog fires after timeout
      AND device resets cleanly
      AND boot log records watchdog reset cause

Given: flash memory budget is exceeded at build time
When: linker runs
Then: build fails with clear error: image too large for flash
      AND no binary is produced
```

---

## Open Questions

Specify blocks receipt until REQUIRED sections complete.
