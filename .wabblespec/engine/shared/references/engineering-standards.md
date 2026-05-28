---
name: engineering-standards
description: WabbleSpec Engineering Standards — naming conventions, file organization, script API contracts, receipt schema versioning, and I/O standards for all framework scripts and modules.
---

# WabbleSpec Engineering Standards

This document is the authoritative reference for framework engineering conventions. All scripts, modules, and skills MUST conform. The module auditor (`agents/module-auditor.md`) checks structural compliance; this document governs the deeper API and naming contract.

---

## 1. Naming Conventions

### Scripts

All scripts in `engine/shared/scripts/` follow kebab-case:

```
<domain>-<operation>.py          # archive.py, version-bump.py
<domain>-<subject>.py            # guard-check.py, receipt-writer.py
<subject>-<action>.py            # wave-queue.py, session-registry.py
```

No abbreviations that are not universally understood. `db` = database, `cfg` = config (acceptable). `rcpt` = not acceptable.

### Modules

Module directories: `engine/modules/l{N}/{name}/`
- `N` = layer number (0–8)
- `name` = kebab-case, matches the `name:` field in SKILL.md frontmatter

### State files

Session-scoped: `state/sessions/{session-id}/{artifact}`
Non-session: `state/{artifact}` (single-terminal assumption)
Archive: `state/archive/{artifact}`
Daemons: `state/daemons/{artifact}`
Queue: `state/queue/{artifact}`
Receipts: `state/receipts/{artifact}.json`

---

## 2. Script API Conventions

Every script in `engine/shared/scripts/` MUST implement:

### Required flags

| Flag | Purpose |
|---|---|
| `--dry-run` | Print what would be written without touching any file. Exit 0. |
| `--help` | Standard argparse help. |

### Optional but strongly encouraged

| Flag | Purpose |
|---|---|
| `--json` | Emit output as JSON instead of human-readable text (for pipe-to-script use). |
| `--session-id` | Scope the operation to a specific session. |

### Exit codes (standard across all scripts)

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Logical failure — bad arguments, validation error, not found, condition not met |
| 2 | I/O or infrastructure failure — file not readable, directory not writable, dependency missing |

### Docstring format

Every script opens with a triple-quoted module docstring containing:
1. One-sentence description of purpose
2. `Replaces:` (what manual step or token cost this eliminates)
3. `Usage:` block with at least two examples (minimal + full)
4. Exit codes table

---

## 3. Receipt Schema Versioning

All receipts include a `schema_version` field. Current version: **1**.

```json
{
  "schema_version": 1,
  "module": "string",
  "session_id": "string",
  "status": "PASS | FAIL | PARTIAL | BLOCKED",
  "timestamp": "ISO-8601"
}
```

**Versioning rules:**
- Additive fields (new optional field): no version bump required
- Renamed or removed fields: bump schema_version, write migration note to `state/archive/schema-migrations.md`
- Breaking schema change: bump schema_version AND emit a Shift cascade

**Validation:** `receipt-writer.py --validate <path>` checks base schema. `agent-output-validator.py --type <type>` checks type-specific fields.

---

## 4. I/O Contracts

### Reading framework state

Scripts MUST NOT read CHANGELOG.md, VERSION, or receipt-index.json into memory for transformation. Use the delegation scripts:
- `archive.py` — CHANGELOG + VERSION + receipt-index (write-only append)
- `receipt-db.py query` — query receipt history without loading JSON files

### Writing framework state

All writes to framework paths (`.wabblespec/CHANGELOG.md`, `.wabblespec/VERSION`, `state/receipts/*.json`) MUST use the delegation scripts defined in `engine/shared/references/script-delegation-contract.md`.

Direct `Write` or `Edit` tool calls to these paths are a Guard Layer 3 invariant violation (I11).

### File locking

Any script that writes a shared state file in a concurrent-safe scenario MUST use the `FileLock` pattern from `wave-queue.py`:

```python
with FileLock(lock_path, timeout=5):
    data = load(...)
    mutate(data)
    save(data)
```

---

## 5. Module File Structure

Every module directory MUST contain:

```
engine/modules/l{N}/{name}/
  SKILL.md               # system prompt — max 500 lines
  skill-rules.json       # activators, authority, collapse_eligible
  rules/
    cold-start.md        # required — one-page session startup guide
  schemas/               # optional — module-specific receipt schemas
  scripts/               # optional — module-specific Python scripts
  references/            # optional — reference documents (loaded on demand)
```

SKILL.md MUST contain:
- YAML frontmatter with `name:` and `description:`
- `## What this skill does` section
- `## Reference Routing` section (if the skill delegates any writes)
- `## How to do it` section with numbered steps
- `## Output contract` section with exact path and schema
- `## A note on common failure modes` with at least two named failure modes

---

## 6. Script Dependency Policy

All scripts in `engine/shared/scripts/` MUST be importable without external dependencies beyond:
- Python 3.8+ stdlib
- `pyyaml` (for YAML parsing)
- `duckdb` (receipt-db.py only)
- `anthropic` (llm-eval.py only — SDK for API calls)

New external dependencies require a `requirements.txt` entry in `engine/shared/scripts/` and explicit documentation in the script's docstring.

---

## 7. Framework vs. Product Boundary (I11)

The boundary is enforced by `skill-rules.json` → `product_space: true`:

```json
{
  "authority": {
    "owns": ["src/**", "tests/**"]
  }
}
```

Product-space modules own files outside `.wabblespec/`. Framework modules own files inside `.wabblespec/`. No module owns both.

Guard Layer 4 (`guard-check.py authority`) enforces this at wave-plan time.

---

## Cross-references

- Script delegation contract: `engine/shared/references/script-delegation-contract.md`
- Skill writing contract: `engine/shared/references/skill-writing-contract.md`
- Session isolation: `engine/shared/references/session-isolation.md`
- Background daemons: `engine/shared/references/background-daemons.md`
- Agents architecture: `engine/shared/references/agents-architecture.md`
- Quality floor gates: `engine/shared/references/quality-floor-gates.md`
