# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Framework
**complexity:** High
**collapse_eligible:** false
**session_id:** foundation-hardening-20260528
**generated_at:** 2026-05-28T13:34:20Z
**strategy:** Option 2 — Fix + Permanent Drift Gate (selected via Propose 2026-05-28)
**sequencing_principle:** Contract/schema layer first; the doctor (Wave 2) becomes the verification instrument for the fix waves (3-4); Guard wiring last and isolated.

## Waves

### Wave 1: Contract & schema foundation

**inputs:** [task-card.md AC2/AC3, brainstorm findings H1/H2/H4/H8, .wabblespec/engine/shared/schemas/, receipt-writer.py]
**outputs:** [recipe.schema.json, wave-queue.schema.json, delivery-receipt.schema.json, receipt-writer.py propose builder + --options-path flag, unified confidence field across builders]
**checkpoint:** All three new schema files exist; receipt-writer.py --validate passes for recipe, wave-queue, delivery, brainstorm (populated options_path), and propose receipts; no builder emits a legacy-only confidence field.
**rollback_to:** null
**verification_mode:** Test
**verification_command:** `python -c "import os,sys; sys.exit(0 if all(os.path.exists('.wabblespec/engine/shared/schemas/'+s) for s in ['recipe.schema.json','wave-queue.schema.json','delivery-receipt.schema.json']) else 1)" && python .wabblespec/engine/shared/scripts/receipt-writer.py --type propose --task-id t --session-id s --status PASS --out - && python .wabblespec/engine/shared/scripts/receipt-writer.py --type brainstorm --task-id t --session-id s --status PASS --options-path /tmp/x.md --out - | grep -q '"options_path": "/tmp/x.md"'`

---

### Wave 2: Build wabblespec-doctor.py

**inputs:** [Wave 1 schemas, task-card.md AC1, .wabblespec/brainstorm/options-20260528T125658Z.md (all 28 findings)]
**outputs:** [.wabblespec/engine/shared/scripts/wabblespec-doctor.py — one check per finding class (C1-C4, H1-H10, M/L tier); flags --all, --severity {critical,high,medium,low}, --format json, --guard-advisory (always exit 0)]
**checkpoint:** wabblespec-doctor.py --all --format json runs to completion and enumerates >= 28 distinct checks; baseline run reports known C/H findings as failing (expected pre-fix RED baseline).
**rollback_to:** Wave 1 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all --format json | python -c "import sys,json; d=json.load(sys.stdin); assert len(d.get('checks',[]))>=28, len(d.get('checks',[])); print('checks='+str(len(d['checks'])))"`

---

### Wave 3: Critical fixes (C1-C4)

**inputs:** [Wave 2 doctor, task-card.md AC4/AC5/AC6, receipt-index.json, archive.py, CLAUDE.md, .claude/skills/ platform dirs, wabblespec.yaml]
**outputs:** [regenerated receipt-index.json (all paths resolve under state/receipts/), platform skill IDs aligned + sync script corrected, archive.py wabble-sound.py path fixed, CLAUDE.md set to 0.45.0 / 103 modules]
**checkpoint:** wabblespec-doctor.py --severity critical exits 0 (all four critical checks green).
**rollback_to:** Wave 2 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --severity critical; test $? -eq 0`

---

### Wave 4: High-tier fixes

**inputs:** [Wave 2 doctor, task-card.md high-tier in-scope, findings H3/H5/H6/H7/H10]
**outputs:** [CLI unified to --delta-class, entity graph regenerated over all drawers, CLAUDE.md script-location section corrected, orphan templates registered-or-removed with provenance, memory-bootstrap duplication resolved]
**checkpoint:** wabblespec-doctor.py --severity high exits 0 (all high-tier checks green).
**rollback_to:** Wave 3 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --severity high; test $? -eq 0`

---

### Wave 5: Wire doctor as advisory gate

**inputs:** [Wave 2 doctor, task-card.md AC7, .wabblespec/state/daemons/daemon-config.json, Guard module + guard-check.py]
**outputs:** [daemon-config.json gains wabblespec-doctor on_archive job, Guard gains advisory (non-blocking) doctor layer]
**checkpoint:** daemon-config contains the doctor on_archive job; doctor --guard-advisory runs and returns exit 0 (never blocks); an Archive/stop run surfaces doctor findings as advisory output.
**rollback_to:** Wave 4 checkpoint (worktree)
**verification_mode:** Demonstration
**verification_command:** `grep -q 'wabblespec-doctor' .wabblespec/state/daemons/daemon-config.json && python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --guard-advisory; test $? -eq 0`

---

## Rollback Map

| Trigger | Rollback target | Condition |
|---|---|---|
| Wave 1 fails | null (re-run from clean) | schema validation fails or receipt-writer regressions |
| Wave 2 fails | Wave 1 checkpoint | doctor cannot enumerate >= 28 checks or crashes |
| Wave 3 fails | Wave 2 checkpoint | HARD error or critical checks still RED after 3 REVISE cycles |
| Wave 4 fails | Wave 3 checkpoint | HARD error or high checks still RED after 3 REVISE cycles |
| Wave 5 fails | Wave 4 checkpoint (git worktree) | Guard edit breaks enforcement or doctor blocks when it must be advisory |

## Notes

- **Wave 5 rollback uses a git worktree**, not a file checkpoint: it edits Guard (invariant-enforcing, "cannot be bypassed") — the highest-blast-radius irreversible-category edit in this plan. Complexity is High and the repo is a git repo, satisfying all three worktree conditions. Waves 1-4 edit framework files that restore cleanly from file checkpoints, so they use wave-checkpoint.
- **Reviewer gate:** this wave plan is a HIGH-impact execution contract AND Wave 5 modifies Guard. Per the Specify carry-forward, the plan routes through Reviewer before Executor starts.
- **Advisory-first:** the doctor Guard layer ships non-blocking. Promotion to blocking is out of scope (deferred until the doctor runs clean across several Archives).
