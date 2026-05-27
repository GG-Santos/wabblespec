# Acceptance Tests — Gateway: Engineering (L4)

## AT-ENG-GW-01: L3 platform receipt required before activation

**Given** an Engineering gateway invocation
**When** no L3 platform receipt exists for the current execution
**Then** the gateway FAILs Phase A — it activates on top of, not instead of, the platform package

---

## AT-ENG-GW-02: Two-phase activation sequence

**Given** an Engineering gateway activation
**When** execution proceeds
**Then**:
- Phase A loads quality-patterns.md, architecture.md, and infrastructure files based on project signals; writes `gateway-spec-receipt`
- Phase B loads build-standards.md, code-quality.md, dependency-standards.md; registers quality-gates.md with Verifier; writes `gateway-verdict-receipt`

---

## AT-ENG-GW-03: Infrastructure files loaded based on project signals

**Given** Engineering gateway Phase A
**When** infrastructure files are loaded
**Then**:
- `cicd.md` is always loaded
- `containers.md` loaded only when Dockerfile or k8s manifests are detected
- `iac.md` loaded only when Terraform/Pulumi files are detected
- `observability.md` loaded only when metrics/tracing config is detected or declared in spec

---

## AT-ENG-GW-04: Test coverage floor BLOCK condition

**Given** Engineering gateway Phase B evaluating a project
**When** statement coverage is below 80% (rule Q1 from code-quality-policy.md)
**Then** verdict is BLOCK — the coverage floor is a hard gate, not advisory

---

## AT-ENG-GW-05: Cyclomatic complexity BLOCK condition

**Given** Engineering gateway Phase B
**When** any function has cyclomatic complexity > 15 (rule Q2)
**Then** verdict is BLOCK for that finding; complexity between 11-15 produces FLAG

---

## AT-ENG-GW-06: Dependency N-2 behind BLOCK condition

**Given** Engineering gateway Phase B evaluating dependencies
**When** any dependency is more than 2 major versions behind current (rule D1)
**Then** verdict is BLOCK for that dependency

---

## AT-ENG-GW-07: Platform-specific build toolchain not re-audited

**Given** an active L3 CLI platform package
**When** Engineering gateway runs
**Then** it does not re-check the CLI-specific build toolchain; it only audits universal quality standards not covered by L3

---

## AT-ENG-GW-08: Low complexity targets use quality-gates.md only

**Given** a Low complexity target
**When** Engineering gateway activates
**Then** only `quality-gates.md` is loaded and evaluated; full gateway activation (all Phase B files) is skipped

---

## AT-ENG-GW-09: Gateway receipt contains all gate results

**Given** a completed Engineering gateway Phase B
**Then** the `gateway-verdict-receipt` contains:
- `gateway`
- `phase`
- `verdict` (PASS | FLAG | BLOCK)
- `coverage_percent`
- `complexity_violations`
- `dependency_findings`
- `platform_receipt_verified`
