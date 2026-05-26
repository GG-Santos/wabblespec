# Instinct Activation Walkthrough

**Script:** `modules/l8/instinct/scripts/instinct.py`  
**Prerequisite:** L8 corpus gate — receipt corpus condition MUST BE MET (100+ receipts) before this walkthrough applies  
**Purpose:** Step-by-step instructions for a human to activate Instinct, review detected patterns, and validate at least 3 to unlock the Synth gate.

---

## What Instinct does

Instinct reads the receipt corpus and detects three types of recurring patterns:

| Pattern type | Detection logic | Threshold |
|---|---|---|
| `high-frequency-failure` | A module's FAIL/PARTIAL rate across its receipts | ≥ 20% failure rate AND ≥ 5 distinct failure receipts |
| `co-occurrence-cluster` | Two modules failing in the same execution wave | ≥ 3 co-occurrences across distinct waves |
| `recurring-gap` | A topic appearing repeatedly in Dream's gap-map.md | ≥ 3 distinct sessions |

Instinct is **read-only** except for writing to `.wabblespec/memory/instinct-observations.md`. It does not alter any module, framework.yaml, or live framework files.

---

## Prerequisites

Before running Instinct, verify:

1. **Receipt count ≥ 100.** The script enforces this internally and will exit with `GATE_NOT_MET` if not met.
2. **entity-graph.json exists** at `.wabblespec/memory/entity-graph.json`. If absent, populate it via EntityGraph first.
3. **No executor PID lock.** The script checks for `.wabblespec/memory/.executor.pid`. Do not run Instinct during an active execution session.

---

## Step 1 — Check gate status

```bash
python modules/l8/instinct/scripts/instinct.py --status
```

Expected output when gate is met:
```
Receipt count: 100/100 required
Entity graph: found
Gate: MET — ready for --activate
```

If `Gate: NOT MET`, the output lists which conditions are unmet. Resolve them before proceeding.

---

## Step 2 — Dry run (preview patterns without writing)

```bash
python modules/l8/instinct/scripts/instinct.py --dry-run
```

This runs all three pattern detection passes and prints a summary without writing to `instinct-observations.md`. Use this to understand what Instinct will detect before committing.

Expected output format:
```
Dry run — N pattern(s) detected (not written)
  [high-frequency-failure] High-frequency failure: {module} confidence=medium
  [co-occurrence-cluster] Co-occurrence cluster: {m1} + {m2} confidence=medium
  [recurring-gap] Recurring gap: {topic} confidence=medium
```

**If 0 patterns detected:** This is valid — it means the corpus is clean. The human-validated patterns condition cannot be met from a run with 0 patterns. Consider whether the gap-map.md has been populated (requires Dream to have run) and whether sufficient real execution failures exist in the corpus.

---

## Step 3 — Activate (write observations)

```bash
python modules/l8/instinct/scripts/instinct.py --activate
```

This writes `.wabblespec/memory/instinct-observations.md`. If the file already exists from a prior run, it is overwritten with the latest analysis.

Expected output:
```
Written: .wabblespec/memory/instinct-observations.md
Patterns detected: N
Human validation required before any pattern can be submitted to Synth.
```

---

## Step 4 — Review instinct-observations.md

Open `.wabblespec/memory/instinct-observations.md`. Each detected pattern has this structure:

```markdown
### Pattern N: {name}

Type: {high-frequency-failure | co-occurrence-cluster | recurring-gap}
Confidence: high | medium
Evidence: {evidence description or receipt paths}
Occurrences: {count}
Human-validated: false

{description paragraph}
```

For each pattern, evaluate:

**Is the pattern genuine or spurious?**

- **Genuine:** The pattern reflects a real structural weakness, coverage gap, or coupling that would benefit from framework evolution. The evidence receipts (when opened) confirm the described behavior. The description explains something non-obvious about how the framework operates in practice.

- **Spurious:** The pattern is an artifact of the seed pipeline rather than real project execution (e.g. a module that appears to fail often because test receipts were generated with PARTIAL status during the testing runs, not because the module is structurally weak). The evidence does not hold up under inspection.

**How to inspect evidence for high-frequency-failure patterns:**

The `evidence` field lists up to 5 receipt paths. Open each:
```bash
# Windows PowerShell
Get-Content ".wabblespec/receipts/{receipt-filename}"
```
Verify the listed receipts actually have `"status": "FAIL"` or `"status": "PARTIAL"` and that the failure was genuine (not a test artifact).

**How to inspect evidence for co-occurrence-cluster patterns:**

Check whether the two co-failing modules have a known dependency relationship. If they share an upstream input and that input was bad in the failing waves, the cluster reflects a propagation artifact — not independent coupling.

**How to inspect evidence for recurring-gap patterns:**

Open `.wabblespec/memory/gap-map.md`. Verify the topic appears with low confidence across multiple session entries, not just once or in a single burst.

---

## Step 5 — Validate genuine patterns

For each pattern you judge to be genuine, change the `Human-validated` field:

```markdown
Human-validated: false
```
→
```markdown
Human-validated: true
```

Add a brief note below the `Human-validated: true` line explaining why you validated it:

```markdown
Human-validated: true
Validation note: {one sentence rationale — why this is a real pattern worth addressing}
```

**Requirement:** At least 3 patterns must have `Human-validated: true` before Synth can activate.

**Do not validate patterns you are uncertain about.** A spurious pattern promoted to Synth will result in framework evolution proposals that do not reflect real behavior. It is better to have fewer validated patterns and re-run Instinct after more real execution sessions accumulate.

---

## Step 6 — Confirm the gate condition is met

After validating at least 3 patterns, update `_shared/references/l8-corpus-gate.md`:

1. Set `gate_status: MET` in the frontmatter.
2. Update the `Human-validated patterns` row: `3+ patterns, Human-validated: true` — YES.
3. Update `last_evaluated` to today's date.

```bash
# Verify the count of validated patterns before updating the gate document
grep "Human-validated: true" .wabblespec/memory/instinct-observations.md | wc -l
```

---

## Step 7 — Synth is now authorized to activate

Once the gate document shows all conditions MET, Synth may activate. Synth reads `instinct-observations.md` and proposes framework evolution candidates based on the validated patterns.

**Synth's scope** (before gate met, Synth is read-only):
- After gate met: Synth may propose changes to `_shared/`, module SKILL.md files, and `framework.yaml`
- Any Blueprint → Forge promotion still requires explicit human sign-off (Forge Attestation condition in the gate)
- Synth does NOT promote changes automatically — every proposal requires human review

---

## Pattern quality heuristics

Use these to distinguish genuine from spurious patterns during review:

| Signal | Suggests genuine | Suggests spurious |
|---|---|---|
| Evidence receipts span multiple dates | Yes | No — single burst |
| Failure mode matches a known module weakness documented in acceptance tests | Yes | No |
| Co-occurring modules have no documented relationship | Yes (coupling) | No — known propagation |
| Gap topic appears in dream-log.json with low confidence across sessions | Yes | No — appears once |
| Pattern would be actionable (a concrete change would address it) | Yes | No — unfixable or already known |
| Pattern matches the benchmark schema `developer_outcome` field | Yes | No |

---

## Troubleshooting

**`GATE_NOT_MET: Receipt count N < 100 required`**  
More receipts needed. Check `python instinct.py --status` for exact count.

**`GATE_NOT_MET: entity-graph.json not found`**  
Run EntityGraph to populate the entity graph before Instinct.

**`GATE_NOT_MET: Executor PID lock active`**  
An execution session is in progress. Wait for it to complete and the PID file to clear.

**`No patterns detected above threshold`**  
The corpus is clean at current thresholds. Options:
- Verify gap-map.md has content (requires Dream to have run at least 3 sessions)
- Accumulate more real execution sessions with genuine failures to raise counts above threshold
- Run `--dry-run` with lower thresholds by modifying the script constants temporarily (document any threshold changes)

**Pattern count < 3 after --activate**  
Cannot validate 3 patterns if fewer than 3 are detected. See "No patterns detected" above.

---

## Cross-references

- `modules/l8/instinct/scripts/instinct.py` — the implementation
- `_shared/references/l8-corpus-gate.md` — gate conditions; update after validation
- `.wabblespec/memory/instinct-observations.md` — written by --activate; edit to add Human-validated: true
- `.wabblespec/memory/gap-map.md` — Dream's gap map; source for recurring-gap pattern detection
- `.wabblespec/memory/entity-graph.json` — required for Instinct gate check
- `modules/l8/synth/SKILL.md` — what Synth does with validated patterns
