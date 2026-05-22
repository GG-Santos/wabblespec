# Other References — v6.1 Lookup Table

> Source: `C:\Vaults\references\Other Projects References\`
> 80+ repos. Most covered in v6 ledger. This file: v6.1-specific signal extraction only.
> Format: Lookup table. Read individual repo only when explicitly pointed here.

---

## MVP-Relevant (read during building)

| Repo | v6.1 module | What to extract | Key file |
|---|---|---|---|
| `claude-code-hooks-mastery` | Hook | Hook pattern library, pre-tool-use recipes | `hooks/` directory |
| `destructive_command_guard-main` | Hook | Safety guard pattern: block + explain vs block + silent | guard logic |
| `claude-code-safety-net-main` | Guard / Hook | Blast radius check before execution | safety check patterns |
| `awesome-claude-agents-main` | Reviewer | Agent decomposition: core/orchestrators/specialized | `agents/` structure |
| `claude-code-workflows-main` | Verifier | Code review as structured verification workflow | `code-review/` |
| `SuperClaude_Framework-master` | Invariants | Invariant enforcement patterns, spec-wide rules | CLAUDE.md + rules |
| `everything-claude-code-main` | CLAUDE.md | Broad CLAUDE.md pattern library | root CLAUDE.md |
| `awesome-claude-code-subagents-main` | Reviewer | Subagent design patterns across all domains | `agents/` |

---

## Hook-specific refs

| Repo | Signal | Extract |
|---|---|---|
| `claude-code-hooks-mastery` | Hook lifecycle mastery | Pre/post tool-use, session start/stop patterns |
| `destructive_command_guard-main` | Guard hook | exit-code contract, stdin JSON parsing, block vs warn |
| `agent-rules-main` | Project rule hooks | `.mdc` rule format, install-project-rules.sh pattern |

**When building the receipt validator hook**, read `claude-code-hooks-mastery` + `destructive_command_guard-main` alongside `extra-refs-v61.md § claude-code-main`.

---

## Skill/Activation Pattern refs

| Repo | Signal | Extract |
|---|---|---|
| `anthropic` | Niche skill patterns | Inspect only — no structural copy |
| `agent-skills-main` | Skill packaging | SKILL.md format variants |
| `ai-skills-main` | MCP + memory skill patterns | skill-rules.json activation examples |
| `awesome-agent-skills-main` | Broad agent skill patterns | activation trigger variety |
| `Agent-Skills-for-Context-Engineering-main` | Context-efficient skill design | loading gate examples |
| `claudekit-skills-main` | Full lifecycle skills | phase-gated skill examples |
| `claude-skills-main` | MCP + mobile skills | platform-specific SKILL.md |
| `stitch-skills-main` | Game + memory skill combo | multi-domain SKILL.md |

---

## Memory refs

| Repo | Signal | Extract |
|---|---|---|
| `homunculus-main` | Memory + spec integration | spec-memory binding pattern |
| `obsidian-skills` | Graph memory | node/edge patterns for notes |
| `interface-design-main` | Memory + design | evidence-based design decisions |

---

## Verifier / Quality gate refs

| Repo | Signal | Extract |
|---|---|---|
| `claude-code-workflows-main` | Code review workflow | `code-review/pragmatic-code-review-subagent.md` |
| `claude-code-security-review-main` | Security verification | security check receipt pattern |
| `claude-code-best-practice-main` | Best practice gates | pre-execution checklist |
| `adversarial-spec-main` | Adversarial review patterns | red-team prompt patterns |
| `clawsec-main` | Security + spec | security spec template |

---

## Archive / Receipt refs

| Repo | Signal | Extract |
|---|---|---|
| `security-bluebook-builder-main` | Structured findings report | `references/bluebook_template.md` |
| `pentest-ai-agents-main` | Status transition model | see `extra-refs-v61.md` |

---

## Platform package refs (L3, post-MVP)

| Repo | Platform | Extract when building |
|---|---|---|
| `aso-skills-main` | Mobile (iOS/App Store) | store submission + ASO gates |
| `gsap-skills-main` | Web (animation) | Web platform animation constraints |
| `hig-doctor-main` | Mobile (Apple HIG) | HIG compliance checker pattern |
| `iothackbot-master` | IoT | device safety, OTA, protocol patterns |
| `webgpu-claude-skill-main` | Web (GPU) | WebGPU platform target spec |
| `Anthropic-Cybersecurity-Skills-main` | Security gateway | L4 Security capability patterns |

---

## Design / UX refs (L4 Aesthetic gateway, post-MVP)

| Repo | Signal |
|---|---|
| `ui-ux-pro-max-skill-main` | Full design system + accessibility gates |
| `creative-director-skill-main` | Creative direction role pattern |
| `interface-design-main` | Evidence-based design decisions |
| `skill.color-expert-main` | Color system as platform-specific rule |
| `humanizer-main` | Voice/tone register patterns |

---

## Economy / Token density refs

| Repo | Signal | Extract |
|---|---|---|
| `agent-rules-main` | Minimal rule format (.mdc) | compact rule card structure |
| `repren-master` | Batch rename — minimal CLI | token-lean command design |
| `auto-commenter-main` | Context-efficient comment insertion | minimum viable MCP tool |
| `context-mode-main` | Sandboxed verbose output | see `extra-refs-v61.md` |

---

## Orchestration refs (multi-agent, post-MVP)

| Repo | Signal | Defer until |
|---|---|---|
| `awesome-claude-agents-main` | Tech lead orchestrator pattern | TeamPlan L4 |
| `agents-main` | Multi-model agent coordination | TeamPlan L4 |
| `compound-engineering-plugin-main` | Plugin-based agent composition | MCPBridge post-MVP |
| `claudian-main` | IoT + orchestration | IoT platform L3 |

---

## Low-signal / Skip for v6.1

These repos are in the v6 ledger but add no new signal for the MVP 7 modules:

| Repo | Why skip |
|---|---|
| `marketingskills-main` | Marketing domain, no structural signal |
| `notion-cookbook-main` | Notion MCP, not in MVP |
| `claude-cookbooks-main` | Pattern cookbook, covered by core refs |
| `pm-skills-main` | PM skills, no receipt/hook signal |
| `Product-Manager-Skills-main` | Same |
| `geo-seo-claude-skills-main` | SEO domain, no structural signal |
| `seo-geo-claude-skills-main` | Duplicate signal |
| `claude-ai-music-skills-main` | Music domain |
| `awesome-legal-skills-main` | Legal domain |
| `mcp-server-guide-main` | MCP post-MVP |
| `web-asset-generator-main` | Web assets, post-MVP |
| `superpowers-chrome-main` | Chrome extension, post-MVP |
| `prompt-master-main` | Prompt patterns, subsumed by agent-creator |
| `SkillForge` | Skill factory patterns, post-MVP |
| `Skill Creator` | Same signal as agent-creator Extra ref |
| `template` | Generic template, low signal |
| `skills-main (1-4)` | Variant skill collections, covered by core |
| `OpenSpec` (Other) | Duplicate of Core OpenSpec-main |
| `oh-my-claudecode-main` (Other) | Duplicate of Core |
| `get-shit-done-main` (Other) | Duplicate of Core |
| `Claude-Code-Game-Studios-main` (Other) | Duplicate of Core |
| `claude-code-security-review-main` (Other) | Duplicate of Core |
| `superpowers-main` (Other) | Duplicate of Core |
| `superpowers` (Other) | Duplicate |
| `cartographer-main` (Other) | Duplicate of Core |

---

## Refs with cautions (use carefully)

| Repo | Caution |
|---|---|
| `toprank-main` | Live mutation workflows need approval gates and rollback receipts |
