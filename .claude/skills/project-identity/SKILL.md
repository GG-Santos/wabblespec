---
name: project-identity
description: Declares and stores the project's visual identity, brand configuration, and aesthetic stance in a project-level identity file. Activates before gateway-aesthetic, gateway-document, or writer when the project has declared brand requirements. Creates `.wabblespec/state/identity.md` as the single source of truth for brand, typography, and tone.
layer: L1
---

# Project Identity

You capture and store the project's brand and aesthetic configuration. You do not design — you interview, record, and make the configuration available to downstream gateways and output skills.

## What this skill does

Creates `.wabblespec/state/identity.md` as the project-level brand configuration file. Downstream modules load this file rather than rediscovering brand decisions each session. Feeds: gateway-aesthetic, gateway-document, writer, report, present.

## When to use

- Project has brand requirements not captured in scope.md
- gateway-aesthetic Phase A requires brand asset input
- gateway-document is producing documents that must match project style
- Explicit `/project-identity` command

## When NOT to use

- `.wabblespec/state/identity.md` already exists and is current — read it, do not re-run
- The project has no visual surface (API/CLI/Library with no document output) — skip

## How to do it

### Step 1 — Check for existing identity file

Read `.wabblespec/state/identity.md`. If FRESH: load it and confirm with user. If absent or STALE: proceed to Step 2.

### Step 2 — Gather identity from user or project

Ask for or infer:
1. **Project name and tagline** — one line
2. **Primary colors** — hex codes or description; minimum: primary + accent
3. **Typography** — heading font / body font (or "use defaults")
4. **Tone** — `professional | conversational | technical | creative` (affects writer and report)
5. **Visual stance** — from gateway-aesthetic: shadow_philosophy, motion_energy, atmosphere
6. **Document defaults** — preferred document format (docx/pdf), page size (letter/A4)

If no brand brief exists: record "undeclared" for each field — downstream gateways use their own defaults.

### Step 3 — Write identity.md

```markdown
# Project Identity

**project_name:** <name>
**tagline:** <tagline or "none">
**locked_at:** <ISO-8601 timestamp>

## Colors

**primary:** <hex>
**accent:** <hex>
**background:** <hex or "white">
**text:** <hex or "black">

## Typography

**heading_font:** <font name or "Arial">
**body_font:** <font name or "Georgia">
**code_font:** <font name or "monospace">

## Tone

**voice:** professional | conversational | technical | creative
**formality:** formal | neutral | casual

## Visual Stance

**shadow_philosophy:** flat | elevated | mixed | undeclared
**motion_energy:** high | moderate | calm | undeclared
**atmosphere:** [list of declared elements or "undeclared"]

## Document Defaults

**preferred_format:** docx | pdf | markdown
**page_size:** letter | A4
**color_theme:** [yes/no — apply brand colors to documents]
```

### Step 4 — Write receipt

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type generic \
  --task-id <task-id> --session-id <session-id> \
  --status PASS \
  --summary "Project identity declared: <project_name>" \
  --out .wabblespec/state/receipts/project-identity-<timestamp>.json
```

## Output contract

- `.wabblespec/state/identity.md` — project brand configuration
- project-identity receipt confirming file written

## Reference Routing

| Situation | Reference |
|---|---|
| Identity receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |
