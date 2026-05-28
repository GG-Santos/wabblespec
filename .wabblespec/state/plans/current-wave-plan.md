# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Framework
**complexity:** High
**collapse_eligible:** false
**session_id:** foundation-hardening-20260528
**generated_at:** 2026-05-28T14:45:05Z
**supersedes:** wave plan as of 2026-05-28T13:48:49Z (cycle-2 post-escalation, 5 waves)
**revised_because:** Executor Wave 1 blocked at Guard Layer 4 — no module's authority.owns covered shared framework infra. Human chose Pause + rescope. Finding #29 added; AC8 added. New first wave (framework-maintenance authority owner, bootstrapped by one-time Attestation) inserted; prior 5 waves renumbered to 2-6, content preserved.
**strategy:** Option 2 — Fix + Permanent Drift Gate
**verification_shell:** bash
**high_tier_scope:** H1, H2, H3, H4, H5, H6, H7, H8, H10 (H9 deferred non-goal)

## Findings of note carried into Executor

- **Finding #29 (NEW):** No module's `authority.owns` covers shared framework infrastructure (engine/shared/**, the Guard module, wabblespec.yaml, CLAUDE.md, daemon-config, .claude/skills/**). Wave 1 establishes a permanent owner.
- **H1 is larger than the audit framing:** 17 of 20 receipt builders emit no top-level numeric `confidence` (only `recipe`, `ref-eval`, `ref-comp` comply). Closed in Wave 2.
- **`receipt-writer.py --validate` does not enforce base-required `confidence`** — AC3 verified by explicit field check.
- **Sibling builder gaps:** receipt-writer has no `propose`, `reviewer`, `scopeframe`, or `guard` builder types. Folded into Wave 2.

## Doctor exit-code contract (implemented Wave 3)

- `--all` → exit 0 on successful enumeration (findings in payload).
- `--severity {critical,high,medium,low}` → exit nonzero iff any check at that severity fails.
- `--guard-advisory` → always exit 0 (non-blocking).
- `--format json` payload: `{"checks":[{"id","severity","status"}...]}`.

## Waves

### Wave 1: Establish framework-maintenance authority owner (Attestation-gated bootstrap)

**inputs:** [task-card.md AC8, scope.md finding #29 + bootstrap assumption, wabblespec.yaml, .wabblespec/engine/modules/, guard-wave-1-receipt-foundation-hardening-20260528.json (the block that triggered the rescope)]
**outputs:**
- `.wabblespec/engine/modules/l2/framework-maintenance/SKILL.md` — minimal SKILL.md (purpose: own shared framework infrastructure paths for framework self-build tasks)
- `.wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json` with `authority.owns` covering ALL shared-infra paths the remaining waves must write: `.wabblespec/engine/shared/**`, `.wabblespec/engine/hooks/**`, `.wabblespec/engine/scripts/**`, `.wabblespec/engine/modules/l2/guard/**`, `.wabblespec/engine/modules/l2/framework-maintenance/**`, `.wabblespec/wabblespec.yaml`, `CLAUDE.md`, `.claude/skills/**`, `.wabblespec/state/daemons/daemon-config.json`, `.wabblespec/state/archive/receipt-index.json`, `.wabblespec/state/memory/**` (broader than entity-graph alone — covers Wave 5 regen of gap-map/staleness-map/closet-index/entity-graph), `.wabblespec/state/attestations/**` (gives the attestation artifact class an owner going forward)
- `.wabblespec/engine/modules/l2/framework-maintenance/scripts/attestation-hash.py` — small helper script (~10 lines) that the operator runs to compute the canonical `content_hash` before authoring an attestation. Written as part of Wave 1 (owned by framework-maintenance/**). The canonical recipe is also embedded inline below so the operator can compute the hash BEFORE Wave 1 has run.
- `wabblespec.yaml` structural registration entry for `framework-maintenance` — a full module record with `id: framework-maintenance`, `layer: L2`, `path:`, `build_status:`, not a stray string mention
- `.wabblespec/state/attestations/framework-maintenance-authority-bootstrap-<timestamp>.json` — human Attestation record with required schema: `attestation_id` (str), `attested_by` (str), `attested_at` (ISO 8601 UTC), `reason` (str), `scope` (object: `module="framework-maintenance"`, `wave=1`, `task_id`), `granted_paths` (array of file/dir paths/globs this attestation authorizes Wave 1 to write — MUST be a subset of the closed whitelist below), `one_time_use` (bool, MUST be `true`), `content_hash` (sha256 hex per the canonical recipe — binds the attestation to the exact files attested), optional `signature` (str). The file MUST PRE-EXIST before `/executor` starts (it is NOT a Wave 1 output).
- After Wave 1 completes successfully, Executor moves the attestation from `.wabblespec/state/attestations/framework-maintenance-authority-bootstrap-<timestamp>.json` to `.wabblespec/state/attestations/consumed/<attestation_id>/<original-filename>` (consume-by-move: prevents replay).

**Bootstrap mechanism (resolves the chicken-and-egg) — engineered for invariant-grade enforcement:**

**Hard preconditions** (before `/executor` may start Wave 1):
- The Attestation file MUST exist at `.wabblespec/state/attestations/framework-maintenance-authority-bootstrap-*.json` — EXACTLY ONE such file. Executor rejects Wave 1 at entry if absent or if multiple exist.
- The Attestation's `attestation_id` MUST NOT already appear as a subdirectory under `.wabblespec/state/attestations/consumed/` (replay prevention via filesystem semantics — no receipt-writer dependency).
- The Attestation's `granted_paths` MUST be a subset of the closed whitelist (no prefix-bounds; explicit allowlist). The whitelist for the bootstrap is exactly:
  ```
  .wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json
  .wabblespec/engine/modules/l2/framework-maintenance/SKILL.md
  .wabblespec/engine/modules/l2/framework-maintenance/scripts/attestation-hash.py
  .wabblespec/engine/modules/l2/framework-maintenance/**
  .wabblespec/wabblespec.yaml
  ```
- The Attestation's `granted_paths` MUST include at minimum: skill-rules.json, SKILL.md, wabblespec.yaml (the irreducible step-1+2+3 set).

**Fixed write order** (narrows the Layer-4 skip to ONE file):
1. **Write `.wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json` first** — the ONLY write that requires an Attestation skip of Guard Layer 4 (no module currently owns this path; once it lands, `--module framework-maintenance` resolves and owns everything else).
2. Write `SKILL.md` and `scripts/attestation-hash.py` — owned by `.wabblespec/engine/modules/l2/framework-maintenance/**` from step 1.
3. Edit `wabblespec.yaml` registration entry — owned by `.wabblespec/wabblespec.yaml` from step 1.
4. Run the verification command below (all four sub-checks must pass).
5. **Consume-by-move:** Executor moves the attestation file from `state/attestations/<filename>` to `state/attestations/consumed/<attestation_id>/<filename>`. This is a filesystem-level consume: replay protection on any future wave is `os.path.isdir('.wabblespec/state/attestations/consumed/<id>')`. No receipt-writer field is required.

Guard Layer 4 is SKIPPED for the SINGLE write in step 1 only; steps 2-5 and all subsequent waves run Guard normally under `--module framework-maintenance`.

**Attestation authoring recipe (the operator runs this BEFORE `/executor`):**
```bash
# 1. Author the framework-maintenance module files first (SKILL.md + skill-rules.json) in the worktree.
# 2. Compute the canonical content_hash:
python -c "
import hashlib
skill = open('.wabblespec/engine/modules/l2/framework-maintenance/SKILL.md','rb').read()
rules = open('.wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json','rb').read()
print(hashlib.sha256(skill + b'\x00---attestation-separator---\x00' + rules).hexdigest())
"
# 3. Author the attestation JSON at .wabblespec/state/attestations/framework-maintenance-authority-bootstrap-<ISO-timestamp>.json
#    with all required fields and content_hash = (the hex printed above).
# 4. Now run /executor — Wave 1 will validate the attestation against the on-disk files.
# After Wave 1 succeeds, .wabblespec/engine/modules/l2/framework-maintenance/scripts/attestation-hash.py
# becomes the permanent helper for any future attestation of this module.
```

**Acknowledged residual (documented, narrow):** `guard-check.py` still has no `--attestation` flag, so the step-1 skip remains an Executor process control rather than a Guard-enforced behavior. The verification command runs AFTER step 1 completes and proves the resulting authority is correct (a posteriori safety net). The Attestation `content_hash` binds SKILL.md + skill-rules.json bytes but does NOT bind the wabblespec.yaml edit; the operator is trusted to register only the attested module. These two residuals are accepted under the trusted-operator model (the operator IS the human attestor — same trust boundary).

**checkpoint:** Attestation record validates against the full schema (all 8 required fields present, correct types, `one_time_use=true`, `scope.module="framework-maintenance"`, `content_hash` equals sha256 of on-disk SKILL.md+skill-rules.json); SKILL.md and skill-rules.json exist; `authority.owns` contains every glob in the outputs list; `wabblespec.yaml` contains a structurally-parsed module entry with `id=framework-maintenance`, `layer=L2`, and `build_status` present; `guard-check.py authority --module framework-maintenance` returns PASS for representative files spanning every subsequent wave's outputs (receipt-writer.py, doctor.py, receipt-index.json, archive.py, CLAUDE.md, daemon-config.json, Guard SKILL.md, entity-graph.json, gap-map.md, a platform skill dir).
**rollback_to:** null (Wave 1 runs in a git worktree; on failure run `git worktree remove <path> --force` and `rm -f .wabblespec/state/attestations/framework-maintenance-authority-bootstrap-*.json` to clear partial state before re-attestation)
**verification_mode:** Attestation
**verification_command:** (runs inside the Wave 1 worktree before merge)
```bash
bash -c 'set -e
python -c "
import json, hashlib, glob, os, sys
# 1) Exactly one attestation file present
atts = sorted(glob.glob(\".wabblespec/state/attestations/framework-maintenance-authority-bootstrap-*.json\"))
assert len(atts) == 1, ('expected exactly one attestation, got', atts)
d = json.load(open(atts[0], encoding=\"utf-8\"))
# 2) All required fields present and non-empty (or correctly typed)
req = [\"attestation_id\",\"attested_by\",\"attested_at\",\"reason\",\"scope\",\"granted_paths\",\"one_time_use\",\"content_hash\"]
miss = [f for f in req if f not in d or d[f] in (None, '', [])]
assert not miss, ('missing/empty fields', miss)
assert isinstance(d[\"granted_paths\"], list) and d[\"granted_paths\"], 'granted_paths empty'
assert d[\"one_time_use\"] is True, 'one_time_use must be True'
assert isinstance(d[\"scope\"], dict) and d[\"scope\"].get(\"module\") == \"framework-maintenance\"
# 3) Replay protection via filesystem (consume-by-move): attestation_id must not exist in consumed/
consumed = os.path.join('.wabblespec/state/attestations/consumed', d['attestation_id'])
assert not os.path.isdir(consumed), ('attestation_id already consumed at', consumed)
# 4) granted_paths must be a SUBSET of the closed whitelist (no prefix-bound bypass)
WHITELIST = {
    '.wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json',
    '.wabblespec/engine/modules/l2/framework-maintenance/SKILL.md',
    '.wabblespec/engine/modules/l2/framework-maintenance/scripts/attestation-hash.py',
    '.wabblespec/engine/modules/l2/framework-maintenance/**',
    '.wabblespec/wabblespec.yaml',
}
extra = [g for g in d['granted_paths'] if g not in WHITELIST]
assert not extra, ('granted_paths contains entries outside the closed whitelist', extra)
# 5) granted_paths must cover the irreducible step-1+2+3 set
REQUIRED_IN_GRANT = {
    '.wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json',
    '.wabblespec/engine/modules/l2/framework-maintenance/SKILL.md',
    '.wabblespec/wabblespec.yaml',
}
miss_grant = [p for p in REQUIRED_IN_GRANT if p not in d['granted_paths']]
assert not miss_grant, ('granted_paths missing required entries', miss_grant)
# 6) content_hash binds SKILL.md + skill-rules.json bytes (canonical separator)
skill = open(\".wabblespec/engine/modules/l2/framework-maintenance/SKILL.md\",\"rb\").read()
rules = open(\".wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json\",\"rb\").read()
got = hashlib.sha256(skill + b'\\x00---attestation-separator---\\x00' + rules).hexdigest()
assert got == d[\"content_hash\"], ('content_hash mismatch', got, d['content_hash'])
"
python -c "
import json
d = json.load(open(\".wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json\"))
owns = d[\"authority\"][\"owns\"]
need = [\".wabblespec/engine/shared/**\",\".wabblespec/engine/hooks/**\",\".wabblespec/engine/scripts/**\",\".wabblespec/engine/modules/l2/guard/**\",\".wabblespec/engine/modules/l2/framework-maintenance/**\",\".wabblespec/wabblespec.yaml\",\"CLAUDE.md\",\".claude/skills/**\",\".wabblespec/state/daemons/daemon-config.json\",\".wabblespec/state/archive/receipt-index.json\",\".wabblespec/state/memory/**\",\".wabblespec/state/attestations/**\"]
miss = [g for g in need if g not in owns]
assert not miss, miss
"
python -c "
import yaml
reg = yaml.safe_load(open(\".wabblespec/wabblespec.yaml\", encoding=\"utf-8\"))
mods = reg.get(\"modules\", reg) if isinstance(reg, dict) else reg
entry = next((m for m in mods if isinstance(m, dict) and m.get(\"id\") == \"framework-maintenance\"), None)
assert entry is not None
assert entry.get(\"layer\") == \"L2\"
assert entry.get(\"build_status\")
"
python .wabblespec/engine/shared/scripts/guard-check.py authority \
  --module framework-maintenance \
  --files ".wabblespec/engine/shared/scripts/receipt-writer.py" \
          ".wabblespec/engine/shared/scripts/wabblespec-doctor.py" \
          ".wabblespec/state/archive/receipt-index.json" \
          ".wabblespec/engine/shared/scripts/archive.py" \
          "CLAUDE.md" \
          ".wabblespec/state/daemons/daemon-config.json" \
          ".wabblespec/engine/modules/l2/guard/SKILL.md" \
          ".wabblespec/state/memory/entity-graph.json" \
          ".wabblespec/state/memory/gap-map.md" \
          ".claude/skills/platform-iot" | grep -q "PASS"
'
```

---

### Wave 2: Contract & schema foundation

(was Wave 1 in the prior plan; content preserved, authority module = framework-maintenance)

**inputs:** [task-card.md AC2/AC3, findings H1/H2/H4/H8, engine/shared/schemas/, receipt-writer.py]
**outputs:** [recipe.schema.json, wave-queue.schema.json, delivery-receipt.schema.json; receipt-writer.py `propose` builder + `reviewer` builder + `scopeframe` builder + `guard` builder + `--options-path` flag in build_brainstorm; `confidence` field emitted by ALL 20 builders with back-compat reads of legacy `confidence_score`/`score`; `--validate` tightened to enforce base-required fields]
**checkpoint:** All three schema files well-formed JSON Schema docs; propose + brainstorm + reviewer + scopeframe + guard receipts each write and `--validate`; every one of the receipt types emits a top-level numeric `confidence` in [0,1].
**rollback_to:** Wave 1 checkpoint
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
for t in verifier executor recipe specify decompose scaffold package release monitor deploy adversary grader nexus brainstorm enhance sharpen audit ref-eval ref-comp ref-plan propose reviewer scopeframe guard; do
  python .wabblespec/engine/shared/scripts/receipt-writer.py --type "$t" --task-id t --session-id s --status PASS --confidence 0.9 --out - \
   | python -c "import sys,json; d=json.load(sys.stdin); assert isinstance(d.get(\"confidence\"),(int,float)) and 0<=d[\"confidence\"]<=1, \"$t\""
done
rm -f "$P" "$B"'
```

---

### Wave 3: Build wabblespec-doctor.py

(was Wave 2; content preserved)

**inputs:** [Wave 2 schemas + new builders, task-card.md AC1, brainstorm options file]
**outputs:** [wabblespec-doctor.py implementing the exit-code contract; checks for C1-C4, H1-H10, M/L tier; a schema-validity check that validates recipe.json against recipe.schema.json and a generated wave-queue file against wave-queue.schema.json; a `--self-test` mode validating bundled good AND malformed fixtures (engine/shared/scripts/tests/fixtures/{good,bad}-{recipe,wave-queue}.json) asserting good→PASS and bad→FAIL; the fixtures themselves]
**checkpoint:** `--all --format json` exits 0 and enumerates ≥28 checks; the named set {C1..C4, H1..H8, H10} present; baseline reports C1-C4 as FAIL (proves checks detect real defects); `--self-test` exits 0 (schema validators discriminate).
**rollback_to:** Wave 2 checkpoint
**verification_mode:** Test
**verification_command:**
```bash
bash -c 'set -e
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --self-test
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all >/dev/null
python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all --format json \
 | python -c "import sys,json; d=json.load(sys.stdin); ch=d[\"checks\"]; assert len(ch)>=28; ids={c[\"id\"] for c in ch}; need={\"C1\",\"C2\",\"C3\",\"C4\",\"H1\",\"H2\",\"H3\",\"H4\",\"H5\",\"H6\",\"H7\",\"H8\",\"H10\"}; assert need<=ids, need-ids; crit={c[\"id\"]:c[\"status\"] for c in ch if c.get(\"severity\")==\"critical\"}; assert any(v!=\"PASS\" for v in crit.values()), \"baseline must detect critical findings\"; print(\"checks=%d named-present detects-critical=OK\"%len(ch))"'
```

---

### Wave 4: Critical fixes (C1-C4)

(was Wave 3; content preserved)

**inputs:** [Wave 3 doctor, AC4/AC5/AC6, receipt-index.json, archive.py, CLAUDE.md, .claude/skills/, wabblespec.yaml]
**outputs:** [receipt-index.json regenerated (all delivery_receipt_path under state/receipts/, all resolve); platform module ids in wabblespec.yaml aligned to short-form skill dir names + sync script corrected; archive.py wabble-sound.py path fixed; CLAUDE.md → 0.45.0 / 103 modules]
**checkpoint:** `--severity critical` exits 0 AND four independent assertions pass: C1 receipt-index has no `.wabblespec/receipts/` prefix and every `tasks[].delivery_receipt_path` resolves; C2 every `platform-*` id in wabblespec.yaml has an exactly-matching `.claude/skills/` dir; C3 the broken `"_shared","scripts","wabble-sound.py"` string is gone from archive.py and wabble-sound.py still exists and is referenced; C4 CLAUDE.md "Current version" line == VERSION file and "103 modules" present.
**rollback_to:** Wave 3 checkpoint
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

### Wave 5: High-tier fixes (H1-H8,H10; H9 deferred)

(was Wave 4; content preserved)

**inputs:** [Wave 3 doctor, high-tier in-scope, findings H3/H5/H6/H7/H10 (H1/H2/H4/H8 closed Wave 2)]
**outputs:** [CLI unified to --delta-class in task-card-writer.py and archive.py; entity graph regenerated over all current drawers; CLAUDE.md script-location section corrected (l5/*/scripts/); orphan templates registered-with-owner or removed-with-provenance; memory-bootstrap duplication resolved]
**checkpoint:** `--severity high` exits 0; `--all` exits 0 with all critical AND high checks PASS; independent grep confirms `--delta-class` in both scripts and `--change-class` gone from task-card-writer.py.
**rollback_to:** Wave 4 checkpoint
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

### Wave 6: Wire doctor as advisory gate

(was Wave 5; content preserved; remains git-worktree-isolated)

**inputs:** [Wave 3 doctor, AC7, daemon-config.json, Guard module + guard-check.py]
**outputs:** [daemon-config.json gains a wabblespec-doctor job on the on_archive trigger; Guard gains an advisory (non-blocking) doctor layer exposed via guard-check.py --advisory-doctor]
**checkpoint:** daemon-config contains the doctor on_archive job; an advisory invocation through guard-check.py surfaces doctor findings AND exits 0 (non-blocking).
**rollback_to:** Wave 5 checkpoint (git worktree)
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
| Wave 1 fails | null — canonical worktree path is `../wabblespec-wave-1-bootstrap`. Run `git worktree remove ../wabblespec-wave-1-bootstrap --force`. If the consume-by-move already ran (state/attestations/consumed/<id>/ exists), the attestation is consumed and a fresh one is required for retry — author a NEW attestation with a NEW `attestation_id` (do not reuse). If consume-by-move did NOT run, delete the unconsumed attestation: `rm -f .wabblespec/state/attestations/framework-maintenance-authority-bootstrap-*.json`. | Hard precondition fail (zero or >1 attestation files; attestation_id already in consumed/; granted_paths not a whitelist subset; required_in_grant entries missing; content_hash mismatch; schema validation fail); OR post-write fail (skill-rules.json missing required owns glob; wabblespec.yaml structural module entry missing; guard-check authority fails for any sample file). |
| Wave 2 fails | Wave 1 checkpoint | schema not well-formed, a --validate fails, options_path absent, or any builder lacks a clean confidence field |
| Wave 3 fails | Wave 2 checkpoint | doctor cannot enumerate ≥28 checks, named set missing, --self-test fails, or baseline does not detect seeded critical findings |
| Wave 4 fails | Wave 3 checkpoint | HARD error, critical RED after 3 REVISE cycles, or any independent C1/C2/C3/C4 assertion fails |
| Wave 5 fails | Wave 4 checkpoint | HARD error, high RED after 3 REVISE cycles, or full-run crit+high not all green |
| Wave 6 fails | Wave 5 checkpoint (git worktree) | Guard edit breaks enforcement, advisory path blocks (exit ≠ 0), or findings not surfaced |

## Notes

- **Wave 1 is the bootstrap.** Mechanism is now explicit (see "Bootstrap mechanism" in Wave 1): Executor reads and validates a one-time Attestation; Guard Layer 4 is skipped ONLY for the paths in `granted_paths`, ONLY during Wave 1, ONLY when a valid Attestation exists. A `content_hash` field binds the Attestation to the exact SKILL.md + skill-rules.json bytes attested, so post-hoc edits invalidate it.
- **authority.owns rationale (justifies expansion beyond AC8's named surface):** `.claude/skills/**` is needed for Wave 4's platform skill-ID rename (C2); `.wabblespec/engine/hooks/**` and `.wabblespec/engine/scripts/**` are needed for downstream fixes that touch the sync script and stop-hook; `.wabblespec/state/memory/**` is needed for Wave 5's entity-graph/gap-map/staleness-map/closet-index regen; `.wabblespec/state/attestations/**` gives the attestation artifact class an owner going forward (otherwise it remains unowned even after Wave 1).
- **Wave 1 uses a git worktree** (High + irreversible-category governance edit + git repo): the new module's files and the wabblespec.yaml change are isolated until Reviewer + Attestation sign off.
- **Wave 6 uses a git worktree** (Guard edit, invariant-enforcing). Two worktree waves total.
- **Reviewer:** new Wave 1 is novel content; recommend a focused Reviewer pass scoped to Wave 1 only (Waves 2-6 were exhaustively reviewed in the prior cycle and content is unchanged). The Reviewer hard-limit counter resets for the new scope.
- **No bypass:** the prior Guard FAIL (guard-wave-1-receipt-foundation-hardening-20260528.json) remains on file as the trigger for this rescope; nothing was bypassed.
- **Advisory-first:** doctor Guard layer ships non-blocking; promotion to blocking is out of scope.
