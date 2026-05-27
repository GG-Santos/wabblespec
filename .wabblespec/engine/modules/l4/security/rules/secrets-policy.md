# Gateway Security — Secrets Policy

Rules enforced by gateway-security Phase B verdict. Violations produce FLAG or BLOCK verdicts. These rules apply to all platforms; platform-specific controls (Keychain, Keystore, hardware secure element) are documented in the respective L3 platform `security/platform-controls.md`.

---

## Rule S1: No Secrets in Source Code

**Rule:** API keys, passwords, private keys, tokens, connection strings, and any credential must not appear in source code.

**Detection:** gateway-security Phase B checks spec for declared SAST/secret scanning configuration. CI pipeline must include Gitleaks or equivalent (see `references/continuous-security.md`).

**Patterns that trigger BLOCK:**
```
Hard-coded strings matching:
  - API key patterns: sk-*, AKIA*, xox[baprs]-*, ghp_*, glpat-*
  - Private key PEM blocks: -----BEGIN * PRIVATE KEY-----
  - Connection strings: postgres://*:*@*, mongodb+srv://*:*@*
  - Generic high-entropy strings (>32 chars) assigned to variables named *key*, *secret*, *token*, *password*, *credential*
```

**Required pattern:**
```python
# Correct: read from environment
api_key = os.environ["OPENAI_API_KEY"]

# Correct: read from secrets manager
secret = boto3.client("secretsmanager").get_secret_value(SecretId="prod/api-key")

# BLOCK: hard-coded
api_key = "sk-live-abc123xyz..."
```

**Failure modes:**
- Any credential detected in source files = BLOCK
- SAST/secret scanning not declared in spec = FLAG (gate requires it)

---

## Rule S2: No Secrets in Version-Controlled Config Files

**Rule:** `.env` files, `config.yaml`, `appsettings.json`, `secrets.yaml`, or any configuration file containing real credentials must not be committed to version control.

**Required:**
- `.env` in `.gitignore` at project root (enforced — missing = FLAG)
- `.env.example` committed instead: placeholder values only, never real credentials
- `*.pem`, `*.key`, `*.p12`, `*.pfx` in `.gitignore`
- Kubernetes secrets manifests: not committed in plaintext; use Sealed Secrets, External Secrets Operator, or equivalent

**Example `.gitignore` entries (minimum required):**
```
.env
.env.local
.env.*.local
*.pem
*.key
*.p12
secrets.yaml
*-secret.yaml
```

**Failure modes:**
- `.env` not in `.gitignore` = BLOCK
- Real credential found in any committed config file = BLOCK
- `.env.example` contains real API key (common mistake) = BLOCK

---

## Rule S3: No Secrets in Log Output

**Rule:** Credentials, tokens, API keys, passwords, and PII that functions as a credential must never appear in log output.

**Required masking patterns:**
```python
# Before logging any user-supplied or config-derived value, mask it
def mask_secret(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return value[:4] + "***" + value[-4:]

# Log safe representation
logger.info("API call authenticated", extra={"key_prefix": api_key[:8]})
# NOT: logger.info(f"Using key: {api_key}")
```

**Declare in spec:** Which fields are masked in logs. The spec must include a log masking declaration:
```yaml
log_masking:
  masked_fields:
    - api_key
    - password
    - access_token
    - refresh_token
    - credit_card_number
    - ssn
  masking_strategy: prefix_4_suffix_4  # or "full_redact"
```

**Structured logging:** If using JSON logging (required by `.wabblespec/engine/shared/dev/infrastructure/observability.md`), ensure the JSON serializer does not log masked fields by accident. Use field-level exclusion, not post-hoc string replacement.

**Failure modes:**
- No log masking declaration in spec = FLAG
- Credential field name in logging call without masking wrapper = BLOCK (caught by SAST rule)
- Error handler that logs `exception.message` without checking if message contains credential = FLAG

---

## Rule S4: No Secrets in Error Responses

**Rule:** Error messages returned to clients (HTTP responses, gRPC status details, CLI error output) must not contain credentials, internal connection strings, or anything that helps an attacker understand internal topology.

**Safe error response (RFC 7807 format):**
```json
{
  "type": "https://errors.example.com/auth/invalid-token",
  "title": "Authentication failed",
  "status": 401,
  "detail": "The provided token is invalid or expired."
}
```

**Unsafe patterns (BLOCK):**
```json
{
  "error": "Database connection failed: postgresql://admin:hunter2@db.internal:5432/prod"
}
```
```json
{
  "error": "Invalid API key: sk-live-abc123 does not match stored hash"
}
```

**Server-side logging:** The full error with internal details may be logged server-side (with secrets masked per Rule S3). The client receives only the sanitized message.

**Failure modes:**
- Connection string in error response = BLOCK
- Credential value echoed back in error response = BLOCK
- Stack trace exposed to client in production = FLAG (web/api-service: treat as BLOCK)

---

## Rule S5: Rotation Policy Declaration

**Rule:** Every secret type used by the system must have a declared rotation policy in the spec.

**Required declaration format:**
```yaml
secrets_rotation:
  - secret_type: database_password
    ttl: 90d
    rotation: manual_with_runbook
    runbook: docs/runbooks/rotate-db-password.md
  - secret_type: api_key_third_party
    ttl: 365d
    rotation: manual_on_compromise
    alert_on_expiry: true
  - secret_type: jwt_signing_key
    ttl: 30d
    rotation: automated
    mechanism: AWS Secrets Manager rotation Lambda
  - secret_type: tls_certificate
    ttl: 90d
    rotation: automated
    mechanism: cert-manager / Let's Encrypt
```

**TTL requirements by secret type (maximum; shorter is better):**

| Secret type | Maximum TTL | Notes |
|---|---|---|
| Database passwords | 90 days | Automated rotation preferred |
| JWT signing keys (symmetric) | 30 days | Key ID (kid) header enables zero-downtime rotation |
| TLS certificates | 90 days | Automated renewal (Let's Encrypt / cert-manager) |
| User-generated API keys | Declared; must have expiry option | Cannot be "never expires" without explicit user setting |
| Service account credentials | 1 hour (OIDC) or 90 days (static) | OIDC federation preferred |
| Encryption keys (at-rest data) | Annual + on-compromise | Key versioning required for re-encryption |

**Failure modes:**
- No rotation policy section in spec = FLAG
- Secret type declared as "rotation: never" without risk acceptance = FLAG
- No runbook reference for manual rotation secrets = FLAG

---

## Rule S6: Production Secrets via Secrets Manager

**Rule:** In production environments, secrets must be injected via a secrets management system. Environment variables set manually (e.g., in container definitions or server configuration) are insufficient.

**Approved secrets management systems:**

| Platform | Approved systems |
|---|---|
| AWS | AWS Secrets Manager, AWS Parameter Store (SecureString) |
| GCP | GCP Secret Manager |
| Azure | Azure Key Vault |
| Kubernetes | External Secrets Operator + any of above; Sealed Secrets |
| HashiCorp | Vault with AppRole or Kubernetes auth |
| Self-hosted | Vault (open source) |

**Pattern: fetch at startup, not at build time:**
```python
# At container/process startup — not baked into image
secret = secretsmanager.get_secret_value(SecretId=os.environ["SECRET_ARN"])
db_password = json.loads(secret["SecretString"])["password"]
```

**What is not acceptable in production:**
- Secrets in Dockerfile ENV instructions (baked into image layers)
- Secrets in Kubernetes deployment manifest env values (committed to git)
- Secrets in CI/CD pipeline environment variables that are manually entered and never rotated

**Declare in spec:**
```yaml
secrets_management:
  system: AWS Secrets Manager
  secret_arns:
    - arn:aws:secretsmanager:us-east-1:123456789:secret:prod/db-password
    - arn:aws:secretsmanager:us-east-1:123456789:secret:prod/api-keys
  injection_method: fetch_at_startup
```

**Failure modes:**
- Production spec with no secrets management declaration = FLAG
- Secrets baked into container image = BLOCK
- Manually-entered env vars as the declared production mechanism (no rotation, no audit trail) = FLAG

---

## Rule S7: CI/CD Secret Hygiene

**Rule:** CI/CD pipelines must not use long-lived static credentials for cloud provider access.

**Required:**
- Cloud provider authentication via OIDC federation (GitHub Actions → AWS/GCP/Azure OIDC)
- No AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY in CI secrets (except for legacy services with documented migration timeline)
- CI secrets (non-cloud): stored in CI platform secret store (GitHub Actions secrets, GitLab CI variables marked protected+masked), not in `.env` files or repository files
- Principle of least privilege: CI role has only permissions needed for deploy pipeline

**OIDC federation example (GitHub Actions → AWS):**
```yaml
permissions:
  id-token: write
  contents: read

- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-deploy
    aws-region: us-east-1
    # No access key or secret key — OIDC handles it
```

**Failure modes:**
- Long-lived AWS/GCP/Azure keys in CI secrets without migration plan = FLAG
- Secrets in repository files (even if in `.gitignore`) used by CI = BLOCK
- CI role with admin/wildcard permissions = FLAG

---

## Rule S8: Secret Scanning in CI

**Rule:** Every repository must have secret scanning configured as a blocking CI gate.

**Minimum requirement:** Gitleaks pre-commit hook + Gitleaks CI step (or GitHub secret scanning alerts set to block PRs). See `references/continuous-security.md` for configuration.

**Pre-commit hook:**
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**CI step (blocks PR merge on detection):**
```yaml
- name: Secret scan
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Custom patterns:** Declare any project-specific secret patterns that Gitleaks default rules do not cover:
```toml
# .gitleaks.toml
[[rules]]
id = "internal-api-key"
description = "Internal API key pattern"
regex = '''int-key-[A-Za-z0-9]{32}'''
```

**Failure modes:**
- No secret scanning declared in spec = FLAG
- Secret scanning configured but not blocking (advisory only) in CI = FLAG
- Pre-commit hook not in repository = informational (enforced at CI level)
