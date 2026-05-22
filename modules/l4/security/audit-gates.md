# Security Gateway — Audit Gates

Registered with Verifier at gateway activation. Supplement platform gates — do not replace them. All gates blocking before Delivery wave.

---

## Gate 1: Git History Secret Scan

**Check:** Full git history contains no committed secrets.

**Method:**
```bash
gitleaks detect --source . --log-opts="--all" --verbose --exit-code 1
```

**Pass:** Exit code 0 — zero findings.
**Fail:** Any finding. Action: rotate the exposed secret immediately, then investigate and remediate.

**False positive handling:** Known false positives (test fixtures, example values) declared in `.gitleaks.toml`:
```toml
[[allowlist.commits]]
description = "Test fixture with fake key"
commits = ["<commit-sha>"]
```

---

## Gate 2: Source Secret Scan (Current HEAD)

**Check:** Current source tree contains no hardcoded secrets.

**Method:**
```bash
# gitleaks on working tree (not history)
gitleaks detect --source . --no-git --verbose --exit-code 1

# Supplementary: trufflehog for entropy-based detection
trufflehog filesystem . --only-verified --fail
```

**Pass:** Zero findings from both tools.
**Fail:** Any finding. Action: remove secret, rotate it (treat as compromised), add to pre-commit hook.

---

## Gate 3: SAST Scan

**Check:** Static analysis finds no new security findings (ERROR or WARNING severity).

**Method:**
```bash
semgrep --config=p/security-audit \
        --config=p/secrets \
        --config=p/owasp-top-ten \
        --error \
        --metrics=off \
        src/
```

**Pass:** Exit code 0 — zero ERROR or WARNING findings beyond established baseline.
**Fail:** Any new finding. Each finding must be triaged: fix, accept-with-justification, or mark false-positive with documented rationale.

**Baseline management:**
```bash
# Establish baseline (first run only):
semgrep --config=p/security-audit src/ --json > .semgrep-baseline.json

# Subsequent runs compare against baseline:
semgrep --config=p/security-audit src/ --baseline-commit=$(git rev-parse HEAD~1)
```

---

## Gate 4: Weak Algorithm Check

**Check:** No weak cryptographic algorithms used in source.

**Method:**
```bash
# Run patterns from vulnerability-patterns.md §Pattern 2 and §Pattern 3
# Grep commands reproduced here for standalone execution:

echo "=== Checking for weak hash algorithms ==="
grep -rn \
  -e 'hashlib\.md5\|hashlib\.sha1' \
  -e 'crypto\.createHash.*md5\|crypto\.createHash.*sha1' \
  src/ --include="*.py" --include="*.ts" --include="*.js"

echo "=== Checking for ECB cipher mode ==="
grep -rn \
  -e 'MODE_ECB\|createCipheriv.*ecb' \
  src/

echo "=== Checking for insecure randomness in security contexts ==="
grep -rn 'Math\.random()' src/ --include="*.ts" --include="*.js" \
  | grep -iE 'token|session|id|nonce|csrf|key|secret|salt|code'

grep -rn 'random\.random\(\)\|random\.randint\|random\.choice' src/ --include="*.py" \
  | grep -iE 'token|session|id|nonce|csrf|key|secret|salt|code'
```

**Pass:** Zero matches on all checks.
**Fail:** Any match. Each must be remediated before Delivery.

---

## Gate 5: Dependency Vulnerability Scan

**Check:** Zero critical or high severity vulnerabilities in dependencies.

**Method:**
```bash
# Run the appropriate command for the project's ecosystem:
npm audit --audit-level=high          # Node
pip-audit --fail-on-known             # Python
cargo audit --deny warnings           # Rust
govulncheck ./...                     # Go

# Container image (if applicable):
trivy image --exit-code 1 --severity HIGH,CRITICAL <image>:<sha>
```

**Pass:** All commands exit 0.
**Fail:** Any critical or high finding. Action: patch or document waiver with CVE ID, affected version, mitigating control, and remediation timeline.

---

## Gate 6: TLS Configuration (Network-Serving Targets Only)

**Check:** Service does not accept TLS 1.0/1.1 connections. No weak cipher suites enabled.

**Method:**
```bash
# testssl.sh against service endpoint
testssl.sh --protocols --cipher-per-proto --severity HIGH <host>:<port>

# Alternative: sslyze
sslyze --regular <host>:<port>
```

**Pass:** TLS 1.0 and 1.1 not supported. No WEAK or CRITICAL cipher findings.
**Fail:** TLS 1.0/1.1 accepted, or any WEAK/CRITICAL cipher suite enabled.

**Applies to:** API/Service targets, Web targets with server-terminated TLS. Not applicable to CLIs.

---

## Gate Summary

| Gate | Description | Applies to | Blocking |
|---|---|---|---|
| 1 | Git history secret scan (full history) | All | Yes |
| 2 | Source secret scan (current HEAD) | All | Yes |
| 3 | SAST scan (Semgrep — zero new findings) | All | Yes |
| 4 | Weak cryptographic algorithm check | All | Yes |
| 5 | Dependency vulnerability scan (zero critical/high) | All | Yes |
| 6 | TLS configuration check | API/Service, Web | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.

These gates run in addition to L3 platform gates, not instead of them.
