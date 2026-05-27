# Game UI Spec Template

> **Platform:** Game | **Conditional load:** activate if HUD or non-trivial UI is in scope.
> **Prerequisites:** game-concept.md (player fantasy, pillars) and systems-index.md (UI system listed) complete.
> The UI serves the player fantasy — every element on screen should earn its space. Clutter is a pillar violation.

---

## Screen Inventory [REQUIRED]

List every screen the player can encounter. Unknown screens at implementation time = scope surprises.

| Screen ID | Name | Entry trigger | Exit trigger | Pauses gameplay? |
|---|---|---|---|---|
| `scr_main_menu` | Main Menu | App launch | New game / load game | N/A |
| `scr_hud` | HUD | Gameplay start | Pause / game end | No |
| `scr_pause` | Pause Menu | Pause input | Resume / quit | Yes |
| `scr_inventory` | Inventory | Inventory input | Close | Yes / No |
| `scr_game_over` | Game Over | Player death | Retry / main menu | Yes |
| [add rows] | | | | |

---

## Navigation Flow

Directed graph of screen transitions. Every arrow is a deliberate design decision — no accidental back-button behavior.

```
[Main Menu] ──New Game──→ [HUD]
[Main Menu] ──Load Game──→ [HUD]
[HUD] ──Pause──→ [Pause Menu]
[Pause Menu] ──Resume──→ [HUD]
[Pause Menu] ──Quit──→ [Main Menu]
[HUD] ──Player Death──→ [Game Over]
[Game Over] ──Retry──→ [HUD]
[Game Over] ──Main Menu──→ [Main Menu]
[HUD] ──Inventory Key──→ [Inventory] (overlay)
[Inventory] ──Close──→ [HUD]
```

**Back/cancel action:** On every screen, the back action is: ___ (console requires a defined back button behavior on all screens).

---

## HUD Design [REQUIRED if HUD present]

### Zone Layout

Divide the screen into named zones. Each zone has a purpose; no element exists outside a zone.

```
┌─────────────────────────────────────────────────────┐
│  [HEADER ZONE]  Health | Armor | Level | Quest timer │
├─────────────────────────────────────────────────────┤
│                                                     │
│                [CENTER ZONE]                        │
│          Crosshair, damage numbers,                 │
│          interaction prompts, subtitles             │
│                                                     │
├─────────────────────────────────────────────────────┤
│  [FOOTER ZONE]  Ability bar | Ammo | Minimap        │
└─────────────────────────────────────────────────────┘
                    [OVERLAY ZONE]
              Screen flash, vignette, effects
              (rendered above all zones, non-interactive)
```

### HUD Element Specs

| Element | Zone | Updates when | Visibility rule | Accessibility label |
|---|---|---|---|---|
| Health bar | Header | `health_changed` signal | Always visible | "Health: N of M" |
| Stamina bar | Header | `stamina_changed` | Hidden at max | "Stamina: N of M" |
| Crosshair | Center | Static | Hidden in menu | "Crosshair" |
| Interaction prompt | Center | Near interactable | Proximity-conditional | "Press [key] to [action]" |
| Subtitles | Center | Dialogue events | User preference | Subtitle text verbatim |
| Minimap | Footer | Player position update | Hideable by player | "Minimap" |
| Ability bar | Footer | Ability state changes | Always visible | "Ability [N]: [name], [cooldown]" |
| Damage numbers | Overlay | Hit events | User preference | Announced via screen reader when > threshold |

**Element priority rule:** When screen real estate is limited (mobile, VR, constrained viewport), hide in this order: damage numbers → minimap → stamina bar → crosshair. Never hide: health bar, subtitles (if active), interaction prompts.

---

## Input Priority Stack [REQUIRED]

Matches `technical-spec.md` input priority. Re-declared here so UI engineers and gameplay engineers share one source.

```
UI (menus, modals, inventory) — highest priority
  └── Player (movement, attack, interact)
        └── Camera (free-look, zoom)
              └── World (ambient, environment) — lowest priority
```

**Rule:** If a UI screen is open, all player and camera inputs are consumed by the UI layer and not passed to gameplay. No shooting through inventory screens.

**Focus management (controller/keyboard):** On every screen open, the initial focus element is declared. The tab/D-pad navigation order is declared. No element is unreachable via keyboard or controller navigation.

---

## Accessibility Requirements [REQUIRED]

Minimum compliance for all game targets. Console certification requires subset of these. Declare which tier you are targeting.

**Tier declaration:** [ ] Basic (minimum — remapping + colorblind) [ ] Standard (+ text scaling + subtitles) [ ] Comprehensive (+ motion sensitivity + screen reader hooks)

| Feature | Requirement | Console cert relevance |
|---|---|---|
| Full action remapping | All gameplay actions remappable, not just presets | Sony, Microsoft required |
| Colorblind modes | Deuteranopia minimum; protanopia and tritanopia recommended | Recommended for certification |
| Text scaling | 100%–150% minimum; 100%–200% preferred | Recommended |
| Subtitles | All voiced dialogue has subtitle option | Required for many rating bodies |
| Motion sensitivity | Camera shake and screen flash intensity sliders | Recommended; epilepsy disclosure required if flash |
| High contrast mode | UI elements readable against varied backgrounds | Recommended |

**Subtitle format:**
- Speaker name displayed when speaker is off-screen or ambiguous
- Line length ≤ 42 characters per line
- Minimum font size at 100% scaling: ___ pt
- Background: semi-transparent bar behind text (not naked text on gameplay background)

---

## Per-Screen Acceptance Scenarios

**Template — apply to each screen in inventory:**

```
Given: player opens [screen]
When: the screen has [empty state condition]
Then: an empty state message is displayed (not blank screen)
      AND the player has a clear action to take (or explicit "no items" message)

Given: player navigates [screen] using controller only
When: screen opens
Then: focus is on the declared initial element
      AND all interactive elements are reachable via D-pad / tab
      AND no interactive element is unreachable without mouse

Given: player presses back/cancel on [screen]
When: back action fires
Then: the previous screen is restored with its previous state intact
      AND no game state was modified by the back action alone
```

**Screen-specific scenarios:**

```
Given: player opens inventory during combat
When: inventory screen is active
Then: gameplay is paused (or game continues — declare which)
      AND all player and camera inputs are consumed by inventory UI
      AND no attacks or movement are registered while inventory is open

Given: player opens pause menu
When: pause is active
Then: all game simulation is halted (physics, AI, timers)
      AND audio fades or ducks per declared audio design
      AND resume restores exact game state with no desync
```

---

## Open Questions

Unresolved screen transitions, element priority conflicts, or accessibility tier decisions go here.
