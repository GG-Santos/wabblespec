# Ref-Eval: hermes-agent-main

**Reference slug:** hermes-agent-main
**Date:** 2026-05-30
**Trust level:** MEDIUM
**Reference type:** Production application (NousResearch open-source agent runtime)

---

## Step 1b — File Inventory

| Path | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| `AGENTS.md` | Developer guide | Large | Architecture, SKILL.md authoring standards, dependency pinning policy, slot-command registry pattern, plugin system, toolset rules | Read |
| `agent/background_review.py` | Post-turn self-improvement | Medium | `_SKILL_REVIEW_PROMPT`, `_MEMORY_REVIEW_PROMPT`, `_COMBINED_REVIEW_PROMPT` strings; forked review agent logic | Read |
| `agent/error_classifier.py` | API error taxonomy | Large | `FailoverReason` enum, priority-ordered classification pipeline, 16 error reason types | Read |
| `agent/iteration_budget.py` | Iteration counter | Small | Thread-safe `IterationBudget` class, `consume/refund` pattern | Read |
| `agent/skill_commands.py` | Skill slash dispatch | Medium | `scan_skill_commands`, `build_skill_invocation_message`, slug normalization | Read |
| `agent/skill_bundles.py` | Bundle slash dispatch | Medium | YAML-defined multi-skill bundles, mtime-based cache invalidation | Read |
| `agent/curator.py` | Skill lifecycle manager | Large (100 lines read) | Curator invariants, lifecycle states, interval config | Read (partial) |
| `hermes-already-has-routines.md` | Marketing / comparison | Small | Cron vs Claude Code Routines comparison; Hermes scheduling capabilities | Read |
| `optional-skills/autonomous-ai-agents/DESCRIPTION.md` | Category doc | Tiny | One-line description | Read |
| `acp_adapter/*.py` | ACP server (IDE integration) | Medium | VS Code/Zed/JetBrains adapter | Skipped — not relevant to WabbleSpec |
| `gateway/platforms/*.py` | Messaging platform adapters | Very Large | Telegram, Discord, Slack, etc. | Skipped — not relevant |
| `agent/lsp/` | LSP client | Medium | Language server integration | Skipped — not relevant |
| `ui-tui/` | React/Ink TUI | Large | Terminal UI | Skipped — not relevant |
| `agent/transports/` | Provider transport layer | Large | Anthropic, Bedrock, Gemini, Codex adapters | Skipped — not relevant |

---

## Step 1c — Connection Map

```
AGENTS.md --(documents)--> run_agent.py, cli.py, model_tools.py, toolsets.py
run_agent.py --(spawns)--> agent/background_review.py::_run_review_in_thread
             --(uses)---> agent/iteration_budget.py::IterationBudget
             --(uses)---> agent/error_classifier.py::classify_api_error
model_tools.py --(imports)--> tools/registry.py (auto-discovery)
tools/*.py --(register to)--> tools/registry.py at import time
agent/skill_commands.py --(imports)--> tools/skills_tool.py, agent/skill_preprocessing.py
agent/skill_bundles.py --(late import)--> agent/skill_commands._load_skill_payload, _build_skill_message
agent/curator.py --(uses)--> tools/skill_usage.py, auxiliary_client.py
hermes_cli/commands.py --(drives)--> COMMAND_REGISTRY → CLI + gateway + Telegram + Slack + autocomplete
```

**Critical contracts:**
- `background_review.py` → `AIAgent`: fork inherits parent's `_cached_system_prompt` (byte-identical) so prefix cache hits. Breaking this — e.g. adding a timestamp — burns ~26% of per-turn cost.
- `skill_commands.py` → `tools/skills_tool.py::SKILLS_DIR`: skill loading is sandboxed to trusted roots. An external path not under SKILLS_DIR or `external_skills_dirs` gets rejected.
- `model_tools.py` → `tools/registry.py`: auto-discovery runs at import time; a tool not in a `TOOLSETS` entry is never exposed to the agent even if registered.

---

## Dimension 1 — Behavior (operational detail)

**SKILL.md authoring standard (AGENTS.md:619–690):**
- `description:` MUST be ≤ 60 characters, one sentence, ending with a period. Enforced by Python assertion in CI.
- Tools referenced in skill prose MUST be native Hermes tool names in backticks. Shell utilities are banned as headline interaction surface (grep → `search_files`, cat → `read_file`).
- `platforms:` gating must match actual POSIX-only imports.
- `author` must credit the human contributor first; "Hermes Agent" goes second.
- Section order is mandated: `# Title`, intro (2–3 sentences stating what it does AND doesn't do), `## When to Use`, `## Prerequisites`, `## How to Run`, `## Quick Reference`, `## Procedure`, `## Pitfalls`, `## Verification`.
- Length targets: ~200 lines complex, ~100 lines simple.

**Background review signal detection (`background_review.py:45–148`):**
- Skill update signals: user corrected style/tone/format/verbosity, user corrected workflow, non-trivial technique emerged, loaded skill turned out wrong.
- Preference order: (1) update currently-loaded skill, (2) update existing umbrella, (3) add support file, (4) create new class-level umbrella.
- Umbrella skill naming rule: name MUST NOT be a PR number, error string, feature codename, or 'fix-X/debug-Y' session artifact.
- "Do NOT capture" enumeration (exact list from `_SKILL_REVIEW_PROMPT`):
  - Environment-dependent failures: missing binaries, fresh-install errors, 'command not found', unconfigured credentials.
  - Negative claims about tools: 'browser tools do not work', 'X is broken'. These harden into refusals that persist after the real problem is fixed.
  - Session-specific transient errors that resolved before conversation ended.
  - One-off task narratives: 'summarize today's market', 'analyze this PR' — not a class of work warranting a skill.

**Curator lifecycle invariants (`curator.py:1–20`):**
- Only touches skills with `created_by: "agent"` provenance — bundled + hub-installed skills are off-limits.
- Never auto-deletes; max destructive action is archive. Archives go to `.archive/` and are restorable.
- Pinned skills bypass all auto-transitions.
- Default intervals: `DEFAULT_INTERVAL_HOURS = 168` (7 days), `DEFAULT_MIN_IDLE_HOURS = 2`, `DEFAULT_STALE_AFTER_DAYS = 30`, `DEFAULT_ARCHIVE_AFTER_DAYS = 90`.

**Error taxonomy (`error_classifier.py:24–64`):**
- 16 named `FailoverReason` values: auth, auth_permanent, billing, rate_limit, overloaded, server_error, timeout, context_overflow, payload_too_large, image_too_large, model_not_found, provider_policy_blocked, format_error, invalid_encrypted_content, multimodal_tool_content_unsupported, llama_cpp_grammar_pattern, thinking_signature, long_context_tier.
- Priority-ordered pipeline: provider-specific patterns > HTTP status > error code > message pattern > SSL transient > server disconnect + large session > transport type > unknown.
- `ClassifiedError` dataclass carries `retryable`, `should_compress`, `should_rotate_credential`, `should_fallback` hints.

**Dependency pinning policy (AGENTS.md:312–329):**
- PyPI: `>=floor,<next_major` for post-1.0; `<0.(current_minor + 2)` for pre-1.0.
- Git URLs: commit SHA only.
- GitHub Actions: commit SHA with comment indicating version.
- Never commit bare `>=X.Y.Z` without a ceiling.

---

## Dimension 2 — Format (identifier level)

**SKILL.md frontmatter fields:** `name`, `description`, `version`, `author`, `license`, `platforms`, `metadata.hermes.tags`, `metadata.hermes.category`, `metadata.hermes.related_skills`, `metadata.hermes.config`.

**skill-bundles/*.yaml schema:** `name` (string), `description` (string), `skills` (list of skill ids), `instruction` (optional multiline string). File stem used as fallback name.

**error_classifier module-level constants:** `_BILLING_PATTERNS`, `_RATE_LIMIT_PATTERNS`, `_USAGE_LIMIT_PATTERNS`, `_CONTEXT_OVERFLOW_PATTERNS`, `_MODEL_NOT_FOUND_PATTERNS`, `_AUTH_PATTERNS`, `_TIMEOUT_MESSAGE_PATTERNS`, `_TRANSPORT_ERROR_TYPES`, `_SERVER_DISCONNECT_PATTERNS`, `_SSL_TRANSIENT_PATTERNS` — all lowercase lists, matched against lowercased error message strings.

**COMMAND_REGISTRY entry fields:** `name` (canonical without slash), `description`, `category` (one of: Session/Configuration/Tools & Skills/Info/Exit), `aliases` (tuple), `args_hint` (string), `cli_only` (bool), `gateway_only` (bool), `gateway_config_gate` (dotpath string).

---

## Dimension 3 — Interactions (contract level)

**background_review → AIAgent fork:** Producer: parent `AIAgent` with `_cached_system_prompt` set. Consumer: `review_agent` must inherit `_cached_system_prompt`, `session_id`, `session_start`, `_memory_store`, `enabled_toolsets`. Breaking: changing any of these makes the HTTP request body non-byte-identical, busting prefix cache.

**skill_commands → skills_tool/registry:** Producer: `skills_tool.SKILLS_DIR` and `get_external_skills_dirs()`. Consumer: `_load_skill_payload` validates path is under a trusted root before calling `skill_view()`. Breaking: loading a skill from outside trusted roots silently returns None.

**COMMAND_REGISTRY → all consumers:** Producer: `hermes_cli/commands.py` defines each `CommandDef` once. Consumers: CLI `process_command()`, gateway `run.py`, gateway help, Telegram `BotCommand` menu, Slack subcommand routing, autocomplete `COMMANDS` dict, help `COMMANDS_BY_CATEGORY`. Breaking: adding a command only to `process_command()` without adding it to COMMAND_REGISTRY makes it invisible to gateway, Telegram, Slack, and help.

---

## Section 1 — Reference Summary

Hermes Agent is a production-grade, open-source agent runtime (NousResearch) built around a Python `AIAgent` class (~12k LOC). It handles multi-provider LLM inference, multi-platform messaging (Telegram, Discord, Slack), a plugin system for memory/model/context-engine backends, a skill system with YAML-defined bundles and a background curator, and a cron scheduler for automated agent tasks.

**Behavioral content:** Background review prompts with explicit signal/anti-pattern taxonomy; skill lifecycle curator invariants; error classification taxonomy with priority-ordered pipeline; iteration budget consume/refund accounting; dependency pinning policy.

**Structural content:** SKILL.md authoring standards (≤60 char description, mandatory section order, platform gating, no marketing words); COMMAND_REGISTRY single-source-of-truth pattern; slug normalization conventions.

**Interaction content:** Prefix-cache-preserving fork pattern for background review agents; trusted-root sandboxing for skill loading; COMMAND_REGISTRY → all consumers automatic derivation.

**Maturity:** Active production system with CI (17k tests), versioned releases, real usage, supply-chain audit workflows. Established May 2026 commit history. The supply-chain audit and dependency pinning policy were reinforced after a real incident (litellm compromise, Mini Shai-Hulud worm).

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `AGENTS.md:619–690` | SKILL.md description period-ending requirement | WabbleSpec CLAUDE.md doesn't require descriptions end with a period; this is cheap to enforce | Add to Gate 2 `lint_prompts` check in `quality-floor-check.py` | Medium |
| `background_review.py:96–146` | "Do NOT capture" anti-pattern list (exact 4-item enumeration) | Dream currently has no guidance on what NOT to distill to Instinct; these anti-patterns prevent persistent false constraints | Add as a `## Signal Anti-Patterns` subsection in Dream SKILL.md | High |
| `AGENTS.md:619–680` | Mandatory `## Pitfalls` section in SKILL.md structure | WabbleSpec has `## When NOT to use` but no explicit pitfalls section; pitfalls cover operational gotchas rather than trigger boundaries | Add to CLAUDE.md skill authoring conventions as a recommended (not required) section | Low-Medium |
| `AGENTS.md:613–616` | Description must state "what it does AND doesn't do" in 2-3 sentence intro | WabbleSpec skill intros are often just "what it does" — the "doesn't do" boundary is pushed to `## When NOT to use` | Add to CLAUDE.md authoring note: intro must state both dimensions | Low |
| `error_classifier.py:24–64` | `FailoverReason` taxonomy and priority-ordered pipeline pattern | WabbleSpec's wave-fix routes errors to Guard without a structured taxonomy; named error reasons would make routing explicit | Create a reference doc enumerating WabbleSpec error classes for wave-fix routing guidance | Medium |
| `AGENTS.md:312–329` | Dependency pinning policy (exact rules: `>=floor,<next_major`, SHA for git) | WabbleSpec Python scripts in `.wabblespec/engine/shared/scripts/` have no stated pinning policy | Add pinning section to CLAUDE.md or a new reference doc | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `AGENTS.md:619` | Description ≤60 char limit is calibrated for Hermes' skill-listing density | WabbleSpec module descriptions (e.g. "EMA confidence decay and gap detection...") legitimately exceed 60 chars | Adopt period-ending requirement only; skip character limit | Low |
| Model names in code (e.g. background_review: `model=agent.model`) | I6 violation if copied literally | WabbleSpec forbids vendor names in framework files | Treat as do_not_copy; use capability descriptors only | Critical |
| `AGENTS.md:619` "author credits the human contributor first" | Misfit — WabbleSpec skills are framework-authored | Not applicable to WabbleSpec's module ownership model | Skip this convention entirely | Low |
| Curator "only touches agent-created skills" concept | Concept maps poorly to WabbleSpec where all modules are framework-authored | Would require a parallel "execution-created" vs "framework-authored" distinction that doesn't exist in WabbleSpec | Study only; do not adopt the agent-created distinction | Medium |
| Background review fork pattern | Requires a running agent process; WabbleSpec sessions are single-agent | Architectural mismatch — WabbleSpec doesn't spawn background threads during active sessions | Study only | Medium |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Description period-ending requirement | Adapt | Direct Gate 2 check, no side effects | `quality-floor-check.py` | High |
| "Do NOT capture" anti-pattern list | Adapt | Dream has no signal discrimination guidance | `dream/SKILL.md` | High |
| Intro must state "does AND doesn't do" | Adapt | CLAUDE.md authoring note | `CLAUDE.md` | Medium |
| Error taxonomy pattern | Adapt | Reference doc for wave-fix routing | New reference doc | Medium |
| Dependency pinning policy | Adapt | CLAUDE.md or reference doc | `CLAUDE.md` | Low |
| `## Pitfalls` section | Adapt | CLAUDE.md recommended sections | `CLAUDE.md` | Low |
| Description ≤60 char limit | Avoid | Calibrated for Hermes context; too restrictive for WabbleSpec | — | — |
| Model names in any framework file | Avoid | I6 hard violation | — | — |
| Author/contributor credits convention | Avoid | Misfit — framework modules have no "human contributor" | — | — |
| Agent-created vs bundled skill distinction | Study Only | Interesting concept but WabbleSpec has no runtime-created modules | — | — |
| Background review fork architecture | Study Only | Architectural mismatch — WabbleSpec is single-agent | — | — |
| Gateway platform adapters | Avoid | Not relevant; no overlap with WabbleSpec use case | — | — |
| ACP adapter | Avoid | Not relevant | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 5 | Both are skill-based agent frameworks but Hermes is a runtime agent; WabbleSpec is a spec-driven SDLC framework. Partial overlap. |
| Architecture fit | 3 | Hermes: long-running Python process, multi-platform, pluggable backends. WabbleSpec: Claude Code session hooks, YAML registry, receipt-gated execution. Very different runtimes. |
| Implementation fit | 7 | The extractable patterns (description standards, anti-pattern lists, error taxonomy) are language/platform-agnostic behavioral conventions |
| Maintenance fit | 6 | Patterns are stable; the Hermes-specific infrastructure (gateway, curator state machine) would require ongoing translation effort |
| Risk level | 2 | Low risk — Phase 1 items are additive documentation and a Gate 2 check |
| Overall usefulness | 6 | Targeted patterns worth adapting; not a wholesale integration target |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning):**
- P1.1: Add description period-ending check to Gate 2 (`quality-floor-check.py`)
- P1.2: Add "do not distill" anti-pattern list to Dream SKILL.md from hermes `_SKILL_REVIEW_PROMPT` "Do NOT capture" enumeration
- P1.3: Add CLAUDE.md note: skill intro must state both "what it does AND doesn't do" in 2–3 sentences

**Phase 2 (Low-Risk Adaptation):**
- P2.1: Add `## Pitfalls` to CLAUDE.md recommended skill sections (complementing `## When NOT to use`)
- P2.2: Create `_shared/references/error-taxonomy.md` documenting WabbleSpec wave-fix error classes (adapting hermes FailoverReason taxonomy to WabbleSpec's context)

**Phase 3 (Deeper Integration — Deferred):**
- P3.1: Enforce `## When NOT to use` section in Gate 2 (CLAUDE.md claims this is enforced but `quality-floor-check.py` doesn't implement it; verify module pass rate before enabling)

**Phase 4 (Do Not Cross):**
- Any model names in framework files (I6)
- Agent-created vs bundled skill distinction (architectural mismatch)
- Background review fork pattern (architectural mismatch)
- Gateway/platform infrastructure

---

## Section 7 — Final Verdict

**Best 3 to steal/adapt:**
1. `background_review.py:96–146` — "Do NOT capture" enumeration: this is the clearest articulation of signal anti-patterns for memory/skill distillation I've seen. Dream lacks this entirely.
2. `AGENTS.md:619` — Period-ending description requirement: cheap to enforce, easy to verify, improves skill routing precision.
3. `error_classifier.py` — Priority-ordered error taxonomy: the pattern of naming error types and routing recovery actions by named class rather than inline string matching is directly applicable to WabbleSpec's wave-fix error routing.

**Worst 3 to avoid:**
1. Model names in any code path (I6 critical).
2. Description ≤60 char limit (too restrictive for WabbleSpec's more specific module descriptions).
3. Curator "agent-created" provenance distinction (architectural mismatch — WabbleSpec has no runtime-created modules).

**Classification:** `supporting` — targeted patterns worth adapting; not a wholesale adoption target.

**Recommended next action:** Proceed to Phase 2 (ref-plan) and implement P1.1 and P1.2 in Phase 3.

---

## Section 8 — Project Synthesis

Two synthesis ideas that require both hermes' logic AND WabbleSpec's specific infrastructure:

**Synthesis 1 — "Frustration = Instinct signal" heuristic**
- Reference contribution: hermes classifies user corrections (style/tone/format/workflow frustration) as FIRST-CLASS skill signals, not memory signals. Encoded in `_SKILL_REVIEW_PROMPT`: "Frustration signals like 'stop doing X', 'this is too verbose'... are FIRST-CLASS skill signals."
- Project contribution: WabbleSpec has an Instinct system (`l5/instinct`) that receives validated observations and promotes them to Synth → Blueprint → Augment. This chain exists specifically for behavioral corrections.
- Target: `.wabblespec/engine/modules/l5/dream/SKILL.md` + `l5/instinct/SKILL.md`
- Gap closed: WabbleSpec currently has no guidance routing user-frustration signals specifically to Instinct vs general memory. Adopting hermes' classification sharpens the signal routing: frustration = Instinct candidate, not just a memory drawer.

**Synthesis 2 — Priority-ordered error routing table for wave-fix**
- Reference contribution: hermes' `error_classifier.py` pipeline — 8 priority levels, named recovery actions (`retryable`, `should_compress`, `should_rotate_credential`, `should_fallback`).
- Project contribution: WabbleSpec's wave-fix skill handles stalled or failed waves, routing to rollback, retry, or escalation. Currently wave-fix uses prose-level guidance without a structured taxonomy.
- Target: `.wabblespec/engine/modules/l3/wave-fix/SKILL.md` + a new `_shared/references/wave-error-taxonomy.md`
- Gap closed: Gives wave-fix an explicit, named error type vocabulary so Guard pre-checks and Executor routing share a common language for error conditions.
