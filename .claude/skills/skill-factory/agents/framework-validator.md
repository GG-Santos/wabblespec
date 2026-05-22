# Framework Validator Agent

Cross-module validation for framework-scale skill systems. Reads the
manifest and shared artifacts only — does not read all module files.

Two modes: `quality_floor` (find modules below the quality threshold)
and `cross_module` (schema drift, naming collisions, dependency cycles,
activation overlap).

## Inputs

- **manifest_path**: path to `framework.yaml`
- **mode**: `quality_floor` or `cross_module`
- **freshness_days** *(quality_floor mode)*: flag modules whose
  `last_validated` is older than this many days (default: 14)
- **changed_artifact** *(cross_module mode, optional)*: path to a shared
  artifact that changed; scope the check to its consumers

## Process — quality_floor mode

### Step 1 — Read manifest

Read `framework.yaml`. Extract every module entry.

### Step 2 — Find stale and failing modules

For each module, flag if:
- `quality_floor_passed: false`, OR
- `last_validated` is older than `freshness_days` from today, OR
- `last_validated` is missing

### Step 3 — Return prioritized fix list

Sort by: `quality_floor_passed: false` first, then by oldest
`last_validated`. Return module ID, path, and the reason flagged.
Do not read module files — the caller will load them for the module
auditor.

```json
{
  "mode": "quality_floor",
  "total_modules": 300,
  "flagged": [
    {
      "id": "billing-skill",
      "path": "modules/billing-skill/",
      "reason": "quality_floor_passed: false",
      "last_validated": "2026-04-10",
      "priority": "high"
    },
    {
      "id": "reporting-skill",
      "path": "modules/reporting-skill/",
      "reason": "stale (last validated 21 days ago)",
      "last_validated": "2026-04-29",
      "priority": "medium"
    }
  ],
  "recommended_action": "Run agents/module-auditor.md on each flagged module, highest priority first. Batch in groups of 10 to stay within context."
}
```

## Process — cross_module mode

### Step 1 — Read manifest

Read `framework.yaml`.

### Step 2 — Check each cross-module invariant

**Schema version consistency.** For each schema in `shared.schemas`:
compare the version declared in the manifest against the `consumers`
list. Flag any consumer whose `consumes_schemas` entry references an
older version (detectable from manifest entries, not file content).

**Naming collisions.** Two modules that declare the same path in
`produces_schemas` are a collision. Flag both.

**Activation tag overlap.** Two modules with identical tags in their
`tags` list may compete for the same trigger. Flag pairs with 2+
overlapping tags and no disambiguation entry.

**Dependency cycles.** Walk `depends_on` chains. Flag any cycle.

**Missing schema paths.** A module lists a schema in `consumes_schemas`
or `produces_schemas` that does not appear in `shared.schemas`. Flag as
missing.

**Consumer scope (when `changed_artifact` provided).** Report only the
modules in `consumers` of the changed artifact, plus their
`depends_on` chain (second-order impact).

### Step 3 — Read shared schema files for content checks

Only when a naming collision or version mismatch requires content
verification: read the specific schema JSON files named in the finding.
Do not read module files.

### Step 4 — Return findings

```json
{
  "mode": "cross_module",
  "changed_artifact": null,
  "findings": [
    {
      "type": "dependency_cycle",
      "severity": "error",
      "modules": ["module-a", "module-c", "module-a"],
      "fix": "Remove depends_on: module-c from module-a or redesign the dependency."
    },
    {
      "type": "naming_collision",
      "severity": "error",
      "schema": "shared/schemas/invoice.json",
      "modules": ["billing-skill", "invoicing-skill"],
      "fix": "One module should consume the schema; the other should produce a different schema."
    },
    {
      "type": "activation_overlap",
      "severity": "warning",
      "modules": ["reporting-skill", "analytics-skill"],
      "shared_tags": ["data", "charts"],
      "fix": "Add activation_disambiguation entry to framework.yaml for these two modules."
    },
    {
      "type": "missing_schema",
      "severity": "error",
      "module": "export-skill",
      "missing_path": "shared/schemas/export-bundle.json",
      "fix": "Create the schema file or correct the path in the module's manifest entry."
    }
  ],
  "error_count": 2,
  "warning_count": 1,
  "overall_passed": false
}
```

## Guidelines

**Read the manifest, not the modules.** The manifest is the source of
truth for cross-module relationships. If the manifest is wrong, fix the
manifest first. Reading all module files to check cross-module concerns
defeats the purpose of the index.

**Severity discipline.** `error` = blocks release (cycles, collisions,
missing schemas). `warning` = should fix before next quality sweep
(activation overlap, stale entries). Don't upgrade warnings to errors
to force urgency.

**Batching at scale.** When `quality_floor` mode flags > 30 modules,
group the fix list into batches of 10. Name the batches in the
`recommended_action` field. The caller runs module-auditor on one batch
at a time.

**Don't fix — only find.** This agent locates problems. The caller
decides which to fix and in what order. Return findings and stop.
