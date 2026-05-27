# Memory Drawer Schema Version

Current declared schema version: **1**

---

## Version History

| Version | Date | Change |
|---|---|---|
| 1 | 2026-05-22 | Initial schema. Fields: id, wing, room, content, status, written_at, expires_at, last_verified, confidence, source, schema_version, wabblespec_schema_version, tags |

---

## Schema Version Field

Every drawer written by the Memory module must include:

```json
{
  "schema_version": 1,
  "wabblespec_schema_version": 1
}
```

Both fields carry the same integer value. `schema_version` is the WabbleSpec Memory field. `wabblespec_schema_version` is the WabbleSpec metadata field stored in ChromaDB.

---

## MemoryMine Behavior on Version Mismatch

MemoryMine reads this file to get `CURRENT_SCHEMA_VERSION`. Any drawer with `wabblespec_schema_version < CURRENT_SCHEMA_VERSION` is flagged as `NEEDS_REBUILD` and excluded from cluster and pattern analysis.

Drawers are never purged automatically. Rebuild is a human-triggered re-write via the Memory module.

---

## Bumping the Version

When a schema change is required:

1. Increment the version number in this file
2. Update the version history table with date and change description
3. Update `CURRENT_SCHEMA_VERSION` constant in `modules/l5/memory-mine/scripts/memory-mine.py`
4. On next MemoryMine run, all older drawers will appear as `NEEDS_REBUILD` in staleness-map
5. Re-write affected drawers via Memory module to migrate them forward
