# Ref-Plan: claude-code-security-review-main

**Date:** 2026-05-31  
**Session:** tier7-expansions-20260530  
**Based on:** `research/ref-eval/claude-code-security-review-main.md`

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| C1 | 17-item hard exclusion list | Behavioral | High | High | Low |
| C2 | 12-item precedents list | Behavioral | High | High | Low |
| C3 | `exploit_scenario` as required finding field | Format | Medium | High | Low |
| C4 | Confidence tiers 0.7/0.8/0.9 for findings | Behavioral | Medium | High | Low |
| C5 | Parallel sub-task false-positive filter pattern | Behavioral | Medium | High | Low |
| C6 | 3-phase security review methodology | Behavioral | Medium | Medium | Low |
| C7 | 3-section filtering override format (docs) | Format | Low | Low | Low |

---

## Exclusion List

| Item | Excluded because |
|---|---|
| constants.py model names | I6 — hardcoded model names banned in framework files |
| action.yml / github_action_audit.py / scripts/ CI bundle | Not portable to WabbleSpec hook/skill model; prompt injection not hardened (README line 44) |
| Per-finding Claude API call architecture | N API calls per run — not integrated into WabbleSpec pipeline |
| C7 (3-section filtering format) | Risk=Low, Project fit=Low — worth studying but not implementing in this pass |

---

## Scored and Ranked

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Score | Tier |
|---|---|---|
| C1 | (3×2)+3-1 = 8 | Tier 1 |
| C2 | (3×2)+3-1 = 8 | Tier 1 |
| C3 | (2×2)+3-1 = 6 | Tier 1 |
| C4 | (2×2)+3-1 = 6 | Tier 1 |
| C5 | (2×2)+3-1 = 6 | Tier 1 |
| C6 | (2×2)+2-1 = 5 | Tier 1 |

---

## Tier Assignments

### Tier 1 — Behavioral additions (additive to existing files, no new files)

**[T1-1] 17-item hard exclusion list + 12-item precedents**
- What: Add `## False-Positive Filtering` section with the 17-item hard exclusion list and 12-item precedents table to gateway-security
- Where: `.claude/skills/gateway-security/SKILL.md`
- How: Append a `## False-Positive Filtering` section after the `## Reference Routing` section. The section contains two sub-sections: `### Hard Exclusions (17 items)` with the numbered list verbatim, and `### Precedents` with the 12 numbered items verbatim. Do not paraphrase — quote from drawer `security-hard-exclusion-rules.json` and `security-precedents.json`.
- Literal values: Exact items from `.wabblespec/state/memory/wings/references/rooms/claude-code-security-review-main/security-hard-exclusion-rules.json` (hard_exclusion_list_17_items array) and `security-precedents.json` (precedents_12_items array)
- Gate: `## False-Positive Filtering` section exists in gateway-security SKILL.md with both sub-sections present and item counts correct (17 and 12)
- Reference location: `security-review.md` lines 139-169; drawers `security-hard-exclusion-rules.json` + `security-precedents.json`
- Sync: Must also apply to `.wabblespec/engine/modules/l4/security/SKILL.md`

**[T1-2] `exploit_scenario` as required finding field in adversary output schema**
- What: Add `exploit_scenario` as a required field in the adversary receipt's `counter_analysis` output
- Where: `.claude/skills/adversary/SKILL.md`
- How: In the Output contract section, find the `counter_analysis` field definition. Add `"exploit_scenario": "string — concrete attack path proving exploitability for each HIGH/CRITICAL finding"` to the schema. Also add a prose rule: "Each HIGH or CRITICAL finding in `counter_analysis.weaknesses` must include an `exploit_scenario` line showing a concrete, step-by-step attack path. A finding without a concrete path is `? INFERRED` and must not appear in final output per the two-pass audit rule."
- Literal values: Field name `exploit_scenario`; description "concrete attack path proving exploitability for each HIGH/CRITICAL finding"
- Gate: `exploit_scenario` appears in the counter_analysis schema in adversary SKILL.md; prose rule present stating the field is required for HIGH/CRITICAL findings
- Reference location: `prompts.py` lines 128-149; drawer `exploit-scenario-and-parallel-filter.json`
- Sync: Must also apply to `.wabblespec/engine/modules/l2/adversary/SKILL.md`

**[T1-3] Confidence scoring tiers (0.7/0.8-0.9/0.9-1.0) in adversary Claim Confidence Protocol**
- What: Add a confidence tier table to the Claim Confidence Protocol section in adversary, extending the existing `? INFERRED / ✓ VERIFIED / ✗ UNCERTAIN` markers with numeric confidence thresholds for what gets reported
- Where: `.claude/skills/adversary/SKILL.md`
- How: In the `### Claim Confidence Protocol` section, after the two-pass audit rule, add a `### Reporting Confidence Thresholds` table:

  | Confidence | Threshold | Action |
  |---|---|---|
  | 0.9–1.0 | Certain | Include — exploit path identified and traceable |
  | 0.8–0.9 | Clear | Include — known exploitation method exists |
  | 0.7–0.8 | Suspicious | Include only if conditions are specific and named |
  | Below 0.7 | Speculative | Do not report — mark ✗ UNCERTAIN and drop |

- Literal values: Exact thresholds 0.7, 0.8, 0.9, 1.0; exact labels "Certain", "Clear", "Suspicious", "Speculative"; rule "Below 0.7: Do not report"
- Gate: Table present in adversary SKILL.md with all four rows; 0.7 threshold explicitly named as the non-report boundary
- Reference location: `security-review.md` lines 124-130; drawer `exploit-scenario-and-parallel-filter.json`
- Sync: Must also apply to `.wabblespec/engine/modules/l2/adversary/SKILL.md`

**[T1-4] Parallel sub-task filter pattern in adversary for multi-finding security mode**
- What: Add a `## Multi-Finding Security Audit Mode` section to adversary that describes the parallel sub-task dispatch pattern
- Where: `.claude/skills/adversary/SKILL.md`
- How: Add a new section `## Multi-Finding Security Audit Mode` before `## Role boundary — Adversary stops here`. Content:

  "When adversary is invoked on a security audit with 3 or more candidate findings, use the parallel sub-task dispatch pattern to avoid anchoring across findings:

  1. Each finding is evaluated by a separate sub-task with no knowledge of how other findings were assessed
  2. Each sub-task independently applies the hard exclusion list and precedents from gateway-security (if active)
  3. Any finding where the sub-task returns confidence below 0.7 is dropped before DREAD scoring
  4. Surviving findings proceed to full DREAD scoring and dual-perspective requirement in the normal flow

  This preserves the anchoring-prevention invariant across findings: a false positive in finding #1 cannot bias the severity assessment of finding #3."

- Literal values: "3 or more candidate findings" threshold; "confidence below 0.7 is dropped"; reference to anchoring-prevention invariant
- Gate: `## Multi-Finding Security Audit Mode` section present in adversary SKILL.md with the four-step dispatch pattern
- Reference location: `security-review.md` lines 185-189; drawer `exploit-scenario-and-parallel-filter.json`
- Sync: Must also apply to `.wabblespec/engine/modules/l2/adversary/SKILL.md`

**[T1-5] 3-phase security review methodology in gateway-security Phase B**
- What: Add a structured 3-phase methodology to gateway-security's Phase B (pre-Executor verdict) step list
- Where: `.claude/skills/gateway-security/SKILL.md`
- How: In the `### Phase B (pre-Executor — verdict)` section, after step 1 ("Load threat-model.md"), add:

  "Security review follows this 3-phase sequence before producing the PASS/FLAG/BLOCK verdict:

  - **Phase 1 — Context Research**: Identify existing security frameworks and libraries in use; examine established secure coding patterns; understand the project's security model and trust boundaries
  - **Phase 2 — Comparative Analysis**: Compare code changes against existing secure patterns; identify deviations from established secure practices; flag code that introduces new attack surfaces
  - **Phase 3 — Vulnerability Assessment**: Trace data flow from user inputs to sensitive operations; look for privilege boundaries crossed unsafely; identify injection points and unsafe deserialization"

- Literal values: Phase 1/2/3 names and their bullet content (verbatim from `security-review.md` lines 89-102)
- Gate: 3-phase structure present in gateway-security SKILL.md Phase B section
- Reference location: `security-review.md` lines 89-102
- Sync: Must also apply to `.wabblespec/engine/modules/l4/security/SKILL.md`

---

## Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| `DEFAULT_CLAUDE_MODEL = 'claude-opus-4-1-20250805'` (constants.py line 8) | I6 — model names banned in framework files |
| `model="claude-3-5-haiku-20241022"` (claude_api_client.py line 68) | I6 — model names banned in framework files |
| GitHub Actions CI bundle (action.yml, github_action_audit.py, scripts/) | Not portable; prompt injection not hardened (README line 44) |

---

## Tier 6 — Synthesis Items

**[T6-1] Confidence-gated adversarial escalation for security findings**
- What: Add a `## Security Audit Mode` section to adversary that applies the confidence tiers at the dispatch point, gating which findings proceed to full DREAD scoring
- Reference contribution: 0.7/0.8/0.9 confidence tiers with named meanings
- Project contribution: Adversary's existing DREAD scoring and dual-perspective requirement
- Target: `.claude/skills/adversary/SKILL.md`
- Note: T1-3 and T1-4 are the implementation steps for this synthesis; T6-1 is the full pattern combining them. Mark as Deferred pending T1-3 and T1-4 validation.
- Gap closed: Currently all adversary findings receive full DREAD treatment regardless of evidence quality

**[T6-2] Guard OPSEC noise × security false-positive precedents dual-axis filter**
- What: Add `security_precedents` array to guard/skill-rules.json that Guard checks before classifying a tool call as LOUD
- Reference contribution: 12 precedents (env vars trusted, UUIDs unguessable, client-side auth not required)
- Project contribution: Guard's existing OPSEC noise taxonomy (QUIET/MODERATE/LOUD from pentest reference)
- Target: `.claude/skills/guard/skill-rules.json`
- Status: Deferred — requires adversarial review of the interaction between OPSEC noise and false-positive precedents before implementing

---

## Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| PR security eval harness | `claudecode/evals/eval_engine.py` lines 56-465, `evals/run_eval.py` | WabbleSpec has skill-tdd and benchmark-loop but no PR-specific security eval that checks out real GitHub PRs via git worktree | Regression testing of gateway-security rule changes against real PR history; validates hard exclusion rule additions don't introduce false negatives | GitHub CLI (gh), git worktree, ANTHROPIC_API_KEY, GITHUB_TOKEN | weeks | "Build a PR security eval harness at `.wabblespec/engine/shared/scripts/pr-security-eval.py` that clones a GitHub repo, checks out a PR via git worktree, runs gateway-security analysis, and writes an EvalResult JSON to `.wabblespec/state/receipts/`; ref: `claudecode/evals/eval_engine.py` lines 56-465" |

---

## Priority Implementation Order

| Order | ID | Item | Target | Why first |
|---|---|---|---|---|
| 1 | T1-1 | Hard exclusion list + precedents | gateway-security SKILL.md | Closes biggest gap: gateway-security has no false-positive filtering vocabulary at all |
| 2 | T1-2 | exploit_scenario field | adversary SKILL.md | Requires no dependency; makes every adversary finding falsifiable |
| 3 | T1-3 | Confidence tiers | adversary SKILL.md | Extends existing < 0.7 trigger; additive only |
| 4 | T1-4 | Parallel sub-task pattern | adversary SKILL.md | Depends on T1-3 (confidence tiers must be defined before dispatch logic references them) |
| 5 | T1-5 | 3-phase methodology | gateway-security SKILL.md | Additive to Phase B; no dependency on T1-1 through T1-4 |

**Sequencing constraints:**
- T1-4 must follow T1-3 (parallel dispatch references the 0.7 threshold defined in T1-3)
- T1-1 and T1-2 are independent and can run in parallel
- T1-5 is independent of all other items

---

## Execution Notes

- All items are additive (no deletions, no renames)
- All items require sync to engine modules — check `.wabblespec/engine/modules/` for matching SKILL.md files before and after each `.claude/skills/` edit
- Items T1-2 through T1-4 all target `.claude/skills/adversary/SKILL.md` — apply in order (T1-2, T1-3, T1-4) without interleaving reads of other files to avoid stale-read errors
- Literal values for T1-1 come from the drawer JSON files, not from re-reading the reference (drawers are FRESH)
