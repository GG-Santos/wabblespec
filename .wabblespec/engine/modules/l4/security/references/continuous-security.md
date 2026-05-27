# Continuous Security Reference

SAST, secret scanning, dependency audit, and pentest scoping requirements.

## SAST (Static Application Security Testing)

SAST analyzes source code without running it. Run in CI on every PR.

### Tools by language

| Language | Tool | Notes |
|---|---|---|
| JavaScript/TypeScript | ESLint (eslint-plugin-security), Semgrep | ESLint catches injection, prototype pollution |
| Python | Bandit, Semgrep | Bandit: hardcoded secrets, injection, weak crypto |
| Go | gosec, Semgrep | gosec: integer overflow, TLS config, SQL injection |
| Rust | cargo-audit, Semgrep | Rust's type system prevents many vulnerabilities |
| Java/Kotlin | SpotBugs + FindSecBugs, Semgrep | FindSecBugs: injection, deserialization |
| Multi-language | Semgrep | Rules for all languages; custom rule support |

### SAST CI gate

```yaml
# Example GitHub Actions step
- name: SAST scan
  run: |
    semgrep --config=auto --error --severity=ERROR .
```

Fail CI on: CRITICAL or HIGH findings.
Warn (do not fail) on: MEDIUM findings with a 7-day remediation window.
Track: LOW findings in issue tracker; resolve before major release.

### SAST false positive policy

SAST generates false positives. Policy:
- Review every finding before suppressing
- Suppression requires: comment explaining why it is a false positive; reviewer sign-off
- Suppression file committed to repository (`# nosec`, `// lgtm`, or equivalent)
- Suppression list reviewed quarterly

## Secret scanning

Secrets committed to version control are compromised — assume the attacker already has them.

### Prevention (pre-commit)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

Gitleaks or detect-secrets as pre-commit hook. Blocks commit before secrets reach remote.

### Detection (in CI)

Run secret scanning on every PR and on main branch:
```yaml
- name: Secret scan
  uses: gitleaks/gitleaks-action@v2
  with:
    config: .gitleaks.toml
```

Fail CI on any detected secret. No exceptions without security team approval.

### Response when secret is detected

1. Rotate the secret immediately — assume it is compromised
2. Revoke/invalidate the old secret
3. Scan git history: `git log -p | grep -i secret_pattern` to find all commits
4. Force-push to remove from history (if not yet widely cloned)
5. Notify affected systems if the secret granted access

### False positive patterns to exclude

```toml
# .gitleaks.toml
[allowlist]
  regexes = [
    "EXAMPLE_KEY",       # test fixtures with fake keys
    "placeholder_value"  # documentation examples
  ]
```

## Dependency audit

### Policy

| Severity | Action | Timeline |
|---|---|---|
| CRITICAL | Block CI immediately | Fix or mitigate within 24 hours |
| HIGH | Block CI | Fix or mitigate within 7 days |
| MEDIUM | Warn in CI | Fix within 30 days |
| LOW | Track in issue | Fix at next major dependency update |

### Commands

```bash
npm audit --audit-level=high     # fail on high+
pip-audit --severity=high        # fail on high+
cargo audit --deny=warnings      # fail on any advisory
go list -json -m all | nancy sleuth  # Go dependency audit
```

### Exceptions

Exceptions require:
- Known false positive documented with CVE analysis
- Mitigation in place (WAF rule, compensating control) documented
- Expiry date — exception must be reviewed before expiry
- Security team sign-off

## Penetration test scoping

When a penetration test is required (new major version, compliance requirement, annual schedule):

Spec must declare the test scope:

```yaml
pentest_scope:
  target:
    - production_url: https://app.example.com
    - api_url: https://api.example.com
  in_scope:
    - authentication flows
    - authorization checks (BOLA, privilege escalation)
    - input validation (all endpoints)
    - session management
    - business logic (payment, admin functions)
  out_of_scope:
    - social engineering
    - physical access
    - third-party services (Stripe, Auth0, etc.)
    - DoS attacks
  test_accounts:
    - regular user account (provided)
    - admin account (provided)
    - two separate user accounts (for BOLA testing)
  timeline:
    - engagement_start: YYYY-MM-DD
    - report_delivery: YYYY-MM-DD+7
  findings_sla:
    - critical: 24 hours to acknowledge, 7 days to fix
    - high: 7 days to acknowledge, 30 days to fix
    - medium: 30 days to acknowledge, 90 days to fix
```
