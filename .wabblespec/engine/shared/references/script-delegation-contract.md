---
name: script-delegation-contract
description: Canonical mapping of every standard framework write operation to its script call. Skills MUST call these scripts instead of performing manual file I/O for CHANGELOG, VERSION, receipt-index, and receipt JSON writes.
---

# Script Delegation Contract

Framework write operations — CHANGELOG append, VERSION bump, receipt-index update, and pipeline receipt JSON construction — are mechanically deterministic. These operations MUST be performed by calling the appropriate script rather than by Claude constructing file content inline. This contract is authoritative for all affected skills.

**Rule:** If an operation appears in this contract, the skill's "How to do it" steps MUST delegate to the listed script. Prose instructions to directly append, write, or construct the artifact are a defect.

---

## Operations and Scripts

### 1. Full Archive Close — `archive.py`

**Replaces:** Steps that instruct Claude to append CHANGELOG.md, bump VERSION, write delivery receipt, and update receipt-index.json as four separate operations.

**Why:** The CHANGELOG file exceeds 98 KB. Reading it into context to append is a 24 000-token cost that occurs on every Archive run. `archive.py` appends in write-only mode — the file is never read into context.

**Canonical call:**

```bash
python .wabblespec/engine/shared/scripts/archive.py \
  --session-id <session-id> \
  --task-id <task-id> \
  --summary "<one-sentence description of what was built>" \
  --delta-class ADDITIVE|COSMETIC|BREAKING \
  --files-delivered "<path1>" "<path2>" \
  --waves-completed <N>
```

**Claude provides:** `--session-id`, `--task-id`, `--summary` (reasoning-dependent), `--delta-class` (derived from wave receipts), `--files-delivered`, `--waves-completed`.

**Script handles:** CHANGELOG append (write-only, never reads existing), VERSION semver bump, delivery receipt JSON write, receipt-index.json patch.

**Optional flags:**

```bash
# Pass extra fields into the delivery receipt
--extra '{"total_receipts_accumulated": 102}'

# Dry run — print what would be written, touch nothing
--dry-run

# Pass not-tested items
--not-tested "item A" "item B"
```

**Exit codes:** 0 = success, 1 = logical failure, 2 = required file missing.

---

### 2. Pipeline Receipt Construction — `receipt-writer.py`

**Replaces:** Steps that instruct Claude to construct a receipt JSON object inline and write it to `.wabblespec/state/receipts/`.

**Why:** Receipt schemas have 10–15 required fields. Claude re-derives the required set each invocation (~300–1 000 tokens). `receipt-writer.py` enforces the schema and handles serialization.

**Supported types:** `verifier`, `executor`, `recipe`, `specify`, `decompose`.

**Canonical calls by type:**

```bash
# Verifier receipt (Step 5 of Verifier)
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type verifier \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS|FAIL|PARTIAL \
  --wave <N> --wave-of <total> \
  --check "V-01:PASS:File exists at declared path" \
  --check "V-02:PASS:All acceptance criteria Then-clauses verified" \
  --verified-at <ISO-8601> \
  --out .wabblespec/state/receipts/verification-wave-<N>-<timestamp>.json

# Executor wave receipt (Step 5 of Executor, per wave)
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type executor \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --wave <N> --wave-of <total> \
  --modules-activated <layer/module> \
  --files-written "<path1>" "<path2>" \
  --delta-class ADDITIVE|COSMETIC|BREAKING \
  --summary "<what this wave produced>" \
  --out .wabblespec/state/receipts/wave-<N>-receipt.json

# Recipe receipt (Step 5 of Recipe)
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type recipe \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --target <target> --platform <platform> \
  --complexity Low|Medium|High \
  --confidence <0.0-1.0> \
  --detection-method <method> \
  --out .wabblespec/state/receipts/recipe-receipt.json

# Specify receipt (Step 5 of Specify)
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type specify \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --requirements "AC1: <criterion>" "AC2: <criterion>" \
  --out .wabblespec/state/receipts/specify-receipt.json

# Decompose receipt (Step 7 of Decompose)
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type decompose \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --waves-json '[{"id":1,"label":"<name>","verification_mode":"Audit"}]' \
  --out .wabblespec/state/receipts/decompose-receipt.json
```

**Print to stdout instead of writing (for inspection):**

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py --type verifier ... --out -
```

**Exit codes:** 0 = success, 1 = bad arguments or schema failure, 2 = output path not writable.

---

### 3. Standalone CHANGELOG Append — `changelog-append.py`

**Use when:** A skill needs to append a changelog entry independently of Archive (e.g., a release notes pipeline that runs outside the standard Archive close).

**Note:** If Archive (`archive.py`) is already in the call chain, do NOT also call `changelog-append.py` — `archive.py` invokes it internally.

```bash
python .wabblespec/engine/shared/scripts/changelog-append.py \
  --version <semver> \
  --timestamp <ISO-8601> \
  --changed "Added X" "Added Y" \
  --fixed "Fixed Z" \
  --not-tested "item A" \
  --delivery-receipt ".wabblespec/state/receipts/delivery-receipt-<id>.json" \
  --waves-planned <N> \
  --waves-completed <N> \
  --waves-failed 0

# Minimal form — only version and timestamp are required:
python .wabblespec/engine/shared/scripts/changelog-append.py \
  --version 0.28.0 \
  --timestamp 2026-05-28T12:00:00Z \
  --body "Raw markdown body text"

# From a delivery receipt:
python .wabblespec/engine/shared/scripts/changelog-append.py \
  --from-receipt .wabblespec/state/receipts/delivery-receipt-<id>.json
```

**Exit codes:** 0 = appended, 1 = bad arguments, 2 = CHANGELOG not found or not writable.

---

### 4. Standalone VERSION Bump — `version-bump.py`

**Use when:** A skill needs to bump the version independently of Archive.

**Note:** If Archive (`archive.py`) is already in the call chain, do NOT also call `version-bump.py` — `archive.py` invokes it internally.

```bash
# Bump by delta class:
python .wabblespec/engine/shared/scripts/version-bump.py --bump ADDITIVE
python .wabblespec/engine/shared/scripts/version-bump.py --bump BREAKING
python .wabblespec/engine/shared/scripts/version-bump.py --bump COSMETIC

# Show current version without changing it:
python .wabblespec/engine/shared/scripts/version-bump.py --show

# Force a specific version:
python .wabblespec/engine/shared/scripts/version-bump.py --set 1.0.0
```

**Delta-class mapping:** BREAKING → major (or minor during 0.x.y pre-stabilization), ADDITIVE → minor, COSMETIC → patch.

**Exit codes:** 0 = success, 1 = bad arguments, 2 = VERSION file missing or unparseable.

---

## Affected Skills Reference

| Skill | Layer | Steps delegated | Script |
|---|---|---|---|
| archive | L7 | Steps 4–6b (CHANGELOG, VERSION, delivery receipt, receipt-index) | `archive.py` |
| verifier | L2 | Step 5 (verification receipt) | `receipt-writer.py --type verifier` |
| executor | L2 | Step 5 per wave (wave receipt) + final (execution receipt) | `receipt-writer.py --type executor` |
| recipe | L0 | Step 5 (recipe receipt) | `receipt-writer.py --type recipe` |
| specify | L1 | Step 5 (specify receipt) | `receipt-writer.py --type specify` |
| decompose | L1 | Step 7 (decompose receipt) | `receipt-writer.py --type decompose` |
| scaffold | L7 | Step 6 (scaffold receipt) | `receipt-writer.py --type scaffold` |
| package | L7 | Step 6 (package receipt) | `receipt-writer.py --type package` |
| release | L7 | Step 6 (release receipt) | `receipt-writer.py --type release` |
| monitor | L7 | Step 7 (monitor receipt) | `receipt-writer.py --type monitor` |
| deploy | L7 | Step 6 (deploy receipt) | `receipt-writer.py --type deploy` |
| adversary | L2 | Step 3 (adversary receipt) | `receipt-writer.py --type adversary` |
| grader | L2 | Step 5 (grader receipt) | `receipt-writer.py --type grader` |
| nexus | L5 | Step 5 (nexus receipt) | `receipt-writer.py --type nexus` |
| brainstorm | L1 | Step 4 (brainstorm receipt) | `receipt-writer.py --type brainstorm` |
| enhance | L1 | Step 5 (enhance receipt) | `receipt-writer.py --type enhance` |
| sharpen | L1 | Step 5 (sharpen receipt) | `receipt-writer.py --type sharpen` |
| audit | L2 | Step 7 (audit receipt) | `receipt-writer.py --type audit` |

| ref-eval | L2 | Receipt write | `receipt-writer.py --type ref-eval` |
| ref-comp | L2 | Receipt write | `receipt-writer.py --type ref-comp` |
| ref-plan | L2 | Receipt write | `receipt-writer.py --type ref-plan` |

## Non-Delegated Receipt Types

**None.** All 100 WabbleSpec skills are fully delegated. receipt-writer.py covers 20 types.

---

### 5. Task Card Write — `task-card-writer.py`

**Use when:** Specify needs to produce `task-card.md`. Claude provides goal, target, complexity, change class, non-goals, assumptions, and criteria text.

```bash
python .wabblespec/engine/shared/scripts/task-card-writer.py \
  --session-id <session-id> \
  --goal "<one sentence, falsifiable>" \
  --target <target> \
  --complexity Low|Medium|High \
  --change-class ADDITIVE|COSMETIC|BREAKING \
  --non-goal "Item 1" --non-goal "Item 2" \
  --assumption "Assumption text" \
  --criterion "AC1|short name|Given ...|When ...|Then ..." \
  --out .wabblespec/state/plans/task-card.md
```

**Exit codes:** 0 = written, 1 = validation failure, 2 = path not writable.

---

### 6. Wave Plan Write — `wave-plan-writer.py`

**Use when:** Decompose needs to produce `current-wave-plan.md`. Claude provides wave names, inputs, outputs, checkpoints, and verification commands as JSON.

```bash
python .wabblespec/engine/shared/scripts/wave-plan-writer.py \
  --session-id <session-id> \
  --target <target> \
  --complexity Low|Medium|High \
  --wave '{"name":"Wave name","inputs":["in"],"outputs":["out"],"checkpoint":"condition","rollback_to":null,"verification_mode":"Audit","verification_command":"python -c \"print(1)\""}' \
  --out .wabblespec/state/plans/current-wave-plan.md
```

**Exit codes:** 0 = written, 1 = validation failure, 2 = path not writable.

---

### 7. Scope Write — `scope-writer.py`

**Use when:** ScopeFrame needs to produce `scope.md`. Claude provides in-scope items, out-of-scope items, and assumptions.

```bash
python .wabblespec/engine/shared/scripts/scope-writer.py \
  --session-id <session-id> \
  --target <target> \
  --complexity Low|Medium|High \
  --in-scope "Item 1" --in-scope "Item 2" \
  --out-of-scope "Excluded item" \
  --assumption "Assumption text" \
  --out .wabblespec/state/scope.md
```

**Exit codes:** 0 = written, 1 = validation failure, 2 = path not writable.

---

### 8. Receipt Chain Validation — `guard-check.py chain`

**Use when:** Guard (or any module) needs to verify the receipt chain is complete for a session before proceeding.

```bash
python .wabblespec/engine/shared/scripts/guard-check.py chain \
  --session-id <session-id> \
  --waves <N> \
  [--receipts-dir .wabblespec/state/receipts/] \
  [--json]
```

**Exit codes:** 0 = PASS (all required receipts present), 1 = FAIL (missing receipts listed), 2 = configuration error.

---

## Cross-references

- Script source: `.wabblespec/engine/shared/scripts/archive.py`
- Script source: `.wabblespec/engine/shared/scripts/receipt-writer.py`
- Script source: `.wabblespec/engine/shared/scripts/changelog-append.py`
- Script source: `.wabblespec/engine/shared/scripts/version-bump.py`
- Script source: `.wabblespec/engine/shared/scripts/task-card-writer.py`
- Script source: `.wabblespec/engine/shared/scripts/wave-plan-writer.py`
- Script source: `.wabblespec/engine/shared/scripts/scope-writer.py`
- Receipts schema: `.wabblespec/engine/shared/schemas/`
- Archive skill: `.wabblespec/engine/modules/l7/archive/SKILL.md`
