# Task Card

**goal:** Two GitHub Actions workflow files and a ruff.toml are committed to main, with all script paths, flags, and dependency references verified correct.
**target:** Library-Package
**complexity:** Low
**change_class:** ADDITIVE
**locked_at:** 2026-05-28T14:00:00Z
**session_id:** real-exec-validation-20260528

## Non-Goals

- Editing Python scripts to resolve lint violations
- Adding additional workflows (test runner, release, deploy)
- Configuring GitHub repo settings or branch protection rules
- Validating workflows execute against a live GitHub remote

## Assumptions

- A GitHub remote will be added before workflows are exercised
- Python 3.11 covers all script syntax in use
- ruff select E,F with ignore E501 is the right starting bar — long docstring lines exist up to 280 chars
- requirements.txt PyYAML dep covers both quality-floor-check.py and validate-module-registry.py
- No existing ruff.toml or pyproject.toml — confirmed by directory scan

## Acceptance Criteria

### AC1 — lint.yml verified

Given lint.yml exists at .github/workflows/lint.yml
When the file is reviewed against actual repo paths
Then all referenced script directories exist in the repo and the workflow YAML is syntactically valid

### AC2 — quality-floor.yml verified

Given quality-floor.yml exists at .github/workflows/quality-floor.yml
When the file is reviewed against actual script paths and flags
Then quality-floor-check.py --verbose and validate-module-registry.py --undeclared are the correct invocations and PyYAML is in the dep list

### AC3 — ruff.toml created

Given no ruff.toml exists in the repo root
When ruff.toml is written to the repo root
Then the file declares select = ["E", "F"] and ignore = ["E501"] and ruff check runs without error on the shared scripts directory

### AC4 — three files committed

Given lint.yml, quality-floor.yml, and ruff.toml are verified and correct
When git commit is run
Then all three files appear in the HEAD commit on main with no unstaged changes remaining
