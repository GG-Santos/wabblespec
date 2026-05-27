# Contract Enforcement

An API contract is a promise. The API module enforces that the promise is kept — changes that break the promise require explicit acknowledgment.

## What constitutes the contract

The API contract (`schemas/api-contract.schema.json`) captures the full promise:
- Endpoint paths and HTTP methods
- Request schema (required fields, types, validation rules)
- Response schema (fields, types, status codes)
- Error format and error codes
- Authentication requirements
- Rate limit declarations
- Versioning scheme

Any change to any of these is a contract change. Contract changes are classified using `rules/change-classification.md`.

---

## Enforcement checks

### Check 1 — Schema backward compatibility
New contract version must not remove required request fields. New contract version must not remove response fields that consumers may be reading. Check by diffing old and new schema: any removal of a `required` field or any field that appeared in previous responses.

### Check 2 — Status code stability
Status codes for existing endpoints must not change meaning. If `404` meant "not found" before, it must still mean "not found." Adding new status codes is ADDITIVE. Changing meaning of existing codes is BREAKING.

### Check 3 — Error format stability
Error response format must not change between versions. If errors have `{ "error": "string" }` shape, that shape must be preserved. Adding optional fields: ADDITIVE. Changing field names or removing fields: BREAKING.

### Check 4 — Authentication requirements
Changing authentication method (e.g., API key → OAuth) is BREAKING. Adding an optional authentication method alongside existing: ADDITIVE.

### Check 5 — Rate limit changes
Reducing rate limits for existing consumers is a BREAKING change in practice (even if technically additive in schema). Increasing limits: ADDITIVE.

---

## Backward compatibility declaration

`backward_compatible: true` in receipt requires that all five checks pass. If any check fails and the change is classified BREAKING, `backward_compatible: false` and the receipt records `breaking_changes: N`.

BREAKING changes require: version bump, deprecation notice or immediate removal with migration guide, and human confirmation before the API receipt is used to approve a deployment.
