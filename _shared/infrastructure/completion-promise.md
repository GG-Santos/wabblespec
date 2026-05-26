# Completion Promise

Loop termination and error recovery patterns for all modules. Every module that enters a loop or cycle must have a defined exit condition. Implied completion is prohibited (I10).

## The promise

A module that starts a process must either:
1. Complete it and write a receipt, OR
2. Fail explicitly with a documented reason in the receipt, OR
3. Escalate to human with a documented block reason

There is no fourth option. "Partially complete" is FAIL with documented partial state.

## Loop termination patterns

### Convergence loop (REVISE cycles)
Used by: Reviewer, Adversary+Grader, Enhance

```
max_cycles: integer (declared before loop starts, never modified mid-loop)
current_cycle: 0

while current_cycle < max_cycles:
    run pass
    if exit_condition met: break
    current_cycle += 1

if current_cycle == max_cycles and not exit_condition:
    ESCALATE — max cycles reached without convergence
```

Never exit silently when max_cycles is reached. Always escalate.

### Wave loop (Executor)
Used by: Executor, Autopilot

```
for each wave in wave_plan:
    run wave
    if wave fails: HALT — do not proceed to next wave
    write wave receipt
    
if all waves pass: write execution-receipt
```

No wave is skipped. No wave failure is absorbed silently.

### Retry loop (transient errors only)
Used by: ReferenceLoad, Memory operations

```
max_retries: 3
backoff: 2^attempt seconds

for attempt in 0..max_retries:
    try operation
    if success: break
    if attempt == max_retries: FAIL with last_error recorded
```

Retry only on transient errors (network timeout, lock contention). Never retry on logical errors (schema validation failure, permission denied).

## Error recovery patterns

### Recoverable error
Error that can be resolved without human input: retry (transient), skip (optional step), or use fallback value.

Receipt records: `error_type: RECOVERABLE`, `recovery_action: string`.

### Non-recoverable error
Error requiring human input or investigation: missing required file, schema validation failure, CRITICAL Guard block, missing receipt in chain.

Receipt records: `status: FAIL`, `failure_reason: string`. Module halts. Does not attempt to continue.

### Escalation
Decision requires human judgment: REVISE max cycles reached, BREAKING change requires consumer notification, gateway BLOCK.

Receipt records: `status: BLOCKED`, `escalation_reason: string`, `human_input_required: true`.

## Orphan session recovery

If a session ends without an Archive receipt: the receipt-index.json entry remains `IN_PROGRESS`. On next session start, Archive --sweep mode detects orphaned IN_PROGRESS entries older than the current session and flags them for human review (not auto-resolution — orphaned state may contain valid partial work).
