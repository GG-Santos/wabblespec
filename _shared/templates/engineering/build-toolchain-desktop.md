# Build Toolchain — Desktop

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Framework

**Framework:** [ ] Electron  [ ] Tauri  [ ] Qt  [ ] .NET WPF/WinUI  [ ] Other: ___
**Target platforms:** [ ] macOS  [ ] Windows  [ ] Linux

---

## Build

**Build tool:** [ ] electron-builder  [ ] Tauri CLI (`tauri build`)  [ ] cmake  [ ] MSBuild  [ ] Other: ___
**Package format:** [ ] .dmg + .pkg (macOS)  [ ] .exe + .msi (Windows)  [ ] .AppImage + .deb (Linux)  [ ] All three
**Auto-updater:** [ ] electron-updater  [ ] Tauri updater  [ ] Squirrel  [ ] None

---

## Code signing

**macOS:** [ ] Developer ID signed + notarized  [ ] unsigned (development only)
**Windows:** [ ] EV code signing certificate  [ ] standard OV certificate  [ ] unsigned (development only)
**Note:** unsigned builds trigger Gatekeeper (macOS) and SmartScreen (Windows) — required gates per `l3/desktop` AT-DES-03

---

## Test runner

**Unit:** [ ] Jest/Vitest (renderer)  [ ] cargo test (Tauri backend)  [ ] Other: ___
**Integration:** [ ] Playwright + Electron  [ ] WebdriverIO  [ ] Other: ___
**Coverage threshold:** 80% statement

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] CircleCI  [ ] GitLab CI  [ ] Other: ___

**Required CI gates:**
- [ ] Lint + type check
- [ ] Unit tests
- [ ] Integration tests (headless Electron/WebdriverIO)
- [ ] Build for all target platforms (macOS + Windows + Linux)
- [ ] Code signing verification (macOS notarization check)
- [ ] Auto-updater package size check
- [ ] Cold start timing (≤ 3s window visible gate)

---

## Distribution

**Channel:** [ ] Direct download (own website)  [ ] GitHub Releases  [ ] Microsoft Store  [ ] Mac App Store  [ ] Homebrew Cask  [ ] Other: ___
**Update channel:** [ ] stable  [ ] beta  [ ] nightly (declare what users are on)
**Rollout strategy:** [ ] staged (% of users)  [ ] full release  [ ] Other: ___

---

## Observability

**Crash reporting:** [ ] Sentry  [ ] Bugsnag  [ ] Backtrace  [ ] None  [ ] Other: ___
**Update analytics:** [ ] electron-updater events  [ ] custom telemetry  [ ] None
**Usage telemetry:** [ ] opt-in only  [ ] None (declare if no telemetry)

_(Monitor generates crash-rate and update-success-rate alerts for desktop — not server latency configs.)_

---

## Notes

_Platform-specific signing certificates location, update server URL, notarization credentials reference:_
