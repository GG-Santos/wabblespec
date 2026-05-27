---
name: package
description: Signs and versions release artifacts. Produces Docker images, binaries, npm tarballs, or platform packages with SHA-256 manifest and provenance chain. Signing failure is a hard error — no unsigned artifact is released.
---

# Package

You produce signed, versioned artifacts ready for deployment. You never produce unsigned artifacts. You never produce artifacts without a manifest. Signing failure stops the pipeline — it is not a warning.

## What this skill does

Takes build outputs from the Executor wave, signs them, produces a manifest with SHA-256 hashes and provenance chain, and writes a package receipt. Deploy consumes your output.

## When to use

After build artifacts are produced by an Executor wave and before Deploy runs, with signing keys available (unsigned artifacts are a hard error).

## Inputs

- Build outputs: binary, Docker image, npm tarball, or platform-specific package
- `.wabblespec/VERSION` — version string to embed in artifact name
- Signing key reference (from CI secrets vault — never in repo)
- `delivery-receipt.json` — confirms Archive has run on this execution

## How to do it

### Step 1 — Verify delivery receipt exists

Package does not run if Archive has not run. Check for `delivery-receipt-*.json` in `.wabblespec/state/receipts/`. If absent: FAIL with `MISSING_DELIVERY_RECEIPT`.

### Step 2 — Collect build outputs

Locate all artifacts declared in the execution plan. Verify each file exists and is non-empty. If any declared artifact is missing: FAIL.

### Step 3 — Compute SHA-256 for each artifact

```bash
sha256sum firmware.bin > firmware.bin.sha256
sha256sum app.tar.gz > app.tar.gz.sha256
```

### Step 4 — Sign artifacts

**Binary / firmware:**
```bash
# Ed25519 signing via cosign or custom tool
cosign sign-blob --key "$SIGNING_KEY_REF" firmware.bin \
  --output-signature firmware.bin.sig \
  --output-certificate firmware.bin.crt
```

**Docker image:**
```bash
cosign sign --key "$SIGNING_KEY_REF" \
  "registry.example.com/app:${VERSION}"
```

**npm tarball:**
```bash
npm pack  # produces app-1.2.3.tgz
# Signing via npm provenance (--provenance flag on npm publish)
# or detached signature via gpg/cosign
```

**If signing fails for any artifact: FAIL immediately.** Do not continue to manifest step. Do not produce any release artifact.

### Step 5 — Write artifact manifest

`.wabblespec/artifacts/manifest-{version}-{timestamp}.json`:
```json
{
  "version": "1.2.3",
  "built_at": "ISO-8601",
  "artifacts": [
    {
      "name": "firmware.bin",
      "path": "dist/firmware.bin",
      "sha256": "abc123...",
      "signature": "dist/firmware.bin.sig",
      "size_bytes": 123456
    }
  ],
  "provenance": {
    "delivery_receipt": ".wabblespec/state/receipts/delivery-receipt-{timestamp}.json",
    "git_commit": "abc1234",
    "git_ref": "refs/tags/v1.2.3",
    "builder": "github-actions",
    "build_id": "CI-run-id"
  },
  "signing": {
    "method": "cosign-ed25519 | gpg | npm-provenance",
    "key_id": "key fingerprint or reference — never the key itself"
  }
}
```

### Step 6 — Write package receipt

## Output contract

**package-receipt** (`.wabblespec/state/receipts/package-receipt-{timestamp}.json`):
```json
{
  "version": "string",
  "artifacts_packaged": "integer",
  "all_signed": "boolean",
  "manifest_path": "string",
  "signing_method": "string"
}
```

Artifact manifest: `.wabblespec/artifacts/manifest-{version}-{timestamp}.json`

## Non-negotiable rules

1. No unsigned artifact leaves Package. Signing failure = pipeline stops.
2. SHA-256 hash computed and recorded for every artifact.
3. Provenance chain links back to delivery receipt, git commit, and CI build ID.
4. Signing key never appears in manifest, receipt, or any output file — only key ID or reference.
5. Package does not run without a delivery receipt from Archive.

## Common failure modes

1. **Treating signing failure as a warning.** A failed signature check is a hard stop. An unsigned artifact that reaches production is an attack surface.

2. **Skipping manifest for "simple" artifacts.** Every artifact needs a manifest. The manifest is what Deploy uses to verify it received the correct artifact.

3. **Embedding secrets in manifest.** Key ID only — never the key material. Manifest is stored in the repo and CI artifacts.
