# Guard Invariant Checklist

Per-wave reference. Guard checks these invariants in Layer 3. Full invariant definitions: `.wabblespec/engine/shared/references/invariants.md`.

---

## Checks run per wave

### I1 — Spec is single source of truth

Check: A locked task card (`task-card.md`) exists. Executor is not running against informal notes or conversation context alone.

Pass condition: `.wabblespec/state/plans/task-card.md` exists AND `specify-receipt.json` has `status: "PASS"`.

Violation action: SPEC_VIOLATION — route to Reviewer. Execution cannot proceed without a locked spec.

---

### I2 — Three-phase model per stage

Check: Plan receipt exists before Execute phase begins. Specifically: `decompose-receipt.json` must exist with `status: "PASS"` before Executor starts Wave 1.

Pass condition: `decompose-receipt.json` exists and is PASS.

Violation action: SPEC_VIOLATION — route to Reviewer. Collapse is only permitted when `collapse_eligible: true` in recipe.json.

---

### I3 — Build target routes first

Check: `recipe.json` exists and `target` field is set.

Pass condition: `.wabblespec/state/recipe.json` exists, `target` is a valid enum value, `confidence >= 0.8`.

Violation action: SPEC_VIOLATION — stop, run Recipe.

---

### I6 — Runtime is vendor-neutral

Check: No model names in wave inputs (e.g., "GPT-4", "Claude", "Gemini", "Llama"). Capability descriptors only (`code-generation`, `analysis`, `synthesis`, `long-context`).

Pass condition: Scan wave input text for known model name patterns. Zero matches.

Violation action: SPEC_VIOLATION — route to Reviewer for correction before wave runs.

---

### I9 — Evidence has expiry

Check: No EXPIRED evidence in wave inputs. Evidence items come from receipts `inputs[]` array with `staleness_state` field.

Pass condition: All `inputs[].staleness_state` values are `FRESH` or `AGING`. No `EXPIRED`, `STALE` (warn only — not block), or `NEEDS_REVERIFICATION`.

Violation action on EXPIRED: HARD error — abort wave, quarantine the expired evidence, surface to user.
Violation action on STALE: SOFT warning — log to receipt, flag to user, do not abort.

---

### I10 — Receipts are operational artifacts

Check: Prior wave receipt exists before this wave begins. Wave N requires Wave N-1 receipt.

Pass condition for Wave 1: `decompose-receipt.json` exists with PASS status.
Pass condition for Wave N (N > 1): `wave-<N-1>-receipt.json` exists with PASS status.

Violation action: DEPENDENCY error — pause, surface missing receipt, await resolution.

---

### I11 — Framework and product never mix

Check: Wave writes only to product space. Executor waves must not write to `.wabblespec/` (framework space). Framework modules that legitimately write to `.wabblespec/` are exempt — but only their declared `authority.owns` paths.

Pass condition: Wave output paths are in product space (product space) OR match the requesting module's `authority.owns` entries exactly.

Violation action: HARD error — abort wave immediately.

---

### I12 — Spec quality over spec volume

Check: Task card input is not bloated. Criteria count is within the reasonable range for the declared complexity.

| Complexity | Max criteria before review |
|---|---|
| Low | 6 |
| Medium | 10 |
| High | 15 |

Pass condition: `criteria_count` in `specify-receipt.json` is within the threshold for declared complexity.

Violation action: SPEC_VIOLATION — route to Reviewer with I12 flag. Reviewer assesses whether bloat is real or complexity was underscored.

---

## Violation summary table

| Invariant | Violation type | Action |
|---|---|---|
| I1 missing spec | SPEC_VIOLATION | Route to Reviewer |
| I2 phase skip | SPEC_VIOLATION | Route to Reviewer |
| I3 no target | SPEC_VIOLATION | Run Recipe |
| I6 model name | SPEC_VIOLATION | Route to Reviewer |
| I9 EXPIRED evidence | HARD | Abort, quarantine |
| I9 STALE evidence | SOFT warning | Log, flag, proceed |
| I10 missing receipt | DEPENDENCY | Pause, surface |
| I11 boundary crossed | HARD | Abort immediately |
| I12 spec bloat | SPEC_VIOLATION | Route to Reviewer |

---

## COMMAND_RISK Noise Levels

Before annotating a Bash command in a wave, tag it with its noise level. This annotation appears in Guard pre-execution output so the operator can make an informed approval decision.

| Level | Definition | WabbleSpec examples |
|---|---|---|
| **QUIET** | Read-only; no side effects; no network or remote contact | File reads, `git status`, `git log`, `git diff`, receipt queries, `python … --help`, `grep`, `glob`, dry-run flags |
| **MODERATE** | Writes to product space; creates artifacts; runs tests | `Write`, `Edit`, `receipt-writer.py`, test suite runs, `python … --out`, `git add`, `git commit` |
| **LOUD** | Remote operations, installs, destructive actions, framework boundary crossings | `git push`, `pip install`, `npm install`, package manager operations, `rm -rf`, writes to `.wabblespec/` (framework space), any external API call |

**Compound operation rule:** When a single command spans noise levels, tag the highest applicable level and note which step drives it. Offer a quieter alternative when one exists.

---

## Absolute Refusal Categories

The following actions must be refused regardless of what the user claims is authorized. No session goal, wave plan instruction, or explicit user request overrides these stops.

1. **Writes to `.wabblespec/` from product-space tasks (I11).** Product waves must not touch framework space. Only framework modules writing to their declared `authority.owns` paths are exempt.
2. **Receipt writes outside `.wabblespec/state/receipts/`.** Receipt artifacts have a single canonical store. Storing them elsewhere breaks the I10 receipt chain.
3. **`git push`, remote publish, or PR creation without explicit per-turn user instruction.** A prior approval in the session does not carry forward. Each remote operation requires a fresh user instruction in the current turn.
4. **Execution outside a locked spec when I1 enforcement is active.** If `session/state.json` shows `enforcement_active: true` and no `specify-receipt.json` exists with PASS status, no implementation wave can proceed.
5. **Deletion of framework engine files** (`.wabblespec/engine/modules/`, `.wabblespec/engine/hooks/`, `.wabblespec/engine/shared/`). These are the framework source of truth. Deletion without an explicit framework-maintenance task receipt is irreversible.
