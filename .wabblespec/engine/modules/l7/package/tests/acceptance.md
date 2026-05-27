# Acceptance Tests — Package (L7)

## AT-PKG-01: Delivery receipt required before Package runs

**Given** a Package invocation when no `delivery-receipt-*.json` exists in `.wabblespec/receipts/`
**When** Package checks its prerequisite
**Then** Package FAILs with `MISSING_DELIVERY_RECEIPT` — Archive must have run before Package

---

## AT-PKG-02: Signing failure is a hard stop

**Given** a Package run where artifact signing fails for any artifact
**When** signing fails
**Then** Package FAILs immediately; it does not continue to the manifest step; no release artifact is produced

---

## AT-PKG-03: No unsigned artifact leaves Package

**Given** a Package run completing successfully
**When** artifacts are produced
**Then** `all_signed: true` in the receipt — every artifact has been signed; Package never produces unsigned artifacts

---

## AT-PKG-04: SHA-256 computed and recorded for every artifact

**Given** a Package run
**When** the artifact manifest is written
**Then** every artifact in the manifest has a `sha256` field with the computed hash

---

## AT-PKG-05: Signing key never appears in manifest or receipt

**Given** a Package run using a signing key
**When** the manifest and receipt are written
**Then** only `key_id` or key reference appears — never the key material itself

---

## AT-PKG-06: Manifest contains provenance chain

**Given** a successfully packaged artifact
**When** the manifest is written to `.wabblespec/artifacts/manifest-{version}-{timestamp}.json`
**Then** the `provenance` object contains:
- `delivery_receipt`
- `git_commit`
- `git_ref`
- `builder`
- `build_id`

---

## AT-PKG-07: Package receipt contains required fields

**Given** a completed Package run
**Then** the receipt at `.wabblespec/receipts/package-receipt-{timestamp}.json` contains:
- `version`
- `artifacts_packaged`
- `all_signed`
- `manifest_path`
- `signing_method`
