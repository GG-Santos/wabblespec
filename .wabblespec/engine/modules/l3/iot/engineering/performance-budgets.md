# IoT/Embedded Performance Budgets

> **Platform:** IoT/Embedded

---

## Flash Budget

Flash is fixed. Image overflow = device won't boot.

```
Total flash:          ___ KB   (from hardware target)
Bootloader:            64 KB   (reserve — secure bootloader)
Application (bank A): ___ KB   (target: ≤ 80% of remaining after bootloader)
OTA staging (bank B): ___ KB   (must equal bank A — same image size)
NVS/settings:          32 KB   (minimum; increase if many keys)
Reserved/overhead:     16 KB
```

**Hard limit:** Application binary must not exceed bank A size. Linker enforces this — build fails if exceeded.

**Target utilization:** ≤ 80% of application partition. Headroom for future patches.

| Check | Threshold | Action on breach |
|---|---|---|
| Flash usage | > 80% | Investigate, remove unused code |
| Flash usage | > 95% | Block merge — OTA may fail |
| Flash usage | > 100% | Build fails — linker error |

**Measure:** `arm-none-eabi-size firmware.elf` → `text + data` = flash usage.

---

## RAM Budget

RAM overflow at runtime = stack corruption or heap exhaustion = crash or silent data corruption.

```
Total RAM:              ___ KB
Static (.bss + .data):  ___ KB   (known at link time)
Stack per task:          ___ KB × ___ tasks = ___ KB
Main/ISR stack:          ___ KB
Heap (if used):          ___ KB   (minimize — avoid in production paths)
DMA buffers:             ___ KB   (must be aligned, often in specific RAM region)
Reserved:                ___ KB
```

**Hard limit:** Total ≤ RAM available. Stack overflow detection enabled (RTOS hook).

| Check | Threshold | Action on breach |
|---|---|---|
| Static RAM (link time) | > 70% total RAM | Audit .bss — find large buffers |
| Peak heap (runtime) | > allocated heap | Increase heap or reduce allocation |
| Stack high-water mark | > 80% of task stack | Increase task stack |
| Stack high-water mark | > 95% | Crash imminent — fix immediately |

**Measure static:** `arm-none-eabi-size firmware.elf` → `data + bss` = static RAM.
**Measure stack:** `uxTaskGetStackHighWaterMark(task_handle)` in FreeRTOS — call periodically in debug builds.

---

## Timing Budgets

### Superloop / Bare metal

| Operation | Budget | Notes |
|---|---|---|
| Sensor read (I2C/SPI) | ___ ms | DMA or interrupt-driven — not blocking poll |
| Data processing | ___ ms | |
| Output update | ___ ms | |
| Total loop period | ___ ms | Must complete before next tick |
| ISR execution | < 10 µs | No blocking, no alloc, post to queue only |

### RTOS Task Periods

| Task | Period | Worst-case execution | Headroom |
|---|---|---|---|
| `sensor_task` | ___ ms | ___ ms | ≥ 20% |
| `comm_task` | Event-driven | ___ ms max | — |
| `watchdog_task` | ___ ms | < 1 ms | — |

**Watchdog pet must happen within watchdog timeout.** Watchdog task highest priority.

### Boot Time

| Phase | Budget |
|---|---|
| Bootloader signature check | < 500 ms |
| Application init (HAL, RTOS, peripherals) | < 2 s |
| First sensor reading available | < 5 s |
| Network connected (WiFi/BLE) | < 30 s |

---

## Power Budget

Battery life is a hard product requirement for battery-operated devices.

```
Battery capacity:     ___ mAh
Target life:          ___ days / ___ hours

Power states:
  Active (WiFi tx):   ___ mA  × ___ ms per cycle
  Active (sensing):   ___ mA  × ___ ms per cycle
  Light sleep:        ___ mA  × ___ ms per cycle
  Deep sleep:         ___ µA  × ___ ms per cycle

Average current:      ___ mA  (weighted average across cycle)
Estimated life:       capacity_mAh / avg_mA = ___ hours
```

**Power optimization priority:**
1. Minimize time in active state (fast sensor read → deep sleep)
2. Disable peripherals when not in use
3. Reduce WiFi/BLE tx power to minimum acceptable
4. Use RTC alarm for periodic wake — not polling

| Mode | Current target | Measure tool |
|---|---|---|
| Deep sleep | < 50 µA | Power analyzer or Nordic PPK2 |
| Light sleep | < 2 mA | |
| Active (no radio) | < 50 mA | |
| WiFi TX peak | < 250 mA | (limited by hardware) |

---

## Communication Latency

| Operation | Budget | Notes |
|---|---|---|
| MQTT publish (WiFi, good signal) | < 500 ms | |
| MQTT subscribe → callback | < 1 s | |
| BLE characteristic write | < 200 ms | |
| OTA chunk download (per chunk) | < 5 s | Depends on network — implement timeout |
| Total OTA time | < 10 min | For typical 1MB image |

**OTA timeout:** If chunk download exceeds timeout, abort and retry from last confirmed chunk. Track byte offset in NVS.

---

## NVS Write Frequency

NVS flash rated ~100k write cycles per sector.

| Key | Write frequency | Cycle life at that rate |
|---|---|---|
| Sensor calibration | Once at setup | Effectively unlimited |
| Device settings | On user change | Effectively unlimited |
| `boot_count` | Every boot | 100k boots ≈ 274 years at 1/day |
| Telemetry cache | Every reading | **DANGEROUS if frequent** |

**Rule:** Never write NVS more than once per minute from automated paths. Telemetry goes to RAM queue — flush batch on network reconnect, not per-reading.

---

## Build Size Trend

Track over time. Sudden increase = unintended dependency pulled in.

```
CI artifact: firmware_size_report.json
{
  "text_bytes": 123456,
  "data_bytes": 4096,
  "bss_bytes": 32768,
  "flash_percent": 72.3,
  "ram_static_percent": 45.1,
  "build": "abc1234",
  "timestamp": "2026-05-22T10:00:00Z"
}
```

Plot `flash_percent` over commits. Alert if single commit increases by > 5%.
