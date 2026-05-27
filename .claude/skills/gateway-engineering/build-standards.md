# Engineering Gateway — Universal Build Standards

These standards apply to all targets regardless of platform. Platform engineering modules handle platform-specific toolchains. These standards are the universal floor.

---

## CI Pipeline Requirements

Every project must have a CI pipeline that runs automatically on every push to a non-draft PR branch. The pipeline must include, in order:

1. **Type check / lint** — zero errors required. Not warnings-as-errors — actual zero errors.
2. **Unit tests** — must pass. Flaky tests must be fixed or explicitly quarantined (not silently skipped).
3. **Integration tests** — must pass. If slow, run on merge queue, not every push.
4. **Security audit** — dependency audit (`npm audit`, `pip-audit`, `cargo audit`). Block on high/critical.
5. **Build artifact** — produce the deployable artifact (binary, container image, bundle).
6. **Smoke test** — run the built artifact and verify it starts. Not a test harness — the real artifact.

**CI must be blocking.** PRs cannot be merged if CI fails. No "merge anyway" override without explicit team approval.

---

## Branch and Merge Strategy

**Main branch protection (required for all projects approaching production):**
- Direct push to main/master: disabled
- PR required for all changes
- CI must pass before merge
- At least one approval required (see code-quality.md for review standards)

**Branch naming convention:** `<type>/<short-description>` — e.g., `feat/user-auth`, `fix/token-expiry`, `chore/bump-deps`

**Commit message convention:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`). Used for automated changelog generation.

---

## Versioning Convention

**Standard:** Semantic Versioning (semver) — `MAJOR.MINOR.PATCH`.

| Increment | When |
|---|---|
| PATCH | Backward-compatible bug fix |
| MINOR | Backward-compatible new feature |
| MAJOR | Breaking change |

**Version source of truth:** One place only — `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod`. Never hardcoded in application code.

**Tagging:** Git tag on every release: `v<semver>`. Tag must match the version in the version file.

---

## Changelog Convention

**Format:** Keep a Changelog (`CHANGELOG.md`) at repo root.

**Required sections per release:** `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

**Automation:** If using Conventional Commits, changelog is auto-generated from commit messages. Commit type mapping:
- `feat:` → Added
- `fix:` → Fixed
- `chore:` → omitted (not user-facing)
- `security:` → Security

**Security entries:** Any security fix must appear in the `Security` section with: CVE ID (if applicable), affected versions, and mitigation advice.

---

## README Requirements

Every project must have a `README.md` at repo root containing:

1. **What it does** — one paragraph, not marketing copy
2. **How to run locally** — exact commands from clone to running, no assumed knowledge
3. **How to run tests** — exact commands
4. **How to build** — exact commands producing the release artifact
5. **Configuration** — all env vars listed (name, type, required/optional, description)
6. **License** — declared

**README must be accurate.** A README where "how to run locally" fails on a clean clone is a gate failure.

---

## Environment Reproducibility

**Local setup must work on a clean machine** with only the declared prerequisites installed. Test by following README from scratch (or delegate to a team member who has not touched the project).

**Prerequisites must be declared** in README: runtime version (e.g., `Node 20+`, `Python 3.11+`, `Go 1.22+`), required system tools, required credentials/secrets (without values — just names and where to get them).

**Docker Compose for local dependencies:** If the project requires a database, cache, or other service, provide a `docker-compose.yml` that starts all dependencies for local development. `docker compose up -d && <app-start-command>` must work.

---

## Release Artifact Standards

**Every release artifact must be:**
- **Reproducible:** Building from the same git tag produces the same artifact
- **Versioned:** Artifact carries the semver version (binary `--version`, container tag, package version)
- **Minimal:** No development dependencies, test fixtures, or secrets bundled in production artifact
- **Auditable:** The git SHA that produced the artifact is traceable (build metadata, container label, or release notes)

**Container labels (if containerized):**
```dockerfile
LABEL org.opencontainers.image.version="1.2.3"
LABEL org.opencontainers.image.revision="<git-sha>"
LABEL org.opencontainers.image.created="<build-timestamp>"
```
