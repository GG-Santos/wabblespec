# User Language

Translation patterns from developer commit language to user-facing changelog language.

## Core principle

Users do not care what changed in the code. They care what changed in their experience. The changelog entry answers: "What can I do now that I couldn't do before?" or "What got better/fixed?"

## Translation patterns

| Developer language | User language |
|---|---|
| "implement OAuth2 PKCE flow" | "Added secure sign-in for mobile apps" |
| "refactor database connection pooling" | (excluded — internal) |
| "fix null pointer exception in auth handler" | "Fixed crash when signing in with certain account types" |
| "add dark mode support" | "Added dark mode" |
| "improve API response time by 40%" | "Responses are 40% faster" |
| "deprecate `/v1/users` endpoint" | "The `/v1/users` API endpoint is deprecated — use `/v2/users` instead" |
| "upgrade dependency: react 18.3" | (excluded — internal) |
| "fix XSS vulnerability in comment renderer" | "Fixed a security issue in comments" (Security section) |

## Rules for translation

1. **Name the user benefit, not the technical mechanism.** "OAuth2 PKCE" → "secure mobile sign-in." The user does not need to know the mechanism.

2. **Do not name internal systems.** Database names, microservice names, internal API names, class names, function names — strip them all. Replace with the user-visible feature or area.

3. **Quantify performance improvements when possible.** "Faster" is weak. "40% faster" is a user benefit. Use the metric from the commit body if available.

4. **Security entries are special.** Name the type of issue fixed but not the exploit details. "Fixed a security issue in the file upload feature" — not "Patched CVE-2026-1234" (include CVE in developer changelog variant).

5. **Scope becomes a product area label.** The conventional commit scope suggests where in the product the change happened. Map it to a user-visible label:
   - `auth` → "sign-in" or "authentication"
   - `dashboard` → "dashboard"
   - `api` → "API"
   - `billing` → "billing"
   - `notifications` → "notifications"

6. **Past tense for completed changes.** "Added support for X." "Fixed crash when Y." "Removed Z."

## Prohibited in user-facing changelog

- Function names: `handleAuth()`, `UserService.delete()`
- Database identifiers: `users table`, `session_tokens column`
- Internal system names: "Our Kafka consumer now..."
- Acronyms without expansion: "PKCE" must be "secure mobile sign-in (PKCE)"
- Error codes without explanation: "Fixed NPE" → "Fixed crash"
- Pull request numbers: #1234 (links are fine; raw PR numbers are noise)
