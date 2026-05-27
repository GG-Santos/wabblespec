# Error Routing Rules

Per-wave reference for Executor. Maps error type to routing action. Full type definitions: `.wabblespec/engine/shared/references/error-taxonomy.md`.

---

## Routing Table

| Error type | recoverable | Action | Target |
|---|---|---|---|
| SOFT | true | retry | Same module — one retry. If retry fails, escalate to HARD. |
| HARD | false | halt | Halt wave. Trigger rollback (human-confirmed). |
| DEPENDENCY | false | pause | Human checkpoint — surface upstream failure, await resolution. |
| CONTEXT_EXHAUSTION | true | compress | Economy module — compress context, resume from last checkpoint. |
| SPEC_VIOLATION | false | loop_back | Spec stage that owns the violated artifact (Specify or ScopeFrame). |
| STALENESS_VIOLATION | false | quarantine | Memory module — quarantine expired evidence, require fresh fetch. |

---

## Decision tree

```
Error received from wave
  -> recoverable = true?
       SOFT: retry once
         -> retry succeeds: continue
         -> retry fails: escalate to HARD
       CONTEXT_EXHAUSTION: invoke Economy -> resume from last checkpoint

  -> recoverable = false?
       HARD: halt wave -> write FAIL receipt -> await human rollback confirmation
       DEPENDENCY: pause execution -> surface missing upstream to user -> wait
       SPEC_VIOLATION: pause execution -> loop back to appropriate spec stage -> wait
       STALENESS_VIOLATION: quarantine evidence -> surface to user -> require fresh fetch -> wait
```

---

## Required error event fields

When emitting an error, include all fields required by `.wabblespec/engine/shared/schemas/error-event.schema.json`:
- `error_type`: one of the 6 types above
- `recoverable`: must match the table exactly
- `upstream_module`: required for DEPENDENCY errors
- `artifact`: required for SPEC_VIOLATION and STALENESS_VIOLATION
- `staleness_state`: required for STALENESS_VIOLATION

---

## Rollback protocol (HARD errors only)

1. Write wave receipt with `status: "FAIL"` and `failure_reason`
2. Surface rollback target from wave plan `rollback_to` field to user
3. Wait for human confirmation before restoring any files
4. Restore files from `.wabblespec/checkpoints/wave-<N>-<timestamp>/` snapshot
5. Update `checkpoint-meta.json` with `restored_at` timestamp
