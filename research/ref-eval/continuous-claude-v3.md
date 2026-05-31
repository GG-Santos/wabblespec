# Ref-Eval: continuous-claude-v3

**Reference path:** `C:\Users\Kirsten\Downloads\Orchestrator\Continuous-Claude-v3`
**Evaluated:** 2026-05-30
**Trust level:** MEDIUM
**Classification:** supporting-reference

---

## Step 1b — File Inventory

| Path | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| `.claude/hooks/README.md` | Hooks overview and setup | small | Architecture diagram, hook event types, setup steps | Read |
| `.claude/hooks/CONFIG.md` | Configuration guide | medium | Settings.json patterns, customization, troubleshooting | Read |
| `.claude/hooks/src/session-start-continuity.ts` | Session resume / handoff lookup | large | UUID-isolated handoff directories, 3-priority lookup, YAML field extraction | Read |
| `.claude/hooks/src/pre-compact-continuity.ts` | Pre-compact handoff generation | medium | Transcript parsing, YAML auto-handoff writer, ledger append | Read |
| `.claude/hooks/src/skill-activation-prompt.ts` | Skill routing on prompt submit | large | Pattern inference, PATTERN_AGENT_MAP (11 entries), LLM validation pass | Read (partial) |
| `.claude/hooks/src/shared/skill-router-types.ts` | TypeScript type schema | small | SkillRule, SkillLookupResult, prerequisite/co-activation fields | Read |
| `.claude/agents/maestro.md` | Multi-agent orchestration coordinator | medium | 5 pattern types, agent dispatch, synthesis protocol, agent reference table | Read |
| `.claude/agents/kraken.md` | TDD implementation agent | medium | 4-state checkpoint machine, validation before advance rule, resume detection | Read |
| `.claude/agents/phoenix.md` | Refactoring and migration planner | medium | Erotetic check, phase output format, backward compatibility table | Read |
| `.claude/agents/aegis.md` | Security analysis agent | medium | Erotetic check, security checklist, risk-ranked findings format | Read |
| `.claude/agents/atlas.md` | E2E and acceptance testing | medium | E2E framework detection, scenario pass/fail format, artifact capture | Read |
| `.claude/rules/dynamic-recall.md` | Memory recall protocol | small | RRF hybrid search, 7 learning types, score interpretation table | Read |
| `.claude/rules/proactive-delegation.md` | Delegation decision rules | small | Pattern detection table, "main context = coordination only" rule | Read |
| `.claude/rules/claim-verification.md` | Claim verification protocol | small | 3 confidence markers, two-pass audit pattern, false-claim taxonomy | Read |
| `.claude/rules/agent-model-selection.md` | Model selection guidance | small | Model hardcoded names, per-agent model recommendations | Read |
| `.claude/rules/no-haiku.md` | Model restriction rule | tiny | Contains model name `haiku` — I6 violation | Read |
| `.claude/hooks/dist/**` | Compiled JS output | large (many) | Identical semantics to `src/` | Skipped — redundant with src/ |
| `.claude/hooks/src/patterns/**` (12 files) | Pattern implementations (TS) | large (each) | Swarm, hierarchical, pipeline, generator-critic, adversarial, map-reduce, jury, blackboard, circuit-breaker, chain-of-responsibility, event-driven | Skipped — too large; sampled via maestro.md |
| `.claude/backup/**` | Deprecated braintrust integration | medium | Legacy hook attempt | Skipped — explicitly deprecated |
| `.claude/runtime/**` | Python MCP client harness | large | MCP schema discovery, harness.py, generate_wrappers.py | Skipped — not behavioral |
| `.claude/scripts/**` | Operational shell/Python scripts | varies | Status, aggregation, tldr scripts | Skipped — project-specific |
| `.claude/servers/**` | MCP server implementations | varies | ast-grep, fetch, firecrawl, git, morph, nia | Skipped — vendor implementations |
| Remaining 20+ agent `.md` files | Specialized agents | small-medium | Role descriptions, tool declarations, output formats | Skipped — sampled 5 representative agents |

---

## Step 1c — Connection Map

```
[session-start-continuity.ts] --reads--> thoughts/shared/handoffs/{sessionName}-{uuidShort}/*.{md,yaml,yml}
[session-start-continuity.ts] --reads--> .claude/tsc-cache/{session_id}/edited-files.log
[pre-compact-continuity.ts]   --reads--> thoughts/ledgers/CONTINUITY_CLAUDE-*.md
[pre-compact-continuity.ts]   --writes--> thoughts/shared/handoffs/{sessionName}/auto-handoff-{ts}.yaml
[pre-compact-continuity.ts]   --calls--> transcript-parser.ts:parseTranscript(transcript_path)
[pre-compact-continuity.ts]   --calls--> transcript-parser.ts:generateAutoHandoff(summary, sessionName)
[skill-activation-prompt.ts]  --reads--> skill-rules.json (promptTriggers.keywords, intentPatterns)
[skill-activation-prompt.ts]  --calls--> shared/resource-reader.ts:readResourceState()
[skill-activation-prompt.ts]  --calls--> skill-validation-prompt.ts:shouldValidateWithLLM()
[skill-activation-prompt.ts]  --calls--> scripts/agentica_patterns/pattern_inference.py (if exists)
[pattern-orchestrator.ts]     --dispatches--> patterns/*.ts (12 named patterns)
[daemon-client.ts]            --manages--> memory daemon (PostgreSQL/SQLite)
[rules/dynamic-recall.md]     --calls--> scripts/core/recall_learnings.py (Hybrid RRF search)
[rules/dynamic-recall.md]     --calls--> scripts/core/store_learning.py (7 type taxonomy)
[agents/*.md]                 --writes--> .claude/cache/agents/{name}/output-{timestamp}.md
[agents/*.md]                 --call--> rp-cli (external binary, not portable)
[agents/kraken.md]            --reads/writes--> thoughts/shared/handoffs/{task}/current.md (checkpoints)
```

**Contract violations if broken:**
- If `session-start-continuity.ts` changes UUID format → handoff lookup fails silently (no match found)
- If agents stop writing to `.claude/cache/agents/{name}/output-{timestamp}.md` → maestro synthesis breaks
- If `skill-rules.json` format changes → `skill-activation-prompt.ts` matches nothing
- If `transcript_path` is absent → `pre-compact-continuity.ts` falls back to legacy tsc-cache summary

---

## Dimension Extraction

### Dimension 1 — Behavior

**Session continuity lookup (3-priority algorithm):**
1. Exact UUID match: `{sessionName}-{uuidShort}` where `uuidShort = sessionId.replace(/-/g,'').slice(0,8)`
2. Legacy path: `{sessionName}/` (no UUID suffix)
3. Any UUID-suffixed dir for same session name, sorted by mtime descending

**Handoff content contract (`extractYamlFields`):**
- Parses `goal: <text>` and `now: <text>` from YAML handoff files
- Returns `{ goal, now }` or null if neither found

**Pre-compact behavior:**
- `trigger === 'auto'` → parse transcript → write YAML handoff → append brief summary to ledger
- `trigger === 'manual'` → warn user only (cannot block)
- Brief summary built from: edited-files.log + build pass/fail counts from `.git/claude/branches/*/attempts.jsonl`
- Written to `thoughts/ledgers/CONTINUITY_CLAUDE-{sessionName}.md` under `## State` before `- Now:` anchor

**Checkpoint state machine (kraken agent):**
- States: `○ PENDING`, `→ IN_PROGRESS`, `✓ VALIDATED`, `✗ FAILED`
- Transitions: PENDING → IN_PROGRESS → VALIDATED | FAILED → IN_PROGRESS (retry)
- Validation JSON block embedded in handoff: `{ test_count, tests_passing, files_modified, last_test_command, last_test_exit_code }`
- Rule: NEVER advance phase without running validation command and checking exit code

**Pattern-to-agent routing (PATTERN_AGENT_MAP):**
```
swarm → research-agent
hierarchical → kraken
pipeline → kraken
generator_critic → review-agent
adversarial → validate-agent
map_reduce → kraken
jury → validate-agent
blackboard → maestro
circuit_breaker → kraken
chain_of_responsibility → maestro
event_driven → kraken
```

**Memory learning taxonomy (7 types):**
`ARCHITECTURAL_DECISION`, `WORKING_SOLUTION`, `CODEBASE_PATTERN`, `FAILED_APPROACH`, `ERROR_FIX`, `USER_PREFERENCE`, `OPEN_THREAD`

**Claim verification markers:**
- `✓ VERIFIED` — Read the file, traced the code (safe to assert)
- `? INFERRED` — Based on grep/search pattern (must verify before claiming)
- `✗ UNCERTAIN` — Haven't checked (must investigate)

**Two-pass audit protocol:**
- Pass 1: Hypotheses (`? INFERRED`) from grep/search
- Pass 2: File read → verify → upgrade to `✓ VERIFIED` or downgrade to `✗ UNCERTAIN`

**Proactive delegation thresholds:**
- Reading 3+ files → spawn scout agent
- External research needed → spawn oracle agent
- Implementation task → route to kraken/spark
- Running tests → route to validator/arbiter

**Epistemic reminder hook:** Injected after Grep results (via `epistemic-reminder` hook) — warns against trusting grep without file read.

**Erotetic Check (E(X,Q)) used by:** phoenix, aegis, atlas, maestro — frame `X = target` and `Q = questions to answer` before acting.

### Dimension 2 — Format

**Agent frontmatter schema:**
```
---
name: <agent-name>
description: <one-line role>
model: opus | sonnet | haiku
tools: [Read, Bash, Grep, Glob, Task, Edit, Write]
---
```

**Agent output file naming:** `.claude/cache/agents/{name}/output-{timestamp}.md`

**Handoff YAML fields:** `goal:`, `now:` (required for session-start injection)

**Checkpoint section format in handoff:**
```markdown
## Checkpoints
**Task:** <description>
**Started:** <ISO timestamp>
**Last Updated:** <ISO timestamp>

### Phase Status
- Phase 1 (Tests Written): ✓ VALIDATED (15 tests passing)
- Phase 2 (Implementation): → IN_PROGRESS (started <timestamp>)
- Phase 3 (Refactoring): ○ PENDING

### Validation State
```json
{ "test_count": N, "tests_passing": N, "files_modified": [...], "last_test_command": "...", "last_test_exit_code": 0 }
```

### Resume Context
- Current focus: <exact step>
- Next action: <next step>
- Blockers: <blockers>
```

**SkillRule schema (skill-rules.json):**
```json
{
  "version": "...",
  "skills": {
    "<name>": {
      "type": "guardrail|domain|workflow|meta|process|exploration|research|planning|validation|debugging|development",
      "enforcement": "block|suggest|warn|require|auto",
      "priority": "critical|high|medium|low",
      "promptTriggers": { "keywords": [...], "intentPatterns": [...] },
      "prerequisites": { "suggest": [...], "require": [...] },
      "coActivate": [...],
      "coActivateMode": "all|any",
      "loading": "lazy|eager|eager-prerequisites"
    }
  }
}
```

**Proactive delegation detection table format:**
```
| Pattern | Signal | Action |
| Multiple tasks | "X and Y", "also", comma-separated | Suggest parallel agents |
```

### Dimension 3 — Interactions

**session-start-continuity → handoff files:**
- Producer: `pre-compact-continuity.ts` writes YAML with `goal:` and `now:` fields
- Consumer: `session-start-continuity.ts` parses `goal:` and `now:` via regex `^goal:\s*(.+)$`
- Break condition: If producer writes non-standard YAML key names, consumer returns null and session starts without context

**skill-activation-prompt → skill-rules.json:**
- Producer: human author writes skill-rules.json with `promptTriggers.keywords` and `intentPatterns`
- Consumer: skill-activation-prompt.ts reads and matches against user prompt
- Break condition: Missing or malformed skill-rules.json → no skills suggested

**agents → maestro synthesis:**
- Producer: each agent writes to `.claude/cache/agents/{name}/output-{timestamp}.md`
- Consumer: maestro reads `ls -t .claude/cache/agents/{name}/output-*.md | head -1`
- Break condition: Agent does not write file → maestro synthesis has no data

**kraken checkpoints → resume:**
- Producer: kraken writes `## Checkpoints` section with state symbols
- Consumer: kraken on resume reads checkpoint, finds `→ IN_PROGRESS`, resumes
- Break condition: Checkpoint not updated → resume starts over from beginning

---

## Section 1 — Reference Summary

**Type:** Production multi-agent orchestration framework for Claude Code. Not a tutorial or boilerplate — actively developed with 14+ TypeScript test files, compiled dist/, and real usage evidence.

**Problem it solves:** Maintains context continuity across Claude Code sessions through session handoffs, provides specialized subagent delegation, routes skill activation via hooks, and persists learnings in a semantic memory backend.

**Behavioral content:** 5 named orchestration patterns (hierarchical, pipeline, swarm, generator-critic, jury), 4-state checkpoint machine for implementation agents, claim verification protocol (3 markers), proactive delegation decision rules with 5 pattern types, memory taxonomy with 7 learning types.

**Structural content:** Agent frontmatter schema with explicit model/tool declarations, output file convention at `.claude/cache/agents/{name}/output-{timestamp}.md`, YAML handoff format with `goal:`/`now:` contract, TypeScript hooks compiled to pre-bundled dist/.

**Interaction content:** UUID-isolated handoff directories protect against session cross-pollination; skill-rules.json is the shared config between hook and prompt; agent output files are the cross-agent handoff mechanism; checkpoint JSON blocks are the resume state contract.

**Maturity:** High. TypeScript source + compiled dist, 14 test files with vitest, real handoff files present, active session state. Red flags: `rp-cli` external binary dependency not portable; multiple `.backup` files; PostgreSQL for memory.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `rules/claim-verification.md` | 3-marker claim verification protocol (✓ VERIFIED, ? INFERRED, ✗ UNCERTAIN) + two-pass audit | Adversary currently issues findings without confidence grading; markers let reviewer distinguish verified from inferred claims | Add `## Claim Confidence Protocol` to `adversary/SKILL.md` with the 3 markers and two-pass pattern | High |
| `agents/kraken.md:Step 5` | Checkpoint state symbols (○ PENDING, → IN_PROGRESS, ✓ VALIDATED, ✗ FAILED) with JSON validation state block | Executor wave states are described narratively; explicit symbols + embedded JSON validation state makes wave progress machine-readable and resumable | Add `## Wave State Symbols` to `executor/SKILL.md`; use symbols in wave plan display | High |
| `agents/phoenix.md`, `agents/aegis.md` | Erotetic Check (E(X,Q)) — frame `X = target`, `Q = questions to answer` before acting | Guard and executor start work without an explicit pre-condition question inventory; this makes the gap explicit and forces enumeration before execution | Add `## Pre-Execution Erotetic Frame` to `guard/SKILL.md` with E(X,Q) protocol | Medium |
| `hooks/src/session-start-continuity.ts:extractYamlFields` + `pre-compact-continuity.ts` | YAML handoff format with `goal:` and `now:` fields as the continuity contract | Current stop-hook writes session state informally; a two-field YAML contract (`goal:`/`now:`) would be machine-parseable by next session's SessionStart hook | Add `goal:` / `now:` YAML fields to our stop-hook output format and make session-start hook parse them | Medium |
| `rules/proactive-delegation.md` | Delegation decision table with explicit thresholds (3+ files → scout, external research → oracle) | Autopilot and executor make delegation decisions implicitly; explicit thresholds reduce inconsistency across runs | Add delegation threshold table to `autopilot/SKILL.md` and `executor/SKILL.md` | Medium |
| `rules/dynamic-recall.md` | 7-type memory learning taxonomy | Our instinct observation types are unstructured; a named taxonomy (`ARCHITECTURAL_DECISION`, `WORKING_SOLUTION`, `FAILED_APPROACH`, etc.) would make instinct indexing and retrieval more precise | Add taxonomy to `memory/SKILL.md` and update drawer writing conventions | Low |
| `agents/maestro.md:Step 3` | 5 named orchestration patterns with agent routing table | Autopilot selects execution mode informally; naming the patterns and associating them with executor behaviors makes mode selection reproducible | Add `## Orchestration Patterns` table to `autopilot/SKILL.md` | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| All agent `.md` frontmatter: `model: opus`, `model: sonnet`, `model: haiku` | Model name hardcoding violates I6 (RUNTIME IS VENDOR-NEUTRAL) | If any of these patterns were copied into WabbleSpec framework files, it would fail the quality floor Gate 1 check and corrupt the invariant | Exclude all model name values; use capability descriptors only | Critical |
| `rules/no-haiku.md` | File name and content embed model name `haiku` — I6 violation | Copying this rule file would embed a vendor model name in the framework | Exclude entirely | Critical |
| `rules/agent-model-selection.md` | Rule body references `Haiku`, `Opus`, `Sonnet` by name | Same I6 violation | Exclude the rule body; keep only the principle (use omit/inherit-parent) | High |
| All agents | `rp-cli` external binary dependency throughout | We do not have `rp-cli`; any adopted agent spec that references it would produce dead tool calls | Exclude all `rp-cli` references; our tools are Grep/Glob/Read | High |
| `rules/dynamic-recall.md` | PostgreSQL + BGE embeddings (`bge-large-en-v1.5`, 1024-dim) memory backend | Heavy external dependency; our memory layer uses file-based drawers and DuckDB | Adopt only the taxonomy and query interface concepts, not the implementation | Medium |
| `CLAUDE_OPC_DIR` environment variable | All memory scripts require `$CLAUDE_OPC_DIR` — project-specific | Not portable to WabbleSpec | Exclude all `CLAUDE_OPC_DIR` references | Medium |
| `.claude/cache/agents/{name}/output-{timestamp}.md` | Agent output file protocol conflicts with WabbleSpec's receipt model | WabbleSpec uses `receipts/*.json` as the operational artifact; a second informal output-file convention adds ambiguity | Exclude the output-file convention; receipt-writer.py is the canonical artifact path | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Claim verification markers (✓ VERIFIED, ? INFERRED, ✗ UNCERTAIN) | Adapt | No I6 conflict; direct behavioral addition | `adversary/SKILL.md` | High |
| Checkpoint state symbols (○ → ✓ ✗) + JSON validation state | Adapt | No I6 conflict; enriches wave state representation | `executor/SKILL.md` | High |
| Erotetic Check E(X,Q) framing | Adapt | No I6 conflict; adds pre-condition questioning | `guard/SKILL.md` | Medium |
| YAML handoff `goal:`/`now:` contract | Adapt | No I6 conflict; machine-parseable continuity | stop-hook + session-start hook | Medium |
| Proactive delegation threshold table | Adapt | No I6 conflict; makes delegation decisions explicit | `autopilot/SKILL.md` | Medium |
| 7-type memory learning taxonomy | Adapt | No I6 conflict; structures instinct typing | `memory/SKILL.md` | Low |
| 5 named orchestration patterns table | Study Only | Partially overlaps existing execution-mode concept; needs reconciliation with WabbleSpec's own wave/recipe model | `autopilot/SKILL.md` (reference only) | Low |
| Model name frontmatter (`model: opus`, `model: haiku`) | Avoid | I6 violation — no model names in framework files | N/A | Do Not Copy |
| `no-haiku.md` rule | Avoid | I6 violation in file name and content | N/A | Do Not Copy |
| `agent-model-selection.md` rule body | Avoid | I6 violation (Haiku/Opus/Sonnet named) | N/A | Do Not Copy |
| `rp-cli` tool calls | Avoid | External binary dependency, not available | N/A | Do Not Copy |
| PostgreSQL/BGE memory backend | Avoid | Heavy dependency; file-based drawers are WabbleSpec's model | N/A | Do Not Copy |
| `CLAUDE_OPC_DIR` env var | Avoid | Project-specific, not portable | N/A | Do Not Copy |
| Agent output file protocol | Avoid | Conflicts with receipt model | N/A | Do Not Copy |
| `.claude/cache/agents/` directory | Avoid | Conflicts with `.wabblespec/state/receipts/` | N/A | Do Not Copy |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 8 | Both are multi-agent orchestration frameworks with spec/receipt/checkpoint concepts |
| Architecture fit | 4 | TypeScript hooks + PostgreSQL vs. Python scripts + DuckDB + markdown; implementation layers incompatible |
| Implementation fit | 3 | `rp-cli`, `CLAUDE_OPC_DIR`, PostgreSQL, BGE embeddings — all non-portable. Behavioral patterns portable; code is not |
| Maintenance fit | 7 | Behavioral conventions (claim markers, state symbols, erotetic check) are stable additions with no maintenance burden |
| Risk level | 3 | Primary risk is I6 violation via model names; easy to filter. No structural coupling risk |
| Overall usefulness | 7 | Strong behavioral pattern value. Implementation non-adoptable; conventions highly adoptable |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Behavioral Additions — implement now):**
- Claim verification markers → `adversary/SKILL.md`
- Checkpoint state symbols → `executor/SKILL.md`
- Erotetic Check framing → `guard/SKILL.md`
- Reference: `rules/claim-verification.md`, `agents/kraken.md:Step 5`, `agents/phoenix.md:Erotetic Check`

**Phase 2 (Low-Risk Augmentation — implement after Phase 1 verified):**
- YAML handoff `goal:`/`now:` contract → stop-hook + session-start hook
- Proactive delegation threshold table → `autopilot/SKILL.md`
- 7-type memory taxonomy → `memory/SKILL.md`
- Reference: `hooks/src/pre-compact-continuity.ts`, `hooks/src/session-start-continuity.ts`, `rules/proactive-delegation.md`, `rules/dynamic-recall.md`

**Phase 3 (Study Only / Deferred):**
- 5-pattern orchestration table → reconcile with WabbleSpec's execution-mode concept before adopting

**Phase 4 (Do Not Cross):**
- All model name references (I6)
- `rp-cli`, `CLAUDE_OPC_DIR`, PostgreSQL, agent output file convention

---

## Section 7 — Final Verdict

**Classification:** supporting-reference (7/10)

**Best 3 to steal:**
1. Checkpoint state symbols `○ → ✓ ✗` + JSON validation state block (`agents/kraken.md:Step 5`) — makes wave state machine observable and resumable
2. Claim verification 3-marker protocol (`rules/claim-verification.md`) — immediately strengthens adversary and verifier audit quality
3. Erotetic Check E(X,Q) framing (`agents/phoenix.md`, `agents/aegis.md`) — pre-execution question inventory forces completeness before guard/executor act

**Worst 3 to avoid:**
1. Any model name in agent frontmatter (`model: opus`, `model: haiku`) — hard I6 violation
2. `rp-cli` tool calls — external binary not available
3. Agent output file convention (`.claude/cache/agents/`) — conflicts with receipt model

**Next action:** Proceed to ref-plan. Phase 1 items are all Tier 1–2 additive behavioral changes with no architectural risk.

---

## Section 8 — Project Synthesis

**Synthesis 1 — E(X,Q) + Guard Pre-Wave Validation**
What: Before each wave, Guard frames `X = wave target files` and `Q = invariant questions` explicitly in its output, making the question inventory part of the guard receipt rather than implicit
Reference contribution: Erotetic Check forces enumeration of questions before acting (`agents/phoenix.md`, `agents/aegis.md`)
Project contribution: Guard already has Layer 1–5 authority/risk checks; the question inventory gives those layers a structured input
Target: `.wabblespec/engine/modules/l2/guard/SKILL.md` + `.claude/agents/wabblespec-guard.md`
Gap closed: Guard PASS receipts currently don't expose the question inventory, making them hard to audit; E(X,Q) output makes gaps visible

**Synthesis 2 — Checkpoint State Machine + Wave Plan Receipts**
What: Wave plan entries in WabbleSpec carry checkpoint/rollback targets; mapping these to the ○ → ✓ ✗ state symbols + JSON validation state block in receipts makes the wave state machine machine-queryable
Reference contribution: 4-state checkpoint machine with embedded JSON validation state (`agents/kraken.md:Step 5`)
Project contribution: Wave plan already has checkpoint and rollback_target fields; receipt-writer.py writes structured JSON
Target: `.wabblespec/engine/modules/l3/executor/SKILL.md`
Gap closed: Wave progress currently reported narratively in receipts; state symbols + JSON validation block enable programmatic resume detection

**Synthesis 3 — Claim Markers + Verifier PASS/FAIL**
What: Verifier receipts annotate each checked criterion with its confidence marker (✓ VERIFIED / ? INFERRED / ✗ UNCERTAIN) before issuing PASS/FAIL, surfacing which claims were verified by reading vs. inferred from grep
Reference contribution: 3-marker claim verification protocol (`rules/claim-verification.md`)
Project contribution: Verifier already produces structured PASS/FAIL receipts with per-criterion status
Target: `.wabblespec/engine/modules/l2/verifier/SKILL.md`
Gap closed: Verifier currently issues PASS/FAIL without distinguishing whether the evidence was read-verified or grep-inferred; markers prevent false PASS from unread evidence

---

## Section 9 — Expansion Opportunities

**Expansion 1 — Epistemic Reminder Hook (post-grep)**
Capability: A PostToolUse hook firing after every Grep call, injecting a contextual warning reminding the agent to read the actual file before making existence or behavior claims
Reference location: `hooks/dist/epistemic-reminder.js` + `rules/claim-verification.md` (Enforcement section)
Why the project lacks it: WabbleSpec's PreToolUse hook (Guard) runs before tools; no PostToolUse hook fires after Grep to reinforce verification discipline
What it would unlock: Reduction in false-PASS verifier receipts where the agent trusted grep output without reading; directly supports Synthesis 3
Dependencies: Claude Code PostToolUse hook with Grep matcher; existing stop-hook.py daemon infrastructure
Effort signal: days
Tier 7 candidate: Yes

**Expansion 2 — Transcript-Based Auto-Handoff Generation**
Capability: On PreCompact, parse the live conversation transcript and generate a structured YAML handoff (goal/now/files changed) automatically, without requiring Claude to manually write one
Reference location: `hooks/src/pre-compact-continuity.ts` + `hooks/src/transcript-parser.ts`
Why the project lacks it: WabbleSpec's stop-hook.py writes session state but doesn't parse the conversation transcript; compaction events have no auto-handoff path
What it would unlock: Cross-session continuity for long tasks that span multiple compaction events, without requiring manual `/archive` or handoff steps
Dependencies: Claude Code PreCompact hook event; transcript_path injection (already supported by harness); Python transcript parser equivalent
Effort signal: weeks
Tier 7 candidate: Yes

**Expansion 3 — Pattern Inference Module**
Capability: A Python script that classifies an agent task description into one of the named orchestration patterns (swarm/hierarchical/pipeline/generator-critic/jury/blackboard) with confidence score, used to automatically configure autopilot execution mode
Reference location: `hooks/src/skill-activation-prompt.ts:runPatternInference()` + `scripts/agentica_patterns/pattern_inference.py`
Why the project lacks it: Autopilot selects execution mode from complexity score alone; there is no pattern classification that maps task shape to orchestration topology
What it would unlock: Autopilot could auto-select the optimal pattern (e.g., jury for high-stakes decisions, swarm for parallel research) rather than defaulting to sequential
Dependencies: pattern_inference.py Python module; existing autopilot SKILL.md and recipe.json
Effort signal: weeks
Tier 7 candidate: Yes
