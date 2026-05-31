# Ref-Eval: hyperframes-main

**Date:** 2026-05-31
**Session:** tier7-expansions-20260530
**Slug:** hyperframes-main
**Reference:** `C:\Vaults\references\Extra Project References\hyperframes-main`
**Trust level:** MEDIUM (production npm package, Apache 2.0, active CI, real downloads — but domain is video rendering, not SDLC)

---

## File Inventory

| Path | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| README.md | Project overview, quick start, package table, skill table | medium | Install flow, why vs Remotion, data-attribute HTML example | Read |
| AGENTS.md | AI agent instructions | small | Build commands, key conventions, skills routing | Read |
| CLAUDE.md | Claude Code dev instructions | small | Bun-only, oxlint/oxfmt, CLI command pattern, Docker test requirement | Read |
| DESIGN.md | Brand design system | medium | Color tokens, typography, spacing, component CSS | Read |
| CONTRIBUTING.md | Contributor guide | medium | Type-safety conventions, registry structure | Read |
| package.json | Monorepo scripts | small | build, lint, format, test pipelines; bun workspaces | Read |
| skills/hyperframes/SKILL.md | Primary authoring skill | large | Discovery phase, design system gate, data attrs, HARD-GATE, output checklist | Read |
| skills/hyperframes-cli/SKILL.md | Dev-loop CLI skill | medium | Lint, inspect, preview, render flags | Read |
| skills/gsap/SKILL.md | GSAP animation skill | medium | Timeline contract, easing, performance, HF-specific rules | Read |
| scripts/lint-skills.ts | Skill content safety linter | small | Detects dangerous inline backtick patterns that break Claude Code | Read |
| packages/ (7 dirs) | Core, CLI, engine, producer, player, studio, shader-transitions | large | Not read — TypeScript source, not applicable to WabbleSpec | Skipped: product source code, out of scope |
| registry/ | 50+ installable blocks and components | large | Not read — HTML composition snippets | Skipped: out of scope |
| docs/ | Mintlify docs site | large | Not read — user-facing docs | Skipped: out of scope |
| skills/ (9 more) | animejs, css-animations, gsap refs, lottie, tailwind, three, waapi, website-to-hyperframes, remotion-to-hyperframes | medium | Not read — all video domain-specific | Skipped: out of scope |

**Connection map:**
- `AGENTS.md` --[routes to]--> `skills/hyperframes/SKILL.md`: agents use skills as source of truth for composition authoring
- `skills/hyperframes/SKILL.md` --[loads on demand]--> `skills/hyperframes/references/*.md`: reference routing to sub-docs
- `CLAUDE.md` --[instructs]--> `packages/cli/src/commands/`: CLI extension pattern for agent-driven code contributions
- `scripts/lint-skills.ts` --[validates]--> `skills/**/SKILL.md`: safety check run in CI and pre-commit
- `package.json` --[runs]--> `scripts/lint-skills.ts`: via `"lint": "oxlint . && tsx scripts/lint-skills.ts"`

---

## Section 1 — Reference Summary

**Type:** Production framework (published npm package, Apache 2.0, active CI, conventional commits). Built by HeyGen. AI-first: the README leads with the agent install path.

**Domain:** HTML-based video rendering. Write HTML with `data-*` attributes, render to MP4. The framework handles headless Chrome capture, FFmpeg encoding, and audio mixing. Domain is video production and animation — completely orthogonal to WabbleSpec's SDLC domain.

**Behavioral content:** Sophisticated composition authoring rules (determinism requirements, timeline contract, scene transition laws, GSAP constraints). Discovery/planning phase before writing. Canonical source-of-truth-first discipline (read `design.md` before any color or font decision). Hard-gated verification at each output stage. Fast/slow checklist split: fast checks block, slow checks run in background.

**Structural content:** 12+ skill files, each scoped to one capability, with explicit "not covered here → see other skill" routing. On-demand sub-reference system: skill body lists secondary references as links loaded only when needed. `<HARD-GATE>` blocks mark non-negotiable verification checkpoints inline. Skill descriptions trigger-condition-only (no workflow content).

**Interaction content:** Skills consume a project-level `design.md` canonical source. CLI tools produce artifacts consumed by later pipeline steps. `lint-skills.ts` validates skill content for Claude Code-specific dangerous patterns — runs as part of the standard lint pipeline.

**Maturity:** High. Active npm downloads, CI enforced, Docker golden baselines, conventional commits, lefthook pre-commit hooks, knip dead-code detection. Skill files have explicit "do not do" lists and cross-references.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `scripts/lint-skills.ts` | INLINE_DANGER check: backtick spans containing `!` or `>word` cause Claude Code load failures | WabbleSpec currently has 6 SKILL.md files with backtick-`!` violations in prose; these may silently break skill loading | Add `lint_prompts.INLINE_DANGER` check to `quality-floor-check.py` that strips fenced blocks then scans inline backtick spans for `!` and `>word` | **High** |
| `skills/hyperframes/SKILL.md` (HARD-GATE block) | `<HARD-GATE>` annotation for non-negotiable inline checkpoints | Skill bodies have gates (e.g. "verify design system loaded before writing HTML") but no standardized marker; readers miss them | Add `<HARD-GATE>` as a recognized optional pattern to CLAUDE.md skill authoring conventions; mark it as a non-negotiable inline verification point | **Medium** |
| `skills/hyperframes/SKILL.md` (Output Checklist) | Fast (blocking) / Slow (background) output verification split | WabbleSpec executor/verifier skills list checks without declaring which are blocking vs. parallelizable; agents may serialize everything | Document the Fast/Slow split convention in CLAUDE.md as an optional pattern for output checklists in skills that do both blocking and async verification | **Low** |
| `scripts/lint-skills.ts` (fenced-block stripping) | Strip fenced code blocks before content analysis | quality-floor-check.py's lint_prompts checks could flag content inside fenced blocks that is valid (e.g., shell examples with `!` are fine inside ` ``` ` blocks) | Apply fenced-block stripping before running INLINE_DANGER check | **High** (prerequisite to Tier 1a) |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| All product source | Domain knowledge adoption | Video rendering logic (GSAP, HTML compositions, Frame Adapters) has zero applicability to WabbleSpec | Do not read product source; treat as out of scope | None if excluded |
| `AGENTS.md` key conventions | Adopting bun/oxlint/oxfmt CI stack | These are JavaScript-ecosystem tools; WabbleSpec uses Python | Do not adopt; inspiration-only for CI hook patterns | Low |
| `skills/hyperframes/SKILL.md` discovery phase | Agent questioning pattern before every task | WabbleSpec's guard/specify already handle intent clarification; adding a second discovery layer is redundant | Note as behavioral pattern but do not wire into existing skills | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| `scripts/lint-skills.ts` INLINE_DANGER patterns | **Adapt** | Real gap in WabbleSpec; 6+ violations confirmed | `quality-floor-check.py` | P1 |
| Fenced-block stripping algorithm | **Adapt** (prerequisite) | Required for INLINE_DANGER check accuracy | `quality-floor-check.py` | P1 |
| `<HARD-GATE>` annotation convention | **Adapt** | Useful standardized marker for inline skill gates | `CLAUDE.md` skill authoring section | P2 |
| Fast/Slow checklist split | **Study Only** | Useful pattern but WabbleSpec doesn't have a standard output checklist format yet | Future CLAUDE.md addition | P3 |
| All video/animation domain content | **Avoid** | Domain-specific, zero applicability | — | — |
| GSAP, HTML composition rules | **Avoid** | Product-domain knowledge | — | — |
| bun/oxlint/oxfmt CI stack | **Avoid** | JavaScript ecosystem; WabbleSpec is Python | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 4 | AI-agent-first philosophy matches WabbleSpec's agent-driven design; domains don't overlap |
| Architecture fit | 2 | JavaScript monorepo vs Python CLI framework — incompatible architectures |
| Implementation fit | 5 | The lint-skills.ts logic is a small Python port; `<HARD-GATE>` is just a CLAUDE.md addition |
| Maintenance fit | 7 | Adding a check to quality-floor-check.py is low maintenance; convention additions to CLAUDE.md are stable |
| Risk level | 2 | Very low — additive only, no breaking changes |
| Overall usefulness | 3 | Inspiration-only. One concrete Tier 1 check worth implementing; the rest is design philosophy that WabbleSpec already embodies. |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe, implement now):**
- Port `scripts/lint-skills.ts` INLINE_DANGER detection to `quality-floor-check.py` as `lint_prompts.INLINE_DANGER`
- Add `<HARD-GATE>` convention note to CLAUDE.md

**Phase 2 (Low-risk, no dependency):**
- Document Fast/Slow checklist split in CLAUDE.md as an optional skill convention

**Phase 3 (Deeper — do not start):**
- None. Domain divergence prevents deeper integration.

**Phase 4 (Do Not Cross):**
- All product-domain content (GSAP, HTML compositions, video rendering pipeline)
- All JavaScript/TypeScript tooling adoption

---

## Section 7 — Final Verdict

**Overall classification:** inspiration-only (3/10)

**Best 3 to adapt:**
1. `scripts/lint-skills.ts` lines 28-43 — INLINE_DANGER regex patterns. Real gap, real violations confirmed (6 files). Port to Python.
2. `skills/hyperframes/SKILL.md` HARD-GATE block — standardized inline gate marker. Adds a missing convention.
3. Fenced-block stripping (lines 60-66 of lint-skills.ts) — prerequisite for accurate lint; prevents false positives in code examples.

**Worst 3 to avoid:**
1. All TypeScript/JavaScript product source — wrong language, wrong domain.
2. GSAP/animation/video knowledge — zero applicability.
3. bun/oxlint/oxfmt CI tooling — Python project, different ecosystem.

**Recommended next action:** Implement Phase 1 items (INLINE_DANGER check + HARD-GATE convention). Both are additive and low-risk.

---

## Section 8 — Project Synthesis

Novel patterns requiring both this reference's approaches AND WabbleSpec's existing capabilities:

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Skill safety CI gate | `lint-skills.ts` INLINE_DANGER regex (fenced-strip + inline scan) | `quality-floor-check.py` Gate 2 lint_prompts infrastructure | `quality-floor-check.py` | 6 confirmed violations would be caught at commit time instead of discovered when skills fail to load |

One synthesis idea. The reference's concrete pattern (safety lint for Claude Code) maps directly onto WabbleSpec's existing quality floor infrastructure. The combination produces a new, actionable gate.

---

## Section 9 — Expansion Opportunities

The reference adds one net-new capability WabbleSpec currently lacks: **a skill content safety gate enforced in CI**.

| Capability | Reference location | Why the project lacks it | What it unlocks | Dependencies | Effort | Tier 7? |
|---|---|---|---|---|---|---|
| Skill content safety lint (Claude Code-specific) | `scripts/lint-skills.ts` | quality-floor-check.py checks structure and coverage but not Claude Code's bash permission scanner patterns | Prevents silent skill load failures in Claude Code sessions | Python re module (stdlib) | hours | No — implement in Phase 1 |

One expansion opportunity. It is small enough for Phase 1 (hours, not days). No separate Tier 7 session needed.
