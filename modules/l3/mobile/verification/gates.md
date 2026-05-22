# Mobile Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

---

## Gate 1: Permission Declaration Audit

**Check:** All declared permissions are used. All used permissions are declared. All iOS permissions have usage description strings.

**Method:**
```bash
# iOS: list all usage description keys
grep "UsageDescription" ios/<App>/Info.plist

# Android: list all permissions
grep "uses-permission" android/app/src/main/AndroidManifest.xml

# For each permission, verify a corresponding API call exists in source:
grep -rn "Camera\|Location\|Contacts\|Notification" src/
```

**Pass:** Every declared permission has a corresponding API usage. Every iOS permission has a non-empty `NSUsageDescription`. No permissions declared but unused.
**Fail:** Any declared permission with no usage. Any iOS permission without a usage description string.

---

## Gate 2: Secure Storage Audit

**Check:** No auth tokens, API keys, or sensitive data in AsyncStorage, NSUserDefaults, or SharedPreferences.

**Method:**
```bash
# Find AsyncStorage writes
grep -rn "AsyncStorage.setItem\|MMKV.set" src/
# Review each: must not store tokens, keys, passwords

# Find secure storage usage
grep -rn "SecureStore\|Keychain\|expo-secure-store" src/
# Verify auth tokens stored here
```

**Pass:** All sensitive data in secure storage. AsyncStorage contains only non-sensitive cached data.
**Fail:** Any auth token, API key, or password stored in AsyncStorage, NSUserDefaults, or SharedPreferences.

---

## Gate 3: HTTPS / ATS Configuration

**Check:** No HTTP endpoints. No certificate verification bypass. ATS not disabled.

**Method:**
```bash
# iOS: check for ATS exceptions
grep -A5 "NSAppTransportSecurity" ios/<App>/Info.plist
# Must not contain NSAllowsArbitraryLoads: true

# Android: check cleartext traffic
grep "cleartextTrafficPermitted" android/app/src/main/res/xml/network_security_config.xml
# Must not be true

# Check all API base URLs:
grep -rn "http://" src/
# Must be zero in production code (http:// in test fixtures is OK)
```

**Pass:** No NSAllowsArbitraryLoads. No cleartext traffic permitted. No http:// production endpoints.
**Fail:** Any ATS exception, cleartext enabled, or http:// production API endpoint.

---

## Gate 4: Android Exported Components

**Check:** All Android components have explicit `android:exported` attribute.

**Method:**
```bash
grep -n "Activity\|Service\|Receiver\|Provider" android/app/src/main/AndroidManifest.xml | grep -v "exported"
# Must return zero results — every component must have exported attribute
```

**Pass:** Every component has explicit `android:exported` attribute.
**Fail:** Any component missing `android:exported`.

---

## Gate 5: Startup Performance

**Check:** Cold start to interactive within declared budget.

**Method:**
```bash
# React Native (Detox):
it('launches within 3s', async () => {
  const startTime = Date.now()
  await device.launchApp({ newInstance: true })
  await waitFor(element(by.id('home-screen'))).toBeVisible().withTimeout(3000)
  expect(Date.now() - startTime).toBeLessThan(3000)
})

# Flutter:
# Use flutter_driver with timeline recording
```

**Pass:** App interactive within declared budget on target device (mid-range, not development machine).
**Fail:** Startup exceeds budget.

---

## Gate 6: Offline Behavior

**Check:** App handles no connectivity as declared in design-document.md for each feature.

**Method (manual test):**
1. Enable airplane mode
2. Launch app cold
3. Navigate to each feature declared with offline behavior
4. Verify declared behavior matches (cached state, error message, disabled state)
5. Restore connectivity
6. Verify app syncs/recovers correctly

**Pass:** Every feature behaves as declared in design-document.md when offline.
**Fail:** Any feature crashes, hangs, or shows undeclared behavior when offline.

---

## Gate 7: No Sensitive Data in Logs

**Check:** Production build logs do not contain tokens, keys, or PII.

**Method:**
```bash
# Build production release
# Launch and authenticate
# Capture logs:
# iOS: idevicesyslog or Console.app
# Android: adb logcat

# Search for sensitive patterns:
adb logcat | grep -i "token\|key\|password\|secret"
# Must return zero matches for actual values (grep for the keys is OK, not the values)
```

**Pass:** Zero sensitive values in production logs.
**Fail:** Any token, key, or password value visible in production log output.

---

## Gate 8: Code Signing Verified

**Check:** Builds are properly signed for their declared distribution method.

**Method:**
```bash
# iOS: verify signing identity
codesign -dv --verbose=4 build/ios/Runner.app

# Android: verify APK/AAB signature
jarsigner -verify -verbose -certs app-release.aab
# or:
apksigner verify --verbose app-release.apk
```

**Pass:** Valid signing identity. Distribution certificate for App Store builds. Keystore matches Play Console upload key.
**Fail:** Unsigned or wrong certificate type.

---

## Gate 9: Store Submission Readiness

**Check:** App passes pre-submission automated checks from each target store.

**Method:**
- iOS: Submit to TestFlight, check App Store Connect for automated scan findings
- Android: Submit to Play Internal Testing, check pre-launch report in Play Console

**Pass:** Zero App Store Connect automated errors. Zero Play Console critical pre-launch findings.
**Fail:** Any automated finding that would cause store rejection (missing privacy manifest, missing NSUsageDescription, targetSdk too old).

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Permission declaration audit | Yes |
| 2 | Secure storage audit | Yes |
| 3 | HTTPS / ATS configuration | Yes |
| 4 | Android exported components | Yes |
| 5 | Startup performance | Yes |
| 6 | Offline behavior | Yes |
| 7 | No sensitive data in logs | Yes |
| 8 | Code signing verified | Yes |
| 9 | Store submission readiness | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
