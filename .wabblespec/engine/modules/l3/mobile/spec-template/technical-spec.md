# Mobile Technical Spec Template (P3)

> **Platform:** Mobile
> **Template version:** 1.0
> **Prerequisite:** systems-design.md complete.

---

## Screen Implementation Specs

Each screen gets one entry.

### `<ScreenName>`

**Route:** `<scheme>://path` (if deep-linkable)

**Props / params:**
```typescript
type ScreenParams = {
  id: string
  mode?: 'view' | 'edit'
}
```

**Data requirements:**
- Fetched from: `GET /api/resource/:id`
- Cached: [ ] Yes (TTL: ___) [ ] No
- Offline behavior: [ ] Cached version shown [ ] Error state shown [ ] N/A

**Loading states:**
- Initial load: skeleton screen (not spinner)
- Refresh: pull-to-refresh indicator
- Error: retry button + error message

**GWT scenarios:**
```
Given: user navigates to screen with valid ID
When: screen mounts
Then: skeleton shown immediately
      AND data loads within declared timeout
      AND screen is interactive within 500ms of data arrival

Given: user navigates to screen with no connectivity
When: screen mounts
Then: cached data displayed (if available)
      AND offline indicator shown
      AND retry available when connectivity restored
```

---

## Authentication Flow

**Token storage:** iOS Keychain (`expo-secure-store` or `react-native-keychain`). Android Keystore.

**Token refresh:** Silent refresh before token expiry. If refresh fails → navigate to login without data loss.

**Biometric auth (if declared):**
```
Given: user enables biometric auth in settings
When: app is foregrounded after background
Then: biometric prompt shown (if OS supports it)
      AND fallback to PIN/password available
      AND feature works if biometric hardware absent
```

---

## Performance-Critical Paths

| Operation | Target | Technique |
|---|---|---|
| App cold start | < 3s | Lazy load non-critical screens |
| Screen transition | < 300ms | `useNativeDriver: true` for animations |
| List scroll | 60fps | `FlatList` with `keyExtractor`, `getItemLayout` |
| Image load | < 1s (cached) | Progressive loading, CDN caching |
| API call | < 2s p95 | Timeout declared, loading state shown |

---

## Accessibility Requirements

| Requirement | Implementation |
|---|---|
| Screen reader support | All interactive elements have `accessibilityLabel` |
| Minimum tap target | 44×44pt / 48×48dp |
| Color contrast | 4.5:1 minimum (WCAG AA) |
| Dynamic type / font scaling | Text scales with OS font size setting |
| Reduce motion | Animations disabled when `prefersReducedMotion` / `AccessibilitySettings.isAnimationDisabled` |

---

## App Store Submission Checklist

### iOS
- [ ] Bundle ID matches provisioning profile
- [ ] All `NSUsageDescription` keys present for requested permissions
- [ ] No private API calls (scan with `nm` or App Store Connect static analysis)
- [ ] App works on minimum declared iOS version
- [ ] IPv6 network compatibility (App Store tests on IPv6-only network)
- [ ] App does not load remote JavaScript (App Store Review Guideline 2.5.2)
- [ ] Privacy manifest (`PrivacyInfo.xcprivacy`) present if using required reason APIs

### Android
- [ ] Target SDK is current year's Android API level (Google Play requirement)
- [ ] 64-bit binaries included (arm64-v8a)
- [ ] App bundle (`.aab`) generated (not `.apk` for Play Store)
- [ ] Data safety section complete in Play Console
- [ ] Keystore backup stored securely (loss = cannot update app)
- [ ] ProGuard/R8 rules declared for any reflection-based libraries
