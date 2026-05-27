# Factory — Acceptance Criteria

## L8 corpus gate

Given receipt count in .wabblespec/receipts/ is fewer than 100 PASS,
When Factory is invoked,
Then Factory exits and outputs "GATE_NOT_MET" with the current count.
Then no scaffold files are written.

## Activation gate — blueprint validation

Given blueprint.json with change_type: AUGMENT,
When Factory is invoked,
Then Factory refuses, outputs "AUGMENT blueprints use Augment, not Factory", and writes nothing.

Given blueprint.json with status: awaiting-attestation,
When Factory is invoked,
Then Factory refuses and names the unmet attestation requirement.
Then Factory does not write any stub files.

Given blueprint.json with status: approved and change_type: NEW,
When Factory is invoked,
Then Factory proceeds to scaffold.

## Idempotency guard

Given the augments directory already contains a subdirectory named {blueprint_id},
When Factory is invoked with the same blueprint,
Then Factory exits with IDEMPOTENCY_GUARD without overwriting any existing file.
Then the existing scaffold is not modified.

Given the augments directory does not contain {blueprint_id},
When Factory is invoked,
Then Factory creates the scaffold directory and writes all stub files.

## Module ID conflict check

Given blueprint specifies a module_id that already exists in framework.yaml,
When Factory evaluates it,
Then Factory surfaces "module ID conflict: [id] already registered in framework.yaml."
Then Factory writes no files until human confirms a different ID.

Given blueprint specifies a module_id that does not exist in framework.yaml,
When Factory evaluates it,
Then Factory proceeds without surfacing a conflict.

## Required scaffold output

Given an approved NEW blueprint,
When Factory scaffolds,
Then the output directory contains exactly: SKILL.md, skill-rules.json, schemas/receipt.schema.json, tests/acceptance.md.
Then no additional files are created.
Then no files are created outside experiments/augments/{blueprint_id}/.

## Stub content — SKILL.md

Given scaffold is produced,
Then SKILL.md begins with a frontmatter block containing name: and description: fields.
Then description: value in frontmatter is filled from blueprint (not [FILL]).
Then SKILL.md contains [FILL] placeholders for: "What this skill does" body, "When to use" body, output contract details, failure mode details.
Then every [FILL] marker includes a hint: "[FILL: describe the primary function]" not bare "[FILL]".
Then no [FILL] marker contains prose behavioral logic — placeholders only.

## Stub content — skill-rules.json

Given scaffold is produced,
Then skill-rules.json is valid JSON (parseable without error).
Then skill-rules.json contains: module (from blueprint module_id), layer (from blueprint), authority.owns, authority.reads, verification_mode.
Then layer, authority.owns, and verification_mode are taken directly from blueprint — not [FILL].
Then activators contains at least one [FILL] marker.
Then anti_activators contains at least one [FILL] marker.
Then receipt_required is a boolean (true or false, not a string).

## Stub content — receipt.schema.json

Given scaffold is produced,
Then schemas/receipt.schema.json is valid JSON Schema (parseable without error).
Then it contains: "$schema", "type": "object", "properties" with at minimum receipt_type, run_id, status, timestamp fields.
Then all four base fields have their types declared.

## Stub content — tests/acceptance.md

Given scaffold is produced,
Then tests/acceptance.md contains at least 3 placeholder acceptance criteria using Given/When/Then format.
Then each criterion has a [FILL] marker for the condition or outcome.
Then the file does not contain any concrete behavioral assertions (no specific values — those come from Augment).

## Stub version tracking

Given scaffold is produced,
Then skill-rules.json contains a factory_version field matching the current Factory module version.
Then SKILL.md frontmatter contains factory_generated_at with the generation timestamp.
Then these fields allow Augment to detect if the stub is stale relative to a Factory update.

## Boundary enforcement

Given any Factory invocation,
Then no file is written directly under modules/.
Then framework.yaml is not modified by Factory.
Then existing receipts in .wabblespec/receipts/ are not modified.
Then only experiments/augments/{blueprint_id}/ receives new files.

## Dry-run

Given --dry-run flag,
Then Factory prints the list of files that would be created and their sizes.
Then Factory prints the module_id conflict check result.
Then no files are written.
Then no idempotency guard fires (dry-run is not a real invocation).
