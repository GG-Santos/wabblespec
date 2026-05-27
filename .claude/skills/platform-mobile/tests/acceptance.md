# Platform Mobile — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified Mobile as the primary target,
When platform-mobile is invoked,
Then it surfaces: "platform-mobile requires Recipe to have identified Mobile as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified Mobile as the primary target,
When platform-mobile activates,
Then the activation sequence completes in order: spec-template load → framework detection → engineering load → security load → Verifier gate registration → receipt write.

## Framework routing: React Native

Given `react-native` is in package.json,
When platform-mobile detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/mobile/react-native.md` is loaded.

## Framework routing: Flutter

Given `pubspec.yaml` contains a `flutter` dependency,
When platform-mobile detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/mobile/flutter.md` is loaded.

## Framework routing: native iOS

Given `.xcodeproj` or `Package.swift` with `UIKit`/`SwiftUI` is present,
When platform-mobile detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/mobile/swift-uikit.md` is loaded.

## Framework routing: native Android

Given `build.gradle` or `AndroidManifest.xml` is present,
When platform-mobile detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/mobile/kotlin-compose.md` is loaded.

## Mobile-specific concerns injected into spec

Given platform-mobile is active,
When spec context is assembled,
Then code signing is declared (iOS Provisioning Profile + cert; Android keystore).
Then OS permissions are declared with required usage description strings.
Then offline-first behavior is designed: declared how the app behaves without network.
Then OTA update strategy is declared (CodePush/EAS Update for React Native, Shorebird for Flutter, store update for native).
Then battery impact for background operations is addressed.
Then deep link handling (Universal Links for iOS, App Links for Android) is declared.
Then App Store Review Guidelines compliance is addressed in the spec.

## Permission usage strings declared

Given the spec includes permission requests (camera, location, notifications, contacts),
When spec context is assembled,
Then iOS Info.plist usage description strings are declared for each permission.
Then the spec notes that missing usage strings cause App Store rejection.

## Screen size variability addressed

Given platform-mobile is active,
When spec context is assembled,
Then layout handles phone, tablet, and foldable screen sizes.
Then no fixed-width layouts are declared as the only layout mode.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-mobile attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-mobile run,
Then platform-mobile does not omit code signing requirements.
Then platform-mobile does not omit offline behavior design.
Then platform-mobile does not treat mobile as identical to Web.

## Receipt fields

Given any successful platform-mobile activation,
Then a receipt is written to `.wabblespec/state/receipts/platform-mobile-<timestamp>.json`.
Then the receipt contains: platform, framework_detected, code_signing_declared, permissions_declared, offline_strategy_declared, ota_strategy_declared, gates_registered, capability_handoff.
