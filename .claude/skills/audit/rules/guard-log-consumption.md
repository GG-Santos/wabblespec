# Guard Log Consumption

Audit reads Guard operation logs as a primary signal source. This document defines how to locate, parse, and classify Guard logs.

## Log location

Guard writes operation logs to `.wabblespec/receipts/` with names matching `guard-wave-*-receipt.json` and to session-level logs if the runtime supports PostToolUse hooks.

For cross-session Guard log consumption, Audit reads all `guard-*-receipt.json` files in `.wabblespec/receipts/` scoped to the current task (matching `task_id` if present, or by timestamp proximity).

## Parsing Guard receipts

Each Guard receipt contains:
- `checks_run`: array of invariant checks performed
- `checks_passed`: array of checks that passed
- `blocked_operations`: array of operations that were halted by Guard
- `risk_tier_triggered`: the highest risk tier encountered in this Guard run
- `violations`: list of invariant violations detected

Audit reads these fields and aggregates across all Guard receipts in scope.

## Classification of Guard findings

### Legitimate block
Guard blocked a genuinely dangerous operation (e.g., destructive filesystem op, command injection attempt, out-of-scope write). This is Guard working correctly. Record in audit report but do not count as a violation.

**Signal:** `blocked_operations` entry has `risk_tier: HIGH | CRITICAL` and the operation is genuinely risky (matches command-risk-policy.md taxonomy).

### Policy violation
Guard blocked an operation that should have been permitted, indicating a misconfigured Guard policy, an overly broad block rule, or a module operating outside its declared scope.

**Signal:** Same operation type blocked ≥ 3 times in one session — likely a policy misconfiguration, not a one-off dangerous attempt.

### Freeze violation
Guard detected a module operating on files outside its declared scope boundary (e.g., writing to another module's directory without authority).

**Signal:** `blocked_operations` entry with `violation_type: scope-freeze`.

## Escalation threshold

If Guard logs show any CRITICAL tier trigger: `attestation_required: true`. Human sign-off needed before the audit receipt can be used to approve a release.
