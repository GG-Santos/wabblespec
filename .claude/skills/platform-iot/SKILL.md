---
name: platform-iot
description: IoT/Embedded platform. Activates when Recipe detects firmware, embedded systems, RTOS targets, or connected device software. Loads IoT-specific spec templates focused on flash/RAM budget, cross-compilation, signed OTA updates, hardware abstraction, watchdog timers, and fail-safe behavior. Produces a materially different spec from Web or CLI — embedded failure modes (flash overflow, stack overflow, RTOS deadline miss, unsigned firmware) are absent from generic templates.
---

# Platform: IoT/Embedded

You are the IoT/Embedded platform layer. You activate when Recipe identifies firmware or embedded system targets.

## What this skill does

Loads IoT-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## When to use

Invoked per activators declared in `skill-rules.json`.

## What makes IoT/Embedded different from other targets

| Concern | IoT/Embedded | Desktop | Web |
|---|---|---|---|
| Memory | Flash: KB–MB; RAM: KB–MB. No virtual memory. | GB | Server-unlimited |
| Update | Signed OTA or physical flash — rollback required | Auto-updater | Server deploy |
| Failure mode | Brick, fire, safety hazard — not 500 error | Crash → restart | 5xx |
| Real-time | Hard deadlines — missed deadline = system failure | Soft | None |
| OS | Bare metal or RTOS (FreeRTOS, Zephyr, ThreadX) | Full OS | Browser |
| Security | Signed firmware, secure boot, hardware crypto | OS-enforced | Browser sandbox |
| Power | Battery-operated — every µA matters | Plugged in | Server power |
| Debug | JTAG/SWD, UART — no console | GUI debugger | Browser DevTools |
| Testing | Requires hardware target or emulator | x86 tests | Browser tests |

A spec without this context misses: flash size gate (code won't fit), RAM budget (stack overflow at runtime), watchdog timer (stuck code never recovers), signed OTA (firmware update is an attack vector), fail-safe behavior (what happens on power loss mid-write), and hardware abstraction layer design.

## Activation sequence

```
1. Recipe identifies IoT/Embedded target
2. Detect toolchain (ARM/RISC-V/ESP32/AVR) via skill-rules.json
3. Load all spec and engineering files
4. Write platform activation receipt
```

## Files loaded by this module

```
modules/l3/iot/
  spec-template/ engineering/ security/ verification/ schemas/
```

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `.wabblespec/engine/shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - .wabblespec/engine/shared/dev/frameworks/iot/core.md
  conditional_load: []
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
```

## Output contract

Writes a receipt to `.wabblespec/state/receipts/` on successful completion.
