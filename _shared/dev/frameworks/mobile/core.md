# Mobile Framework Core

Cross-framework knowledge for iOS, Android, React Native, and Flutter targets. Loaded by Apply for every Mobile platform task.

## Mobile-first constraints

Every mobile spec must declare:
- **Target OS versions**: minimum iOS version, minimum Android API level
- **Network assumption**: unreliable cellular; offline-first design required
- **Battery**: background tasks must justify their power cost
- **Screen sizes**: smallest and largest supported screen; how layout adapts
- **Permissions**: every OS permission requested, with UX flow for the ask

## Distribution requirements

### iOS

- **Provisioning**: Development + Distribution profiles declared; code signing certificate type
- **App Store Review**: all App Store Review Guidelines addressed for the feature set
- **Info.plist**: usage description strings for every permission (camera, location, microphone, contacts, health, photos) — missing strings cause rejection
- **Background modes**: declared in Capabilities; background app refresh, location updates, push notifications, background fetch — each requires justification

### Android

- **Keystore**: signing keystore managed (Google Play App Signing recommended)
- **Permissions**: declared in AndroidManifest.xml; runtime permission flow for dangerous permissions
- **Target SDK**: must target current SDK level (Google Play requirement); declare `minSdkVersion` and `targetSdkVersion`
- **ProGuard/R8**: declare obfuscation rules; ensure they don't break reflection-based code

## Navigation patterns

Spec must declare navigation architecture:
- **Tab bar** (bottom tabs): primary navigation for peer sections
- **Stack** (push/pop): drill-down within a section
- **Modal** (overlay): transient tasks, confirmations, sheet presentations
- **Deep link**: URI scheme or Universal Link/App Link — declare all deep link routes and how they map to screens

## Offline-first design

For each data type, spec must declare:
- **Cache strategy**: which data is cached; TTL; eviction policy
- **Optimistic updates**: for mutations (show result immediately, roll back on failure)
- **Sync**: how local changes sync when connectivity returns; conflict resolution
- **Offline state**: what the user sees and can do when offline

## Performance budget

| Metric | Target |
|---|---|
| App launch (cold start) | < 400ms to interactive (iOS) / < 1s (Android) |
| Frame rate | 60fps steady state; 120fps on ProMotion/high-refresh displays if declared |
| Memory | Declare peak memory budget; crash on low memory is unacceptable |
| Binary size | Declare size budget; App Store thin-provisioning helps but large assets still matter |
| Battery | Declare background task frequency and expected power impact |

## Security requirements

- **Keychain/Keystore**: all secrets (tokens, API keys, credentials) stored in OS secure storage — never in UserDefaults/SharedPreferences or files
- **Certificate pinning**: for high-security apps (banking, healthcare) — declare policy and pin rotation strategy
- **Biometric auth**: use OS biometric APIs; never re-implement biometric logic
- **Jailbreak/root detection**: declare if required; know its limitations (detectable but not foolproof)
- **Sensitive data**: clear from memory when app backgrounds; do not log PII; screenshot prevention for sensitive screens

## Testing

- Unit tests: business logic, use cases, view models
- UI tests: XCUITest (iOS) / Espresso (Android) / Detox (RN) / integration_test (Flutter) for critical flows
- Device testing: declare which device/OS combinations are tested (not just simulator)
