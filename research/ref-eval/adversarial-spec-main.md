# Ref-Eval: adversarial-spec-main

**Date:** 2026-05-31
**Reference path:** `C:\Vaults\references\Other Projects References\adversarial-spec-main\adversarial-spec-main`
**Slug:** adversarial-spec-main
**Evaluated by:** ref-adopt pipeline

---

## File Inventory

| Path | Purpose | Size | Key Contents | Status | Transfer Check |
|---|---|---|---|---|---|
| `skills/adversarial-spec/SKILL.md` | Primary skill definition | Large | Multi-model debate workflow, interview mode, convergence rules, preserve-intent, personas | Read | N/A — primary file |
| `skills/adversarial-spec/scripts/debate.py` | CLI orchestrator | Large | Parallel model dispatch, session management, profile loading, CLI argument parsing | Read | Behavioral: retry protocol (3x exponential), output format, flag-based modifiers |
| `skills/adversarial-spec/scripts/models.py` | Model calling + cost tracking | Large | `call_models_parallel`, `CostTracker`, `detect_agreement`, `extract_spec`, `ModelResponse` dataclass | Read | CostTracker pattern, ModelResponse schema, JSONL Codex parsing, Gemini CLI output filtering |
| `skills/adversarial-spec/scripts/prompts.py` | Prompt templates | Medium | PRESERVE_INTENT_PROMPT, FOCUS_AREAS dict (6 keys), PERSONAS dict (10 keys), SYSTEM_PROMPT_PRD, SYSTEM_PROMPT_TECH, REVIEW_PROMPT_TEMPLATE, PRESS_PROMPT_TEMPLATE | Read | All prompt text: preserve-intent taxonomy, focus criteria, persona definitions, press verification steps |
| `skills/adversarial-spec/scripts/providers.py` | Provider config + Bedrock | Large | MODEL_COSTS, BEDROCK_MODEL_MAP (25 entries), profile management, credential validation | Read | Profile persistence pattern, friendly-name→ID resolution pattern |
| `skills/adversarial-spec/scripts/session.py` | Session state + checkpointing | Small | `SessionState` dataclass, path-traversal-safe save/load, checkpoint per round | Read | Path-traversal guard (`is_relative_to`), checkpoint naming convention |
| `skills/adversarial-spec/scripts/telegram_bot.py` | Telegram notifications | Medium | Async poll-for-reply, send_long_message, setup wizard | Skimmed | Transfer check: no transferable behavioral framework. Domain-specific integration. |
| `skills/adversarial-spec/scripts/tests/test_models.py` | Model unit tests | Large | 90%+ coverage mandate, mutation-resistant assertions (explicit "Mutation:" comments), boundary checks | Read | Mutation comment convention; `is_relative_to` path guard pattern |
| `skills/adversarial-spec/scripts/tests/test_prompts.py` | Prompt unit tests | Medium | Full prompt content integrity checks, persona normalization tests | Read | Persona normalization pattern (space/underscore → hyphen) |
| `skills/adversarial-spec/scripts/tests/test_cli.py` | CLI integration tests | Small | End-to-end CLI argument tests | Skimmed | Transfer check: no transferable framework beyond what test_models.py already provides |
| `skills/adversarial-spec/scripts/tests/test_providers.py` | Provider validation tests | Small | Bedrock resolution, credential validation | Skimmed | Transfer check: Bedrock-specific, not applicable |
| `skills/adversarial-spec/scripts/tests/test_session.py` | Session state tests | Small | Path traversal safety, checkpoint creation | Skimmed | Transfer check: path-traversal guard pattern already covered by session.py read |
| `skills/adversarial-spec/scripts/tests/test_model_calls.py` | Live API call tests | Small | Real-model integration tests with env var skipping | Skimmed | Transfer check: no transferable framework |
| `skills/adversarial-spec/scripts/tests/test_telegram_bot.py` | Telegram tests | Small | Telegram-specific | Skimmed | Transfer check: domain-specific, skip |
| `.claude-plugin/plugin.json` | Plugin metadata | Small | name, version, description, keywords | Read | No transferable content |
| `.claude-plugin/marketplace.json` | Marketplace listing | Small | Marketplace registration | Skimmed | No transferable content |
| `README.md` | User documentation | Large | Quick start, feature docs, usage examples | Read | Feature documentation supplement to SKILL.md |
| `CONTRIBUTING.md` | Dev standards | Small | 90% coverage floor, Google-style docstrings, ruff+mypy | Read | 90% coverage floor with mutation comments as documentation |
| `.github/workflows/ci.yml` | CI pipeline | Small | Lint (ruff), typecheck (mypy), test (3 Python versions), manifest validation | Read | Manifest validation job pattern |
| `pyproject.toml` | Build config | Small | Python 3.10+ requirement, ruff config | Skimmed | Transfer check: no framework content |
| `.pre-commit-config.yaml` | Pre-commit hooks | Small | ruff + mypy hooks | Skimmed | Transfer check: tool-specific |
| `requirements.txt` / `requirements-dev.txt` | Dependencies | Small | litellm, pytest, ruff, mypy | Skimmed | Transfer check: litellm is the core external dependency — intentionally not adopting per I6 |

---

## Connection Map

```
SKILL.md --[invokes]--> debate.py: critique subcommand with spec stdin
debate.py --[imports]--> models.py: call_models_parallel, CostTracker, ModelResponse
debate.py --[imports]--> prompts.py: REVIEW_PROMPT_TEMPLATE, PRESS_PROMPT_TEMPLATE, get_doc_type_name
debate.py --[imports]--> providers.py: get_bedrock_config, validate_model_credentials, load_profile
debate.py --[imports]--> session.py: SessionState, save_checkpoint
models.py --[imports]--> prompts.py: FOCUS_AREAS, PRESERVE_INTENT_PROMPT, get_system_prompt
models.py --[imports]--> providers.py: CODEX_AVAILABLE, MODEL_COSTS, DEFAULT_COST
providers.py --[imports]--> prompts.py: FOCUS_AREAS, PERSONAS (for list_focus_areas/list_personas)
debate.py --[writes]--> ~/.config/adversarial-spec/sessions/<id>.json: session state (via SessionState.save)
debate.py --[writes]--> .adversarial-spec-checkpoints/<id>-round-N.md: per-round spec checkpoint
debate.py --[reads/writes]--> ~/.claude/adversarial-spec/config.json: Bedrock config (via providers.py)
```

**Key contract:** `models.py:call_single_model` consumes: system_prompt (string from get_system_prompt), user_message (formatted from REVIEW_PROMPT_TEMPLATE with spec+context+focus injected), outputs: `ModelResponse(model, response, agreed, spec, error, input_tokens, output_tokens, cost)`. Breaking `extract_spec` or `detect_agreement` breaks this contract.

---

## Section 1 — Reference Summary

**Type:** Production Claude Code plugin skill. Active CI, 90% test coverage mandate with mutation-resistant tests, real usage evidence (GitHub), Python 3.10+ typed.

**Problem it solves:** Single-model spec review misses gaps; adversarial multi-model debate forces a spec to survive challenges from multiple independent perspectives before being considered production-ready.

**Behavioral content:**
- Multi-round debate loop with convergence gate (all models + Claude must agree)
- Interview mode (8 topic areas, probing follow-up rules, assumption-challenging)
- Preserve-intent protocol (ERROR/RISK/PREFERENCE taxonomy; removal requires harm justification)
- Anti-laziness press (3-question verification when model agrees early)
- Focus modes (security/scalability/performance/ux/reliability/cost) with blocking-issue flags
- 10 professional personas with role-specific critique criteria
- PRD vs. tech-spec typed critique criteria
- Convergence meta-rule: quality over speed, skepticism of rounds 1-2

**Structural content:**
- Round output format: `--- Round N ---` / Opponent Models / Claude's Critique / Synthesis
- [SPEC]/[/SPEC] tags for revised spec extraction
- [AGREE] token for convergence detection
- [TASK]/[/TASK] export format with 5 fields + acceptance criteria list
- Profile JSON schema: models, doc_type, focus, persona, context, preserve_intent
- Session JSON schema: session_id, spec, round, doc_type, models, focus, persona, preserve_intent, history

**Interaction content:**
- `models.py:call_models_parallel` → ThreadPoolExecutor(max_workers=len(models)) → per-model `call_single_model`
- Each model gets identical inputs; responses are collected independently (no cross-contamination)
- Retry contract: 3 attempts, exponential backoff (1s, 2s, 4s)

**Maturity:** HIGH. Active CI on 3 Python versions, 90% floor, mutation-resistant test comments, pre-commit hooks.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `prompts.py:7-29` — PRESERVE_INTENT_PROMPT | ERROR/RISK/PREFERENCE taxonomy + "additions are cheap, deletions require justification" | Adversary currently challenges by domain (weaknesses/alternatives/assumptions/failures) but has no vocabulary for distinguishing "this is factually wrong" from "this is unconventional" — the three-type taxonomy adds precision | Add a `## Preserve Intent Mode` section to `adversary` SKILL.md with the taxonomy; activate when `challenger_mode: "spec-bound"` and `preserve_intent: true` passed | High |
| `SKILL.md:402-425` — Anti-Laziness Check (Press protocol) | 3-question verification when reviewer agrees too quickly: confirm read entire doc, list 3 sections reviewed, explain why it's complete, identify remaining concerns | Adversary's two-pass audit catches unverified findings but has no protocol for detecting shallow analysis that happens to produce a PASS. Press pattern covers the false-positive PASS case | Add `## Press Mode` subsection to `adversary` SKILL.md: when `strong_output_acknowledged: true` with fewer than 3 distinct challenge domains engaged, apply press verification before finalizing | High |
| `SKILL.md:210-260` — Interview mode topic 8-area framework | Prior attempts analysis ("What failed before, why?"), privacy/security stakeholder concerns, tradeoff/priorities dimension ("if we can't have everything, what gets cut first?"), "What keeps you up at night?" risk framing | WabbleSpec's interview skill covers 9 dimensions but uses abstract labels; this reference provides concrete probing sub-questions per dimension | Add `## Deep Interview Mode` subsection to `interview` SKILL.md with 3 specific additions: (1) prior-failure probing, (2) tradeoffs/priorities axis, (3) "what keeps you up at night?" risk framing | Medium |
| `SKILL.md:140-188` — PRD vs. Tech Spec critique criteria | Two typed criterion checklists with explicit quality gates (PRD: measurable success criteria, scope lists what's OUT; Tech: complete API contracts with method+path+request+response+error codes) | `specify` Step 4 checklist has generic rules; typed criteria per document kind would add precision to spec validation | Add PRD-criteria and tech-spec-criteria tables to `specify` SKILL.md Step 4 as optional typed coverage check when `target: Product` or `target: Framework` | Medium |
| `SKILL.md:569-583` — Convergence rules / quality-over-speed | "A spec that takes 7 rounds but is bulletproof is better than one that converges in 2 rounds with gaps." + skepticism of early agreement | `specify` has no explicit guidance on pressure to converge early; this principle prevents accepting a spec that passes Step 4 checkbox quickly but has blind spots | Add as a `## Pitfalls` bullet to `specify` SKILL.md: "Do not converge early. A task card that passes all Step 4 checks quickly but was written in isolation is higher risk than one that required 3 revision cycles to resolve." | Low-Medium |
| `prompts.py:112-123` — Persona definitions | 10 professional persona definitions as concise role descriptions (15-year security engineer who "thinks like an attacker"; on-call engineer paged at 3am; junior developer who flags ambiguity) | WabbleSpec has no persona rotation mechanism; these persona definitions are production-hardened and could seed a named-reviewer dimension in adversary or specify | Add persona table as a reference lookup in `adversary` SKILL.md — a caller can specify `persona: "junior-developer"` to activate ambiguity-detection mode vs. `persona: "security-engineer"` for attack-surface mode | Medium |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| All model name references in SKILL.md (lines 26-35, 313-348) | I6 violation: 30+ hardcoded model names and API key env vars | Framework files must use capability placeholders, not provider names | Do not copy SKILL.md model tables; extract only the behavioral protocols | Critical — do not copy |
| `debate.py` infrastructure dependency | `litellm` + CLI binary dependency | WabbleSpec skills are instructions, not runtime Python scripts; importing this pattern would couple to an external library | Extract prompt protocols and display formats only; no script adoption | High |
| AskUserQuestion calls (SKILL.md:313, 350) | Conflicts with prior directive against AskUserQuestion | Prior ref-adopt sessions explicitly banned this pattern | Do not adopt the model-selection AskUserQuestion pattern | High |
| `SKILL.md:400-425` — "Claude is an active participant" framing | If adopted literally, creates ambiguity about when Claude is moderating vs. challenging | WabbleSpec's adversary is already scoped to challenge-only with a role-boundary section | Adopt the press/verification protocol only; do not adopt "active participant" framing which blurs adversary vs. executor roles | Medium |
| Session persistence to `~/.config/` | Writes outside project boundary | WabbleSpec state goes to `.wabblespec/state/` per I11 | No adoption — session state model conflicts with WabbleSpec's per-task state model | Medium |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| PRESERVE_INTENT_PROMPT (prompts.py:7-29) | Adapt | High-value behavioral protocol, I6-clean, no dependencies | `adversary` SKILL.md | 1 |
| Press protocol (SKILL.md:402-425) | Adapt | Fills a gap in adversary's false-positive PASS detection | `adversary` SKILL.md | 2 |
| 8-topic interview framework sub-questions | Adapt | Enriches existing interview skill without overwriting | `interview` SKILL.md | 3 |
| PRD/Tech Spec typed criteria checklists | Adapt | Adds precision to specify's validate step | `specify` SKILL.md | 4 |
| Quality-over-speed convergence rule | Adapt | Important pitfall missing from specify | `specify` SKILL.md | 5 |
| Persona definitions (prompts.py:112-123) | Adapt | Reference table for adversary caller-specified focus | `adversary` SKILL.md | 6 |
| All model names and API key env vars | Avoid | I6 violation | — | — |
| litellm / debate.py scripts | Avoid | External binary dependency; conflicts with I10 | — | — |
| AskUserQuestion calls | Avoid | Prior directive against this pattern | — | — |
| Session persistence to ~/.config/ | Avoid | Conflicts with I11, WabbleSpec state model | — | — |
| Telegram integration | Avoid | Domain-specific external service | — | — |
| AWS Bedrock config | Avoid | I6 vendor-specific | — | — |
| Codex CLI / Gemini CLI subprocess routing | Avoid | I6 + external binary dependency | — | — |
| "Claude is active participant" framing | Study only | Blurs role boundaries in WabbleSpec context | — | — |
| [SPEC]/[AGREE]/[TASK] token protocol | Study only | Interesting convergence signaling but conflicts with WabbleSpec receipt-gate model | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 8 | Adversarial review is already a WabbleSpec module; this reference deepens it with protocols for three specific gaps |
| Architecture fit | 5 | Reference is a Python script runner; WabbleSpec is a behavioral instruction set. The scripts themselves don't fit. The behavioral protocols do. |
| Implementation fit | 8 | All Tier 1-2 items are additive prose additions to existing SKILL.md files. No new scripts required. |
| Maintenance fit | 9 | Adopting behavioral text does not create a maintenance dependency on litellm or any external library |
| Risk level | 2 | (10 = very risky) Risk is low: all items are additive and easily removable if they create confusion |
| Overall usefulness | 7 | Supporting-reference: strong behavioral protocols, but infrastructure is entirely non-transferable |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — implement now):**
1. Preserve-intent taxonomy (ERROR/RISK/PREFERENCE + "additions are cheap") → `adversary` SKILL.md
2. Press protocol (3-question verification for suspicious agreement) → `adversary` SKILL.md
3. Deep interview additions (prior-failure probing, tradeoffs axis, "what keeps you up at night") → `interview` SKILL.md

**Phase 2 (Low-Risk Adaptation — implement now):**
4. PRD/Tech Spec typed criteria → `specify` SKILL.md Step 4
5. Quality-over-speed convergence pitfall → `specify` SKILL.md Pitfalls
6. Persona reference table → `adversary` SKILL.md

**Phase 3 (Deeper Integration — future):**
- Multi-persona spec review as a named reviewer mode in `specify` clarity gate

**Phase 4 (Do Not Cross):**
- Model names, litellm, AskUserQuestion, Bedrock, session state to ~/.config/

---

## Section 7 — Final Verdict

**Classification: supporting-reference (7/10)**

**Best 3 to steal:**
1. `prompts.py:7-29` — PRESERVE_INTENT_PROMPT. The cleanest articulation of "challenge things that are wrong vs. things that are unusual" seen in any reference. The three-tier taxonomy (ERROR/RISK/PREFERENCE) is immediately applicable to adversary.
2. `SKILL.md:402-425` — Anti-Laziness Press protocol. The specific 3-question verification set for early agreement is the behavioral equivalent of WabbleSpec's two-pass audit rule, applied to the false-positive PASS case rather than the false-negative MISS case.
3. `SKILL.md:210-260` — Interview topic framework. The "What failed before?" and "What keeps you up at night?" probing questions enrich the current interview skill's abstract dimension labels with concrete angles.

**Worst 3 to avoid:**
1. All model name references (I6 — pervasive throughout SKILL.md and all Python scripts)
2. litellm/debate.py script infrastructure (external binary dependency; conflicts with WabbleSpec's instruction-based skill model)
3. AskUserQuestion adoption for model selection (prior directive; also conflicts with I6 if model names appear in options)

**Recommended next action:** Implement Phase 1+2 items directly (6 Tier 1-2 items, all additive prose changes to 3 files).

---

## Section 8 — Project Synthesis

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Preserve-intent adversary mode | Three-tier taxonomy (ERROR/RISK/PREFERENCE) with harm-justification gate for removals | Adversary's `spec-bound` challenger mode with access to the locked task card | `adversary` SKILL.md | Adversary currently challenges on all dimensions equally; preserve-intent mode prevents adversary from flagging style deviations as weaknesses when the spec makes deliberate choices |
| Breaking-change press gate | Press protocol: 4-question verification before accepting suspicious agreement | BREAKING/ADDITIVE delta classification in specify; if delta = BREAKING, extra scrutiny is warranted | `specify` SKILL.md Step 3.6 | Adversarial spec gate (Step 3.6) currently only checks if adversary runs at all; press-on-agreement adds a quality floor to what "adversary found nothing" means |
| Typed document review criteria | PRD vs. tech-spec split with explicit "no technical implementation details in PRD" rule and "every API endpoint has error codes in tech spec" rule | Specify's GWT format applies the same criteria regardless of target type | `specify` SKILL.md Step 4 | Specify validates criteria syntax but not domain-appropriate completeness; typed checklists add semantic coverage validation |

---

## Section 9 — Expansion Opportunities

**Per-skill growth scan:**

| Reference Capability | Project equivalent? | Tier 7 candidate? |
|---|---|---|
| Multi-model parallel critique | No equivalent | Yes — but requires external API calls; out of scope without a provider |
| Interview mode (8 topics + probing) | Partial: `interview` SKILL.md has 9 dimensions | No — partial match; Tier 1 enrichment |
| PRD document type generation | No: WabbleSpec produces task cards, not PRDs | Yes — new document type |
| Preserve-intent challenge protocol | No | No — Tier 1 addition to existing adversary |
| Task-to-spec pipeline (PRD → tech spec) | Partial: specify exists but no PRD stage | Yes — new workflow stage |
| Cost tracking per model call | No equivalent in WabbleSpec | No — infrastructure specific to external model calls |
| Session persistence + resume | Partial: session-state.py exists but scoped to WabbleSpec tasks | No — different scope/model |
| Export to task list ([TASK] format) | Partial: decompose produces wave plans | No — adjacent but decompose covers this |
| Convergence detection ([AGREE] token) | No | No — WabbleSpec uses receipts, not convergence tokens |
| Focus mode critique (security/scalability/etc.) | Partial: gateway-security has domain gates | No — domain gates exist; Tier 1 enrichment |
| 10-persona reviewer system | No | Yes — net-new capability |
| Telegram async feedback loop | No | No — domain-specific, low priority |
| Saved profiles for critique configs | No | No — low value without multi-model infrastructure |
| Per-round diff generation | No | No — WabbleSpec receipts serve this function |

**Expansion Opportunities:**

| Capability | Reference location | Why project lacks it | What it would unlock | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| PRD generation + review workflow | `SKILL.md:128-165`, system prompts in `prompts.py:125-161` | WabbleSpec produces task cards for developers, not business-facing PRDs for stakeholders | Would allow WabbleSpec to cover the full spec lifecycle from stakeholder intent through technical task card | Needs a new `prd` module or extension to `specify` | weeks | Yes |
| Multi-persona task card review | `prompts.py:112-123` persona definitions + SKILL.md Step 2 selection logic | WabbleSpec's specify clarity gate uses a single fresh-subagent; no named professional lenses | Sending a draft task card through "junior-developer" + "qa-engineer" + "security-engineer" personas before locking would catch ambiguity (junior), untestable criteria (QA), and attack-surface gaps (security) | Requires subagent dispatch from specify; 3-persona minimum | days | Yes |

**Gateway bundling signal:** PRD generation and multi-persona review both operate in the "specification quality" layer. They could be bundled into a `gateway-spec` module that handles both the stakeholder-facing PRD output format and the multi-persona review workflow, sharing a common quality token system. Recommended: evaluate as a single gateway rather than two separate Tier 7 expansions.

---

*Section 9 yields 2 Tier 7 items: PRD workflow and multi-persona review.*
