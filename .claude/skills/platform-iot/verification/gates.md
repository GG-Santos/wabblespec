# IoT/Embedded Verification Gates

> **Platform:** IoT/Embedded | All 9 gates must pass before Delivery wave begins.

---

## Gate 1: Flash Budget Declared and Enforced

**Condition:** Flash partition layout declared in design-document.md. Build fails if image exceeds partition.

**Verify:**
```bash
# Confirm linker script matches declared budget
grep -E "FLASH.*LENGTH" src/linker.ld

# Confirm build gate exists in CI
grep -E "check_flash|flash.*budget|overflowed" .github/workflows/*.yml

# Confirm size gate passes on current build
arm-none-eabi-size build/firmware.elf
# text + data must be < application partition size
```

**Pass:** flash_used ≤ application partition size AND CI fails build if exceeded.
**Fail:** No linker enforcement, or flash usage undeclared, or CI ignores overflow.

**Why this matters:** Flash overflow = image won't fit = device won't boot. This is a hard failure at the build stage, not discovered at runtime.

---

## Gate 2: RAM Budget Declared with Breakdown

**Condition:** RAM budget in design-document.md has explicit breakdown: static (.bss+.data) + stack per task × task count + heap + DMA buffers. Total ≤ available RAM.

**Verify:**
```bash
arm-none-eabi-size build/firmware.elf
# data + bss = static RAM

# Sum task stacks from source
grep -r "xTaskCreate\|ulStackDepth\|stack_size" src/
```

**Pass:** All RAM categories declared, totals add up, stack HWM checked in debug build.
**Fail:** "RAM: 128KB" with no breakdown, or stack sizes undeclared, or no HWM measurement.

---

## Gate 3: Watchdog Timer Configured and Tested

**Condition:** Hardware watchdog enabled in production build. Pet happens from highest-priority task. Boot cause register checked on startup.

**Verify:**
```bash
# Watchdog enabled in production config
grep -E "WATCHDOG|IWDG|WDT" sdkconfig src/watchdog.c

# Boot cause check exists
grep -r "reset_reason\|esp_reset_reason\|RCC_CSR\|boot_cause" src/

# Pet call exists in watchdog task only
grep -r "watchdog_pet\|IWDG->KR.*AAAA\|wdt_feed" src/
```

**Hardware test:** Disable pet → observe device resets within timeout → re-enable → normal operation.

**Pass:** Watchdog enabled, pet in highest-priority task, boot cause logged.
**Fail:** Watchdog disabled in production, pet in multiple tasks with no coordination, no boot cause check.

---

## Gate 4: OTA Signature Verification — Valid Accepted, Invalid Rejected

**Condition:** Device applies correctly signed images and rejects unsigned or tampered images.

**Verify:**
```bash
# Signature check exists in OTA code path
grep -r "verify_signature\|ed25519_verify\|ota_verify" src/

# Private key NOT in repository
git log --all --full-history -- "*.pem" "*.key" "*private*"
# Must return empty

# Public key IS in repository (not secret)
grep -r "OTA_PUBLIC_KEY\|public_key" src/
```

**Hardware test:** Flash tampered image → device must reject → check log for rejection message → device continues on current firmware.

**Pass:** Verification in code path, private key absent from repo, tampered image rejected on device.
**Fail:** Signature check skipped or bypassable, private key in repo, device applies unsigned image.

---

## Gate 5: Dual-Bank OTA Rollback — Power Loss Safe

**Condition:** Power loss at any point during OTA write does not brick device. Device boots from bank A if bank B update incomplete or fails boot.

**Verify:**
```bash
# Boot confirmation call exists (ESP-IDF: esp_ota_mark_app_valid_cancel_rollback)
grep -r "mark_app_valid\|ota_confirm\|cancel_rollback" src/

# Rollback trigger exists in bootloader config
grep -E "BOOTLOADER_FACTORY_RESET|OTA_ROLLBACK|boot_attempts" sdkconfig
```

**Hardware test:** Cut power at 25%, 50%, 75% through OTA write → device must recover to bank A each time.

**Pass:** Boot confirmation call present, rollback configured, power-loss test passes at all cut points.
**Fail:** No boot confirmation = device marks failed image as good on next boot, no rollback.

---

## Gate 6: No Credentials or Secrets in Source Control

**Condition:** No plaintext secrets committed to repository.

**Verify:**
```bash
# Scan for common secret patterns
git log --all -p | grep -iE \
  "(password|psk|api_key|private_key|BEGIN RSA|BEGIN EC|AKIA[A-Z0-9]{16})" \
  | grep -v "# example\|placeholder\|_EXAMPLE\|YOUR_"

# Check .gitignore covers secret files
grep -E "\.pem|\.key|secrets\.|\.env" .gitignore

# Confirm OTA signing key not present
find . -name "*.pem" -o -name "*signing_key*" | grep -v ".git"
```

**Pass:** No secrets found in git history, .gitignore covers key file patterns.
**Fail:** Any plaintext credential or private key in history — requires history rewrite and key rotation.

---

## Gate 7: TLS Enforced for All Network Communication

**Condition:** Device uses TLS for MQTT, HTTP, and OTA download. No plaintext transport in production build.

**Verify:**
```bash
# MQTT transport is TLS
grep -r "mqtts://\|MQTT_TRANSPORT_OVER_SSL\|mqtt_cfg.*tls" src/

# HTTP client uses HTTPS
grep -r "https://\|esp_http_client.*cert" src/
grep -v "http://" src/   # should return no production URLs

# Server cert or CA pinned
grep -r "server_cert\|ca_cert\|certificate" src/
```

**Pass:** All network endpoints use TLS, server certificate validated, no `verify_mode=NONE`.
**Fail:** Any plaintext `mqtt://` or `http://` endpoint in production paths, or TLS verify disabled.

---

## Gate 8: Input Validation at Network Boundary

**Condition:** All network-received data has length check before parse. No unbounded string operations on untrusted input.

**Verify:**
```bash
# Length check before payload processing
grep -r "handle_mqtt\|on_message\|mqtt_callback" src/ -A 10 \
  | grep -E "len.*MAX|MAX.*len|payload_len"

# No unsafe string functions on network input
grep -rn "strcpy\|strcat\|sprintf\|gets" src/
# Any match = investigate — ensure not used on untrusted data

# snprintf used with explicit bounds
grep -rn "snprintf" src/ | wc -l  # should be > 0 if string formatting used
```

**Pass:** Length check present before every network payload parse, no unbounded ops on untrusted data.
**Fail:** Missing length check, `strcpy` on network data, `sprintf` with untrusted format string.

---

## Gate 9: Production Build Flags Verified

**Condition:** Production binary has: UART disabled, DEBUG_BUILD absent, watchdog enabled, debug symbols absent from .bin.

**Verify:**
```bash
# UART logging stripped from production binary
arm-none-eabi-strings build/firmware.bin | grep -iE "DEBUG|uart_write|printf"
# Should return empty (or only non-log strings)

# Production flag set
grep "PRODUCTION_BUILD\|NDEBUG" CMakeLists.txt sdkconfig

# No debug symbols in .bin (they're in .elf only)
file build/firmware.bin
# "data" not "ELF with debug info"

# Binary size reasonable (debug builds are 2-3x larger)
ls -la build/firmware.bin
```

**CI enforcement:**
```yaml
- name: Verify production build flags
  run: |
    strings build/firmware.bin | grep -q "DEBUG_BUILD" && \
      { echo "DEBUG_BUILD found in production binary"; exit 1; } || true
```

**Pass:** UART output absent from .bin, production flags set, binary size consistent with release build.
**Fail:** Debug strings in production binary, watchdog disabled, UART logging active in production.

---

## Gate Summary

| # | Gate | Automated | Hardware required |
|---|---|---|---|
| 1 | Flash budget enforced | Yes (CI) | No |
| 2 | RAM budget declared | Partial (static analysis) | No |
| 3 | Watchdog configured and tested | Partial | Yes |
| 4 | OTA signature: valid accepted, invalid rejected | Partial | Yes |
| 5 | Dual-bank rollback — power loss safe | No | Yes |
| 6 | No credentials in source control | Yes (git scan) | No |
| 7 | TLS enforced | Yes (grep) | No |
| 8 | Input validation at boundary | Partial (static) | No |
| 9 | Production build flags verified | Yes (CI) | No |

Gates 3, 4, 5 require hardware-in-loop or physical device testing. Document test results in delivery receipt.
