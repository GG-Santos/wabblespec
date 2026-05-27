# Acceptance Tests — Deploy (L7)

## AT-DEPLOY-01: Artifact hash verified before any deployment action

**Given** a Deploy invocation for any environment
**When** Deploy begins execution
**Then** it re-computes SHA-256 of the artifact and compares against the manifest hash before touching the environment; a mismatch FAILs with `ARTIFACT_HASH_MISMATCH`

---

## AT-DEPLOY-02: Prior environment receipt required — no skip to production

**Given** a Deploy invocation targeting `production`
**When** Deploy checks preconditions
**Then** a staging Deploy receipt must exist; absent staging receipt FAILs with `MISSING_PRIOR_ENV_RECEIPT`

**Given** a Deploy invocation targeting `staging`
**When** Deploy checks preconditions
**Then** a dev Deploy receipt must exist

---

## AT-DEPLOY-03: Production requires Attestation

**Given** a Deploy invocation targeting `production`
**When** Attestation is missing
**Then** Deploy FAILs with `MISSING_ATTESTATION` — no automated production deploy without human sign-off

---

## AT-DEPLOY-04: Rollback plan must be declared before activation

**Given** a Deploy invocation with no rollback plan declared
**When** Deploy checks for the rollback plan
**Then** Deploy FAILs with `MISSING_ROLLBACK_PLAN` — deployment does not begin without an exit plan

---

## AT-DEPLOY-05: Health check failure triggers immediate rollback

**Given** a deployment that completes but health check fails
**When** the health check result is evaluated
**Then** rollback is executed immediately and the deploy receipt records `status: ROLLED_BACK`

---

## AT-DEPLOY-06: Deploy receipt contains required fields

**Given** a completed Deploy run (any outcome)
**Then** the receipt at `.wabblespec/state/receipts/deploy-receipt-{env}-{timestamp}.json` contains:
- `environment`
- `version`
- `artifact_hash_verified`
- `prior_env_receipt_verified`
- `attestation_verified`
- `rollback_plan`
- `health_check_passed`
- `status` (DEPLOYED | ROLLED_BACK | FAILED)
