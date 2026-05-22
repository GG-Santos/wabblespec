# Module Plan — Guard (L2)

**Tier:** 2 — FOUNDATION
**Layer:** L2 Orchestration
**v5.3 origin:** Guard module — runtime input validation and constraint enforcement

---

## Purpose

Pre-execution input validation and constraint enforcement. Guard runs before each Executor wave to validate inputs against declared schemas, check scope constraints (I12), and verify invariant compliance. Validates only — never transforms inputs. Routes violations to Reviewer (minor) or raises SPEC_VIOLATION error (hard block). Guard is the last line of defense before execution touches project/repo/.

---

## Activation

`skill-rules.json` triggers:
- Before each Executor wave (always — Guard is mandatory pre-wave gate)
- Explicit `/guard <input>` command for standalone validation
- Verifier Audit mode consultation (Guard provides constraint checklist)

Guard cannot be bypassed. No Executor wave proceeds without Guard PASS.

---

## Validation Layers

Guard runs four validation layers in sequence:

### Layer 1: Schema validation

- All wave inputs validated against declared input schemas (from skill-rules.json authority declarations)
- Malformed inputs: HARD error — abort wave
- Missing required fields: HARD error — abort wave
- Unknown fields: SOFT warning — log, proceed

### Layer 2: Scope constraint (I12)

- Verify: wave task within declared scope.md boundaries
- Verify: no out-of-scope files targeted (I11 — project/repo/ only for Executor)
- Verify: wave does not expand scope beyond current spec stage
- Scope violation: SPEC_VIOLATION error — route to human (cannot self-resolve)

### Layer 3: Invariant compliance

Checks all 12 invariants before wave execution:

| Invariant | Check |
|---|---|
| I1 (Single entry point) | Wave does not create competing entry points |
| I2 (Plan/Execute separation) | Wave is not mixing spec writing with code execution |
| I6 (Vendor-neutral) | No model names in wave inputs |
| I9 (Evidence expiry) | No EXPIRED evidence in wave inputs |
| I10 (Receipt chain) | Prior wave receipt exists before this wave begins |
| I11 (Framework/Product separation) | Wave writes only to declared target (not crossing boundary) |
| I12 (Spec quality) | Wave spec inputs not bloated (word count within threshold) |

Invariant violation: SPEC_VIOLATION error — Reviewer consulted, Attestation if irreversible.

### Layer 4: Authority check

- Verify: requesting module has authority over target files (from skill-rules.json)
- Unauthorized write target: HARD error — abort, log violation
- No module can grant itself authority it did not declare in skill-rules.json

---

## Workflow

```
1. Receive wave inputs from Executor

2. Run Layer 1 — schema validation
   -> HARD violation: return error to Executor, abort wave

3. Run Layer 2 — scope constraint
   -> SPEC_VIOLATION: route to Reviewer, halt wave pending resolution

4. Run Layer 3 — invariant compliance
   -> SPEC_VIOLATION: route per invariant (Reviewer for minor, Attestation for irreversible)

5. Run Layer 4 — authority check
   -> HARD violation: return error to Executor, abort wave

6. All layers pass: return PASS to Executor, wave proceeds

7. Write Guard receipt (per wave)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — mandatory pre-wave, authority declaration |
| `rules/invariant-checklist.md` | Rules | Per-invariant check specification |
| `rules/scope-validation.md` | Rules | Scope boundary check rules |
| `rules/authority-matrix.md` | Rules | Module authority lookup |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Executor | Executor calls Guard before each wave; Guard PASS required to proceed |
| Reviewer | Guard routes SPEC_VIOLATION to Reviewer for resolution |
| Specify | Guard reads scope.md (Specify output) for scope constraint checks |
| Verifier | Verifier reads Guard receipts during Audit verification mode |
| ScopeFrame | Guard reads scope.md maintained by ScopeFrame |

---

## Verification Mode

**Observation** — Guard receipt present for every wave, no bypassed validations, all four layers run per wave.

---

## Receipt Extension Fields

```json
{
  "wave_id": "string",
  "schema_validation": "PASS|FAIL",
  "scope_constraint": "PASS|FAIL|SPEC_VIOLATION",
  "invariant_compliance": "PASS|FAIL|SPEC_VIOLATION",
  "authority_check": "PASS|FAIL",
  "overall": "PASS|FAIL",
  "violations": ["string"]
}
```
