# InferenceGuard Acceptance Criteria

## AC-1: Activation on Red task with Tier 2 triggers

**Given:** Task card with `task_type: red-team` and gateway-security active  
**And:** Input contains "exploit SQL injection via payload"  
**When:** InferenceGuard executes  
**Then:** Receipt shows `activated: true`  
**And:** `triggers_detected` includes `exploit` and `payload` (Tier 2 terms)  
**And:** `transformations` array is non-empty with original→transformed pairs  
**And:** `tier_applied: standard`

## AC-2: Non-activation on general code task

**Given:** Task card with `task_type: code-generation`  
**And:** No gateway-security receipt in session  
**When:** InferenceGuard executes  
**Then:** Receipt shows `activated: false, reason: gateway_inactive`  
**And:** No transformations applied to input  
**And:** Input containing "implement a delete function" is unchanged

## AC-3: Suppression via task card flag

**Given:** Task card contains `inference_guard: false`  
**And:** Gateway-security is active  
**When:** InferenceGuard executes  
**Then:** Receipt shows `activated: false, reason: suppressed`  
**And:** No trigger detection runs  
**And:** No transforms applied

## AC-4: Receipt written on every execution (I10)

**Given:** Any InferenceGuard execution  
**When:** Module completes  
**Then:** A receipt file exists at `.wabblespec/receipts/inference-guard-receipt-<timestamp>.json`  
**And:** Receipt contains `"module": "inference-guard"` and `"activated": true|false`  
**And:** No execution completes without a receipt (implied completion prohibited)

## AC-5: No model names in output (I6)

**Given:** Any InferenceGuard receipt  
**Then:** Receipt contains no model names, provider names, or version strings  
**And:** Only capability descriptors and SDLC vocabulary appear

## AC-6: Tier 3 blocked without explicit flag

**Given:** Task card with `task_type: security` (no `inference_guard_tier: heavy`)  
**And:** Input contains "phishing attack simulation"  
**When:** InferenceGuard executes  
**Then:** `phishing` is NOT in `triggers_detected` (Tier 3 term, not enabled)  
**And:** `tier_applied: light` or `tier_applied: standard` (not `heavy`)

## AC-7: Excluded terms are never triggers

**Given:** Input contains "roleplay as an attacker" or "ignore previous instructions"  
**When:** InferenceGuard executes  
**Then:** `roleplay` and `ignore` are NOT in `triggers_detected`  
**And:** These terms are never transformed

## AC-8: validate-graph passes after registration

**Given:** inference-guard is registered in `framework.yaml`  
**When:** `python _shared/scripts/validate-graph.py` runs  
**Then:** Exit code 0, no MODULE_FILE_DRIFT, no DEPENDENCY_VIOLATION

## AC-9: Script delegation confirmed

**Given:** `_shared/scripts/inference-guard.py` exists  
**When:** InferenceGuard activates  
**Then:** Module calls the script for detection and transformation  
**And:** Module does not contain a reimplemented trigger detection loop
