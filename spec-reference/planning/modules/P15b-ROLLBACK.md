# Module Plan — Rollback (L2)

**Tier:** 3 — SUPPORTING
**Layer:** L2 Orchestration
**v5.3 origin:** Rollback module — explicit recovery for completed-state failures

---

## Purpose

Execute controlled rollback to a prior known-good state. Distinct from Executor's checkpoint-based mid-wave recovery (which handles failures during execution). Rollback handles post-completion failures: a wave that passed but produced bad output, a deploy that succeeded but broke production, a Forge promotion that passed Benchmark but behaved unexpectedly in production. All Rollback operations require Attestation — they are irreversible state changes.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/rollback <target>` command only — never auto-triggered
- Target types: wave checkpoint, deploy snapshot, Forge pre-promotion snapshot
- Cannot activate without:
  - Rollback target exists (checkpoint or snapshot path declared)
  - Attestation received

---

## Rollback Targets

| Target type | Source | What is restored |
|---|---|---|
| Wave checkpoint | `.wabblespec/checkpoints/<wave-id>/` (Executor) | project/repo/ state at checkpoint |
| Deploy snapshot | Deploy receipt rollback_to field | Previous deployed artifact version |
| Forge snapshot | `.wabblespec/experiments/rollback-<timestamp>/` | Live framework files pre-promotion |
| Release revert | Release receipt git_tag field | Code state — requires git operations + human steps |

---

## Workflow

```
1. Receive rollback target (type + identifier)

2. Locate rollback source:
   -> Wave: read checkpoint from .wabblespec/checkpoints/
   -> Deploy: read deploy receipt rollback_to field
   -> Forge: read .wabblespec/experiments/rollback-<timestamp>/
   -> Release: read git tag from release receipt

3. Present rollback summary to human:
   -> What will be restored
   -> From where
   -> What will be lost (changes made after target state)

4. Request Attestation — human explicitly confirms

5. Execute rollback:
   -> Wave checkpoint: restore project/repo/ files from checkpoint
   -> Deploy: trigger Deploy module with previous artifact version
   -> Forge: copy snapshot files back to live framework paths
   -> Release: provide git revert instructions (cannot execute git tag deletion — human step)

6. Verify restored state:
   -> Hash check: restored files match checkpoint/snapshot hashes
   -> IF mismatch: HARD error — do not claim success

7. Write Rollback receipt
```

---

## Release Rollback Note

Release rollback (reverting a published git tag and release) is partially manual. Rollback provides the git commands and steps, but does not execute them — git tag deletion and force-push are destructive operations that must be human-executed. Rollback writes a rollback instruction document to `.wabblespec/receipts/rollback-release-instructions.md`.

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — explicit command only |
| `rules/attestation-required.md` | Rules | All rollback operations require Attestation |
| `rules/restore-verification.md` | Rules | Hash check required after restore |
| `rules/release-partial.md` | Rules | Release rollback is partially manual — document human steps |
| `schemas/rollback-record.schema.json` | Schema | Rollback record format |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Executor | Executor's checkpoint is Rollback's wave target source |
| Deploy | Rollback triggers Deploy with previous artifact for deploy-level rollback |
| Forge | Rollback reads Forge pre-promotion snapshot |
| Release | Rollback provides instructions for release-level revert (human execution) |
| Autopilot | Autopilot routes to Rollback when post-wave verification fails after completion |

---

## Verification Mode

**Attestation** — human sign-off before any restoration, restored state hash-verified, receipt written.

---

## Receipt Extension Fields

```json
{
  "rollback_target_type": "wave|deploy|forge|release",
  "rollback_target_id": "string",
  "attestation_received": "boolean",
  "restore_hash_verified": "boolean",
  "partial_manual_steps": "boolean",
  "instructions_path": "string"
}
```
