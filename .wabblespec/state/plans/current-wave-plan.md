# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Framework
**complexity:** High
**collapse_eligible:** false
**session_id:** foundation-hardening-20260528
**generated_at:** 2026-05-28T13:34:20Z
**revised_at:** 2026-05-28T13:48:49Z (Reviewer cycle 0 → REVISE: verification layer hardened); 2026-05-28T13:55:00Z (Reviewer cycle 1 → REVISE: independent assertions corrected against real file shapes and empirically tested)
**strategy:** Option 2 — Fix + Permanent Drift Gate (selected via Propose 2026-05-28)
**verification_shell:** bash (all verification_command entries run under bash via the Bash tool, not PowerShell; temp files are repo-relative under .wabblespec/state/receipts/_v_*)
**high_tier_scope:** H1, H2, H3, H4, H5, H6, H7, H8, H10. **H9 (unit-test harness for the 42 scripts) is a deferred non-goal** (fast-follow), excluded from "high-tier fixed."

## Findings of note discovered during planning/review (feed Executor)

- **H1 is larger than the audit framing:** 17 of 20 receipt builders emit no top-level numeric `confidence` (only `recipe`, `ref-eval`, `ref-comp` comply). Wave 1's confidence unification must touch all of: verifier, executor, specify, decompose, scaffold, package, release, monitor, deploy, adversary, grader, nexus, brainstorm, enhance, sharpen, audit, ref-plan. (`grader` legitimately also has a separate `score` field — that is its verdict grade, distinct from base `confidence`; keep both.)
- **`receipt-writer.py --validate` does not currently enforce the base schema's required `confidence`** (receipts lacking it still validate PASS). Therefore AC3 is verified by an explicit field check, NOT by `--validate`. Wave 1 should also tighten `--validate` to enforce base-required fields, but the gate does not rely on that.

## Doctor exit-code contract (defined here, implemented in Wave 2)

- `wabblespec-doctor.py --all` → **exit 0 on successful enumeration** regardless of findings (findings reported in the output payload). This is AC1's "command exits 0, executes all 28 checks." M/L findings remaining RED never break this run.
- `wabblespec-doctor.py --severity {critical,high,medium,low}` → **exit nonzero iff any check of that severity is failing**; exit 0 when all pass. Pass/fail gate for fix waves.
- `wabblespec-doctor.py --guard-advisory` → **always exit 0** (non-blocking), findings printed to stdout.
- `--format json` payload shape: `{"checks":[{"id","severity","status"}...]}` where id ∈ {C1..C4, H1..H10, M*, L*} and status ∈ {PASS, FAIL}.

## Waves

### Wave 1: Contract & schema foundation

**inputs:** [task-card.md AC2/AC3, findings H1/H2/H4/H8, engine/shared/schemas/, receipt-writer.py]
**outputs:** [recipe.schema.json, wave-queue.schema.json, delivery-receipt.schema.json; receipt-writer.py `propose` builder + `--options-path` flag in build_brainstorm; `confidence` field emitted by ALL 20 builders (back-compat reads of legacy `confidence_score`/`score`); `--validate` tightened to enforce base-required fields]
**checkpoint:** Three schema files are well-formed JSON Schema docs; a freshly written propose receipt and a brainstorm receipt (with populated `options_path`) write and `--validate`; and EVERY one of the 20 receipt types emits a top-level numeric `confidence` in [0,1].
**rollback_to:** null
**verification_mode:** Test
**verification_command:**
```bash
bash -c 'set -e
for s in recipe wave-queue delivery-receipt; do
  python -c "import json; d=json.load(open(\".wabblespec/engine/shared/schemas/$s.schema.json\")); assert isinstance(d,dict) and (\"properties\" in d or \"\$schema\" in d)"
done
P=.wabblespec/state/receipts/_v_propose.json; B=.wabblespec/state/receipts/_v_brain.json
python .wabblespec/engine/shared/scripts/receipt-writer.py --type propose   --task-id t --session-id s --status PASS --confidence 0.9 --out "$P"
python .wabblespec/engine/shared/scripts/receipt-writer.py --type brainstorm --task-id t --session-id s --status PASS --confidence 0.9 --options-path X.md --out "$B"
python .wabblespec/engine/shared/scripts/receipt-writer.py --validate "$P"
python .wabblespec/engine/shared/scripts/receipt-writer.py --validate "$B"
grep -q "\"options_path\": \"X.md\"" "$B"
for t in verifier executor recipe specify decompose scaffold package release monitor deploy adversary grader nexus brainstorm enhance sharpen audit ref-eval ref-comp ref-plan; do
  python .wabblespec/engine/shared/scripts/receipt-writer.py --type "$t" --task-id t --session-id s --status PASS --confidence 0.9 --out - \
   | python -c "import sys,json; d=json.load(sys.stdin); assert isinstance(d.get(\"confidence\"),(int,float)) and 0<=d[\"confidence\"]<=1, \"$t\""
done
rm -f "$P" "$B"'
```

---

### Wave 2: Build wabblespec-doctor.py

**inputs:** [Wave 1 schemas, task-card.md AC1, .wabblespec/brainstorm/options-20260528T125658Z.md]
**outputs:** [wabblespec-doctor.py implementing the exit-code contract; checks for C1-C4, H1-H10, M/L tier; a schema-validity check that validates recipe.json against recipe.schema.json and a generated wave-queue file against wave-queue.schema.json (covers config-schema half of AC2); a `--self-test` mode that validates bundled good AND malformed fixtures (engine/shared/scripts/tests/fixtures/{good,bad}-{recipe,wave-queue}.json) for each schema, asserting good→PASS and bad→FAIL; the fixtures themselves (this is the doctor's own validator self-test, NOT the deferred 42-script harness H9)]
**checkpoint:** `--all --format json` exits 0 and enumerates ≥28 checks; baseline reports the SPECIFIC seeded critical findings (C1,C2,C3,C4) as FAIL — proving the checks detect real defects rather than passing vacuously; AND `--self-test` exits 0, confirming each schema validator accepts the good fixture and rejects the malformed one (RV-A2: schema check is provably non-vacuous).
**rollback_to:** Wave 1 checkpoint
**verification_mode:** Test
**verification_command:**
```bash
bash -c 'set -e
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --self-test
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all >/dev/null
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all --format json \
 | python -c "import sys,json; d=json.load(sys.stdin); ch=d[\"checks\"]; assert len(ch)>=28, len(ch); ids={c[\"id\"] for c in ch}; need={\"C1\",\"C2\",\"C3\",\"C4\",\"H1\",\"H2\",\"H3\",\"H4\",\"H5\",\"H6\",\"H7\",\"H8\",\"H10\"}; assert need<=ids, need-ids; crit={c[\"id\"]:c[\"status\"] for c in ch if c.get(\"severity\")==\"critical\"}; assert any(v!=\"PASS\" for v in crit.values()), \"baseline must detect critical findings\"; print(\"checks=%d named-present detects-critical=OK\"%len(ch))"'
```

---

### Wave 3: Critical fixes (C1-C4)

**inputs:** [Wave 2 doctor, AC4/AC5/AC6, receipt-index.json, archive.py, CLAUDE.md, .claude/skills/, wabblespec.yaml]
**outputs:** [receipt-index.json regenerated (all delivery_receipt_path under state/receipts/, all resolve); platform module ids in wabblespec.yaml aligned to the short-form skill dir names + sync script corrected; archive.py wabble-sound.py path fixed; CLAUDE.md → 0.45.0 / 103 modules]
**checkpoint:** `--severity critical` exits 0 AND four independent assertions pass (each reads the underlying artifact directly, not the doctor): C1 receipt-index has no `.wabblespec/receipts/` prefix and every `tasks[].delivery_receipt_path` resolves; C2 every `platform-*` id in wabblespec.yaml has an exactly-matching `.claude/skills/` dir; C3 the broken `"_shared","scripts","wabble-sound.py"` string is gone from archive.py; C4 CLAUDE.md states 0.45.0 + 103 and no longer 0.39.0.
**rollback_to:** Wave 2 checkpoint
**verification_mode:** Test
**verification_command:**
```bash
bash -c 'set -e
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --severity critical
python -c "import json,os,sys; idx=json.load(open(\".wabblespec/state/archive/receipt-index.json\")); ps=[t.get(\"delivery_receipt_path\",\"\") for t in idx[\"tasks\"]]; assert all(\".wabblespec/receipts/\" not in p for p in ps); sys.exit(1 if [p for p in ps if p and not os.path.exists(p)] else 0)"
python -c "import os,re,sys; ids=[m.group(1) for m in (re.match(r\"\s*-\s*id:\s*(platform-[a-z-]+)\",l) for l in open(\".wabblespec/wabblespec.yaml\",encoding=\"utf-8\")) if m]; sys.exit(1 if [i for i in ids if not os.path.isdir(os.path.join(\".claude/skills\",i))] else 0)"
! grep -q "\"_shared\", \"scripts\", \"wabble-sound.py\"" .wabblespec/engine/shared/scripts/archive.py
grep -q "wabble-sound.py" .wabblespec/engine/shared/scripts/archive.py
test -f .wabblespec/engine/shared/scripts/wabble-sound.py
python -c "import re,sys; cm=open(\"CLAUDE.md\",encoding=\"utf-8\").read(); ver=open(\".wabblespec/VERSION\").read().strip(); m=re.search(r\"Current version[:*\s]*([0-9]+\.[0-9]+\.[0-9]+)\",cm); assert m and m.group(1)==ver, (m and m.group(1),ver); assert re.search(r\"103 (skill )?modules\",cm), \"103 modules\""'
```

---

### Wave 4: High-tier fixes (H1-H8,H10; H9 deferred)

**inputs:** [Wave 2 doctor, high-tier in-scope, findings H3/H5/H6/H7/H10 (H1/H2/H4/H8 closed Wave 1)]
**outputs:** [CLI unified to --delta-class in task-card-writer.py + archive.py; entity graph regenerated over all current drawers; CLAUDE.md script-location section corrected (l5/*/scripts/); orphan templates registered-with-owner or removed-with-provenance; memory-bootstrap duplication resolved]
**checkpoint:** `--severity high` exits 0; `--all` exits 0 enumerating ≥28 checks with all critical AND high checks PASS (post-fix full-run green, satisfying AC1 + high-tier ACs); independent grep confirms `--delta-class` present in both scripts and `--change-class` gone from task-card-writer.py.
**rollback_to:** Wave 3 checkpoint
**verification_mode:** Test
**verification_command:**
```bash
bash -c 'set -e
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --severity high
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all >/dev/null
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all --format json \
 | python -c "import sys,json; ch=json.load(sys.stdin)[\"checks\"]; assert len(ch)>=28; assert all(c[\"status\"]==\"PASS\" for c in ch if c.get(\"severity\") in (\"critical\",\"high\")), \"crit/high not green\"; print(\"crit+high PASS\")"
grep -q -- "--delta-class" .wabblespec/engine/shared/scripts/archive.py .wabblespec/engine/shared/scripts/task-card-writer.py
! grep -q -- "--change-class" .wabblespec/engine/shared/scripts/task-card-writer.py'
```

---

### Wave 5: Wire doctor as advisory gate

**inputs:** [Wave 2 doctor, AC7, .wabblespec/state/daemons/daemon-config.json, Guard module + guard-check.py]
**outputs:** [daemon-config.json gains a wabblespec-doctor job on the on_archive trigger; Guard gains an advisory (non-blocking) doctor layer exposed via guard-check.py --advisory-doctor]
**checkpoint:** daemon-config contains the doctor on_archive job; a real advisory invocation through the Guard path surfaces doctor findings in its output AND exits 0 (non-blocking) — proven by exercising guard-check's doctor layer, not by grepping config text alone.
**rollback_to:** Wave 4 checkpoint (git worktree)
**verification_mode:** Demonstration
**verification_command:**
```bash
bash -c 'set -e
python -c "import json; c=json.load(open(\".wabblespec/state/daemons/daemon-config.json\")); s=json.dumps(c); assert \"wabblespec-doctor\" in s and \"on_archive\" in s, \"doctor on_archive job missing\""
if OUT=$(python .wabblespec/engine/shared/scripts/guard-check.py --advisory-doctor 2>&1); then RC=0; else RC=$?; fi
test $RC -eq 0
echo "$OUT" | grep -Eq "(C|H|M|L)[0-9]+|FAIL|PASS|finding"'
```

---

## Rollback Map

| Trigger | Rollback target | Condition |
|---|---|---|
| Wave 1 fails | null (re-run from clean) | schema not well-formed, a --validate fails, options_path absent, or any builder lacks a clean confidence field |
| Wave 2 fails | Wave 1 checkpoint | doctor cannot enumerate ≥28 checks, crashes, or baseline does not detect the seeded critical findings |
| Wave 3 fails | Wave 2 checkpoint | HARD error, critical RED after 3 REVISE cycles, or an independent C1/C2/C3/C4 assertion fails |
| Wave 4 fails | Wave 3 checkpoint | HARD error, high RED after 3 REVISE cycles, or full-run crit+high not all green |
| Wave 5 fails | Wave 4 checkpoint (git worktree) | Guard edit breaks enforcement, advisory path blocks (exit ≠ 0), or findings not surfaced |

## Notes

- **Verification shell is bash**; temp files repo-relative under `.wabblespec/state/receipts/_v_*` (cleaned up).
- **Circularity broken with empirically-tested assertions:** the C1/C2/C3/C4 independent checks in Wave 3 were run against the current (broken) repo state during planning and correctly detected the live defects (43 legacy paths; the 3 mismatched platform ids; the `_shared` archive.py string; the 0.39.0 CLAUDE.md drift). They read the underlying artifacts directly (receipt-index `tasks[]`, registry `- id:` lines vs skill dirs, archive.py source, CLAUDE.md), not the doctor's output. Wave 2 additionally requires the doctor's baseline to detect the seeded critical findings, so a stubbed doctor check fails the gate.
- **Accepted residual (disclosed, not hidden):** config-schema *conformance* of recipe.json and wave-queue files (the config half of AC2) is verified by the doctor's schema-validity check (Wave 2), which depends on the instrument. Mitigation: Wave 1 independently proves the schema files are well-formed, and Wave 2's baseline-detection requirement guards against a vacuous schema check. Full independent config-conformance would require a standalone JSON-Schema validator (jsonschema is not assumed installed) — out of scope for this task.
- **AC1 resolved** via the documented exit-code contract: `--all` exits 0 on enumeration; pass/fail gating uses `--severity`. Remaining M/L findings never break a gate.
- **Wave 5 rollback uses a git worktree** (edits Guard, invariant-enforcing; High + irreversible-category + git repo).
- **Post-escalation hardening (human-authorized 2026-05-28, beyond the 3-cycle limit):** RV-A2 closed — Wave 2 now requires a doctor `--self-test` proving each schema validator accepts a good fixture and rejects a malformed one, so the schema check (incl. wave-queue config conformance) is provably non-vacuous. RV-A5 closed — Wave 3 now parses the CLAUDE.md "Current version" line and asserts it equals the VERSION file (empirically confirmed to detect the live 0.39.0↔0.45.0 drift), replacing the brittle whole-file grep. RV-TOOL (no reviewer/propose builder) remains folded into Wave 1's builder-closure scope.
- **Reviewer gate:** HIGH-impact contract + Guard edit → Reviewer. Reached the 3-cycle REVISE limit (cycle 0/1/2 all REVISE, MAJOR count 6→2→2, all in verification-command micro-semantics) → ESCALATE. Human directed one final residual-hardening pass (above); plan is now cleared to proceed to Executor.
- **Advisory-first:** doctor Guard layer ships non-blocking; promotion to blocking is out of scope.
