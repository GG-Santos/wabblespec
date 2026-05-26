# Platform: Game

Game development target. Activates when Recipe identifies a game as the primary build target.

**Skill:** `modules/l3/game/SKILL.md`

## What makes Game different

| Concern | Game approach |
|---------|--------------|
| Frame budget | All per-frame operations declare time budget (target: 16ms at 60fps) |
| Input handling | Input polling vs event-driven declared; latency requirements stated |
| State serialization | Save/load system declared; serialization format versioned |
| Platform certification | Platform-specific certification requirements (TRC, TCR, Lot Check) declared if console target |
| Asset pipeline | Asset build pipeline declared; hot-reload strategy for development |
| Physics/simulation | Determinism requirements declared (replay, netplay) |
| Audio | Audio budget declared; streaming vs in-memory per asset |

## Platform-specific spec sections

- Game loop architecture: update/render separation, fixed vs variable timestep
- Input contract: all input actions declared with default bindings and rebinding support
- Save system: what is saved, when, format, versioning, migration strategy
- Platform targets: PC, console (which), mobile — certification requirements per platform
- Performance budget: draw calls, texture memory, CPU/GPU split — targets declared
- Network architecture (if multiplayer): client-server vs P2P, authority model, latency handling

## Security controls loaded

- Anti-cheat: client-authoritative vs server-authoritative model declared; client-auth flagged as risk
- DRM: if applicable, integration declared and third-party DRM risks acknowledged
- User data: player stats and preferences handled per platform data privacy requirements (COPPA if applicable)
- Mod support: if mods are supported, sandboxing strategy declared

## Gateway interaction

Game targets typically activate:
- `gateway-engineering` — always (frame budget, input contracts)
- `gateway-security` — if online features (auth, anti-cheat, leaderboards)
- `gateway-experience` — for UX and accessibility requirements (console platform requirements often mandate accessibility)
