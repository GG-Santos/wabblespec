---
name: wave-review
description: Perform a WabbleSpec native parallel code review. Reads the pending review file prepared by wave-review.py, spawns three parallel Agent subagents (standard correctness, security, design), synthesizes findings via Grader, writes a wave-review receipt to the main receipt chain, routes HIGH/CRITICAL findings through Triage, and writes quality drawers for Dream/entity-graph. Use when the user asks to review a wave or when session-start surfaces a pending review.
---

# wave-review

Perform a WabbleSpec native parallel code review. The diff and context are already
extracted by `wave-review.py` — this skill reviews inline, synthesizes via Grader,
routes through Triage, and feeds Dream/entity-graph.

## Usage

```
/wave-review [--ref HEAD] [--type standard|security|design|multi]
```

## When NOT to use

- User pasted findings already — fix them directly via `/wave-fix`
- A completed receipt exists for this ref and HEAD has not changed
- User asks to fix findings (`/wave-fix`) or iterate (`/wave-refine`)

## IMPORTANT

You perform the review using parallel Agent subagents and the existing Grader for
synthesis. Do not merge findings manually. Do not route findings to Triage yourself —
call Triage as a module. Do not write `finding.schema.json` fields by guessing —
populate all required fields.

## Instructions

### 1. Find the pending review file

```bash
python .wabblespec/engine/shared/scripts/wave-review.py --list
```

If pending: read the JSON at the path shown. It contains `diff`, `review_prompt_template`,
`task_criteria`, `scope_excerpt`, `invariants_excerpt`, `commit_info`.

If none exists: prepare one:

```bash
python .wabblespec/engine/shared/scripts/wave-review.py --ref HEAD
```

### 2. Spawn three parallel Agent subagents

Send all three in a single response (one tool-call turn):

**Agent 1 — Standard:** Use `review_prompt_template`. Review `diff` for correctness,
error handling, robustness, code quality. Ground every finding in explicit diff evidence.

**Agent 2 — Security:** Use `.wabblespec/engine/shared/review/security.txt` criteria.
Review `diff` for trust-boundary failures, injection, secrets, unsafe execution.

**Agent 3 — Design:** Use `.wabblespec/engine/shared/review/design.txt` criteria.
Review `diff` for interface quality, abstraction, state management, spec alignment.

Also check `invariants_excerpt` — any invariant violation is automatically HIGH severity.

Each agent outputs: `VERDICT: PASS|FAIL` and findings as
`[SEVERITY] file:line — description — fix`

### 3. Synthesize via Grader

Pass all three agent outputs to the Grader module:
- `primary_output`: the combined agent findings
- `adversary_counter_analysis`: cross-agent challenges
- `spec_artifact`: `task_criteria` + `scope_excerpt` from the pending file

Grader returns a consolidated ACCEPT/REVISE/ESCALATE verdict and structured findings.

Map Grader output to `finding.schema.json` format:
- `finding_id`: `wave-reviewer-<timestamp>-<index>`
- `severity`: CRITICAL|HIGH|MEDIUM|LOW
- `category`: spec_violation|logic_error|security_gap|design_debt|invariant_breach
- `description`: what the finding is (not the fix)
- `evidence`: exact diff line or path
- `fix_recommendation`: specific, actionable
- `confidence`: 0.85 for multi-agent agreement, 0.7 for single-agent only
- `file`: relative path if file-specific
- `line`: line number if available

Sort: CRITICAL → HIGH → MEDIUM → LOW. Group by file within each tier.

### 4. Write the receipt to the main receipt chain

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type wave-review \
  --task-id <task_id-from-pending> \
  --session-id <session_id-from-pending> \
  --status PASS|FAIL \
  --target <resolved_ref> \
  --summary "<verdict> std:<V> sec:<V> des:<V> | <H>H <M>M <L>L" \
  --confidence 0.88 \
  --out .wabblespec/state/receipts/wave-review-<ref>-<timestamp>.json
```

### 5. Write quality drawers (HIGH/CRITICAL → Dream + entity-graph)

```bash
python .wabblespec/engine/shared/scripts/wave-review.py \
  --write-drawers '<findings-json-array>' \
  --ref <resolved_ref> \
  --session-id <session_id> \
  --task-id <task_id>
```

Findings become FRESH drawers in `wings/quality/`. Dream decays them each session stop;
entity-graph builds file co-occurrence edges. Closed findings go STALE automatically.

### 6. Route through Triage (HIGH/CRITICAL only)

Invoke Triage for each HIGH or CRITICAL finding:
- **security_gap** → Security gateway immediately + severity-based routing
- **spec_violation | invariant_breach** → Interview → Specify (delta) → Executor
- **design_debt** → Clean (COSMETIC) or Specify + Executor (structural)

### 7. Mark complete and post to PR (optional — VCS MCP only)

After marking the review complete, when a GitHub or GitLab MCP server is active in the session AND a PR/MR number is declared in the wave plan or task card, post HIGH and CRITICAL findings as inline review comments:

Use `~~github-mcp` or `~~gitlab-mcp` capability tools. Post only findings at HIGH or CRITICAL severity — MEDIUM and LOW stay in the receipt only.

Format for each comment:
```
[wave-review] <severity> | <category>
<finding.description>

Suggestion: <finding.fix_recommendation>
Confidence: <finding.confidence>
```

Map: `finding.file` → comment file path, `finding.line` → comment line, `finding.description + fix_recommendation` → comment body.

Skip silently when: no VCS MCP active, no PR/MR number in task card, or no HIGH/CRITICAL findings. Do not emit a typed error.

```bash
python .wabblespec/engine/shared/scripts/wave-review.py \
  --complete <ref> --verdict PASS|FAIL \
  --receipt .wabblespec/state/receipts/wave-review-<ref>-<timestamp>.json
```

Present consolidated verdict, per-agent verdicts, finding counts. If FAIL: offer `/wave-fix`.

## Reference Routing

| Situation | Reference |
|---|---|
| GitHub/GitLab MCP PR comment posting (Step 7) | `engine/shared/references/mcp-servers-integration.md` → GitHub MCP section |

## See also

- `/wave-fix` — fix open wave review findings
- `/wave-refine` — iterative fix-review loop
- `/triage` — classify and route individual findings
