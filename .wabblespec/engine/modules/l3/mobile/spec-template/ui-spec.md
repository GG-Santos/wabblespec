# Mobile UI Spec

> **Purpose:** Screen-by-screen definition of the mobile UI. Required before any UI implementation begins.
> Fill in all [REQUIRED] sections. Navigation diagram must be a directed graph — no cycles except intentional loops.

---

## Navigation Pattern [REQUIRED]

Declare the top-level navigation structure. Mixed patterns (tab bar + drawer) require explicit declaration of which takes precedence.

| Pattern | When to use |
|---|---|
| **Tab bar (bottom)** | 3–5 top-level destinations; peer relationships; iOS and Android both |
| **Navigation drawer** | 5+ destinations; hierarchical; Android-primary |
| **Stack only** | Single linear flow (onboarding, checkout); no persistent nav chrome |
| **Mixed** | Tab bar for main app + stack within each tab (most common) |

**Declared pattern:** ___

**Top-level destinations (if tab bar):**

| Tab | Icon | Label | Badge? |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

## Screen Inventory [REQUIRED]

Every screen in the app. Fill before implementation. Screens not listed here are not in scope.

| Screen ID | Name | Route / Deep Link | Auth required? | Data source |
|---|---|---|---|---|
| SCR-001 | | | Yes / No | |
| SCR-002 | | | | |

---

## Navigation Flow

Document as a directed graph. Every edge is a trigger (tap, swipe, system event).

```
[SCR-001: Launch]
  → (onboarding not complete) → [SCR-002: Onboarding]
  → (onboarding complete, not authenticated) → [SCR-003: Login]
  → (authenticated) → [SCR-004: Home]

[SCR-004: Home]
  → (tap product) → [SCR-005: Product Detail]
  → (tap cart icon) → [SCR-006: Cart]
  → (tab: Profile) → [SCR-007: Profile]

[SCR-003: Login]
  → (login success) → [SCR-004: Home]
  → (tap "Register") → [SCR-008: Registration]
  → (forgot password) → [SCR-009: Password Reset]
```

**Back behavior:** Declare explicitly for any screen where Android back button or iOS swipe-back is non-standard.

| Screen | Back behavior | Reason |
|---|---|---|
| SCR-002 (Onboarding) | Disabled | Cannot go back before completing |
| | | |

---

## Touch Target Standards

All interactive elements must meet minimum touch target sizes. These are non-negotiable for accessibility compliance.

| Platform | Minimum touch target | Recommended |
|---|---|---|
| iOS | 44 × 44 pt | 48 × 48 pt |
| Android | 48 × 48 dp | 56 × 56 dp |

**Enforcement:** Any element smaller than the minimum must be wrapped in a hit area container that expands the tap zone without changing visual size.

```swift
// SwiftUI — expand tap area without visual change
Button(action: handleTap) {
    Image(systemName: "heart")
        .frame(width: 24, height: 24)
}
.contentShape(Rectangle().size(width: 44, height: 44))  // tap zone
```

```kotlin
// Compose — use minimumInteractiveComponentSize (Material 3)
// Or explicit padding:
IconButton(
    onClick = { /* ... */ },
    modifier = Modifier.size(48.dp)  // entire area is tappable
) {
    Icon(Icons.Default.Favorite, contentDescription = "Like")
}
```

---

## Safe Area Declarations

All screens must respect device safe areas. Declare per-screen handling.

**iOS safe areas:** Status bar (top), home indicator (bottom), notch / Dynamic Island (top/sides).
**Android safe areas:** Status bar (top), navigation bar (bottom — variable height, can be gesture-nav or button-nav).

```
Standard screen layout:
┌──────────────────────────┐
│  [Safe area top]         │  ← Status bar / notch
│  ┌────────────────────┐  │
│  │ Navigation bar     │  │
│  ├────────────────────┤  │
│  │                    │  │
│  │   Content area     │  │
│  │                    │  │
│  └────────────────────┘  │
│  [Safe area bottom]      │  ← Home indicator / nav bar
└──────────────────────────┘
```

| Screen | Extends behind top safe area? | Extends behind bottom safe area? | Notes |
|---|---|---|---|
| SCR-004 (Home) | No | No | Standard |
| SCR-005 (Detail) | Yes (hero image) | No | Image bleeds under status bar |

---

## Keyboard Avoidance

Screens with text input must declare keyboard avoidance behavior. Unhandled keyboards obscure input fields.

| Screen | Has text input? | Avoidance behavior |
|---|---|---|
| SCR-003 (Login) | Yes | Scroll view; active field scrolls above keyboard |
| SCR-006 (Cart) | No | N/A |

**Standard patterns:**
- `ScrollView` with `keyboardDismissMode: .interactive` (iOS) — user can dismiss keyboard by scrolling
- `WindowInsets.ime` (Compose) — content pushed up by keyboard height
- Bottom sheet forms: set `adjustResize` or use `imePadding()` modifier

---

## Accessibility Requirements [REQUIRED]

Declare the accessibility tier before implementation. Tier affects verification gate pass/fail.

| Tier | Description |
|---|---|
| **A (minimum)** | Screen reader labels on all interactive elements; no unlabeled buttons |
| **AA (required)** | A + Dynamic Type support; minimum contrast 4.5:1; touch targets met |
| **AAA (enhanced)** | AA + full keyboard nav; no flashing content; all media has captions |

**Declared tier:** ___

**VoiceOver / TalkBack requirements:**

Every interactive element must have a meaningful accessibility label. Decorative images must be hidden from screen readers.

```swift
// SwiftUI
Button(action: addToCart) {
    Image(systemName: "cart.badge.plus")
}
.accessibilityLabel("Add \(product.name) to cart")
.accessibilityHint("Double tap to add one item to your cart")

// Decorative image — hide from VoiceOver
Image("background-pattern")
    .accessibilityHidden(true)
```

```kotlin
// Compose
IconButton(onClick = { addToCart(product) }) {
    Icon(Icons.Default.AddShoppingCart,
         contentDescription = "Add ${product.name} to cart")  // non-null = accessible
}

// Decorative
Image(painter = painterResource(R.drawable.bg_pattern),
      contentDescription = null)  // null = hidden from TalkBack
```

**Dynamic Type / Font scaling:**

| Platform | Support required | Test method |
|---|---|---|
| iOS | Dynamic Type sizes XS–XXXL | Settings > Accessibility > Display & Text Size > Larger Text |
| Android | Font scale 85%–200% | Settings > Accessibility > Display > Font Size |

All text must use scalable units (no fixed-point sizes). Layout must not break at maximum scale — use flexible containers, not fixed-height cells.

---

## Element Specs

Per-screen element table. Fill for screens with non-obvious interactive elements.

**Screen: SCR-004 (Home)**

| Element | Type | Action | Accessibility label | State variants |
|---|---|---|---|---|
| Product card | Tappable container | Navigate to detail | "Product name, $price" | Default / Highlighted |
| Filter button | Toggle | Open filter sheet | "Filter products" | Default / Active |
| Search bar | Text input | Filter results inline | "Search products" | Empty / Focused / Has text |

---

## Loading and Empty States

Every data-driven screen must declare all states explicitly.

| State | Trigger | UI |
|---|---|---|
| Loading | Data not yet available | Skeleton / spinner per screen declaration |
| Empty | Data loaded, zero results | Illustration + message + CTA (if applicable) |
| Error | Network/server error | Message + retry button |
| Success | Data loaded | Normal content |

Skeleton screens are preferred over spinners for content-heavy screens (lists, feeds). Spinners are acceptable for action feedback (submitting a form).

---

## GWT Acceptance Scenarios

```
Given: a button has no visible label (icon-only)
When: VoiceOver or TalkBack focuses the element
Then: the accessibility label announces the action (not "button" or nothing)
      AND the hint describes the result if non-obvious

Given: the user enables maximum font size in system settings
When: any screen renders text
Then: all text scales to the maximum Dynamic Type / font scale size
      AND no text is clipped, overlapping, or truncated unexpectedly
      AND all tap targets remain at least the platform minimum size

Given: a keyboard appears over a text input
When: the user activates the field
Then: the field is visible above the keyboard (not obscured)
      AND the user can dismiss the keyboard via the standard system gesture
      AND no content is permanently hidden behind the keyboard
```
