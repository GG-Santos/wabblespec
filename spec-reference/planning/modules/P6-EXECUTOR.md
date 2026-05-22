# Module Plan — Executor (L2)

**Tier:** 1 — CRITICAL
**Layer:** L2 Orchestration
**v5.3 origin:** Execution logic embedded across Apply/Autopilot — formalized as standalone module in v6.1

---

## Purpose

Wave execution engine. Reads wave plan from Decompose. Manages Apply invocations per wave. Saves checkpoint state before each wave. Routes errors by type. Triggers rollback on HARD failure. Coordinates ModelRouter for runtime lane selection per wave. No implementation logic lives in Executor — it orchestrates; Apply implements.

---

## Activation

`skill-rules.json` triggers:
- Decompose produces locked wave plan
- Explicit `/execute` command with wave plan path
- Resume from checkpoint after DEPENDENCY or CONTEXT_EXHAUSTION error

---

## Execution Loop

```
For each wave in wave plan (in order):

  1. Request runtime lane from ModelRouter (task shape = wave context type)

  2. Save checkpoint state (file snapshot of project/repo/ at this point)

  3. Load required modules for this wave (platform + gateways + _shared/dev/)

  4. Invoke Apply with:
     -> Wave spec sections
     -> Loaded module context
     -> Runtime lane from ModelRouter

  5. Apply executes and reports:
     -> Output artifacts
     -> Any delta proposals (scope deviations)
     -> Errors (typed)

  6. Handle delta proposals:
     -> ADDITIVE/COSMETIC: pass to Specify --patch inline
     -> BREAKING: pause execution, loop back to spec stage

  7. Handle errors:
     -> SOFT: retry once, log to wave receipt
     -> HARD: halt wave, trigger rollback to prior checkpoint (human-confirmed)
     -> DEPENDENCY: pause, surface upstream failure, await resolution
     -> CONTEXT_EXHAUSTION: Economy compresses context, resume or checkpoint
     -> SPEC_VIOLATION: pause, loop back to Specify for correction
     -> STALENESS_VIOLATION: quarantine evidence, surface to MemorySearch

  8. Invoke Verifier with wave output + verification mode from wave plan

  9. Handle Verifier result:
     -> PASS: write wave receipt, advance to next wave
     -> FAIL: enter REVISE loop (max 3 cycles)
     -> BLOCKED: human escalation (Attestation required)

  10. Write wave receipt

After all waves: write final execution receipt, notify Archive
```

---

## Checkpoint State

Checkpoint is a snapshot of `project/repo/` before each wave begins. Format:

```json
{
  "wave": "integer",
  "wave_name": "string",
  "snapshot_path": ".wabblespec/checkpoints/wave-<N>-<timestamp>/",
  "saved_at": "timestamp",
  "files_snapshotted": ["array of paths"]
}
```

Checkpoints stored in `.wabblespec/checkpoints/`. Cleaned up after successful full execution. Preserved on HARD error for rollback.

Rollback restores from checkpoint. Always human-confirmed. Partial wave output is discarded — checkpoint state is restored fully.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Wave receipts | `.wabblespec/receipts/wave-<N>-receipt.md` | Per-wave I10 compliance |
| Final execution receipt | `.wabblespec/receipts/execution-receipt.md` | Full execution I10 compliance |
| Checkpoints | `.wabblespec/checkpoints/` | Rollback state |
| Checkpoint index | `.wabblespec/checkpoints/index.md` | Lists all checkpoints, status |

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over checkpoints/ and execution receipts |
| `scripts/snapshot.py` | Script | Deterministic file snapshot for checkpoint creation |
| `rules/error-routing.md` | Rules | Error type to action map |
| `rules/rollback-policy.md` | Rules | Rollback conditions, human confirmation requirement |
| `rules/delta-handling.md` | Rules | ADDITIVE vs. BREAKING delta routing |
| `schemas/checkpoint.schema.json` | Schema | Checkpoint index validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Decompose | Reads wave plan — cannot start without it |
| ModelRouter | Requests runtime lane before each wave |
| Apply | Invokes Apply for each wave — Apply implements, Executor orchestrates |
| Verifier | Invokes Verifier at each wave checkpoint |
| Specify | Routes BREAKING delta proposals and SPEC_VIOLATION errors to Specify |
| Economy | Economy handles CONTEXT_EXHAUSTION — Executor resumes after compression |
| Archive | Notifies Archive on full execution complete |
| Autopilot | Autopilot can manage Executor for multi-stage full lifecycle runs |

---

## Verification Mode

**Observation** — all waves completed, all wave receipts written, checkpoint index updated, final execution receipt written. Verifier handles per-wave gate checks independently.

---

## Receipt Extension Fields

```json
{
  "waves_planned": "integer",
  "waves_completed": "integer",
  "waves_failed": "integer",
  "rollbacks_triggered": "integer",
  "delta_proposals": "integer",
  "breaking_deltas": "integer",
  "errors_by_type": {
    "SOFT": "integer",
    "HARD": "integer",
    "DEPENDENCY": "integer",
    "CONTEXT_EXHAUSTION": "integer",
    "SPEC_VIOLATION": "integer",
    "STALENESS_VIOLATION": "integer"
  },
  "checkpoints_saved": "integer"
}
```

---

## v5.3 Mapping

| v5.3 execution (Apply + Autopilot) | v6.1 Executor |
|---|---|
| Apply managed its own wave execution | Executor manages waves, Apply implements per-wave |
| Rollback checkpoints in Decompose (v5.2+) | Checkpoints saved by Executor before each wave |
| Error handling in Apply | Error routing in Executor (typed, not prose) |
| Autopilot meta-orchestrated everything | Executor owns execution loop; Autopilot owns full lifecycle |
| No explicit checkpoint state format | Structured checkpoint snapshot with index |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Checkpoint storage format | File copy (current) vs. git stash vs. diff patch | Per-module planning |
| Checkpoint cleanup policy | On success only vs. configurable retention | Per-module planning |
| Parallel wave execution | Sequential only (current) vs. parallel for independent waves | Post-MVP consideration |
