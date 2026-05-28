# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Library-Package
**complexity:** Medium
**collapse_eligible:** false
**session_id:** phase2-script-delegation-20260528
**generated_at:** 2026-05-28T12:05:00Z

## Waves

### Wave 1: Audit and contract file

**inputs:**
- `.wabblespec/state/plans/task-card.md`
- All `.claude/skills/*/SKILL.md` files (read for audit — .claude/skills copies are live; engine/modules/ copies are source of truth)
- `.wabblespec/engine/shared/scripts/archive.py` (interface reference)
- `.wabblespec/engine/shared/scripts/receipt-writer.py` (interface reference)
- `.wabblespec/engine/shared/scripts/changelog-append.py` (interface reference)
- `.wabblespec/engine/shared/scripts/version-bump.py` (interface reference)

**outputs:**
- `.wabblespec/engine/shared/references/script-delegation-contract.md` (CREATE)
- Audit list in wave receipt: exact set of affected SKILL.md files with the specific step(s) in each that require replacement

**checkpoint:** `script-delegation-contract.md` exists at `.wabblespec/engine/shared/references/` and contains entries for all four scripts (`archive.py`, `receipt-writer.py`, `changelog-append.py`, `version-bump.py`), each with a complete CLI example invocation

**verification_command:** `python -c "c=open('.wabblespec/engine/shared/references/script-delegation-contract.md').read(); missing=[s for s in ['archive.py','receipt-writer.py','changelog-append.py','version-bump.py'] if s not in c]; print('PASS' if not missing else 'FAIL: '+str(missing))"`

**rollback_to:** null

**verification_mode:** Audit

---

### Wave 2: Rewrite affected SKILL.md files

**inputs:**
- Audit list from Wave 1 receipt (exact set of affected SKILL.md files)
- `.wabblespec/engine/shared/references/script-delegation-contract.md` (Wave 1 output)
- Each affected `engine/modules/*/SKILL.md` file (source of truth copies)
- Script interfaces from Wave 1 (archive.py, receipt-writer.py, changelog-append.py, version-bump.py)

**outputs:**
- N modified `engine/modules/*/SKILL.md` files (N from audit; expected 7–11), each with:
  - Manual write step(s) replaced by explicit `python .wabblespec/engine/shared/scripts/<script>.py` call with correct args
  - `## Reference Routing` section added (or updated) with entry pointing to `script-delegation-contract.md`
- `archive/SKILL.md` Steps 4–6b specifically: replaced with single `archive.py` invocation

**checkpoint:** Every SKILL.md in the audit list contains at least one `python .wabblespec/engine/shared/scripts/` call where manual write prose previously appeared; `archive/SKILL.md` contains no prose instructing direct writes to `CHANGELOG.md`, `VERSION`, or `receipt-index.json` in Steps 4–6b; every modified SKILL.md has a `## Reference Routing` section

**verification_command:** `python -c "
import glob, sys
skills = glob.glob('.wabblespec/engine/modules/**/SKILL.md', recursive=True)
fails = []
for p in skills:
    c = open(p).read()
    if 'python .wabblespec/engine/shared/scripts/' not in c:
        continue  # not an affected skill — skip
    if '## Reference Routing' not in c:
        fails.append(p + ': missing Reference Routing')
print('PASS' if not fails else 'FAIL\n' + '\n'.join(fails)); sys.exit(0 if not fails else 1)
"`

**rollback_to:** Wave 1 checkpoint

**verification_mode:** Audit

---

### Wave 3: Sync to .claude/skills/ and quality floor

**inputs:**
- All modified `engine/modules/*/SKILL.md` files (Wave 2 outputs)
- `.wabblespec/engine/scripts/wabblespec-sync-skills.py`
- `.wabblespec/engine/shared/scripts/quality-floor-check.py`

**outputs:**
- Updated `.claude/skills/*/SKILL.md` files (synced from engine/modules/)
- quality-floor-check output confirming modified modules still pass both gates

**checkpoint:** `wabblespec-sync-skills.py` exits 0; quality-floor-check passes for all modified modules; `.claude/skills/archive/SKILL.md` content matches `engine/modules/l7/archive/SKILL.md`

**verification_command:** `python .wabblespec/engine/scripts/wabblespec-sync-skills.py && python .wabblespec/engine/shared/scripts/quality-floor-check.py && git diff --name-only HEAD -- ".claude/skills/" | python -c "import sys; lines=[l.strip() for l in sys.stdin if l.strip()]; unexpected=[l for l in lines if not any(x in l for x in ['archive','verifier','executor','recipe','specify','decompose','changelog','scaffold','release','package','gateway-engineering','document'])]; print('AC6 PASS' if not unexpected else 'AC6 FAIL: '+str(unexpected)); sys.exit(0 if not unexpected else 1)"`

**rollback_to:** Wave 2 checkpoint

**verification_mode:** Test

---

## Rollback Map

| Wave | Rollback target | Trigger condition |
|---|---|---|
| Wave 1 fails | null (Wave 1 — no prior checkpoint) | HARD error or BLOCKED after 3 REVISE cycles |
| Wave 2 fails | Wave 1 checkpoint | HARD error or BLOCKED after 3 REVISE cycles |
| Wave 3 fails | Wave 2 checkpoint | sync or quality-floor-check exits non-zero after 3 REVISE cycles |
