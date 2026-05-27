# Build Toolchain — Mobile

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Framework

**Framework:** [ ] React Native  [ ] Flutter  [ ] Native iOS (Swift)  [ ] Native Android (Kotlin)  [ ] Other: ___
**Target platforms:** [ ] iOS  [ ] Android  [ ] both

---

## Build

**Build tool:** [ ] Xcode (iOS)  [ ] Android Studio / Gradle (Android)  [ ] `flutter build`  [ ] EAS Build (RN cloud)  [ ] fastlane  [ ] Other: ___
**Minimum OS versions:** iOS `___` / Android API `___`
**Code signing:** [ ] Apple Developer account (App Store Connect)  [ ] Android Keystore  [ ] Both

---

## Test runner

**Unit:** [ ] Jest (RN)  [ ] Flutter test  [ ] XCTest  [ ] JUnit5  [ ] Other: ___
**E2E / device:** [ ] Detox (RN)  [ ] Flutter integration_test  [ ] XCUITest  [ ] Espresso  [ ] Other: ___
**Coverage threshold:** 80% statement

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] Bitrise  [ ] CircleCI  [ ] Xcode Cloud  [ ] EAS Build  [ ] Other: ___

**Required CI gates:**
- [ ] Lint + type check
- [ ] Unit tests
- [ ] Build (iOS simulator + Android emulator)
- [ ] E2E smoke tests on emulator/simulator
- [ ] Bundle size check
- [ ] Dependency audit
- [ ] Crash-free rate gate (post-deploy, via monitoring)

---

## Distribution

**iOS:** [ ] App Store Connect  [ ] TestFlight (internal/external)  [ ] Enterprise distribution
**Android:** [ ] Google Play (internal track → production)  [ ] Direct APK  [ ] Enterprise MDM
**OTA updates:** [ ] Expo Updates (RN)  [ ] CodePush (RN)  [ ] None (store-only updates)
**OTA signing:** [ ] enforced  [ ] N/A

---

## Observability

**Crash reporting:** [ ] Firebase Crashlytics  [ ] Sentry  [ ] Bugsnag  [ ] Other: ___
**Analytics:** [ ] Firebase Analytics  [ ] Mixpanel  [ ] Amplitude  [ ] None  [ ] Other: ___
**Performance monitoring:** [ ] Firebase Performance  [ ] Datadog RUM Mobile  [ ] None  [ ] Other: ___

_(Monitor uses this to select mobile-appropriate output format — crash-free rate alerts, not p99 server latency.)_

---

## Notes

_Provisioning profile management, build variant naming, known CI quirks:_
