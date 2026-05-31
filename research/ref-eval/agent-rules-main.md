# Ref-Eval: agent-rules-main

**Reference path:** `C:\Vaults\references\Other Projects References\agent-rules-main\agent-rules-main`
**Evaluated:** 2026-05-31
**Evaluator:** ref-adopt pipeline

---

## Section 1 — Reference Summary

**Type:** Archived personal slash-command library (Cursor `.mdc` rules + global rules). The README explicitly states: "This was old stuff I used mid 2025 when I was still using Cursor. My new work is here: https://github.com/steipete/agent-scripts."

**Problem it solves:** Provides slash commands (`/commit`, `/bug-fix`, `/pr-review`, etc.) for Claude Code/Cursor, plus MCP server setup docs and Swift/Apple platform reference documentation.

**Behavioral content:** Decision logic for multi-step workflows (bug-fix flow, PR review from 6 roles, Five Whys analysis, continuous improvement triggers). The `continuous-improvement.mdc` encodes when to create/update rules (pattern in 3+ files threshold, quality checklist with 6 criteria). The `update-docs.mdc` encodes a parallel-agent documentation system with LLM-optimization constraints.

**Structural content:** `.mdc` frontmatter format (description, globs, alwaysApply), DO/DON'T code examples convention, cross-reference linking between rules, section headings (When to Apply, Common Pitfalls).

**Interaction content:** `install-project-rules.sh` writes to `~/.claude/CLAUDE.md` via `@path` import. `steipete-mcps.md` references `mcp-sync.sh`. `cursor-rules-meta-guide.mdc` governs authoring of all other `.mdc` files. MCP best practices govern both `mcp-best-practices.mdc` and `mcp-releasing.mdc`.

**Maturity signals:** No tests, no CI, no versioned releases, README explicitly deprecates the repo. Personal authorship by Peter Steinberger (steipete). Updated mid-2025. Low maturity.

**Red flags:** Deprecated. `tweak-claude.sh` and `install-project-rules.sh` contain hardcoded paths (`/Users/steipete/Projects/`). `commit-fast.mdc` auto-skips confirmation. `steipete-mcps.md` hardcodes model names (OpenAI `gpt-4o`, `llava:latest`).

---

## Section 2 — File Inventory

| Path | Purpose | Size | Key contents | Status | Transfer check |
|---|---|---|---|---|---|
| README.md | Deprecation notice | Small | Points to new repo | Read | None — no content |
| docs/appkit.md | Apple AppKit framework docs (scraped) | Large | UIKit/AppKit API reference | Skipped | Swift domain only — no transferable framework or behavioral patterns |
| docs/mcp-best-practices.mdc | MCP tool development standards | Medium | no-stdio rule, info command, Pino logging, release checklist | Read | YES — no-stdio, lenient parameter parsing, info command convention are transferable behavioral rules for any tool interface |
| docs/mcp-releasing.mdc | NPM release procedure for MCP | Small | dry-run, beta tagging, changelog check | Read | Partial — release prep checklist has overlap with archive.py workflow |
| docs/modern-swift.md | Swift architecture patterns | Medium | SwiftUI state management, async patterns | Skimmed | None — Apple platform domain |
| docs/swift-argument-parser.mdc | Swift CLI arg parser docs (scraped) | Large | ArgumentParser API | Skipped | None — Swift domain only |
| docs/swift-observable.mdc | Swift Observable protocol docs (scraped) | Large | @Observable API | Skipped | None — Swift domain only |
| docs/swift-observation.mdc | Swift Observation framework (scraped) | Large | Observation API | Skipped | None — Swift domain only |
| docs/swift-testing-api.mdc | Swift Testing framework API (scraped) | Large | @Test, @Suite, #expect macros | Skimmed | None — Swift Testing domain only |
| docs/swift-testing-playbook.mdc | XCTest → Swift Testing migration | Large | Migration patterns, parameterized tests | Skimmed | None — Swift domain only |
| docs/swift6-migration.mdc | Swift 6 concurrency migration (scraped) | Large | Actor, Sendable, data race safety | Skipped | None — Swift domain only |
| docs/swiftdata.md | SwiftData framework docs (scraped) | Large | SwiftData persistence API | Skipped | None — Swift domain only |
| docs/swiftui.md | SwiftUI framework docs (scraped) | Very Large | SwiftUI full API | Skipped | None — Swift domain only |
| docs/uikit.md | UIKit framework docs (scraped) | Very Large | UIKit full API | Skipped | None — Swift domain only |
| global-rules/github-issue-creation.mdc | GitHub issue creation template | Small | Plan/create/present flow, `gh issue create` | Read | Minor — issue template structure (summary/problem/approach/criteria/scope) partially relevant to task card structure |
| global-rules/mcp-peekaboo-setup.mdc | Peekaboo MCP setup guide | Small | Screenshot tool config | Read | None — tool-specific |
| global-rules/mcp-sync-rule.md | MCP config sync script + docs | Medium | Cross-app MCP config diff/sync | Read | None — tool-specific utility |
| global-rules/mcp-sync.sh | Bash config comparison script | Medium | jq-based diff logic | Skimmed | None — tool-specific |
| global-rules/setup-mcps.sh | MCP install script | Small | `claude mcp add-json` calls | Skimmed | None — tool-specific |
| global-rules/steipete-mcps.md | MCP server catalog and setup | Medium | Server list, install commands, `cly` terminal trick | Read | Minor — `cly` terminal title pattern has no project equivalent; named model identifiers (I6 violation) |
| global-rules/terminal-title-wrapper.zsh | zsh function for terminal titles | Tiny | `cly` function | Skimmed | None — zsh/macOS specific |
| install-project-rules.sh | CLAUDE.md installer | Small | `@path` import injection | Read | None — tool-specific |
| project-rules/add-to-changelog.mdc | Changelog update command | Small | Keep a Changelog format, 6 steps | Read | None — already covered by changelog SKILL.md |
| project-rules/analyze-issue.mdc | GitHub issue analysis | Small | 10-section spec template | Read | Minor — Out of Scope section in issue template echoes task card non-goals |
| project-rules/bug-fix.mdc | Bug fix workflow | Small | Create issue → branch → test → PR | Read | None — domain workflow already covered |
| project-rules/check.mdc | Code quality check workflow | Small | Priority order: build errors → test failures → lint | Read | None — domain-specific |
| project-rules/clean.mdc | Code formatting commands | Small | black/isort/flake8/prettier/eslint | Read | None — domain-specific |
| project-rules/code-analysis.mdc | Code analysis menu (6 types) | Small | Knowledge graph, quality, performance, security, architecture, test coverage | Read | Minor — six-type analysis taxonomy overlaps with gateway skills |
| project-rules/commit-fast.mdc | Fast commit with auto-selection | Small | Generate 3 suggestions, auto-use first | Read | AVOID — auto-skip conflicts with I10 (implied completion) |
| project-rules/commit.mdc | Conventional commit workflow | Small | 12 commit types with emojis, body for complex changes | Read | None — already covered by commit SKILL.md |
| project-rules/context-prime.mdc | Project context loading | Small | README → CLAUDE.md → git ls-files → config review | Read | None — already covered |
| project-rules/continuous-improvement.mdc | Rule improvement framework | Medium | 3+ files threshold, quality checklist (6 criteria), review cadence | Read | YES — "3+ files" creation trigger and 6-item quality checklist are transferable to CLAUDE.md skill authoring |
| project-rules/create-command.mdc | Command creation guide | Small | 7 command categories, 7-section template | Read | None — already covered by skill-creator |
| project-rules/create-docs.mdc | Documentation creation | Small | 11-section doc template | Read | None — partially covered by document SKILL.md |
| project-rules/cursor-rules-meta-guide.mdc | Cursor rules authoring standards | Small | DO/DON'T examples, use actual codebase code, cross-reference DRY | Read | YES — "use actual codebase examples" and cross-reference DRY principles are transferable to CLAUDE.md skill authoring conventions |
| project-rules/five.mdc | Five Whys root cause analysis | Small | 5-step problem drill-down, validate root cause, systemic solutions | Read | YES — structured root cause analysis method not yet in diagnose SKILL.md |
| project-rules/implement-task.mdc | Task implementation approach | Small | Strategy → Approaches → Tradeoffs → Steps → Checklist | Read | None — already covered by specify/decompose |
| project-rules/mcp-inspector-debugging.mdc | MCP Inspector Playwright workflow | Medium | Phase 1-4 Playwright automation, iTerm integration | Read | None — macOS/tool-specific |
| project-rules/mermaid.mdc | Mermaid diagram generation | Small | ER, flowchart, sequence, class diagram types | Read | None — diagram tooling |
| project-rules/modern-swift.mdc | Modern Swift coding standards | Large | SwiftUI architecture, @Observable, async/await | Read | None — Swift domain only |
| project-rules/pr-review.mdc | Multi-perspective PR review | Small | 6 roles: PM/Dev/QE/Security/DevOps/UX | Read | YES — explicit 6-role review taxonomy is a supplement to reviewer SKILL.md |
| project-rules/safari-automation.mdc | Safari AppleScript automation | Medium | Window management, JS execution, Shadow DOM, timing | Read | None — macOS AppleScript domain |
| project-rules/screenshot-automation.mdc | Screenshot AppleScript patterns | Medium | Bundle ID detection, screencapture, error handling | Read | None — macOS AppleScript domain |
| project-rules/update-docs.mdc | LLM-optimized documentation system | Medium | Parallel agents, timestamps, concrete file refs, no-duplication, token-efficient | Read | YES — strong documentation system with LLM-optimization constraints transferable to document SKILL.md |
| swift6-migration-compact.md | Compact Swift 6 migration reference | Medium | Data race safety, actor isolation, migration checklist | Skimmed | None — Swift domain only |
| tweak-claude.sh | Interactive MCP/rules management CLI | Small | Add/remove MCPs and rules interactively | Read | None — tool-specific, hardcoded personal paths |

**Connection map:**
- `cursor-rules-meta-guide.mdc` --[governs]--> all `.mdc` files: required structure (frontmatter + bullet style)
- `continuous-improvement.mdc` --[triggers]--> all `.mdc` files: when to create/update rules
- `install-project-rules.sh` --[writes to]--> `~/.claude/CLAUDE.md`: injects `@path` import
- `steipete-mcps.md` --[references]--> `mcp-sync.sh`: sync utility
- `mcp-best-practices.mdc` --[governs]--> `mcp-releasing.mdc`: release checks reference the best practices
- `modern-swift.mdc` and `docs/modern-swift.md`: identical content in two locations

---

## Section 3 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `continuous-improvement.mdc` | "3+ files" rule creation threshold | Gives explicit trigger signal for when to create new skills rather than relying on vague "patterns" | Add to CLAUDE.md skill authoring: "Create a new skill when a behavioral pattern appears unguided in 3+ distinct agent actions" | Medium |
| `continuous-improvement.mdc` | 6-item quality checklist (Actionable/Specific/Tested/Complete/Current/Linked) | Gives a named checklist for evaluating whether a new skill is ready to publish | Add to CLAUDE.md or skill-creator SKILL.md as a pre-publish gate | Medium |
| `cursor-rules-meta-guide.mdc` | "Show actual codebase examples, not theoretical ones" | Prevents abstract examples that don't match real project patterns | Add to CLAUDE.md skill authoring conventions section | Low-Medium |
| `cursor-rules-meta-guide.mdc` | Cross-reference related rules (DRY) | Prevents duplicating content across skills; link instead | Add to CLAUDE.md: "Cross-reference related skills by name rather than duplicating content" | Low |
| `update-docs.mdc` | Parallel agent dispatch for doc sections | Speeds up large documentation tasks by running section agents in parallel | Add to document SKILL.md as an explicit parallel dispatch pattern | Medium |
| `update-docs.mdc` | Timestamp header on every generated doc (`<!-- Generated: YYYY-MM-DD HH:MM:SS UTC -->`) | Signals when docs were last updated; avoids stale doc confusion | Add to document SKILL.md output format section | Low |
| `update-docs.mdc` | No-duplication enforcement: each piece of information in exactly ONE file | Prevents doc fragmentation and drift | Add to document SKILL.md as a structural gate | Medium |
| `update-docs.mdc` | Token-efficient writing: avoid redundant explanations, focus on concrete file references | Makes docs more useful for LLM consumers of the project | Add to document SKILL.md under output format | Medium |
| `project-rules/five.mdc` | Five Whys structured drill-down with root cause validation | Adds a named method to the diagnose skill's reasoning toolkit | Add to diagnose SKILL.md as an optional root cause analysis mode | Low |
| `project-rules/pr-review.mdc` | 6-role review taxonomy (PM/Dev/QE/Security/DevOps/UX) | Reviewer skill currently lacks explicit role assignment; named roles improve coverage | Add role taxonomy table to reviewer SKILL.md | Low |

---

## Section 4 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `commit-fast.mdc` | Auto-skips confirmation on commit selection | Violates I10 (no implied completion) — agent auto-selects without human verification | Already excluded | High |
| `steipete-mcps.md` | Hardcodes model names (`gpt-4o`, `llava:latest`) | Violates I6 (runtime is vendor-neutral) | Do not adopt model references | High |
| `tweak-claude.sh` | Hardcodes personal paths (`/Users/steipete/`) | Would break on any machine | Do not adopt scripts with hardcoded paths | Medium |
| `global-rules/setup-mcps.sh` | Installs specific external tools as dependencies | Couples framework to external services | Do not adopt tool-specific setup | Medium |
| `cursor-rules-meta-guide.mdc` | Adds Cursor-specific frontmatter conventions (`globs:`, `alwaysApply:`) | These are Cursor/Claude Code specific fields that may not be appropriate in all contexts | Adapt only the content principles, not the format fields | Low |
| `continuous-improvement.mdc` | "Monthly/Quarterly/Annually" maintenance cadence | Time-sensitive content — violates CLAUDE.md "no time-sensitive info in descriptions" rule | Extract the principle (review cadence) without dates | Low |

---

## Section 5 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| `continuous-improvement.mdc` — "3+ files" threshold | Adapt | Specific, actionable trigger condition | CLAUDE.md skill authoring | Medium |
| `continuous-improvement.mdc` — quality checklist | Adapt | Named 6-item gate not yet in project | CLAUDE.md or skill-creator | Medium |
| `cursor-rules-meta-guide.mdc` — codebase examples rule | Adapt | Prevents theoretical drift in skill examples | CLAUDE.md skill authoring | Low-Medium |
| `cursor-rules-meta-guide.mdc` — cross-reference DRY | Adapt | Reduces content duplication across skills | CLAUDE.md skill authoring | Low |
| `update-docs.mdc` — parallel agent dispatch | Adapt | Not yet in document SKILL.md | document SKILL.md | Medium |
| `update-docs.mdc` — timestamp + no-duplication + token-efficient | Adapt | Three concrete output constraints | document SKILL.md | Medium |
| `five.mdc` — Five Whys method | Adapt (minor) | Structured method for diagnose skill | diagnose SKILL.md | Low |
| `pr-review.mdc` — 6-role taxonomy | Study only | Reviewer skill already partially covers; roles add marginal value | reviewer SKILL.md (reference only) | Low |
| `mcp-best-practices.mdc` — no-stdio, info command, Pino | Avoid | We consume MCP tools, don't build them; rules are for MCP server developers | — | — |
| `commit-fast.mdc` | Avoid | I10 violation | — | — |
| `steipete-mcps.md` — model names | Avoid | I6 violation | — | — |
| All Swift/Apple docs | Avoid | Domain-specific, no transfer | — | — |
| AppleScript automation files | Avoid | macOS GUI domain, no transfer | — | — |
| Tool-specific setup scripts | Avoid | Hardcoded paths + external dependencies | — | — |

---

## Section 6 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 4 | Framework builds skills/rules; reference builds rules. Conceptual overlap exists but primary domain (Swift/macOS) doesn't intersect |
| Architecture fit | 3 | Cursor `.mdc` format vs. WabbleSpec SKILL.md; different but compatible for content extraction |
| Implementation fit | 6 | Transferable items are simple text additions to existing SKILL.md and CLAUDE.md files |
| Maintenance fit | 7 | Transferable items are stable behavioral principles, not version-dependent content |
| Risk level | 2 | Low risk — deprecated repo, no model dependencies in transferable items |
| Overall usefulness | 4 | Narrow band of transferable content; most of reference is domain-specific or deprecated |

**Overall usefulness 4 — inspiration-only.**

---

## Section 7 — Final Verdict

**Classification: inspiration-only (4/10)**

**Best 3 to steal:**
1. `update-docs.mdc`: parallel agent dispatch + token-efficient writing + no-duplication enforcement (3 concrete constraints in one file)
2. `continuous-improvement.mdc`: "3+ files" creation threshold + 6-item quality checklist — these are named, specific, actionable additions to skill authoring conventions
3. `cursor-rules-meta-guide.mdc`: "use actual codebase examples, not theoretical ones" — small but directly applicable to CLAUDE.md

**Worst 3 to avoid:**
1. `commit-fast.mdc`: auto-skip confirmation (I10)
2. `steipete-mcps.md` model name references (I6)
3. All Swift/Apple scraped docs — zero transfer value, large files that would bloat context

**Recommended next action:** Proceed to Phase 2 (ref-plan) for the narrow set of Tier 1 items. No Tier 4/5/6 items justified.

---

## Section 8 — Project Synthesis

The reference encodes a "living rule improvement loop" (continuous-improvement.mdc): observe patterns → create rules → measure effectiveness → update or deprecate. WabbleSpec has I8 (execution → receipt → instinct → synth → blueprint) but no explicit threshold signal for when to create a *new* skill from observed patterns (vs. augmenting an existing one).

**Synthesis idea:** A "pattern density threshold" for skill creation could be derived by combining continuous-improvement's "3+ files" signal with WabbleSpec's instinct observation taxonomy. When 3+ instinct observations of the same type accumulate in a room, that is the trigger to run Specify for a new skill rather than augmenting an existing one.

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Pattern density → skill creation trigger | "3+ files" threshold from continuous-improvement.mdc | Instinct observation count tracking in memory layer | CLAUDE.md skill authoring + instinct SKILL.md | No formal threshold for new-skill vs. augmentation decisions |

---

## Section 9 — Expansion Opportunities

Per-skill growth scan completed. Reference has ~45 files. Swift domain skills: 0 transfer. MCP server development skills: 0 transfer (we consume, don't build). Generic workflow skills: already covered by WabbleSpec.

**Remaining candidates:**
- `five.mdc` (Five Whys): diagnose SKILL.md exists but lacks a named root cause drill-down method. Adding Five Whys is a Tier 1 augmentation, not a net-new capability.
- `update-docs.mdc` (LLM-optimized documentation system): document SKILL.md exists. Adding the parallel dispatch pattern is augmentation.
- `mcp-best-practices.mdc` (MCP server development standards): WabbleSpec has no MCP server development module. But this is a domain we do not build in — creating an MCP server development skill would be out of scope.

**Net-new capabilities the project lacks:** None. All reference capabilities either exist in WabbleSpec or are out of project scope.

No Tier 7 candidates.
