# IoT/Embedded Technical Spec Template (P3)

> **Platform:** IoT/Embedded | **Prerequisite:** systems-design.md complete.

---

## Peripheral Driver Specs

Each peripheral gets one entry.

### `<Peripheral Name>` (e.g. BME280 Temperature/Humidity)

**Interface:** SPI / I2C at ___ Hz
**HAL calls:** `hal_i2c_write()`, `hal_i2c_read()`
**Initialization sequence:**
```c
// 1. Power-on delay: 2ms
// 2. Write config register: 0xF4 = 0x27 (normal mode, 1x oversampling)
// 3. Read chip ID: expect 0x60
bme280_status_t bme280_init(bme280_handle_t *handle);
```

**Read cycle:** Every ___ ms. Non-blocking: DMA or interrupt-driven read.

**GWT scenarios:**
```
Given: sensor is powered and configured
When: read is triggered
Then: raw ADC values are returned within 10ms
      AND values are within physical plausible range
      AND CRC matches if sensor provides CRC

Given: sensor is not responding (unplugged)
When: read is attempted
Then: HAL returns HAL_TIMEOUT after ___ ms
      AND application uses last known value
      AND error counter increments
```

---

## Watchdog Implementation

```c
// Initialize hardware watchdog (must be done before RTOS scheduler starts):
void watchdog_init(uint32_t timeout_ms) {
    IWDG->KR = 0xCCCC;   // Start watchdog
    IWDG->KR = 0x5555;   // Enable write
    IWDG->PR = 0x04;     // Prescaler /64
    IWDG->RLR = (timeout_ms * LSI_FREQ) / (64 * 1000);
    IWDG->KR = 0xAAAA;   // Reload
}

// Pet watchdog (from watchdog task only):
void watchdog_pet(void) {
    IWDG->KR = 0xAAAA;
}
```

**Boot cause check:** On startup, read reset cause register. If watchdog reset: log, increment watchdog_reset counter in NVS, alert if count > threshold (crash loop).

---

## OTA Signature Verification

```c
// Keys burned at manufacturing — immutable after provisioning
extern const uint8_t OTA_PUBLIC_KEY[32];  // Ed25519 public key in flash

ota_status_t ota_verify_image(const uint8_t *image, size_t len, const uint8_t *sig) {
    // 1. Compute SHA-256 of image
    uint8_t hash[32];
    sha256_compute(image, len, hash);

    // 2. Verify Ed25519 signature
    if (!ed25519_verify(sig, hash, sizeof(hash), OTA_PUBLIC_KEY)) {
        log_error("OTA signature verification FAILED");
        return OTA_ERR_INVALID_SIGNATURE;
    }
    return OTA_OK;
}
```

**Signing private key:** Never on device. In HSM or CI secrets vault. Never in source control.

---

## Memory Safety

**Stack overflow detection:** Enable RTOS stack overflow hook. In FreeRTOS:
```c
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    // Log task name to persistent storage before reset
    log_critical("Stack overflow in task: %s", pcTaskName);
    NVIC_SystemReset();  // Force reset
}
```

**Heap:** Avoid in embedded. If used: use FreeRTOS heap_4.c (coalescing). Track peak heap usage in debug builds.

**No `malloc`/`free` in production paths.** Pre-allocate all buffers at startup.

---

## Debug / Logging Strategy

| Build type | UART logging | Log level | Watchdog |
|---|---|---|---|
| Debug | Enabled | DEBUG | Disabled (allows breakpoints) |
| Release/Production | Disabled | ERROR → NVS only | Enabled |

**Production logging:** Error events written to circular log in NVS. Readable via diagnostic command or on next OTA upload.

**No `printf` in ISRs.** UART output blocks — use DMA-backed ring buffer logger.
