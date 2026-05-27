# Mobile Systems Design Template (P2)

> **Platform:** Mobile
> **Template version:** 1.0
> **Prerequisite:** design-document.md `[REQUIRED]` sections complete.

---

## Navigation Architecture

**Navigation library:** [ ] React Navigation (RN) [ ] Flutter Navigator 2.0 [ ] UINavigationController (iOS) [ ] Jetpack Navigation (Android)

**Navigation structure:**

```
Root
  ├── Auth Stack (unauthenticated)
  │     ├── Login
  │     └── Register
  └── Main Tab Navigator (authenticated)
        ├── Tab: Home
        │     └── Home Stack
        │           ├── HomeScreen
        │           └── DetailScreen
        ├── Tab: Search
        └── Tab: Profile
```

**Deep link routing:**

| URL pattern | Navigates to | Auth required |
|---|---|---|
| `<scheme>://home` | HomeScreen | Yes |
| `<scheme>://item/:id` | DetailScreen with item ID | Yes |

---

## State Management

**State library:** [ ] Redux Toolkit [ ] Zustand [ ] MobX [ ] Riverpod (Flutter) [ ] Provider (Flutter) [ ] TCA (iOS) [ ] None (local state only)

**State categories:**

| Category | Location | Persistence | Notes |
|---|---|---|---|
| Auth token | Secure storage | Cross-session | Never in AsyncStorage/SharedPreferences |
| User preferences | AsyncStorage / SharedPreferences | Cross-session | Non-sensitive only |
| UI state | Component state | Session only | |
| Cached API data | AsyncStorage + memory | Session + disk | With TTL |
| Offline queue | AsyncStorage | Cross-session | Actions queued when offline |

---

## Network Layer

**HTTP client:** [ ] axios [ ] fetch (native) [ ] Dio (Flutter) [ ] URLSession (iOS) [ ] OkHttp (Android)

**Base configuration:**
```
- Timeout: 30s (connect), 60s (read)
- Retry: 3 attempts with exponential backoff (network errors only, not 4xx)
- Interceptors: auth token injection, response error normalization
- Certificate pinning: [ ] Yes (high-security apps) [ ] No
```

**Offline queue:** Network requests that fail due to no connectivity are queued and retried when connectivity restores.

---

## Local Storage Strategy

| Data | Storage | Encrypted | TTL |
|---|---|---|---|
| Auth tokens | `expo-secure-store` / iOS Keychain / Android Keystore | Yes | Session or declared |
| User ID | AsyncStorage / SharedPreferences | No | Permanent |
| Cached content | AsyncStorage / SQLite | No | Declare per content type |
| Media cache | File system | No | LRU eviction at ___ MB |
| Offline queue | AsyncStorage | No | Until processed |

**No sensitive data in AsyncStorage or SharedPreferences** — these are unencrypted.

---

## Background Processing

| Background task | Declared mode | iOS API | Android API | Frequency |
|---|---|---|---|---|
| Background fetch | Background fetch mode | `BGAppRefreshTask` | WorkManager | System-determined |
| Push notification | Remote notifications mode | `UNUserNotificationCenter` | FCM | On receipt |
| Location tracking | Location mode (continuous only if justified) | `CLLocationManager` | FusedLocationProvider | ___min interval |

**Minimize background work.** Each background mode declared in Info.plist (iOS) and AndroidManifest.xml (Android) is reviewed by app store. Unjustified modes cause rejection.

---

## Push Notifications

**Provider:** [ ] Firebase Cloud Messaging (FCM) [ ] APNs direct [ ] OneSignal [ ] Other: ___

**Notification types:**

| Type | Triggered by | Actions | Deep link |
|---|---|---|---|
| Order update | Server event | Tap → open order detail | `<scheme>://order/:id` |
| [list types] | | | |

**Permission:** Requested at the right moment — not on first launch. Present value proposition before system prompt.

---

## Screen Size Handling

**Breakpoints:**

| Device class | Width range | Layout changes |
|---|---|---|
| Phone (portrait) | 320–428pt | Single column |
| Phone (landscape) | 568–926pt | Two column or scroll |
| Tablet | 768pt+ | Sidebar or expanded layout |
| Foldable | Variable | Adaptive |

**Minimum tap target:** 44×44pt (iOS HIG) / 48×48dp (Material Design). No touch targets smaller than this.
