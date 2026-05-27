# Error Event Catalog

**Schema:** `.wabblespec/engine/shared/schemas/error-event.schema.json`  
**Consumed by:** l2/executor (routing), l2/triage (resolution), l2/grader (audit), l6/copy (user-facing message composition)  
**Purpose:** Definitive list of typed error events the framework can emit, with the module that emits each, the routing action it triggers, and the user-facing message template Copy must use.

---

## Error types and routing table

| Type | Routing action | Recoverable | Meaning |
|---|---|---|---|
| `SOFT` | `retry` | true | Transient or recoverable condition; retry same operation |
| `HARD` | `halt` | false | Unrecoverable violation; abort wave, require human intervention |
| `DEPENDENCY` | `pause` | true | Upstream module failure; pause until upstream resolves |
| `CONTEXT_EXHAUSTION` | `compress` | true | Context window pressure; summarize and continue |
| `SPEC_VIOLATION` | `loop_back` | true | Task card or scope violation; return to ScopeFrame or Reviewer |
| `STALENESS_VIOLATION` | `quarantine` | false | EXPIRED evidence presented; quarantine artifact, block use |

---

## Per-module error event registry

### L2: Guard

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Schema validation failure | `HARD` | Missing required fields or malformed input in wave | "Wave inputs are malformed — required field `{field}` is missing. Correct the wave plan before resubmitting." |
| Scope violation | `SPEC_VIOLATION` | Wave targets out-of-scope file | "The file `{path}` is not in scope for this task. Review scope.md and revise the wave plan." |
| Scope expansion | `SPEC_VIOLATION` | Wave expands beyond current task card stage | "This wave would expand the task beyond the declared scope. Return to ScopeFrame to revise the task card." |
| I9 violation (expired evidence) | `HARD` | EXPIRED staleness state in wave inputs | "Evidence `{artifact}` has expired and cannot be used. Remove or refresh the evidence before continuing." |
| I10 violation (missing prior receipt) | `DEPENDENCY` | Prior wave receipt not found | "Wave {N} cannot start — receipt for wave {N-1} is missing. Resolve the previous wave first." |
| I11 violation (boundary crossed) | `HARD` | Wave writes to `.wabblespec/` framework space | "Wave attempted to write to framework space at `{path}`. Waves may only write to product space." |
| I1/I2/I3/I6/I12 violation | `SPEC_VIOLATION` | Invariant check failure | "Invariant {code} violated: {description}. Route to Reviewer for resolution." |
| Unauthorized write target | `HARD` | Module lacks authority over target path | "Module `{module}` does not have declared authority over `{path}`. Update skill-rules.json or route to the correct module." |
| Missing skill-rules.json | `HARD` | Module has no authority declaration (I5) | "Module `{module}` has no skill-rules.json. All modules require an authority declaration. This is an I5 violation." |
| COMMAND_RISK BLOCK | `HARD` | Shell command classified BLOCK | "Command `{command}` is classified BLOCK. Reason: {risk}. Safer alternative: {alternative}. Remove or replace before resubmitting." |
| `WABBLESPEC_MEMORY_READY` failure | `HARD` | `WABBLESPEC_MEMORY_PATH` unset | "`WABBLESPEC_MEMORY_PATH` is not set. Run the bootstrap script before starting a session that uses Memory." |
| `CHROMADB_EXISTS` failure | `HARD` | `chroma.sqlite3` absent | "ChromaDB store not found at `{path}`. Run: `python scripts/migrate-json-drawers.py` to initialize." |
| `CLOSET_INDEX_GATE` violation | `SPEC_VIOLATION` | Closet indexing triggered before 50-drawer threshold | "Closet indexing requires at least 50 curated drawers. Current count: {n}. Add more drawers before building the closet index." |

---

### L2: Executor

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Wave plan assembly failure | `SOFT` | Cannot assemble wave plan from task card | "Wave plan could not be assembled. Verify the task card is complete and retry." |
| Module not found | `HARD` | Declared module in recipe.json not registered | "Module `{module}` is declared in the recipe but not registered in framework.yaml. Register it before executing." |
| Context exhaustion | `CONTEXT_EXHAUSTION` | Context window pressure detected mid-wave | "Context window is approaching capacity. Compressing intermediate state and continuing." |

---

### L2: Verifier

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Acceptance criterion FAIL | `HARD` | Verifier check fails with no retry path | "Acceptance criterion `{criterion_id}` failed: {detail}. The wave output does not meet the declared requirement." |
| Missing executor receipt | `DEPENDENCY` | No executor receipt to verify against | "Verifier cannot run — executor receipt for wave {N} is not present. Ensure the executor completed successfully." |

---

### L2: Archive

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Missing receipt | `HARD` | Required receipt absent from delivery receipt set | "Delivery receipt is incomplete — receipt `{receipt_id}` is missing. Archive cannot proceed with partial delivery. See runbook: `docs/runbooks/missing-receipt.md`." |
| Shift trigger error | `SOFT` | BREAKING/ADDITIVE delta triggers Shift but Shift encounters conflict | "Shift triggered by {delta_class} change. A conflict was found at `{location}`. Resolve the conflict manually and rerun Archive." |

---

### L2: Rollback

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| No rollback target found | `HARD` | No prior receipt to roll back to | "Rollback cannot proceed — no prior receipt found for `{task_id}`. Manual recovery is required." |
| Rollback conflict | `HARD` | Rollback would overwrite uncommitted changes | "Rollback blocked by uncommitted changes in `{path}`. Stash or commit changes before rolling back." |

---

### L5: Memory

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| STALENESS_VIOLATION | `STALENESS_VIOLATION` | EXPIRED evidence presented to any module | "Evidence `{drawer_id}` is EXPIRED and cannot be used. It has been quarantined. Request a fresh version or remove it from the wave inputs." |
| Schema mismatch | `HARD` | ChromaDB drawer schema does not match current schema | "Drawer `{id}` has a schema mismatch with the current drawer.schema.json. Trigger MemoryMine rebuild to reindex." |

---

### L5: Dream

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| PID lock active | `SOFT` | `.dream.pid` exists — another Dream process running | "Dream is already running (PID: {pid}). Wait for the current run to complete before starting a new one." |
| State transition error | `HARD` | Dream attempted to change staleness state (not its role) | "Dream attempted a staleness state transition, which is not its role. State transitions are owned by staleness-checker.py. Check the implementation." |

---

### L5: Forget

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Force required | `SPEC_VIOLATION` | Attempting to delete FRESH/AGING drawer without `force: true` | "Drawer `{id}` is {state}. Deletion requires `force: true` and a `compliance_reference`. Confirm this is intentional before proceeding." |
| Provenance record deletion attempt | `HARD` | Wave plan includes deletion of a Provenance ledger entry | "Provenance records are append-only and cannot be deleted. Remove the deletion step from the wave plan." |

---

### L7: Deploy

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Missing artifact hash | `HARD` | Artifact hash not present before deploy begins | "Deployment cannot start — artifact hash not verified. Run the hash verification step before invoking Deploy." |
| Missing prior environment receipt | `DEPENDENCY` | No receipt for the prerequisite environment | "Cannot deploy to `{env}` — no receipt found for the required prior environment `{prior_env}`. Deploy must progress through environments in order." |
| Missing Attestation (production) | `HARD` | Production deploy attempted without Attestation | "Production deployment requires Attestation. No Attestation found for this build. Complete the Attestation process before deploying to production." |
| Health check failure | `HARD` | Post-deploy health check did not pass | "Health check failed after deployment to `{env}`. Initiating rollback. Check `docs/runbooks/` for diagnosis steps." |
| Incomplete runbooks | `HARD` | Monitor receipt references stub/partial runbooks | "Production deploy blocked — runbook stubs are incomplete for: {runbook_list}. Replace all `___ UNDECLARED` markers before deploying." |

---

### L7: Release

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Missing production deploy receipt | `DEPENDENCY` | Release attempted without a production deploy receipt | "Release cannot proceed — no production deployment receipt found. Deploy to production before creating a release." |
| Unsigned tag | `HARD` | Tag is not annotated and signed | "Release tag `{tag}` must be an annotated signed tag. Use `git tag -a -s` to create it." |

---

### L7: Package

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Signing failure | `HARD` | Artifact signing fails or signing key unavailable | "Package signing failed for `{artifact}`. This is a hard stop — unsigned artifacts cannot be delivered. Verify the signing key is available and retry." |
| Key in manifest | `HARD` | Signing key found in package manifest | "Package manifest contains a signing key at `{path}`. Remove it immediately — keys must not be included in distributed packages." |
| Missing delivery receipt | `DEPENDENCY` | Package attempted without delivery receipt | "Package cannot run — no delivery receipt found for `{task_id}`. Ensure the delivery phase completed successfully." |

---

### L7: Monitor

| Event | Type | Trigger | User-facing message template |
|---|---|---|---|
| Guard log pattern detected | `DEPENDENCY` | Repeated blocks (≥ 3), CRITICAL tier, or freeze violation in session Guard logs | "Guard log monitoring detected: {pattern} (occurrences: {count}). Routing to Triage for investigation." |
| UNDECLARED SLO | `SOFT` | SLO dimension found with no declared target | "SLO for `{dimension}` is undeclared in performance-budgets.md. Monitor will not generate an alert for this dimension. Declare a target to enable monitoring." |

---

## User-facing message rules

These rules apply when Copy uses error messages from this catalog. They supplement, not replace, Copy's own rules.

1. **Never use "Something went wrong."** Every error message must name the specific failure (`receipt missing`, `hash not verified`, `signing failed`, etc.) and the concrete next step.

2. **Name the artifact or module.** Messages that reference only a generic category ("the deployment failed") are not actionable. Include `{task_id}`, `{path}`, `{module}`, or `{artifact}` as appropriate.

3. **Include the next step.** Every error message must tell the user what to do next: remove the step, run a script, add a field, or route to a specific module.

4. **HARD errors must not suggest retry.** Routing action `halt` means human intervention is required. Do not include retry language in HARD error messages.

5. **SOFT errors must not suggest escalation.** Routing action `retry` is expected to succeed eventually. Do not include panic language.

6. **STALENESS_VIOLATION messages must include "quarantined."** Users must understand the evidence is not just stale — it has been set aside and cannot be used until refreshed.

---

## Adding a new error event

1. Confirm the error type matches one of the 6 in `error-event.schema.json`. If a new type is genuinely needed, update the schema first.
2. Add the entry to this catalog in the emitting module's section.
3. Write the user-facing message template following the rules above.
4. Update the emitting module's SKILL.md to document when it emits the new error.
5. Register the routing action in the orchestration config at `.wabblespec/engine/shared/references/orchestration.md` if not already handled by the type's default routing.
