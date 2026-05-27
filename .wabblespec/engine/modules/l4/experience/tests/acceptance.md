# Acceptance Tests — Gateway: Experience (L4)

## AT-EXP-GW-01: Requires explicit scope declaration at P1

**Given** a visual-facing project where user research has NOT been declared in scope at P1
**When** Experience gateway is evaluated for activation
**Then** it does not activate — it requires explicit user-research scope declaration; Design gateway still applies unconditionally

---

## AT-EXP-GW-02: Design gateway must be active before Experience activates

**Given** an Experience gateway invocation
**When** no Design gateway receipt exists for the current execution
**Then** the gateway FAILs Phase A — Experience activates on top of Design, not independently

---

## AT-EXP-GW-03: Experience adds to Design; does not replace it

**Given** both Design and Experience gateways active on a project
**When** the Experience gateway evaluates the project
**Then** it performs research method compliance, screen reader matrix, color blindness simulation, cognitive/motor accessibility checks, and satisfaction measurement — it does not re-run the WCAG 2.1 AA baseline audit (that is Design's domain)

---

## AT-EXP-GW-04: Usability test scenarios must be written before sessions

**Given** Experience gateway Phase B evaluating a usability study
**When** test scenarios have not been written before sessions begin (rule R2 from research-standards-policy.md)
**Then** verdict is FLAG — scenario-first is required for valid usability research

---

## AT-EXP-GW-05: Screen reader matrix requires NVDA/Firefox

**Given** Experience gateway Phase B evaluating screen reader coverage
**When** NVDA with Firefox is not included in the test matrix (rule AT1 from accessibility-testing-policy.md)
**Then** verdict is FLAG — NVDA/Firefox is the required minimum for screen reader testing

---

## AT-EXP-GW-06: Drag-and-drop must have alternatives

**Given** Experience gateway Phase B evaluating an interface with drag-and-drop interactions
**When** no alternative input mechanism exists (rule AT4)
**Then** verdict is FLAG — gesture-only interactions fail motor accessibility requirements

---

## AT-EXP-GW-07: Research insights written to Memory as FRESH drawers

**Given** a completed Experience gateway run
**When** research insights are produced
**Then** they are written to Memory as FRESH drawers; they are not left only in the gateway receipt

---

## AT-EXP-GW-08: Research ethics requirements enforced

**Given** Experience gateway Phase B loading research-ethics.md
**When** a research plan lacks participant consent or anonymization procedures
**Then** the finding is surfaced in the verdict receipt as a FLAG

---

## AT-EXP-GW-09: Gateway receipt contains all gate results

**Given** a completed Experience gateway Phase B
**Then** the `gateway-verdict-receipt` contains:
- `gateway`
- `phase`
- `verdict` (PASS | FLAG | BLOCK)
- `research_method_check`
- `usability_scenarios_written`
- `screen_reader_matrix_check`
- `color_blindness_simulation`
- `cognitive_accessibility_check`
- `motor_accessibility_check`
- `satisfaction_measurement_declared`
- `design_gateway_receipt_verified`
