# Module Plan — Recipe (L0)

**Tier:** 1 — CRITICAL
**Layer:** L0 Intake
**v5.3 origin:** BuildType (renamed Recipe)

---

## Purpose

Identify build target before any other decision. Target routes everything downstream: platform package, spec template variant, capability gateways, engineering split, security split, verification gates. Nothing loads before Recipe fires.

---

## Activation

Gate 1 (Recipe gate) — fires at session start. Does not use `skill-rules.json` pattern matching. It IS the gate.

Fires again when:
- Build target is explicitly changed mid-session
- Project signals conflict with declared target (Ground detects mismatch)

---

## Detection Signals

Recipe reads project signals in priority order. First confident match wins.

| Priority | Signal | Example |
|---|---|---|
| 1 | Existing `.wabblespec/recipe.json` | Previously declared target |
| 2 | Design Document file present | `GDD.md`, `PRD.md`, `FDS.md` |
| 3 | Platform-specific config files | `package.json` + DOM imports = Web, `Cargo.toml` + `no_std` = IoT |
| 4 | Directory structure patterns | `src/routes/` = Web/API, `Assets/` + `Scenes/` = Game |
| 5 | User intent in opening message | "I'm building a CLI tool" |
| 6 | No confident signal | Ask via Interview |

### Per-Target Detection Rules (outline — full rules in `rules/target-detection.md`)

| Target | Strong signals |
|---|---|
| Web | `package.json` + React/Vue/Next/Svelte/Angular imports, `index.html`, `vite.config`, `webpack.config` |
| API/Service | `package.json` + Express/Fastify/FastAPI/Gin, no frontend framework, OpenAPI spec |
| Game | Unity `Assets/`, Godot `project.godot`, `GDD.md`, Unreal `.uproject` |
| Mobile | `ios/`, `android/`, `pubspec.yaml` (Flutter), `Expo` config, `React Native` config |
| Desktop | `electron.js`, `tauri.conf.json`, `src-tauri/` |
| CLI | `bin/` entry in `package.json`, `click` / `cobra` / `clap` imports, `cmd/` directory |
| IoT/Embedded | `no_std`, `CMakeLists.txt` + embedded target, `micropython`, `platformio.ini` |
| Library/Package | No `main` entry, `lib.rs` or `index.ts` export-only, registry publish config |
| Extension/Plugin | `manifest.json` with `manifest_version`, `.vscodeignore`, `plugin.xml` |
| Data/Pipeline | Airflow DAGs, dbt models, Spark jobs, `pipeline.yaml`, `etl/` directory |
| AI/Agent | LangChain/LlamaIndex imports, agent loop structure, eval harness, `prompts/` directory |

### Multi-Target Projects

Monorepos or projects with multiple targets are flagged. Recipe declares a PRIMARY target for the session. Secondary targets are noted in `recipe.json` but do not load their platform packages until explicitly switched.

If primary target is ambiguous across two candidates: ask user.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| `recipe.json` | `.wabblespec/recipe.json` | Declared target, detection method, session lock |
| Loaded platform package | `.wabblespec/modules/platform/<TARGET>/` | Active for session |
| Spec template variant | Declared in `recipe.json` | Used by Specify at P1 |
| Recipe receipt | `.wabblespec/receipts/recipe-receipt.md` | Operational artifact for downstream |

### recipe.json structure

```json
{
  "target": "Web|API-Service|Game|Mobile|Desktop|CLI|IoT-Embedded|Library-Package|Extension-Plugin|Data-Pipeline|AI-Agent",
  "detection_method": "file-signals|user-declaration|interview|existing-recipe",
  "confidence": 0.0,
  "secondary_targets": [],
  "spec_template": "WDD|SDD|GDD|PRD|FDS|PDD|SAD|ASD",
  "collapse_eligible": false,
  "locked_at": "timestamp",
  "session_id": "string"
}
```

---

## Workflow

```
1. Read .wabblespec/recipe.json if exists
   -> IF exists AND not expired: load target, skip detection, write receipt
   -> IF exists AND expired: re-detect, confirm or update

2. Run detection signal scan (priority order above)
   -> IF confident match (confidence >= 0.8): declare target
   -> IF ambiguous (two targets >= 0.6): present candidates, ask user
   -> IF no signal: ask user via Interview mini-flow

3. Write recipe.json with target, method, confidence, timestamp

4. Load platform package for declared target

5. Declare spec template variant

6. Set collapse_eligible based on Decompose complexity threshold

7. Write Recipe receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration spec |
| `skill-rules.json` | Required | Authority declaration (owns: recipe.json, target declaration) |
| `rules/target-detection.md` | Rules | Full detection rules per target |
| `rules/multi-target.md` | Rules | Monorepo and multi-target handling |
| `schemas/recipe.schema.json` | Schema | recipe.json validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension (adds: target, detection_method, confidence) |
| `references/target-signals.md` | Reference | Canonical signal list per target |

---

## Integration Points

| Module | Relationship |
|---|---|
| ScopeFrame | Reads recipe.json to set session boundaries |
| Specify | Reads spec_template from recipe.json |
| All platform packages | Recipe loads the active one |
| Interview | Recipe delegates ambiguous detection to Interview mini-flow |
| Decompose | Reads collapse_eligible from recipe.json |
| Verifier | Reads target from recipe.json for target-specific gates |
| Ground | Can trigger Recipe re-fire if target mismatch detected |

---

## Verification Mode

**Observation** — target is declared, recipe.json exists, platform package is loaded, spec template is set. No automation required. Verifier observes state.

---

## Receipt Extension Fields

Beyond base receipt schema:

```json
{
  "target": "string",
  "detection_method": "string",
  "confidence": "number",
  "secondary_targets": "array",
  "spec_template": "string",
  "collapse_eligible": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 BuildType | v6.1 Recipe |
|---|---|
| 6 targets (Web, Game, Mobile, Desktop, CLI, IoT) | 11 targets (+API/Service, Library/Package, Extension/Plugin, Data/Pipeline, AI/Agent) |
| Routed to Development gateway | Routes to Platform package (Development gateway distributed) |
| No multi-target handling | Primary + secondary target model |
| No recipe.json persistence | recipe.json persists across sessions |
| No collapse_eligible | collapse_eligible declared at intake |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| recipe.json expiry | Session-scoped only vs. persists until target changes | Per-module planning |
| Multi-target switching UX | Explicit command vs. auto-detect on file open | Per-module planning |
| Confidence threshold for auto-declare | 0.8 (proposed) vs. adjustable | Per-module planning |
