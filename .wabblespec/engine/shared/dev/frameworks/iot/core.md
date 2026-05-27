# IoT / Embedded Framework Core

Cross-framework knowledge for firmware, embedded systems, and IoT device software. Loaded by Apply for every IoT platform task.

## Hardware target declaration (required)

Every IoT/Embedded spec must declare:
- **MCU/SoC**: specific family and part number (e.g., STM32F4, ESP32-S3, RP2040, nRF52840)
- **Clock speed**: MHz
- **Flash**: total KB/MB; available for firmware (subtract bootloader)
- **RAM**: total KB/MB; available for stack + heap + static
- **OS**: bare metal, FreeRTOS, Zephyr, ThreadX, or other
- **Toolchain**: GCC ARM, Clang, LLVM; version; SDK version

## Resource budget

```
Flash budget:
  Bootloader:      [KB]
  Application:     [KB — must fit in remaining]
  Reserved/OTA:    [KB — second slot for OTA if applicable]
  File system:     [KB — if SPIFFS/LittleFS used]
  Total:           [KB — sum ≤ flash size]

RAM budget:
  Stack (per task): [KB × number of tasks]
  Heap:             [KB]
  Static data:      [KB — BSS + data segments]
  DMA buffers:      [KB — if DMA used]
  Total:            [KB — sum ≤ RAM size]
```

Spec must include both budgets. Exceeding flash = linker error. Exceeding RAM = stack overflow or heap exhaustion (silent corruption).

## Real-time requirements

For RTOS-based systems, spec must declare per task:
- Task name and priority (higher number = higher priority in most RTOSes)
- Execution period (how often it runs)
- Worst-case execution time (WCET) — must leave headroom
- Deadline (when it must complete — usually period for periodic tasks)

Hard deadlines: missed = system failure (motor control, safety systems). Soft deadlines: missed = degraded performance.

## OTA update requirements

Every connected embedded device must declare OTA strategy:
- **Delivery**: HTTPS pull (device checks server), MQTT push, BLE OTA
- **Image format**: raw binary, ELF, or container (MCUboot)
- **Signature verification**: Ed25519 or RSA signature verified before flashing — mandatory
- **Rollback**: automatic rollback if new firmware fails health check
- **Anti-brick**: bootloader that verifies firmware before handing off; can always flash new image

```
Update flow:
  Server marks new firmware available
  → Device downloads to secondary slot
  → Device verifies signature
  → Device marks slot as pending
  → Device resets
  → Bootloader validates pending slot
  → If valid: swap and boot; if invalid: boot from original slot
```

## Watchdog timer

Every firmware must configure the watchdog:
```c
// Enable hardware watchdog: resets MCU if not fed within timeout
WDT_init(5000);  // 5 second timeout

// Feed in main loop (must happen before timeout)
WDT_feed();

// Do NOT disable watchdog in production
// Do NOT feed watchdog in ISR (masks starvation)
```

Spec must declare: watchdog timeout, where it is fed, and what happens if it fires.

## Communication stack

Spec must declare the full communication stack:
- **Protocol**: MQTT, CoAP, HTTP/HTTPS, BLE GATT, Zigbee, Z-Wave, LoRa, Matter
- **Transport**: TCP, UDP, BLE L2CAP
- **Encryption**: TLS 1.2+ for TCP/IP; declare cipher suite constraints for constrained MCUs
- **Authentication**: device certificates (mutual TLS), pre-shared keys, API keys
- **QoS**: MQTT QoS 0/1/2; retry behavior on disconnect

## Security requirements

- **Secure boot**: verify bootloader signature chain from hardware root of trust if platform supports it
- **Firmware signing**: all OTA payloads signed; key management declared (key rotation plan)
- **Credential storage**: device credentials in hardware security element (ATECC608, TPM) or protected flash region; never in external flash without encryption
- **Debug interface**: JTAG/SWD disabled in production builds (physically or via option bytes)
- **Physical tamper**: declare tamper detection if applicable (anti-tamper switches, epoxy encapsulation)

## Failure modes

Spec must declare behavior for:
- Communication loss: how long before device enters autonomous safe mode
- Sensor failure: how detected; what action taken; alert strategy
- Power brownout: flash write protection during power loss; state recovery on restart
- Memory exhaustion (heap): assert + log + safe reset vs limp mode
- Stack overflow: hardware stack overflow detection if MCU supports it

## Testing

- **Unit tests on host**: compile and test HAL-abstracted business logic on x86; fast feedback
- **Hardware-in-the-loop**: test on actual target hardware for timing, peripheral, and interrupt tests
- **Flash regression**: check firmware size in CI — alert if approaching budget
- **Power measurement**: measure current consumption in key modes; compare to budget
