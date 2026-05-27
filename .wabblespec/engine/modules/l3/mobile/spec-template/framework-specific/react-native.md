# Framework-Specific Architecture: React Native

> **Applies when:** `react-native` in package.json + `*.tsx` files and no Flutter/Swift/Kotlin detected.
> Covers Expo (managed + bare) and bare React Native CLI. Declare which in technical-spec.md.
> **Version authority:** React Native 0.73+ (New Architecture available). Expo SDK 50+.

---

## Architecture Declaration [REQUIRED]

Declare before implementation begins. These choices affect native module availability and build toolchain.

| Decision | Options | Notes |
|---|---|---|
| **Expo vs bare RN** | Expo managed / Expo bare / React Native CLI | Expo managed: no native code, fastest start; bare: full native access |
| **New Architecture** | Enabled / Disabled | New Arch uses JSI (direct JS↔native calls, no serialization). Enables Fabric + TurboModules. Enabled by default in RN 0.74+ |
| **Target platforms** | iOS only / Android only / Both | Declare — affects native module choices and CI matrix |

**Declared:** ___

---

## New Architecture vs Bridge

**Old Architecture (Bridge):** JS and native communicate via an asynchronous JSON-serialization bridge. All values cross as serialized strings. Event loop blocks during serialization.

**New Architecture (JSI):** JavaScript Interface — a C++ layer that lets JS hold direct references to native objects. No serialization. Synchronous when needed.

```typescript
// TurboModule (New Arch) — synchronous native call
import { NativeModules } from 'react-native'
const { CameraModule } = NativeModules  // typed via codegen

// Fabric component (New Arch) — host components with direct view binding
// Registered via codegenNativeComponent — not manually
```

**What changes for you:** If using New Architecture, native modules must be TurboModules (codegen-typed, C++ bridge). Legacy native modules that only implement the old Bridge will not work without a compatibility shim. Verify all third-party native dependencies support New Architecture before enabling.

---

## Expo Managed vs Bare

**Expo Managed:**
```
No native code in repo.
Build on Expo servers (EAS Build) or locally via Expo CLI.
Config plugins handle native modification at build time.
```

```typescript
// app.json / app.config.ts — Expo managed config
export default {
  expo: {
    name: 'MyApp',
    slug: 'myapp',
    ios: { bundleIdentifier: 'com.example.myapp', supportsTablet: true },
    android: { package: 'com.example.myapp' },
    plugins: [
      'expo-camera',
      ['expo-location', { locationAlwaysAndWhenInUsePermission: '...' }]
    ]
  }
}
```

**Expo Bare / RN CLI:**
```
ios/ and android/ directories present in repo.
Direct native code modification possible.
Third-party native modules linked manually or via autolinking.
```

---

## Platform-Specific Files

```typescript
// Component.ios.tsx     — iOS-only implementation
// Component.android.tsx — Android-only implementation
// Component.tsx         — shared fallback

// Or via Platform.select:
import { Platform, StyleSheet } from 'react-native'

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.select({ ios: 44, android: 24, default: 0 }),
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 } },
      android: { elevation: 4 }
    })
  }
})
```

**Rule:** Platform-specific files (`.ios.tsx`, `.android.tsx`) are preferred over inline `Platform.select` when the platform difference is more than a single style value. Inline `Platform.select` is acceptable for minor style differences only.

---

## Navigation (React Navigation)

```typescript
// navigation/RootNavigator.tsx
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'

// Type the param list — prevents passing wrong params
type RootStackParamList = {
  Home: undefined
  ProductDetail: { productId: string }
  Settings: undefined
}

const Stack = createNativeStackNavigator<RootStackParamList>()

// Deep link config — declare before implementation
const linking = {
  prefixes: ['myapp://', 'https://myapp.example.com'],
  config: {
    screens: {
      ProductDetail: 'products/:productId'
    }
  }
}
```

**SafeAreaView:**
```typescript
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context'

// Root — wrap entire app
<SafeAreaProvider>
  <NavigationContainer>
    ...
  </NavigationContainer>
</SafeAreaProvider>

// Per-screen — apply edges explicitly
<SafeAreaView edges={['top', 'bottom']} style={styles.container}>
  {children}
</SafeAreaView>
```

Never use `marginTop: 44` or hardcoded status bar heights. `SafeAreaView` handles notch, Dynamic Island, and Android status bar.

---

## Animations (React Native Reanimated)

```typescript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS  // bridge back to JS thread when needed
} from 'react-native-reanimated'

function AnimatedCard() {
  const scale = useSharedValue(1)

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }]
  }))

  return (
    <Animated.View style={[styles.card, animatedStyle]}>
      <Pressable onPressIn={() => { scale.value = withSpring(0.95) }}
                 onPressOut={() => { scale.value = withSpring(1.0) }}>
        ...
      </Pressable>
    </Animated.View>
  )
}
```

**Reanimated runs on the UI thread** — shared values and animated styles execute without crossing to JS. `runOnJS` is required when calling JS functions (state updates, navigation) from a worklet.

Do not use the built-in `Animated` API for anything that needs to run at 60/120fps. Use Reanimated.

---

## Native Modules and Permissions

```typescript
// Declare all required permissions in app.json (Expo) or Info.plist/AndroidManifest.xml (bare)
// Request at runtime — never assume permission is granted

import { Camera } from 'expo-camera'  // or react-native-camera for bare

async function requestCameraPermission() {
  const { status } = await Camera.requestCameraPermissionsAsync()
  if (status !== 'granted') {
    // Handle denial gracefully — show explanation, not a crash
    return false
  }
  return true
}
```

**Permission UX rule:** Request permission at the moment of need (user taps "Take Photo"), not on app launch. Pre-prompt with a rationale screen before the system permission dialog — one-strike on iOS.

---

## GWT Acceptance Scenarios

```
Given: the app is built with New Architecture enabled
When: a native module is called from JavaScript
Then: the call uses JSI (no Bridge serialization)
      AND the native module is declared in the codegen spec
      AND any third-party native dep has been verified to support New Architecture

Given: the app runs on a device with a notch or Dynamic Island
When: any screen renders
Then: no UI elements are obscured by the status bar, notch, or home indicator
      AND SafeAreaView (not hardcoded margins) handles the safe area on all devices

Given: a permission is required for a feature
When: the user first encounters that feature
Then: the system permission dialog is shown at that moment (not at app launch)
      AND denial is handled gracefully with a fallback UI
      AND the permission rationale is shown before the system dialog on Android (if applicable)
```
