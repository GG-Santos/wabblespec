# Mobile Engineering — Build Toolchain

## React Native / Expo

**Preferred:** Expo with EAS Build (cloud build service — no local Xcode/Android Studio required for CI).

### EAS Build config (`eas.json`)
```json
{
  "cli": { "version": ">= 7.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": false }
    },
    "production": {
      "ios": { "resourceClass": "m-medium" },
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "ios": { "appleId": "...", "ascAppId": "..." },
      "android": { "serviceAccountKeyPath": "./google-service-account.json" }
    }
  }
}
```

### Build commands
```bash
# Local development
npx expo start

# EAS cloud build
eas build --platform ios --profile production
eas build --platform android --profile production

# Submit to stores
eas submit --platform ios --latest
eas submit --platform android --latest

# OTA update
eas update --branch production --message "Fix login crash"
```

---

## Flutter

### Build commands
```bash
# iOS
flutter build ipa --release

# Android
flutter build appbundle --release

# Run tests
flutter test
flutter drive --target=test_driver/app.dart
```

### Fastlane (iOS signing automation)
```ruby
# Fastfile
lane :build_ios do
  match(type: "appstore")
  build_app(scheme: "Runner", export_method: "app-store")
end
```

---

## iOS Build Pipeline

**Toolchain:** Xcode (macOS runner required). Fastlane + Match recommended for certificate management.

**Fastlane Match:** Stores certificates and provisioning profiles encrypted in a git repo. All team members and CI use Match to sync signing identities.

```bash
# Initialize Match (once):
fastlane match init

# Sync certificates:
fastlane match appstore

# Build + sign:
fastlane run build_app \
  scheme:"<Scheme>" \
  export_method:"app-store"
```

**App Store submission:** Fastlane Deliver or Xcode Organizer or Transporter.

---

## Android Build Pipeline

**Keystore:** Generated once. Store in a secure location. **Loss = cannot update app on Play Store.**

```bash
# Generate keystore (one time):
keytool -genkey -v -keystore release.keystore \
  -alias <alias> -keyalg RSA -keysize 2048 -validity 10000

# Build signed AAB:
cd android && ./gradlew bundleRelease

# Or via Gradle signing config in build.gradle:
signingConfigs {
  release {
    storeFile file(System.getenv("KEYSTORE_PATH"))
    storePassword System.getenv("KEYSTORE_PASSWORD")
    keyAlias System.getenv("KEY_ALIAS")
    keyPassword System.getenv("KEY_PASSWORD")
  }
}
```

**Never commit keystore or passwords.** CI secrets only.

**Google Play App Signing:** Recommended — Google manages the final signing key. Upload key is different from distribution key.

---

## CI Build Matrix

iOS and Android require separate runners:

```yaml
jobs:
  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: fastlane match appstore --readonly
      - run: fastlane build_ios

  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '17' }
      - run: npm ci
      - run: cd android && ./gradlew bundleRelease
        env:
          KEYSTORE_PATH: ${{ secrets.KEYSTORE_PATH }}
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
```

---

## CI Build Gates

Before any store submission:
1. TypeScript: `tsc --noEmit` / Dart analysis: `dart analyze` — zero errors
2. Unit tests pass
3. E2E tests pass (Detox for RN, integration_test for Flutter)
4. iOS build signs without error
5. Android build signs without error (keystore valid)
6. Bundle size within declared budget
7. `expo-doctor` / `flutter doctor` — no blocking issues
8. Accessibility scan (if tooling available)
