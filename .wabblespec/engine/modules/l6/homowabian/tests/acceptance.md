# Acceptance Tests — Homowabian (L6)

## AT-HOMO-01: Register is passively set via CLAUDE.md, not skill invocation

**Given** a session where register level is to be configured
**When** the register is set
**Then** it is set via CLAUDE.md configuration, not by invoking Homowabian as a skill command

---

## AT-HOMO-02: Four register levels recognized

**Given** a Homowabian configuration
**When** register level is declared
**Then** the following levels are valid: `normal`, `lite`, `full`, `ultra`

---

## AT-HOMO-03: Receipts always JSON regardless of register

**Given** any active register level including `lite`
**When** a task completes and a receipt is written
**Then** the receipt is always in JSON format — register level does not change the receipt format

---

## AT-HOMO-04: Module exists for documentation, not invocation

**Given** the Homowabian module
**When** examined for its operational role
**Then** the module documents how register control works; it is not invoked as a skill to change register during a session — CLAUDE.md is the configuration mechanism
