# Desktop Engineering — Build Toolchain

## Electron

**Preferred packager:** electron-builder (handles signing, notarization, auto-updater config, multi-platform output).
**Alternative:** electron-forge (more opinionated, tighter Vite integration).

### electron-builder config (`electron-builder.yml`)
```yaml
appId: com.yourorg.appname
productName: AppName

directories:
  output: release

files:
  - dist/
  - "!src/"
  - "!test/"

mac:
  category: public.app-category.productivity
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  notarize:
    teamId: ${APPLE_TEAM_ID}

win:
  target:
    - target: nsis
      arch: [x64, arm64]
  signingHashAlgorithms: [sha256]
  timeStampServer: http://timestamp.digicert.com

linux:
  target: [AppImage, deb, rpm]

publish:
  provider: github
  owner: <org>
  repo: <repo>
```

### Build commands
```bash
# Development
npm run dev           # Vite dev server + Electron

# Production build (all platforms from CI)
npm run build         # Compile TypeScript + Vite frontend
npm run dist -- --mac     # Package for macOS (requires macOS runner)
npm run dist -- --win     # Package for Windows
npm run dist -- --linux   # Package for Linux
```

### Entitlements (macOS)
```xml
<!-- build/entitlements.mac.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC ...>
<plist version="1.0">
<dict>
  <key>com.apple.security.cs.allow-jit</key><true/>
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key><false/>
  <key>com.apple.security.network.client</key><true/>
</dict>
</plist>
```

---

## Tauri

### Build commands
```bash
# Development
npm run tauri dev

# Production build (current platform)
npm run tauri build

# Cross-platform (from CI only — each OS must be its own runner)
```

### tauri.conf.json key fields
```json
{
  "tauri": {
    "bundle": {
      "identifier": "com.yourorg.appname",
      "icon": ["icons/32x32.png", "icons/icon.icns", "icons/icon.ico"]
    },
    "updater": {
      "active": true,
      "endpoints": ["https://releases.yourorg.com/{{target}}/{{current_version}}"],
      "dialog": true,
      "pubkey": "<base64-encoded-public-key>"
    },
    "security": {
      "csp": "default-src 'self'; script-src 'self'"
    }
  }
}
```

---

## CI Build Matrix

Each OS must build on its own runner (cross-compilation has significant limitations):

```yaml
# GitHub Actions matrix
strategy:
  matrix:
    os: [macos-latest, windows-latest, ubuntu-latest]
    arch: [x64, arm64]
    exclude:
      - os: ubuntu-latest
        arch: arm64   # unless specifically needed
```

---

## Notarization (macOS) CI Flow

```
Build → Sign (Developer ID cert) → Notarize (Apple servers) → Staple → Package DMG
```

**Notarization timing:** 1–5 minutes. CI pipeline must wait for approval before stapling.

**Stapling:** Required for offline Gatekeeper verification. Unstapled apps require network on first launch.

---

## CI Build Gates

Before any release:
1. TypeScript: `tsc --noEmit` — zero errors
2. Tests pass (including integration tests with real Electron process)
3. Build succeeds on all declared OS targets
4. Code signing completes without error (exit 0 from signing tool)
5. Notarization approved (macOS)
6. Auto-updater manifest (`latest.yml`) generated and signed
7. Startup time measured: `time ./AppName --version` or equivalent
8. Installer smoke test: install → launch → basic functionality → uninstall
