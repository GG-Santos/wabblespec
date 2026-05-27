# Versioning Policy

Every API must declare a versioning scheme before API module runs. Undeclared versioning is a violation.

## Supported schemes

### semver (Semantic Versioning)

URL path: `/v1/`, `/v2/`, etc. Only the major version appears in the URL.

Rules:
- Major bump: BREAKING change (removes or changes existing endpoint contract)
- Minor bump: ADDITIVE change (new endpoints, new optional fields)
- Patch bump: non-breaking fixes (no contract change)

When to use: Internal APIs, developer APIs, SDKs where clients control upgrades.

---

### date-based

URL path: `/2024-01-15/endpoint` or header `API-Version: 2024-01-15`.

Rules:
- A new date version is cut whenever a BREAKING change is introduced
- All date versions are supported simultaneously during the deprecation window
- ADDITIVE changes are applied to the current date version without a new date version

When to use: Public APIs with many clients at different versions (Stripe pattern). Clients opt in to new dates; old dates remain functional.

---

### header-based

No version in URL. Version declared in request header: `Accept: application/vnd.api+json;version=2` or `X-API-Version: 2`.

Rules:
- Same major/minor/patch logic as semver applies to the version number in the header
- Default version served when no header present must be declared (do not serve latest implicitly)

When to use: When URL cleanliness is required but versioning is still needed.

---

## Scheme selection

Record `versioning_scheme` in receipt. Once declared in an API contract, the scheme must not change without a BREAKING version bump and migration guide.

## Minimum API contract fields

Every API contract (see `schemas/api-contract.schema.json`) must declare:
- Versioning scheme
- Base URL
- Authentication method
- Rate limits (or `NONE` if no limits)
- Error format
- Deprecation policy reference
