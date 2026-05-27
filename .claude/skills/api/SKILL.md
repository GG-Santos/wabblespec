---
name: api
description: API lifecycle management. Version, deprecate, audit contracts, enforce backward compatibility. Four modes: --version, --deprecate, --contract, --audit.
---

# API

APIs have callers. Callers have expectations. You manage the contract between them across its full lifecycle: versioning new releases, marking deprecations, auditing contracts for drift, and enforcing backward compatibility rules.

## What this skill does

Manages API lifecycle across four modes. Writes contract artifacts. Enforces compatibility rules. Writes api receipt.

## When to use

- Adding a new API version
- Marking an endpoint or field as deprecated
- Auditing whether implementation matches declared contract
- Checking backward compatibility of a proposed change

## Inputs

- Mode: `--version` | `--deprecate` | `--contract` | `--audit`
- API contract path (OpenAPI spec, schema file, or contract.md)
- Previous contract version (for --version and --audit)

## How to do it

### --version

Declare new API version. Apply versioning scheme per rules/versioning-policy.md. Write new contract entry. Identify breaking changes between previous and new version. Record `breaking_changes` count.

Versioning schemes: `semver` (v1.2.3), `date-based` (2026-05-23), `header-based` (Accept: application/vnd.api+json;version=2).

### --deprecate

Mark endpoint, field, or behavior as DEPRECATED. Required fields: `deprecated_in`, `sunset_date`, `replacement` (or `no-replacement` if retiring). Write deprecation notice to contract. Record in `deprecations_added`.

Sunset date must be at least 6 months from deprecation. Shorter sunset requires explicit user justification.

### --contract

Write or update the formal API contract document. Contract must include: endpoint paths, request/response schemas, authentication method, error responses, versioning header, rate limits if applicable. Write to `.wabblespec/api/contract-<timestamp>.json`.

### --audit

Compare implementation to declared contract. Check: all declared endpoints exist, request/response shapes match, deprecated items still present if sunset date not reached, no undeclared endpoints exposed. Flag drift as violations.

## Output contract

**api-receipt.json** (`.wabblespec/state/receipts/api-receipt-<timestamp>.json`):

```json
{
  "mode": "version | deprecate | contract | audit",
  "api_version": "string",
  "versioning_scheme": "semver | date-based | header-based",
  "breaking_changes": "integer",
  "deprecations_added": "integer",
  "deprecations_sunset": "integer",
  "backward_compatible": "boolean",
  "contract_path": ".wabblespec/api/contract-<timestamp>.json"
}
```
