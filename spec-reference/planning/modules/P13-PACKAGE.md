# Module Plan — Package (L7)

**Tier:** 3 — SUPPORTING
**Layer:** L7 Delivery
**v5.3 origin:** Package module — artifact preparation and signing before deployment

---

## Purpose

Prepare and sign deployment artifacts from built output. Package does not build — it receives build output from Executor and produces signed, versioned artifacts ready for Deploy or registry publish. Artifact integrity guaranteed: no Package receipt = no Deploy activation. Every artifact has a declared provenance chain from source to signed artifact.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/package <build-output>` command
- Delivery gate: Executor build wave completes, Verifier passes, Package triggered
- Cannot activate without:
  - Build output (from Executor)
  - Version declared (from Archive version bump)
  - Signing credentials declared (from spec or environment)

---

## Artifact Types by Build Target

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

---

## Artifact Manifest

Every Package run produces an artifact manifest:

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

Manifest written to `.wabblespec/receipts/artifact-manifest-<version>.json`. Deploy reads manifest to verify artifact before deployment.

---

## Workflow

```
1. Receive: build output path, version (from Archive), signing credentials

2. Validate inputs:
   -> Build output exists
   -> Version matches Archive receipt
   -> Signing credentials available (from env — never from code)

3. Assemble artifact per build target:
   -> Bundle, compress, containerize as appropriate
   -> Include version metadata in artifact (embedded version string)

4. Compute artifact hash (SHA-256)

5. Sign artifact via declared signing method:
   -> Signing failure is HARD error — abort, do not produce unsigned artifact

6. Write artifact manifest

7. Write Package receipt

8. Signal Deploy: artifact ready (artifact manifest path)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — post-Executor, post-Archive version bump |
| `rules/signing-policy.md` | Rules | Signing required for all artifacts — no unsigned artifacts to Deploy |
| `rules/version-embedding.md` | Rules | Version must be embedded in artifact, not only in filename |
| `rules/credentials-policy.md` | Rules | Signing credentials from env vars only |
| `schemas/artifact-manifest.schema.json` | Schema | Manifest validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Executor | Package receives build output from Executor |
| Archive | Archive provides version bump before Package runs; Package references Archive receipt in provenance chain |
| Deploy | Deploy reads artifact manifest from Package before activating |
| Verifier | Verifier checks Package receipt exists before Delivery gate passes |
| Security gateway | Package signing policy enforced by Security gateway cross-cutting check |

---

## Verification Mode

**Audit** — artifact hash computed, artifact signed with declared method, manifest written with full provenance chain, no unsigned artifact produced.

---

## Receipt Extension Fields

```json
{
  "artifact_id": "string",
  "version": "string",
  "artifact_hash": "string",
  "signing_method": "string",
  "signing_succeeded": "boolean",
  "manifest_path": "string",
  "provenance_chain": ["string"]
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| SBOM generation | Package generates SBOM (CycloneDX/SPDX) vs. separate module | Per-project at P3 |
| Artifact storage | Local only vs. artifact registry (Artifactory, GHCR) declared in spec | Per-project |
| Multi-arch builds | Single arch vs. multi-arch (arm64 + amd64) declared in spec | P10 platform refinement |
