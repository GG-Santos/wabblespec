# Cold-Start Behavior — PRD

Defines what PRD does when its expected upstream artifacts are absent.

## Absent: existing product concept or file

Condition: User invokes `/prd` without a description or file.
Detection: No `concept` input and no `existing_file` path provided.
Action: Ask up to 3 clarifying questions to establish product concept, target users, and success criteria before drafting. Do not draft a PRD from zero context.
Do NOT: Generate a generic placeholder PRD — produces a document no one can review.

## Absent: intent.md or prior interview output

Condition: No `intent.md` exists when PRD runs.
Detection: `.wabblespec/state/plans/intent.md` absent.
Action: Proceed with the user's concept description. If ambiguity is high (complexity would be High), suggest running Interview first. If user wants to proceed, gather the minimum via the Step 1 clarifying questions.
Do NOT: Block execution — PRD can run without a prior interview for simpler products.

## Absent: prior receipts

Condition: `recipe-receipt.json` absent.
Detection: Stem missing.
Action: Proceed as ad-hoc run. Write `prd-output.md` in working directory instead of `.wabblespec/state/plans/prd.md`. Receipt is optional in ad-hoc mode.

## Default state on cold start

| Field | Default |
|---|---|
| `document_version` | 1.0 |
| `status` | Draft |
| `criteria_checked` | 7 (all) |
| `continue_to_spec` | false |
| `output_path` | prd-output.md (ad-hoc) or .wabblespec/state/plans/prd.md (framework) |
