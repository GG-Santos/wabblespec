# Polish — Excluded Types

Polish cannot run on any of these. Attempting to do so returns `SPEC_VIOLATION`.

| Type | Path pattern | Reason |
|---|---|---|
| Code files | `project/**`, `repo/**` | Apply owns code — Polish has no authority here |
| Schema files | `**/*.json`, `**/*.yaml`, `**/*.yml` | No prose — structural format, not natural language |
| Receipts | `.wabblespec/receipts/**` | Immutable after write — I10 |
| Memory drawers | `.wabblespec/memory/wings/**` | Memory module owns drawer content |
| Plans | `.wabblespec/plans/**` | Plans are operational artifacts — not delivery prose |

## What Polish CAN touch

- SKILL.md files (prose documentation)
- Task spec cards (`.wabblespec/plans/task-card.md`)
- Document module outputs (README sections, CHANGELOG entries, API reference prose)
- Any prose artifact produced by Executor waves that is not in an excluded path
