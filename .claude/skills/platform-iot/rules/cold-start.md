# Cold-Start Behavior — Platform IoT/Embedded

Defines how the IoT/embedded platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `_shared/dev/frameworks/iot/core.md` missing.
Detection: File read returns 404.
Action: Log warning. Apply continues without hardware target declaration, resource budget tables, and OTA strategy rules. Decompose proceeds.
Do NOT: Fail the session.

## Absent: security reference files

Condition: `modules/l3/iot/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security uses generic controls. Firmware signing and JTAG-disabled-in-production requirements remain enforced as platform invariants.

## Absent: spec-template files

Condition: `modules/l3/iot/spec-template/design-document.md` absent.
Action: Specify uses generic structure.

## Default state on cold start

| Field | Default |
|---|---|
| `mcu` | Not declared — Specify must declare MCU model, clock speed, flash, RAM |
| `rtos` | Not declared — Specify must declare RTOS or bare-metal decision |
| `flash_budget` | Not declared — Specify must declare (code must not exceed 80% flash utilization) |
| `ram_budget` | Not declared — Specify must declare; no dynamic allocation in hard real-time paths |
| `ota_strategy` | Not declared — required for any deployed device; Specify must elicit |
| `firmware_signing` | Required — unsigned firmware is a BLOCK |
| `jtag_production` | Disabled in production builds — enforced invariant |
| `credential_storage` | Hardware secure element or flash with encryption — plaintext credential storage is a BLOCK |
| `communication_stack` | Not declared — Specify must declare (MQTT / CoAP / HTTP / BLE / LoRa) |
| `watchdog` | Required — Specify must declare watchdog timeout and recovery behavior |

Firmware signing, JTAG disabled, and watchdog requirement are platform invariants — enforced even without framework files.
