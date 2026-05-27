# WabbleSpec Defect Taxonomy

Named defect cards for framework-specific failures. Used by Triage (classification), Guard (invariant checking), and Verifier (post-wave validation). Each card: symptom → detection → fix path → test.

Scope: WabbleSpec framework defects only. General software bugs (null access, off-by-one, etc.) use standard Bug routing without a defect card.

---

## Defect Card Index

| ID | Name | Severity default | Owner module |
|---|---|---|---|
| WD-001 | RECEIPT_MISSING_FIELDS | High | Triage → Executor |
| WD-002 | SCOPE_NOT_CONFIRMED | High | Triage → ScopeFrame |
| WD-003 | INVARIANT_VIOLATION | High | Guard → Triage |
| WD-004 | STALE_DRAWER_CITED | Medium | Triage → Memory |
| WD-005 | WAVE_CHECKPOINT_MISSING | High | Triage → Executor |
| WD-006 | ECONOMY_CAPTURE_SKIPPED | Medium | Triage → Executor |
| WD-007 | ACTIVATION_ORDER_VIOLATION | High | Triage → re-entry point |
| WD-008 | HOOK_NOT_WIRED | Critical | Triage → Executor |

Recurrence escalation from Triage SKILL.md applies: second occurrence escalates severity one level, third+ escalates to High minimum.

---

## WD-001 — RECEIPT_MISSING_FIELDS

**Symptom:** Receipt validation fails. Downstream module cannot read a required field. Receipt schema check in `/wabble-health` Check 1.3 returns FAIL.

**Detection:**
```bash
# Validate against base schema:
cat .wabblespec/receipts/<module>-receipt.json | python3 -c "
import sys, json, jsonschema, pathlib
receipt = json.load(sys.stdin)
schema = json.loads(pathlib.Path('.wabblespec/engine/shared/schemas/receipt.base.schema.json').read_text())
jsonschema.validate(receipt, schema)
print('PASS')
"
# Or: run /wabble-health — Check 1.3 samples 10 most recent receipts
```

**Fix path:** Identify which module wrote the incomplete receipt (check `module` field or filename). Re-run that module. Verify receipt fields against `receipt.base.schema.json` before proceeding.

**Test:** `/wabble-health` Check 1.3 returns PASS. Receipt validator exits 0.

**Triage route:** Bug → Medium (single) / High (recurrence). Route: Specify (delta) → Executor.

---

## WD-002 — SCOPE_NOT_CONFIRMED

**Symptom:** ScopeFrame receipt has `user_confirmed: false` or field absent. `scope.md` lacks `locked_at`. Downstream modules ran without locked scope.

**Detection:**
```bash
cat .wabblespec/receipts/scopeframe-receipt.json | python3 -c "
import sys, json
r = json.load(sys.stdin)
if not r.get('user_confirmed', False):
    print('FAIL: user_confirmed not true')
    sys.exit(1)
print('PASS')
"
```

**Fix path:** Do not proceed. Re-run ScopeFrame from Step 3 (present for confirmation). Do not write receipt until user explicitly confirms. Any downstream receipts from the unconfirmed session are suspect — review for scope drift.

**Test:** `scopeframe-receipt.json` has `"user_confirmed": true`. `scope.md` has non-empty `locked_at` field.

**Triage route:** Bug → High. Route: ScopeFrame re-entry (Step 3) → user confirmation → re-lock.

---

## WD-003 — INVARIANT_VIOLATION

**Symptom:** Guard receipt contains non-empty `violations[]` array. Executor proceeded despite Guard FAIL, OR Guard was not run before Executor in current wave.

**Detection:**
```bash
cat .wabblespec/receipts/guard-receipt.json | python3 -c "
import sys, json
r = json.load(sys.stdin)
v = r.get('violations', [])
if v:
    print(f'FAIL: {len(v)} violation(s):')
    for vi in v:
        print(f'  - {vi}')
    sys.exit(1)
print('PASS')
"
```

**Fix path:**
1. Identify violated invariant by ID (e.g., I3, I12) from the violations array
2. Read `.wabblespec/engine/shared/references/invariants.md` for that invariant's definition
3. Fix the root cause — do not suppress the violation
4. Re-run Guard; verify `violations: []` before Executor proceeds

**Test:** Re-run Guard on the same wave inputs. `violations: []` in receipt. Guard receipt status = PASS.

**Triage route:** Bug → High (any violation). Route: Guard re-run → fix → Guard re-run → Executor. Critical if violation is I1 (safety) or I2 (no hallucination).

---

## WD-004 — STALE_DRAWER_CITED

**Symptom:** Module output or spec cites a Memory drawer whose `staleness` state is EXPIRED or NEEDS_REVERIFICATION. Evidence at `evidence_paths` no longer matches the claimed standard.

**Detection:**
```bash
# /wabble-health Check 3.1 reports EXPIRED drawer count
# Manual check: query Memory for cited drawer ID
# Verify: does the evidence file still show the claimed pattern?
```

**Fix path:**
1. Load the cited drawer from Memory
2. Navigate to each path in `evidence_paths`
3. If pattern still present: update staleness to FRESH, update `last_verified`
4. If pattern gone or changed: mark drawer NEEDS_REVERIFICATION; do not cite until re-verified
5. If evidence path does not exist: invalidate drawer; remove citation from output

**Test:** `/wabble-health` Check 3.1 returns 0 EXPIRED drawers. Re-read the drawer — `staleness: FRESH`.

**Triage route:** Bug → Medium (single EXPIRED drawer). Route: Memory update → re-cite or remove citation.

---

## WD-005 — WAVE_CHECKPOINT_MISSING

**Symptom:** Wave completed successfully, but expected checkpoint directory absent from `.wabblespec/checkpoints/<wave-id>/`. Rollback to this wave is impossible.

**Detection:**
```bash
# Check checkpoint exists for completed wave:
ls .wabblespec/checkpoints/<wave-id>/
# Expected: directory with copied artifacts

# From wave plan: rollback_to field names the wave-id
```

**Fix path:**
1. If wave outputs are still intact: write checkpoint now by copying wave output artifacts to `.wabblespec/checkpoints/<wave-id>/`
2. If wave outputs are partial or corrupted: rollback is not possible — escalate to user, identify last safe state
3. Add checkpoint write step to wave plan before proceeding to next wave

**Test:** `.wabblespec/checkpoints/<wave-id>/` exists and contains expected wave output artifacts.

**Triage route:** Bug → High (rollback impossible). Route: Executor (write checkpoint) or user escalation if state is unrecoverable.

---

## WD-006 — ECONOMY_CAPTURE_SKIPPED

**Symptom:** Large output (> 2000 tokens) pasted inline in receipt or module output without a capture citation. Receipt missing `captures[]` array. Economy Rule 2 violated. Context flooded.

**Detection:**
```bash
# Estimate: 1 token ≈ 4 chars English prose, ≈ 3 chars code
# If inline output > 8000 chars: likely > 2000 tokens
# Check receipt for captures array:
cat .wabblespec/receipts/<module>-receipt.json | python3 -c "
import sys, json
r = json.load(sys.stdin)
captures = r.get('captures', [])
print(f'captures: {captures}')
"
```

**Fix path:**
1. Write the large output retrospectively to `.wabblespec/captures/<module>-<timestamp>.txt`
2. Update the receipt `captures[]` array with the capture path and summary
3. Replace the inline output with the Economy Rule 2 citation format: `[captured: <path> — <N> tokens — <summary>]`

**Test:** Receipt has non-empty `captures[]`. Inline citation references the capture file path. File exists at declared path.

**Triage route:** Bug → Medium. Route: Specify (delta for receipt) → Executor (write capture, update receipt).

---

## WD-007 — ACTIVATION_ORDER_VIOLATION

**Symptom:** Module ran before its prerequisite completed. Common patterns: Specify before ScopeFrame confirmed; Executor before Verifier signed off on prior wave; Archive before all wave receipts written.

**Detection:**
```bash
# Check receipt timestamps — prerequisite receipt must precede dependent receipt
python3 -c "
import json, pathlib, datetime

def read_ts(path):
    r = json.loads(pathlib.Path(path).read_text())
    return r.get('timestamp', '')

prereq = read_ts('.wabblespec/receipts/scopeframe-receipt.json')
dependent = read_ts('.wabblespec/receipts/specify-receipt.json')

if prereq < dependent:
    print('PASS: order correct')
else:
    print(f'FAIL: specify ran before scopeframe (scopeframe: {prereq}, specify: {dependent})')
"
```

**Fix path:**
1. Identify the earliest module that ran out of order
2. Re-run from that module forward in correct sequence
3. Invalidate any receipts produced out of order — they may contain scope drift
4. Do not proceed until prerequisite receipts all precede dependent receipts

**Test:** Receipt timestamps in prerequisite → dependent order. All receipts in session reflect the correct sequence.

**Triage route:** Bug → High. Route: re-entry at violated prerequisite → re-run forward.

---

## WD-008 — HOOK_NOT_WIRED

**Symptom:** `hooks/pre-tool-use-receipt-check.py` missing OR not referenced in `.claude/settings.json`. Receipt checking not enforced. Modules can execute without receipts.

**Detection:**
```bash
# /wabble-health Check 4.2 — FAIL if either condition true
# Manual:
Test-Path hooks\pre-tool-use-receipt-check.py   # must be True
python3 -c "
import json, pathlib
settings = json.loads(pathlib.Path('.claude/settings.json').read_text())
hooks = settings.get('hooks', {})
pre_tool = hooks.get('PreToolUse', [])
hook_scripts = [h.get('matcher', '') + str(h) for h in pre_tool]
print('wired' if any('receipt-check' in s for s in hook_scripts) else 'NOT WIRED')
"
```

**Fix path:**
1. If hook file missing: restore from `.wabblespec/engine/shared/hooks/` or re-implement per hook specification
2. If file exists but not in settings: add to `.claude/settings.json` under `PreToolUse` hooks
3. Verify hook fires on next tool use: check for hook output in subsequent tool calls

**Test:** `/wabble-health` Check 4.2 returns PASS. Hook file present. `settings.json` references it.

**Triage route:** Bug → Critical (receipt enforcement completely absent). Route: Executor (immediate wave) — restore hook before any further module execution.

---

## Symptom-to-Defect Quick Map

| Symptom | Check first |
|---|---|
| Receipt validation error / schema mismatch | WD-001 |
| scope.md has no `locked_at` / module ran before scope confirmed | WD-002 |
| Guard receipt non-empty violations array | WD-003 |
| EXPIRED drawer cited as evidence | WD-004 |
| Rollback target checkpoint directory missing | WD-005 |
| Context flooded with large output, no capture citation | WD-006 |
| Module receipt timestamp precedes prerequisite receipt | WD-007 |
| `/wabble-health` Check 4.2 FAIL / no hook output | WD-008 |

---

## What this taxonomy does not cover

General software bugs in target projects (null access, off-by-one, async race, type coercion, etc.) do not get Wabble defect cards. Those use standard Bug routing without a WD-prefix classification. Assign a WD card only when the defect is a WabbleSpec framework failure — receipt, scope, guard, memory, checkpoint, economy, activation order, or hook integrity.
