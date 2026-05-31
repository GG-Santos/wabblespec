# WabbleSpec Architecture Roadmap — v7.0+

**Generated:** 2026-05-28
**Basis:** Full codebase audit (103 modules, 33 scripts, all SKILL.md files) + Claude Code architecture documentation research
**Status:** Draft — requires Specify + Decompose before execution

---

## 1. Honest Current State

WabbleSpec v6.1 is a well-structured prompt injection framework. Every skill is a detailed system prompt delivered to the LLM, which then performs mechanical file I/O directly — reading large MD/JSON files into context, reasoning about structure, writing receipts, bumping version strings, appending changelogs. The LLM is doing work that deterministic code should own.

### What works well
- 33 Python scripts cover the most expensive operations (archive, changelog, receipt writing, version bump, drawer writes, staleness, graph traversal)
- Memory module uses a real database (ChromaDB + SQLite) — this is the right model
- Receipt chain and invariant enforcement provide real behavioral guarantees
- Hook architecture (pre-tool-use, session start) gives the framework actual leverage over LLM behavior

### What is broken or missing

| Problem | Impact | Root Cause |
|---|---|---|
| ~40% of framework writes still manual (task cards, wave plans, most receipts) | Hundreds of wasted tokens per session | Scripts exist but SKILL.md files don't call them |
| `scope.md` and `recipe.json` are global singletons | Two terminals pollute each other | No session namespace; paths resolve to repo root |
| Sequential single-agent execution | Wave N must finish before Wave N+1 starts | No task queue, no parallel workers |
| Receipts are 200+ scattered JSON files | No aggregation, no querying, O(n) file walks | No structured store |
| Skills load full MD documents into context | Repeated token cost on every invocation | No selective injection, no subagent isolation |
| No background automation | Staleness sweeps, memory mining run manually | No daemon architecture |
| `.wabblespec/` root has stray files | Confusing, inconsistent | No file organization standard enforced |
| No formal engineering standards | Naming, I/O contracts, script API conventions vary | Never codified |

---

## 2. Architecture Vision: From Command to Collaboration

### Current model (command)

```
User
 └─ /skill command
     └─ Load CLAUDE.md + 3-5 reference MD files + prior receipts into context
         └─ LLM reads full documents, reasons about structure
             └─ LLM writes receipt JSON manually
                 └─ LLM writes CHANGELOG manually
                     └─ LLM bumps VERSION manually
                         └─ Return prose summary to user
```

Every session: ~15,000–50,000 tokens consumed on file loading before any real work.

### Target model (collaboration)

```
User
 └─ Orchestrator (minimal context: task prompt + schemas only)
     ├─ Subagent A: Reasoning task (receives only what it needs, returns typed receipt)
     ├─ Subagent B: Independent parallel task (typed receipt)
     └─ Scripts: All structured file I/O (scripts never enter LLM context)
         └─ DuckDB: receipts indexed, queryable, aggregatable
             └─ Daemon: background staleness/memory/graph work happens outside LLM turns
```

The LLM handles: reasoning, content generation, decision-making, error interpretation.
Scripts handle: all structured file reads and writes.
Daemons handle: background maintenance that doesn't require LLM reasoning.

---

## 3. Roadmap Overview

```
  NOW         Phase 1    Phase 2    Phase 3     Phase 4     Phase 5-6   Phase 7-8    Phase 9
  v6.1  ──────────────────────────────────────────────────────────────────────────────  v8.0

  Current     Cleanup    Script     New         Session     Skills as   Background   Standards
  State       + Org      Delegation Automation  Isolation   Subagents   Daemons      + DB
              Fix        Completion Scripts     + Worktrees Typed I/O   Parallel
                                                            Arch Shift  Waves
              1 session  1 session  2 sessions  2 sessions  4 sessions  3 sessions   1 session

  CRITICAL    CRITICAL   HIGH       HIGH        HIGH        STRATEGIC   STRATEGIC    ONGOING
```

---

## 4. Phase 1 — Root Organization + Path Deduplication

**What:** Clean up `.wabblespec/` root to the declared structure. Eliminate duplicated state paths.
**Effort:** 1 session, Low complexity
**Unblocks:** Everything — path confusion causes inconsistent reads

### 4.1 `.wabblespec/` root — declared vs actual

The root MUST contain only:

| File | Purpose | Status |
|---|---|---|
| `VERSION` | Semver string | OK |
| `wabblespec.yaml` | Module registry | OK |
| `INDEX.md` | Framework dashboard | OK |
| `CHANGELOG.md` | Release history | OK |
| `state/` | All session and runtime state | OK |
| `engine/` | All scripts, hooks, schemas, references | OK |

Currently also present (must move):

| File | Current Location | Move To |
|---|---|---|
| `scope.md` | `.wabblespec/scope.md` | `.wabblespec/state/scope.md` (already also there — deduplicate) |
| `recipe.json` | `.wabblespec/recipe.json` | `.wabblespec/state/recipe.json` (already also there — deduplicate) |
| `options-*.md` | `.wabblespec/options-*.md` | `.wabblespec/state/working/` |
| `brainstorm/` | `.wabblespec/brainstorm/` | `.wabblespec/state/brainstorm/` |

### 4.2 Canonical path rule

All skills, scripts, and hooks read/write:
- `.wabblespec/state/scope.md` (not root)
- `.wabblespec/state/recipe.json` (not root)

One path. No duplication. Session isolation (Phase 4) will further namespace these under a session ID.

---

## 5. Phase 2 — Script Delegation Completion

**What:** Wire every skill that currently performs manual framework writes to call the existing scripts that already handle those writes.
**Effort:** 1 session, Medium complexity
**Immediate ROI:** Eliminates hundreds of tokens per operation across every session

### 5.1 Automation gap — what exists vs what is called

| Skill | Manual Write | Available Script | Wired? |
|---|---|---|---|
| Recipe | recipe.json, receipt | `recipe-writer.py` | NO |
| Verifier | verification receipt JSON | `receipt-writer.py --type verifier` | NO |
| Guard | guard receipt JSON | `receipt-writer.py --type guard` | NO (partial) |
| Executor | wave receipt, execution receipt | `receipt-writer.py --type executor` | NO |
| Decompose | receipt | `receipt-writer.py --type decompose` | NO |
| Specify | receipt | `receipt-writer.py --type specify` | NO |
| Shift | shift receipt | `receipt-writer.py` | NO |
| Memory | drawer metadata writes | `drawer-writer.py` | NO |
| Provenance | ledger append | `provenance-append.py` | NO (mentioned but not enforced) |
| Changelog | CHANGELOG append | `changelog-append.py` | NO (skill instructs manual write) |
| Archive | all 4 writes | `archive.py` | PARTIALLY (script called but steps still prose) |
| Benchmark | tracker.json | `tracker-update.py` | NO |
| Factory | module scaffold | `module-scaffold.py` | PARTIAL |

### 5.2 Delegation contract

Add `## Script Delegation Contract` section to `skill-writing-contract.md` with a table:

| Operation | Script | Minimum Args |
|---|---|---|
| Write any receipt | `receipt-writer.py --type <type> --task-id ... --status ...` | type, task-id, status |
| Append changelog | `changelog-append.py --version ... --timestamp ...` | version, timestamp |
| Bump VERSION | `version-bump.py --bump <BREAKING\|ADDITIVE\|COSMETIC>` | bump class |
| Full Archive | `archive.py --session-id ... --task-id ... --summary ...` | session-id, task-id |
| Write drawer | `drawer-writer.py --drawer-id ... --topic ... --content ...` | drawer-id, topic |
| Append provenance | `provenance-append.py` | (see script header) |

Rule: Any SKILL.md step that produces a structured file output in `.wabblespec/` SHALL invoke the canonical script rather than instructing the LLM to compose and write the file.

---

## 6. Phase 3 — New Automation Scripts

**What:** Scripts don't yet exist for Specify (task cards), Decompose (wave plans), and ScopeFrame (scope files). Build them.
**Effort:** 2 sessions, Medium complexity

### 6.1 Scripts to build

**`task-card-writer.py`**
- Input: goal, complexity, acceptance criteria (as structured args), change_class
- Output: formatted `task-card.md` at the canonical path
- LLM's job: reason about what the criteria should be; hand off the writing
- Eliminates: ~500 tokens of "now write task-card.md with these fields..." per session

**`wave-plan-writer.py`**
- Input: task-id, wave count, per-wave: modules, description, dependencies
- Output: formatted `current-wave-plan.md`
- LLM's job: decompose the task into waves; hand off the formatting
- Eliminates: wave plan formatting tokens per session

**`scope-writer.py`**
- Input: target, complexity, in-scope items, out-of-scope items, assumptions
- Output: formatted `scope.md` (session-namespaced — see Phase 4)
- LLM's job: determine the scope boundaries; hand off the file write

**`decisions-writer.py`**
- Input: decisions, rejected alternatives, constraints, resolved questions
- Output: formatted `decisions.md`
- LLM's job: identify decisions; hand off the file

### 6.2 Guard Layer 1–3 automation

Current: `guard-check.py` handles only Layers 4–5 (deterministic: file ownership, command risk).
Layers 1–3 (invariant checks, spec completeness, context integrity) require LLM reasoning.

**Pattern for partial automation:**
- Extract all pattern-expressible checks into Guard as named checks with script stubs
- Example: "receipt chain complete" is checkable by `receipt-chain-validate.py` — no LLM needed
- LLM handles only genuinely semantic checks (spec completeness, implied completion detection)
- Reduces Guard's LLM reasoning load by ~30%

---

## 7. Phase 4 — Session Isolation + Multi-Terminal

**What:** Fix the fundamental flaw that `scope.md`, `recipe.json`, and session state are global singletons. Two terminals running simultaneously corrupt each other.
**Effort:** 2 sessions, Medium complexity

### 7.1 The problem

Every WabbleSpec file that is "current session" state is stored at a single fixed path in the repo root. Two terminals both writing `scope.md` = last writer wins.

### 7.2 The solution: git worktrees + session namespacing

Claude Code's native answer to parallel session isolation is git worktrees. Each session created with `claude --worktree <name>` operates in `.claude/worktrees/<name>/` — a separate filesystem checkout of the same repo. Any relative path from `cwd` is naturally isolated.

**Session state paths become session-scoped:**

```
Current (broken):
  .wabblespec/state/scope.md         ← shared across all sessions
  .wabblespec/state/recipe.json      ← shared
  .wabblespec/state/session/state.json ← shared

Target (isolated):
  .wabblespec/state/sessions/<session-id>/scope.md
  .wabblespec/state/sessions/<session-id>/recipe.json
  .wabblespec/state/sessions/<session-id>/state.json
  .wabblespec/state/sessions/<session-id>/receipts/
  .wabblespec/state/sessions/<session-id>/plans/
```

Or via worktree: each session's `.wabblespec/state/` is the session-scoped root because it's in a different checkout directory. No path changes needed — isolation comes from worktree.

### 7.3 Session registry

New file: `.wabblespec/state/session-registry.json`
- Lists all active sessions with: session_id, worktree path, started_at, task_id, status
- Updated by `session-state.py` (add: register, unregister, list subcommands)
- Enables: "show me all active sessions", conflict detection, orphan cleanup

### 7.4 Recipe supports explicit session ID

`recipe-writer.py --session-id <id>` writes recipe to the session-namespaced path.
All scripts accept `--session-id` to resolve to the correct session directory.

---

## 8. Phase 5–6 — Skills as Subagents (The Architecture Shift)

**What:** Convert WabbleSpec skills from "system prompt injections into main context" to "subagent definitions with typed I/O". This is the single largest architectural improvement possible.
**Effort:** 4 sessions, High complexity
**Impact:** Eliminates context bloat, enables parallelism, produces validated typed receipts

### 8.1 Current vs target skill model

**Current:**
```
/skill → SKILL.md loads into main conversation context (~500-3000 tokens)
       → LLM reads reference docs (~2000-10000 tokens)
       → LLM reads prior receipts (~1000-5000 tokens)
       → LLM reasons + writes files
       → Main context grows by all of the above on every skill invocation
```

**Target:**
```
Orchestrator receives: task prompt (200 tokens) + output schema (100 tokens)
Subagent spins up: own context window, receives only its task
Subagent loads: only its own skill doc + references it actually needs
Subagent calls scripts: all file I/O handled externally
Subagent returns: validated typed receipt matching the schema
Main context receives: typed receipt (100-500 tokens) — not the full skill execution
```

### 8.2 Subagent definition format

Each skill gets a corresponding `.claude/agents/<skill-name>.md`:

```markdown
---
name: specify
description: Writes the task card from a locked scope. Returns a typed specify receipt.
skills: [specify]
outputFormat:
  type: json_schema
  schema:
    $ref: ".wabblespec/engine/shared/schemas/specify-receipt.extension.schema.json"
background: false
---
```

The SKILL.md continues to exist as the behavioral contract. The agent definition adds:
- `outputFormat`: forces a typed return (not prose)
- `skills:` preloads only what this agent needs
- `background:` for agents that don't need interactive permission

### 8.3 Orchestrator pattern

The main WabbleSpec session becomes a thin orchestrator:
1. Receives user intent
2. Invokes appropriate subagent with a minimal prompt
3. Receives typed receipt
4. Passes receipt to next subagent
5. Never loads full skill documentation into its own context

This is how Recipe → ScopeFrame → Specify → Decompose → Executor works at the end state.

### 8.4 Migration order

Migrate by layer, least context-expensive first:

| Wave | Skills | Rationale |
|---|---|---|
| 1 | Archive, Changelog, Verifier, Guard | Already mostly script-delegated; cleanest typed I/O |
| 2 | Recipe, ScopeFrame, Specify | Core chain; high-frequency; high ROI |
| 3 | Decompose, Executor | Complex but well-defined output schemas |
| 4 | Memory, Entity-Graph, Provenance | L5 — complex internal state |
| 5 | L8 (Instinct through Forge) | Most complex; migrate last |

---

## 9. Phase 7 — Background Daemons

**What:** Move framework maintenance work (staleness sweeps, memory mining, graph updates, quality checks) out of LLM turns into persistent background processes.
**Effort:** 2 sessions, Medium complexity

### 9.1 What should be a daemon

| Task | Current | Target |
|---|---|---|
| Memory staleness sweep | Runs only when explicitly invoked | Daemon: watch for new receipts, trigger sweep |
| Memory mining (pattern extraction) | Manual `/memory-mine` invocation | Daemon: runs nightly or after N new receipts |
| Entity graph updates | Manual after skill changes | Daemon: file-watch on SKILL.md files |
| Quality floor checks | Manual before L8 gates | Daemon: runs after each Archive |
| Receipt chain validation | Manual pre-Archive | Daemon: validates on receipt write |
| Staleness map regeneration | Manual | Daemon: regenerates after each Archive |

### 9.2 Daemon architecture using Claude Code supervisor

Claude Code has a production daemon system: `claude --bg` creates a persistent background session managed by a supervisor process. The supervisor handles crash recovery, process lifecycle, and wake-from-sleep.

```
WabbleSpec Daemon Definitions:
  .claude/agents/ws-staleness-daemon.md
  .claude/agents/ws-memory-mine-daemon.md
  .claude/agents/ws-graph-updater-daemon.md
  .claude/agents/ws-quality-floor-daemon.md
```

Each daemon definition:
- Has a trigger condition (file watch, schedule, event)
- Uses scripts for all file I/O (no LLM writing files)
- Writes a daemon receipt on completion
- Does NOT block the main session

### 9.3 File-watch triggers

```
Archive completes → trigger staleness-checker, quality-floor, receipt-chain-validate
SKILL.md changes → trigger graph-updater, activator-audit
N new receipts → trigger memory-mine
```

Implemented via the existing `SessionStart` hook pattern — extend the hook architecture to watch for file changes and spawn daemon sessions.

---

## 10. Phase 8 — DuckDB Receipt Store

**What:** Replace scattered JSON receipt files with a queryable DuckDB database.
**Effort:** 2 sessions, Medium complexity

### 10.1 Why DuckDB specifically

- Single file (`receipts.duckdb`), no server, works in Python subprocess
- Reads existing JSON files natively: `SELECT * FROM read_json_auto('state/receipts/*.json')`
- No migration required for legacy receipts — they remain readable
- Supports aggregation queries that Archive currently can't do efficiently:
  ```sql
  SELECT session_id, COUNT(*) as receipt_count, MAX(status) as final_status
  FROM receipts WHERE project_key = 'current-project'
  GROUP BY session_id
  ```
- Guard staleness queries become:
  ```sql
  SELECT staleness_state, confidence FROM drawers
  WHERE drawer_id = ? ORDER BY written_at DESC LIMIT 1
  ```
  vs current: walk `state/memory/wings/**/drawers/*.json`

### 10.2 Schema design

```sql
CREATE TABLE receipts (
  seq          BIGINT PRIMARY KEY,
  session_id   TEXT NOT NULL,
  task_id      TEXT NOT NULL,
  receipt_type TEXT NOT NULL,
  status       TEXT NOT NULL,   -- PASS/FAIL/PARTIAL/BLOCKED
  written_at   TIMESTAMP NOT NULL,
  payload      JSON,             -- full receipt content
  module_id    TEXT,
  wave         INTEGER,
  delta_class  TEXT              -- BREAKING/ADDITIVE/COSMETIC/null
);

CREATE TABLE drawers (
  drawer_id       TEXT PRIMARY KEY,
  wing            TEXT,
  room            TEXT,
  topic           TEXT,
  staleness_state TEXT,
  confidence      FLOAT,
  written_at      TIMESTAMP,
  expires_at      TIMESTAMP,
  content_hash    TEXT
);
```

### 10.3 Migration path

1. `receipt-writer.py` gains `--db` flag (writes to DuckDB AND JSON for transition period)
2. `drawer-writer.py` gains `--db` flag
3. Guard and Archive switch to DB queries
4. After 2+ sessions of DB operation, JSON-only writes deprecated
5. Legacy JSON remains as audit trail (append-only, never deleted)

---

## 11. Phase 9 (Parallel) — Agent Teams + Parallel Wave Execution

**What:** Implement parallel wave execution using Claude Code's Agent Teams architecture.
**Effort:** 3 sessions, High complexity

### 11.1 Current vs target wave execution

**Current:**
```
Wave 1: [Task A, Task B, Task C] — executed sequentially in one session
Wave 2: starts only after Wave 1 complete
```

**Target:**
```
Wave 1: Task A → Worker Agent 1 (background)
        Task B → Worker Agent 2 (background, parallel)
        Task C → Worker Agent 3 (background, parallel)
        All write receipts independently
        Orchestrator aggregates when all complete
Wave 2: starts when Wave 1 tasks all have PASS receipts
```

### 11.2 Agent Teams implementation

Claude Code Agent Teams use a shared task list at `~/.claude/tasks/<team-name>/` with file locking for concurrent task claiming.

WabbleSpec maps naturally:
- Team name = task-id (e.g., `task-20260528-refactor`)
- Task list entries = wave tasks from `current-wave-plan.md`
- Worker agents = subagents with `background: true`
- Shared state = DuckDB receipts database (concurrent-safe)

```
task queue:
  .claude/tasks/ws-<task-id>/
    wave-1-task-A.json  { status: claimed, worker: agent-1 }
    wave-1-task-B.json  { status: pending }
    wave-1-task-C.json  { status: pending }
```

### 11.3 Dependency enforcement

Wave dependency tracking (Wave N starts only after Wave N-1 PASS) implemented by:
- Decompose writing dependency metadata to the task queue
- Worker agents check dependencies before claiming tasks
- Orchestrator watches for all Wave N tasks complete before releasing Wave N+1

---

## 12. Phase 10 — Standards Codification

**What:** Write and enforce formal WabbleSpec Engineering Standards. These codify what is currently inconsistent or undocumented.
**Effort:** 1 session, Low complexity

### 12.1 Naming conventions

| Artifact | Convention | Example |
|---|---|---|
| Receipt files | `<module>-receipt-<ISO-date>T<time>Z.json` | `verifier-receipt-20260528T110000Z.json` |
| Delivery receipts | `delivery-receipt-<session-id>.json` | |
| Scripts | `<verb>-<noun>.py` in lowercase-hyphen | `receipt-writer.py` |
| SKILL.md | Title case skill name, kebab-case directory | `archive/SKILL.md` |
| State dirs | lowercase-hyphen | `state/sessions/`, `state/working/` |
| Session IDs | `<project-slug>-<ISO-date>` | `script-delegation-20260528` |
| Subagent defs | `ws-<skill>.md` | `ws-archive.md` |
| Daemon defs | `ws-<function>-daemon.md` | `ws-staleness-daemon.md` |

### 12.2 File organization standard

```
.wabblespec/
├── VERSION                    # semver, no trailing newline
├── CHANGELOG.md               # append-only, most-recent-first
├── INDEX.md                   # auto-generated dashboard
├── wabblespec.yaml            # module registry
├── engine/
│   ├── shared/
│   │   ├── scripts/           # 33+ Python scripts
│   │   ├── references/        # 50+ reference docs
│   │   ├── schemas/           # JSON schemas
│   │   └── agents/            # quality auditor defs
│   └── hooks/                 # JS hook files
└── state/
    ├── session-registry.json  # active sessions (Phase 4)
    ├── sessions/              # per-session state (Phase 4)
    │   └── <session-id>/
    │       ├── scope.md
    │       ├── recipe.json
    │       ├── state.json
    │       ├── plans/
    │       └── receipts/
    ├── receipts/              # legacy + shared receipts
    ├── receipts.duckdb        # queryable store (Phase 8)
    ├── archive/               # receipt-index.json
    ├── memory/                # ChromaDB + knowledge graph
    ├── experiments/           # L8 evolution artifacts
    ├── logs/                  # sync.log, daemon.log
    └── working/               # session scratch (options, brainstorm)
```

### 12.3 Script API standard

Every WabbleSpec script SHALL:
- Accept `--help` and print usage
- Accept `--dry-run` and emit what would be written without touching files
- Exit 0 on success, 1 on bad args/logic failure, 2 on file not found
- Print to stdout only; errors to stderr
- Never load files that aren't given as explicit arguments
- Accept `--session-id` to resolve session-namespaced paths (Phase 4)

### 12.4 Receipt schema versioning

Current: no `schema_version` field on receipts.
Standard: every receipt includes `"schema_version": 2` (Phase 8 onwards).
Legacy receipts: implicitly `schema_version: 1`.

### 12.5 I/O contracts

Every skill's input contract = what files/receipts it reads before acting.
Every skill's output contract = what receipt it writes and what script it uses.
Both declared in SKILL.md under standardized `## Input Contract` and `## Output Contract` headers.

---

## 13. Execution Sequencing

### Immediate (this session or next)
1. Archive `toprank-integration-phase1` (user confirmed done)
2. Phase 1: Fix `.wabblespec/` root organization + deduplicate scope/recipe paths
3. Phase 2: Wire existing scripts to all skills that currently write manually

### Short term (next 3-5 sessions)
4. Phase 3: Build task-card-writer.py, wave-plan-writer.py, scope-writer.py
5. Phase 4: Session isolation (worktree support, session-namespaced paths)
6. Phase 10: Standards document (codify what phases 1-4 establish)

### Medium term (5-10 sessions)
7. Phase 5-6: Skills as subagents — start with Archive, Verifier, Guard (Wave 1)
8. Phase 7: Background daemons — staleness sweeper first
9. Phase 8: DuckDB receipt store

### Long term (10+ sessions)
10. Phase 5-6: Complete subagent migration (all layers)
11. Phase 9: Agent Teams + parallel wave execution

---

## 14. What Makes WabbleSpec "Smart" Rather Than "Commanding"

The distinction is architectural, not aesthetic.

**Command model**: LLM reads instructions, writes files, returns summary. Framework is a prompt. Every operation costs tokens even for mechanical work.

**Collaboration model**: LLM handles only decisions and content that require reasoning. Scripts handle all structured I/O. Subagents scope their context to only what they need. Daemons run maintenance without LLM involvement. The framework actively reduces what the LLM must do so that LLM work is spent exclusively on things that actually need a language model.

Concrete markers of the target state:
- A receipt write costs 0 LLM tokens (script call)
- A staleness check costs 0 LLM tokens (DuckDB query)
- Running two sessions in parallel is a first-class supported operation (worktrees)
- Archive completes in 2 seconds (one script call) vs the current 60+ seconds of reading and writing
- The LLM's context window contains the task, the decision, and the result — not the file system

---

## 15. What Stays LLM-Owned

Not everything should be scripted. The LLM's unique contribution is:

- **Reasoning about what the criteria should be** (Specify — criteria content)
- **Decomposing tasks into waves** (Decompose — wave structure and dependency reasoning)
- **Identifying what changed and classifying it** (delta_class reasoning in Executor/Verifier)
- **Evaluating test results and determining PASS/FAIL** (Verifier semantic checks)
- **Writing code, documentation, spec content** (the actual deliverables)
- **Catching implied completion** (Guard semantic layer)
- **Surfacing anomalies and contradictions** (Adversary, Grader, Reviewer)

Everything else is automation.
