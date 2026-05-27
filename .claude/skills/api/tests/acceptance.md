# API — Acceptance Criteria

## BLOCK: absent contract file

Given API is invoked but no contract file (OpenAPI spec, proto file, or GraphQL schema) exists at the declared path,
Then API surfaces: "API requires a contract file. Provide an OpenAPI spec (openapi.yaml), proto file (*.proto), or GraphQL schema (schema.graphql)."
Then no receipt is written.
Then API does not generate contract assumptions from code alone.

## Mode: --version

Given a contract file exists and `--version` is specified,
When API runs in version mode,
Then a new contract entry is written with the declared version.
Then breaking changes between the previous and new contract version are identified and `breaking_changes` count is recorded.
Then `versioning_scheme` in the receipt reflects the declared scheme (semver, date-based, or header-based).

## Mode: --deprecate

Given `--deprecate` is specified with a target endpoint or field,
When API runs in deprecate mode,
Then the contract entry is marked DEPRECATED with `deprecated_in`, `sunset_date`, and `replacement` (or `no-replacement`) fields.
Then if the declared sunset date is fewer than 6 months from deprecation, API requires explicit user justification before proceeding.
Then `deprecations_added` in the receipt is incremented.

## Mode: --contract

Given `--contract` is specified,
When API runs in contract mode,
Then a formal contract document is written to `.wabblespec/api/contract-<timestamp>.json`.
Then the contract includes: endpoint paths, request/response schemas, authentication method, error responses, versioning header.

## Mode: --audit

Given `--audit` is specified with an implementation path and a prior contract,
When API runs in audit mode,
Then all declared endpoints are checked for existence in implementation.
Then request/response shape drift is detected and reported.
Then deprecated items are verified present if sunset date has not been reached.
Then undeclared endpoints exposed by implementation are flagged as violations.
Then `backward_compatible` in the receipt is false when violations are found.

## Absent consumer list

Given a contract exists but no consumer list is declared,
When API runs,
Then API surfaces: "API consumer list absent. Breaking change impact cannot be assessed without knowing which services consume this API."
Then API proceeds and flags the missing consumer list in the receipt.
Then the run is not blocked.

## Absent rules files: fallback to SKILL.md defaults

Given `rules/versioning-policy.md` is missing,
When API runs,
Then API applies SKILL.md versioning rules.
Then the receipt logs: "versioning-policy.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful API run,
Then the receipt contains: `mode`, `api_version`, `versioning_scheme`, `breaking_changes`, `deprecations_added`, `deprecations_sunset`, `backward_compatible`, `contract_path`.
