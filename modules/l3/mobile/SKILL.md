---
name: platform-mobile
description: Mobile platform. Activates when Recipe detects an iOS, Android, React Native, or Flutter application target. Loads mobile spec templates, engineering rules, security controls, and verification gates specific to mobile concerns. Produces a materially different spec from Web or Desktop — focused on code signing, app store review, OTA updates, OS permission model, battery/network constraints, and offline-first design.
---

# Platform: Mobile

You are the Mobile platform layer. You activate when Recipe identifies a mobile application target and load the constraints, templates, and verification gates specific to that environment.

## What this skill does

Loads mobile-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## When to activate

Recipe must have already run and identified Mobile as the primary target. Activation signals in `skill-rules.json`.

## What makes Mobile different from other targets

| Concern | Mobile | Desktop | Web |
|---|---|---|---|
| Distribution | App Store / Google Play review process | Direct installer / store | CDN deploy |
| Code signing | Required (iOS Provisioning Profile + cert; Android keystore) | Required | N/A |
| OTA updates | React Native: CodePush/EAS Update; Flutter: Shorebird; native: store update only | Auto-updater | Server deploy |
| OS permissions | User-granted at runtime (camera, location, notifications, contacts) | OS prompt at first use | Browser prompt |
| Network | Unreliable, cellular, metered — offline-first required | Assumed connected | Assumed connected |
| Battery | Every background operation costs battery | N/A | N/A |
| Screen sizes | Variable (phone, tablet, foldable) | Variable but less extreme | Responsive |
| Deep links | Universal Links (iOS) / App Links (Android) | URL scheme | URL |
| Background | Severely restricted — declare background modes explicitly | Unrestricted | Limited |
| App binary size | Store limits (4GB iOS, no hard Android limit but user experience degrades) | N/A | Bundle size |

A spec written without this platform context will miss: provisioning profile setup, App Store Review Guidelines compliance, background mode declarations, permission usage description strings (iOS requires these in Info.plist or App Store rejection), offline behavior design, cellular data sensitivity, and keystore management for Android releases.

## Activation sequence

```
1. Recipe identifies Mobile target and signals platform-mobile activation
2. Load spec-template variant
3. Detect framework (React Native/Flutter/native iOS/native Android) via skill-rules.json signals
4. Load engineering/build-toolchain.md and engineering/performance-budgets.md
5. Load security/threat-model.md and security/platform-controls.md
6. Register verification/gates.md with Verifier
7. Write platform activation receipt
```

## Framework routing

| Detected signal | Framework |
|---|---|
| `react-native` in package.json | React Native |
| `pubspec.yaml` with `flutter` dependency | Flutter |
| `.xcodeproj` or `Package.swift` with `UIKit`/`SwiftUI` | Native iOS |
| `build.gradle` or `AndroidManifest.xml` | Native Android |
| `capacitor.config.ts` or `capacitor.config.json` | Capacitor (web hybrid) |

## Output contract

**Platform activation receipt** (`.wabblespec/receipts/platform-mobile-{timestamp}.json`)

## Files loaded by this module

```
modules/l3/mobile/
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```
