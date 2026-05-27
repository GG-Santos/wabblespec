# L7 — Release

Release and operations layer. L7 modules close out a pipeline run, publish artifacts, and manage the operational lifecycle of deployed software.

## Modules

| Module | Role |
|--------|------|
| `archive` | Closes the pipeline run. Aggregates all receipts into a delivery receipt. Bumps VERSION. Appends CHANGELOG entry. Core pipeline module — every run ends here. |
| `changelog` | Generates or updates the CHANGELOG. Reads from run receipts. Idempotent — safe to re-run for the same version range. Requires `from_ref` and `version` declared. |
| `commit` | Creates a git commit from staged changes. Never passes `--no-verify`. Hook failures surface to human. Not idempotent. |
| `deploy` | Deploys built artifacts to a target environment. Requires environment declared. |
| `package` | Packages built artifacts for distribution (npm, pip, docker, binary, etc.). |
| `release` | Orchestrates the full release sequence: package → deploy → publish → changelog → tag. |
| `scaffold` | Generates project scaffolding: directory structure, boilerplate files, CI configuration. |
| `monitor` | Observability and alerting setup. Configures monitoring for deployed services. |

## Key behaviors

**Archive** is mandatory. No pipeline run is complete without an Archive delivery receipt. Archive has exclusive write authority over `.wabblespec/VERSION` — no other module may bump the version.

**Commit** enforces two hard rules:
1. Never passes `--no-verify` — hooks must run
2. Hook failures surface to human — commit halts, does not retry

**Release** is the orchestrator for the full publish sequence. It calls Package, Deploy, Changelog, and Commit in order. A failure at any step halts the sequence and requires human resolution.

**Scaffold** runs at project initiation, not during an ongoing pipeline. It is idempotent for new files but never overwrites existing files — it skips any file that already exists.

## VERSION bump rules

Archive applies these rules (worst signal wins):

| Signal | Bump |
|--------|------|
| Any `change_class: BREAKING` in session | Major (`x.0.0`) |
| Any `change_class: ADDITIVE` or `DEPRECATION`, no BREAKING | Minor (`0.x.0`) |
| Only COSMETIC or unclassified | Patch (`0.0.x`) |

## Layer rules

- Archive must always run — a task is not done until the delivery receipt exists
- Commit never skips hooks — `--no-verify` is prohibited
- Release never force-pushes — any push operation that would require `--force` halts and escalates to human
- Deploy requires explicit environment declaration — no implicit target environments
- Changelog is idempotent; all other L7 modules are not
