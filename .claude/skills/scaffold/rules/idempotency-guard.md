# Scaffold Idempotency Guard

Scaffold generates initial project structure exactly once. It refuses to run if the project is already initialized.

---

## Primary Guard: project-map.md

Before generating any files, Scaffold checks:

```
.wabblespec/project-map.md
```

**If file exists:** Scaffold ABORTS immediately.

```
SCAFFOLD BLOCKED: project-map.md already exists at .wabblespec/project-map.md.
This project has already been initialized. Scaffold runs once only.
To add a new platform target, use the platform module directly (modules/l3/<target>/).
To regenerate project structure, delete project-map.md and re-run Scaffold (requires human confirmation).
```

Do not overwrite, do not prompt to continue, do not offer to merge. Hard stop.

**If file does not exist:** Proceed with scaffolding.

---

## Write Order (critical)

Files must be written in this exact order:

1. Platform-specific directories and starter files (from the selected L3 platform module template)
2. `.wabblespec/` directory structure (`receipts/`, `plans/`, `memory/`, `checkpoints/`, `archive/`)
3. `.wabblespec/VERSION` — initial version `0.0.1`
4. `.wabblespec/CHANGELOG.md` — empty with header
5. **Last: `.wabblespec/project-map.md`** — written only after all other files succeed

**Why last:** `project-map.md` is the completion marker. If any earlier step fails, the guard file is not written — Scaffold can be re-run after fixing the failure.

If any file write fails before `project-map.md` is written, Scaffold FAILS and reports which file failed. Do not write `project-map.md` on partial completion.

---

## project-map.md Format

```markdown
# Project Map

Generated: <ISO-8601 timestamp>
Platform: <selected L3 platform target>
Scaffold version: <from modules/l7/scaffold/skill-rules.json version>

## Directory Structure

<tree of generated directories and their purpose>

## Next Steps

1. Run Explore to discover entry points
2. Run Recipe to begin first task
```

---

## Post-Scaffold: Trigger Explore

After writing `project-map.md`, Scaffold signals Explore to run.

Explore traverses from declared entry points, writes findings to Memory as FRESH drawers, and updates `project-map.md` with discovered structure.

Scaffold does not wait for Explore to complete — it signals and closes with PASS. Explore runs as the next stage.

---

## What Scaffold Does NOT Generate

- Test files (Test module handles test generation from spec)
- CI/CD pipeline config (Engineering gateway owns this)
- Security configuration (Security gateway owns this)
- Any file under `project/repo/` that is product code (Apply module writes product code)

Scaffold generates structure only: directories, empty files, `.wabblespec/` infrastructure, and `project-map.md`.
