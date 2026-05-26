# Dependency Policy Reference

**Enforced by:** l4/engineering gateway (Phase B, dependency-standards.md)  
**Consumed by:** l2/executor (dep upgrade waves), l2/reviewer (dep violation review), l7/deploy (production gate)  
**Purpose:** Decision tree and upgrade workflow for dependency violations flagged by the Engineering gateway. The standards (N-2 rule, EOL detection, lock file policy) live in `modules/l4/engineering/dependency-standards.md`. This reference covers what to do when a violation is found.

---

## Violation classes and severity

| Violation | Gateway result | Action required |
|---|---|---|
| Direct dep > 2 major versions behind (N-2) | FLAG | Schedule upgrade; must resolve before next production deploy |
| Runtime on EOL version | BLOCK | Upgrade before any production deploy — no exceptions |
| Lock file missing or out of sync | BLOCK | Commit lock file or re-run install to sync |
| Unused direct dependency detected | FLAG | Remove in current wave or open ticket |
| Known CVE in direct dependency | BLOCK | Patch immediately; do not deploy until resolved |
| Known CVE in transitive dependency | FLAG | Upgrade parent dep; document if no upstream fix available |
| Private registry fallback enabled | BLOCK | Remove fallback — dependency confusion attack surface |

**BLOCK vs. FLAG:** BLOCK stops the Executor wave. FLAG allows the wave to continue but the finding must be resolved before the delivery receipt can be issued for a production deploy.

---

## Upgrade decision tree

When the Engineering gateway flags a dependency violation:

```
Is the violation a BLOCK (EOL runtime, CVE, lock file, private registry)?
  YES → Stop current wave. Resolve before proceeding.
        EOL runtime: see "Runtime upgrade workflow" below.
        CVE: see "Security patch workflow" below.
        Lock file: run install, commit lock file, resubmit wave.
        Private registry: remove fallback config from .npmrc / pip.conf.
  NO (FLAG — N-2 or unused dep) →
    Is the current task a production deploy?
      YES → Must resolve before delivery receipt issued.
      NO →
        Is N-2 violation on a dep with a known CVE?
          YES → Treat as BLOCK — patch immediately.
          NO →
            Does the upgrade require more than one major version jump?
              YES → Stage the upgrade: see "Staged upgrade workflow" below.
              NO → Upgrade in the current wave or next sprint sprint. Open ticket.
```

---

## Upgrade workflows

### Standard single-major-version upgrade

For direct dependencies 1 major version behind with no CVE.

1. Read the upstream CHANGELOG for the target version. Identify all BREAKING CHANGES.
2. Write a migration plan: list files that import the dep, list API calls that changed.
3. Open a dedicated upgrade wave (not bundled with feature work — Commit module enforces this).
4. Update the dependency in the manifest to the new major version.
5. Run the test suite. Address all failures from breaking changes.
6. Run lint and type check.
7. Update lock file.
8. Run `npm outdated` / `pip list --outdated` / equivalent to confirm no remaining violations.
9. Write the commit body explaining WHY the upgrade happened (security, unblock feature, EOL avoidance) — not just WHAT changed.
10. Reference the upstream CHANGELOG entry in the commit body.

### Staged upgrade workflow (multiple major versions behind)

For direct dependencies 2+ major versions behind (N-2 BLOCK territory) with no active CVE.

**Rule:** Never jump more than one major version at a time. Each jump is a separate commit.

1. Identify all major version milestones between current and target (e.g. v2 → v3 → v4).
2. For each milestone:
   a. Read CHANGELOG for that version.
   b. Upgrade to that major version only.
   c. Run full test suite — fix all breaking changes.
   d. Commit with descriptive body (see step 9 above).
3. After all milestones: verify no remaining N-2 violations.
4. Total waves required: one per major version jump. Do not compress into one wave — history is lost.

**Exception:** If the dep has not been modified since the last jump and the intermediate version was never used in production, the intermediate step may be skipped with a documented rationale in the commit body.

### Security patch workflow (CVE in direct dependency)

1. Identify the patched version from the CVE advisory (NVD / GitHub Advisory / vendor).
2. If a patch exists in the same major version: upgrade to the patched minor/patch version immediately.
3. If the patch requires a major version bump: follow the standard upgrade workflow; mark the wave as `SECURITY` in the task card.
4. If no upstream patch exists: evaluate mitigations (input validation, disabling the vulnerable feature, vendoring a patched fork). Document in the task card.
5. **Do not deploy to production with an unpatched known CVE.** The Deploy gateway blocks this.
6. After upgrade: run `npm audit` / `pip-audit` / `cargo audit` to confirm zero high/critical CVEs.

### Runtime EOL upgrade

1. Check `endoflife.date/{runtime}` for the next supported LTS/stable version.
2. For Node: upgrade to the next LTS (not the latest — latest may not be LTS yet).
3. Update runtime declaration files: `.nvmrc`, `.node-version`, `pyproject.toml requires-python`, `go.mod go directive`.
4. Update Dockerfile `FROM` line and CI runner version in parallel.
5. Run full test suite on the new runtime.
6. Update build-toolchain.md to reflect the new runtime version.
7. **Do not run a parallel deployment** on EOL and non-EOL runtime simultaneously — pick a cutover date and execute it.

---

## Adding a new dependency

Before running `npm install` / `pip install` / `cargo add`, answer all four questions from dependency-standards.md:

1. Is this in the standard library? (If yes: use stdlib.)
2. Is it actively maintained? (Last commit < 12 months.)
3. Does it have a clean CVE history? (`npm audit` / `pip-audit` / `cargo audit` after install.)
4. What is the transitive dep cost? (`npm ls {package}` / `pipdeptree` / `cargo tree`)

If adding anyway: document the decision in the commit body with answers to all four questions.

---

## Dep upgrade in the CI pipeline

The Engineering gateway Phase B reads the output of these commands. Ensure they are in CI:

```bash
# Node
npm outdated --json          # dep freshness check
npm audit --audit-level=high # CVE check
npx depcheck                 # unused dep check
npm ci                       # lock file sync check (fails on mismatch)

# Python
pip list --outdated          # dep freshness
pip-audit                    # CVE check
go mod tidy && git diff --exit-code go.sum  # lock file sync

# Go
go list -u -m all            # dep freshness
govulncheck ./...            # CVE check
go mod verify                # integrity check

# Rust
cargo outdated               # dep freshness
cargo audit                  # CVE check
cargo verify-project         # manifest integrity
```

---

## Dependency policy and the L8 gate

The Instinct layer (post-L8 gate) will detect patterns in receipts. Common dependency-related patterns it may surface:

- Repeated N-2 violations on the same dependency across multiple receipts → systemic upgrade deferral
- CVE patches always arriving as hotfixes rather than in scheduled upgrades → reactive-only dependency posture
- Lock file out-of-sync findings → CI is not enforcing lock file freshness

These patterns, if detected by Instinct, become candidates for human-validated improvements to the dependency workflow.

---

## Cross-references

- `modules/l4/engineering/dependency-standards.md` — measurement commands, EOL sources, lock file rules
- `_shared/references/version-policy.md` — semantic versioning and BREAKING CHANGE classification
- `modules/l4/security/SKILL.md` — secrets-in-git check (S1–S8); not a dep concern but often co-found
- `modules/l7/commit/SKILL.md` — commit body requirements for upgrade commits (WHY not WHAT)
- `modules/l7/deploy/SKILL.md` — Deploy blocks on unpatched CVE
