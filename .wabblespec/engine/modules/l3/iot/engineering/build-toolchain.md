# IoT/Embedded Build Toolchain

> **Platform:** IoT/Embedded

---

## Toolchain Selection

| Target | Toolchain | Build system |
|---|---|---|
| STM32 / ARM Cortex-M | `arm-none-eabi-gcc` | CMake + STM32CubeMX or Makefile |
| ESP32 / ESP32-S3 | `xtensa-esp32-elf-gcc` | ESP-IDF (CMake-based) |
| ESP32-C3 / RISC-V | `riscv32-unknown-elf-gcc` | ESP-IDF |
| nRF52 / nRF53 | `arm-none-eabi-gcc` | Zephyr (west + CMake) |
| RP2040 | `arm-none-eabi-gcc` | CMake (pico-sdk) |
| AVR (Arduino-compatible) | `avr-gcc` | PlatformIO |
| Multi-target | `arm-none-eabi-gcc` | PlatformIO |

**Cross-compilation:** Host is x86-64 Linux/Mac/Windows. Target is bare-metal ARM/Xtensa/RISC-V. Never use host `gcc` for firmware.

---

## Build System Configs

### CMake (ARM/STM32/RP2040)

```cmake
cmake_minimum_required(VERSION 3.20)
project(firmware C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -Werror")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ffunction-sections -fdata-sections")
set(LINKER_FLAGS "-Wl,--gc-sections -Wl,-Map=${PROJECT_NAME}.map")

# Optimization: size for release, debug info for debug
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Os")
    add_definitions(-DNDEBUG -DPRODUCTION_BUILD)
else()
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Og -g3")
    add_definitions(-DDEBUG_BUILD)
endif()

add_executable(${PROJECT_NAME}.elf ${SOURCES})
target_link_options(${PROJECT_NAME}.elf PRIVATE ${LINKER_FLAGS})

# Binary outputs
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND arm-none-eabi-objcopy -O binary ${PROJECT_NAME}.elf ${PROJECT_NAME}.bin
    COMMAND arm-none-eabi-objcopy -O ihex ${PROJECT_NAME}.elf ${PROJECT_NAME}.hex
    COMMAND arm-none-eabi-size ${PROJECT_NAME}.elf
)
```

### ESP-IDF (ESP32)

```bash
# Project structure
my_project/
  CMakeLists.txt      # top-level
  main/
    CMakeLists.txt
    main.c
  components/         # reusable components
  sdkconfig           # Kconfig selections (committed to git)
  sdkconfig.defaults  # baseline config for CI

# Build commands
idf.py set-target esp32s3
idf.py build
idf.py flash monitor

# CI build
idf.py build 2>&1 | tee build.log
# Check exit code — nonzero = build failure
```

### Zephyr (nRF52/nRF53)

```bash
# Initialize workspace
west init -m https://github.com/zephyrproject-rtos/zephyr --mr v3.6.0
west update

# Build for target
west build -b nrf52840dk/nrf52840 app/

# Board-specific config
app/
  prj.conf            # Kconfig selections
  boards/
    nrf52840dk_nrf52840.conf  # board overlay config
  CMakeLists.txt
```

### PlatformIO (multi-target)

```ini
; platformio.ini
[env:production]
platform = espressif32
board = esp32dev
framework = espidf
build_flags =
    -DPRODUCTION_BUILD
    -Os
    -Wall -Werror
build_type = release

[env:debug]
platform = espressif32
board = esp32dev
framework = espidf
build_flags =
    -DDEBUG_BUILD
    -Og -g3
build_type = debug
```

---

## Linker Script Requirements

Flash and RAM overflow = build fails. Linker script enforces budget:

```ld
/* stm32f446re.ld */
MEMORY {
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
}

/* If image exceeds FLASH LENGTH, linker errors:
   region `FLASH' overflowed by NNN bytes */
```

**Never ignore linker overflow errors.** Image too large = device won't boot.

---

## Build Outputs

| File | Purpose |
|---|---|
| `firmware.elf` | Debug symbol file — used with JTAG/GDB |
| `firmware.bin` | Raw binary for flashing |
| `firmware.hex` | Intel HEX format (many flashers require this) |
| `firmware.map` | Symbol map — audit for unexpected large symbols |
| `build.log` | Full build output including size report |

**Size report (arm-none-eabi-size):**
```
   text    data     bss     dec     hex filename
 123456    4096   32768  160320   27240 firmware.elf
```
- `text` = flash usage (code + read-only data)
- `data` = initialized variables (in flash + copied to RAM at boot)
- `bss` = zero-initialized RAM
- `dec` = total — compare to budget

---

## CI Gates

```yaml
# .github/workflows/firmware.yml
jobs:
  build:
    runs-on: ubuntu-latest
    container: espressif/idf:v5.2.1  # pinned — never :latest

    steps:
      - uses: actions/checkout@v4

      - name: Build Release
        run: idf.py build
        env:
          IDF_TARGET: esp32s3

      - name: Check flash budget
        run: |
          SIZE=$(python3 scripts/check_size.py build/firmware.bin)
          BUDGET=1572864  # 1.5MB — adjust to project
          if [ "$SIZE" -gt "$BUDGET" ]; then
            echo "FLASH OVERFLOW: $SIZE bytes > $BUDGET byte budget"
            exit 1
          fi

      - name: Check RAM budget (static)
        run: |
          arm-none-eabi-size build/firmware.elf | python3 scripts/check_ram.py

      - name: Verify production flags
        run: |
          # Confirm DEBUG_BUILD not set in release binary
          arm-none-eabi-strings build/firmware.bin | grep -v "DEBUG_BUILD"

      - name: Sign firmware (if OTA enabled)
        run: |
          espsecure.py sign_data --keyfile ${{ secrets.OTA_SIGNING_KEY }} \
            --version 2 build/firmware.bin --output build/firmware.signed.bin
```

**Toolchain version pinned in CI.** Floating compiler = non-deterministic builds.

---

## OTA Image Preparation

```bash
# ESP-IDF: generate signed OTA image
espsecure.py sign_data \
  --keyfile ota_signing_key.pem \   # NOT in repo — from CI secrets
  --version 2 \
  firmware.bin \
  --output firmware.signed.bin

# STM32: sign with custom tool or mcuboot
imgtool sign \
  --key ota_signing_key.pem \
  --header-size 0x200 \
  --align 4 \
  --version 1.2.3 \
  --slot-size 0x60000 \
  firmware.bin firmware.signed.bin
```

**OTA signing key never in repository.** Stored in CI secrets vault or HSM.

---

## Debug / Flash Tools

| Tool | Purpose |
|---|---|
| OpenOCD + GDB | JTAG/SWD debugging for ARM targets |
| `idf.py flash monitor` | ESP32 flash + serial monitor |
| J-Link GDB Server | nRF52/nRF53 debugging |
| `west flash` | Zephyr unified flash command |
| `avrdude` | AVR flash programming |
| Segger Ozone | GUI debugger for J-Link targets |

**Production builds:** Debug symbols not included in `.bin`/`.hex`. Keep `.elf` file for post-mortem symbol resolution.
