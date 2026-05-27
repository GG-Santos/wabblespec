# Experience Gateway — Platform UX Reference

iOS HIG, Material Design, Windows Fluent, and terminal UX patterns.

## iOS Human Interface Guidelines

Key principles for iOS/iPadOS native apps:

### Navigation patterns

- **Tab bar**: 2-5 primary destinations; persistent; bottom of screen
- **Navigation bar**: title + back button + optional trailing actions; top of screen
- **Sheet**: modal overlay for tasks; swipe down to dismiss
- **Full-screen modal**: for immersive tasks (camera, full-screen media)

Tab bar: flat, peer navigation. Push navigation: hierarchical, parent-child. Mixing them: use tab bar for top-level destinations; push for drill-down within each tab.

### Typography (iOS)

Use Dynamic Type. Respect the user's text size preference:
```swift
Text("Body text")
    .font(.body)  // automatically scales with Dynamic Type
    // NOT: .font(.system(size: 17)) — fixed size ignores user preference
```

Minimum touch target: 44×44 points (not pixels — logical units).

### Haptics

Use `UIFeedbackGenerator` for meaningful feedback:
- Impact: for collisions or transitions between states
- Notification: for success, warning, error events
- Selection: for picker changes

Do not use haptics as decoration. Each haptic event must have a corresponding meaningful action.

### Safe areas

Respect safe areas on all iPhone models. Content must not be hidden under notch, Dynamic Island, or home indicator:
```swift
.safeAreaInset(edge: .bottom) { /* bottom content */ }
// Or: .padding(.bottom, geometry.safeAreaInsets.bottom)
```

Spec must list which edges have content extending to screen edge (e.g., background colors) vs which have padding.

## Material Design (Android)

Google's design system for Android and cross-platform.

### Navigation patterns (Material 3)

- **Navigation bar**: 3-5 primary destinations; bottom of screen (≤ 600dp width)
- **Navigation rail**: 3-7 destinations; left side (> 600dp width, tablets)
- **Navigation drawer**: many destinations; persistent or modal
- **Top app bar**: title + leading icon + trailing actions; contextual

### Component model (Material 3)

Material 3 uses dynamic color derived from the user's wallpaper (on Android 12+). Apps should work with both:
- Static brand color scheme
- Dynamic color scheme derived from system

Declare in spec: static-only, or support dynamic color.

### Minimum touch target

48×48dp minimum for all interactive elements (maps to 48px on 1x screens; 96px on 2x).

### Typography (Material)

Use Material's type scale:
```
Display Large: 57sp  Display Medium: 45sp  Display Small: 36sp
Headline Large: 32sp  Headline Medium: 28sp  Headline Small: 24sp
Title Large: 22sp  Title Medium: 16sp  Title Small: 14sp
Body Large: 16sp  Body Medium: 14sp  Body Small: 12sp
Label Large: 14sp  Label Medium: 12sp  Label Small: 11sp
```

Use `sp` units (scale-independent pixels) for text — respects user's font size preference.

## Windows Fluent Design

For Windows desktop apps (WinUI 3, WPF with Fluent):

### Core principles

- **Acrylic**: translucent material using backdrop blur for sidebars, command bars
- **Mica**: tinted material that picks up desktop wallpaper color for title bars, backgrounds
- **Reveal**: subtle highlight on hover; built into WinUI controls
- **Depth**: layers separated by shadows and z-levels

### Window chrome

- Title bar: custom title bars should integrate with Mica; follow XAML `TitleBar` API
- Snap layouts: app windows must work with Windows 11 snap layouts (correct min/max size behavior)
- Dark/light: respond to system theme; `RequestedTheme` property or `Application.RequestedTheme`

### Typography

Use Segoe UI Variable (Windows 11) as the default font. Never override the system font for UI chrome — only override for content areas where brand typography is appropriate.

## Terminal / CLI UX

For command-line tools:

### Output design

```
Error:   [red] Error: file not found: config.json
Warning: [yellow] Warning: --output flag is deprecated; use --dest
Success: [green] ✓ Build complete (1.23s)
Info:    Scanning 47 files...
Data:    (plain; no color)
```

Rules:
- Color: use `NO_COLOR` env var to disable; respect `--no-color` flag; detect TTY (`isatty()`)
- Progress: spinner for indeterminate wait; progress bar for determinate; update in-place (ANSI escape codes)
- Table output: align columns; use headers; support `--json` for machine-readable output
- Verbosity: `--quiet` suppresses all non-error output; `--verbose` or `DEBUG=1` enables extra detail

### Interactive prompts

For interactive CLIs (setup wizards, configuration):
- Indicate selected option clearly (`[•] Option A` / `[ ] Option B`)
- Always provide a non-interactive flag for CI/scripts
- Never prompt in a pipe (`stdin.isTTY` check before prompting)
- Ctrl+C should exit cleanly with exit code 130, not print a traceback

### Error message format

```
Error: {what went wrong}
  {context: file path, line number, value}
  
  {how to fix it}
  
Run '{tool} help {subcommand}' for more information.
```

- Always tell users how to fix the error
- Include the value that caused the error (not just "invalid input")
- Link to documentation when appropriate
