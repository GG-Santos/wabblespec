# Build Toolchain — IoT / Embedded

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Hardware target

**MCU/SoC:** `___ UNDECLARED` _(e.g., STM32F4, ESP32-S3, Nordic nRF52840, Raspberry Pi CM4)_
**Architecture:** [ ] ARM Cortex-M  [ ] RISC-V  [ ] Xtensa  [ ] x86 (embedded Linux)  [ ] Other: ___
**RTOS:** [ ] FreeRTOS  [ ] Zephyr  [ ] bare metal  [ ] Embedded Linux (Yocto)  [ ] Other: ___

---

## Language and toolchain

**Language:** [ ] C  [ ] C++  [ ] Rust  [ ] MicroPython  [ ] Other: ___
**Compiler:** [ ] arm-none-eabi-gcc  [ ] LLVM/clang  [ ] rustc (embedded target)  [ ] Other: ___
**SDK:** `___ UNDECLARED` _(e.g., STM32CubeIDE HAL, ESP-IDF, Zephyr SDK, nRF Connect SDK)_

---

## Build

**Build system:** [ ] CMake  [ ] Make  [ ] West (Zephyr)  [ ] cargo (Rust embedded)  [ ] Other: ___
**Output format:** [ ] .bin  [ ] .elf  [ ] .hex  [ ] .uf2  [ ] Other: ___
**Debug interface:** [ ] JTAG  [ ] SWD  [ ] UART  [ ] OpenOCD  [ ] Other: ___

---

## Test runner

**Unit (host-side):** [ ] Unity (C)  [ ] CMocka  [ ] cargo test  [ ] pytest (via serial)  [ ] Other: ___
**Hardware-in-the-loop:** [ ] QEMU  [ ] renode  [ ] physical device farm  [ ] None
**Static analysis:** [ ] MISRA C checker  [ ] clang-analyzer  [ ] cargo clippy  [ ] Other: ___
**Coverage (host-side):** [ ] gcov/lcov  [ ] llvm-cov  [ ] 80% statement on host-compilable code

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] GitLab CI  [ ] Other: ___

**Required CI gates:**
- [ ] Compile (no warnings with -Wall -Werror or equivalent)
- [ ] Static analysis (MISRA / clang-analyzer)
- [ ] Unit tests (host-side)
- [ ] Flash size check (≤ 80% of target flash)
- [ ] RAM static analysis (≤ 75% peak)
- [ ] Hardware-in-the-loop tests (if device farm available)
- [ ] OTA package signing verification
- [ ] Watchdog coverage check (all code paths kick watchdog within window)

---

## OTA update pipeline

**OTA mechanism:** [ ] MCUBOOT  [ ] ESP-IDF OTA  [ ] Mender  [ ] Balena  [ ] Custom  [ ] None
**Signing:** [ ] ed25519 (imgtool)  [ ] RSA (imgtool)  [ ] Custom  [ ] None
**Signing key storage:** `___ UNDECLARED` _(must be HSM or secrets vault — never in source)_
**Rollback:** [ ] A/B partition (automatic on boot failure)  [ ] manual  [ ] None

---

## Fleet observability

**Deployment target:** [ ] AWS IoT Core  [ ] Azure IoT Hub  [ ] Google Cloud IoT  [ ] Balena Cloud  [ ] Self-hosted MQTT  [ ] Other: ___
**Telemetry protocol:** [ ] MQTT  [ ] CoAP  [ ] HTTP  [ ] Other: ___
**Fleet metrics:** [ ] device uptime  [ ] firmware version distribution  [ ] crash/reset count  [ ] battery level  [ ] Other: ___
**Alerting on:** [ ] crash rate threshold  [ ] OTA update failure rate  [ ] watchdog reset count  [ ] Other: ___

_(Monitor generates fleet-level alert rules rather than server-side SLO configs.)_

---

## Notes

_Hardware revision declarations, known errata, lab provisioning procedure:_
