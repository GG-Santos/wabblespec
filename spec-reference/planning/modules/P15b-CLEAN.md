# Module Plan — Clean (L1)

**Tier:** 3 — SUPPORTING
**Layer:** L1 Spec Core
**v5.3 origin:** Clean module — targeted surface-level code cleanup

---

## Purpose

Apply targeted surface-level cleanup to project/repo/ code. Removes dead code, normalizes formatting, renames identifiers to match spec conventions, and removes deprecated patterns flagged by Specify. Scope always declared explicitly — Clean never determines its own scope. All changes are ADDITIVE or COSMETIC — BREAKING changes route to Executor halt. Full before/after diff written to receipt.

---

## Activation

`skill-rules.json` triggers:
- Specify flags deprecated patterns (auto-clean eligible items notified)
- Explicit `/clean <scope>` command with declared scope
- Verifier flags formatting violations in Review mode
- Cannot activate without declared scope (no unbounded clean)

---

## Operation Types

| Operation | Classification | Condition |
|---|---|---|
| Remove dead code (unreachable, unused exports) | COSMETIC | Dead code confirmed by static analysis |
| Normalize formatting (whitespace, line endings, indent) | COSMETIC | Format config exists (eslint, ruff, gofmt, etc.) |
| Rename to match spec conventions | ADDITIVE | Spec canonical name differs from code name |
| Remove deprecated patterns | COSMETIC | Specify flagged as deprecated |
| Remove commented-out code blocks | COSMETIC | No active reference to commented code |

Clean does NOT:
- Extract functions or introduce abstractions (structural — requires Specify + Executor)
- Rename across package/module boundaries without Migrate
- Modify test assertions (Test module owns test stubs)
- Touch .wabblespec/ (framework files — Clean is product-code only)

---

## Delta Classification

Before applying any change, Clean classifies the delta:

- COSMETIC: no behavior change, no API surface change → proceed
- ADDITIVE: new canonical names (renames that extend interface) → proceed with diff record
- BREAKING: any change that could break consumers → halt, route to Executor with Specify delta

Renames are always treated as at minimum ADDITIVE. Dead code removal is COSMETIC only if the symbol is provably unreferenced.

---

## Workflow

```
1. Receive scope declaration (files, directories, or pattern)

2. Validate scope: all targets within project/repo/ (I11 check)

3. Analyze targets:
   -> Identify dead code (unreferenced symbols)
   -> Identify formatting violations
   -> Identify deprecated pattern usage (from Specify flagged list)
   -> Identify spec convention mismatches (from EntityGraph canonical names)

4. For each identified item:
   -> Classify: COSMETIC|ADDITIVE|BREAKING
   -> BREAKING: halt and report — do not apply

5. Apply COSMETIC and ADDITIVE changes

6. Write before/after diff to .wabblespec/receipts/clean-diff-<timestamp>.md

7. Write Clean receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — scope required, no unbounded clean |
| `rules/scope-declaration.md` | Rules | Scope must be explicit — no implicit full-repo clean |
| `rules/delta-policy.md` | Rules | BREAKING changes halt and route to Executor |
| `rules/no-framework-files.md` | Rules | Clean cannot touch .wabblespec/ |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Specify | Specify flags deprecated patterns → Clean removes them |
| EntityGraph | Clean reads EntityGraph for canonical name lookup (rename alignment) |
| Verifier | Verifier Review mode routes formatting violations to Clean |
| Executor | BREAKING changes found by Clean halt and route to Executor for proper wave |
| Instinct | Instinct observes Clean patterns (recurring cleanup signals → Synth proposal) |

---

## Verification Mode

**Review** — diff written for all changes, no BREAKING changes applied, scope boundaries honored, no .wabblespec/ files touched, receipt written.

---

## Receipt Extension Fields

```json
{
  "scope": "string",
  "files_analyzed": "integer",
  "cosmetic_changes": "integer",
  "additive_changes": "integer",
  "breaking_halted": "integer",
  "diff_path": "string"
}
```
