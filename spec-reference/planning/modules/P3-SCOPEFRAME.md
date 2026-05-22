# Module Plan — ScopeFrame (L0)

**Tier:** 2 — CORE
**Layer:** L0 Intake
**v5.3 origin:** No direct equivalent — new in v6.1 (partially from Enhance/Sharpen boundary behavior)

---

## Purpose

Define session boundaries before spec work begins. Establishes what is in scope, what is explicitly out of scope, and what assumptions are declared. Feeds directly into Specify at P1. Prevents scope creep and spec bloat (I12).

---

## Activation

`skill-rules.json` triggers:
- After Recipe declares build target (Stage gate fires)
- Before Interview or Specify begin
- Explicit `/scope` command
- When Decompose detects scope expansion mid-execution (re-trigger)

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| `scope.md` | `.wabblespec/scope.md` | Active session scope declaration |
| ScopeFrame receipt | `.wabblespec/receipts/scopeframe-receipt.md` | I10 compliance |

### scope.md structure

```markdown
# Session Scope

**target:** <build target from Recipe>
**stage:** P1|P2|P3|P4
**locked_at:** <timestamp>

## In Scope

- <explicit inclusions>

## Out of Scope

- <explicit exclusions — non-goals>

## Declared Assumptions

- <assumptions that spec depends on>

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
```

---

## Workflow

```
1. Read recipe.json (target, spec_template)

2. Read any existing spec artifacts (Design Document if P2+)

3. Draft scope boundaries:
   -> In-scope: what this session must produce
   -> Out-of-scope: what is explicitly excluded
   -> Assumptions: what is taken as given without verification

4. Present scope for confirmation (Observation gate)
   -> User confirms or adjusts
   -> If adjusted: re-draft, re-confirm

5. Write scope.md

6. Write ScopeFrame receipt

7. Scope.md becomes input to Specify (P1) and Decompose (P2+)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over scope.md |
| `rules/scope-discipline.md` | Rules | What belongs in scope vs. non-goals; anti-bloat rules |
| `schemas/scope.schema.json` | Schema | scope.md structure validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | ScopeFrame reads recipe.json for target and template |
| Interview | ScopeFrame triggers Interview when scope is ambiguous |
| Specify | Reads scope.md as primary constraint input |
| Decompose | Reads scope.md to bound wave planning |
| Verifier | Checks output against scope.md — out-of-scope output is SPEC_VIOLATION |
| Ground | Reads scope.md to detect scope drift in generated output |

---

## Verification Mode

**Observation** — scope.md exists, has non-empty In Scope and Out of Scope sections, has been confirmed.

---

## Receipt Extension Fields

```json
{
  "in_scope_count": "integer",
  "out_of_scope_count": "integer",
  "assumptions_count": "integer",
  "user_confirmed": "boolean",
  "scope_changes": "integer"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Scope.md lifetime | Session-scoped only vs. persists with spec | Per-module planning |
| Scope change trigger | Manual only vs. auto-detect on Decompose expansion | Per-module planning |
