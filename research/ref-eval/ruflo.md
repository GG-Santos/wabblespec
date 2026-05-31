# Ref-Eval: ruflo (Claude Flow V3 / ruvnet Orchestrator)

**Evaluated:** 2026-05-30  
**Slug:** ruflo  
**Reference path:** `C:\Users\Kirsten\Downloads\Orchestrator\ruflo`  
**Trust level:** MEDIUM  
**Overall verdict:** inspiration-only (4/10)

---

## File Inventory

| File | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| `.agents/README.md` | Entry point, structure docs | small | `.agents/` layout, invocation syntax (`$skill-name`), link to ruvnet/claude-flow | Read |
| `.agents/config.toml` | Codex CLI configuration | medium | Model selection (hardcoded names), approval policy, swarm/neural/hooks config | Read |
| `.agents/skills/agent-swarm/SKILL.md` | Swarm orchestration persona | small | Topology types, agent spawn patterns, MCP tool calls | Read |
| `.agents/skills/agent-memory-coordinator/SKILL.md` | Memory management persona | medium | Memory hierarchy, namespaces, Best Practices section | Read |
| `.agents/skills/agent-sparc-coordinator/SKILL.md` | SPARC methodology orchestrator | medium | Phase transitions, quality gates 1-5, agent coordination | Read |
| `.agents/skills/agent-orchestrator-task/SKILL.md` | Task decomposition agent | medium | Task patterns (Feature, BugFix, Refactor), parallel/sequential planning | Read |
| `.agents/skills/agent-raft-manager/SKILL.md` | Raft consensus coordinator | small | Leader election, log replication, follower management | Read |
| `.agents/skills/agent-byzantine-coordinator/SKILL.md` | Byzantine fault tolerance | small | PBFT three-phase protocol, malicious actor detection | Read |
| `.agents/skills/agent-queen-coordinator/SKILL.md` | Hierarchical swarm orchestrator | medium | Sovereign status writes, resource allocation, succession planning | Read |
| `.agents/skills/agent-v3-queen-coordinator/SKILL.md` | V3-specific orchestrator | medium | 15-agent topology diagram, ADR-001 to ADR-010, performance targets | Read |
| `.agents/skills/agent-adaptive-coordinator/SKILL.md` | Dynamic topology switcher | large | WorkloadAnalyzer class, TopologyOptimizer, rollback triggers with named thresholds | Read |
| `.agents/skills/agent-sona-learning-optimizer/SKILL.md` | Self-optimizing neural agent | small | LoRA, EWC++, "+55% quality", benchmark numbers | Read |
| `.agents/skills/agent-worker-specialist/SKILL.md` | Task execution worker | medium | Status protocol (task-received → progress → complete), files_modified schema | Read |
| `.agents/skills/agent-crdt-synchronizer/SKILL.md` | CRDT conflict resolution | very large | G-Counter, OR-Set, LWW-Register, RGA implementations in full JS | Read |
| `.agents/skills/agent-collective-intelligence-coordinator/SKILL.md` | Hive mind coordinator | medium | Consensus building, cognitive load balancing, "write every 30 seconds" mandate | Read |
| `.agents/skills/agentdb-vector-search/SKILL.md` | Vector database integration | large | HNSW, quantization types, benchmarks ("150x faster"), MMR, CLI commands | Read |
| `.agents/skills/flow-nexus-neural/SKILL.md` | Distributed neural training | very large | Cluster init, node deploy, federated learning, marketplace templates | Read |
| `.agents/skills/agent-coordinator-swarm-init/SKILL.md` | Swarm initializer | small | Swarm spawn pattern | Skipped — redundant with agent-swarm |
| 70+ remaining agent skills | Domain agents (payments, auth, CI/CD, etc.) | small-medium each | Product-domain personas with MCP tool wrappers | Skipped — domain-specific, no framework value |

**Connection map:**

```
config.toml --[skill registration]--> skills/swarm-orchestration, memory-management, sparc-methodology, security-audit
agent-queen-coordinator --[directs]--> agent-worker-specialist: task assignments via memory namespace "coordination"
agent-queen-coordinator --[delegates]--> agent-collective-intelligence-coordinator: consensus decisions
agent-orchestrator-task --[spawns]--> agent-sparc-coordinator: phase execution
agent-sparc-coordinator --[invokes]--> specialized SPARC agents: phase outputs via memory
agent-adaptive-coordinator --[monitors]--> agent-swarm: performance metrics
agent-memory-coordinator --[stores]--> all agents: shared state via "coordination" namespace
agent-raft-manager --[interfaces with]--> agent-byzantine-coordinator: consensus fallback
agent-crdt-synchronizer --[integrates with]--> agent-raft-manager: hybrid consistency model
agentdb-vector-search --[used by]--> agent-memory-coordinator: semantic retrieval
```

What breaks if a file changes: The MCP memory namespace `"coordination"` is the shared state bus. Any skill that writes `swarm$shared$*` keys is consumed by queen/collective-intelligence. Renaming the namespace breaks all cross-agent reads.

---

## Section 1 — Reference Summary

**Type:** Production multi-agent framework (active npm packages: `@claude-flow/cli`, `agentic-flow`, `agentdb`). Targeting OpenAI Codex CLI.

**Problem it solves:** Coordinates multiple LLM agents across complex software development tasks — decomposition, parallel execution, consensus, memory sharing.

**Behavioral content:** Agent persona definitions with embedded decision logic. Key patterns: topology selection by task characteristics, PBFT/Raft consensus for distributed agreement, CRDT merge semantics for conflict-free state, rollback triggers with numeric thresholds.

**Structural content:** `.agents/skills/<name>/SKILL.md` — YAML frontmatter + freeform markdown. No WabbleSpec-style GWT criteria, no `## When NOT to use`, no receipt contracts. Skill invocation via `$skill-name` prefix, not slash commands.

**Interaction content:** All cross-agent coordination flows through a shared memory namespace (`mcp__claude-flow__memory_usage` with `namespace: "coordination"`). Skills write structured JSON under `swarm$<role>$<key>` paths. No file-based receipts — memory is the completion signal.

**Maturity assessment:** Active — real npm packages with semver, benchmarks published. But significant AI-generated boilerplate (symmetric skill structures, marketing numbers without methodology). No tests in skills directory. The CRDT implementations are real CS (GCounter, OR-Set, LWW-Register correctly implemented) but unused in single-agent contexts.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `agent-adaptive-coordinator/SKILL.md` lines 88-134 | Topology decision matrix — 5 task dimensions (complexity, parallelizability, interdependencies, resource_requirements, time_sensitivity) mapped to execution strategy | WabbleSpec Decompose only uses complexity (Low/Medium/High). Adding parallelizability and interdependencies as explicit dimensions would improve wave sequencing decisions — currently waves are always sequential, but some could safely run in parallel | Add a `## Task Profile` section to `decompose/SKILL.md` Step 3 with the 5-dimension assessment; map to "sequential", "parallel-eligible", or "mixed" wave execution label in the wave plan | Medium |
| `agent-adaptive-coordinator/SKILL.md` lines 330-358 | Rollback trigger thresholds — named dict with float values: `performance_degradation: 0.25`, `error_rate_increase: 0.15`, `agent_failure_rate: 0.30` | WabbleSpec Rollback triggers on "HARD error" — qualitative. Named numeric thresholds make trigger conditions explicit in the wave plan's Rollback Map | Add a `rollback_triggers:` block to the wave plan output contract in Decompose, and a corresponding threshold check step in Executor | Medium |
| `agent-sparc-coordinator/SKILL.md` lines 69-88 | Quality gate naming — each phase gate gets a descriptive name ("Specification Complete", "Algorithms Validated", "Design Approved") not just a number | WabbleSpec checkpoints are named by wave label but gates don't have explicit quality-gate names. Named gates appear in receipts and are easier to audit across a project | Add gate name as an optional field in the wave plan checkpoint block: `gate_name: "<human-readable condition>"` | Low |
| `agent-worker-specialist/SKILL.md` lines 20-56 | Progress payload schema — `steps_completed: []`, `current_step: string`, `progress_percentage: int`, `blockers: []`, `files_modified: []` | Executor wave receipts currently don't include a structured progress payload — they write PASS/FAIL with summary. This schema would make wave-level receipts queryable | Add `files_modified` and `steps_completed` fields to the wave execution receipt schema in `receipt-writer.py` (already owns the schema) | Low |
| `agent-memory-coordinator/SKILL.md` lines 138-145 | Memory hierarchy model — Global (Long-term) → Project (Medium-term) → Session (Short-term) → Task (Ephemeral) | WabbleSpec's drawer staleness model already has FRESH/STALE/EXPIRED/CONFIRMED states but lacks explicit temporal tier names. Adding tier labels improves the staleness reference doc | Add `temporal_tier` field to drawer schema docs; maps to existing staleness_state | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `config.toml` lines 17, 17 | Model names hardcoded (`gpt-5.3-codex`, `claude-sonnet`, `claude-opus`) | Direct I6 violation — no model names in framework files | Do not copy any config structure that references model names | Critical |
| All `agent-*` SKILL.md files | MCP tool prefixes (`mcp__claude-flow__*`, `mcp__flow-nexus__*`) embedded in skill bodies | I6 — vendor-specific provider names in framework files | Use `~~capability-name` form per CLAUDE.md convention | Critical |
| `agent-collective-intelligence-coordinator/SKILL.md` lines 96-104 | "EVERY 30 SECONDS you MUST write to memory" completion signal | I10 — memory writes as implied completion; no receipt chain | Pattern incompatible with WabbleSpec's receipt-gated model | High |
| `agent-sona-learning-optimizer/SKILL.md` | Claims of "+55% quality improvement", "2211 ops/sec" for a SKILL.md persona | AI-generated marketing numbers with no reproducible methodology; sourced from "@ruvector/sona@0.1.1" which may not exist | Do not import any benchmark claims | Medium |
| `agent-crdt-synchronizer/SKILL.md` | Full CRDT implementations (G-Counter, OR-Set, etc.) embedded in SKILL.md | The SKILL.md would be 1000+ lines; WabbleSpec skills target 1-3 pages. Also, CRDTs solve multi-node state conflicts — WabbleSpec is single-agent runtime | Do not copy | Medium |
| `agent-queen-coordinator/SKILL.md` lines 10-11 | "sovereign", "hive", "royal directives", "rebellious" terminology | Creates a confusing mental model when adapted to single-agent SDLC framework | Avoid the anthropomorphic terminology | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Topology decision matrix (adaptive-coordinator lines 88-134) | Adapt | Directly improves Decompose wave strategy | `skills/decompose/SKILL.md` Step 3 | High |
| Rollback trigger thresholds (adaptive-coordinator lines 330-358) | Adapt | Quantifies currently qualitative rollback conditions | `skills/decompose/SKILL.md` output + `skills/rollback/SKILL.md` | Medium |
| Quality gate naming (sparc-coordinator lines 69-88) | Adapt | Format improvement for wave plan checkpoint blocks | `skills/decompose/SKILL.md` output contract | Low |
| Worker progress payload schema (worker-specialist lines 20-56) | Study Only | Schema is interesting but receipt-writer.py owns the schema — needs dedicated task to add fields | `receipt-writer.py` (future task) | Low |
| Memory hierarchy temporal tiers (memory-coordinator lines 138-145) | Adapt | Adds temporal tier label to drawer schema docs | `shared/references/staleness-states.md` | Low |
| Model names in config.toml | Avoid | I6 violation | N/A | Critical |
| MCP vendor prefixes in skill bodies | Avoid | I6 violation | N/A | Critical |
| Memory-as-completion-signal pattern | Avoid | I10 violation | N/A | Critical |
| SONA benchmark claims | Avoid | Unverifiable marketing numbers | N/A | High |
| CRDT implementations | Avoid | Wrong runtime model; over-scoped for single-agent | N/A | Medium |
| Queen/hive/sovereign terminology | Avoid | Confusing mental model | N/A | Low |
| "MANDATORY" / "EVERY 30 SECONDS" imperative patterns | Avoid | Wrong cadence model for single-agent WabbleSpec | N/A | Medium |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 5 | Shares goal (structured multi-step task execution with quality gates) but fundamentally different execution model (multi-agent vs single-agent, memory-bus vs receipt-chain) |
| Architecture fit | 2 | MCP server dependency, Codex CLI target, multi-agent topology — incompatible with WabbleSpec's single-agent hook-enforced runtime |
| Implementation fit | 3 | Skill format differs (no `## When NOT to use`, no receipt contracts, vendor MCP names). Direct copy would violate I6 and I10 |
| Maintenance fit | 4 | Active project — patterns may evolve, but WabbleSpec adaptations would be decoupled from upstream |
| Risk level | 7 | High I6+I10 invariant conflict if any pattern adopted uncritically; marketing claims could corrupt instinct observations |
| Overall usefulness | 4 | Two genuine behavioral patterns worth adapting; everything else is incompatible or harmful |

**Overall usefulness 4/10 — inspiration-only.**

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning):**
- Topology decision matrix → Decompose Step 3 task profile assessment
- Rollback trigger thresholds → Decompose output contract Rollback Map

**Phase 2 (Low-Risk Adaptation):**
- Quality gate naming → Decompose wave plan output contract
- Temporal tier labels → staleness-states.md reference doc

**Phase 3 (Deeper Integration — defer):**
- Worker progress payload schema → requires receipt-writer.py schema change, own task

**Phase 4 (Do Not Cross):**
- Any MCP vendor names
- Model names
- Multi-agent topology as infrastructure
- Memory-as-completion-signal
- SONA/HNSW performance claims

---

## Section 7 — Final Verdict

**Classification: inspiration-only (4/10)**

**Best 3 to steal:**
1. Topology decision matrix (`agent-adaptive-coordinator/SKILL.md` lines 88-134) — the 5-dimension task assessment → execution strategy mapping is the one genuinely useful behavioral heuristic in the reference.
2. Rollback trigger thresholds (`agent-adaptive-coordinator/SKILL.md` lines 330-358) — `performance_degradation: 0.25`, `error_rate_increase: 0.15`, `agent_failure_rate: 0.30` give WabbleSpec's Rollback Map quantitative teeth.
3. Quality gate naming convention (`agent-sparc-coordinator/SKILL.md` lines 69-88) — descriptive gate names per checkpoint make the wave plan self-documenting.

**Worst 3 to avoid:**
1. Model names in config.toml (I6 violation — hard stop).
2. MCP vendor prefixes (`mcp__claude-flow__*`) embedded in skill bodies (I6 violation — if adopted, would need to be purged from every skill that referenced them).
3. Memory-as-completion-signal ("write to memory every 30 seconds", "MANDATORY status writes") — directly contradicts I10's receipt-gated model; adopting this pattern would silently hollow out the receipt chain.

**Recommended next action:** Implement Phase 1 safe wins (topology decision matrix → Decompose, rollback thresholds → Decompose + Rollback), write Tier 7 expansion drawers for parallel topology planning and CRDT-based wave merge.

---

## Section 8 — Project Synthesis

Novel patterns possible only by combining ruflo's approaches with WabbleSpec's existing infrastructure:

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Topology-scored wave plan | WorkloadAnalyzer 5-dimension profile (adaptive-coordinator lines 88-134) | Decompose already has complexity scoring and wave sequencing; queue-orchestrator.py can run parallel waves | `skills/decompose/SKILL.md` Step 3 | Decompose currently assigns wave count by complexity alone — adding parallelizability assessment enables it to recommend `execution_mode: parallel` for independent waves, which queue-orchestrator.py already supports |
| Quantitative Rollback Map | Named float thresholds in `rollback_triggers` dict (adaptive-coordinator lines 330-358) | Rollback.SKILL.md has 4 rollback types but trigger conditions are qualitative ("HARD error", "deploy detect rollback trigger") | `skills/decompose/SKILL.md` output contract, `skills/rollback/SKILL.md` | Wave plans would carry machine-readable trigger conditions; rollback activation becomes auditable |

---

## Section 9 — Expansion Opportunities

| Capability | Reference location | Why project lacks it | What it would unlock | Dependencies | Effort | Tier 7 candidate |
|---|---|---|---|---|---|---|
| Parallel agent topology planner | `agent-adaptive-coordinator/SKILL.md` topology switching (lines 88-300); `agent-v3-queen-coordinator/SKILL.md` 15-agent mesh diagram | WabbleSpec is single-agent by design; queue-orchestrator.py provides parallel wave execution but no topology analysis step | Would let Decompose declare `execution_mode: parallel` for eligible waves with automatic capacity estimation — queue-orchestrator.py would consume this | queue-orchestrator.py already exists; needs topology-analysis step in Decompose | days | Yes |
| CRDT-based parallel wave merge | `agent-crdt-synchronizer/SKILL.md` full implementation | Parallel waves in WabbleSpec can conflict when writing to the same file (no merge semantics) | Safe parallel writes to shared files during wave execution; reduced serialization of independent waves | queue-orchestrator.py, new merge layer | weeks | Yes |
