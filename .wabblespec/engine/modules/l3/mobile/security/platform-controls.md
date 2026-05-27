# Mobile Security — Platform Controls

These controls apply to all Mobile targets. Enforced by Verifier via `verification/gates.md`.

---

## Control 1: Secure Storage for Credentials

**Rule:** Auth tokens, API keys, passwords, and any sensitive identifiers must be stored in OS-managed secure storage only.

**Acceptable:**
- `expo-secure-store` (maps to iOS Keychain / Android Keystore)
- `react-native-keychain`
- iOS native: Keychain Services with appropriate `kSecAttrAccessible` level
- Android native: Android Keystore + EncryptedSharedPreferences

**Prohibited:**
- `AsyncStorage` / `MMKV` (unencrypted) for sensitive values
- `NSUserDefaults` / `SharedPreferences` for sensitive values
- Plain JSON files in documents directory

**Enforcement:** Grep for `AsyncStorage.setItem` / `SharedPreferences.putString` and review — tokens must not be stored this way.

---

## Control 2: HTTPS Only / ATS Enabled

**Rule:** All network communication must use HTTPS. No HTTP fallback. No certificate verification bypass.

**iOS enforcement:**
```xml
<!-- Info.plist — no NSAllowsArbitraryLoads -->
<key>NSAppTransportSecurity</key>
<dict>
  <!-- No NSAllowsArbitraryLoads key at all, or explicitly false -->
</dict>
```

**Android enforcement:**
```xml
<!-- network_security_config.xml -->
<network-security-config>
  <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```

**Prohibited:** `NSAllowsArbitraryLoads: true`, `cleartextTrafficPermitted="true"`, `TrustManager` that accepts all certs, `HostnameVerifier` that returns true for all hosts.

---

## Control 3: No Sensitive Data in Logs

**Rule:** Production builds must not log auth tokens, passwords, API keys, PII, or session identifiers.

**Enforcement:** Code review. Use a logging utility that:
- In development: logs everything
- In production: strips or hashes sensitive fields before logging

```typescript
// Safe logging pattern:
logger.debug('Auth response', { userId: response.userId })  // OK — not a token
// Not:
logger.debug('Auth response', { token: response.token })    // FAIL
```

---

## Control 4: Android Exported Component Minimization

**Rule:** All Android components (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) must explicitly declare `android:exported`.

**Default for components without intent filters:** `android:exported="false"`.
**Components with intent filters:** must explicitly set `android:exported="true"` and validate all incoming data.

**Enforcement:** `lint` check in CI (`MissingConstraints` or `AndroidManifest` lint rules). Every component must have explicit `exported` attribute.

---

## Control 5: Permission Minimization

**Rule:** Only permissions actively used by features in the current release are declared. Unused permissions are removed.

**iOS:** Remove any `NSUsageDescription` key whose feature is not yet implemented or has been removed.

**Android:** Remove any `uses-permission` that no API call requires.

**Process:** Before each release, audit: list all declared permissions → map each to a specific API call in source → remove any with no mapping.

---

## Control 6: Backup Exclusion for Sensitive Data

**Rule:** Sensitive data stored in files (not OS keychain) must be excluded from device backups.

**iOS:**
```swift
// Exclude file from iCloud backup:
var url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
url.appendPathComponent("sensitive-file")
try? url.setResourceValues({
  var values = URLResourceValues()
  values.isExcludedFromBackup = true
  return values
}())
```

**Android:**
```xml
<!-- AndroidManifest.xml -->
<application android:allowBackup="false" ... />
<!-- or for selective backup rules: android:fullBackupContent="@xml/backup_rules" -->
```

---

## Control 7: Deep Link Validation

**Rule:** Deep link handlers must validate all incoming URL parameters before acting.

**iOS (Universal Links):**
```swift
func application(_ app: UIApplication, open url: URL, ...) -> Bool {
  guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
        let id = components.queryItems?.first(where: { $0.name == "id" })?.value,
        isValidId(id) else {
    return false
  }
  // navigate with validated id
}
```

**Android:**
- Validate `getIntent().getData()` before use
- Use allowlist of supported paths — reject unknown paths
- Never execute arbitrary code from a deep link parameter

---

## Control 8: OTA Update Integrity (if OTA enabled)

**Rule:** OTA updates must be cryptographically verified before application.

**EAS Update:** Verify `expo-updates` is configured with code signing. Public key embedded in app binary.

**CodePush:** Verify bundle hash from signed manifest. Enable `CodePush.SyncStatus.CHECKING_FOR_UPDATE` logging.

**No unsigned OTA.** If signature verification cannot be configured, disable OTA and use store-only updates.
