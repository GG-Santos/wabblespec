# Contributing

How to add a module, pass the quality floor, and run a pipeline seed run.

## Adding a module

### 1. Create the module directory

```
modules/l{N}/{name}/
  SKILL.md
  skill-rules.json
  rules/          (optional)
  schemas/        (optional)
```

Layer determines placement. If unsure: L1 for analysis/planning tools, L2 for control/enforcement, L6 for output polish, L7 for delivery/release.

### 2. Write SKILL.md

Required YAML frontmatter:
```markdown
---
name: {module-id}
description: {one sentence, 20+ characters, no hedging}
---
```

Required sections (headings must be exact):
- `## What this skill does`
- `## When to use`
- One of: `## Output`, `## What this produces`, `## Produces`, `## Receipt`, `## Writes`

Body must be at least 200 characters after the frontmatter.

### 3. Write skill-rules.json

Required fields:
```json
{
  "module": "{module-id}",
  "layer": "L{N}",
  "tier": 1,
  "activators": ["/module-name", "trigger phrase"],
  "authority": {
    "owns": [".wabblespec/receipts/{module}-receipt-*.json"],
    "reads": []
  },
  "verification_mode": "Observation",
  "receipt_required": true
}
```

`tier` values: 1 = core/pipeline module, 2 = analysis/support, 3 = polish/delivery.
`verification_mode` values: `Observation`, `Audit`, `None`.
`activators` must be non-empty unless `loading_gate` or `commands` is present.

### 4. Register in framework.yaml

Add an entry under `modules:`:
```yaml
- id: {module-id}
  layer: L{N}
  build_status: built
  depends_on: []
  quality_floor_passed: true
  last_validated: "YYYY-MM-DD"
```

If the module consumes a shared file, add the module ID to that file's `consumers` list.

### 5. Run quality floor check

```bash
python _shared/scripts/quality-floor-check.py --framework framework.yaml --module {module-id} --verbose
```

All 14 checks must PASS before the module is considered built.

### 6. Run validate-graph

```bash
python _shared/scripts/validate-graph.py --framework framework.yaml
```

Must report 0 violations. Any new `depends_on` or shared file `consumers` entry must reference a valid module ID.

## Running a pipeline seed run

Seed runs accumulate PASS receipts toward the L8 gate (100+ required).

### Naming convention
`seed-run-YYYYMMDD{a|b|c...}` — e.g. `seed-run-20260525a`

### Minimum receipt set per run
recipe → scopeframe → specify → decompose → executor → verifier → delivery (7 receipts)

### Steps
1. Write `recipe-receipt-{run-id}.json` — declare task, platform, complexity
2. Write `scopeframe-receipt-{run-id}.json` — declare scope boundaries
3. Write `specify-receipt-{run-id}.json` — declare spec produced
4. Write `decompose-receipt-{run-id}.json` — declare wave plan + checkpoint
5. Execute the task (waves)
6. Write `executor-receipt-{run-id}.json` — declare waves completed
7. Run verifier checkpoint (e.g. quality-floor-check.py for quality tasks)
8. Write `verifier-receipt-{run-id}.json` — declare checkpoint result
9. Write `delivery-receipt-{run-id}.json` — aggregate, list all receipts
10. Bump VERSION and write CHANGELOG entry

## Quality floor check — common failures

| Failure | Fix |
|---------|-----|
| FRONTMATTER | SKILL.md has UTF-8 BOM or missing `name:`/`description:` in frontmatter |
| SECTION_WHAT | Heading is `## What this module does` instead of `## What this skill does` |
| REQUIRED_FIELDS | skill-rules.json missing one of the 7 required fields |
| AUTHORITY_OWNS | `authority.owns` is empty array or missing |
| ACTIVATORS_VALID | `activators` is empty and no `loading_gate` or `commands` present |

**BOM note:** Windows text editors often save with UTF-8 BOM. The checker handles this via `utf-8-sig` encoding. If adding SKILL.md files from external sources, verify frontmatter starts with `---` not `\xef\xbb\xbf---`.
