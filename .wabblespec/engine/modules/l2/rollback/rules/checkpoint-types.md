# Rollback Checkpoint Types

Three rollback target types. Each has a distinct source path, trigger condition, and verification requirement.

---

## Type 1: Wave Checkpoint

Restores to the last Executor checkpoint written before a failing wave.

**Source path:** `.wabblespec/state/checkpoints/<wave-id>/`

**Trigger condition:** Executor detects HARD error during wave execution and writes a checkpoint. Rollback is activated by Executor (not by human) to signal the rollback target.

**Checkpoint structure:**
```
.wabblespec/state/checkpoints/<wave-id>/
  manifest.json         — list of all files modified in wave, with SHA-256 hashes before modification
  files/                — copy of all modified files at their pre-wave state
```

**Rollback process:**
1. Read `manifest.json` — enumerate files to restore
2. State what will be restored and what changes (made after the checkpoint) will be lost
3. Require Attestation — do not proceed without human confirmation
4. Copy each file from `checkpoints/<wave-id>/files/` back to its original path
5. Verify: SHA-256 each restored file against `manifest.json` hashes
6. Write rollback receipt

**After rollback:** Executor can re-attempt the failed wave from the checkpoint state.

---

## Type 2: Deploy Snapshot

Restores to the prior deployment state.

**Source path:** `rollback_to` field in the Deploy receipt (`deploy-receipt-<timestamp>.json`).

**Trigger condition:** Deploy module detects rollback trigger condition (health check failure, error rate spike, manual trigger). Deploy surfaces the `rollback_to` reference from its receipt.

**`rollback_to` field format:**
```json
{
  "rollback_to": {
    "env": "staging | dev",
    "artifact_sha256": "string",
    "artifact_path": ".wabblespec/artifacts/<manifest>",
    "deploy_receipt": ".wabblespec/state/receipts/deploy-receipt-<prev-timestamp>.json"
  }
}
```

**Rollback process:**
1. Read the prior deploy receipt at `rollback_to.deploy_receipt`
2. Verify artifact SHA-256 matches `rollback_to.artifact_sha256`
3. State what deployment state will be restored and what changes will be reverted
4. Require Attestation
5. Re-deploy the prior artifact to the target environment (using the same deploy mechanism — do not skip Deploy gates)
6. Confirm health checks pass at prior artifact version
7. Write rollback receipt

**Note:** Re-deployment uses the same Deploy module flow. Rollback is not a shortcut around Deploy gates.

---

## Type 3: Forge Pre-Promotion Snapshot

Restores framework files to their pre-Forge-promotion state.

**Source path:** `.wabblespec/state/experiments/rollback-<timestamp>/`

**Trigger condition:** Forge pre-promotion snapshot was created before promoting an experiment to production. If promotion is found to be defective, this snapshot restores the pre-promotion framework state.

**Snapshot structure:**
```
.wabblespec/state/experiments/rollback-<timestamp>/
  manifest.json         — list of framework files modified by Forge, with pre-promotion hashes
  files/                — copy of framework files at pre-promotion state
```

**Rollback process:**
1. Read `manifest.json` from the experiment's rollback directory
2. State which framework files will be restored and what promoted changes will be reverted
3. Require Attestation — framework rollback is high-impact
4. Copy each file from `rollback-<timestamp>/files/` back to production paths
5. Verify: SHA-256 each restored file against manifest hashes
6. Write rollback receipt
7. Update `.wabblespec/state/experiments/{plan-name}/experiment-manifest.schema.json` status to `rollback-executed`

---

## Attestation Requirement (all types)

All three types require human Attestation before execution. No automated rollback path exists.

Attestation presentation must include:
- Rollback type and source path
- Exact list of files that will be restored
- List of changes that will be permanently lost (since checkpoint/snapshot)
- SHA-256 hashes of source files that will replace current files

Do not begin restoration until Attestation is explicitly confirmed.

---

## Hash Verification (all types)

After restoring every file, verify SHA-256 of restored file against the checkpoint/snapshot manifest.

If any hash mismatches:
- Report exact mismatch (file path, expected hash, actual hash)
- Do NOT silently continue
- Mark rollback receipt status PARTIAL with mismatch details
- Surface to human for resolution

---

## Type 4: Worktree Isolation

Provides git-native isolation for high-risk waves. Stronger than Type 1 (file copies) because the entire working tree is isolated — changes cannot bleed into the main branch.

**Trigger conditions (all must be true):**
- Complexity is High, AND
- Wave contains at least one of: irreversible file operations, database migrations, breaking schema changes, or direct edits to framework files

**When NOT to use:** Low/Medium complexity, routine implementation waves, waves where Type 1 file checkpoint is sufficient. Worktree overhead is not justified for small tasks.

**Source path:** `.worktrees/<wave-id>/` at target project root (gitignored).

**Pre-wave setup process:**
1. Verify target project is a git repository (`git rev-parse --git-dir` exits 0)
2. Detect existing isolation: if `GIT_DIR != GIT_COMMON` (and not a submodule), skip creation — already isolated
3. Verify `.worktrees/` is in `.gitignore`. If not: add it, commit before proceeding
4. Create worktree on a new branch: `git worktree add .worktrees/<wave-id> -b wabble/<wave-id>`
5. Verify clean baseline in worktree (run project test suite or equivalent lint/check)
6. If baseline fails: report failures, require explicit human confirmation before continuing
7. Record worktree path and branch name in wave plan `rollback_to` field

**Rollback process (wave fails):**
1. State what changes exist in the worktree branch and what will be discarded
2. Require Attestation — human confirms worktree discard
3. Remove worktree: `git worktree remove --force .worktrees/<wave-id>`
4. Delete branch: `git branch -D wabble/<wave-id>`
5. Verify removal: confirm `.worktrees/<wave-id>/` no longer exists
6. Write rollback receipt — status, worktree path, branch discarded

**Cleanup after successful wave:**
Wave success does not mean automatic merge. After Verifier PASS:
1. Human reviews diff on `wabble/<wave-id>` branch
2. Human merges or cherry-picks to main branch (Rollback does not execute merge)
3. Rollback writes cleanup instructions — does not execute them
4. Human removes worktree and branch after merge

**Sandbox fallback:** If `git worktree add` fails (sandbox denial, no git repo, permission error): fall back to Type 1 wave checkpoint. Record fallback reason in wave plan. Do not silently skip — wave plan must reflect actual rollback type used.

**Attestation requirement:** Same as all rollback types — no restoration or discard without human Attestation.

---

## Release Rollback (git tag revert)

Not a checkpoint type — handled separately.

Rollback provides the exact git commands to human but does not execute them:
```
git tag -d <version>
git push origin :refs/tags/<version>
```

Human executes manually. Rollback writes a rollback receipt recording that commands were provided and human confirmation that execution occurred.
