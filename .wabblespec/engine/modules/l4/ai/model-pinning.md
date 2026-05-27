# Model Governance — Pinning and Versioning

## Version Pinning

Model version pinned in all environments — no `latest` alias in production. Pinned version format: provider-specific model ID.

Examples: `claude-sonnet-4-6`, `gpt-4o-2024-08-06`

## Version Bump Process

Before promoting to a new model version:

1. Eval suite runs against new model version
2. All declared dimensions must pass thresholds
3. Red-team pass on known failure cases
4. Staged rollout: staging first, production after validation
5. Rollback plan declared before promotion begins

## Fallback Model

Declared for each model use: what model is used if primary is unavailable?

- Fallback model must pass eval suite at baseline threshold
- No fallback = model unavailability is a declared outage (acceptable if explicitly stated)

## Audit Gates

- [ ] Model version pinned in all environments (no `latest` alias in production)
- [ ] Fallback model declared or outage accepted explicitly
- [ ] Fallback model passes eval suite at baseline threshold
- [ ] Version bump process followed: eval → red-team → staging → production
- [ ] Rollback plan declared before any version promotion begins
