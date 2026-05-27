# CI/CD Engineering Standards

Loaded by Apply when gateway-engineering is active. Covers pipeline design, deployment strategies, and quality gates.

## CI pipeline requirements

Every project must declare a CI pipeline. Spec must include:
- **Trigger**: on push, on PR, on merge to main, on tag
- **Test gate**: which tests run in CI; what failure means (block merge vs warn)
- **Build gate**: build must succeed in CI before deploy
- **Security gate**: dependency audit, SAST, secret scanning run in CI

### Minimum required CI steps

```yaml
# Example structure (GitHub Actions / GitLab CI / etc.)
stages:
  - lint:       # formatting, type check, style
  - test:       # unit + integration tests
  - build:      # compile, package
  - security:   # audit, SAST, secret scan
  - deploy:     # if previous stages pass

# Each stage: runs in parallel where possible; fails fast on error
```

### Fail conditions — declare in spec

| Condition | CI behavior |
|---|---|
| Test failure | Block merge; require fix |
| Build failure | Block merge; require fix |
| Secret detected | Block merge; require remediation |
| High severity CVE | Block merge (configurable to warn-only in brownfield) |
| Coverage drop | Warn only (unless declared as gate) |

## Secret management in CI

Rules:
- Secrets in CI via environment secrets / secrets manager — never in code or YAML files
- OIDC (OpenID Connect) for cloud provider auth: eliminates long-lived credentials
  ```yaml
  # GitHub Actions → AWS OIDC
  permissions:
    id-token: write
  steps:
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::123456789:role/github-actions-role
        aws-region: us-east-1
  ```
- Rotate secrets regularly — declare rotation period in spec
- Least-privilege: CI credentials scoped to minimum required actions

## Deployment strategies

Spec must declare the deployment strategy per environment:

| Strategy | How | When |
|---|---|---|
| Rolling | Replace instances one at a time | Default; low risk; works without load balancer |
| Blue-green | Provision new stack; switch traffic | Zero downtime; instant rollback; double infra cost |
| Canary | Route % of traffic to new version | Progressive risk; requires traffic splitting infra |
| Feature flags | Deploy code; enable via flag | Decouple deploy from release; requires flag system |
| Recreate | Stop all, deploy new, start | Simple; has downtime; only for non-HA workloads |

### Approval gates

Spec must declare: which environments require manual approval before deploy.

Recommended:
- dev: automatic deploy on merge
- staging: automatic deploy on merge
- production: manual approval gate before deploy

## Rollback policy

Spec must declare:
- **Trigger**: what constitutes a rollback event (error rate spike, p99 latency threshold, manual trigger)
- **Mechanism**: redeploy previous version, traffic switch (blue-green), feature flag disable
- **Time to rollback**: target time from decision to traffic restored
- **Data**: if migration ran, is rollback safe? (forward-only migrations are the standard answer — plan accordingly)

## Caching in CI

Cache expensive operations to reduce build time:
```yaml
# Node dependencies
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# Docker layers
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

Spec must declare: cache keys and invalidation strategy for each cached item.

## Environment parity

Dev, staging, and production must be as similar as possible:
- Same container image (different config, not different image)
- Same database engine and version
- Same secrets manager (different secrets, same structure)
- Infrastructure as code: same IaC definitions, different variable sets

Differences that are acceptable: instance size, replica count, retention periods.
Differences that are not acceptable: different database engines, different runtimes, different OS.
