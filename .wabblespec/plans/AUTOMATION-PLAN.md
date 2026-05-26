# WabbleSpec Automation Implementation Plan

**Version:** 0.11.0  
**Date:** 2026-05-26  
**Scope:** Phase 3 of the mechanical-layer automation initiative.  
**Baseline:** 20 scripts already in `_shared/scripts/`. This plan covers the next 9.

---

## Context

Two prior sessions built the automation foundation:

**Session 1 (Archive phase):** `archive.py`, `changelog-append.py`, `version-bump.py`, `receipt-writer.py`  
Eliminated ~28K–40K tokens per Archive run. CHANGELOG is now append-only. VERSION is a CLI call.

**Session 2 (Session lifecycle + module registration):** `framework-register.py`, `module-scaffold.py`, `receipt-chain-validate.py`, `recipe-writer.py`, `session-state.py`  
Eliminated ~13K tokens per framework.yaml write. Module scaffolding now generates quality-gate-passing stubs.

**This plan:** Guard automation, memory layer, L8 pipeline, and pipeline orchestration.

---

## Structural Patterns (what makes something automatable)

All nine scripts in this plan are instances of three patterns:

| Pattern | Description | Examples in this plan |
|---|---|---|
| **A — Lookup-table** | Input matched against a policy table; result returned. Table never changes between calls — reading the file is overhead. | command-risk-check, guard-check layer 4+5 |
| **B — Schema-enforced write** | Fixed JSON or Markdown structure, variable content. Claude re-derives structure every time. | drawer-writer, tracker-update, provenance-append |
| **C — Aggregate-and-report** | Scan multiple files, compute statistics or state, write summary. Deterministic from inputs. | index-update, fixture-split, document-check |

If a step matches one of these patterns, it is a script candidate. If it requires understanding context, intent, or tradeoffs — it stays with Claude.

---

## Token Impact Summary

| Script | Pattern | Tokens saved per operation | Frequency |
|---|---|---|---|
| `guard-check.py` | A | ~2,500–3,500 per wave | Every wave in every session |
| `command-risk-check.py` | A | ~2,225 per Guard invocation | Every Guard run |
| `drawer-writer.py` | B | ~300 per drawer | Every Memory write |
| `tracker-update.py` | B | ~13K per L8 operation | L8 pipeline stages |
| `fixture-split.py` | C | ~500 per fixture set | Every new benchmark |
| `index-update.py` | C | ~2,000 per session | Post-session |
| `provenance-append.py` | B | ~400 per Memory write | Every Memory write |
| `document-check.py` | A | ~1,000 per document wave | Document phases |
| `pipeline.py` | meta | eliminates sequencing overhead | Every session boundary |

---

## Implementation Waves

### Wave 1 — Guard Automation
*Scripts: `command-risk-check.py`, `guard-check.py`*  
*Priority: Highest — runs on every wave in every session*

### Wave 2 — Memory Layer
*Scripts: `drawer-writer.py`, `provenance-append.py`*  
*Priority: High — every Memory write is a candidate*

### Wave 3 — L8 Pipeline
*Scripts: `tracker-update.py`, `fixture-split.py`*  
*Priority: Medium — runs during evolution cycles*

### Wave 4 — Verification and Reporting
*Scripts: `document-check.py`, `index-update.py`*  
*Priority: Medium — improves Verifier and session close*

### Wave 5 — Orchestration
*Scripts: `pipeline.py`*  
*Priority: Medium — composes all prior scripts into two entry points*

---

## Wave 1 — Guard Automation

### Script 1: `command-risk-check.py`

**What it replaces:** Claude reading `_shared/references/command-risk-policy.md` (8.9 KB, ~2,225 tokens) on every Guard invocation to classify shell commands.

**Pattern:** A — lookup table. The policy is a static classification table. It does not change between sessions. Embedding it in Python eliminates the file read entirely.

**Interface:**

```bash
# Classify one or more shell commands
python _shared/scripts/command-risk-check.py \
  --commands "git add -A" "git push --force" "npm run build" "rm -rf /tmp"

# JSON output mode (for guard-check.py internal use)
python _shared/scripts/command-risk-check.py \
  --commands "git push --force" "curl http://api.example.com" \
  --json

# Read commands from a wave plan file (extracts bash_command fields)
python _shared/scripts/command-risk-check.py \
  --from-wave-plan .wabblespec/plans/wave-current.md
```

**Output (human-readable):**
```
git add -A            SAFE
git push --force      BLOCK  — use --force-with-lease instead
npm run build         SAFE
rm -rf /tmp           WARN   — add rationale to wave plan step
```

**Output (--json):**
```json
{
  "overall": "BLOCK",
  "commands": [
    { "command": "git push --force", "verdict": "BLOCK",
      "safer_alternative": "git push --force-with-lease" }
  ]
}
```

**Exit codes:** 0 = all SAFE/WARN, 1 = any BLOCK, 2 = parse error

**Classification table to embed** (from `command-risk-policy.md`):

| Category | Pattern | Verdict |
|---|---|---|
| git | `push --force` / `push -f` | BLOCK |
| git | `push --force-with-lease` | WARN |
| git | `reset --hard` | BLOCK |
| git | `checkout -- <path>` / `restore <path>` (working tree) | BLOCK |
| git | `clean -fd` / `clean -fdx` | BLOCK |
| git | `branch -D` | BLOCK |
| git | `filter-branch` / `filter-repo` | BLOCK |
| git | `clean -f` without `-d` | WARN |
| git | `rebase` without `--abort` | WARN |
| git | `commit --amend` | WARN |
| git | `push --force-with-lease` | WARN |
| git | `log`, `status`, `diff`, `show`, `fetch` | SAFE |
| git | `checkout -b`, `branch -m` | SAFE |
| git | `clean --dry-run` / `clean -n` | SAFE |
| filesystem | `rm -rf` outside `/tmp` or build dirs | BLOCK |
| filesystem | `rmdir`, `rm -r` on repo paths | BLOCK |
| filesystem | `chmod -R 777` | BLOCK |
| filesystem | `rm -rf /tmp/...` | WARN |
| filesystem | `cp -r`, `mv` | WARN |
| filesystem | `ls`, `cat`, `head`, `tail`, `find`, `wc` | SAFE |
| network | `curl` / `wget` to external URLs | WARN |
| network | `curl` to localhost/127.0.0.1 | SAFE |
| database | `DROP TABLE`, `TRUNCATE` | BLOCK |
| database | `DELETE FROM` without WHERE | BLOCK |
| database | `ALTER TABLE` | WARN |
| database | `SELECT`, `EXPLAIN` | SAFE |
| node/python | `npm install`, `pip install` | WARN |
| node/python | `npm ci` | SAFE |
| node/python | `npx`, `uvx` (external download) | WARN |

**SAFE exception rule:** If a command matches both a SAFE and a non-SAFE pattern, SAFE wins.

**Not covered by script (stay with Claude):** Commands not matching any pattern default to WARN with a note that the classification is uncertain.

---

### Script 2: `guard-check.py`

**What it replaces:** Claude reading `skill-rules.json` (~1–2 KB) and doing manual glob matching for Guard Layer 4 (authority check) and calling `command-risk-check.py` for Layer 5. Together these save ~2,500–3,500 tokens per Guard invocation.

**Pattern:** A — lookup table (authority.owns globs + command risk).

**What it does NOT replace:** Guard Layers 2 (scope constraint) and 3 (invariant compliance) remain with Claude — these require reasoning about context, not pattern matching.

**Interface:**

```bash
# Layer 4: authority check — does module own the target files?
python _shared/scripts/guard-check.py authority \
  --module executor \
  --files ".wabblespec/receipts/executor-receipt-xyz.json" \
           ".wabblespec/plans/task-card.md"

# Layer 4 + file_path_patterns misactivation check
python _shared/scripts/guard-check.py authority \
  --module archive \
  --files "src/foo.ts" "src/bar.ts" \
  --wave-files "src/foo.ts" "src/bar.ts"

# Layer 5: command risk (delegates to command-risk-check.py)
python _shared/scripts/guard-check.py commands \
  --commands "git add -A" "git push --force"

# Combined layers 4+5 for a full wave pre-check
python _shared/scripts/guard-check.py wave \
  --module executor \
  --files ".wabblespec/receipts/executor-receipt-xyz.json" \
  --commands "git add -A" "python _shared/scripts/validate-graph.py" \
  --json
```

**Output (`wave --json`):**
```json
{
  "layer_4": {
    "verdict": "PASS",
    "misactivation_risk": false,
    "unauthorized_files": []
  },
  "layer_5": {
    "verdict": "WARN",
    "command_warnings": ["git add -A — SAFE (no annotation needed)"],
    "blocking_commands": []
  },
  "overall": "PASS"
}
```

**Exit codes:** 0 = PASS (layers 4+5), 1 = FAIL or BLOCK, 2 = module not found / skill-rules.json missing

**Implementation notes:**
- Reads `modules/{layer}/{module}/skill-rules.json` directly — no framework.yaml read
- Uses `fnmatch.fnmatch()` for glob matching against `authority.owns` list
- Delegates command classification to `command-risk-check.py` (subprocess or shared import)
- `misactivation_risk` = True when `file_path_patterns` is non-empty AND none of `wave-files` match any pattern

**Verification:** Call against the 10 existing modules that have `file_path_patterns` declared; confirm misactivation_risk fires correctly. Call against a module that owns `.wabblespec/receipts/archive-*` and verify it blocks an attempt to write `src/foo.ts`.

---

## Wave 2 — Memory Layer

### Script 3: `drawer-writer.py`

**What it replaces:** Claude reasoning about which fields a drawer JSON requires, constructing the JSON, and issuing a Write tool call. The drawer schema (`_shared/schemas/drawer.schema.json`) defines 15 properties, 11 required.

**Pattern:** B — schema-enforced write.

**Required fields (from schema):** `id`, `topic`, `wing`, `room`, `staleness_state`, `written_at`, `source`, `source_module`, `confidence`, `evidence`, `provenance`

**Interface:**

```bash
# Create a new drawer
python _shared/scripts/drawer-writer.py \
  --id arch-layer-overview-20260526 \
  --topic "WabbleSpec layer architecture overview" \
  --wing architecture \
  --room core-design \
  --confidence 0.9 \
  --source-path _shared/references/invariants.md \
  --source-type reference \
  --source-module memory \
  --content "L0 handles session intake. L1 covers spec and planning..." \
  --out .wabblespec/memory/wings/architecture/core-design/arch-layer-overview-20260526.json

# Dry run — print JSON without writing
python _shared/scripts/drawer-writer.py ... --dry-run

# Update confidence on an existing drawer
python _shared/scripts/drawer-writer.py \
  --update .wabblespec/memory/wings/architecture/core-design/arch-layer-overview-20260526.json \
  --confidence 0.95 \
  --staleness-state FRESH

# Validate an existing drawer against schema
python _shared/scripts/drawer-writer.py \
  --validate .wabblespec/memory/wings/architecture/core-design/arch-layer-overview-20260526.json
```

**Output JSON structure:**
```json
{
  "id": "arch-layer-overview-20260526",
  "topic": "...",
  "wing": "architecture",
  "room": "core-design",
  "staleness_state": "FRESH",
  "written_at": "2026-05-26T...",
  "last_verified": null,
  "expires_at": null,
  "source": {
    "path": "_shared/references/invariants.md",
    "type": "reference"
  },
  "source_module": "memory",
  "confidence": 0.9,
  "evidence": [],
  "superseded_by": null,
  "contradicts": [],
  "provenance": { "written_by": "memory", "events": [] }
}
```

**Valid wings:** `architecture`, `implementation`, `decisions`, `operations`  
**Valid staleness states:** `FRESH`, `AGING`, `STALE`, `EXPIRED`, `NEEDS_REVERIFICATION`, `SUPERSEDED`

**Exit codes:** 0 = written, 1 = validation failure, 2 = output path not writable

---

### Script 4: `provenance-append.py`

**What it replaces:** Claude constructing provenance ledger entries and updating `index.json`. Provenance is append-only — same pattern as `changelog-append.py`. The existing `ledger.md` is never read; `open('a')` appends the new entry.

**Pattern:** B — schema-enforced write, append-only.

**Interface:**

```bash
# Record a Memory write event
python _shared/scripts/provenance-append.py record \
  --drawer-id arch-layer-overview-20260526 \
  --topic "WabbleSpec layer architecture overview" \
  --source-path _shared/references/invariants.md \
  --source-type reference \
  --written-by memory \
  --confidence 0.9

# Record a cascade event (BREAKING spec change)
python _shared/scripts/provenance-append.py cascade \
  --spec-path modules/l2/executor/SKILL.md \
  --change-class BREAKING \
  --affected-drawers "arch-layer-overview-20260526" "executor-wave-protocol-20260525"

# Record a contradiction
python _shared/scripts/provenance-append.py contradiction \
  --drawer-id arch-layer-overview-20260526 \
  --contradicts-drawer executor-wave-protocol-20260525 \
  --description "Layer L2 description conflicts with wave protocol detail"

# Record a deletion (from Forget)
python _shared/scripts/provenance-append.py delete \
  --drawer-id old-drawer-20260521 \
  --reason "Superseded by arch-layer-overview-20260526" \
  --requesting-module forget

# Show provenance record for a drawer (reads index.json only)
python _shared/scripts/provenance-append.py show \
  --drawer-id arch-layer-overview-20260526
```

**Writes:**
- `.wabblespec/memory/provenance/ledger.md` — appended with `open('a')`, never read
- `.wabblespec/memory/provenance/index.json` — patched in place (load → update entry → atomic write)

**Exit codes:** 0 = appended, 1 = bad arguments, 2 = provenance directory not found

---

## Wave 3 — L8 Pipeline

### Script 5: `tracker-update.py`

**What it replaces:** Claude reading `experiments/tracker.json` (~13K tokens in a mature tracker), finding the entry by `blueprint_id`, patching fields, and rewriting. Pure JSON CRUD.

**Pattern:** B — schema-enforced write.

**Tracker entry fields (from current tracker.json):** `blueprint_id`, `run_at`, `metric_name`, `metric_type`, `developer_outcome`, `held_out_cases`, `held_out_value`, `threshold`, `direction`, `verdict`, `failure_note`, `requeue_decision`, `fixture_set`, `golden_ref`, `notes`, `forge_status`, `forge_at`, `forge_receipt`

**Interface:**

```bash
# Show one entry
python _shared/scripts/tracker-update.py show \
  --blueprint-id acceptance-test-executor-enforcement-v1

# Create new tracker entry (after Benchmark runs)
python _shared/scripts/tracker-update.py add \
  --blueprint-id my-new-candidate-v1 \
  --metric-name false_completion_rate \
  --metric-type rate \
  --developer-outcome false_completion \
  --threshold 0.0 \
  --direction lower_is_better \
  --fixture-set .wabblespec/experiments/fixtures/my-new-candidate-v1/ \
  --golden-ref .wabblespec/experiments/fixtures/my-new-candidate-v1/golden.json

# Record benchmark result
python _shared/scripts/tracker-update.py set \
  --blueprint-id my-new-candidate-v1 \
  --held-out-cases 8 \
  --held-out-value 0.0 \
  --verdict PASS \
  --notes "All 8 held-out cases passed..."

# Record forge promotion
python _shared/scripts/tracker-update.py forge \
  --blueprint-id my-new-candidate-v1 \
  --forge-status PROMOTED \
  --forge-receipt .wabblespec/receipts/forge-my-new-candidate-v1-receipt.json

# List all entries with status
python _shared/scripts/tracker-update.py list

# List only entries pending forge
python _shared/scripts/tracker-update.py list --forge-status pending
```

**Exit codes:** 0 = success, 1 = entry not found or bad arguments, 2 = tracker file not readable

---

### Script 6: `fixture-split.py`

**What it replaces:** Claude manually computing the dev/held-out split for benchmark fixtures and writing `split.json` and `golden.json`. Both are fully deterministic from the fixture cases.

**Pattern:** C — aggregate-and-report.

**Interface:**

```bash
# Generate split.json from fixtures.json
python _shared/scripts/fixture-split.py split \
  --fixtures .wabblespec/experiments/fixtures/my-candidate-v1/fixtures.json \
  --seed 4202 \
  --dev-ratio 0.2
# Writes: split.json alongside fixtures.json

# Generate golden.json from fixtures.json (extracts expected_outcome per case)
python _shared/scripts/fixture-split.py golden \
  --fixtures .wabblespec/experiments/fixtures/my-candidate-v1/fixtures.json \
  --outcome-field expected_outcome \
  --eval-fields "expected_missed_test" "expected_error"
# Writes: golden.json alongside fixtures.json

# Both in one pass
python _shared/scripts/fixture-split.py all \
  --fixtures .wabblespec/experiments/fixtures/my-candidate-v1/fixtures.json \
  --seed 4202 \
  --dev-ratio 0.2

# Validate an existing split against its fixtures
python _shared/scripts/fixture-split.py validate \
  --fixtures .wabblespec/experiments/fixtures/my-candidate-v1/fixtures.json
```

**`split.json` output structure (matches existing format):**
```json
{
  "version": "1.0",
  "fixture_set": ".wabblespec/experiments/fixtures/my-candidate-v1/",
  "created_at": "2026-05-26T...",
  "seed": 4202,
  "split_method": "random",
  "total_cases": 10,
  "dev_cases": ["at-001", "at-003"],
  "held_out_cases": ["at-002", "at-004", "at-005", "at-006", "at-007", "at-008", "at-009", "at-010"]
}
```

**Split algorithm:** Shuffle all case IDs using the given seed, take `floor(n * dev_ratio)` as dev (minimum 1), remainder as held-out. With 10 cases and `dev_ratio=0.2`: 2 dev, 8 held-out.

**Exit codes:** 0 = written, 1 = fixtures.json not found or malformed, 2 = output not writable

---

## Wave 4 — Verification and Reporting

### Script 7: `document-check.py`

**What it replaces:** Claude reading a reference document file to check whether a `## Cross-references` section exists and is non-empty. This is a grep — Claude should not load a potentially large reference file just to confirm section presence.

**Pattern:** A — lookup-table (structural pattern matching).

**Interface:**

```bash
# Check cross-references section (reference-type deliverables)
python _shared/scripts/document-check.py \
  --file _shared/references/foo.md \
  --type reference
# output: PASS or CROSS_LINK_MISSING with detail

# Check any document type (returns cross_link_verified: null for non-reference)
python _shared/scripts/document-check.py \
  --file .wabblespec/CHANGELOG.md \
  --type changelog

# Batch check all reference files in a directory
python _shared/scripts/document-check.py \
  --dir _shared/references/ \
  --type reference

# JSON output (for Verifier receipt writing)
python _shared/scripts/document-check.py \
  --file _shared/references/foo.md \
  --type reference \
  --json
```

**JSON output:**
```json
{
  "file": "_shared/references/foo.md",
  "type": "reference",
  "cross_link_checked": true,
  "cross_link_verified": true,
  "cross_link_section_found": true,
  "cross_link_entries": 3,
  "finding": null
}
```

**Checks performed for `--type reference`:**
1. Does `## Cross-references` or `## See also` section exist?
2. Does the section contain at least one non-empty, non-HTML-comment entry?
3. Are entries real links or file references (not just placeholder text)?

**Exit codes:** 0 = PASS or not applicable, 1 = CROSS_LINK_MISSING, 2 = file not found

---

### Script 8: `index-update.py`

**What it replaces:** Claude manually reading validate-graph output, quality-floor-check output, receipts directory contents, and witness.json to rewrite specific sections of `.wabblespec/INDEX.md`. Each source is already scriptable — this aggregates them.

**Pattern:** C — aggregate-and-report.

**Interface:**

```bash
# Regenerate all auto-updated sections from live script outputs
python _shared/scripts/index-update.py

# Update specific sections only
python _shared/scripts/index-update.py --sections modules quality receipts witness

# Dry run — print what would be written
python _shared/scripts/index-update.py --dry-run

# Write JSON summary instead of updating INDEX.md
python _shared/scripts/index-update.py --json
```

**Sections managed by this script (auto-updated):**

| Section | Data source | Update trigger |
|---|---|---|
| `## Active Modules` | `validate-graph.py --json` | Module count |
| `## Quality Floor` | `quality-floor-check.py --json` | Pass rate |
| `## Receipt Archive` | `receipt-index.json` + `receipts/` count | After archive |
| `## Witness` | `archive/witness.json` | After `--record-witness` |
| `## Version` | `.wabblespec/VERSION` | After version bump |

**Sections NOT touched (hand-authored, owned by humans):**
- `## L8 Gate` — human-validated state
- `## Cold-Start Coverage` — annotated notes
- `## Evolution Experiments` — narrative
- `## Planned Tasks` — active planning
- `## Hook System`, `## OMC Extractions`, etc. — reference notes

**Implementation note:** Script replaces only the content between a managed section header and the next `##` header. Uses a marker comment pattern to identify managed sections:
```markdown
<!-- auto-updated: index-update.py -->
96/96 modules PASS both gates...
<!-- end auto-updated -->
```

On first run, wraps the existing content in these markers. Subsequent runs replace between the markers. If markers are absent, appends the section with markers rather than touching existing content.

**Exit codes:** 0 = updated, 1 = INDEX.md not found, 2 = source scripts not runnable

---

## Wave 5 — Orchestration

### Script 9: `pipeline.py`

**What it replaces:** Claude issuing 4–6 separate script invocations in sequence at session boundaries, keeping track of argument threading between them. A thin orchestrator that chains the existing scripts.

**Pattern:** meta — composes existing scripts.

**Two entry points:**

```bash
# START: session open — recipe + session init + witness drift check
python _shared/scripts/pipeline.py start \
  --session-id seed-run-20260526xx \
  --target Framework \
  --complexity Low \
  --confidence 0.97 \
  --detection-method explicit-instruction
```

**What `start` does internally, in order:**
1. `recipe-writer.py` — writes `recipe.json` + `recipe-receipt-{session-id}.json`
2. `session-state.py init` — initializes `session/state.json`
3. `validate-graph.py --check-hashes` — checks for module drift, surfaces any DRIFT warnings
4. Reports: session initialized, recipe written, drift status

```bash
# CLOSE: session end — chain validate + archive + witness update + dream
python _shared/scripts/pipeline.py close \
  --session-id seed-run-20260526xx \
  --summary "Built foo.md and bar.md" \
  --delta-class ADDITIVE \
  --files-delivered "_shared/references/foo.md" "_shared/references/bar.md" \
  [--not-tested "item A"] \
  [--extra '{"total_receipts_accumulated": 102}']
```

**What `close` does internally, in order:**
1. `receipt-chain-validate.py` — validates chain; exits FAIL if chain is incomplete (blocks archive)
2. `archive.py` — writes delivery receipt, appends CHANGELOG, bumps VERSION, updates receipt-index
3. `validate-graph.py --record-witness` — updates witness for any changed modules
4. `index-update.py` — regenerates managed INDEX.md sections
5. `session-state.py complete` — marks session complete in state.json
6. Reports: version bump, receipt count, chain status, any drift

**Dry run for both:**
```bash
python _shared/scripts/pipeline.py start ... --dry-run
python _shared/scripts/pipeline.py close ... --dry-run
```

**Additional subcommands:**

```bash
# Status: show current session state and chain status
python _shared/scripts/pipeline.py status

# Guard pre-wave: layers 4+5 check before a wave
python _shared/scripts/pipeline.py guard \
  --module executor \
  --files "path/to/file.json" \
  --commands "git add -A"
```

**Exit codes:** 0 = all steps succeeded, 1 = a step failed (which step is named in output), 2 = configuration error

**Implementation note:** `pipeline.py` calls scripts via `subprocess.run()` with captured output, not by importing them. This keeps each script independently testable and prevents import-time side effects. Arguments are threaded explicitly — no shared global state between steps.

---

## Non-Goals (what this plan does not automate)

The following remain with Claude and will not be scripted:

| Component | Reason |
|---|---|
| Guard Layers 2–3 | Scope constraint and invariant compliance require understanding the specific task context |
| Specify (writing requirements) | The R1–Rn text is the product of reasoning |
| Decompose (wave sequencing) | Wave order depends on understanding risk and dependency within the task |
| Verifier check content | Judgment about whether a check actually passes requires reading the output |
| Executor wave summary | Synthesizes what was built — reasoning-dependent |
| SKILL.md content | The prose is the value; `module-scaffold.py` already handles structure |
| Synth / Blueprint content | Hypothesis and spec authorship require explicit reasoning |
| Instinct pattern classification | Human-validated by design — automation would defeat the purpose |
| Task card content | The goal/criteria text requires understanding the task |
| Wave plan wave content | Inputs/outputs/checkpoint per wave are judgment calls |

---

## File Locations and Naming

All nine scripts go into `_shared/scripts/` alongside the existing 20.

```
_shared/scripts/
  command-risk-check.py       # Wave 1a
  guard-check.py              # Wave 1b
  drawer-writer.py            # Wave 2a
  provenance-append.py        # Wave 2b
  tracker-update.py           # Wave 3a
  fixture-split.py            # Wave 3b
  document-check.py           # Wave 4a
  index-update.py             # Wave 4b
  pipeline.py                 # Wave 5
```

---

## Acceptance Criteria (per script)

Each script must pass all four checks before being considered done:

1. **`--dry-run` smoke test:** Produces correct output without writing any files.
2. **`--json` mode (where applicable):** Output is valid JSON parseable by Python.
3. **Exit codes correct:** 0/1/2 as specified. Confirmed by running the error path.
4. **Self-consistent with existing scripts:** Reads and writes the same file formats as the rest of the pipeline (receipt schemas, framework.yaml shape, drawer schema, tracker shape).

For `guard-check.py` specifically:
- Layer 4 PASS/FAIL confirmed against at least 3 modules with different `authority.owns` patterns
- `misactivation_risk` fires correctly for at least 1 module with `file_path_patterns`
- Layer 5 correctly delegates BLOCK to `command-risk-check.py`

For `pipeline.py`:
- `start` followed by `close` on a real session produces a valid delivery receipt and bumped version
- A failed `receipt-chain-validate` inside `close` blocks archive and exits 1

---

## Build Order Within Each Wave

Build order within each wave:

**Wave 1:** `command-risk-check.py` first (standalone, no dependencies) → `guard-check.py` second (uses command-risk-check).

**Wave 2:** `drawer-writer.py` and `provenance-append.py` are independent — build in parallel.

**Wave 3:** `fixture-split.py` first (no dependencies) → `tracker-update.py` second (references fixture paths).

**Wave 4:** `document-check.py` and `index-update.py` are independent — build in parallel.

**Wave 5:** `pipeline.py` last — depends on all prior scripts existing and working.

---

## Dependencies

| Script | Requires | Notes |
|---|---|---|
| `command-risk-check.py` | stdlib only | No external deps |
| `guard-check.py` | `command-risk-check.py`, `fnmatch` (stdlib) | Reads skill-rules.json |
| `drawer-writer.py` | stdlib only | Validates against embedded schema subset |
| `provenance-append.py` | stdlib only | Append-only — never reads ledger |
| `tracker-update.py` | stdlib only | JSON CRUD |
| `fixture-split.py` | stdlib only (`random`) | Deterministic from seed |
| `document-check.py` | stdlib only (`re`) | Grep-level markdown parsing |
| `index-update.py` | `validate-graph.py`, `quality-floor-check.py` | Calls as subprocess |
| `pipeline.py` | All prior scripts | Subprocess orchestration |

All scripts require Python 3.8+, which the project already targets. No new `pip install` requirements beyond `pyyaml` (already required by existing scripts).

---

## Relationship to Existing Scripts

The nine new scripts do not replace any existing script. They extend the automation layer into new areas:

```
EXISTING                          NEW (this plan)
─────────────────────────────     ────────────────────────────────
archive.py           ──────────── pipeline.py (orchestrates close)
recipe-writer.py     ──────────── pipeline.py (orchestrates start)
session-state.py     ──────────── pipeline.py (orchestrates start/close)
receipt-chain-validate.py ─────── pipeline.py (orchestrates close)
validate-graph.py    ──────────── index-update.py (calls as subprocess)
                                  pipeline.py (calls for witness update)
quality-floor-check.py ─────────  index-update.py (calls as subprocess)
framework-register.py ──────────  (unchanged — guard-check reads skill-rules
                                   directly, not via framework-register)
markdown-extract.py  ──────────── document-check.py (companion, different concern)
receipt-writer.py    ──────────── (unchanged — guard-check writes guard receipts
                                   using receipt-writer internally)
```

---

## Version Tracking

Each wave completion should be archived using `archive.py` with `--delta-class ADDITIVE`. Expected version progression:

| After | Version |
|---|---|
| Wave 1 (guard) | 0.12.0 |
| Wave 2 (memory) | 0.13.0 |
| Wave 3 (L8) | 0.14.0 |
| Wave 4 (verification) | 0.15.0 |
| Wave 5 (orchestration) | 0.16.0 |

---

*This plan is the implementation spec. Each wave is independently executable. Start with Wave 1.*
