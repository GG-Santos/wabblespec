# Cold-Start Behavior — Forget

Defines what Forget does when its expected compliance policy or memory artifacts are absent.

## Absent: memory store

Condition: `memory/` is empty or does not exist.
Detection: Index read returns empty.
Action: Forget run is a no-op — nothing to delete. Log: "Memory store empty — no deletion targets." Return immediately with zero deletions.

## Absent: compliance-policy.md

Condition: `rules/compliance-policy.md` missing.
Detection: File read returns 404.
Action: BLOCK Forget execution. Surface: "compliance-policy.md required before Forget can execute. Deletion without policy context risks non-compliant data handling."
Do NOT: Proceed without a declared compliance policy.

## Absent: deletion-types.md

Condition: `rules/deletion-types.md` missing.
Detection: File read returns 404.
Action: Apply known deletion types from SKILL.md (hard_delete, soft_delete, anonymize). Log: "deletion-types.md missing — using SKILL.md definitions."

## Absent: target drawer specified

Condition: Forget triggered without specifying what to delete.
Detection: No drawer ID or deletion criteria in request.
Action: Surface: "Forget requires explicit deletion target (drawer ID, topic pattern, or compliance trigger). Refusing to operate without a declared target."
Do NOT: Auto-discover and delete drawers without explicit targeting.

## Absent: human confirmation for hard_delete

Condition: A hard_delete operation is requested without explicit confirmation step in the call.
Detection: Deletion type is `hard_delete` but no confirmation receipt.
Action: BLOCK. Surface: "hard_delete requires explicit human confirmation. Re-invoke with confirmation flag."
Do NOT: Hard-delete without confirmation, even with compliance justification.

## Default state on cold start

| Field | Default |
|---|---|
| `deletions_executed` | 0 |
| `deletion_type` | `soft_delete` (default; hard_delete requires explicit declaration) |
| `cascade` | false (related drawers not deleted unless explicitly declared) |
| `audit_log` | Written — every Forget run produces a deletion receipt |
| `recoverable` | true for soft_delete; false for hard_delete |
