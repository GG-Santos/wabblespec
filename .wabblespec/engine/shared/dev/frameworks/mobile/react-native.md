# React Native Framework

Loaded by Apply when react-native is detected in package.json.

## Version baseline

React Native 0.73+ with New Architecture (Fabric + JSI + TurboModules). If Old Architecture detected, note it and flag migration.

## Architecture decisions spec must declare

- **New Architecture**: enabled or not; if not, migration timeline
- **Expo vs bare**: Expo SDK (managed or bare workflow) vs bare React Native
- **OTA updates**: Expo EAS Update, CodePush, or no OTA
- **Navigation**: React Navigation 6+ (Stack, Tab, Drawer, Native Stack)

## Bridge vs JSI

New Architecture: JSI enables synchronous native calls — no serialization overhead.

Old Architecture: Bridge is async; large data across bridge is a performance bottleneck. Spec must declare which operations cross the bridge.

## Component and performance

- Use `FlatList` / `SectionList` for long lists — not `ScrollView` with `.map()`
- `FlatList` requires: `keyExtractor`, `renderItem`, `getItemLayout` if fixed height
- `useCallback` and `React.memo` on `renderItem` — prevent re-rendering on scroll
- Image optimization: `react-native-fast-image` or Expo Image for caching
- Hermes engine: always enabled in 0.70+ (faster startup, lower memory)

## Platform-specific code

```typescript
import { Platform } from 'react-native'

// Inline
const paddingTop = Platform.OS === 'ios' ? 20 : 0

// Platform files (automatic selection)
// Component.ios.tsx  →  loaded on iOS
// Component.android.tsx  →  loaded on Android
```

Declare in spec which components or behaviors differ per platform.

## Navigation patterns

```typescript
// Stack
const Stack = createNativeStackNavigator()
// Tab
const Tab = createBottomTabNavigator()
// Drawer
const Drawer = createDrawerNavigator()
```

Spec must include full navigator structure with auth flow (authenticated vs unauthenticated stacks).

## Deep linking

```typescript
// app.json or linking config
const linking = {
  prefixes: ['myapp://', 'https://myapp.com'],
  config: {
    screens: {
      Home: '',
      Profile: 'profile/:id',
    },
  },
}
```

Declare all deep link routes in spec; test with both scheme and Universal Link / App Link.

## Native modules

When a native module is required (e.g., Bluetooth, NFC, custom camera):
- Prefer community library over custom native module
- If custom: declare the API surface in spec; document iOS (Swift/ObjC) and Android (Kotlin/Java) implementations
- New Architecture: implement as TurboModule with TypeScript spec

## Testing

- Jest + `@testing-library/react-native` for component tests
- Detox for E2E (runs on device/emulator); declare which flows are covered
- Mock native modules in Jest setup
