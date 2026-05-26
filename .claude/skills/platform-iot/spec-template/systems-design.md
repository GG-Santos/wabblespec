# IoT/Embedded Systems Design Template (P2)

> **Platform:** IoT/Embedded | **Prerequisite:** design-document.md complete.

---

## Hardware Abstraction Layer (HAL)

All hardware access goes through a HAL. Application code never accesses registers directly.

```c
// hal/hal_gpio.h
typedef enum { HAL_GPIO_LOW = 0, HAL_GPIO_HIGH = 1 } hal_gpio_state_t;

hal_status_t hal_gpio_write(uint8_t pin, hal_gpio_state_t state);
hal_gpio_state_t hal_gpio_read(uint8_t pin);
hal_status_t hal_gpio_set_direction(uint8_t pin, hal_gpio_dir_t dir);
```

**HAL enables:** Unit testing without hardware (mock HAL), porting to different MCU (swap HAL implementation).

---

## Task/Interrupt Architecture

```
Hardware Interrupts (ISR — minimal work, no blocking)
  └── Post to queue or set semaphore
        └── RTOS Task (process event, do blocking work)

Superloop (bare metal):
  while(1) {
    read_sensors();        // fast, non-blocking
    process_data();
    update_outputs();
    pet_watchdog();
    sleep_until_next_tick();
  }
```

**ISR rules:**
- No blocking calls (no mutex lock, no UART printf)
- No dynamic memory allocation
- Minimum work: set flag or post to queue, return

---

## Communication Stack

| Interface | Protocol | Purpose |
|---|---|---|
| WiFi / Ethernet | MQTT / HTTP | Cloud telemetry and OTA |
| BLE | GATT profiles | Phone app / provisioning |
| UART | Debug / CLI | Development only — disabled in production build |
| SPI/I2C | Sensor protocols | Peripheral communication |

**Network resilience:**
- Reconnect with exponential backoff (1s → 2s → 4s → max 60s)
- Queue telemetry locally when offline
- Flush queue on reconnect (oldest first)
- Queue size bounded — oldest dropped when full

---

## NVS / Persistent Storage

Non-Volatile Storage for settings and state:

| Key | Type | Default | Description |
|---|---|---|---|
| `wifi_ssid` | string | "" | WiFi credentials |
| `device_id` | string | chip serial | Unique device identifier |
| `fw_version` | string | build-time | Current firmware version |
| `boot_count` | uint32 | 0 | Boot count (detect crash loops) |

**NVS wear leveling:** Use platform NVS API (ESP-IDF NVS, Zephyr settings subsystem) — not raw flash writes. Raw writes without wear leveling destroy flash.

**Write frequency:** NVS writes rated for ~100k cycles. Limit write-heavy operations.

---

## OTA Architecture (Dual-Bank)

```
Flash layout:
  [Bootloader 64KB] [Bank A - Active] [Bank B - Staging] [NVS 32KB]

OTA flow:
  1. Server sends new image metadata (version, size, SHA-256 hash, signature)
  2. Device verifies: new version > current, image fits in bank B
  3. Download image chunks to bank B
  4. Verify SHA-256 of downloaded image
  5. Verify signature with burned public key
  6. Set boot flag: "try bank B on next boot"
  7. Reboot
  8. Bootloader: try bank B, verify signature, boot if valid
  9. Application: confirm boot success → set bank B as active
  10. If step 9 not reached (crash loop): bootloader reverts to bank A
```

---

## Power Management

| Mode | CPU | Peripherals | Wake trigger | Current |
|---|---|---|---|---|
| Active | Full speed | All on | — | ___ mA |
| Light sleep | Stopped (RAM retained) | Selected on | Timer / interrupt | ___ mA |
| Deep sleep | Off (RAM lost) | RTC only | Timer / pin | ___ µA |

**Wake-on-event:** Deep sleep with RTC alarm for periodic sensor reads. Minimize active time.

**Battery life estimate:** `(capacity_mAh) / (avg_current_mA) = hours`. Recalculate as features added.
