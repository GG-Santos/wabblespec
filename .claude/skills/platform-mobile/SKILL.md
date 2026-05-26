---
name: platform-mobile
description: Mobile platform. Activates when Recipe detects an iOS, Android, React Native, or Flutter application target. Loads mobile spec templates, engineering rules, security controls, and verification gates specific to mobile concerns. Produces a materially different spec from Web or Desktop — focused on code signing, app store review, OTA updates, OS permission model, battery/network constraints, and offline-first design.
---

# Platform: Mobile

You are the Mobile platform layer. You activate when Recipe identifies a mobile application target and load the constraints, templates, and verification gates specific to that environment.

## What this skill does

Loads mobile-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## When to use

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

## Design phase sequence

```
P0: product-concept.md           ← Pillars, platform decision, connectivity stance (REQUIRED before P1)
P1: design-document.md           ← Product requirements, user stories, OS permission declarations
    ui-spec.md                   ← Screen inventory, navigation pattern, touch targets (load with P1)
P2: systems-design.md            ← Architecture, state management, offline strategy
    framework-specific/          ← Load matched framework doc (conditional on detection)
      react-native.md            ← If react-native in package.json
      flutter.md                 ← If pubspec.yaml with flutter
      swift-uikit.md             ← If .xcodeproj or Package.swift detected
      kotlin-compose.md          ← If build.gradle or AndroidManifest.xml detected
P3: technical-spec.md            ← Implementation spec, GWT acceptance scenarios
```

**Invariant:** product-concept.md pillars and platform decision must be declared before Specify receipt. ui-spec.md must be loaded alongside P1 — mobile UI architecture decisions (navigation pattern, safe areas, touch targets) cannot be deferred to implementation.

## Framework routing

| Detected signal | Framework |
|---|---|
| `react-native` in package.json | React Native |
| `pubspec.yaml` with `flutter` dependency | Flutter |
| `.xcodeproj` or `Package.swift` with `UIKit`/`SwiftUI` | Native iOS |
| `build.gradle` or `AndroidManifest.xml` | Native Android |
| `capacitor.config.ts` or `capacitor.config.json` | Capacitor (web hybrid) |

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `_shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - _shared/dev/frameworks/mobile/core.md
    - modules/l3/mobile/spec-template/product-concept.md
    - modules/l3/mobile/spec-template/ui-spec.md
  conditional_load:
    - signal: "react-native in package.json"
      load: modules/l3/mobile/spec-template/framework-specific/react-native.md
    - signal: "pubspec.yaml with flutter"
      load: modules/l3/mobile/spec-template/framework-specific/flutter.md
    - signal: ".xcodeproj or Package.swift"
      load: modules/l3/mobile/spec-template/framework-specific/swift-uikit.md
    - signal: "build.gradle or AndroidManifest.xml"
      load: modules/l3/mobile/spec-template/framework-specific/kotlin-compose.md
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
    - gateway-experience/references/     # if experience gateway active
    - gateway-design/references/         # if design gateway active
    - gateway-aesthetic/references/      # if aesthetic gateway active
```

## Output contract

**Platform activation receipt** (`.wabblespec/receipts/platform-mobile-{timestamp}.json`)

## Files loaded by this module

**Always loaded:**
```
modules/l3/mobile/
  spec-template/product-concept.md        ← P0 (always)
  spec-template/design-document.md
  spec-template/ui-spec.md                ← loaded with P1
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  engineering/qa-pipeline.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```

**Conditionally loaded (framework-specific):**
```
modules/l3/mobile/spec-template/framework-specific/
  react-native.md    ← if react-native in package.json
  flutter.md         ← if pubspec.yaml with flutter dependency
  swift-uikit.md     ← if .xcodeproj or Package.swift detected
  kotlin-compose.md  ← if build.gradle or AndroidManifest.xml detected
```
