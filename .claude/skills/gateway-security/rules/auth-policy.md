# Gateway Security — Auth Policy

Rules enforced by gateway-security Phase B verdict. Any spec that declares an endpoint, API surface, or user-facing operation must satisfy all applicable rules below. Violations produce FLAG or BLOCK verdicts.

---

## Rule A1: Every Endpoint Declares Its Auth Requirement

**Requirement:** The spec (systems-design.md or technical-spec.md) must include an auth model section listing every endpoint or operation group with one of:

| Classification | Meaning |
|---|---|
| `authenticated` | Requires valid session or access token |
| `public` | No auth required; read-only acceptable |
| `admin-only` | Requires authenticated session AND admin role/scope |
| `service-to-service` | mTLS or service account token; not end-user auth |

**Failure mode:** Endpoint listed with no auth classification = BLOCK. Partial coverage (some endpoints declared, some omitted) = FLAG with list of undeclared endpoints.

**Verification:** Gateway Phase B checks that auth model section exists and all endpoints appear in it.

---

## Rule A2: Session Token Requirements

**Requirements for session cookies:**

```
Set-Cookie: session=<token>; HttpOnly; Secure; SameSite=Strict; Path=/
```

| Attribute | Required value | Rationale |
|---|---|---|
| `HttpOnly` | Must be set | Prevents XSS from reading the token via JavaScript |
| `Secure` | Must be set | Prevents transmission over HTTP |
| `SameSite` | `Strict` (preferred) or `Lax` | Prevents CSRF. `None` requires explicit justification |
| `Path` | `/` or most restrictive applicable path | Reduces exposure scope |
| Max-Age / Expires | Must be declared | No implicit "session" lifetime |

**TTL defaults (must be declared in spec; these are maximums):**

| Token type | Maximum TTL | Notes |
|---|---|---|
| Session cookie | 24 hours | Sliding window acceptable; absolute expiry required |
| Access token (JWT) | 15 minutes | Short-lived; refresh via refresh token |
| Refresh token | 30 days | Rotating (see Rule A3) |
| API key (user-generated) | Declared per product | Must have revocation mechanism |
| Service account token | 1 hour | OIDC federation preferred over long-lived tokens |

**Failure modes:**
- Session cookie without HttpOnly = BLOCK
- Session cookie without Secure = BLOCK (on HTTPS deployments)
- No TTL declared for any token type = FLAG

---

## Rule A3: Refresh Token Rotation

**Requirement:** Refresh tokens must rotate on every use. The server must:

1. Issue a new refresh token on every `/token/refresh` call
2. Invalidate the old refresh token immediately upon issuance of the replacement
3. Detect and reject reuse of a previously invalidated refresh token (refresh token reuse detection)
4. On reuse detection: invalidate the entire token family (all refresh tokens issued from the original grant)

**Rotation failure scenario (why this matters):**
```
1. Attacker steals refresh token RT1
2. Victim uses RT1 → server issues RT2, invalidates RT1
3. Attacker uses RT1 → server detects reuse → invalidates entire family including RT2
4. Both sessions destroyed — victim must re-authenticate
```

**Failure modes:**
- Refresh tokens without rotation = BLOCK
- No reuse detection = FLAG (with recommendation to implement full family invalidation)

**Exception:** Single-page apps using silent refresh with short-lived access tokens and no persistent refresh token do not require rotation (no refresh token exists). Declare this pattern in spec.

---

## Rule A4: MFA Requirements

**MFA is required for the following operations regardless of platform type:**

| Operation | MFA requirement |
|---|---|
| Admin panel login | Required |
| Privilege escalation (user → admin) | Required |
| Account deletion | Required; prefer delay window + confirmation email |
| Payment method add/change | Required |
| Bulk data export | Required |
| Disabling MFA on an account | Required |
| API key generation | Required |

**Acceptable MFA methods (in order of strength):**
1. Hardware security key (WebAuthn / FIDO2 passkey)
2. Authenticator app (TOTP — RFC 6238)
3. Push notification (with number matching)
4. SMS OTP (weak — acceptable only with documented risk acceptance; not acceptable for admin operations)

**Not acceptable as MFA:**
- Email "magic link" as second factor (phishable)
- Security questions
- Backup codes used as primary second factor (backup codes are emergency recovery, not daily MFA)

**Failure modes:**
- Admin operations without MFA declared = BLOCK
- SMS-only MFA for admin = FLAG with risk acceptance requirement
- MFA bypass via API (e.g., mobile app skips MFA that web enforces) = BLOCK

---

## Rule A5: No Credentials in localStorage or sessionStorage

**Rule:** Auth tokens, session identifiers, or any credential granting API access must not be stored in `localStorage` or `sessionStorage`.

**Rationale:** Both are readable by any JavaScript on the page, including XSS payloads. A single XSS vulnerability can harvest all stored tokens.

**Permitted storage locations:**

| Storage | Permitted for credentials | Notes |
|---|---|---|
| `httpOnly` cookie | Yes | JavaScript-inaccessible; CSRF protection required |
| Memory (JS variable) | Yes (with caveats) | Lost on page refresh; requires re-auth flow |
| `localStorage` | No | XSS accessible |
| `sessionStorage` | No | XSS accessible |
| Non-httpOnly cookie | No | XSS accessible |

**Caveats for memory storage:** If using access token in memory + refresh token in httpOnly cookie:
- Refresh token must follow Rule A3 (rotation)
- Silent refresh on page load must use `httpOnly` cookie, not any JS-readable storage
- Declare this architecture in spec

**Failure modes:**
- Auth token in localStorage with no justification = BLOCK
- Auth token in sessionStorage with no justification = BLOCK

---

## Rule A6: API Key Storage

**Rule:** API keys (user-generated tokens for programmatic access) must not be stored in plaintext.

**Required storage pattern:**
```
Store: SHA-256 hash of the key (or bcrypt/Argon2 for slow-hash preference)
Display: Full key shown to user exactly once on creation — never again
Prefix: Store a non-secret prefix (e.g., first 8 chars) for UI identification
```

**Key issuance:**
```
Generated key: sk-live-a1b2c3d4e5f6...
Stored in DB:  { prefix: "sk-live-a1", hash: sha256("sk-live-a1b2c3d4..."), created_at, last_used, scope }
Shown to user: Once, at creation time, with instruction to copy now
```

**Failure modes:**
- API keys stored in plaintext in database = BLOCK
- API keys logged in application logs = BLOCK (see also secrets-policy.md Rule S3)
- API keys displayable after initial issuance = FLAG

---

## Rule A7: OAuth / OIDC Implementation

**For any integration using OAuth 2.0 or OIDC:**

**Required:**
- Authorization Code flow with PKCE (RFC 7636) for all browser and mobile clients
- State parameter validated on callback to prevent CSRF
- Nonce validated in ID token for OIDC flows
- Token endpoint called server-side (not from browser) for Authorization Code exchange
- `redirect_uri` validation: exact match only (no prefix or wildcard matching)

**Forbidden:**
- Implicit flow (deprecated in OAuth 2.1)
- Resource Owner Password Credentials flow (except for legacy service-to-service with documented justification)
- `redirect_uri` wildcards in production

**Failure modes:**
- OAuth without PKCE for browser/mobile client = BLOCK
- Missing state parameter validation = BLOCK
- Wildcard redirect_uri = BLOCK
