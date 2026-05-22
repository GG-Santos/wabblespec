# WabbleSpec v6.1 — Delivery

**Layer:** L7 Delivery
**Document scope:** All L7 modules — Archive, Package, Deploy, Release, Scaffold, Monitor
**Depends on:** L6 Expression (Document output), L2 Executor (build output), L2 Verifier (gate passes), L5 Memory (EXPIRED drawer detection), L8 Instinct (receives delivery signals)

---

## Overview

L7 Delivery closes, packages, ships, and records. Where L2 Executor builds and L6 Expression documents, L7 converts completed work into a permanent record and a deployed artifact. Every Delivery operation writes a receipt. Every receipt chains to its predecessors. Nothing ships without Archive having closed the execution first.

Six modules:

| Module | Tier | Purpose |
|---|---|---|
| Archive | 1 — CRITICAL | Close execution, aggregate receipts, bump version, write delivery receipt |
| Package | 3 — SUPPORTING | Sign and version built artifacts for deployment |
| Deploy | 3 — SUPPORTING | Execute deployment to declared environments |
| Release | 3 — SUPPORTING | Git tag, release notes, stakeholder communication |
| Scaffold | 3 — SUPPORTING | Generate initial project structure (once per project lifecycle) |
| Monitor | 3 — SUPPORTING | Generate observability config from SLO declarations post-deploy |

---

## Layer Boundaries

What L7 owns:
- Permanent execution record (Archive delivery receipt)
- Artifact signing and versioning (Package)
- Deployment execution (Deploy)
- Release coordination and git tag (Release)
- Initial project structure generation (Scaffold)
- Observability configuration generation (Monitor)

What L7 does not own:
- Code execution or build (Executor)
- Verification gate decisions (Verifier)
- Application code content (Apply)
- Runtime monitoring operation — Monitor generates config, does not run monitors
- Memory operations — Archive --sweep reads Memory index, but Memory owns drawer lifecycle

Hard boundary: L7 writes delivery artifacts and config files to `project/repo/`. L7 does not modify spec artifacts in `.wabblespec/` (except Archive, which owns `.wabblespec/VERSION`, `.wabblespec/CHANGELOG.md`, and `.wabblespec/receipts/delivery-receipt-*.md`).

---

## Delivery Pipeline Sequence

Normal project delivery follows this sequence:

```
Executor: execution complete (all waves pass Verifier)
  -> Archive: aggregate receipts, bump version, write delivery receipt
  -> Package: sign and version artifact (reads Archive version + receipt)
  -> Deploy: push artifact to declared environment (reads Package manifest)
  -> Monitor: generate observability config (reads Deploy receipt + Engineering SLO)
  -> Release: git tag, release notes, publish (reads Deploy receipt + Archive changelog)
              Attestation required before git tag push
```

Scaffold is not part of this pipeline — it runs once at project creation, before any execution begins.

---

## Archive

**Tier:** 1 — CRITICAL
**v5.3 origin:** Archive module — enriched with --sweep, --entomb modes, Instinct notification replacing Nexus refresh hook

### Purpose

Close and finalize a change. Archive reads all receipts produced during execution, aggregates them into one delivery receipt, bumps the version, writes a changelog entry, and preserves the full provenance trail. Receipts are never deleted — only superseded and archived. Archive is the permanent record of what happened.

### Receipt Aggregation

Archive reads all receipts from `.wabblespec/receipts/` for the current execution session:

| Receipt type | Source files |
|---|---|
| Research receipts | `referenceload-receipt.md`, `memorysearch-receipt.md`, `explore-receipt.md` |
| Plan receipts | `interview-receipt.md`, `scopeframe-receipt.md`, `specify-receipt.md`, `propose-receipt.md`, `decompose-receipt.md` |
| Wave receipts | `wave-<N>-receipt.md` (one per wave) |
| Runtime receipts | `runtime-<timestamp>.md` |
| Verification receipts | `verification-<wave>-<timestamp>.md` |
| Reviewer receipts | `reviewer-receipt-<timestamp>.md` |
| Execution receipt | `execution-receipt.md` |

### Not-Tested Compilation

Archive aggregates all `not_tested` fields from every receipt into one consolidated list. No gaps are hidden. Implied completion is prohibited (I10).

```markdown
## Not Tested

- <item from wave 1 receipt>
- <item from verification receipt>
- <item from apply receipt>
```

Delivery is not blocked by not-tested items — they are recorded, not resolved. Resolution becomes future scope.

### Version Management

Archive bumps version following semantic versioning based on change classifications across receipts:

| Change type | Version bump |
|---|---|
| BREAKING in any receipt | major |
| ADDITIVE only | minor |
| COSMETIC only | patch |

Version written to `.wabblespec/VERSION`. Changelog entry appended to `.wabblespec/CHANGELOG.md`.

Changelog entry format:

```markdown
## [version] — timestamp

### Changed
- <BREAKING or ADDITIVE items from receipts>

### Fixed
- <COSMETIC or correction items>

### Not Tested
- <aggregated not-tested list>

### Receipts
- execution-receipt: <path>
- verification summary: <N waves, N passed, N failed>
```

### Modes

**Default mode:** Aggregate receipts, compose delivery receipt, bump version, write changelog.

**--sweep mode:** Batch entomb stale artifacts. Reads `.wabblespec/memory/index.md` for EXPIRED drawers. Archives them to `.wabblespec/memory/closets/`. Writes sweep receipt listing what was archived.

**--entomb mode:** Archive specific artifact set. Caller declares which artifacts. Archive moves them to `.wabblespec/archive/<timestamp>/`. Writes entomb receipt with provenance note.

### Delivery Receipt Structure

```markdown
# Delivery Receipt

**version:** semver
**timestamp:** ISO 8601
**target:** build target
**stages_completed:** [P1, P2, P3, P4, Execution]
**waves_completed:** integer
**confidence:** aggregate from wave receipts

## Receipts Aggregated

| Receipt | Path | Result |
|---|---|---|
| Research | ... | PASS |
| Plan | ... | PASS |
| Execution | ... | PASS |

## Not Tested

- <consolidated list>

## Change Classification

- BREAKING: integer count
- ADDITIVE: integer count
- COSMETIC: integer count

## Version Bump

- Previous: semver
- New: semver
- Reason: BREAKING|ADDITIVE|COSMETIC
```

### Outputs

| Output | Location | Purpose |
|---|---|---|
| Delivery receipt | `.wabblespec/receipts/delivery-receipt-<timestamp>.md` | Master I10 record |
| VERSION | `.wabblespec/VERSION` | Current version |
| CHANGELOG.md | `.wabblespec/CHANGELOG.md` | Human-readable change history |
| Sweep receipt | `.wabblespec/receipts/sweep-<timestamp>.md` | --sweep audit trail |
| Entomb receipt | `.wabblespec/archive/<timestamp>/entomb-receipt.md` | --entomb audit trail |

All prior receipts remain in `.wabblespec/receipts/`. Archive never deletes — only aggregates and records.

### Workflow

```
1. Receive: execution complete signal from Executor (or explicit /archive command)

2. Read all receipts from .wabblespec/receipts/ for this execution session

3. Aggregate not_tested lists from all receipts

4. Determine version bump from change classifications across all receipts

5. Write changelog entry to .wabblespec/CHANGELOG.md

6. Bump .wabblespec/VERSION

7. Compose delivery receipt

8. Notify Instinct: execution complete, receipts available for pattern tracking

9. If --sweep:
   -> Read memory index for EXPIRED drawers
   -> Archive EXPIRED drawers to closets/
   -> Write sweep receipt

10. If --entomb:
    -> Move declared artifacts to .wabblespec/archive/<timestamp>/
    -> Write entomb receipt

11. Write delivery receipt to .wabblespec/receipts/
```

### Activation

`skill-rules.json` triggers Archive on:
- Executor signals full execution complete (all waves passed Verifier)
- Explicit `/archive` command with target execution
- `--sweep` flag: batch entomb stale artifacts
- `--entomb` flag: archive specific artifact set

### Integration Points

| Module | Relationship |
|---|---|
| Executor | Archive receives execution complete signal from Executor |
| Verifier | Archive reads all verification receipts for delivery record |
| Instinct | Archive notifies Instinct on completion — Instinct reads receipts for pattern tracking |
| Memory | Archive --sweep reads Memory index for EXPIRED drawers |
| Provenance | Archive --entomb records provenance note for archived artifacts |
| Deploy | Deploy reads delivery receipt as prerequisite gate |

### Verification Mode

**Audit** — all required receipts present, not-tested list complete, VERSION bumped, CHANGELOG updated, delivery receipt written with no missing fields.

### Receipt Extension Fields

```json
{
  "receipts_aggregated": 0,
  "not_tested_items": 0,
  "version_previous": "string",
  "version_new": "string",
  "version_bump_reason": "BREAKING|ADDITIVE|COSMETIC",
  "breaking_count": 0,
  "additive_count": 0,
  "sweep_mode": false,
  "artifacts_swept": 0,
  "entomb_mode": false,
  "artifacts_entombed": 0
}
```

### v5.3 Mapping

| v5.3 Archive | v6.1 Archive |
|---|---|
| Close and finalize change | Same |
| Version bump + changelog | Same |
| --entomb mode | Same |
| --sweep mode | Same |
| Nexus refresh hook | Replaced by Instinct notification |
| No consolidated not-tested | not_tested aggregated from all receipts into delivery receipt |

---

## Package

**Tier:** 3 — SUPPORTING
**v5.3 origin:** Package module — artifact preparation and signing before deployment

### Purpose

Prepare and sign deployment artifacts from built output. Package does not build — it receives build output from Executor and produces signed, versioned artifacts ready for Deploy or registry publish. Artifact integrity is guaranteed: no Package receipt = no Deploy activation. Every artifact has a declared provenance chain from source to signed artifact.

### Artifact Types by Build Target

| Build target | Artifact | Signing method |
|---|---|---|
| Web | Static files / Docker image | Docker image signing (cosign), CDN deploy key |
| API/Service | Docker image / binary | cosign or platform signing |
| Mobile (iOS) | .ipa + xcarchive | Apple code signing (Xcode automatic or manual) |
| Mobile (Android) | .aab + .apk | Android keystore |
| Desktop (Electron) | .dmg / .exe / .AppImage | Apple notarization, Windows Authenticode |
| Desktop (Tauri) | Platform bundle | Same as Electron per OS |
| CLI | Binary / npm tarball / wheel | GPG signature for binaries; npm / PyPI signing |
| IoT/Embedded | .bin / .elf + manifest | OTA signing key, manifest hash |
| Library/Package | npm tarball / wheel / crate | Registry-level signing (npm provenance, PyPI Trusted Publishers) |
| Data/Pipeline | Container image + DAG files | Container signing + DAG manifest |
| AI/Agent | Container image + model config | Container signing |

### Artifact Manifest

Every Package run produces an artifact manifest written to `.wabblespec/receipts/artifact-manifest-<version>.json`:

```json
{
  "artifact_id": "string",
  "build_target": "string",
  "version": "semver",
  "built_from": "git-commit-sha",
  "build_timestamp": "ISO 8601",
  "artifact_path": "string",
  "artifact_hash": "sha256",
  "signing_method": "string",
  "signature_path": "string",
  "provenance_chain": ["executor-receipt-id", "archive-receipt-id"]
}
```

Deploy reads this manifest to verify the artifact before deployment.

### Signing Rules

- Signing is required for all artifacts — Package never produces unsigned artifacts for Deploy
- Signing credentials sourced from environment variables only — never from code or spec files
- Signing failure is a HARD error — abort, do not produce unsigned artifact
- Version must be embedded in artifact (not only in filename)

### Workflow

```
1. Receive: build output path, version (from Archive receipt), signing credentials

2. Validate inputs:
   -> Build output exists
   -> Version matches Archive receipt
   -> Signing credentials available in environment

3. Assemble artifact per build target:
   -> Bundle, compress, containerize as appropriate
   -> Embed version metadata in artifact

4. Compute artifact hash (SHA-256)

5. Sign artifact via declared signing method:
   -> Signing failure: HARD error, abort — do not produce unsigned artifact

6. Write artifact manifest to .wabblespec/receipts/artifact-manifest-<version>.json

7. Write Package receipt

8. Signal Deploy: artifact ready (artifact manifest path)
```

### Activation

`skill-rules.json` triggers Package on:
- Delivery gate: Executor build wave completes, Verifier passes, Package triggered
- Explicit `/package <build-output>` command

Cannot activate without:
- Build output from Executor
- Version declared from Archive version bump (Archive receipt present)
- Signing credentials declared in environment

### Integration Points

| Module | Relationship |
|---|---|
| Executor | Package receives build output from Executor |
| Archive | Archive provides version bump before Package runs; Package references Archive receipt in provenance chain |
| Deploy | Deploy reads artifact manifest before activating |
| Verifier | Verifier checks Package receipt exists before Delivery gate passes |
| Security gateway | Package signing policy enforced by Security gateway cross-cutting check |

### Verification Mode

**Audit** — artifact hash computed, artifact signed with declared method, manifest written with full provenance chain, no unsigned artifact produced.

### Receipt Extension Fields

```json
{
  "artifact_id": "string",
  "version": "string",
  "artifact_hash": "string",
  "signing_method": "string",
  "signing_succeeded": true,
  "manifest_path": "string",
  "provenance_chain": ["string"]
}
```

---

## Deploy

**Tier:** 3 — SUPPORTING
**v5.3 origin:** Deploy module — deployment execution and verification

### Purpose

Execute deployment of built artifacts to declared environments. Deploy does not build — it receives signed artifacts from Package and pushes them to the declared deployment target. Every deployment writes a deploy receipt. Rollback is declared before deploy begins, not invented during failure.

Deploy never activates during active Executor waves — it is post-execution only.

### Deployment Targets

Deploy routes to platform-specific mechanisms based on Recipe's active build target:

| Build target | Deployment mechanism |
|---|---|
| Web | CDN deploy (Vercel, Cloudflare Pages, S3+CloudFront — static or SSR) |
| API/Service | Container registry push + orchestrator deploy (Kubernetes, ECS, Cloud Run) |
| Mobile | App store submission (TestFlight, Play Console internal track) |
| Desktop | Distribution channel upload (GitHub Releases, store submission) |
| CLI | Registry publish (npm, PyPI, crates.io, Homebrew) — handled by Package |
| IoT/Embedded | OTA update server push or physical flash (declared in spec) |
| Library/Package | Registry publish — handled by Package |
| Data/Pipeline | Orchestrator deploy (Airflow DAG upload, dbt run trigger) |
| AI/Agent | Model endpoint deploy or agent service deploy |

### Environment Model

Environments declared in spec before Deploy can activate:

```markdown
## Environments

| Name | Target | Promotion gate | Rollback target |
|---|---|---|---|
| staging | staging cluster | manual approval | previous deploy |
| production | prod cluster | Attestation required | staging |
```

Promotion from staging to production requires Attestation (human sign-off). Production deployments never proceed without explicit human confirmation — this is non-negotiable.

### Rollback Declaration

Rollback must be declared before Deploy begins:

```markdown
## Rollback Plan

**trigger:** <condition — e.g., error rate > 5% OR p99 latency > 2x baseline>
**action:** redeploy previous artifact version
**rollback_to:** <artifact version or deploy ID>
**human_required:** true
**max_time_to_rollback:** 5 minutes
```

Deploy writes rollback plan to deploy receipt. Automatic rollback trigger detection is allowed (Monitor alerts). Rollback action requires human confirmation — never fully automatic in v6.1.

### Post-Deploy Verification

After deployment executes, Deploy runs declared verification:

| Check | When required |
|---|---|
| Health check | Declared in spec — required for API/Service, IoT |
| Smoke test | Declared in spec |
| Latency baseline check | Declared in spec — required when SLO declared |

If verification fails: Deploy writes FAIL to receipt and triggers rollback prompt. Human confirms rollback.

### Workflow

```
1. Receive: artifact path, target environment, rollback plan

2. Validate prerequisites:
   -> Artifact exists and signed (Package receipt present)
   -> Environment declared in spec
   -> Rollback plan present
   -> Attestation received (if production environment)

3. Pre-deploy snapshot:
   -> Record current deployed version as rollback target
   -> Write snapshot to deploy receipt

4. Execute deployment via platform-specific mechanism

5. Post-deploy verification:
   -> Health check (if declared)
   -> Smoke test (if declared)
   -> Latency baseline check (if declared)

6. Write deploy receipt:
   -> IF verification passes: PASS
   -> IF verification fails: trigger rollback prompt (human confirms)

7. Notify Instinct of deployment event (pattern signal)
```

### Activation

`skill-rules.json` triggers Deploy on:
- Delivery gate: Verifier passes all gates, Archive completes, Package receipt present
- Explicit `/deploy <environment>` command

Cannot activate without:
- Signed artifact from Package (Package receipt present)
- Deployment target declared in spec
- Rollback plan declared in spec or wave plan

### Integration Points

| Module | Relationship |
|---|---|
| Package | Deploy receives signed artifact manifest from Package |
| Archive | Archive completes before Deploy triggers (delivery receipt must be present) |
| Verifier | Verifier passes all gates before Deploy activates |
| Autopilot | Autopilot gates Deploy activation within lifecycle |
| Instinct | Deploy notifies Instinct on completion (deployment event for pattern tracking) |
| Security gateway | Deploy reads security controls for production hardening checklist |
| Monitor | Monitor generates observability config after Deploy receipt confirms |

### Verification Mode

**Demonstration** — artifact deployed to declared environment, post-deploy health check passes, rollback plan written to receipt, Attestation received for production.

### Receipt Extension Fields

```json
{
  "environment": "string",
  "artifact_version": "string",
  "rollback_to": "string",
  "attestation_received": true,
  "health_check_passed": true,
  "smoke_test_passed": true,
  "deployment_id": "string"
}
```

---

## Release

**Tier:** 3 — SUPPORTING
**v5.3 origin:** Release module — release coordination, git tag, release notes, stakeholder communication

### Purpose

Coordinate release: git tag, release notes, stakeholder communication, and release artifact publishing. Release runs after Deploy succeeds. Marks the version as shipped in Archive. Writes the release to the project's release channel. Release is the final step in the Delivery pipeline before Evolution begins observing the shipped version.

### Prerequisites

Release cannot activate without all three receipts present:
- Deploy receipt (production deployment confirmed)
- Archive receipt (version bump and changelog entry present)
- Package receipt (signed artifact exists)

In addition: Release requires Attestation before the git tag push — pushing a tag is irreversible in practice.

### Release Artifacts

| Artifact | Source | Destination |
|---|---|---|
| Git tag | Archive version | `git tag v<semver>` + push to origin |
| Release notes | Archive changelog entry + Memory research log | GitHub Releases body / release doc |
| Signed artifact attachment | Package artifact manifest | GitHub Releases assets (if applicable) |
| Internal announcement | Release notes (condensed) | Declared communication channel |

### Release Notes Structure

Release notes derived from Archive changelog entry — not invented:

```markdown
# Release v<semver> — <YYYY-MM-DD>

## What changed

<from Archive changelog: BREAKING / ADDITIVE / COSMETIC entries>

## Migration notes (if BREAKING)

<from Specify BREAKING delta records>

## Known issues

<from Verifier not-tested list + open decisions flagged as unresolved at ship>

## Artifacts

| Platform | Download | SHA-256 |
|---|---|---|
| <platform> | <link> | <hash from Package manifest> |
```

### Irreversibility Handling

Git tag push is irreversible in practice. Force-deleting a pushed tag is destructive and breaks downstream consumers. Release activates Attestation gate before tag push. Human explicitly confirms:

- Version string is correct
- Deploy receipt confirmed
- Known issues documented
- Attestation: human signs off before push proceeds

### Workflow

```
1. Validate prerequisites:
   -> Deploy receipt present (production deploy confirmed)
   -> Archive receipt present (version + changelog)
   -> Package receipt present (signed artifact)

2. Request Attestation:
   -> Human confirms version, deploy, known issues
   -> Attestation receipt written before proceeding

3. Compose release notes from Archive changelog

4. Append known issues from:
   -> Verifier not-tested compilation
   -> Open decisions flagged unresolved at ship

5. Create and push git tag:
   -> Tag: v<semver>
   -> Annotated tag with release notes summary
   -> Push to origin

6. Publish to release channel:
   -> GitHub Releases (default)
   -> Or declared equivalent (GitLab, internal tracker)

7. Send internal announcement (if declared in spec)

8. Notify Archive: release complete (Archive marks version as RELEASED)

9. Notify Instinct: release event (release cycle signal for pattern tracking)

10. Write Release receipt
```

### Activation

`skill-rules.json` triggers Release on:
- Deploy receipt confirms successful deployment to production
- Explicit `/release <version>` command

### Integration Points

| Module | Relationship |
|---|---|
| Deploy | Release activates only after Deploy receipt confirms production success |
| Archive | Release reads Archive changelog for release notes; notifies Archive on release complete |
| Package | Release attaches Package artifact manifest (hash, links) to release notes |
| Verifier | Release reads Verifier not-tested compilation for known issues section |
| Instinct | Release notifies Instinct: release cycle complete (pattern signal) |
| Autopilot | Autopilot marks lifecycle complete after Release receipt written |

### Verification Mode

**Attestation** — human sign-off before git tag push, release notes sourced from Archive, Deploy receipt confirmed, release receipt written.

### Receipt Extension Fields

```json
{
  "version": "string",
  "git_tag": "string",
  "tag_pushed": true,
  "release_channel": "string",
  "release_url": "string",
  "attestation_received": true,
  "known_issues_count": 0,
  "announcement_sent": false
}
```

---

## Scaffold

**Tier:** 3 — SUPPORTING
**v5.3 origin:** Development gateway — Scaffold module, moved to Delivery in v6.1

### Purpose

Generate initial project structure for new projects. Scaffold activates once per project lifecycle — at project creation. Reads the active platform package to produce the correct directory layout, configuration files, CI skeleton, and spec template. Does not generate application code — structure only.

Idempotency guard: if `project-map.md` already exists, Scaffold aborts. It does not re-scaffold.

### What Scaffold Generates

Common output (all targets):

| File | Purpose |
|---|---|
| `README.md` | Skeleton from Document template |
| `.gitignore` | Platform-appropriate ignores |
| `.wabblespec/` | Framework skeleton (INDEX.md stubs) |
| CI config | Pipeline skeleton (lint + test + build stages) |
| `src/`, `tests/`, `docs/` | Directory structure |
| Spec template | P1 design doc skeleton — target-specific variant |

Platform-specific output (varies by build target):

| Platform | Key generated files |
|---|---|
| Web | `package.json`, `tsconfig.json`, `vite.config.ts`, `.eslintrc`, `src/index.ts` |
| API/Service | `Dockerfile`, `.dockerignore`, `src/main.ts`, `openapi.yaml` skeleton |
| Mobile | Platform project files (`ios/`, `android/` or `pubspec.yaml`), `app.json` |
| Desktop | `electron-builder.json` or `tauri.conf.json`, platform entitlements skeleton |
| CLI | `bin/` entry, `package.json` with `bin` field, or `Cargo.toml` with `[[bin]]` |
| IoT/Embedded | `CMakeLists.txt` or `platformio.ini`, `main.c`/`main.rs` skeleton |
| Library/Package | `src/index.ts` + `src/lib.rs` equivalent, exports config |
| Extension/Plugin | `manifest.json` skeleton, `background.ts`, `content.ts` |
| Data/Pipeline | `dbt_project.yml` or `airflow/` skeleton |
| AI/Agent | `agent.yaml` skeleton, `tools/` directory |
| Game | Engine project file (varies by engine) |

Scaffold does not populate content — it creates structure and skeletons with TODO markers.

### Workflow

```
1. Verify: no project-map.md exists (idempotency check)
   -> IF exists: abort — "Scaffold already ran"

2. Read active platform package from Recipe

3. Generate common files (all targets):
   -> README.md skeleton
   -> .gitignore (platform-appropriate)
   -> .wabblespec/ framework skeleton (INDEX.md stubs)
   -> CI pipeline skeleton (lint + test + build stages)
   -> docs/ directory with placeholder

4. Generate platform-specific files:
   -> Package manager config
   -> Build tool config
   -> Entry point files with TODO markers
   -> Spec template (P1 design doc — target-specific variant)

5. Write all files to project/repo/ (I11: product files only)

6. Trigger Explore: generate initial project-map.md from scaffolded structure

7. Write Scaffold receipt
```

### Activation

`skill-rules.json` triggers Scaffold on:
- Recipe identifies new project (no existing `project-map.md`, empty or near-empty repo)
- Explicit `/scaffold <platform>` command

Cannot activate if `project-map.md` already exists.

### Integration Points

| Module | Relationship |
|---|---|
| Recipe | Recipe identifies platform before Scaffold activates |
| Explore | Scaffold triggers Explore after generation to build initial project-map.md |
| Document | Document generates README content; Scaffold creates the file stub |
| Platform packages (L3) | Scaffold reads platform package for target-appropriate file conventions |
| Autopilot | Scaffold is first step in new project lifecycle — Autopilot sequences it |

### Verification Mode

**Observation** — all declared files written to `project/repo/`, `.gitignore` present, CI config present, spec template present, `project-map.md` generated by Explore, receipt written.

### Receipt Extension Fields

```json
{
  "platform_target": "string",
  "files_generated": 0,
  "spec_template_variant": "string",
  "explore_triggered": true
}
```

---

## Monitor

**Tier:** 3 — SUPPORTING
**v5.3 origin:** Monitor module — post-deployment observability configuration

### Purpose

Generate observability configuration for deployed artifacts. Monitor reads Engineering gateway SLO declarations and platform-appropriate monitoring patterns to produce metric definitions, log schemas, and alerting rules. Writes config files to `project/repo/monitoring/`. Does not operate monitors — generates the config that external monitoring infrastructure consumes.

### What Monitor Generates

| Output | Description | Applicable targets |
|---|---|---|
| Metrics config | Prometheus / StatsD / CloudWatch metric definitions | API/Service, Data/Pipeline |
| Log schema | Structured log format declaration | All server-side targets |
| Alert rules | Threshold-based alerts derived from SLO | All targets with SLO declared |
| Health check config | Liveness + readiness probe definitions | API/Service, IoT/Embedded |
| Dashboard template | Grafana / CloudWatch dashboard JSON skeleton | API/Service, Data/Pipeline |
| Tracing config | OpenTelemetry / Jaeger trace sampling config | API/Service |

### SLO-to-Alert Binding

Monitor reads Engineering gateway SLO declarations and generates alert rules:

| SLO type | Alert rule generated |
|---|---|
| Availability target (e.g. 99.9%) | Alert when error rate exceeds `1 - target` over rolling window |
| Latency p99 target | Alert when p99 exceeds target for > 5 minutes |
| Throughput floor | Alert when RPS drops below declared floor |
| Custom metric | Alert rule declared in spec — Monitor implements |

Alert window and evaluation frequency must be declared in spec — not defaulted.

### Log Schema

All server-side targets produce structured JSON logs. Monitor declares the schema:

```json
{
  "timestamp": "ISO 8601",
  "level": "DEBUG|INFO|WARN|ERROR|FATAL",
  "service": "service name",
  "trace_id": "string (optional)",
  "message": "string",
  "context": {}
}
```

No unstructured logs in server-side targets. Monitor enforces this via linting rules in CI config.

### Tooling Selection by Platform

| Platform | Default monitoring tooling |
|---|---|
| API/Service | Prometheus + Grafana (default), CloudWatch (AWS), or declared |
| Data/Pipeline | Airflow metrics, dbt monitoring, or declared |
| AI/Agent | Token usage metrics, latency histograms, refusal rate |
| IoT/Embedded | Platform-specific — declared in spec |

### Workflow

```
1. Read: Engineering gateway SLO declarations, platform package monitoring patterns, Deploy receipt

2. Select monitoring tooling per platform (from platform package)

3. Generate metric definitions aligned to SLO

4. Generate alert rules from SLO thresholds

5. Generate log schema

6. Generate health check config (API/Service, IoT/Embedded)

7. Write all config to project/repo/monitoring/ or declared path

8. Write Monitor receipt
```

### Activation

`skill-rules.json` triggers Monitor on:
- Deploy receipt confirmed (Monitor generates config after successful deploy)
- Engineering gateway SLO declared in spec (Monitor notified to align alerts)
- Explicit `/monitor <environment>` command

Platform targets that require observability by default: API/Service, Data/Pipeline, AI/Agent, Desktop (server components).

### Integration Points

| Module | Relationship |
|---|---|
| Deploy | Deploy receipt triggers Monitor; Monitor config deployed alongside artifact |
| Engineering gateway | Monitor reads SLO declarations for alert rule generation |
| Platform packages (L3) | Platform monitoring conventions determine tooling selection |
| Instinct | Deploy events observed by Instinct; Monitor alerts feed operational patterns |
| Verifier | Verifier Measurement mode reads Monitor thresholds for quantitative gate |

### Verification Mode

**Observation** — metric definitions present, alert rules aligned to SLO declarations, log schema declared, health check config present (if applicable), receipt written.

### Receipt Extension Fields

```json
{
  "environment": "string",
  "monitoring_tool": "string",
  "metrics_defined": 0,
  "alert_rules_generated": 0,
  "slo_bindings": 0,
  "log_schema_declared": true,
  "output_path": "string"
}
```

---

## L7 Layer Interactions

### Receipt chain through Delivery

Delivery is the most chain-dependent layer. Each module requires receipts from its predecessors:

```
Executor receipt
  -> Archive receipt (required by Package, Deploy)
     -> Package receipt (required by Deploy, Release)
        -> Deploy receipt (required by Release, Monitor)
           -> Release receipt (marks lifecycle complete)
           -> Monitor receipt (observability config deployed)
```

No stage can skip its upstream receipt. Archive without an Executor receipt is rejected. Deploy without a Package receipt is rejected. Release without a Deploy receipt is rejected.

### Attestation gates in Delivery

Two Attestation gates in L7:

1. **Deploy → production:** Human sign-off before Deploy executes against production environment. Staging does not require Attestation.
2. **Release → git tag push:** Human sign-off before annotated tag is pushed to origin. Tag push is irreversible.

Both gates write Attestation records to their respective receipts.

### Instinct notification pattern

Three L7 modules notify Instinct on completion:
- Archive: execution complete, receipts available for pattern analysis
- Deploy: deployment event (version, environment, timestamp)
- Release: release cycle complete (version shipped)

Instinct accumulates these signals across cycles to detect patterns in delivery velocity, failure rates, and release cadence.

### Scaffold position in lifecycle

Scaffold is not part of the standard delivery pipeline. It runs exactly once, at the start of a new project's lifecycle:

```
New project detected (no project-map.md)
  -> Scaffold: generate structure
  -> Explore: generate project-map.md
  -> Standard pipeline begins (L0 Interview, L1 Specify, ...)
```

After Scaffold runs, `project-map.md` exists and Scaffold's idempotency guard prevents any future re-scaffold.

---

## Invariants Enforced by L7

| Invariant | How L7 enforces it |
|---|---|
| I8 (Human gates for irreversible) | Deploy requires Attestation for production; Release requires Attestation for git tag push |
| I10 (Receipts as operational artifacts) | Archive aggregates all receipts; Package, Deploy, Release, Monitor, Scaffold each write receipts; Archive never deletes receipts |
| I11 (Framework-product separation) | Scaffold and Monitor write to `project/repo/` only; Archive owns `.wabblespec/` records but does not touch product files |

---

## Sub-Components Summary

| Module | Required components |
|---|---|
| Archive | SKILL.md, skill-rules.json, rules/version-bump.md, rules/not-tested-policy.md, rules/sweep-policy.md, schemas/delivery-receipt.schema.json, schemas/receipt.schema.json |
| Package | SKILL.md, skill-rules.json, rules/signing-policy.md, rules/version-embedding.md, rules/credentials-policy.md, schemas/artifact-manifest.schema.json, schemas/receipt.schema.json |
| Deploy | SKILL.md, skill-rules.json, rules/environment-policy.md, rules/rollback-policy.md, rules/attestation-policy.md, schemas/receipt.schema.json |
| Release | SKILL.md, skill-rules.json, templates/release-notes.md, rules/attestation-required.md, rules/source-only.md, schemas/receipt.schema.json |
| Scaffold | SKILL.md, skill-rules.json, templates/ (11 platform templates + common/), rules/idempotency.md, rules/no-code.md, schemas/receipt.schema.json |
| Monitor | SKILL.md, skill-rules.json, templates/prometheus/, templates/cloudwatch/, templates/opentelemetry/, templates/log-schema.json, rules/slo-binding.md, rules/no-unstructured-logs.md, schemas/receipt.schema.json |

---

## Cross-References

- L6 Expression (Document generates release and onboarding content): `WabbleSpec v6.1 — Expression.md`
- L8 Evolution (receives Instinct signals from Archive, Deploy, Release): `WabbleSpec v6.1 — Evolution.md`
- L2 Executor and Verifier (upstream of Archive): `WabbleSpec v6.1 — Core.md` § L2 Orchestration
- Platform packages (L3, inform Scaffold and Deploy): `WabbleSpec v6.1 — Platform.md`
- Engineering gateway SLO declarations (read by Monitor): `WabbleSpec v6.1 — Engineering.md`
- Security gateway signing policy (cross-cuts Package): `WabbleSpec v6.1 — Security.md`
- Invariants: `WabbleSpec v6.1 — Core.md` § Invariants
- Verification modes: `WabbleSpec v6.1 — Core.md` § Verification Modes
