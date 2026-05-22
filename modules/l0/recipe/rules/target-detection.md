# Target Detection Rules

Lookup table for Recipe signal scanning. Work through priorities in order. Stop at the first confident match (confidence ≥ 0.8).

---

## Priority 1 — Existing recipe.json

If `.wabblespec/recipe.json` exists and `session_id` matches the current session: load it. Confidence = 1.0. Skip all other detection.

If `session_id` does not match: run detection from Priority 2. The old recipe.json may inform but does not lock.

---

## Priority 2 — Design Document

| Document | Target |
|---|---|
| `GDD.md` or `game-design-document.*` | Game |
| `PRD.md` or `product-requirements.*` | Web or API-Service (check for frontend signals to distinguish) |
| `FDS.md` or `functional-design.*` | API-Service or CLI |
| `ASD.md` or `architecture.*` | API-Service |
| `SAD.md` or `system-architecture.*` | API-Service |

Confidence from design document: 0.85. Requires corroborating signal from Priority 3 or 4 to reach 0.95.

---

## Priority 3 — Platform config files

| File | Target | Confidence |
|---|---|---|
| `package.json` + React/Vue/Next/Svelte/Angular imports | Web | 0.9 |
| `package.json` + Express/Fastify/Koa + no frontend framework | API-Service | 0.85 |
| `Cargo.toml` + `no_std` feature | IoT-Embedded | 0.9 |
| `Cargo.toml` (standard, with binary target) | CLI | 0.75 |
| `pubspec.yaml` | Mobile (Flutter) | 0.9 |
| `expo.config.*` or `app.json` with Expo | Mobile | 0.9 |
| `electron.js` or `electron-builder.yml` | Desktop | 0.95 |
| `tauri.conf.json` or `src-tauri/` | Desktop | 0.95 |
| `platformio.ini` or `CMakeLists.txt` + embedded target | IoT-Embedded | 0.9 |
| `micropython` references | IoT-Embedded | 0.9 |
| `manifest.json` with `manifest_version` key | Extension-Plugin (browser) | 0.9 |
| `.vscodeignore` or `vsce` dependency | Extension-Plugin (VS Code) | 0.9 |
| `plugin.xml` | Extension-Plugin (other) | 0.85 |
| `openapi.yaml` or `swagger.json` at root | API-Service | 0.85 |
| `dbt_project.yml` | Data-Pipeline | 0.95 |
| `airflow_dag*.py` or `dags/` directory | Data-Pipeline | 0.9 |
| `requirements.txt` + `langchain`/`llama_index`/`openai` imports | AI-Agent | 0.85 |

---

## Priority 4 — Directory structure patterns

| Pattern | Target | Confidence |
|---|---|---|
| `src/routes/` + `src/components/` | Web | 0.75 |
| `src/routes/` + no frontend framework | API-Service | 0.7 |
| `Assets/` + `Scenes/` (Unity) | Game | 0.9 |
| `project.godot` present | Game | 0.95 |
| `.uproject` present | Game | 0.95 |
| `ios/` + `android/` directories | Mobile | 0.85 |
| `bin/` entry in `package.json` | CLI | 0.8 |
| `cmd/` directory (Go convention) | CLI | 0.75 |
| `lib.rs` or `index.ts` as only export, no `main` | Library-Package | 0.75 |
| `prompts/` + `evals/` + agent loop code | AI-Agent | 0.8 |
| `pipeline/` or `etl/` directories | Data-Pipeline | 0.7 |

---

## Priority 5 — User intent in opening message

Scan for explicit target statements:
- "I'm building a CLI tool" → CLI, confidence 0.9
- "This is a web app" / "React app" / "Next.js project" → Web, confidence 0.9
- "REST API" / "FastAPI service" / "backend service" → API-Service, confidence 0.9
- "game" / "Unity" / "Godot" → Game, confidence 0.85
- "mobile app" / "iOS" / "Android" / "Flutter" → Mobile, confidence 0.85
- "desktop app" / "Electron" / "Tauri" → Desktop, confidence 0.9
- "VS Code extension" / "browser extension" / "plugin" → Extension-Plugin, confidence 0.85
- "library" / "npm package" / "SDK" → Library-Package, confidence 0.85
- "data pipeline" / "ETL" / "dbt" → Data-Pipeline, confidence 0.9
- "AI agent" / "LLM app" / "chatbot" / "RAG" → AI-Agent, confidence 0.85

---

## Ambiguity resolution

If two targets both score ≥ 0.6 after all priorities: present both candidates to the user and ask for confirmation. Do not auto-declare.

Common ambiguous pairs and distinguishing questions:
- Web vs API-Service: "Does this have a browser UI, or is it consumed by other services/CLIs?"
- CLI vs Library-Package: "Is this invoked from the terminal by a user, or imported as a dependency?"
- Mobile vs Desktop: "Is this running on a phone/tablet, or a desktop/laptop OS?"
- AI-Agent vs API-Service: "Is the core value an LLM reasoning loop, or is the LLM a feature inside a conventional service?"

---

## Multi-target projects

If the project has both a frontend and backend under one repo:
1. Declare primary target as the one the current session is focused on
2. List the other as `secondary_targets` in recipe.json
3. Note: secondary target platform packages do not load until explicitly switched

Ask user to confirm which target is in scope for this session if both are active.
