# IoT/Embedded Platform Verification

> **Platform:** IoT/Embedded

---

## How to Run Gates

### Gate 1: Flash Budget

```bash
# After build completes:
arm-none-eabi-size build/firmware.elf

# Output:
#    text    data     bss     dec     hex filename
#  123456    4096   32768  160320   27240 build/firmware.elf

# flash_used = text + data
# Compare to partition budget from design-document.md

python3 scripts/check_flash.py \
  --elf build/firmware.elf \
  --budget-kb 960          # bank A size from linker script
# Exit 0 = pass, Exit 1 = over budget
```

**Linker also enforces:** If image physically exceeds partition, build fails with:
```
region `FLASH' overflowed by 12345 bytes
```
This is a hard failure — no binary produced.

---

### Gate 2: RAM Budget (Static)

```bash
arm-none-eabi-size build/firmware.elf
# data + bss = static RAM usage
# Must be < (total RAM - stack allocation - heap allocation)

# FreeRTOS: also check task stack allocations in task creation calls
grep -r "xTaskCreate\|xTaskCreateStatic" src/ \
  | python3 scripts/sum_stack_sizes.py
```

---

### Gate 3: Stack High-Water Mark (Runtime)

Add to debug build — run for minimum 1 hour of realistic workload:

```c
// In watchdog_task or a debug reporting task:
void report_stack_usage(void) {
    UBaseType_t hwm = uxTaskGetStackHighWaterMark(sensor_task_handle);
    log_debug("sensor_task stack HWM: %u words remaining", hwm);
    // hwm < 50 words = danger zone
}
```

**Interpret:** `uxTaskGetStackHighWaterMark` returns words remaining (not used). Low value = stack nearly exhausted.

---

### Gate 4: Watchdog Behavior

Verify in integration test or hardware test:

1. Disable watchdog pet in watchdog task (comment out `watchdog_pet()` call)
2. Observe device resets within `timeout_ms`
3. Check boot log records watchdog reset cause
4. Re-enable — verify normal operation resumes

```c
// Boot cause check (ESP-IDF example):
esp_reset_reason_t reason = esp_reset_reason();
if (reason == ESP_RST_WDT || reason == ESP_RST_TASK_WDT) {
    nvs_increment_counter("watchdog_reset_count");
    log_error("Watchdog reset detected");
}
```

---

### Gate 5: OTA Signature Verification

```bash
# Test valid image — must apply
espsecure.py sign_data --keyfile valid_key.pem firmware.bin --output valid.bin
# Flash valid.bin → device must accept and boot new image

# Test invalid image — must reject
dd if=/dev/urandom bs=32 count=1 > bad_sig.bin
cat firmware.bin bad_sig.bin > tampered.bin
# Flash tampered.bin → device must reject, stay on current image
# Check log: "OTA signature verification FAILED"

# Test rollback
# Flash image that doesn't call ota_mark_app_valid_cancel_rollback() (ESP-IDF)
# Device must revert to previous image after max_boot_attempts
```

---

### Gate 6: Power Consumption

Requires hardware measurement tool (Nordic PPK2, Otii Arc, or bench supply with current sensing):

```
Test procedure:
1. Flash production build (UART disabled, watchdog enabled)
2. Allow device to reach steady state (30 seconds)
3. Measure current in each power mode:
   - Active: trigger sensor read via GPIO/BLE
   - Light sleep: observe between readings
   - Deep sleep: RTC wakeup disabled, measure baseline
4. Compare to budgets in performance-budgets.md
```

**Automated:** Some targets support software current estimation via CPU cycle counting, but hardware measurement is authoritative.

---

### Gate 7: Fail-Safe — Power Loss During OTA

```
Test procedure:
1. Start OTA update
2. Cut power at various points during flash write:
   a. During chunk download (before any flash write)
   b. After 25% of image written
   c. After 75% of image written
   d. After write complete, before boot flag set
3. Power on device
4. Verify: device boots from previous working image (bank A)
5. Verify: boot log records failed update attempt
6. Verify: device is NOT bricked (still functional)
```

Run test at each cut point. All must pass.

---

### Gate 8: Linker Symbol Map Audit

```bash
# Generate map file
cmake --build . -- VERBOSE=1 2>&1 | grep -i "map"
# Or: add -Wl,-Map=firmware.map to linker flags

# Find largest symbols
python3 scripts/parse_map.py firmware.map --top 20

# Flag unexpected large allocations:
# - Test code compiled into production build
# - Printf format strings (indicate logging not stripped)
# - Large static buffers not in design doc
```

---

### Gate 9: Hardware-in-Loop Smoke Test

Minimum set for CI with hardware target attached (e.g., via JTAG runner):

```python
# test_smoke.py — runs via pytest with serial connection to device
def test_device_boots():
    serial = connect_serial(port=DEVICE_PORT, baud=115200)
    output = serial.read_until("Application started", timeout=10)
    assert "Application started" in output

def test_sensor_read():
    serial.write(b"READ_SENSOR\r\n")  # debug CLI command
    output = serial.read_until("\r\n", timeout=5)
    value = float(output.strip())
    assert 0 <= value <= 100  # plausible range for temperature

def test_watchdog_disabled_in_debug():
    # Debug build only — watchdog disabled to allow breakpoints
    assert "WATCHDOG_ENABLED" not in build_flags()
```

**CI with hardware:** Use self-hosted runner with device attached. Not all CI platforms support this — use QEMU or hardware emulator where available.

---

## Interpreting Common Failures

| Failure | Cause | Fix |
|---|---|---|
| `region 'FLASH' overflowed` | Image too large | Enable `-Os`, run `--gc-sections`, audit large symbols in .map |
| Stack overflow hook fired | Task stack too small | Increase stack, or move large locals to static/heap |
| Watchdog fires immediately | Watchdog task starved | Check task priorities — watchdog task must be highest |
| OTA rejected valid image | Wrong key or key mismatch | Verify key burned matches key used to sign |
| Device bricks after OTA | Missing `ota_mark_valid` call | Application must confirm boot before rollback window expires |
| NVS read fails on boot | Flash wear or bad write | Check `nvs_flash_init` return code, add erase-and-reinit fallback |
| Current 10x higher than budget | Peripheral not sleeping | Audit power state transitions — confirm deep sleep entry |
