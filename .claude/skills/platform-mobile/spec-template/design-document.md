# Mobile Design Document Template (P1)

> **Platform:** Mobile
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-mobile activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this mobile app does, who uses it, which platforms (iOS/Android/both) it targets, and the primary workflow it enables.

---

## Framework [REQUIRED]

[ ] React Native (with Expo managed workflow)
[ ] React Native (bare workflow)
[ ] Flutter
[ ] Native iOS (Swift/SwiftUI)
[ ] Native Android (Kotlin/Jetpack Compose)
[ ] Capacitor (web hybrid)
[ ] Other: ___

**Minimum OS versions:**
- iOS: ___ (check App Store Connect requirements annually)
- Android: API level ___ (Android ___)

---

## OS Permissions [REQUIRED]

Each permission must have a usage description string. iOS rejects apps at review if `NSUsageDescription` key is missing for any requested permission.

| Permission | iOS Info.plist Key | Android Permission | Usage description (shown to user) |
|---|---|---|---|
| Camera | `NSCameraUsageDescription` | `CAMERA` | "Used to scan QR codes" |
| Location (when in use) | `NSLocationWhenInUseUsageDescription` | `ACCESS_FINE_LOCATION` | "Used to show nearby items" |
| Notifications | N/A (requested via UNUserNotificationCenter) | `POST_NOTIFICATIONS` (Android 13+) | "For order status updates" |
| [list all] | | | |

**Permission request timing:** Request at the point of need (not on first launch). User must understand why before the system prompt appears.

**Permission denial handling:** Document degraded behavior for each denied permission.

---

## Code Signing Strategy [REQUIRED]

### iOS
- **Bundle ID:** `com.<org>.<app>`
- **Provisioning profile type:** [ ] App Store Distribution [ ] Ad Hoc [ ] Enterprise
- **Certificate type:** Apple Distribution
- **Managed by:** [ ] Xcode automatic [ ] Fastlane Match [ ] Manual
- **Team ID:** (in secrets, not committed)

### Android
- **Application ID:** `com.<org>.<app>`
- **Keystore:** Generated once, stored in CI secrets (never committed to repo)
- **Key alias:** ___
- **Managed by:** [ ] Google Play App Signing [ ] Self-managed

---

## OTA Update Strategy [REQUIRED]

| Property | Decision |
|---|---|
| OTA mechanism | [ ] EAS Update (Expo) [ ] CodePush (AppCenter) [ ] Shorebird (Flutter) [ ] None — store updates only |
| What can be OTA updated | JS bundle only (RN/Flutter) — native code requires store update |
| Rollback capability | [ ] Yes [ ] No |
| Update channel | [ ] production [ ] staging [ ] beta |
| Update check frequency | On app foreground |
| User visibility | [ ] Silent (JS only) [ ] Prompted |

**Note:** OTA updates that change native code require a store release. OTA is for JS/Dart-only changes.

---

## Offline Behavior [REQUIRED]

This must be declared. "We'll handle it later" is not acceptable — offline UX shapes architecture.

| Feature | Offline behavior |
|---|---|
| [Core feature 1] | [ ] Works offline [ ] Cached last state [ ] Disabled with message [ ] Requires connectivity |
| [Core feature 2] | [ ] Works offline [ ] Cached last state [ ] Disabled with message [ ] Requires connectivity |

**Connectivity detection:** App detects offline state via `NetInfo` (RN) / `Connectivity` (Flutter) / `NWPathMonitor` (iOS) and responds appropriately.

**Sync strategy:** When connectivity restored: [ ] Automatic background sync [ ] User-triggered sync [ ] N/A

---

## App Store Configuration [REQUIRED]

**iOS (App Store Connect):**
- App name: ___ (30 char max)
- Subtitle: ___ (30 char max)
- Category: Primary: ___ Secondary: ___
- Age rating: ___
- Privacy policy URL: Required for apps with user accounts or data collection
- App privacy labels: Document what data is collected and how used

**Android (Google Play Console):**
- App name: ___ (50 char max)
- Category: ___
- Content rating: ___
- Data safety section: Document what data is collected, shared, encrypted

---

## GWT Acceptance Scenarios (Mobile-specific)

```
Given: the app is launched with no network connectivity
When: the user navigates to a feature declared as "requires connectivity"
Then: the app shows a clear offline indicator
      AND the feature is disabled with an explanatory message
      AND the app does not crash or show an error dialog

Given: the app requests a sensitive OS permission (camera, location)
When: the user denies the permission
Then: the app does not crash
      AND the user sees a clear explanation of what functionality is unavailable
      AND the app does not re-request the permission immediately

Given: an OTA update is available (if OTA enabled)
When: the app is foregrounded
Then: the update is downloaded in background without affecting current session
      AND the update applies on next cold launch
      AND a failed update does not break the current version

Given: the app is backgrounded for more than 5 minutes
When: the user returns to the app
Then: the app resumes to the correct screen (not the home screen)
      AND no authentication session is unexpectedly invalidated
      AND no data loss occurred during backgrounding
```

---

## Open Questions

List unresolved design decisions. Specify blocks receipt until REQUIRED sections complete.
