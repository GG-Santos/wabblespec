# Platform: IoT / Embedded

IoT device and embedded systems target. Activates when Recipe identifies firmware, embedded software, or an IoT device application as the primary build target.

**Skill:** `modules/l3/iot/SKILL.md`

## What makes IoT / Embedded different

| Concern | IoT / Embedded approach |
|---------|------------------------|
| Resource constraints | RAM, flash, CPU budget declared per target hardware |
| OTA updates | OTA update strategy declared — rollback mechanism required |
| Communication | Protocol stack declared (MQTT, CoAP, BLE, Zigbee, etc.) |
| Hardware faults | Watchdog timer strategy declared; hardware fault handlers declared |
| Power management | Sleep modes and wake strategies declared for battery-powered devices |
| Real-time | RTOS vs bare-metal declared; real-time deadlines declared if RTOS |
| Certification | FCC, CE, UL, or domain-specific certifications declared if applicable |

## Platform-specific spec sections

- Hardware target: MCU/SoC family, clock speed, RAM, flash — specific to target board
- Communication stack: protocol, transport, message format, QoS level
- Power profile: active/sleep current budgets; battery life target
- OTA strategy: update delivery, signature verification, rollback trigger, anti-brick mechanism
- Failure modes: what happens on comms loss, sensor failure, power brownout
- Security model: device authentication, firmware signing, secure boot

## Security controls loaded

- Firmware signing: OTA payloads must be signed and signature verified before flashing
- Secure boot: boot chain validation declared if platform supports it
- Credential storage: device credentials in hardware security element or protected flash region
- Network: TLS required for any network communication; certificate validation declared
- Physical access: JTAG/debug interface disabled in production builds
- Supply chain: firmware build is reproducible; build provenance declared

## Gateway interaction

IoT/Embedded targets typically activate:
- `gateway-security` — always (OTA, credentials, physical access surface)
- `gateway-engineering` — always (resource budgets, real-time constraints, fault handling)

IoT targets do not activate aesthetic, design, or experience gateways unless there is a companion app.
