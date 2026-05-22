# Module Plan — Deploy (L7)

**Tier:** 3 — SUPPORTING
**Layer:** L7 Delivery
**v5.3 origin:** Deploy module — deployment execution and verification

---

## Purpose

Execute deployment of built artifacts to declared environments. Deploy does not build — it receives built artifacts from Package or Executor and pushes them to the declared deployment target. Every deployment writes a deploy receipt. Rollback is declared before deploy begins, not invented during failure.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/deploy <environment>` command
- Delivery gate: Verifier passes all gates, Archive completes, Deploy triggered
- Cannot activate without:
  - Built artifact (from Package or Executor output)
  - Deployment target declared in spec
  - Rollback plan declared in spec or wave plan

Deploy never activates during active Executor waves. Deploy is post-execution, not concurrent.

---

## Deployment Targets

Deploy routes to platform-specific deployment modules based on Recipe's active build target:

| Build target | Deployment mechanism |
|---|---|
| Web | CDN deploy (Vercel, Cloudflare Pages, S3+CloudFront), static or SSR |
| API/Service | Container registry push + orchestrator deploy (Kubernetes, ECS, Cloud Run) |
| Mobile | App store submission (TestFlight, Play Console internal track) |
| Desktop | Distribution channel upload (GitHub Releases, store submission) |
| CLI | Registry publish (npm, PyPI, crates.io, Homebrew) — handled by Package |
| IoT/Embedded | OTA update server push or physical flash (declared in spec) |
| Library/Package | Registry publish — handled by Package |
| Data/Pipeline | Orchestrator deploy (Airflow DAG upload, dbt run trigger) |
| AI/Agent | Model endpoint deploy or agent service deploy |

---

## Environment Model

Environments declared in spec before Deploy can activate:

```markdown
## Environments

| Name | Target | Promotion gate | Rollback target |
|---|---|---|---|
| staging | staging cluster | manual approval | previous deploy |
| production | prod cluster | Attestation required | staging |
```

Promotion from staging to production requires Attestation (human sign-off) — non-negotiable for production deployments (I8 analog: irreversible actions require Attestation).

---

## Rollback Declaration

Rollback must be declared before Deploy begins:

```markdown
## Rollback Plan

**trigger:** error rate > 5% OR p99 latency > 2x baseline (example — declared per project)
**action:** redeploy previous artifact version
**rollback_to:** <artifact version or deploy ID>
**human_required:** true|false
**max_time_to_rollback:** 5 minutes
```

Deploy writes rollback plan to deploy receipt. Rollback execution is human-confirmed (never automatic in v6.1) — automatic trigger detection is allowed, but rollback action requires human confirmation.

---

## Workflow

```
1. Receive: artifact path, target environment, rollback plan

2. Validate prerequisites:
   -> Artifact exists and is signed/verified (from Package receipt)
   -> Environment declared in spec
   -> Rollback plan present
   -> Attestation received (if production environment)

3. Pre-deploy snapshot:
   -> Record current deployed version as rollback target
   -> Write snapshot to deploy receipt

4. Execute deployment via platform-specific mechanism

5. Post-deploy verification:
   -> Health check (if declared)
   -> Smoke test (if declared)
   -> Latency baseline check (if declared)

6. Write deploy receipt:
   -> IF verification passes: PASS
   -> IF verification fails: trigger rollback prompt (human confirms)

7. Notify Instinct of deployment event (pattern signal)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — post-package, post-Attestation for production |
| `rules/environment-policy.md` | Rules | Environment declaration required, promotion gate required |
| `rules/rollback-policy.md` | Rules | Rollback plan required before deploy |
| `rules/attestation-policy.md` | Rules | Production deploy requires Attestation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Package | Deploy receives signed artifact from Package |
| Archive | Archive completes before Deploy triggers (receipts must be present) |
| Verifier | Verifier passes all gates before Deploy activates |
| Autopilot | Autopilot gates Deploy activation within lifecycle |
| Instinct | Deploy notifies Instinct on completion (deployment event for pattern tracking) |
| Security gateway | Deploy reads security controls for production hardening checklist |

---

## Verification Mode

**Demonstration** — artifact deployed to declared environment, post-deploy health check passes, rollback plan written to receipt, Attestation received for production.

---

## Receipt Extension Fields

```json
{
  "environment": "string",
  "artifact_version": "string",
  "rollback_to": "string",
  "attestation_received": "boolean",
  "health_check_passed": "boolean",
  "smoke_test_passed": "boolean",
  "deployment_id": "string"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Automatic rollback trigger | Detection automatic, execution human-confirmed (current) vs. fully manual | Implementation |
| Blue-green vs. rolling | Platform-specific default vs. declared in spec always | P10 platform refinement |
| Multi-environment promotion chain | Two-stage (staging→prod) vs. configurable chain | Per-project |
