# Cold-Start Behavior — API

Defines what API does when its contract files or versioning artifacts are absent.

## Absent: API contract file

Condition: API invoked but no contract file (OpenAPI spec, proto file, or GraphQL schema) exists.
Detection: Declared contract path returns 404.
Action: Surface: "API requires a contract file. Provide an OpenAPI spec (openapi.yaml), proto file (*.proto), or GraphQL schema (schema.graphql)."
Do NOT: Generate contract assumptions from code alone.

## Absent: versioning-policy.md

Condition: `rules/versioning-policy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md versioning rules. Log: "versioning-policy.md missing — using SKILL.md defaults."

## Absent: deprecation-lifecycle.md

Condition: `rules/deprecation-lifecycle.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md deprecation rules. Log: "deprecation-lifecycle.md missing — using SKILL.md defaults."

## Absent: prior API receipt for this contract

Condition: No prior `api-receipt-<timestamp>.json` for this contract version.
Action: Treat as first review. No prior contract to diff against.

## Absent: consumer list

Condition: API contract exists but no declared consumers (clients of this API).
Detection: Spec has no consumers section.
Action: Surface: "API consumer list absent. Breaking change impact cannot be assessed without knowing which services consume this API."
Do NOT: Block the review. Flag the missing consumer list in the receipt.

## Default state on cold start

| Field | Default |
|---|---|
| `contract_format` | Detected from file extension (yaml/json = OpenAPI, .proto = gRPC, .graphql = GraphQL) |
| `versioning_strategy` | Not declared — must be specified (URL path / header / content negotiation) |
| `deprecation_notice_period` | Minimum 1 minor version (per policy default) |
| `breaking_change_policy` | MAJOR version bump required — enforced as API invariant |
| `consumer_impact_known` | false — until consumer list declared |
