---
name: archive
description: Finalizes a completed execution by aggregating all receipts into one delivery receipt, bumping the version, and appending a changelog entry. A task is not done until Archive runs.
---

# Archive

A task is not complete until you run. You are the permanent record. You read every receipt produced during this execution, compile a not-tested list, determine the version bump, and write the delivery receipt. Implied completion is prohibited (I10) — you make completion provable and auditable.

## What this skill does

Reads all receipts from the current execution session. Compiles `not_tested` items from every receipt into a consolidated list. Determines version bump from change classifications. Delegates all file I/O (CHANGELOG append, VERSION bump, delivery receipt write, receipt-index patch) to `archive.py`. All prior receipts remain untouched — Archive never deletes.

## Reference Routing

| Situation | Reference |
|---|---|
| CHANGELOG append, VERSION bump, delivery receipt write, receipt-index patch | `engine/shared/references/script-delegation-contract.md` |
| Linear ticket closure (Step 7b) | `engine/shared/references/mcp-servers-integration.md` → Linear section |

## When to use / when not to use

**Use when:**
- Executor signals full execution complete (all waves passed Verifier)
- Explicit `/archive` command targeting a completed execution

**Do not use when:**
- Any wave receipt is missing (gap in the receipt chain)
- Any wave receipt has status FAIL (execution not complete)
- Verifier has not issued PASS for all waves

## Inputs

- All receipts in `.wabblespec/state/receipts/` written during this session (for not-tested aggregation)
- `.wabblespec/VERSION` and `.wabblespec/CHANGELOG.md` — accessed by `archive.py` directly; not loaded into Claude context

## Receipt index

Archive maintains `.wabblespec/state/archive/receipt-index.json` as a queryable audit record across all executions. Schema: `schemas/receipt-index.schema.json`.

**Query use cases the index enables:**
- All tasks with `status=FAIL` — find incomplete executions
- All tasks where `receipts_by_module.<module>.status=FAIL` — find which module failed across sessions
- All tasks with non-empty `not_tested_list` — scope future work
- All tasks with `status=IN_PROGRESS` — find orphaned sessions

**Status transitions:**

| Transition | When |
|---|---|
| (none) → PENDING | ScopeFrame not yet run — entry created by Recipe |
| PENDING → IN_PROGRESS | ScopeFrame receipt written |
| IN_PROGRESS → PASS | Archive writes delivery receipt, all_waves_passed = true |
| IN_PROGRESS → FAIL | Archive writes delivery receipt, missing receipts or wave FAIL |
| IN_PROGRESS → BLOCKED | Escalation gate fires — human input required |
| BLOCKED → IN_PROGRESS | Human resolves block, execution resumes |

The index is never deleted. FAIL entries are audit evidence, not garbage.

---

## How to do it

### Step 0 — Initialize or update receipt index

Read `.wabblespec/state/archive/receipt-index.json`. If absent: create it with `index_version: 1`, empty `tasks[]`.

Find or create the index entry for the current `task_id`:
- If no entry exists: create PENDING entry with `started_at` = ScopeFrame receipt timestamp, `waves_planned` from decompose receipt, `receipts_by_module` keys from required receipt list (all PENDING)
- If entry exists: update in place — do not duplicate

Update `receipts_by_module` status for all receipts already written this session. Modules with written receipts: PASS. Modules not yet run: PENDING. Modules not applicable: SKIP.

Write updated index back before proceeding to Step 1.

### Step 1 — Gather all receipts

Read every receipt written during this execution. Required receipts:
- `scopeframe-receipt.json`
- `specify-receipt.json`
- `decompose-receipt.json`
- `guard-wave-*-receipt.json` (one per wave)
- `wave-*-receipt.json` (one per wave)
- `verification-wave-*-*.json` (one per wave)
- `execution-receipt.json`
- `reviewer-receipt-*.json` (if Reviewer ran — include all)

If any required receipt is missing: FAIL. Record which receipt is absent in the delivery receipt failure reason. Do not compose a delivery receipt with gaps in the chain.

### Step 2 — Compile not-tested list

Read the `not_tested` field from every receipt. Aggregate all items into one list. Deduplicate exact duplicates but preserve distinct items even if similar. This list appears verbatim in the delivery receipt.

No items are minimized, summarized away, or hidden. Delivery is not blocked by not-tested items — they are recorded, not resolved. They become the starting scope for the next related session.

### Step 3 — Run archive.py

Provide the reasoning-dependent arguments. The script handles all file I/O without loading CHANGELOG or VERSION into context.

```bash
python .wabblespec/engine/shared/scripts/archive.py \
  --session-id <current-session-id> \
  --task-id <task-id> \
  --summary "<one-sentence description of what was built this session>" \
  --delta-class ADDITIVE|COSMETIC|BREAKING \
  --files-delivered "<path1>" "<path2>" \
  --waves-completed <N> \
  [--not-tested "item A" "item B"]
```

**Claude provides:**
- `--summary` — synthesize from wave receipts: what was produced and why
- `--delta-class` — derive from the highest change class in any wave receipt (`BREAKING` > `ADDITIVE` > `COSMETIC`)
- `--files-delivered` — union of `files_written` fields from all wave receipts in this session
- `--waves-completed` — count of waves with status PASS
- `--not-tested` — aggregated not-tested list from Step 2 (one `--not-tested` arg per item)

**Script handles:** CHANGELOG append (write-only, never read into context), VERSION semver bump, delivery receipt JSON write, receipt-index patch.

See `engine/shared/references/script-delegation-contract.md` for full flag reference and optional args (`--extra`, `--dry-run`).

### Step 6b — Drift signal scoring

Before composing the final report, score the archive urgency to calibrate the language used when surfacing Archive to the user or when surfacing it in the executor closeout packet.

Count how many of these signals are present:
- **(a)** Total files touched across all wave receipts is high (more than 5 distinct files)
- **(b)** Any framework or protocol file was touched: `.claude/`, `.wabblespec/engine/`, any `SKILL.md`, `skill-rules.json`, `schema/*.json`, or a `references/*.md` file
- **(c)** Session involved 3 or more memory-worthy observations (drawers written, instinct records updated, entity graph modified)

| Score | Urgency | Surface as |
|---|---|---|
| 0–1 signals | LOW | "Archive available if you want." |
| 2 signals | MEDIUM | "Recommend Archive -- significant changes detected." |
| 3+ signals | HIGH | "Strongly recommend Archive -- framework files touched." |

Record the score and label in the delivery receipt under `archive_urgency`.

### Step 7 — Report to user

Surface: version bumped from X to Y, N receipts aggregated, not-tested count, drift signal score and urgency label. Provide delivery receipt path. If not-tested list is non-empty, name the items — they are actionable future scope.

### Step 7b — Linear ticket closure (optional — Linear MCP only)

After writing the delivery receipt, when `linear_issue_id` is present in the task card AND Linear MCP is available:

1. Invoke `linear_update_issue_status` with `issue_id: <linear_issue_id>`, `status: "Done"`
2. Post the delivery receipt path as a comment on the Linear issue: `linear_create_comment issue_id: <id> body: "WabbleSpec archive complete. Delivery receipt: <path>. Version: <new_version>."`
3. Record in the delivery receipt: `linear_ticket_closed: true`, `linear_issue_id: "<id>"`

Skip silently when: Linear MCP unavailable, `linear_issue_id` absent from task card, or the Linear call returns an error. Do not block archiving on Linear sync failure. Record `linear_ticket_closed: false` with reason when skipped.

See `engine/shared/references/mcp-servers-integration.md` → Linear section for full call patterns.

### Step 8 — Shift trigger (post-archive hook)

After writing the delivery receipt, check if any receipt in this session has `delta_class = BREAKING` or `delta_class = ADDITIVE` with a spec artifact touched (any SKILL.md, schema, or rules file modified).

If yes: invoke `modules/l1/shift` with:
- `spec_before`: previous version of the spec artifact (from git history or prior archive)
- `spec_after`: current spec artifact path

Record the following additive fields in the delivery receipt:
```json
{
  "shift_triggered": "boolean",
  "shift_receipt_path": "string — path to shift receipt, null if shift_triggered = false"
}
```

Do not block archiving on Shift completion. Shift runs after the delivery receipt is written.

### Step 9 — Sweep mode (--sweep)

When invoked with `--sweep`: scan `.wabblespec/state/archive/receipt-index.json` for entries with staleness state `EXPIRED` (≥ 50 changes since last touch).

Batch-entomb all EXPIRED entries in one operation:
- Update their `status` to `ARCHIVED_STALE`
- Record `swept_at` timestamp on each entry
- Write updated index

Record the following additive field in the delivery receipt:
```json
{
  "swept_count": "integer — entries swept; 0 if --sweep not used or no EXPIRED entries found"
}
```

### Step 10 — Nexus refresh hook (post-archive)

Before invoking graph-builder.py, run a pre-check: collect the union of `files_written` fields from all wave receipts in this session. Check whether any entry matches a framework-graph-relevant pattern:

- Path starts with `modules/` **and** ends with `SKILL.md` or `skill-rules.json`
- Path starts with `.wabblespec/engine/shared/schemas/` **and** ends with `.json`
- Exact match: `framework.yaml`

Path matching is prefix/suffix — `src/modules/feature.py` does **not** match. Only paths rooted at `modules/` qualify.

**If no file matches:** skip graph-builder.py. Record `nexus_refreshed: false`, `nexus_skip_reason: "no-framework-files-modified"`. Do not invoke graph-builder.py.

**If any file matches:** invoke `modules/l5/nexus/scripts/graph-builder.py --scope {matched-files}` for dependency edges only (not full graph reconstruction). Record `nexus_refreshed: true`, `nexus_skip_reason: null`.

**If Nexus graph does not exist yet (first archive run):** skip regardless of file matches. Record `nexus_refreshed: false`, `nexus_skip_reason: "nexus-not-initialized"`. Do not fail archiving.

Record the following additive fields in the delivery receipt:
```json
{
  "nexus_refreshed": "boolean — true if graph-builder.py ran successfully",
  "nexus_skip_reason": "string — null when nexus_refreshed=true; 'no-framework-files-modified' or 'nexus-not-initialized' when false"
}
```

## Output contract

**delivery-receipt** (`.wabblespec/state/receipts/delivery-receipt-<timestamp>.json`):

Base receipt schema. Extension fields:
```json
{
  "receipts_aggregated": "integer",
  "not_tested_items": "integer",
  "version_previous": "string",
  "version_new": "string",
  "version_bump_reason": "BREAKING|ADDITIVE|COSMETIC",
  "waves_completed": "integer",
  "all_waves_passed": "boolean",
  "nexus_refreshed": "boolean — true if graph-builder.py ran successfully this session",
  "nexus_skip_reason": "string — null when nexus_refreshed=true; 'no-framework-files-modified' or 'nexus-not-initialized' when false"
}
```

**VERSION** (`.wabblespec/VERSION`): plain text semver string, e.g. `0.2.0`. Single line, no trailing newline needed.

**CHANGELOG.md** (`.wabblespec/CHANGELOG.md`): append-only. New entry prepended at top (most recent first) or appended at bottom — be consistent with any existing format. Never modify existing entries.

## When to Suppress Optional Output

Archive produces several optional output blocks: the not-tested summary, the drift signal score label, and the Shift trigger record. Suppress these blocks in the following conditions — they add noise without informational value:

| Condition | Blocks to suppress |
|---|---|
| Zero not-tested items across all receipts | Omit the not-tested summary section entirely. A `not_tested_items: 0` field in the receipt is sufficient. |
| Single-wave task with no SKILL.md or schema file touched | Omit the drift signal scoring language ("Recommend Archive…"). Just write the receipt and state version. |
| Dry-run invocation (`--dry-run` flag on archive.py) | Omit the "Archive complete" user-facing message. The dry-run output is its own confirmation. |
| Shift did not trigger (no BREAKING or ADDITIVE spec artifact change) | Omit the Shift trigger record from the user-facing report. It appears in the receipt but is not surfaced in conversation. |

Suppression applies only to the user-facing output, not to the receipt fields. Receipt fields are always written in full regardless of suppression rules.

## A note on common failure modes

1. **Declaring complete with missing receipts.** Count the expected receipts before composing the delivery receipt. One missing wave receipt means the execution chain is broken. Surface the gap rather than composing a partial delivery receipt.

2. **Hiding not-tested items.** If a receipt says `not_tested: ["edge case X", "performance under load"]`, those appear in the delivery receipt exactly as written. Never summarize them. The not-tested list is how future sessions know what was deferred.

3. **Treating Archive as optional admin.** Archive is the completion gate. A session that ends without an Archive receipt did not officially complete. The hook in `.claude/settings.json` will surface this as a missing receipt at the next session start.
