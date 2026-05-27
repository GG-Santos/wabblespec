---
name: rollback
description: Controlled restoration to prior known-good state. Three rollback target types: wave checkpoint (Executor), deploy snapshot (Deploy receipt rollback_to field), Forge pre-promotion snapshot. All rollback operations require Attestation. Release rollback provides instructions but does not execute git operations. Hash verification required after restoration.
---

# Rollback

You restore. You do not decide to restore — Executor or Deploy detects the rollback condition, human confirms via Attestation, then you execute.

## What this skill does

Controlled restoration to prior known-good state. Three rollback target types: wave checkpoint (Executor), deploy snapshot (Deploy receipt rollback_to field), Forge pre-promotion snapshot. All rollback operations require Attestation. Release rollback provides instructions but does not execute git operations. Hash verification required after restoration.

## When to use

- Executor detects HARD error and checkpoints a rollback target
- Deploy detects rollback trigger condition
- Forge pre-promotion snapshot needs restoration
- Explicit `/rollback` command with target declared

All activations require Attestation before execution.

## Four rollback target types

**Wave checkpoint** — restores to last Executor checkpoint written before the failing wave. Source: `.wabblespec/state/checkpoints/<wave-id>/`.

**Deploy snapshot** — restores to prior deployment state. Source: `rollback_to` field in Deploy receipt.

**Forge pre-promotion snapshot** — restores framework files to pre-promotion state. Source: `.wabblespec/state/experiments/rollback-<timestamp>/`.

**Worktree isolation** — discards an isolated git worktree branch created for a high-risk wave. No file restoration needed — work was never merged to main branch. Source: `.worktrees/<wave-id>/` in target project. Trigger: High-complexity waves with irreversible operations. Sandbox fallback: Type 1 wave checkpoint when git worktree is unavailable. Full specification: `rules/checkpoint-types.md` Type 4.

## Process

1. Identify rollback target type and source path
2. State what will be restored and what will be lost (since checkpoint)
3. Require Attestation — human confirms before any restoration
4. Execute restoration
5. Verify: hash check on restored files against checkpoint manifest
6. Write rollback receipt declaring: target, timestamp, files restored, hash verification result

## Release rollback

Git tag revert is partially manual. Rollback provides the exact commands:
```
git tag -d <version>
git push origin :refs/tags/<version>
```
Does not execute these — provides to human for manual execution.

## Output contract

Writes a receipt to `.wabblespec/state/receipts/` on successful completion.

## What not to do

- Do not execute any restoration without Attestation
- Do not skip hash verification after restoration
- Do not execute git operations for release rollback — provide commands only
