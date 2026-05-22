# CLI Security — Platform Controls

These controls apply to all CLI targets. They are enforced by Verifier via `verification/gates.md`.

---

## Control 1: No Credential Arguments

**Rule:** Credentials (API keys, passwords, tokens, secrets) must not be accepted as positional arguments or named flags.

**Enforcement:** Code review + GWT test.

**Accepted forms:**
- Env var: `TOOL_API_KEY=<value> <tool> <cmd>`
- Stdin prompt: tool prompts for secret, input masked
- Config file: `~/.config/<tool>/config.toml` with `chmod 600`

**Rejected forms:**
- `<tool> deploy --api-key sk-abc123` — flag with value in args
- `<tool> login <password>` — positional arg

**Exception process:** None. This control has no exceptions.

---

## Control 2: No Shell Injection

**Rule:** User-supplied values must never be concatenated into shell command strings.

**Enforcement:** Code review.

**Banned patterns:**
```python
os.system(f"git clone {user_url}")          # Python — shell=True equivalent
subprocess.run(f"cp {src} {dst}", shell=True) # Python — explicit shell
```
```javascript
exec(`git clone ${userUrl}`)                // Node — exec uses shell
```
```go
exec.Command("sh", "-c", "git clone "+url)  // Go — shell injection
```

**Required patterns:**
```python
subprocess.run(["git", "clone", user_url])  # Python — no shell
```
```javascript
execFile("git", ["clone", userUrl])         // Node — no shell
```
```go
exec.Command("git", "clone", url)           // Go — explicit args
```

---

## Control 3: Path Validation Before File I/O

**Rule:** Any user-supplied file path must be resolved and validated before any read/write operation.

**Implementation:**
```python
import os
def safe_path(user_path: str, allowed_root: str) -> str:
    resolved = os.path.realpath(user_path)
    if not resolved.startswith(os.path.realpath(allowed_root)):
        raise ValueError(f"Path traversal detected: {user_path}")
    return resolved
```

**Validation must happen before:** `open()`, `os.rename()`, `shutil.copy()`, or any equivalent.

---

## Control 4: Secrets Never in Output

**Rule:** Credential values must not appear in stdout, stderr, log files, or debug output.

**Implementation:**
- Before logging or printing, scrub known secret patterns
- Mask in error handler: catch exceptions that might contain secret values, strip before printing
- Config file display: when showing config, mask fields marked as secrets (`api_key = "sk-***"`)

---

## Control 5: Minimal File Permissions

**Rule:** Files created by the CLI must have the minimum required permissions.

| File type | Required permissions |
|---|---|
| Config file containing secrets | 0600 (owner read/write only) |
| Output data files | 0644 (world-readable is fine) |
| Executable scripts created by tool | 0755 |
| State/cache files | 0600 or 0644 (declare in design-document) |

**Implementation:** Set permissions explicitly on creation. Do not rely on umask.

---

## Control 6: Dependency Audit Gate

**Rule:** `npm audit` / `pip-audit` / `cargo audit` must pass with zero critical or high findings before release.

**CI integration:** Run audit as a required CI step. Block release on any critical/high finding.

**Waiver process:** Critical findings with no fix available must be documented in a `SECURITY.md` entry with: CVE ID, affected version, impact assessment, and remediation timeline.

---

## Control 7: No Telemetry Without Opt-Out

**Rule:** Any data collection or network activity not directly required for the command's function must have an opt-out mechanism.

**Opt-out env var convention:** `<TOOL>_NO_TELEMETRY=1` or `<TOOL>_DISABLE_TELEMETRY=1`

**What counts as telemetry:** Usage statistics, error reports sent to external services, update checks, license pings.

**What does not count:** Network calls explicitly requested by the user as part of the command's purpose.

---

## Control 8: Update Check Security

If the CLI implements an update check:
- Must use HTTPS (TLS 1.2+ minimum)
- Must verify TLS certificate (no `InsecureSkipVerify`)
- Must not execute downloaded code without user confirmation
- Must not auto-update without explicit user consent
- Update check must be skippable: env var `<TOOL>_NO_UPDATE_CHECK=1`
