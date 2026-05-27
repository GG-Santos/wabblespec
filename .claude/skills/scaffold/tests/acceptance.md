# Acceptance Tests — Scaffold (L7)

## AT-SCAF-01: Idempotency guard refuses if project-map.md exists

**Given** `.wabblespec/project-map.md` exists in the target directory
**When** Scaffold is invoked
**Then** Scaffold FAILs immediately with `PROJECT_ALREADY_EXISTS` and a message directing the user to Executor for features or Migrate for structural changes; no file is overwritten or merged

---

## AT-SCAF-02: project-map.md written last

**Given** a Scaffold run generating files
**When** generation is in progress
**Then** `project-map.md` is the final file written; if generation fails mid-way, the absence of `project-map.md` allows a clean re-run

---

## AT-SCAF-03: Explore triggered after generation

**Given** a successful Scaffold run that writes all project files
**When** the last file is written
**Then** Explore is invoked to index the new structure; `explore_triggered: true` in the receipt

---

## AT-SCAF-04: Eleven platform targets supported

**Given** a Scaffold invocation
**When** platform target is declared
**Then** the following are supported: CLI, Web, API-Service, Library, Extension, Desktop, Mobile, Data-Pipeline, AI-Agent, Game, IoT; each routes to the corresponding L3 module template

---

## AT-SCAF-05: Minimum file set includes WabbleSpec infrastructure

**Given** a successful Scaffold run
**When** generated files are examined
**Then** the minimum set includes:
- `src/` directory
- `tests/` directory
- `.wabblespec/project-map.md`
- `.wabblespec/receipts/`
- `.wabblespec/memory/`
- `.wabblespec/VERSION` (initialized to "0.1.0")
- `.wabblespec/CHANGELOG.md`
- `README.md`
- `.gitignore`
- Platform-appropriate build config

---

## AT-SCAF-06: AI-Agent platform requires L4/ai gateway

**Given** a Scaffold invocation with `platform: AI-Agent`
**When** the platform template is loaded
**Then** the L4/ai gateway is included as a required dependency in the project structure

---

## AT-SCAF-07: Receipt contains generation counts

**Given** a completed Scaffold run
**Then** the receipt at `.wabblespec/receipts/scaffold-receipt-{timestamp}.json` contains:
- `project_name`
- `platform`
- `language`
- `files_created`
- `directories_created`
- `explore_triggered`
