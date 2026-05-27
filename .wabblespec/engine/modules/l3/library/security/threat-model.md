# Library Security — Threat Model

## Threat Surface

A library's threat surface differs from applications. The library itself is rarely attacked directly — it becomes an attack vector through its consumers and the supply chain that delivers it.

1. **Supply chain compromise** — malicious code injected via compromised registry account, dependency, or CI pipeline
2. **Typosquatting** — malicious package published with a name similar to this library to trap mis-typed installs
3. **Prototype pollution** — library mutates `Object.prototype` or global prototypes, affecting all consumer code
4. **ReDoS via regex** — library uses backtracking regexes on consumer-supplied input, enabling denial of service
5. **Malicious postinstall** — postinstall/preinstall scripts execute arbitrary code at consumer install time
6. **Version confusion** — consumers pin to an old version with known vulnerabilities due to missing security advisories

---

## Threat 1: Supply Chain Compromise

**Description:** Attacker gains publish access (stolen npm token, compromised CI, malicious maintainer) and publishes a version containing backdoor code that executes in every consumer's environment.

**Attack scenarios:**
- Stolen npm access token used to publish `<lib>@<next-patch>` with added `eval()`
- CI pipeline injects malicious code during build step before `npm publish`
- Compromised dependency publishes new version with malicious `postinstall`

**Mitigations:**
- Publish from CI only — no human publish from local machine
- CI publishes using a scoped npm token with `publish` permission only (no delete, no settings)
- Enable npm 2FA for publish
- Use `npm publish --provenance` (GitHub Actions provenance attestation)
- Lock all build-time dependencies (exact versions in CI, not `^`)
- Pin GitHub Actions to commit SHA (not tag)
- Run `npm audit` / `cargo audit` / `pip-audit` as CI gate before publish

**Verification gate:** CI pipeline reviewed. Publish token is scoped to publish-only. Provenance attestation enabled.

---

## Threat 2: Typosquatting / Name Confusion

**Description:** Attacker publishes `<lib>js`, `<lib>-js`, `<lib>_utils`, or other name variants to catch developers who mistype the package name.

**Mitigations (defensive, for library publisher):**
- Register obvious name variants on the registry if feasible
- Include canonical package name prominently in README and documentation
- Publish `SECURITY.md` with the canonical registry URL
- Monitor for name-similar packages (npm namespace watch)

**Verification gate:** README states canonical install command. SECURITY.md exists with canonical package name.

---

## Threat 3: Prototype Pollution

**Description:** Library code that accepts objects and merges/copies them can allow an attacker to inject properties onto `Object.prototype`, affecting all objects in the consumer's runtime.

**Attack scenario:**
```javascript
lib.merge(target, JSON.parse('{"__proto__": {"isAdmin": true}}'))
// Now: ({}).isAdmin === true — for ALL objects in the process
```

**Mitigations:**
- Never use `obj[key] = value` where `key` is user-supplied without validation
- Block `__proto__`, `constructor`, `prototype` as property names
- Use `Object.create(null)` for dictionaries that accept arbitrary keys
- Use `structuredClone()` or validated deep clone instead of `{...obj}` for untrusted input
- Audit all merge/assign/clone functions in the library

**Verification gate:** Code review of all object merge/assign operations. No `__proto__` assignment paths.

---

## Threat 4: ReDoS via Backtracking Regex

**Description:** Library uses a regex that can be caused to backtrack exponentially on crafted input, consuming 100% CPU for seconds or minutes in consumer applications.

**Attack scenario:**
```javascript
// Vulnerable: (a+)+ pattern
const result = lib.validate("aaaaaaaaaaaaaaaaaaaab")
// Takes seconds/minutes to complete
```

**Mitigations:**
- Avoid nested quantifiers in regexes: `(a+)+`, `(a|a)+`, `(a*)*`
- Use linear-time regex engines where available (Node 18+ `v` flag, RE2)
- Validate with `safe-regex` or `vuln-regex-detector` against all library regexes
- For complex validation, prefer parser-combinator approach over single regex

**Verification gate:** All regexes in library audited with `safe-regex`. No nested quantifier patterns.

---

## Threat 5: Malicious Postinstall

**Description:** `preinstall`/`postinstall`/`prepare` scripts in `package.json` execute at install time in the consumer's environment with full OS access.

**Mitigation:**
- **Zero postinstall scripts in this library.** No `postinstall`, `preinstall`, or `prepare` scripts.
- Build steps are developer-facing only (in `devDependencies` and dev scripts)
- The published `dist/` is pre-built — no build step needed at install time

**Verification gate:** `package.json` `scripts` field contains no `postinstall`, `preinstall`, or `install` keys. Confirmed in `npm pack --dry-run` output.

---

## Threat 6: Version Confusion / Unpatched Consumers

**Description:** Security vulnerability found in older version, but many consumers remain on it because they don't know about the fix.

**Mitigations:**
- File GitHub Security Advisory for any security fix (enables Dependabot alerts for consumers)
- Clearly mark security fixes in CHANGELOG with `[Security]` tag
- Publish patch for last two MAJOR versions when practical
- Maintain a `SECURITY.md` with disclosure process and supported versions
- Use `npm deprecate <lib>@<bad-version> "Security: upgrade to <fixed>"` to warn consumers

**Verification gate:** `SECURITY.md` exists. Security fixes marked in CHANGELOG. GitHub Security Advisory filed for any past vulnerabilities.
