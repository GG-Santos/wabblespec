# Game Engineering — Build Toolchain

## Unity

**Build pipeline:** Unity Cloud Build (CI) or local build via `Unity -batchmode -buildTarget`.

```bash
# Headless build:
Unity -batchmode -nographics -quit \
  -projectPath . \
  -buildTarget StandaloneWindows64 \
  -executeMethod BuildScript.BuildWindows \
  -logFile build.log

# Asset bundle build:
Unity -batchmode -executeMethod BuildScript.BuildAssetBundles
```

**Addressables:** Use for asset streaming. Build player + content separately. Content can update without full player update.

**Platform builds:** Each platform requires its own build target. Texture compression varies per platform — Unity generates platform-specific variants automatically.

---

## Unreal Engine

```bash
# Build (Unreal Build Tool):
./Engine/Build/BatchFiles/RunUAT.sh BuildCookRun \
  -project="MyGame.uproject" \
  -platform=Win64 \
  -configuration=Shipping \
  -cook -stage -pak -archive \
  -archivedirectory="./Build/Win64"
```

**Cooking:** Must cook content for each target platform. Cooking converts raw assets to platform-optimized formats.

**Shipping vs Development:** Shipping = no debug symbols, no console, smaller binary. Development = profiling enabled.

---

## Godot

```bash
# Export (headless):
godot --headless --export-release "Windows Desktop" build/game.exe
godot --headless --export-release "Linux/X11" build/game.x86_64
godot --headless --export-release "macOS" build/game.dmg
godot --headless --export-release "Android" build/game.apk
```

**Export templates:** Must download and install official export templates for target platforms.

---

## Asset Pipeline

**Source assets:** Never committed in source format if binary > 1MB — use Git LFS.

**Build-time processing:**
1. Import source assets (textures, audio, meshes)
2. Compress per platform (BC7/PC, ASTC/mobile)
3. Generate MIP maps for textures
4. Pack into asset bundles / PAK files
5. Generate asset manifest with sizes and hashes

**Asset bundle strategy:**
- Core bundle (loaded at startup): UI textures, common audio
- Level bundles (loaded per level): geometry, level-specific assets
- DLC bundles (optional download): additional content

---

## CI Build Gates

Before any playtest/release build:
1. Build succeeds for all declared platforms (zero compile errors)
2. No asset import errors in build log
3. Build size within declared budget per platform
4. Smoke test: game launches and reaches main menu in < declared time
5. Frame rate test: benchmark scene runs at ≥ target fps on minimum spec
6. Save/load test: save → quit → load → verify state matches
7. Code signing (where required): valid certificate, notarized (macOS)
8. Platform certification checklist started (console platforms)
