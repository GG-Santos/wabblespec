# CLI Security — Threat Model

## Threat Surface

A CLI tool's threat surface is different from a web application. The primary attack vectors are:

1. **Shell injection via arg interpolation** — user-supplied args passed unsanitized to shell commands
2. **Path traversal** — user-supplied file paths that escape intended scope
3. **Credential exposure** — secrets visible in process list, shell history, or error output
4. **Supply chain** — malicious code in dependencies or postinstall scripts
5. **Privilege escalation** — tool runs with more permissions than needed

---

## Threat 1: Shell Injection via Arg Interpolation

**Description:** User passes a value like `; rm -rf /` as a CLI argument. If the tool passes this to a shell (`exec(sh -c "git clone " + url)`), arbitrary commands execute.

**Attack scenario:**
```bash
<tool> process --repo "https://example.com/repo; rm -rf ~"
```

**Mitigations:**
- Never construct shell commands via string concatenation
- Use execvp/exec-family calls with explicit argument arrays (never `sh -c "... + userInput"`)
- In Node: use `execa` or `child_process.execFile` (not `exec`). In Python: `subprocess.run([...])` with list args (never `shell=True`). In Go: `exec.Command(binary, args...)`. In Rust: `Command::new(binary).args([...])`.
- Validate that values conform to expected format before use

**Verification gate:** Code review check for `shell=True`, `exec(`, `sh -c "` + variable concatenation.

---

## Threat 2: Path Traversal

**Description:** User passes `../../etc/passwd` or `../sensitive-file` as a file path argument. Tool reads/writes outside intended directory.

**Attack scenario:**
```bash
<tool> read --file "../../.env"
```

**Mitigations:**
- Resolve all paths with `path.resolve()` / `os.path.abspath()` / `filepath.Abs()` before use
- Validate resolved path is within expected root:
  ```python
  resolved = os.path.abspath(user_path)
  if not resolved.startswith(os.path.abspath(allowed_root)):
      sys.exit("Error: path traversal detected")
  ```
- Never operate on paths before resolution

**Verification gate:** GWT test passes a `../../` path and expects non-zero exit with traversal error message.

---

## Threat 3: Credential Exposure

**Description:** API keys, passwords, or tokens visible in `ps aux` output, shell history files, or CI logs.

**Attack scenarios:**
```bash
<tool> deploy --api-key sk-abc123   # visible in ps aux
history | grep api-key              # in shell history
```

**Mitigations:**
- Never accept credentials as positional arguments or `--flag value` arguments
- Accept credentials via: env vars (`TOOL_API_KEY`), stdin prompt (masked), or config file with restrictive permissions (0600)
- Mask credential values in all error messages, logs, and debug output
- Config file: write with `chmod 600` if it contains credentials

**Verification gate:** Spec declares credential handling strategy. Code review confirms no credential flags. GWT test verifies rejection of credential-as-arg.

---

## Threat 4: Supply Chain

**Description:** Malicious code injected via npm/PyPI/crates.io dependency, or via postinstall script.

**Mitigations:**
- Lock file committed (package-lock.json / requirements.txt pinned / Cargo.lock / go.sum)
- Audit dependencies before adding: `npm audit` / `pip-audit` / `cargo audit`
- No postinstall scripts that execute arbitrary code
- Minimize dependency count — each dep is an attack surface
- Pin to exact versions in production builds (not `^` or `~` ranges in lockfile)

**Verification gate:** Lock file present in repo. `npm audit` / `cargo audit` run in CI with zero critical findings gate.

---

## Threat 5: Privilege Escalation

**Description:** Tool requests or assumes elevated privileges it does not need.

**Mitigations:**
- Document any operations that require elevated privileges (sudo, admin)
- Request elevation only for specific operations, not at tool startup
- Never setuid
- If the tool installs a daemon/service, document the required permissions explicitly

**Verification gate:** Tool must not require sudo to install or run basic commands. Declared in design-document.

---

## Threat 6: Network Calls Without Disclosure

**Description:** Tool makes unexpected network calls — telemetry, update checks, license validation — without user knowledge.

**Mitigations:**
- Any network call must be disclosed in --help text for the relevant command
- Telemetry/update checks: opt-out env var required (`TOOL_NO_TELEMETRY=1`, `TOOL_NO_UPDATE_CHECK=1`)
- Never make network calls on `--help` or `--version` invocations
- Document all network destinations in design-document.md

**Verification gate:** `<tool> --help` must not make network calls (test with network blocked).
