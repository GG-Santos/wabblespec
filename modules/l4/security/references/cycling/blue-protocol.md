# Blue Protocol — Defense Phase

Activated by `/security-blue` or as Phase C of a security cycle. Responds to Red findings by designing and implementing defenses.

## Role

Blue is the defender. Blue reads Red's findings and produces: mitigations for each finding, hardening beyond the specific findings (class-level defense), and regression tests that verify both the fix and the broader defense.

Blue does not patch findings — Blue fixes the root cause. Patching a specific endpoint is not Blue; fixing the input validation pattern across all endpoints is Blue.

## Required task card flag

Blue phase task cards MUST declare: `inference_guard: false`

Blue works with explicit vulnerability names from Red findings. InferenceGuard transforms would corrupt these names and break Blue's ability to map findings to code. Suppression is mandatory, not optional.

## ContextTuner profiles for Blue tasks

Blue switches context type by phase:
- **Analysis phase** (reading Red findings, root cause analysis): `security-review` (temperature=0.50)
- **Implementation phase** (writing fixes and regression tests): `code-generation` (temperature=0.20)

Model-router selects the appropriate profile based on the dominant content of the current Blue wave.

## STM transforms on Blue findings

Apply `hedge_reducer` and `direct_mode` STM transforms to all defense findings before receipt write:
- Removes hedging from root cause analysis ("might be", "could be", "appears to")
- Removes preamble from implementation blocks ("Sure, here is the fix")

STM is applied to the prose content of defense findings only — not to code blocks or test cases. Run `_shared/scripts/stm-pipeline.py` with transforms `["hedge_reducer", "direct_mode"]` on each finding's prose fields before writing the Blue receipt.

## Required output per Red finding

For each Red finding, Blue must produce:

### 1. Root cause analysis

Why did this vulnerability exist? One of:
- Missing control (no validation, no auth check)
- Incorrect control (validation existed but was bypassable)
- Incomplete control (validation existed for some paths but not all)
- Configuration error (control existed but was disabled or misconfigured)

The fix must address the root cause, not the symptom.

### 2. Minimum two defense layers

One layer is never sufficient. Declare both:
- **Layer 1**: primary fix (the control that directly prevents the attack)
- **Layer 2**: secondary control (defense-in-depth — reduces impact if Layer 1 fails)

Example for IDOR:
- Layer 1: ownership check on resource access (`WHERE user_id = ?` in query)
- Layer 2: response field filtering (never return fields the requester has no right to see)

### 3. Class-level hardening

The finding revealed a pattern. Fix the pattern, not just the instance.

Example: finding RED-001 is IDOR on `/users/{id}`. Class-level hardening:
- Audit all endpoints that take resource IDs
- Verify each has an ownership check
- Create a test helper that makes ownership checks easy to write and hard to forget

### 4. Regression tests

For each finding:
- A test that reproduces the vulnerability (fails before fix)
- A test that verifies the fix works (passes after fix)
- A test that verifies the class-level hardening (covers similar attack paths)

The PoC-as-test-case from Red becomes the regression test suite for Blue.

## Defense finding format

```markdown
## DEFENSE: {title} (responds to RED-{number})

**ID**: BLUE-{number}  
**Severity addressed**: {CRITICAL | HIGH | MEDIUM | LOW}  
**Root cause**: {missing | incorrect | incomplete | configuration}  

### Root Cause Analysis
{Why this vulnerability existed}

### Mitigation — Layer 1 (Primary)
{The main fix; how it prevents the attack}

Implementation:
```
{Code change, config change, or architectural change}
```

### Mitigation — Layer 2 (Defense in Depth)
{Secondary control that limits impact if Layer 1 is bypassed}

### Class-Level Hardening
{What broader pattern was addressed; what was audited and changed across the codebase}

### Regression Tests
```
{Test that reproduces original vulnerability — should fail without fix}
{Test that verifies fix — should pass with fix}
{Test covering related attack paths}
```

### Verification
- [ ] PoC from RED-{number} no longer works
- [ ] All regression tests pass
- [ ] Class-level audit completed; findings documented
```

## Security debt tracking

If a finding cannot be fully fixed in the current cycle (resource constraints, architectural dependency):

```markdown
## DEFERRED: {title} (RED-{number})

**Risk acceptance**: {who accepts the risk; date}
**Compensating control**: {what reduces the risk in the interim}
**Fix timeline**: {when will this be addressed}
**Re-test required**: yes — verify compensating control is effective
```

CRITICAL findings must not be deferred without security team sign-off and documented risk acceptance.

## Output

Blue produces:
1. Defense findings (one per Red finding)
2. Class-level hardening summary (what was changed beyond specific findings)
3. Regression test suite (all tests passing)
4. Deferred items list (if any, with risk acceptance documentation)
5. Verification matrix (each Red finding mapped to Blue response and verification status)
