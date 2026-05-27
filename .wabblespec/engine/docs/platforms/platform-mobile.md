# Platform: Mobile

iOS and Android application target. Activates when Recipe identifies a mobile app as the primary build target.

**Skill:** `modules/l3/mobile/SKILL.md`

## What makes Mobile different

| Concern | Mobile approach |
|---------|----------------|
| Permissions | Declared permission set — minimal, justified, request at point of need |
| Offline | Offline-first or online-only declared up front; sync strategy if offline-first |
| Battery | Background work budget declared; no unbounded background polling |
| Memory | Image loading strategy declared; memory pressure handling |
| Platform split | iOS-only, Android-only, or cross-platform (React Native, Flutter, etc.) declared |
| App store | App store compliance review required for any new permission or entitlement |
| Deep links | Universal links / App Links scheme declared if used |
| Push notifications | Notification permission strategy: when to ask, what to send |

## Platform-specific spec sections

- Permission manifest: each permission with user-visible justification string
- Offline strategy: what works offline, what degrades, what fails explicitly
- Background task budget: which tasks run in background and under what constraints
- Screen and navigation structure: stack, tab, modal hierarchy
- Platform-specific behavior: iOS vs Android differences explicitly called out

## Security controls loaded

- Data at rest: sensitive data encrypted using platform keychain/keystore — not UserDefaults or SharedPreferences for secrets
- Certificate pinning: declared for apps handling financial or health data
- Jailbreak/root detection: declared requirement (most apps skip; must be explicit when required)
- Deep link validation: incoming deep link parameters validated before use

## Gateway interaction

Mobile targets typically activate:
- `gateway-security` — always (sensitive data storage, deep links)
- `gateway-engineering` — Medium/High complexity
- `gateway-aesthetic` — any UI work (platform conventions differ significantly from web)
- `gateway-experience` — user-facing features
