# IoT/Embedded Platform Security Controls

> **Platform:** IoT/Embedded

---

## Control 1: Signed OTA — Mandatory

Every OTA image must be signed with Ed25519. Device rejects unsigned or invalid-signature images.

```c
// Verification before any flash write — no exceptions
ota_status_t ota_begin_update(const uint8_t *image, size_t len, const uint8_t *sig) {
    if (ota_verify_image(image, len, sig) != OTA_OK) {
        log_error("OTA rejected: invalid signature");
        return OTA_ERR_INVALID_SIGNATURE;
        // Do NOT proceed to flash write
    }
    return ota_write_to_staging_bank(image, len);
}
```

**Key management:**
- Public key burned to device flash at manufacturing — immutable
- Private key: HSM or CI secrets vault — never on device, never in source control
- Key rotation: requires new devices to carry new public key; old devices need coordinated update

**Enforcement:** CI pipeline refuses to produce unsigned binaries. Signing happens as final build step with key from vault.

---

## Control 2: Secure Boot

Bootloader verifies application signature before transferring execution. Unsigned or tampered application does not run.

```
Boot sequence:
  1. ROM bootloader (immutable, in chip ROM)
  2. Secondary bootloader (signed, verified by ROM)
  3. Application (signed, verified by secondary bootloader)

If any verification fails:
  → Do NOT execute the image
  → Log failure to persistent storage
  → Either halt or revert to known-good bank
```

**Platform-specific:**
- ESP32: Enable Secure Boot V2 in sdkconfig (`CONFIG_SECURE_BOOT=y`, `CONFIG_SECURE_BOOT_V2_ENABLED=y`)
- STM32: Use SBSFU (Secure Boot and Secure Firmware Update) or TF-M
- nRF52: Use MCUboot with signature verification enabled

**Once enabled, cannot be disabled without hardware access to fuses.** Enable in production only after thorough testing.

---

## Control 3: Flash Encryption

Encrypts flash contents so physical flash dump yields ciphertext, not plaintext credentials or code.

**ESP32:** `CONFIG_FLASH_ENCRYPTION_ENABLED=y` — AES-256 XTS, key in eFuse
**STM32:** RDP Level 1 (read protection) — prevents JTAG readback of flash
**nRF52:** `CONFIG_SOC_FLASH_NRF_RRAM` + ARM TrustZone partition

**What this protects:** WiFi PSK, device certificates, firmware IP
**What this does NOT protect:** Data in RAM (visible via JTAG if JTAG not disabled), side-channel attacks

---

## Control 4: Disable Debug Interfaces in Production

JTAG/SWD/UART must be disabled before shipping.

```c
// Compile-time disable of UART logging:
#ifdef PRODUCTION_BUILD
    #define log_debug(...)  // expands to nothing
    #define log_info(...)   // expands to nothing
    // log_error() → NVS only, no UART output
#endif
```

**Fuse-based JTAG disable (permanent):**
- ESP32: `espefuse.py burn_efuse JTAG_DISABLE` — irreversible
- STM32: Set RDP to Level 2 — irreversible, disables JTAG permanently
- nRF52: `APPROTECT` register

**Process:** Test with debug enabled → final production flash → burn fuses → ship. Burned fuses cannot be undone.

---

## Control 5: Per-Device Credentials

No shared secrets across device fleet.

```
Each device gets at manufacturing:
  - Unique device_id (chip serial or provisioned UUID)
  - Unique device certificate (issued by device CA)
  - Unique device private key (generated on-device or provisioned via secure channel)
  
Server validates:
  - Certificate chain → device CA → root CA
  - device_id in certificate matches registered device
  - Certificate not revoked (CRL or OCSP)
```

**Why per-device:** Single compromised device does not expose entire fleet. Revoke one certificate = one device offline, not all.

**Storage:** Device private key in hardware secure element (ATECC608, SE050) where available. If no secure element: flash encryption + RDP.

---

## Control 6: TLS for All Network Communication

No plaintext network traffic from production devices.

```c
// MQTT with TLS (ESP-IDF):
esp_mqtt_client_config_t mqtt_cfg = {
    .broker.address.uri = "mqtts://broker.example.com:8883",
    .broker.verification.certificate = server_root_ca_pem,
    .credentials.authentication.certificate = device_cert_pem,
    .credentials.authentication.key = device_private_key_pem,
};
```

**Certificate pinning:** Pin server certificate or public key — reject connections to unexpected servers even if certificate is CA-signed.

**No `ESP_MQTT_TRANSPORT_TCP` in production.** No `verify_mode = SSL_VERIFY_NONE`.

---

## Control 7: Input Validation at Network Boundary

All data received from network treated as untrusted.

```c
// Before parsing any network payload:
int handle_mqtt_message(const uint8_t *payload, size_t len) {
    // 1. Length check first — before any parsing
    if (len > MAX_PAYLOAD_SIZE) {
        log_error("Payload too large: %zu bytes", len);
        return ERR_INVALID_INPUT;
    }
    // 2. Validate structure (JSON schema, protobuf, or manual field checks)
    // 3. Validate value ranges
    // 4. Only then process
}
```

**No `sprintf` with untrusted input.** Use `snprintf` with explicit bounds everywhere.
**No `strcpy`, `strcat`, `gets`.** Use `strlcpy`, `strlcat`, or bounded equivalents.

---

## Control 8: No Credentials in Source Control

```
Prohibited in repository:
  - WiFi PSK (even test network)
  - MQTT broker passwords
  - OTA signing private key
  - Device certificates or private keys
  - Cloud API tokens
  - Any secret used by production devices

Allowed in repository:
  - OTA public key (burned to device — not secret)
  - Server CA certificate (public)
  - Test certificates for CI emulator (clearly marked test-only)
```

**CI secrets:** Use GitHub Actions secrets, GitLab CI variables, or Vault. Reference by environment variable in build scripts. Never echo or log secret values.

---

## Control 9: Monotonic Version Counter (Anti-Rollback)

Prevents downgrade attacks that reintroduce patched vulnerabilities.

```c
// On successful boot of new firmware:
uint32_t committed_version = nvs_read_uint32("min_fw_version");
uint32_t current_version = FW_VERSION_INT;  // from build system

if (current_version > committed_version) {
    nvs_write_uint32("min_fw_version", current_version);
}

// In OTA acceptance check:
if (new_image_version <= committed_version) {
    log_error("OTA rejected: version %u <= committed minimum %u",
              new_image_version, committed_version);
    return OTA_ERR_VERSION_ROLLBACK;
}
```

**Stronger:** Use eFuse-based anti-rollback counter (ESP32 supports this). eFuse writes are irreversible — version can only increase.

---

## Non-Negotiable Rules

These apply to every IoT firmware built under this platform:

1. Unsigned OTA images are never applied — no exceptions, no override flag
2. Production build has UART logging disabled
3. Watchdog enabled in all production builds
4. No plaintext network traffic (no HTTP, no unencrypted MQTT)
5. No shared secrets across device fleet
6. OTA signing private key never touches device flash or source repository
7. Input length validated before parse — always
8. No dynamic memory in ISRs or time-critical paths
