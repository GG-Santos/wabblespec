# Reference Index — WabbleSpec v6.1

> Generated: 2026-05-21
> Purpose: Master lookup for all repos in `C:\Vaults\references`. Load during runtime to avoid re-reading raw repos.
> Design: Table-first. No prose. Every row answers: what module, what to read, what to extract.

---

## How to Use This System

**During building, do not read raw repos.** Load the relevant reference card instead:

| Build phase | Card to load |
|---|---|
| Building Hook | `token-protocol.md` § Hook + `extra-refs-v61.md` § claude-code-main |
| Building Recipe/Specify/Decompose | `core-refs-v61.md` § L1 modules |
| Building Executor/Verifier/Archive | `core-refs-v61.md` § L2 modules + `extra-refs-v61.md` § toprank + pentest |
| Building Memory | `core-refs-v61.md` § mempalace + codeflow + `extra-refs-v61.md` § context-mode |
| Building Reviewer agent | `extra-refs-v61.md` § agent-creator |
| Validating activation patterns | `core-refs-v61.md` § anthropic-skills + oh-my-claudecode |

---

## Tier Map

### Core Project References (20 repos)

| Repo | Primary v6.1 module | Secondary | Read priority |
|---|---|---|---|
| agent-os-main | Specify (standards extraction) | Economy/token density | MED |
| andrej-karpathy-skills-main | Skill packaging | Orchestration patterns | LOW |
| anthropic-skills-main | skill-rules.json activation | Memory / MCP patterns | HIGH |
| cartographer-main | Recipe (target detection) | WabbleFlow graph | MED |
| caveman-main | CLAUDE.md patterns | CLI platform | LOW |
| Claude-Code-Game-Studios-main | Path-scoped activation rules | Hook (git layer) | MED |
| claude-code-security-review-main | Verifier (security checks) | Receipt patterns | MED |
| claude-plugins-official-main | skill-rules.json schema | MCP adapter | MED |
| codeflow-main | Memory (graph layer) | WabbleFlow | LOW |
| financial-services-main | Data schemas + pipelines | Security gates | LOW |
| G0DM0D3-main | CLI platform patterns | Security | LOW |
| get-shit-done-main | Executor + Verifier + Archive | Recipe / Decompose | TOP |
| graphify-7 | Memory graph | WabbleFlow | LOW |
| mattpocock-skills-main | Skill packaging | TypeScript patterns | LOW |
| mempalace-develop | Memory architecture | Staleness design | TOP |
| oh-my-claudecode-main | Executor agent design | skill-rules.json | HIGH |
| oh-my-codex-main | Skill packaging | MCP bridge | LOW |
| OpenSpec-main | Specify + Recipe | Archive patterns | HIGH |
| superpowers-main | Decompose (7-stage model) | Hook (git worktree) | HIGH |
| ui-ux-pro-max-skill-main | Design gateway | Aesthetic module | LOW |

### Extra Project References (8 repos)

| Repo | Primary v6.1 module | Secondary | Read priority |
|---|---|---|---|
| agent-creator | Reviewer agent design | Executor agent design | TOP |
| claude-ads-main | Command routing | Receipt scoring | MED |
| claude-code-main | Hook implementation | Pre-tool-use pattern | TOP |
| context-mode-main | Memory (SQLite/FTS5) | Session continuity | HIGH |
| hyperframes-main | Archive (render/lint) | Receipt schema | MED |
| Open-LLM-VTuber-main | Provider abstraction | Offline/local support | LOW |
| pentest-ai-agents-main | Archive (findings DB) | Verifier (status transitions) | HIGH |
| toprank-main | Verifier (fixture evals) | Archive persistence | HIGH |

### Other Projects References (80+ repos)

See `other-refs-v61.md` for full lookup table.
Key v6.1 signal repos (already fully mapped in v6 ledger):
- `claude-code-hooks-mastery` → Hook patterns
- `destructive_command_guard-main` → Hook safety model
- `awesome-claude-agents-main` → Reviewer agent patterns
- `claude-code-workflows-main` → Verifier workflow patterns
- `claude-code-safety-net-main` → Guard/safety patterns
- `SuperClaude_Framework-master` → Invariant enforcement reference
- `everything-claude-code-main` → Broad CLAUDE.md patterns
- `awesome-claude-code-subagents-main` → Subagent design

---

## v6.1 MVP Module → Best Reference Mapping

| MVP Module | Top reference | Second reference | Key file in ref |
|---|---|---|---|
| Hook (pre-tool-use) | `claude-code-main` (Extra) | `claude-code-hooks-mastery` (Other) | `examples/hooks/bash_command_validator_example.py` |
| Recipe | `get-shit-done-main` (Core) | `OpenSpec-main` (Core) | `commands/` directory |
| Specify | `OpenSpec-main` (Core) | `agent-os-main` (Core) | `WORKSPACE_REIMPLEMENTATION_DIRECTION` |
| Decompose | `get-shit-done-main` (Core) | `superpowers-main` (Core) | phase breakdown commands |
| Executor | `get-shit-done-main` (Core) | `oh-my-claudecode-main` (Core) | `execute-phase` skill |
| Verifier | `toprank-main` (Extra) | `get-shit-done-main` (Core) | fixture eval patterns |
| Archive | `pentest-ai-agents-main` (Extra) | `toprank-main` (Extra) | findings DB schema |
| Memory | `mempalace-develop` (Core) | `context-mode-main` (Extra) | drawer structure |
| Reviewer agent | `agent-creator` (Extra) | `awesome-claude-agents-main` (Other) | `SKILL.md` + `prompt-patterns.md` |
