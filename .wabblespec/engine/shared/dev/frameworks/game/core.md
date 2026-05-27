# Game Framework Core

Cross-framework knowledge for game development targets. Loaded by Apply for every Game platform task.

## Game loop contract

Every game spec must declare the game loop architecture:

```
Fixed timestep (physics):   update(fixedDeltaTime)  →  runs N times per frame
Variable timestep (render): render(interpolation)    →  runs once per frame
```

Separating physics (fixed) from rendering (variable) prevents physics instability at different frame rates.

```
accumulator += deltaTime
while accumulator >= FIXED_TIMESTEP:
    physics.update(FIXED_TIMESTEP)
    accumulator -= FIXED_TIMESTEP
render(accumulator / FIXED_TIMESTEP)   ← interpolation factor
```

Spec must declare: target frame rate (60fps, 90fps, 120fps), fixed timestep value, and whether variable timestep is acceptable for the project type.

## Frame budget allocation (16.6ms at 60fps)

| System | Budget guideline |
|---|---|
| Physics + logic | 3-5ms |
| AI / pathfinding | 1-2ms |
| Rendering (CPU draw calls) | 2-4ms |
| GPU (render) | 10-12ms |
| Audio | 0.5ms |
| UI | 1ms |
| Headroom | 1-2ms |

Spec must declare: per-system budget for performance-sensitive games. Profiling gates must verify these budgets in Verifier.

## Input handling

Spec must declare:
- **Input method**: gamepad, keyboard/mouse, touch, or all three
- **Input polling vs events**: polling (every frame) vs event queue (when changed)
- **Input latency**: target frames from input to visual response (1-2 frames recommended)
- **Rebinding**: whether players can rebind actions; which actions are rebindable
- **Accessibility**: accessible input alternatives (eye tracking, switch access) if required by platform cert

## Save system

```
Save file = game state snapshot at a point in time
```

Spec must declare:
- **Save format**: binary (fast, compact) or JSON (human-readable, larger)
- **Format version**: version field required; migration strategy for old saves
- **Save triggers**: manual save, auto-save on checkpoint, continuous save
- **Corruption handling**: backup + verify on load; if corrupt, offer rollback or new game
- **Cloud sync**: Steam Cloud, iCloud, Google Play Games; conflict resolution policy

## Networking (if multiplayer)

| Model | When | Security risk |
|---|---|---|
| Server-authoritative | Competitive / anti-cheat required | Correct — server validates all state |
| Client-authoritative | None — never for games with consequences | All clients can cheat |
| P2P | Casual / cooperative | One peer can cheat; acceptable for low-stakes |

- **Client prediction**: render player actions immediately, roll back if server disagrees
- **Lag compensation**: server rewinds state to client's time when validating hits
- **Dedicated server vs relay**: declare infrastructure

Spec must declare: authority model, state sync frequency, and latency tolerance.

## Anti-cheat architecture

- **Memory scanning**: client-side detection is detectable and bypassable — declare it as a deterrent, not a guarantee
- **Server validation**: only server-authoritative games can enforce fairness
- **Obfuscation**: protect game binaries from reverse engineering (Burst IL2CPP on Unity, shipping builds)

## Platform certification checklist requirements

Every console/store platform requires passing certification. Spec must address:
- **TRC (PlayStation)**: crash rate requirements, trophy implementation, save data requirements
- **TCR (Xbox)**: accessibility requirements, suspend/resume behavior, achievement implementation
- **Lot Check (Nintendo)**: very strict; no crashes, specific UI requirements, save data handling

PC platforms (Steam, Epic, GOG): less strict but spec must still address: windowed/fullscreen mode, controller support, Steam Overlay compatibility, and accessibility options.
