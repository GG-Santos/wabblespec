# Cold-Start Behavior — Memory

Defines what Memory does when its expected upstream artifacts or storage state are absent.

## Absent: memory store directory

Condition: `memory/` directory does not exist or is empty.
Detection: Directory read returns empty on session open.
Action: Initialize memory store with empty drawer set. Write `memory/index.json` with empty `drawers: []`. Do not error — an empty memory store is a valid starting state.
Do NOT: Fail or block other modules because memory is empty.

## Absent: index.json

Condition: `memory/` exists but `memory/index.json` is missing.
Detection: File read returns 404.
Action: Scan `memory/` for existing drawer directories, reconstruct index from directory contents. Log: "index.json missing — reconstructed from directory scan."
Do NOT: Overwrite existing drawer content during reconstruction.

## Absent: schema version file

Condition: `memory/schema-version.json` missing.
Detection: File read returns 404.
Action: Assume schema version 1 (baseline). Write schema-version.json with `{"version": 1}`. Log: "Schema version not declared — assumed v1."

## Absent: specific drawer requested by another module

Condition: A module (e.g., Nexus, Dream) requests a drawer that does not exist.
Detection: Drawer path resolves to no file.
Action: Return empty result — drawer absent is not an error. Do NOT create the drawer on behalf of the requesting module. Drawer creation requires explicit Memory write operation.

## Absent: staleness thresholds file

Condition: `rules/staleness-thresholds.md` missing when Memory evaluates drawer age.
Detection: File read returns 404.
Action: Apply hardcoded defaults: FRESH < 7 days, STALE > 30 days, ANCIENT > 90 days. Log: "Staleness thresholds file missing — using defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `drawer_count` | 0 |
| `schema_version` | 1 (assumed if file absent) |
| `palace_initialized` | true after first write |
| `staleness_evaluation` | Enabled with defaults if threshold file absent |
| `compression` | Not applied until memory store has 50+ drawers or explicit trigger |
