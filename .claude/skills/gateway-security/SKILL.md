---
name: gateway-security
description: Security capability gateway. Cross-cutting security concerns that apply regardless of platform. Activates on any target tagged with security-sensitive characteristics. Catches vulnerabilities that CLI, Web, and API/Service platform modules do not surface — git history exposure, cryptographic weaknesses, SAST findings, secrets in source, and cross-service trust failures.
---

# Gateway: Security

You are the cross-cutting security layer. You activate on top of (not instead of) the active platform package. Platform modules handle platform-specific threats. This gateway handles threats that apply regardless of platform: secrets in git history, weak cryptography, insecure randomness, SAST findings, and cross-boundary trust failures.

## What this skill does

| Concern | Covered by L3 platform | Covered by L4 gateway |
|---|---|---|
| Shell injection | CLI platform | — |
| XSS / CSRF | Web platform | — |
| SQL injection | API/Service platform | — |
| Auth bypass | API/Service platform | — |
| Secrets in git history | No L3 module | Yes |
| Weak cryptographic algorithms | No L3 module | Yes |
| Insecure randomness (security use) | No L3 module | Yes |
| SAST findings (Semgrep / Bandit / CodeQL) | No L3 module | Yes |
| Hardcoded secrets in source | No L3 module | Yes |
| Cross-service trust (blind data acceptance) | No L3 module | Yes |
| Encryption at rest (DB, file) | No L3 module | Yes |
| TLS configuration (cipher suites, cert management) | No L3 module | Yes |

## When to use

- Any target at L4 complexity or higher (declared by Recipe)
- Any target with tags: `security`, `authentication`, `payments`, `PII`, `secrets`
- Budget-gated for lower complexity: activation costs one adversarial review cycle

## Activation sequence

### Phase A (Specify time — knowledge injection)

```
1. Confirm platform package (L3) has already activated and written its receipt
2. Load references/ directory into Specify context:
   - references/threat-modeling.md (STRIDE, trust boundaries, threat format)
   - references/owasp.md (Top 10, API Top 10, ASVS baseline)
   - references/continuous-security.md (SAST, secret scanning, pentest scoping)
   - references/compliance.md (GDPR, SOC2, HIPAA, PCI-DSS — load relevant sections)
3. Run STRIDE analysis on the task
4. Produce security requirements as acceptance criteria in the spec
5. Write gateway-spec-receipt (Phase A)
```

### Phase B (pre-Executor — verdict)

```
1. Load threat-model.md (cross-cutting threats)
2. Load vulnerability-patterns.md (code patterns to grep for)
3. Load controls.md (required controls not covered by L3)
4. Register audit-gates.md with Verifier (supplements platform gates — does not replace them)
5. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

Security verdicts (BLOCK, CRITICAL, CVE) must be written in full prose regardless of any active output-compression mode. See homowabian auto-clarity rule.

### Runtime permission model (informational)

Gateway-security concerns apply at spec and verification time. The runtime permission system operates separately at execution time. Key facts relevant to security analysis:

- **Mode `bypassPermissions`** auto-approves all tool calls including destructive operations. Flag any task configuration that activates this mode as a security concern.
- **Policy settings** (MDM/enterprise deployment) have highest authority and cannot be overridden by any session grant, project setting, or hook.
- **Hook-based permission decisions** (`PreToolUse` → `permissionDecision: "deny"`) are the correct mechanism for security-enforcing hooks. Informational hooks (like WabbleSpec's prompt-guard) do not make permission decisions.
- **Classifier (auto mode):** A transcript-aware classifier can auto-approve or auto-block tool calls. `transcriptTooLong` and `unavailable` classifier results fall back to normal prompting rather than fail-closed — document this as a residual risk in threat models for security-sensitive deployments.
- **Rule source priority:** `policySettings` > `flagSettings` > `cliArg` > `command` > `session` > `localSettings` > `projectSettings` > `userSettings`.

Full permission decision tree: `_shared/references/permission-flow.md`.

### Red/Blue/Purple cycling (activated via /security-cycle or /security-red)

```
Phase A: Intel — references/cycling/security-profile.md (Recon + Surface + Context)
Phase B: Red  — references/cycling/red-protocol.md (attack)
Phase C: Blue — references/cycling/blue-protocol.md (defend)
Phase D: Purple — references/cycling/cycle-protocol.md (score + decision; 9-component model)
```

### InferenceGuard integration

InferenceGuard (L2) activates automatically when gateway-security is active. It prevents false refusals during Red-phase PoC generation and vulnerability analysis.

- Red protocol: InferenceGuard active, tier=standard, technique=leetspeak (configurable in security-profile)
- Blue protocol: InferenceGuard SUPPRESSED — task card must declare `inference_guard: false`
- Purple scoring: 9th component (inference quality, 5%) reads `inference_guard_summary.refusal_count` from Red receipt

Override tier/technique in the security profile header fields: `InferenceGuard tier` and `InferenceGuard technique`.

## Output contract

- Cross-cutting threat assessment (additive to platform threat model)
- SAST report (Semgrep or equivalent)
- Git history secret scan result
- Gateway activation receipt with all gate results

## Files loaded by this module

```
modules/l4/security/
  threat-model.md
  vulnerability-patterns.md
  controls.md
  audit-gates.md
```
