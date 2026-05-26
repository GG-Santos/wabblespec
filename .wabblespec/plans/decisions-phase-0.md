# Phase 0 — Locked Decisions

**Date:** 2026-05-23  
**Status:** LOCKED — no module is built before this document is confirmed  
**Parent plan:** STANDALONE-INTEGRATION-PLAN.md  

This document locks three things:
1. All architectural decisions with rationale
2. Receipt extension fields for all 26 new modules
3. Exact surgery diffs for Reviewer and Recipe (text-level changes, no interpretation needed)

---

## Part A — Architectural decisions

### A1. Layer placements — confirmed

All placements from STANDALONE-INTEGRATION-PLAN.md §1.1 stand. No amendments.

One clarification: **Audit** lands at L2 (not L1) because it consumes Guard logs and its authority must be co-equal to Guard. An L1 module cannot authoritatively audit an L2 module's output. L2-to-L2 is the correct peer relationship.

### A2. Adversary + Grader extraction contract

**What moves out of Reviewer:**
- The full Adversary analysis spec (Weaknesses / Missed alternatives / Unstated assumptions / Failure scenarios)
- The anchoring-prevention rule (receive output only, no context)
- The Grader scoring rubric (0.0–1.0 scale, ACCEPT/REVISE/ESCALATE thresholds)
- The revision guidance quality rule (specific and actionable)
- The anti-inflation rule

**What stays in Reviewer:**
- Budget gate check (confidence < 0.7, impact HIGH, explicit request)
- REVISE loop management (max 3 cycles, structured findings passed back)
- Receipt aggregation (Reviewer receipt links to adversary + grader receipts)
- Prompt-injection detection in reviewed artifacts

**Adversary invocation protocol (used by all callers, not just Reviewer):**

```
Input:  artifact_to_challenge (string or file path)
        challenger_mode: "open" | "spec-bound"
          open = no ground truth; challenge on own merits
          spec-bound = challenge against spec_artifact (required if spec-bound)
        spec_artifact (path — required when challenger_mode = spec-bound)
Output: adversary-receipt.json
        counter_analysis (embedded in receipt as structured object)
```

**Grader invocation protocol:**

```
Input:  primary_output (artifact or decision)
        adversary_counter_analysis (from Adversary receipt)
        spec_artifact (path — ground truth)
Output: grader-receipt.json
        verdict: ACCEPT | REVISE | ESCALATE
        score: 0.0–1.0
        revision_guidance (required if REVISE)
        escalation_reason (required if ESCALATE)
```

**Reviewer after extraction:**

Reviewer becomes a coordinator. It owns:
- The budget gate (decides whether to invoke Adversary + Grader at all)
- The REVISE cycle (invokes Adversary + Grader again on revised output)
- The escalation cap (forces ESCALATE at cycle 3)
- The aggregate receipt (references both sub-receipts)

Reviewer does NOT embed any evaluation logic. All evaluation is in Adversary and Grader.

**External interface locked (unchanged after surgery):**

Reviewer receipt fields that must not change: `triggered`, `trigger_condition`, `revise_cycles`, `verdict`, `grader_score`, `escalated`, `escalation_reason`, `findings`, `finding_summary`.

Two new fields added (additive): `adversary_receipt_path` (string), `grader_receipt_path` (string).

### A3. Enhance + Sharpen trigger placement

**Decision: Recipe triggers them, not ScopeFrame.**

Rationale:
- Recipe already makes a quality judgment (confidence ≥ 0.8). Input quality is a parallel judgment — same information, same moment.
- ScopeFrame expects clear input. Pushing vague/broad input to ScopeFrame produces bad scope artifacts that pollute the whole downstream chain.
- Detecting input quality at Recipe costs zero extra tool calls — it is a classification step added to the same scan Recipe already runs.

**Detection rules (locked):**

`input_vague = true` when ALL of the following are absent from the opening user message:
- A named artifact (file, module, component, service, endpoint, test)
- A measurable outcome (number, threshold, user-observable behavior)
- A named constraint (must not, cannot, by date, under N tokens, backwards-compatible)
- A specific scope boundary (only this file, just the login flow, excluding mobile)

`input_broad = true` when:
- Two or more interpretations of the user intent are plausible at ≥ 0.5 confidence each, AND
- No priority signal disambiguates them (user did not rank, quantify, or constrain to one)

These are independent. A single opening message can trigger both, one, or neither.

**Recipe routing after detection:**

```
If input_vague AND NOT input_broad → Enhance → ScopeFrame
If input_broad AND NOT input_vague → Sharpen → ScopeFrame
If input_vague AND input_broad    → Enhance → Sharpen → ScopeFrame
If neither                        → ScopeFrame (no change)
```

Recipe does NOT wait for Enhance/Sharpen to complete before writing recipe.json. Recipe writes recipe.json first (target + complexity locked), then routes. The input_quality fields are written to recipe.json as well.

### A4. Plan placement in pipeline

**Plan is L1, optional for Low complexity, mandatory for Medium+.**

Insertion point: after Propose, before Decompose.

```
Specify → Propose → [Plan] → Decompose
```

Plan is not mandatory for Low complexity tasks — they can go Specify → Decompose directly. Plan triggers when:
- Complexity is Medium or High (Recipe declares this)
- Autopilot L2+ autonomy level
- Explicit `/plan` command

Plan consumes Propose's output (options + recommendation). Plan produces a plan artifact with: chosen approach, expert perspectives applied, architectural rationale, open risks, and a go/no-go recommendation before Decompose.

**Adversary gates Plan (budget-gated, spec bound to task card):**

After Plan produces its artifact, if complexity is High or the plan touches security/infrastructure/irreversible scope: Adversary challenges it, Grader scores it. Max 3 REVISE cycles. On ESCALATE: surface to human before Decompose.

### A5. Nexus graph schema interoperability

**Decision: Nexus, Shift, and Memory share one graph interchange format.**

Format is a superset of `drawer.schema.json`. A new `_shared/schemas/graph-node.schema.json` and `_shared/schemas/graph-edge.schema.json` define the interchange. These are created in Phase 3 alongside Nexus.

Rules:
- Every entity in Nexus's graph is backed by one or more Memory drawers (drawer_id reference mandatory on graph nodes)
- EntityGraph's output format is an input to Nexus's graph-builder.py — EntityGraph must already produce compatible entity/relationship records
- Shift reads Nexus graph to identify downstream consumers when computing compatibility

This dependency means Nexus must be built after EntityGraph is verified to produce compatible output. Check EntityGraph's script (modules/l5/entity-graph/scripts/entity-graph.py) before building Nexus.

### A6. Shared infrastructure — `_shared/infrastructure/` vs `_shared/references/`

Boundary rule (locked):

- `_shared/infrastructure/` — how the framework runs. Files that configure or govern framework behavior. These are read by modules to know what to do, not to know about a domain.
  - economy-principles.md — token economy rules
  - guard-policy.md — default risk tier configuration
  - gateway-pattern.md — routing architecture documentation
  - version-tracking.md — VERSION file ownership and semver protocol
  - completion-promise.md — loop termination and error recovery patterns

- `_shared/references/` — what modules know about domains. These provide knowledge that informs module decisions, not framework configuration.
  - compression-discipline.md — how to compress output
  - model-routing.md — how to route by task shape and context type
  - adversarial-patterns.md — patterns for challenge analysis
  - ears-syntax.md — requirement syntax
  - etc.

Rule: if removing the file would change how the framework routes or enforces behavior → infrastructure. If removing it would only reduce domain knowledge → reference.

### A7. framework.yaml — consumer declaration rule

No `_shared/references/` or `_shared/infrastructure/` file is created without at least one named consumer in framework.yaml. Undeclared shared files are orphans and become dead weight.

Rule: the consumers list must name module IDs from framework.yaml (e.g., `[specify, executor, guard]`), not generic descriptions.

### A8. Receipt schema extension pattern

Extension fields go in a sidecar schema file in the module's `schemas/` directory, named `<module>-receipt.schema.json`. The base schema is always extended via JSON Schema `allOf` or an `extends` convention documented inline.

Pattern for all new modules:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "<Module> Receipt Extension",
  "description": "Extends receipt.base.schema.json. Module-specific fields.",
  "allOf": [
    { "$ref": "../../../_shared/schemas/receipt.base.schema.json" }
  ],
  "properties": {
    ... module-specific fields ...
  }
}
```

---

## Part B — Receipt extension fields (all 26 modules)

Fields listed below are the extension fields only. Base schema fields (module, layer, phase, wave, timestamp, checks_run, checks_passed, evidence, status, inputs, outputs, not_tested, confidence, failure_reason, revise_cycles) are always present and not repeated here.

---

### B1. Adversary (L2)

```json
{
  "challenger_mode": "open | spec-bound",
  "spec_artifact_path": "string — null if challenger_mode = open",
  "challenges_produced": "integer — number of challenge points raised",
  "challenge_domains_covered": {
    "weaknesses": "boolean",
    "missed_alternatives": "boolean",
    "unstated_assumptions": "boolean",
    "failure_scenarios": "boolean"
  },
  "anchoring_prevention_applied": "boolean — must be true; false = invariant violation",
  "strong_output_acknowledged": "boolean — true if Adversary found no real weaknesses",
  "counter_analysis": {
    "weaknesses": ["array of strings"],
    "missed_alternatives": ["array of strings"],
    "unstated_assumptions": ["array of strings"],
    "failure_scenarios": ["array of strings"]
  }
}
```

### B2. Grader (L2)

```json
{
  "verdict": "ACCEPT | REVISE | ESCALATE",
  "score": "number 0.0–1.0",
  "score_rationale": "string — one sentence explaining the score",
  "spec_artifact_path": "string — ground truth used",
  "adversary_receipt_path": "string — input adversary receipt",
  "revision_guidance": "string — required when verdict = REVISE; null otherwise",
  "escalation_reason": "string — required when verdict = ESCALATE; null otherwise",
  "adversary_concerns_assessed": "integer — how many Adversary points were evaluated",
  "adversary_concerns_within_scope": "integer — how many were within current spec scope"
}
```

### B3. Enhance (L1)

```json
{
  "dimensions_present": ["array — which of 9 dimensions were present in original input"],
  "dimensions_absent": ["array — which were missing"],
  "dimensions_derived": ["array — which were inferred without explicit user statement"],
  "critical_dimensions_resolved": "boolean — Task + Target + Format all present or derived",
  "questions_asked": "integer — 0 to 3",
  "questions_answered": "integer",
  "vague_resolved": "boolean — input is no longer vague after Enhance",
  "enhanced_input_path": ".wabblespec/enhance/enhanced-<timestamp>.md"
}
```

### B4. Sharpen (L1)

```json
{
  "interpretations_produced": "integer — 1 to 3",
  "interpretations": [
    {
      "rank": "integer",
      "description": "string",
      "confidence": "number 0.0–1.0"
    }
  ],
  "interpretation_chosen": "string — description of selected interpretation",
  "user_confirmed": "boolean — true if user was asked and confirmed; false if auto-selected",
  "broad_resolved": "boolean — input is no longer broad after Sharpen"
}
```

### B5. Brainstorm (L1)

```json
{
  "options_generated": "integer",
  "convergence_trigger": "volume_cap | diminishing_returns | user_signal | time_budget",
  "options": ["array of option summary strings — one per option"],
  "evaluation_deferred": "boolean — true = no evaluation during generation (correct); false = invariant violation",
  "top_options_path": ".wabblespec/brainstorm/options-<timestamp>.md"
}
```

### B6. Plan (L1)

```json
{
  "plan_options_count": "integer",
  "chosen_approach_summary": "string — one sentence",
  "expert_perspectives_applied": ["array — e.g. security, architecture, operability, performance"],
  "adversary_triggered": "boolean",
  "grader_score": "number 0.0–1.0 — null if adversary not triggered",
  "grader_verdict": "ACCEPT | REVISE | ESCALATE | null",
  "open_risks": ["array of risk strings"],
  "go_no_go": "GO | NO_GO | CONDITIONAL",
  "plan_artifact_path": ".wabblespec/plans/plan-<timestamp>.md",
  "human_escalation_required": "boolean"
}
```

### B7. Analyze (L1)

```json
{
  "method_used": "5-whys | fishbone | fault-tree | timeline",
  "root_cause_identified": "boolean",
  "root_cause_confidence": "number 0.0–1.0",
  "root_cause_summary": "string",
  "contributing_factors_count": "integer",
  "evidence_sources": ["array of paths or drawer IDs consulted"],
  "rca_report_path": ".wabblespec/analysis/rca-<timestamp>.md",
  "nexus_queried": "boolean — true if Nexus was called for cross-module context"
}
```

### B8. Perf (L1)

```json
{
  "baseline_measured": "boolean — must be true before any optimization claim",
  "platform_budget_applied": "string — which platform budget was used",
  "optimization_opportunities": "integer",
  "estimated_improvement_pct": "number — null if unmeasurable",
  "profiling_method": "string — tool or technique used",
  "perf_baseline_path": ".wabblespec/perf/baseline-<timestamp>.json",
  "regressions_detected": "integer — 0 is clean"
}
```

### B9. Deps (L1)

```json
{
  "deps_scanned": "integer — total dependencies found",
  "risk_summary": {
    "critical": "integer",
    "high": "integer",
    "medium": "integer",
    "low": "integer",
    "unknown": "integer"
  },
  "outdated_count": "integer",
  "license_violations": "integer",
  "sbom_path": ".wabblespec/deps/sbom-<timestamp>.json",
  "supply_chain_flags": ["array of flagged packages with reason"]
}
```

### B10. Audit (L2)

```json
{
  "dimensions_checked": ["array — e.g. wcag-aa, gdpr, license-compliance, guard-log-review"],
  "wcag_level_achieved": "AA | AAA | PARTIAL | FAIL | not-applicable",
  "guard_logs_consumed": "boolean",
  "guard_log_violations_found": "integer",
  "total_violations": "integer",
  "violations_by_dimension": {
    "wcag": "integer",
    "gdpr": "integer",
    "license": "integer",
    "guard-log": "integer"
  },
  "compliance_report_path": ".wabblespec/audits/compliance-<timestamp>.md",
  "attestation_required": "boolean — true if violations require human sign-off"
}
```

### B11. Nexus (L5)

```json
{
  "query_type": "why-query | blast-radius | pattern-discovery | what-changed",
  "domain": "string — topic or module area queried",
  "drawers_queried": "integer",
  "relationships_found": "integer",
  "entities_traversed": "integer",
  "response_path": ".wabblespec/nexus/response-<timestamp>.json",
  "graph_freshness": "FRESH | AGING | STALE — state of graph at query time",
  "entity_graph_used": "boolean"
}
```

### B12. Shift (L1)

```json
{
  "change_class": "BREAKING | DEPRECATION | ADDITIVE | COSMETIC",
  "reverse_drift_detected": "boolean",
  "reverse_drift_details": "string — null if not detected",
  "downstream_consumers_affected": "integer",
  "affected_consumer_ids": ["array of module ids"],
  "compatibility_report_path": ".wabblespec/shift/compat-<timestamp>.md",
  "semantic_diff_path": ".wabblespec/shift/diff-<timestamp>.md",
  "loop_back_required": "boolean — true when BREAKING + downstream consumers exist"
}
```

### B13. Sync (L1)

```json
{
  "specs_reconciled": "integer — number of spec artifacts involved",
  "divergence_severity": "MINOR | MAJOR",
  "auto_merged": "boolean",
  "human_review_required": "boolean",
  "merge_strategy": "auto | manual | escalated",
  "conflicts_resolved": "integer",
  "conflicts_escalated": "integer",
  "sync_result_path": ".wabblespec/sync/result-<timestamp>.md"
}
```

### B14. Organize (L1)

```json
{
  "files_audited": "integer",
  "orphans_found": "integer",
  "naming_violations": "integer",
  "depth_violations": "integer",
  "duplicates_found": "integer",
  "actions_taken_auto": "integer — moves/renames done without human input",
  "actions_requiring_confirmation": ["array of paths — must be human-confirmed before acting"],
  "organize_report_path": ".wabblespec/organize/report-<timestamp>.md"
}
```

### B15. Flag (L1)

```json
{
  "mode": "create | rollout | audit | retire",
  "flag_id": "string",
  "previous_state": "DRAFT | ACTIVE | ROLLING | RETIRED | null",
  "new_state": "DRAFT | ACTIVE | ROLLING | RETIRED",
  "rollout_gate_passed": "boolean — null if mode != rollout",
  "flag_manifest_path": ".wabblespec/flags/manifest.json"
}
```

### B16. API (L1)

```json
{
  "mode": "version | deprecate | contract | audit",
  "api_version": "string",
  "versioning_scheme": "semver | date-based | header-based",
  "breaking_changes": "integer",
  "deprecations_added": "integer",
  "deprecations_sunset": "integer — deprecated items that reached sunset",
  "backward_compatible": "boolean",
  "contract_path": ".wabblespec/api/contract-<timestamp>.json"
}
```

### B17. Proofread (L6)

```json
{
  "content_type": "documentation | ui-copy | long-form | legal | marketing",
  "errors_found": "integer — total",
  "factual_errors": "integer — must be 0 for PASS",
  "readability_score": "number — Flesch-Kincaid Reading Ease; target by type",
  "terminology_inconsistencies": "integer",
  "unsupported_claims": "integer — claims without verifiable source",
  "gate_passed": "boolean"
}
```

### B18. Markdown (L6)

```json
{
  "format_type": "obsidian | agentskills | standard",
  "frontmatter_written": "boolean",
  "links_resolved": "integer — wikilinks or relative links confirmed valid",
  "callout_blocks_added": "integer",
  "output_path": "string"
}
```

### B19. Copy (L6)

```json
{
  "copy_type": "label | error-message | tooltip | security-warning | placeholder | cta",
  "character_count": "integer",
  "max_character_limit": "integer — from design system or platform constraint",
  "within_limit": "boolean",
  "security_warning_non_dismissable": "boolean — null if copy_type != security-warning",
  "recovery_path_present": "boolean — for error-messages: must state what user can do next"
}
```

### B20. Writer (L6)

```json
{
  "content_type": "landing-page | blog | technical-article | case-study | awareness",
  "word_count": "integer",
  "structure_framework": "AIDA | problem-solution | storytelling | inverted-pyramid",
  "target_audience": "string",
  "calls_to_action": "integer",
  "output_path": "string"
}
```

### B21. Legal (L6)

```json
{
  "document_type": "privacy-policy | terms-of-service | gdpr-dpa | disclaimer | cookie-policy",
  "jurisdiction": "GDPR | CCPA | PIPEDA | general | multi",
  "required_clauses_present": "boolean — must be true for PASS",
  "clauses_checked": "integer",
  "clauses_missing": ["array of missing clause names"],
  "template_used": "string — path to base template",
  "output_path": "string",
  "legal_review_recommended": "boolean — always true; this module produces a starting point, not legal advice"
}
```

### B22. Translate (L6)

```json
{
  "source_locale": "string — BCP 47",
  "target_locales": ["array of BCP 47 locale tags"],
  "strings_extracted": "integer",
  "strings_translated": "integer",
  "strings_missing_translation": "integer",
  "truncation_violations": "integer — must be 0 for PASS",
  "locale_manifest_path": "string"
}
```

### B23. Optimize (L6)

```json
{
  "modes_run": ["array — e.g. seo, ai-search, structured-data, performance, social, local, video, voice"],
  "core_web_vitals_addressed": "boolean",
  "structured_data_schemas_added": ["array of schema types added"],
  "metadata_updated": "boolean",
  "signal_hierarchy_followed": "boolean — Core Web Vitals > structured data > metadata > copy"
}
```

### B24. Market (L6)

```json
{
  "market_category_defined": "boolean",
  "icp_defined": "boolean",
  "differentiators_count": "integer",
  "channels_recommended": ["array of channel names"],
  "positioning_statement_written": "boolean",
  "strategy_doc_path": "string"
}
```

### B25. Changelog (L7)

```json
{
  "commits_processed": "integer — total commits in range",
  "commits_included": "integer — included in entry",
  "commits_excluded": "integer — excluded (chore, merge, etc.)",
  "version_covered": "string — semver or date range",
  "entry_type": "user-facing | developer | both",
  "entry_path": "string",
  "breaking_changes_highlighted": "boolean"
}
```

### B26. Commit (L7)

```json
{
  "commit_type": "feat | fix | chore | docs | refactor | test | perf | build | ci",
  "scope": "string — null if no scope",
  "subject_line": "string — 72-char max",
  "files_staged": "integer",
  "files_unstaged_left": "integer — unstaged after this commit",
  "commit_hash": "string — null until git confirms",
  "breaking_change_footer": "boolean — BREAKING CHANGE: footer present if needed",
  "conventional_commits_compliant": "boolean — must be true for PASS"
}
```

---

## Part C — Surgery diffs

### C1. Reviewer surgery (modules/l2/reviewer/SKILL.md)

**Step 2 — current text:**

```
### Step 2 — Adversary analysis

**Adversary receives:** The primary output only. No reasoning, no context from the module
that produced it, no explanation of why choices were made. This prevents anchoring —
Adversary must argue against the output on its own merits.

Adversary produces a structured counter-analysis:

## Weaknesses
<What could go wrong with this approach?>

## Missed alternatives
<What other approach was not considered?>

## Unstated assumptions
<What is being assumed without evidence?>

## Failure scenarios
<Under what conditions does this output fail?>

Adversary's job is the strongest honest case against the output — not destruction,
but rigorous challenge.

**Adversary role boundary:** [...]
```

**Step 2 — replacement text:**

```
### Step 2 — Adversary analysis

Invoke `modules/l2/adversary` with:
- `artifact_to_challenge`: the primary output
- `challenger_mode`: "spec-bound"
- `spec_artifact`: the spec artifact (task card or scope.md)

Adversary returns `adversary-receipt.json` containing a structured counter-analysis.
Record the receipt path in `adversary_receipt_path`.

Do not reproduce or interpret Adversary's logic here. Adversary is the authority on
its own analysis. If Adversary receipt is missing or status = FAIL, halt and surface
to human — do not proceed to Grader.
```

---

**Step 3 — current text:**

```
### Step 3 — Grader evaluation

**Grader receives:** Primary output + Adversary counter-analysis + spec artifact
(task card).

Grader evaluates against the spec, not personal preference. Produces:

- **Verdict:** ACCEPT | REVISE | ESCALATE
- **Score:** 0.0–1.0 quality assessment of primary output against spec
- **Revision guidance:** What specifically must change (required when verdict is REVISE)
- **Escalation reason:** Why human judgment is needed (required when ESCALATE)

**ACCEPT:** [...]
**REVISE:** [...]
**ESCALATE:** [...]
```

**Step 3 — replacement text:**

```
### Step 3 — Grader evaluation

Invoke `modules/l2/grader` with:
- `primary_output`: the primary output
- `adversary_counter_analysis`: from the Adversary receipt (counter_analysis field)
- `spec_artifact`: the spec artifact (task card or scope.md)

Grader returns `grader-receipt.json` containing verdict, score, and revision guidance.
Record the receipt path in `grader_receipt_path`. Extract `verdict` and `grader_score`
from the Grader receipt — these are the values Reviewer writes to its own receipt.

Do not reproduce or interpret Grader's scoring logic here. Grader is the authority on
its own verdict.
```

---

**Step 4 — REVISE loop (no text change, only the invocation references update):**

The REVISE loop already says "Send revision guidance to originating module / Originating module produces revised output / Adversary reviews revised output / Grader re-evaluates." These naturally now mean "invoke l2/adversary again" and "invoke l2/grader again." No text change needed beyond the Step 2/3 replacements.

---

**Step 5 — receipt (additive only):**

Add to the receipt extension fields (after `finding_summary`):

```json
"adversary_receipt_path": {
  "type": "string",
  "description": "Path to the adversary-receipt.json produced for this review cycle. Null if triggered = false."
},
"grader_receipt_path": {
  "type": "string",
  "description": "Path to the grader-receipt.json produced for this review cycle. Null if triggered = false."
}
```

---

**agents/adversary.md — replacement text:**

```
# Adversary (delegation stub)

Adversary analysis is now handled by the standalone module at `modules/l2/adversary/`.
This stub is retained for backwards-compatibility of any direct agent reference.

**Do not define analysis logic here.** Route all Adversary invocations to the
`modules/l2/adversary` module directly.
```

**agents/grader.md — replacement text (same pattern):**

```
# Grader (delegation stub)

Grader evaluation is now handled by the standalone module at `modules/l2/grader/`.
This stub is retained for backwards-compatibility of any direct agent reference.

**Do not define evaluation logic here.** Route all Grader invocations to the
`modules/l2/grader` module directly.
```

---

### C2. Recipe surgery (modules/l0/recipe/SKILL.md)

**New step inserted after Step 2b (between Step 2b and Step 3):**

```
### Step 2c — Assess input quality

After target detection, evaluate the quality of the opening user message independently
of the target. This runs every time Recipe runs detection (not when loading an
existing recipe.json — Step 1 exit bypasses this).

**Vague check (input_vague = true when ALL of these are absent):**
- A named artifact: file, module, component, service, endpoint, test, feature name
- A measurable outcome: a number, threshold, user-observable behavior that can be
  confirmed true or false
- A named constraint: must not, cannot, by date, under N tokens, backwards-compatible,
  no breaking change
- A specific scope boundary: only this file, just the login flow, excluding mobile

**Broad check (input_broad = true when BOTH are true):**
- Two or more interpretations of user intent are plausible at ≥ 0.5 confidence each
- No priority signal disambiguates them (user did not rank, quantify, or constrain
  to one interpretation)

Write results to recipe.json `input_quality` field (see output contract below).

**Routing after assessment:**
- input_vague AND NOT input_broad → invoke Enhance → then ScopeFrame
- input_broad AND NOT input_vague → invoke Sharpen → then ScopeFrame
- input_vague AND input_broad    → invoke Enhance → invoke Sharpen → then ScopeFrame
- neither                        → proceed to ScopeFrame directly

Recipe writes recipe.json before invoking Enhance or Sharpen. The target and complexity
are locked. Enhance and Sharpen operate on input clarity only — they do not change the
target or complexity score.
```

---

**recipe.json output contract — additions (additive, new fields only):**

```json
{
  "input_quality": {
    "vague": "boolean",
    "broad": "boolean",
    "enhanced": "boolean — true after Enhance ran",
    "sharpened": "boolean — true after Sharpen ran"
  }
}
```

---

**receipt extension — additions (additive):**

```json
{
  "input_quality": {
    "vague": "boolean",
    "broad": "boolean",
    "enhanced": "boolean",
    "sharpened": "boolean"
  }
}
```

---

**rules/target-detection.md — new section at end of file:**

```
---

## Input quality assessment

Run after target detection. Independent of target confidence.

### Vague detection

Input is vague when ALL of the following are absent from the opening user message:

1. Named artifact: a specific file, module, component, service name, endpoint path,
   test name, feature name, or class/function name
2. Measurable outcome: a number, threshold, percentage, timing constraint, or a
   user-observable behavior that produces a true/false result
3. Named constraint: "must not X", "cannot Y", "by date Z", "under N tokens",
   "backwards-compatible", "no breaking change", "zero downtime"
4. Scope boundary: "only this file", "just the login flow", "excluding mobile",
   "within module X", "not touching the database"

If all four are absent → input_vague = true.

### Broad detection

Input is broad when BOTH:
1. Two or more interpretations of user intent each score ≥ 0.5 confidence
2. No priority signal resolves the ambiguity (no ranking, no constraint, no "most
   important is...", no "start with...", no quantity that selects one interpretation)

If both conditions met → input_broad = true.

### Common vague inputs (examples)

- "Improve performance" → vague (no artifact, no measurement, no scope)
- "Fix the bug" → vague (no named artifact, no constraint, no scope)
- "Make it better" → vague (no artifact, no measurable outcome, no scope)
- "Add authentication" → borderline; check for constraints/scope before declaring vague

### Common broad inputs (examples)

- "Work on the frontend" → broad (React components? CSS? Performance? New feature?)
- "Improve the API" → broad (versioning? new endpoints? documentation? performance?)
- "Help with the database" → broad (schema? queries? migrations? backups?)
```

---

## Part D — Issues found during Phase 0 review

### D1. EntityGraph compatibility check (blocks Nexus build)

Before building Nexus (Phase 3), verify that `modules/l5/entity-graph/scripts/entity-graph.py` produces output that Nexus's graph-builder.py can consume. The output format needs to include entity IDs that map to Memory drawer IDs. If EntityGraph does not currently output drawer_id references, EntityGraph needs a minor update before Nexus can be built.

**Action:** Read entity-graph.py at Phase 3 start. If drawer_id references are absent, add them as part of the Nexus phase before building graph-builder.py.

### D2. Specify Step 3.6 references Reviewer — needs Phase 1 pre-requisite

`modules/l1/specify/SKILL.md` Step 3.6 currently says "invoke Reviewer" for the adversarial spec gate. After Phase 1 extracts Adversary as standalone, Step 3.6 must be updated to say "invoke `modules/l2/adversary`" directly. This is a one-line change.

**Action:** Add Step 3.6 update to the Phase 1 task list as a small surgical item alongside the main Reviewer surgery.

### D3. Economy module is currently a stub

`modules/l2/economy/SKILL.md` states it activates only after 50+ executions and currently defers to invariant I12. The `_shared/infrastructure/economy-principles.md` file (created in Phase 4) will be the primary economy reference. Economy's SKILL.md should reference it once created. No surgery before Phase 4, but note the dependency.

### D4. `_shared/schemas/` pattern for new graph schemas

Phase 3 creates `graph-node.schema.json` and `graph-edge.schema.json`. These go in `_shared/schemas/` alongside the existing schemas. Add them to framework.yaml `shared.schemas` with consumers: `[nexus, shift, entity-graph]`.

### D5. Autopilot surgery — DEFERRED

**Resolved 2026-05-23.** Autopilot surgery (adding Plan to orchestration envelope, Nexus awareness, Audit scheduling) is deferred until all 26 standalone modules are built and wired. The orchestration layer must not be modified until it has a complete, stable module inventory to route against. All Phase 2 and Phase 3 Autopilot surgical items are removed from the integration plan. A separate Autopilot surgery plan will be created post-integration.

### D6. EntityGraph compatibility — confirmed

**Resolved 2026-05-23.** `entity-graph.py` examined. Output node format: `{"id": "type::label", "type": "...", "label": "...", "drawer_count": N}`. No `drawer_id` references on nodes. Nexus's `graph-builder.py` needs drawer_id to back every entity against a Memory drawer (architecture decision A5). **Action at Phase 3:** Before building Nexus, add `drawer_id` field to EntityGraph node output. This is a minor additive change to entity-graph.py — not a breaking change to downstream consumers since the new field is additive.

### D7. v5.2 module modifications added to plan

**Resolved 2026-05-23.** Four existing modules gain new modes/hooks from v5.2 Amendment. These are now in the integration plan:

| Module | Change | Phase |
|---|---|---|
| Archive | `--sweep` mode + Nexus refresh hook (post-archive targeted graph update) | Phase 3 |
| Monitor | Guard log auto-routing → typed DEPENDENCY error event → Triage | Phase 3 |
| Feedback | `--metrics` mode (CSV/JSON ingest → Memory production-evidence + Product) | Phase 4 |
| Economy | `--budget` mode (token ceiling in AGENT.md → advisory before pipeline overage) | Phase 4 |

Instinct EMA formula confirmed from v5.3: `confidence_new = 0.9 × confidence_old + 0.1 × outcome_signal`. Outcome signal: +1.0 GOOD+, -1.0 NEEDS WORK, 0.0 no Grader data. Staleness decay: -0.05 per unreinforced session. Prune at ≤ 0.1. L8 already built — this is a verification note, not a build action.

---

## Part E — Phase 0 checklist

- [x] Architectural decisions documented and rationale locked
- [x] Layer placements confirmed for all 26 modules
- [x] Adversary + Grader extraction contract defined (invocation protocols, what moves, what stays)
- [x] Enhance/Sharpen trigger strategy locked (Recipe triggers, detection rules defined)
- [x] Plan placement locked (after Propose, before Decompose; mandatory for Medium+)
- [x] Nexus graph interoperability constraint documented
- [x] Shared infrastructure boundary rule locked
- [x] framework.yaml consumer declaration rule locked
- [x] Receipt schema extension pattern locked
- [x] Receipt extension fields defined for all 26 modules
- [x] Reviewer surgery diff written (Steps 2 and 3, agent stubs, receipt additions)
- [x] Recipe surgery diff written (Step 2c, recipe.json additions, target-detection.md addition)
- [x] Seven issues documented (D1–D7) with action items
- [x] Autopilot surgery deferred (D5) — removed from Phase 2/3 surgical lists
- [x] EntityGraph compatibility confirmed (D6) — drawer_id addition scoped to Phase 3
- [x] v5.2 module modifications added to plan (D7) — 4 modules, Phases 3–4
- [ ] User confirms this document before Phase 1 starts

**Phase 1 may begin after user confirmation of this document.**
