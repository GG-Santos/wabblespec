# Mobile Security — Threat Model

## Threat Surface

Mobile apps run on user-owned devices that may be compromised (jailbroken/rooted), operate on untrusted networks, and store sensitive data locally. The threat surface includes local storage, network traffic, the binary itself, and OS-level APIs.

1. **Insecure local storage** — sensitive data in AsyncStorage, SharedPreferences, or NSUserDefaults (all unencrypted)
2. **Network interception** — plaintext traffic or disabled certificate verification on untrusted networks
3. **Binary tampering** — app binary modified or repackaged by attacker
4. **OTA update hijack** — malicious OTA bundle injected via compromised CDN or MITM
5. **Exported component hijacking (Android)** — exported Activities/Services accessible to malicious apps
6. **Permission abuse** — app requests more permissions than needed; broad permissions are an attack surface
7. **Credential leakage via logs/backups** — tokens written to console or unencrypted device backup

---

## Threat 1: Insecure Local Storage

**Description:** Auth tokens, API keys, or personal data stored in `AsyncStorage` (React Native), `SharedPreferences` (Android), or `NSUserDefaults` (iOS) — all unencrypted. Any app with file system access on a rooted/jailbroken device can read them.

**Attack scenario:**
```javascript
// Vulnerable:
await AsyncStorage.setItem('authToken', token)  // stored unencrypted

// On jailbroken iOS: attacker reads ~/Library/Caches/<bundleID>/RCTAsyncLocalStorage_V1/
```

**Mitigations:**
- Auth tokens, passwords, and sensitive keys stored in OS keychain only
- iOS: `expo-secure-store` → Keychain Services. Android: `expo-secure-store` → Android Keystore
- AsyncStorage: non-sensitive data only (UI preferences, non-PII cache)
- Declare in design-document.md exactly what goes in AsyncStorage vs secure storage

---

## Threat 2: Network Interception

**Description:** App communicates over HTTP, or disables certificate verification, allowing MITM on untrusted networks (coffee shop WiFi, corporate proxy, attacker hotspot).

**Mitigations:**
- HTTPS only — no HTTP endpoints in production
- Certificate validation enabled (never `NSAllowsArbitraryLoads: true` or `TrustAllCerts`)
- Certificate pinning for high-security apps (banking, healthcare):
  - iOS: `NSPinnedDomains` in `NSAppTransportSecurity`
  - Android: `network_security_config.xml` with `<pin-set>`
  - React Native: `react-native-ssl-pinning`
- ATS (App Transport Security) enabled — no exceptions without justification in design-document

---

## Threat 3: Binary Tampering

**Description:** Attacker repackages the app with malicious code (bypassed paywalls, cheats, spyware) and distributes via unofficial channels. Users install the tampered APK.

**Mitigations:**
- Android: Enable Google Play App Signing (distribution key managed by Google)
- iOS: App Store signing prevents distribution of tampered binaries through App Store
- For sideloaded apps (Android): Runtime integrity check via `SafetyNet` / `Play Integrity API`
- Obfuscation (ProGuard/R8 for Android, bitcode for iOS) makes reverse engineering harder — but not a primary defense

---

## Threat 4: OTA Update Hijack

**Description:** Attacker intercepts or replaces an OTA JavaScript bundle (CodePush, EAS Update) with a malicious bundle that runs in the app's context with full network and storage access.

**Mitigations:**
- OTA updates served over HTTPS only
- Bundle integrity verified via code signing before application
- EAS Update: `expo-updates` verifies bundle signature using public key embedded in app
- CodePush: verifies bundle hash from manifest before applying
- Rollback capability: if OTA causes crashes, auto-rollback to previous bundle
- Declare OTA update policy in design-document.md; justify if OTA is used

---

## Threat 5: Exported Component Hijacking (Android)

**Description:** Android Activities, Services, or BroadcastReceivers with `android:exported="true"` can be invoked by any app on the device, potentially triggering privileged operations.

**Attack scenario:**
```
// Malicious app launches:
am start -n com.target.app/.DeepLinkActivity --data "target://admin/delete-all"
```

**Mitigations:**
- Set `android:exported="false"` on all components that do not need to be externally accessible
- For deep link Activities: validate the incoming URI before acting (`android:exported="true"` required)
- Use `Intent.setPackage()` for explicit intents to ensure correct recipient
- Validate all data from incoming Intents before processing

---

## Threat 6: Permission Abuse

**Description:** App requests broad permissions (location always, contacts, full photo library) beyond what features require. Over-permission is an attack surface: a compromised dependency can abuse those permissions.

**Mitigations:**
- Request minimum required permission level (location "when in use" not "always" unless background tracking justified)
- iOS: `PHPickerViewController` (no photo library permission needed for picking) instead of `NSPhotoLibraryUsageDescription`
- Request permissions at point of need, not on first launch
- Remove unused permissions before each release (audit against feature set)

---

## Threat 7: Credential Leakage via Logs/Backups

**Description:** Auth tokens appear in console logs (`console.log(authToken)`) that are accessible via `adb logcat` or Xcode console. Device backups include unencrypted app data.

**Mitigations:**
- Strip all logging in production builds that could include tokens, keys, or PII
- Use a logging library that scrubs sensitive patterns in production
- Android: set `android:allowBackup="false"` in AndroidManifest (or use encrypted backup)
- iOS: sensitive data excluded from iCloud backup via `NSURLIsExcludedFromBackupKey`
- Keychain data: not included in unencrypted iTunes backup by default (verify `kSecAttrAccessible` level)
