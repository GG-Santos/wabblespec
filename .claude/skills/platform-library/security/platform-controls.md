# Library Security — Platform Controls

These controls apply to all Library/Package targets. Enforced by Verifier via `verification/gates.md`.

---

## Control 1: No Postinstall Scripts

**Rule:** The published package must not contain `postinstall`, `preinstall`, or `install` lifecycle scripts.

**Enforcement:** `npm pack --dry-run` + manual review of published `package.json`.

**Why:** Postinstall scripts execute arbitrary code in the consumer's environment at install time. They are a primary supply chain attack vector.

**Exception process:** None. Zero exceptions. If native compilation is required (e.g., native addon), use optional dependencies with explicit consumer opt-in.

---

## Control 2: No Prototype Mutation

**Rule:** The library must not modify `Object.prototype`, `Array.prototype`, `Function.prototype`, or any built-in prototype.

**Enforcement:** Code review. Grep for `prototype.` assignments.

**Banned patterns:**
```javascript
Object.prototype.myMethod = function() {}   // forbidden
Array.prototype.flatten = function() {}     // forbidden
```

**Allowed:** Defining methods on library-owned classes/instances only.

---

## Control 3: Safe Object Merge

**Rule:** Any function that merges or copies object properties from untrusted input must block prototype pollution keys.

**Required implementation:**
```javascript
const BLOCKED_KEYS = new Set(['__proto__', 'constructor', 'prototype'])

function safeMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (BLOCKED_KEYS.has(key)) continue
    target[key] = source[key]
  }
}
```

**Applies to:** Any merge, assign, extend, defaults, or deep-clone function that accepts user-supplied objects.

---

## Control 4: Regex Safety

**Rule:** All regexes in the library must be verified as non-backtracking before release.

**Enforcement:** `safe-regex` or `vuln-regex-detector` run against all regex literals in source.

**CI command:**
```bash
npx safe-regex-cli src/**/*.ts
```

**Flagged patterns:** `(a+)+`, `(a|a)+`, `(a*)*`, `(.+)+`, overlapping alternations with shared prefixes.

---

## Control 5: No Credential Handling

**Rule:** Libraries must not accept, store, or transmit credentials (API keys, passwords, tokens).

**Exception:** Libraries explicitly designed for auth (e.g., an OAuth client). In that case:
- Credentials must never be logged
- Credentials must never appear in error messages
- Credentials must never be stored in non-memory state without explicit consumer consent
- Document credential lifecycle explicitly in design-document.md

---

## Control 6: Minimal Network Access

**Rule:** Libraries must not make network calls at import time or without explicit consumer invocation.

**No automatic calls:**
- No telemetry on import
- No update checks on first call
- No license validation on startup

**If the library makes network calls by design:**
- Document all network destinations in design-document.md
- All calls must be consumer-triggered (not background/automatic)
- TLS required for all connections (no HTTP fallback)
- Certificate verification must not be disabled

---

## Control 7: Dependency Minimization

**Rule:** Each added dependency must be justified. Dependencies with known vulnerabilities block release.

**Dependency review checklist (per dependency):**
- [ ] Cannot be replaced with < 20 lines of owned code
- [ ] Actively maintained (commit in last 12 months)
- [ ] No known critical/high CVEs
- [ ] Does not itself have a large dependency tree
- [ ] License is compatible with this library's license

**CI gate:** `npm audit --audit-level=high` / `cargo audit` / `pip-audit` — zero high/critical findings block release.

---

## Control 8: Published Artifact Integrity

**Rule:** Published package contents must match what was built from the tagged commit.

**Enforcement:**
- Publish from CI only, triggered by tag push
- CI runs full build + tests before publish
- `npm publish --provenance` enabled (links published package to CI run + source commit)
- For Rust: `cargo publish` from CI after `cargo test` passes on the tagged ref
- Verify `npm pack --dry-run` output does not include: `src/`, `.env`, credentials, test fixtures with real data

---

## Control 9: SECURITY.md Required

**Rule:** Every published library must have a `SECURITY.md` at the repository root.

**Required content:**
- Canonical package name and registry URL
- Supported versions (which versions receive security patches)
- Vulnerability disclosure process (email, GitHub Security Advisory form, etc.)
- Response time commitment
- PGP key or contact for encrypted disclosure (if applicable)
