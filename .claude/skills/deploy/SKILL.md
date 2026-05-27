---
name: deploy
description: Executes deployment of a packaged artifact to a target environment. Requires package receipt + prior environment Deploy receipt. Production requires Attestation. Rollback plan declared before activation. Never deploys without verified artifact manifest.
---

# Deploy

You move a signed artifact from Package into a running environment. You verify the artifact before touching the environment. You require proof that the prior environment succeeded before deploying to production. You never deploy without a declared rollback plan.

## What this skill does

```
dev → staging → production

Each hop requires:
  - Package receipt (artifact is signed and manifested)
  - Deploy receipt from prior environment (cannot skip staging to reach production)
  - Rollback plan declared in this invocation
  - Attestation required for production hop only
```

## When to use

Invoked per activators declared in `skill-rules.json`.

## Inputs

- `package-receipt-*.json` — confirms artifact is signed
- `manifest-{version}-{timestamp}.json` — artifact hashes for verification
- `deploy-receipt-{prior-env}-*.json` — proof prior environment passed
- Rollback plan (declared inline or in deployment config)
- Attestation (production only — signed confirmation from authorized human)

## How to do it

### Step 1 — Verify package receipt and manifest

Load manifest. Re-compute SHA-256 of the artifact about to be deployed. Compare against manifest hash. If mismatch: FAIL with `ARTIFACT_HASH_MISMATCH` — do not proceed.

### Step 2 — Verify environment preconditions

- **staging:** confirm dev Deploy receipt exists
- **production:** confirm staging Deploy receipt exists + Attestation signed

If missing prior receipt: FAIL with `MISSING_PRIOR_ENV_RECEIPT`.
If production and missing Attestation: FAIL with `MISSING_ATTESTATION`.

### Step 3 — Confirm rollback plan

Rollback plan must be declared before deployment begins:

```yaml
rollback:
  strategy: previous-version | blue-green-swap | feature-flag-disable
  previous_version: "1.1.2"          # for previous-version strategy
  rollback_trigger: auto-on-healthcheck-fail | manual
  rollback_window_minutes: 30
  verified_at: "ISO-8601"            # when rollback was last tested
```

If no rollback plan: FAIL with `MISSING_ROLLBACK_PLAN`.

### Step 4 — Execute deployment

Platform-specific:

**Kubernetes:**
```bash
kubectl set image deployment/app app=registry/app:${VERSION}
kubectl rollout status deployment/app --timeout=5m
```

**ECS:**
```bash
aws ecs update-service --cluster prod --service app \
  --task-definition app:${TASK_REVISION} --force-new-deployment
```

**Lambda:**
```bash
aws lambda update-function-code \
  --function-name app --zip-file fileb://app.zip
aws lambda publish-version --function-name app
```

**Serverless / static:**
```bash
aws s3 sync dist/ s3://bucket/ --delete
aws cloudfront create-invalidation --distribution-id ID --paths "/*"
```

### Step 5 — Health check

After deployment, run health checks before declaring success:
- HTTP: `GET /health` returns 200 within 30s
- Expected response body matches declared contract

If health check fails: execute rollback immediately. Write deploy receipt with `status: ROLLED_BACK`.

### Step 6 — Write deploy receipt

## Output contract

**deploy-receipt** (`.wabblespec/state/receipts/deploy-receipt-{env}-{timestamp}.json`):
```json
{
  "environment": "dev | staging | production",
  "version": "string",
  "artifact_hash_verified": "boolean",
  "prior_env_receipt_verified": "boolean",
  "attestation_verified": "boolean",
  "rollback_plan": "object",
  "health_check_passed": "boolean",
  "status": "DEPLOYED | ROLLED_BACK | FAILED"
}
```

## Non-negotiable rules

1. Artifact hash verified against manifest before any deployment action.
2. Prior environment receipt required — no skip-to-production.
3. Production requires Attestation — no automated production deploy without human sign-off.
4. Rollback plan declared before activation — no deploy without exit plan.
5. Health check failure triggers immediate rollback.

## Common failure modes

1. **Deploying to production without staging receipt.** Staging is not optional. The deploy chain exists because staging catches environment-specific issues that dev doesn't.

2. **Skipping artifact verification.** An artifact that passes Package checks may be corrupted in transit. Re-verify hash before deployment.

3. **Declaring rollback plan without testing it.** `verified_at` field is not cosmetic — rollback plans that have never been exercised often fail when needed. Test rollback in staging.
