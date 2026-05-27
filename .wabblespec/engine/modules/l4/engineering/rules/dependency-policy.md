# Gateway Engineering — Dependency Policy

Rules enforced by gateway-engineering Phase B verdict. Applies to any target with external dependencies (libraries, runtimes, frameworks). Violations produce FLAG or BLOCK verdicts.

---

## Rule D1: Dependency Freshness

**Requirement:** Every project declares a dependency freshness policy in the spec or AGENT.md. Stale major versions are tracked as risk, not ignored.

| Staleness class | Definition | Action |
|---|---|---|
| Current | Within 1 major version of latest stable | Permitted |
| One major behind | N-1 of latest stable | FLAG — document reason and upgrade timeline |
| Two+ majors behind | N-2 or older | BLOCK — must justify with written risk acceptance or schedule upgrade |

**Measurement:** Gateway Phase B runs `npm outdated` / `pip list --outdated` / `cargo outdated` (or project equivalent) and classifies each dependency.

**Failure modes:**
- No freshness check in CI = FLAG
- Dependencies two or more major versions behind with no documented justification = BLOCK
- Package manager lock file absent (no pinning) = BLOCK

---

## Rule D2: EOL Runtime and Framework Detection

**Requirement:** No production target may declare a dependency on a runtime or framework that has reached end-of-life (EOL).

**EOL definition:** Official security support has ended. Sources: endoflife.date, vendor EOL pages.

| EOL status | Action |
|---|---|
| Active LTS or maintained | Permitted |
| Security-fixes-only (maintenance mode) | FLAG with upgrade timeline required |
| EOL (no security fixes) | BLOCK |

**Common EOL signals:**
- Node.js: not in the LTS schedule at nodejs.org/en/about/previous-releases
- Python: past end-of-security-fixes at devguide.python.org/versions/
- Ruby: not listed at www.ruby-lang.org/en/downloads/branches/
- Java: not on active LTS from OpenJDK or vendor

**Failure modes:**
- Production target running EOL runtime = BLOCK
- EOL framework version pinned in lockfile = BLOCK
- No automated EOL detection (e.g., Dependabot, Renovate, or equivalent) = FLAG

---

## Rule D3: Vulnerability Audit Gate

**Requirement:** Dependency vulnerability scanning runs in CI and gates merge.

| Severity | Action |
|---|---|
| CRITICAL | BLOCK — must resolve before merge |
| HIGH | BLOCK — must resolve or document accepted risk before merge |
| MEDIUM | FLAG — must appear in changelog or PR description |
| LOW/INFO | Log only — no gate |

**Acceptable resolutions for HIGH/CRITICAL:**
1. Update to patched version
2. Replace dependency with unaffected alternative
3. Written risk acceptance signed by a human reviewer (if no patch available) — must include: CVE ID, affected paths, mitigating controls, and review date

**Failure modes:**
- No vulnerability audit in CI = BLOCK
- CRITICAL vulnerability with no resolution and no risk acceptance = BLOCK
- Audit configured to warn-only on HIGH/CRITICAL = BLOCK (must be error-level)

---

## Rule D4: Dependency License Compliance

**Requirement:** Every dependency license is verified against the project license before merge. SBOM (Software Bill of Materials) is required for production targets.

| Situation | Action |
|---|---|
| Compatible OSS license (MIT, Apache 2.0, BSD, ISC) | Permitted |
| Copyleft license (GPL, AGPL) in a closed-source project | BLOCK — incompatible by default; requires legal sign-off |
| Unknown / unlicensed dependency | BLOCK — cannot ship unknown license terms |
| Commercial license dependency | FLAG — must be declared in spec with cost and terms |

**SBOM requirement:** A machine-readable SBOM (CycloneDX or SPDX format) must be generated as a CI artifact for any production release.

**Failure modes:**
- No license check in CI = FLAG
- GPL/AGPL dependency in closed-source project without legal sign-off = BLOCK
- SBOM absent from release artifacts = FLAG

---

## Rule D5: Dependency Minimization

**Requirement:** Dependencies added to a project must be justified. Every new dependency in a PR must include a rationale comment or PR description entry: what it provides, why an existing dependency or standard library approach was insufficient.

| Criterion | Requirement |
|---|---|
| New runtime dependency (shipped to production) | Justification required in PR |
| New dev dependency (build, test, lint only) | No justification required |
| Dependency that adds > 100KB to bundle size | Bundle size impact declared in PR |
| Transitive dependency count > 50 added by new dep | FLAG — review transitive tree before merge |

**Failure modes:**
- No rationale for new production dependency = FLAG
- Bundle size impact undeclared for large dependencies = FLAG (Web target only — enforced by performance budget check)
