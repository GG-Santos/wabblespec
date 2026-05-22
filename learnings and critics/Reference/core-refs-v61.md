# Core References — v6.1 Extraction Cards

> Source: `C:\Vaults\references\Core Project References\`
> Format: One card per repo. What to extract for MVP 7 modules. No prose.

---

## get-shit-done-main

**Stars: 63K | Language: JS | v6.1 relevance: TOP**

| Module | Extract | Key files |
|---|---|---|
| Recipe | Phase/complexity detection logic | `.planning/` conventions |
| Decompose | Phase-per-task breakdown | `plan-phase` skill |
| Executor | execute-phase wave runner | `execute-phase` skill |
| Verifier | verify-work as distinct phase | `verify-work` skill |
| Archive | STATE.md continuity pattern | `.planning/STATE.md` |

**What to copy:**
- `verify-work` as a phase separate from execute — proven at 63K users
- `.planning/` directory convention → map to `.wabblespec/plans/`
- CONTEXT.md predicate format (grep-auditable, verbatim citations) → map to `meta.md`
- Named defect taxonomy (25+ patterns: Port Drift, State Trample, Phase-Dir Prefix Drift) → expand WabbleSpec's 6 error types

**What to avoid:**
- 147 workflow files without consolidation
- `--dangerously-skip-permissions` as default use case

**Read when:** Building Executor, Verifier, or Archive modules.

---

## OpenSpec-main

**Stars: 49K | Language: TypeScript | v6.1 relevance: HIGH**

| Module | Extract | Key files |
|---|---|---|
| Specify | proposal → spec → archive artifact flow | `commands/` |
| Recipe | Target routing before commit | workspace detection logic |
| Archive | `/opsx:archive` pattern | archive command |

**Critical lesson (direct warning to v6.1):**
> WORKSPACE_REIMPLEMENTATION_DIRECTION doc says: "Don't predetermine path with abstract internal machinery." They built materializers, adapters, target metadata — tore it all out. Users never needed it.
> WabbleSpec: do not build L3-L8 before L0-L2 user-visible workflow runs.

**What to copy:**
- "Workspace visibility is not change commitment" — separate exploration from planning from execution
- User-visible flow first: every phase must answer "can user complete next natural step?"

**What to avoid:**
- Mid-reimplementation instability — do not copy implementation, only concepts
- Multi-platform support (20+ assistants) = lowest-common-denominator

**Read when:** Building Specify module or defining phase artifact structure.

---

## mempalace-develop

**Stars: private | Language: Python | v6.1 relevance: TOP**

| Module | Extract | Key files |
|---|---|---|
| Memory | wings/rooms/drawers hierarchy | `src/` storage layer |
| Memory | Search/storage separation | retrieval vs. write modules |
| Memory | Staleness — what NOT to do | No staleness model = retrieval noise |

**What validates WabbleSpec design:**
- `drawers` as atomic evidence unit — independently converged, vocabulary confirmed
- Storage ↔ search separation already correct in WabbleSpec
- Local-first validated

**What to avoid:**
- Embedding-based semantic retrieval (300MB model, external dep, breaks offline)
- 29 MCP tools — scatter not power
- Benchmark claims disconnected from outcomes (96.6% R@5 on LongMemEval = meaningless for spec evidence)
- Verbatim storage — structured evidence is correct for framework use

**Read when:** Building Memory module or designing staleness states.

---

## oh-my-claudecode-main

**Stars: 34K | Language: TypeScript | v6.1 relevance: HIGH**

| Module | Extract | Key files |
|---|---|---|
| Executor | Agent roles: analyst/architect/executor/verifier | `.omc/agents/` |
| Reviewer | Adversarial agent pattern | `code-reviewer` agent |
| skill-rules.json | Skill scoping: project vs user level | `.omc/skills/` |
| Recipe | `/omc-doctor` health check concept | diagnostic command |

**What to copy:**
- Skill scoping: `.omc/skills/` (project, version-controlled) vs `~/.omc/skills/` (personal) → formalize in WabbleSpec
- `/omc-doctor` diagnostic command → WabbleSpec needs health check entry point
- Writer-memory and session search as named user-invocable skills (not hidden infrastructure)
- Model routing by task complexity (haiku/sonnet/opus) — validates RuntimeProbe direction

**What to avoid:**
- Growing skill count indefinitely without pruning mechanism
- "Zero learning curve" at expense of structural guarantees

**Read when:** Building Reviewer agent or designing skill scoping.

---

## agent-os-main

**Stars: 4.6K | Language: Shell | v6.1 relevance: MED**

| Module | Extract | Key files |
|---|---|---|
| Specify | discover-standards → inject-standards flow | `commands/agent-os/` |
| Economy | "every word costs tokens" philosophy | `agent-os/standards/` |

**What to copy:**
- "Discover before prescribe" — extract real patterns before writing rules → Explore feeds Specify
- "Every word costs tokens" — rules-first, then reasoning, minimal, example-driven, actionable
- One concept per standard — better decomposition than hierarchical depth

**What to avoid:**
- Advisory-only standards (no enforcement = useless without Gate)
- Narrow scope without expansion path

**Read when:** Writing Economy module or designing standards injection in Specify.

---

## superpowers-main

**Stars: private | Language: Markdown | v6.1 relevance: HIGH**

| Module | Extract | Key files |
|---|---|---|
| Decompose | 7-stage mandatory workflow mental model | `README.md` |
| Executor | Git worktrees as wave isolation | worktree commands |
| Specify | Mandatory brainstorm/propose gate | first-stage enforcement |

**What to copy:**
- Git worktrees as Executor wave isolation — stronger than checkpoint-based rollback. `EnterWorktree`/`ExitWorktree` already in harness.
- Mandatory brainstorm gate before P1 spec work on new projects — elevate Propose from demand-triggered to required
- 7-stage user-facing mental model for onboarding doc

**What to avoid:**
- Multi-platform portability (depth > breadth for this use case)
- Vague "skills trigger automatically" claims
- Framing framework as methodology user follows — WabbleSpec does the following

**Read when:** Building Decompose or designing first-contact onboarding doc.

---

## anthropic-skills-main

**Stars: official | Language: mixed | v6.1 relevance: HIGH**

| Module | Extract | Key files |
|---|---|---|
| skill-rules.json | Skill packaging contract | `SKILL.md` patterns |
| Memory | Memory retrieval patterns | memory skill |
| Hook | Pre-tool-use hook examples | hooks config |

**What to copy:**
- Skill packaging: SKILL.md + skill-rules.json activation contract
- Hook-based context injection patterns
- Progressive loading gate references

**Read when:** Building skill-rules.json schema or hook activation patterns.

---

## Claude-Code-Game-Studios-main

**Stars: private | Language: Markdown | v6.1 relevance: MED**

| Module | Extract | Key files |
|---|---|---|
| skill-rules.json | Path-scoped activation (`file_path_patterns`) | path rule examples |
| Hook | Pre-commit receipt check concept | 12 hook examples |

**What to copy:**
- `file_path_patterns` as optional activation field in skill-rules.json — rules fire on active file path prefix
- Pre-commit hook checking for pending receipts/open REVISE cycles (git-layer safety net)

**What to avoid:**
- 49 agents = theater (same model, different labels)
- 73 slash commands = discovery failure
- Model-name-to-role coupling (violates I6)
- Monolithic CLAUDE.md

**Read when:** Adding path-scoped activation to skill-rules.json schema.

---

## codeflow-main

**Stars: private | Language: mixed | v6.1 relevance: LOW (MVP)**

| Module | Extract | Key files |
|---|---|---|
| Memory | Graph layer patterns | local graph structure |

Defer until Memory core (Memory + MemorySearch) is proven. EntityGraph is v2.

---

## claude-code-security-review-main

**Stars: private | Language: mixed | v6.1 relevance: MED**

| Module | Extract | Key files |
|---|---|---|
| Verifier | Security check patterns | review commands |
| Receipt | Audit receipt patterns | receipt schema |

**Read when:** Building security gateway at L4 (post-MVP).

---

## cartographer-main (Core)

**Stars: private | Language: mixed | v6.1 relevance: MED**

| Module | Extract | Key files |
|---|---|---|
| Recipe | Project type detection | detection patterns |
| WabbleFlow | Blast radius calculation | graph queries |

**Read when:** Building Recipe target detection.

---

## Low-priority core refs (skip for MVP)

| Repo | Reason to skip for MVP | When to revisit |
|---|---|---|
| andrej-karpathy-skills-main | Skill packaging, no MVP-specific signal | L6+ |
| caveman-main | CLAUDE.md style, no structural patterns | Economy module |
| claude-plugins-official-main | MCP bridge patterns, not in MVP | MCPBridge post-MVP |
| financial-services-main | Data schemas, no MVP signal | Data gateway L4 |
| G0DM0D3-main | CLI patterns, covered by other refs | CLI platform L3 |
| graphify-7 | Graph/EntityGraph, v2 territory | Memory v2 |
| mattpocock-skills-main | TypeScript skill patterns | SDK target |
| oh-my-codex-main | Codex CLI patterns | Multi-agent |
| ui-ux-pro-max-skill-main | Design gateway | L4 Aesthetic |
