# Package Signing Policy

All artifacts produced by Package must be signed. Signing failure is a HARD error — execution does not continue.

---

## Signing Failure = HARD Error

If signing fails for any reason, Package:

1. Writes a FAIL receipt immediately
2. Does NOT write the artifact manifest
3. Does NOT mark the artifact as ready for Deploy
4. Surfaces the signing failure with exact error output

There is no fallback for signing failure. There is no `--skip-signing` option. Unsigned artifacts never reach Deploy.

Common signing failures and their resolution:

| Failure | Resolution |
|---|---|
| Signing key not found | Verify `WABBLESPEC_SIGNING_KEY_PATH` env var is set |
| Key permission denied | Check file permissions on signing key |
| Tool not installed | Install required signing tool (see Engineering gateway build-standards.md) |
| Certificate expired | Renew certificate — do not sign with expired cert |

---

## Artifact Manifest (SHA-256 Required)

Package writes one manifest per artifact set. Manifest is written before signing the manifest itself.

**Manifest format** (`.wabblespec/artifacts/manifest-<timestamp>.json`):

```json
{
  "manifest_version": 1,
  "created_at": "ISO-8601",
  "artifacts": [
    {
      "name": "string",
      "path": "string — path relative to project root",
      "sha256": "string — hex digest",
      "size_bytes": 0,
      "type": "docker-image | binary | npm-tarball | python-wheel | zip | other"
    }
  ],
  "signing": {
    "algorithm": "string — e.g. RSA-SHA256, Ed25519",
    "key_id": "string — key identifier, not the key itself",
    "signature": "string — base64-encoded signature of canonical manifest JSON",
    "signed_at": "ISO-8601"
  },
  "provenance": {
    "source_commit": "string — git SHA if applicable",
    "build_recipe_receipt": "string — path to recipe receipt",
    "package_receipt": "string — path to this package receipt"
  }
}
```

**Canonical JSON for signing:** Serialize manifest without the `signing` field, sorted keys, no extra whitespace. Sign that canonical form.

---

## SHA-256 Computation

SHA-256 must be computed on the final artifact file, not on intermediate build outputs.

- Docker images: SHA-256 of the compressed image tarball
- Binaries: SHA-256 of the final binary (after stripping if applicable)
- npm tarballs: SHA-256 of the .tgz file
- Python wheels: SHA-256 of the .whl file

Do not use MD5 or SHA-1. Do not truncate the digest.

---

## Provenance Chain

Every manifest must include a `provenance` block linking the artifact back to:
- Source commit (if git is used)
- The Recipe receipt that initiated the task
- The Package receipt itself (self-reference — written last)

This chain allows Deploy and Release to trace any artifact back to its originating task spec.

---

## Version Tagging

Package reads `.wabblespec/VERSION` for the version string. It does not infer version from git tags, package.json, or other sources.

Archive must have written a delivery receipt (with a version bump) before Package runs. Package is blocked without an Archive receipt declaring the current version.

---

## Platform-Specific Signing

| Platform target | Signing tool |
|---|---|
| Desktop (Electron/Tauri) | Platform code signing certificate (Apple notarization / Windows Authenticode) |
| Mobile | App store signing certificates (iOS provisioning profile / Android keystore) |
| Docker image | `cosign` or `docker trust` |
| npm package | `npm publish` with 2FA / provenance flag |
| Binary | `gpg --detach-sign` or platform-specific tool |
| Python wheel | `twine` with signing |

Specific tool configuration lives in the L3 platform engineering module (`engineering/build-toolchain.md`). Package reads platform from the active L3 receipt and applies platform-specific signing.
