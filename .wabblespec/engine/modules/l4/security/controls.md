# Security Gateway — Cross-Cutting Controls

These controls supplement L3 platform controls. Apply regardless of platform type.

---

## Control 1: Pre-Commit Secret Scanning

**Rule:** A pre-commit hook must block any commit containing a credential pattern before it reaches the remote.

**Implementation:**
```bash
# Install gitleaks as pre-commit hook
# Option A: gitleaks native hook
gitleaks protect --staged --verbose

# Option B: via pre-commit framework (.pre-commit-config.yaml)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**Required for:** All repos. No exceptions. The cost of a committed secret far exceeds the cost of a pre-commit hook.

**What to do if a secret is found in history:**
1. Rotate the secret immediately — treat as compromised
2. Use `git filter-repo` to rewrite history (if repo is not public) or accept history is permanent
3. Force-push rewritten history with team notification
4. Document the incident in SECURITY.md

---

## Control 2: SAST in CI

**Rule:** A static analysis security test runs on every PR. Pipeline fails on any new ERROR or WARNING finding.

**Tool selection (in order of preference):**

| Language | Preferred SAST | Alternative |
|---|---|---|
| TypeScript/JavaScript | Semgrep (`p/security-audit`, `p/secrets`) | ESLint security plugin |
| Python | Semgrep + Bandit | Pylint security rules |
| Go | Semgrep + gosec | staticcheck |
| Rust | cargo-audit + Semgrep | — |
| Any | Semgrep (language-agnostic rules) | CodeQL (GitHub Actions) |

**CI integration:**
```yaml
- name: SAST scan
  run: |
    semgrep --config=p/security-audit \
            --config=p/secrets \
            --config=p/owasp-top-ten \
            --error \
            --metrics=off \
            src/
```

**Baseline management:** First run creates a `.semgrep-baseline.json`. Subsequent runs compare against baseline — only new findings block the build. Existing findings tracked in backlog with resolution timeline.

---

## Control 3: Full History Secret Scan (Release Gate)

**Rule:** Before any public release or production deployment, a full git history scan must pass with zero findings.

**This differs from Control 1 (pre-commit):** Pre-commit catches new additions. This control catches anything that was committed before the hook was installed, or committed by a team member without the hook.

**Implementation:**
```bash
gitleaks detect --source . --log-opts="--all" --verbose
# Must exit 0 (zero findings) before release artifact is published
```

**Frequency:** On every release candidate. Not on every commit (too slow for history scan).

**Waiver:** If a historical finding is a known false positive (e.g., a test fixture with a fake credential): document the finding's commit hash and rationale in `.gitleaks-ignore.json`. Do not suppress globally.

---

## Control 4: Cryptographic Algorithm Review

**Rule:** Any use of cryptographic primitives must use approved algorithms (see vulnerability-patterns.md). Code review checklist item.

**Review checklist for crypto code:**
- [ ] Hash algorithm: SHA-256+ or bcrypt/Argon2 for passwords — not MD5/SHA-1
- [ ] Cipher mode: GCM or CBC with random IV — not ECB
- [ ] Key size: AES-256, RSA-2048+, ECDSA P-256+
- [ ] IV/nonce: random per operation — not hardcoded
- [ ] Randomness source: CSPRNG — not PRNG
- [ ] Certificate verification: enabled — not skipped

**Code review requirement:** Any PR touching cryptographic code requires a reviewer who can verify the checklist above. Flagged in PR with label `crypto`.

---

## Control 5: Dependency Vulnerability Gate (Release)

**Rule:** Zero critical or high dependency vulnerabilities in any release artifact.

**Enforcement:**
```bash
# Application dependencies
npm audit --audit-level=high       # Node
pip-audit --fail-on-known          # Python
cargo audit --deny warnings        # Rust
govulncheck ./...                  # Go

# Container image (if containerized)
trivy image --exit-code 1 --severity HIGH,CRITICAL <image>:<sha>
```

**This control differs from platform dependency audits:** Platform modules run audit at build time. This control enforces audit as a release gate — the final check before an artifact is marked releasable.

**Finding response times:**
- CRITICAL: patch within 7 days, or document no fix exists + mitigating control
- HIGH: patch within 30 days
- MEDIUM: patch in next scheduled maintenance window
- LOW: track, no deadline

---

## Control 6: Secrets Never in Environment Inspection

**Rule:** Running process must not expose secrets via environment inspection APIs or debug endpoints.

**Banned patterns:**
```bash
# Express debug endpoint that dumps env
app.get('/debug/env', (req, res) => res.json(process.env))

# Python debug mode that exposes Werkzeug debugger
app.run(debug=True)  # Werkzeug debugger allows arbitrary code execution

# Django DEBUG=True in production (exposes settings, SQL queries in error pages)
```

**Verification:** For web/API targets — verify no endpoint returns `process.env`, `os.environ`, or equivalent. Verify DEBUG/development mode is disabled in production config.

---

## Control 7: Security Incident Response Declared

**Rule:** Before production deployment, the project must have a declared security contact and incident response path.

**Minimum required:**
- `SECURITY.md` at repo root: how to report a vulnerability (email or private disclosure channel)
- Team knows who owns security response
- Known-CVE disclosure process: if a CVE is found in the project's dependencies, who is notified and by when

**SECURITY.md minimum content:**
```markdown
## Reporting Security Vulnerabilities

Do not open a public GitHub issue for security vulnerabilities.

Email: security@<org>.com (or use GitHub private security advisory)

We will respond within 48 hours and aim to patch within 7 days for critical issues.
```
