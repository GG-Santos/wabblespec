# IoT/Embedded Threat Model

> **Platform:** IoT/Embedded

---

## Threat Surface

IoT devices differ from servers: physical access is common, devices deploy to untrusted environments, firmware update is an attack vector, and flash memory may be readable without authentication.

---

## Threat 1: Unsigned Firmware Installation

**Description:** Attacker delivers malicious firmware via OTA channel or physical flash programming tool.

**Impact:** Full device compromise. Attacker controls all outputs, can exfiltrate credentials stored in flash, pivot to network.

**Attack vectors:**
- Intercept OTA download (MITM on unencrypted channel)
- Forge OTA metadata (version, hash)
- Physical access: connect JTAG/SWD, flash arbitrary image
- Supply chain: compromise firmware build or distribution

**Controls:**
- Ed25519 signature on every OTA image — device rejects unsigned or invalid-signature images
- HTTPS/TLS for OTA download transport
- Secure boot: bootloader verifies application signature before executing
- Disable JTAG/SWD in production fuses (if MCU supports it)
- Private signing key never on device, never in source control — HSM or CI secrets vault

**Residual risk:** Physical fuse bypass on some MCUs (requires lab equipment). Accept if device is not high-value target; document if it is.

---

## Threat 2: Credential Extraction from Flash

**Description:** Attacker reads flash memory directly (via JTAG, SPI clip, or chip decap) and extracts WiFi credentials, API keys, or device secrets.

**Impact:** Network compromise, cloud account access, mass device impersonation if shared key.

**Attack vectors:**
- JTAG/SWD readback (if not disabled in fuses)
- SPI flash clip (external flash chip)
- Chip decapsulation (advanced, expensive)

**Controls:**
- Per-device credentials (not shared key across fleet)
- Enable flash read protection (RDP Level 1/2 on STM32, Flash Encryption on ESP32)
- Store secrets in hardware secure element or eFuse where available
- WiFi PSK: use WPA3 or WPA2-Enterprise where possible
- API tokens: short-lived, scoped to device ID, revocable server-side

**Never store in plaintext flash:**
- WiFi PSK
- Device certificates / private keys
- Cloud API tokens
- OTA signing keys (these never go on device — only public key)

---

## Threat 3: Replay Attack on OTA or Commands

**Description:** Attacker captures a valid OTA image or command packet and replays it later — potentially downgrading firmware to a vulnerable version or re-executing a command.

**Impact:** Firmware downgrade (reintroducing patched vulnerabilities), duplicate command execution.

**Attack vectors:**
- Capture OTA metadata + image, replay to trigger install of old version
- Capture MQTT command, replay to device

**Controls:**
- OTA: enforce monotonic version counter — device rejects images with version ≤ current version
- Commands: include sequence number or timestamp + HMAC; device rejects replays
- OTA version stored in eFuse (immutable) or NVS with integrity check

---

## Threat 4: Physical Tampering — Debug Interface Exploitation

**Description:** Attacker connects JTAG/SWD/UART to running device and reads memory, halts execution, or injects code via debugger.

**Impact:** Memory dump of running state (credentials, keys), arbitrary code execution, circumventing secure boot.

**Attack vectors:**
- Exposed debug header (JTAG 10-pin, SWD 4-pin, UART TX/RX pads)
- Unlocked JTAG in production build

**Controls:**
- Disable JTAG/SWD via MCU fuses before shipping (STM32: RDP Level 2, ESP32: JTAG disable eFuse)
- UART: disable in production build (`#ifdef PRODUCTION_BUILD`)
- Remove debug pads from production PCB (or fill with solder)
- Document: once fuses blown, device cannot be recovered via JTAG — accept or reject

---

## Threat 5: Network — MQTT/HTTP Command Injection

**Description:** Attacker publishes malicious MQTT messages to device's subscribed topics, or sends crafted HTTP responses from a rogue server.

**Impact:** Unauthorized command execution, device misconfiguration, OTA trigger pointing to malicious server.

**Attack vectors:**
- Compromised MQTT broker
- DNS spoofing pointing device to attacker-controlled server
- Malformed payload exploiting parser bugs (buffer overflow, format string)

**Controls:**
- Mutual TLS (mTLS): device authenticates server certificate + server authenticates device certificate
- Message payload validation: length check before parse, reject oversized payloads
- Command allowlist: device only executes known-valid commands
- OTA URL pinned or validated against trusted domain — device rejects unexpected OTA servers
- No `sprintf` with untrusted input — use `snprintf` with explicit bounds

---

## Threat 6: Denial of Service — Crash Loop / Watchdog Abuse

**Description:** Attacker sends inputs that crash the device or cause it to enter a crash loop, making it unavailable.

**Impact:** Device unavailable, possible data loss, watchdog reset counter exhaustion.

**Attack vectors:**
- Malformed MQTT payload causing buffer overflow → crash
- High-frequency requests exhausting heap or task queue
- OTA trigger causing repeated failed boot → rollback loop

**Controls:**
- Input validation at network boundary — reject malformed payloads before processing
- Queue size bounded — drop oldest when full (never block ISR on full queue)
- Boot loop detection: if `boot_count` increments > threshold without successful run, enter safe mode
- Exponential backoff on reconnect — don't flood network on failure

---

## Threat 7: Supply Chain — Compromised Toolchain or Dependencies

**Description:** Build toolchain, SDK, or third-party library is compromised, inserting malicious code into firmware.

**Impact:** Backdoored firmware ships to all devices.

**Attack vectors:**
- Malicious package in package manager (esp-idf components, PlatformIO libraries)
- Compromised CI runner
- Trojanized compiler (rare but documented: XcodeGhost, SolarWinds)

**Controls:**
- Pin all dependencies to exact versions with hash verification
- Use lock files (IDF component lock, west.yml with SHA pins)
- CI: verify toolchain hash before build
- Code review for any dependency addition or version bump
- Minimal dependencies — every library is an attack surface

---

## Assets Ranked by Value

| Asset | Value | Primary threat |
|---|---|---|
| OTA signing private key | Critical | Supply chain compromise |
| Device certificate / private key | High | Flash extraction |
| WiFi PSK | High | Flash extraction |
| Cloud API tokens | High | Flash extraction |
| Firmware integrity | High | Unsigned firmware |
| Device availability | Medium | Crash loop / DoS |
| Telemetry data | Low–Medium | Network intercept |
