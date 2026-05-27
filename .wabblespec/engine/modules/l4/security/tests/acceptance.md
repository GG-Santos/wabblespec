# Acceptance Tests — Gateway: Security (L4)

## AT-SEC-GW-01: L3 platform receipt required before activation

**Given** a Security gateway invocation
**When** no L3 platform receipt exists for the current execution
**Then** the gateway FAILs Phase A with a missing-platform-receipt error — it activates on top of, not instead of, the platform package

---

## AT-SEC-GW-02: Phase A runs at Specify time, Phase B runs pre-Executor

**Given** a Security gateway activation
**When** execution proceeds
**Then**:
- Phase A writes `gateway-spec-receipt` and injects cross-cutting security requirements into the spec
- Phase B writes `gateway-verdict-receipt` with a PASS / FLAG / BLOCK verdict before Executor begins

---

## AT-SEC-GW-03: Platform-specific threats are not re-checked

**Given** a project with an active L3 Web platform package
**When** Security gateway runs
**Then** it does not re-audit XSS, CSRF, or SQL injection — those are owned by the L3 module; the gateway only covers cross-cutting concerns

---

## AT-SEC-GW-04: Secrets in git history checked

**Given** a Security gateway Phase B run
**When** the git history secret scan runs
**Then** if secrets are found in git history, the finding is present in the gateway receipt with FLAG or BLOCK severity depending on secret type

---

## AT-SEC-GW-05: SAST findings surface in gateway receipt

**Given** a Security gateway Phase B run
**When** SAST (Semgrep/Bandit/CodeQL) findings are present
**Then** they appear in the gateway activation receipt; critical findings produce BLOCK verdict, moderate produce FLAG

---

## AT-SEC-GW-06: STRIDE analysis produced in Phase A

**Given** Security gateway Phase A
**When** context injection runs
**Then** a STRIDE analysis of the task is produced and security requirements are written as acceptance criteria in the spec

---

## AT-SEC-GW-07: Auth policy rules enforced (A1-A7 from auth-policy.md)

**Given** Security gateway Phase B evaluating an authentication-related target
**When** auth-policy.md rules are applied
**Then** any violation of rules A1-A7 produces a FLAG or BLOCK finding in the verdict receipt per rule severity

---

## AT-SEC-GW-08: Secrets policy rules enforced (S1-S8 from secrets-policy.md)

**Given** Security gateway Phase B evaluating any target
**When** secrets-policy.md rules are applied
**Then** any violation of rules S1-S8 (secrets in source, env file exposure, rotation policy) produces a FLAG or BLOCK finding per rule severity

---

## AT-SEC-GW-09: Gateway receipt contains all gate results

**Given** a completed Security gateway Phase B
**Then** the `gateway-verdict-receipt` contains:
- `gateway`
- `phase`
- `verdict` (PASS | FLAG | BLOCK)
- `gates_run`
- `findings` (list with severity per finding)
- `platform_receipt_verified`
