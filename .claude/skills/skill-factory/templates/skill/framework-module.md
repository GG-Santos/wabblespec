---
name: {{ module_id }}
description: {{ trigger_description }}
layer: {{ layer }}
gateway: {{ gateway }}
---

# {{ module_name }}

> Layer: {{ layer }} | Gateway: {{ gateway }} | Tier: {{ tier }}
> Receipt schema: `schemas/receipt.{{ module_id }}.schema.json`
> Upstream receipts required: {{ upstream_receipts }}

## Purpose and Scope

{{ purpose_statement }}

**In scope:** {{ in_scope }}

**Out of scope:** {{ out_of_scope }}

**Activates when:** {{ activation_conditions }}

**Does not activate when:** {{ suppression_conditions }}

## Inputs

{{ inputs_table }}

## Decision Logic

{{ decision_logic }}

## Workflow

{{ workflow_steps }}

## Verification Criteria

Before producing a receipt, confirm:

{{ verification_criteria }}

## Receipt Production

On successful verification, write `.wabblespec/receipts/{{ module_id }}-{wave}-{timestamp}.json` conforming to `schemas/receipt.{{ module_id }}.schema.json`.

Status rules:
- `PASS`: all verification criteria met, all declared checks passed
- `PARTIAL`: non-blocking criteria unmet, blocking criteria all met
- `FAIL`: any blocking criterion unmet — downstream phase must not proceed

## Output Contract

**Good output:** {{ good_output_example }}

**Bad output:** {{ bad_output_example }}

**Discriminator:** {{ discriminator }}

## Failure Modes

{{ failure_modes }}

## References

Load on demand only:
{{ references_list }}
