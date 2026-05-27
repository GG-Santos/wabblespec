# Interaction Design

## Touch Targets

| Platform | Minimum size |
|---|---|
| Mobile | 44x44px (Apple HIG and Android Material) |
| Desktop with touch | 44x44px |
| Desktop mouse-only | 32x32px, with keyboard alternative |

Touch target is the interactive area, not the visual size. A small icon can have a larger invisible hit area.

## Keyboard Access

All interactions keyboard-accessible. No mouse-only or touch-only interactions. Keyboard audit required before delivery:
- Tab order is logical (follows visual/reading order)
- All interactive elements reachable by Tab/Shift-Tab
- Enter and Space activate buttons and links
- Arrow keys navigate within menus, listboxes, and grids
- Escape closes modals, dropdowns, and overlays

## Focus Management

Focus lands on a meaningful element after every state change:

| State change | Focus destination |
|---|---|
| Modal opens | Modal heading or first interactive element |
| Modal closes | Trigger element |
| Page navigation | Main content or page heading |
| Error appears | Error message or first invalid field |

No focus that moves to a decorative or non-interactive element.

## Gestures

No gesture-only interactions. Every gesture has a visible button or control equivalent:

| Gesture | Required equivalent |
|---|---|
| Swipe to delete | Delete button in row or context menu |
| Swipe to reveal actions | Actions available via context menu or edit mode |
| Pull to refresh | Refresh button |
| Pinch to zoom | Zoom controls |
| Long press | Right-click or context menu equivalent |

Custom gestures must be discoverable — not assumed.

## Audit Gates

- [ ] Touch targets meet minimums (44x44px mobile, 32x32px desktop mouse-only)
- [ ] All interactions keyboard-accessible
- [ ] Tab order is logical
- [ ] Focus management declared per state change type
- [ ] No gesture-only interactions — all have visible equivalents
