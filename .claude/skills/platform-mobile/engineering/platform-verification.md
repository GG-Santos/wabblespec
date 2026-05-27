# Mobile Engineering — Platform Verification

How to run and interpret the mobile verification gates in `verification/gates.md`.

---

## Running All Gates

```bash
# TypeScript
npx tsc --noEmit

# Dart analysis
dart analyze

# Unit tests
npm test                      # RN Jest
flutter test                  # Flutter

# E2E tests
npx detox test --configuration ios.sim.release  # RN Detox
flutter drive --target=test_driver/app.dart     # Flutter

# iOS build
eas build --platform ios --profile production --non-interactive

# Android build
eas build --platform android --profile production --non-interactive
```

---

## Verifying Permissions

**iOS:** Check `ios/<AppName>/Info.plist` for all `NSUsageDescription` keys:
```bash
grep -c "UsageDescription" ios/<AppName>/Info.plist
# Count must match number of permission types declared in design-document
```

**Android:** Check `android/app/src/main/AndroidManifest.xml`:
```bash
grep "uses-permission" android/app/src/main/AndroidManifest.xml
# Compare against design-document.md permission table
```

---

## Verifying Secure Storage

```bash
# React Native: verify sensitive data uses expo-secure-store or react-native-keychain
grep -rn "AsyncStorage.setItem" src/
# Review each — auth tokens must NOT be in AsyncStorage

grep -rn "SecureStore\|Keychain" src/
# Verify auth tokens stored here
```

---

## Performance Measurement

### iOS (Xcode Instruments)
1. Open app in Xcode → Product → Profile → Time Profiler
2. Launch from cold state
3. Measure time from launch to first interactive frame
4. Identify heaviest functions in startup path

### Android (Android Studio Profiler)
1. Run → Profile → CPU Profiler
2. Record method trace from app launch
3. Identify slow initialization

### React Native specific
```bash
# Enable Flipper performance plugin for frame rate measurement
# Or use Perf Monitor: Shake device → Show Perf Monitor
```

---

## App Store Pre-Submission Checks

### iOS TestFlight
```bash
# Build and submit to TestFlight:
eas build --platform ios --profile production
eas submit --platform ios --latest

# Check for App Store Connect automated scan issues before human review:
# - Missing privacy manifest
# - Deprecated API usage
# - Missing NSUsageDescription keys
```

### Android Internal Testing
```bash
# Build AAB:
eas build --platform android --profile production

# Upload to Play Console → Internal Testing track
eas submit --platform android --latest

# Check pre-launch report in Play Console
# (Google runs automated tests on physical devices)
```

---

## Interpreting Gate Failures

**Gate FAIL — missing permission usage description (iOS):**
- Add the missing `NSXxxUsageDescription` key to `ios/<App>/Info.plist`
- String must explain WHY the app needs access (not just "we need camera access")

**Gate FAIL — sensitive data in AsyncStorage:**
- Identify all auth token / secret storage calls
- Replace with `expo-secure-store` or `react-native-keychain`
- Migrate existing stored values on next app launch

**Gate FAIL — startup over 3s:**
- Profile with Xcode Instruments / Android Studio
- Defer heavy initialization (analytics, crash reporting, feature flags) to after first frame
- Lazy-load non-critical screens

**Gate FAIL — 60fps not maintained in list:**
- Check for `renderItem` functions doing heavy computation — move to `useMemo`
- Add `keyExtractor` returning stable unique keys
- Add `getItemLayout` for fixed-height items
- Check for missing `useNativeDriver` on animations
