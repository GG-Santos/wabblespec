---
name: scaffold
description: Generates initial project structure from a platform target. Runs once per project — idempotency guard refuses if project-map.md already exists. Triggers Explore after generation to index what was created.
---

# Scaffold

You generate the initial structure of a new project. You run exactly once per project. You refuse to run if the project already exists. You trigger Explore after generation so the fresh structure is immediately indexed and usable.

## What this skill does

Generates initial project structure from a platform target. Runs once per project — idempotency guard refuses if project-map.md already exists. Triggers Explore after generation to index what was created.

## When to use / when not to use

**Use when:**
- Starting a brand new project with no existing structure
- Platform target is known (CLI, Web, API-Service, Mobile, IoT, etc.)
- `.wabblespec/project-map.md` does not exist

**Do not use when:**
- `.wabblespec/project-map.md` already exists — hard refuse with `PROJECT_ALREADY_EXISTS`
- Adding a feature to an existing project (use Executor)
- Migrating an existing codebase (use Migrate)

## Idempotency guard

```
Before any file generation:
  IF .wabblespec/project-map.md exists:
    FAIL with PROJECT_ALREADY_EXISTS
    Message: "Project already scaffolded. Use Executor for features, Migrate for structural changes."
    Do not overwrite. Do not merge. Stop.
```

This is the only guard needed. The map file's existence is the canonical signal that Scaffold has run.

## Inputs

- Platform target (required): CLI | Web | API-Service | Library | Extension | Desktop | Mobile | Data-Pipeline | AI-Agent | Game | IoT
- Language (optional — defaults to platform convention if omitted)
- Project name
- Author / org name

## How to do it

### Step 1 — Idempotency check

Check for `.wabblespec/project-map.md`. If exists: FAIL immediately (see above).

### Step 2 — Load platform template

Route to platform module for structure definition:

| Platform | Primary language | Structure source |
|---|---|---|
| CLI | Node/Python/Go/Rust | L3/cli template |
| Web | Node/TypeScript | L3/web template |
| API-Service | Node/Python/Go/Java | L3/api-service template |
| Library | Target language | L3/library template |
| Extension | JavaScript | L3/extension template |
| Desktop | Node (Electron) / Rust (Tauri) | L3/desktop template |
| Mobile | RN / Flutter | L3/mobile template |
| Data-Pipeline | Python/SQL | L3/data-pipeline template |
| AI-Agent | Python/Node | L3/ai-agent template (requires L4/ai) |
| Game | Target engine language | L3/game template |
| IoT | C/C++/Rust | L3/iot template |

### Step 3 — Generate project structure

Create directories and starter files. Minimum set:

```
{project-name}/
  src/                    # source root
  tests/                  # test root
  .wabblespec/
    project-map.md        # written last — idempotency sentinel
    receipts/
    memory/
    VERSION               # initialized to "0.1.0"
    CHANGELOG.md          # initialized with header only
  README.md               # minimal — project name + platform
  .gitignore              # platform-appropriate
  {build-config}          # package.json / pyproject.toml / Cargo.toml / CMakeLists.txt
  {lint-config}           # eslint / ruff / clippy / etc.
```

Platform-specific additions loaded from L3 module templates.

**Write `project-map.md` last.** If generation fails mid-way, absence of project-map.md means Scaffold can be re-run cleanly.

### Step 4 — Write project-map.md

`.wabblespec/project-map.md`:
```markdown
# Project Map

**Project:** {name}
**Platform:** {platform}
**Language:** {language}
**Scaffolded:** {ISO-8601 timestamp}
**WabbleSpec version:** {VERSION from root}

## Structure

{directory tree of what was generated}

## Next steps

- Run Explore to index the project
- Fill in design-document.md prerequisites
- Run Recipe to detect platform and load skill modules
```

### Step 5 — Trigger Explore

After all files written: invoke Explore to index the newly created structure. Explore's output populates the initial project understanding. Do not skip — Scaffold without Explore leaves the project unindexed.

### Step 6 — Write scaffold receipt

## Output contract

**scaffold-receipt** (`.wabblespec/receipts/scaffold-receipt-{timestamp}.json`):
```json
{
  "project_name": "string",
  "platform": "string",
  "language": "string",
  "files_created": "integer",
  "directories_created": "integer",
  "explore_triggered": "boolean"
}
```

## Common failure modes

1. **Running on an existing project.** The idempotency guard exists because partial scaffolding on an existing project causes divergence. The guard is not optional.

2. **Writing project-map.md first.** If written first and generation fails, the guard blocks re-runs and the project is stuck. Always write project-map.md last.

3. **Skipping Explore.** A freshly scaffolded project that hasn't been indexed is opaque to subsequent Recipe and Executor runs. Always trigger Explore.
