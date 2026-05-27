# Gateway Leaf Plan

**Date:** 2026-05-24
**Status:** COMPLETE — executed 2026-05-24, VERSION 0.3.3
**Scope:** gateway-aesthetic, gateway-design, gateway-experience promotion to `build_status: built`

---

## 1. Context

### 1.1 V5.3 reference material

No v5.3 plans exist in `.wabblespec/plans/`. The plans directory contains only:
- STANDALONE-INTEGRATION-PLAN.md (current integration plan)
- PHASE-0-DECISIONS.md (locked architectural decisions)
- README.md, task-card.md, current-wave-plan.md

No v5.3 leaf module definitions are available. The plan is derived entirely from what exists in the current codebase.

### 1.2 Established gateway pattern

The two built gateways establish the reference pattern:

| Gateway | Rules files | Leaf skill modules | Receipt schema |
|---|---|---|---|
| gateway-security | threat-model.md, vulnerability-patterns.md, controls.md, audit-gates.md | None | None |
| gateway-engineering | build-standards.md, code-quality.md, dependency-standards.md, quality-gates.md | None | None |

Both are **rules-only**: the gateway SKILL.md loads rules files directly. No separate child skill modules exist or are needed. No receipt schema extension files exist -- gateways emit receipts in the standard base format.

This is the model to follow for the three deferred gateways.

---

## 2. Existing state

### 2.1 gateway-aesthetic (modules/l4/aesthetic/)

| File | Present | Notes |
|---|---|---|
| SKILL.md | Yes | Complete — activation sequence, output contract, all rules files referenced |
| skill-rules.json | Yes | Complete — activators, invariants, `loads:` list, produces |
| brand.md | Yes | Brand assets, voice, prohibited treatments, audit gates |
| color.md | Yes | Semantic token system, WCAG contrast, dark mode scope |
| typography.md | Yes | Type scale, font loading, hierarchy |
| motion.md | Yes | Duration/easing tokens, reduced-motion requirement |
| design-tokens.md | Yes | Token policy, naming convention, no raw values rule |
| audit-gates.md | Yes | Consolidated gate checklist |

**Assessment:** All files present. No new content needed.

**framework.yaml gaps:**
- `build_status: deferred` → must become `built`
- `last_validated: ""` → must become `2026-05-24`
- `consumes_schemas: []` — no schemas consumed (correct, matches security/engineering pattern)
- `depends_on: []` — correct (aesthetic has no upstream gateway dependency)

### 2.2 gateway-design (modules/l4/design/)

| File | Present | Notes |
|---|---|---|
| SKILL.md | Yes | Complete — activation sequence (Confirm L3, load 5 rules files + audit-gates), output contract |
| skill-rules.json | Yes | Complete — activators, invariants, `loads:` list, `coordinates_with: [modules/l4/aesthetic/]` |
| ux-principles.md | Yes | Mental model declarations, feedback timing, error recovery paths |
| information-architecture.md | Yes | Navigation depth, labeling, search/filter thresholds |
| interaction-design.md | Yes | Touch targets, keyboard nav, focus management, gesture alternatives |
| design-system.md | Yes | Design system declaration, Storybook requirement |
| accessibility-floor.md | Yes | WCAG 2.1 AA enforcement |
| audit-gates.md | Yes | Consolidated gate checklist |

**Assessment:** All files present. No new content needed.

**framework.yaml gaps:**
- `build_status: deferred` → must become `built`
- `last_validated: ""` → must become `2026-05-24`
- `depends_on: []` — correct for build-time (aesthetic coordination is runtime-only per skill-rules.json `coordinates_with` field, not a prerequisite)

### 2.3 gateway-experience (modules/l4/experience/)

| File | Present | Notes |
|---|---|---|
| SKILL.md | Yes | Complete — activation sequence (Confirm Design gateway, Confirm user research in scope at P1, load 5 rules files + audit-gates), output contract |
| skill-rules.json | Yes | Complete — activators, invariants, `loads:` list, `supplements: [modules/l4/design/, modules/l4/aesthetic/]` |
| user-research.md | Yes | Research method selection, cadence |
| usability-testing.md | Yes | Test scenarios, metrics |
| accessibility-deep-dive.md | Yes | Screen reader matrix, color blindness, cognitive, motor |
| satisfaction-measurement.md | Yes | SUS, NPS, in-product feedback |
| research-ethics.md | Yes | Consent, anonymization, compensation |
| audit-gates.md | Yes | Consolidated gate checklist |

**Assessment:** All files present. No new content needed.

**framework.yaml gaps:**
- `build_status: deferred` → must become `built`
- `last_validated: ""` → must become `2026-05-24`
- `depends_on: []` → **must become `[gateway-design]`**. Skill-rules.json invariant states: "Gateway activates only after Design gateway has written its activation receipt." This is a runtime prerequisite that must be declared in framework.yaml. (security/engineering have no such dependencies because they operate independently; experience does not.)

---

## 3. Leaf module determination

**Finding: No leaf skill modules are required.**

The v5.3 leaf module definitions are unavailable, but the v6.1 content makes the answer clear: all three deferred gateways already follow the established rules-only pattern. Each gateway SKILL.md loads its domain rules files directly -- the rules files ARE the leaf content, not separate modules.

Creating separate skill modules for brand, color, typography, ux-principles, etc. would duplicate content that already exists as rules files and add routing overhead with no benefit. The security and engineering gateways demonstrate this pattern works correctly.

**Decision: rules-only, same as gateway-security and gateway-engineering.**

---

## 4. Gaps to fix before promotion

### Gap 1 — gateway-pattern.md consumer list (A7 violation)

`_shared/infrastructure/gateway-pattern.md` currently lists `consumers: [gateway-security, gateway-engineering]` in framework.yaml. But gateway-pattern.md already documents all 6 gateways (the routing table, verdict schema, and cross-gateway sequencing apply to aesthetic, design, and experience equally).

**Fix:** Update framework.yaml `_shared.infrastructure` consumer list for gateway-pattern.md to include `gateway-aesthetic`, `gateway-design`, `gateway-experience`.

### Gap 2 — gateway-experience framework.yaml `depends_on`

Experience's skill-rules.json invariant and SKILL.md activation sequence both require Design gateway to have activated first. The framework.yaml `depends_on: []` contradicts this.

**Fix:** Set `depends_on: [gateway-design]` on gateway-experience in framework.yaml.

### Gap 3 — No other gaps found

Receipt schemas: not needed (pattern set by security/engineering).
New rules files: not needed (all rules files present and complete).
SKILL.md updates: not needed (all three are complete).
skill-rules.json updates: not needed (all three are complete).

---

## 5. Build order

```
Step 1 — Fix Gap 1 (gateway-pattern.md consumers) — no new files, framework.yaml edit only
Step 2 — Promote gateway-aesthetic and gateway-design in parallel (no inter-dependency)
          - framework.yaml: build_status → built, last_validated → 2026-05-24
Step 3 — Promote gateway-experience (depends_on gap fixed, gateway-design already built)
          - framework.yaml: depends_on → [gateway-design], build_status → built, last_validated → 2026-05-24
Step 4 — VERSION bump (PATCH) and CHANGELOG entry
```

Total new files: 0.
Total files modified: 1 (framework.yaml, covering all 4 changes).
Total SKILL.md edits: 0.

---

## 6. Execution checklist (for executor to verify before marking done)

- [ ] framework.yaml gateway-pattern.md consumer list updated (adds gateway-aesthetic, gateway-design, gateway-experience)
- [ ] framework.yaml gateway-aesthetic: `build_status: built`, `last_validated: 2026-05-24`
- [ ] framework.yaml gateway-design: `build_status: built`, `last_validated: 2026-05-24`
- [ ] framework.yaml gateway-experience: `depends_on: [gateway-design]`, `build_status: built`, `last_validated: 2026-05-24`
- [ ] `build_status: deferred` count in framework.yaml = 0 after execution
- [ ] VERSION bumped (PATCH)
- [ ] CHANGELOG entry written

---

## 7. What this plan does NOT do

- Does not create any new skill modules
- Does not create any leaf modules under modules/l4/
- Does not modify any SKILL.md file
- Does not create receipt schema extensions (pattern not established at L4)
- Does not touch gateway-security or gateway-engineering (built, stable)
- Does not touch gateway-ai (already built, separate domain)
- Does not start Front 1 (real execution) — that requires separate user confirmation
