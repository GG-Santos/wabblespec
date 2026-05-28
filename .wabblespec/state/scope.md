# Session Scope

**target:** Library-Package
**complexity:** Low
**locked_at:** 2026-05-28T14:00:00Z
**session_id:** real-exec-validation-20260528

## In Scope

- Verify lint.yml — ruff invocation paths and trigger paths
- Add ruff.toml with select E,F to prevent style-only CI failures
- Verify quality-floor.yml — script paths, flags, and dep list
- Fix any issues found in either workflow file
- Commit .github/workflows/lint.yml, quality-floor.yml, and ruff.toml

## Out of Scope

- Editing Python scripts to resolve lint violations
- Adding additional workflows (test runner, release, deploy)
- Configuring GitHub repo settings or branch protection rules
- Validating workflows execute against a live GitHub remote

## Assumptions

- A GitHub remote will be added before workflows are exercised
- Python 3.11 covers all script syntax in use
- ruff --select E,F is the right starting bar — not full default ruleset
- requirements.txt PyYAML dep covers both quality-floor-check.py and validate-module-registry.py
- No existing ruff.toml or pyproject.toml — confirmed by directory scan

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
