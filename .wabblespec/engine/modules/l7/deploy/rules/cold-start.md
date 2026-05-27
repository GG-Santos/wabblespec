# Cold-Start Behavior — Deploy

Defines what Deploy does when its upstream build artifacts or deployment configuration are absent.

## Absent: build artifact / CI pass

Condition: Deploy invoked but no successful build artifact or CI PASS receipt.
Detection: No build output in expected artifact location; or CI status is not PASS.
Action: BLOCK Deploy. Surface: "Deploy requires a passing build. No build artifact or CI PASS found."
Do NOT: Deploy unbuilt or untested code.

## Absent: deployment configuration

Condition: No deployment configuration file (`deploy.yaml`, `Dockerfile`, `appspec.yml`, etc.) found.
Detection: Expected config file absent.
Action: Surface: "No deployment configuration found. Declare: target environment, deployment strategy (rolling/blue-green/canary), and infrastructure."
Do NOT: Infer deployment strategy without declaration.

## Absent: environment declaration

Condition: Deploy invoked without specifying target environment.
Action: Surface: "Which environment? (staging / production / preview)"
Do NOT: Default to production. Production deployment requires explicit declaration.

## Absent: rollback plan

Condition: Deploy to production but no rollback procedure declared in spec or infrastructure config.
Detection: Production target detected, no rollback entry in spec.
Action: FLAG (not BLOCK): "Production deploy without declared rollback plan. Declare rollback procedure in spec before deploying."

## Default state on cold start

| Field | Default |
|---|---|
| `target_environment` | Not declared — must be specified |
| `strategy` | Not declared — must be specified (rolling / blue-green / canary / recreate) |
| `health_check` | Required — deploy blocked until health check passes |
| `rollback_trigger` | Error rate > 1% or health check failure |
| `production_gate` | Explicit declaration required — no implicit production deploys |
