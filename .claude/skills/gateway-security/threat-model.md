# Security Gateway — Cross-Cutting Threat Model

These threats are not covered by any L3 platform module. They apply regardless of target type.

---

## Threat 1: Secrets in Git History

**Description:** Credentials, API keys, or connection strings committed to git, then removed in a later commit. The secret remains accessible in git history to anyone with repo access — or publicly if the repo is public.

**Why platform modules miss this:** Platform security modules check running code. Git history is not code — it requires a separate scan.

**Attack scenario:**
```
# Developer commits .env with real API key
git commit -m "add config"
# Realizes mistake, removes .env
git commit -m "remove .env"
# Key is still in git history:
git log --all --full-history -- .env
git show <commit-hash>:.env
```

**Mitigations:**
- Pre-commit hook: `git-secrets` or `gitleaks` — blocks commits containing secret patterns
- Repo scan: `gitleaks detect --source . --log-opts="--all"` covers full history
- If secret found in history: rotate the secret immediately, then optionally rewrite history
- `.gitignore` for `.env`, `*.pem`, `*_rsa`, `*.key` — present at repo initialization, not added later

**Verification gate:** Gate 1 — `gitleaks` scan of full git history, zero findings.

---

## Threat 2: Hardcoded Secrets in Source

**Description:** API keys, tokens, or passwords embedded directly in source code (not in git history — in current HEAD).

**Attack scenarios:**
```python
API_KEY = "sk-live-abc123xyz"          # hardcoded in source
db = psycopg2.connect("postgresql://admin:password@localhost/prod")  # connection string with creds
```

**Why platform modules miss this:** Platform modules check runtime behavior. Hardcoded secrets exist in source code and may not be exercised in tests.

**Mitigations:**
- SAST scan: Semgrep rule `generic.secrets.security.detected-generic-secret` or equivalent
- `trufflehog filesystem .` — entropy-based secret detection
- Code review checklist item: any string literal that looks like a credential
- Secret rotation if found: treat as compromised immediately

**Verification gate:** Gate 2 — SAST/trufflehog scan of current HEAD, zero secret findings.

---

## Threat 3: Weak Cryptographic Algorithms

**Description:** Use of cryptographic algorithms or configurations known to be weak or broken.

**Specific patterns:**
- MD5 or SHA-1 for password hashing (use bcrypt/Argon2/scrypt)
- MD5 for data integrity (use SHA-256+)
- ECB cipher mode (use GCM or CBC with random IV)
- RSA key size < 2048 bits
- DES or 3DES (use AES-256)
- Hardcoded IV or salt (must be random per operation)
- `Math.random()` / `random.random()` for security-sensitive values (use `crypto.randomBytes()` / `secrets.token_bytes()`)

**Why platform modules miss this:** Platform modules focus on protocol-level security (auth, transport). Cryptographic implementation choices are application-level.

**Verification gate:** Gate 3 — SAST scan for weak algorithm usage. Code review for crypto implementations.

---

## Threat 4: Insecure Randomness in Security Contexts

**Description:** Pseudo-random number generators (PRNG) used where cryptographic randomness is required — token generation, nonce generation, session ID generation, CSRF token generation.

**Attack scenario:**
```javascript
// PRNG — predictable, seeded from timestamp
const sessionId = Math.random().toString(36)

// Correct: CSPRNG
const sessionId = crypto.randomBytes(32).toString('hex')
```

**Mitigations:**
- All security-sensitive random values use CSPRNG: `crypto.randomBytes()` (Node), `secrets.token_bytes()` (Python), `crypto/rand` (Go), `rand::rngs::OsRng` (Rust)
- PRNG (`Math.random()`, `random.random()`, `rand::random()`) banned for: tokens, IDs, nonces, salts, CSRF values, password reset codes

**Verification gate:** Gate 3 (combined with crypto weakness check).

---

## Threat 5: Cross-Service Trust Failure

**Description:** Service A receives data from service B and uses it without validation, trusting that service B's data is clean. If service B is compromised, service A becomes a vector.

**Attack scenarios:**
```
# Service A trusts header set by upstream proxy
user_id = request.headers.get('X-User-Id')  # what if proxy is bypassed?

# Service A passes service B's response body directly to DB
db.insert(upstream_response['user'])  # mass assignment from untrusted upstream
```

**Mitigations:**
- Internal traffic: validate at service boundary even if traffic comes from "trusted" internal service
- Never trust `X-User-Id`, `X-Role`, `X-Forwarded-For` headers unless set by a controlled gateway
- Upstream data: validate schema before using in queries or persisting
- mTLS for service-to-service: prevents spoofed internal requests

**Verification gate:** Gate 4 — code review: all inputs from upstream services pass through schema validation before use.

---

## Threat 6: Encryption at Rest Gaps

**Description:** Sensitive data stored unencrypted — in database, in files, in object storage — where a storage-layer compromise exposes plaintext data.

**Applies when:** Target stores: passwords, PII, payment data, health records, auth tokens, private keys.

**Mitigations:**
- Passwords: never stored — only bcrypt/Argon2/scrypt hash stored
- PII fields: column-level or application-level encryption (declare which)
- Auth tokens: store hash only, not raw token
- Files containing sensitive data: encrypted at rest (S3 SSE-KMS, disk encryption declared)
- Private keys: never in database — in secrets manager (Vault, AWS Secrets Manager, etc.)

**Verification gate:** Gate 5 — data model review: no plaintext passwords, tokens, or PII in schema fields that lack encryption declaration.

---

## Threat 7: TLS Misconfiguration

**Description:** Service accepts connections with weak cipher suites, outdated TLS versions, or unverified certificates.

**Mitigations:**
- Minimum TLS version: 1.2. Preferred: 1.3.
- TLS 1.0 and 1.1: disabled
- Weak cipher suites disabled: RC4, DES, 3DES, NULL, EXPORT, ANON
- Certificate verification: never `InsecureSkipVerify=true`, never `verify=False` in production
- Certificate expiry monitoring: alert at 30 days before expiry

**Verification gate:** Gate 6 — `testssl.sh` or `sslyze` against service endpoint. Zero weak protocol or cipher findings.
