# Security Gateway — Audit Gates

Registered with Verifier at gateway activation. Supplement platform gates — do not replace them. All gates blocking before Delivery wave.

## Coverage Map

Defines what this gateway covers, what L3 platform modules cover, and what is explicitly out of scope. Review this before adding findings — a finding in the wrong layer wastes triage bandwidth.

### Covered by this gateway (L4)

| Category | Threat patterns | Gate |
|---|---|---|
| Secrets in git history | Committed API keys, tokens, passwords | Gate 1 |
| Secrets in source | Hardcoded credentials, API keys in source files | Gate 2 |
| Static analysis | SAST findings: injection, insecure patterns, OWASP Top 10 | Gate 3 |
| Weak cryptography | MD5/SHA1 hashes, ECB mode, weak key sizes | Gate 4 |
| Insecure randomness | `Math.random()` / `random.random()` in security contexts | Gate 4 |
| Dependency CVEs | Critical/High CVEs in direct and transitive dependencies | Gate 5 |
| TLS configuration | TLS 1.0/1.1, weak cipher suites | Gate 6 |
| Deserialization RCE | Pickle injection (Python), YAML deserialization, eval injection | Gate 3 (SAST) |
| Cryptographic randomness | Insecure PRNG seeding, predictable nonces | Gate 4 |
| Certificate validation bypass | Disabled cert verification, trust-all implementations | Gate 3 (SAST) |

### Covered by L3 platform modules (not duplicated here)

| Category | Platform |
|---|---|
| SQL injection | API/Service platform (Gate 7) |
| Shell injection via args | CLI platform (Gate 3) |
| Path traversal via args | CLI platform (Gate 7) |
| XSS / dangerouslySetInnerHTML | Web platform (Gate 8) |
| CSRF on state-mutating endpoints | Web platform (Gate 2) |
| Auth enforcement (401 on protected endpoints) | API/Service platform (Gate 1) |

### Explicitly excluded from this gateway

These are not reported here — either handled elsewhere or out of WabbleSpec security scope:

- **Denial of Service** — resource exhaustion, algorithmic complexity attacks. Not flagged even if exploitable from local network.
- **Rate limiting gaps** — handled by API/Service Gate 8. Not duplicated.
- **Informational / theoretical issues** — only flag when >80% confidence of actual exploitability in the target's threat model.
- **Existing pre-PR vulnerabilities** — this gateway assesses new changes, not inherited debt. Pre-existing findings go to Triage as separate debt items.

## Confidence threshold

Only report findings where confidence of actual exploitability ≥ 0.80. Theoretical issues and style-adjacent concerns do not qualify. Each finding must state: who exploits it, from where, with what impact.

## Analysis methodology

Run gates in this order to maximize signal before committing to deep analysis:

**Phase 1 — Repository context** (before any gate execution)
- Identify existing security frameworks and libraries in use
- Look for established secure coding patterns (existing sanitization, validation)
- Understand the project's declared threat model (`security/threat-model.md`)

**Phase 2 — Comparative analysis**
- Compare new code against existing secure patterns in codebase
- Flag deviations from established practices (inconsistent sanitization, new attack surfaces)

**Phase 3 — Vulnerability assessment**
- Execute gates 1–6 in order
- Trace data flow from user inputs to sensitive operations
- Identify privilege boundaries crossed unsafely
- Map each finding to a gate and a coverage category above

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
