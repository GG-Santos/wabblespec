---
name: clean
description: Applies targeted surface-level cleanup to  code. Removes dead code, normalizes formatting, renames identifiers to match spec conventions, removes deprecated patterns flagged by Specify. Scope always declared explicitly — no unbounded clean. BREAKING changes halt and route to Executor.
---

# Clean

You apply surface-level cleanup to declared scope in product space. You do not determine your own scope — scope must be declared explicitly before you begin. You classify every change before applying it. BREAKING changes do not proceed.

## What this skill does

Applies targeted surface-level cleanup to  code. Removes dead code, normalizes formatting, renames identifiers to match spec conventions, removes deprecated patterns flagged by Specify. Scope always declared explicitly — no unbounded clean. BREAKING changes halt and route to Executor.

## When to use

- Specify flags deprecated patterns (auto-clean eligible items notified)
- Explicit `/clean <scope>` command with declared scope
- Verifier flags formatting violations in Review mode

Cannot activate without declared scope.

## Operation types

| Operation | Classification |
|---|---|
| Remove dead code (unreachable, unused exports) | COSMETIC — only if dead code confirmed by static analysis |
| Normalize formatting (whitespace, line endings, indent) | COSMETIC — only if format config exists |
| Rename to match spec conventions | ADDITIVE |
| Remove deprecated patterns | COSMETIC — only if Specify flagged as deprecated |
| Remove commented-out code blocks | COSMETIC — only if no active reference |

Clean does NOT:
- Extract functions or introduce abstractions (structural — requires Specify + Executor)
- Rename across package/module boundaries without Migrate
- Modify test assertions (Test module owns test stubs)
- Touch `.wabblespec/` for any reason

## Delta classification

Classify before applying any change:
- COSMETIC: no behavior change, no API surface change → proceed
- ADDITIVE: new canonical names, renames that extend interface → proceed with diff record
- BREAKING: any change that could break consumers → halt and route to Executor with Specify delta

Renames are always ADDITIVE minimum. Dead code removal is COSMETIC only if the symbol is provably unreferenced.

## Workflow

1. Receive scope declaration (files, directories, or pattern)
2. Validate scope: all targets within product space (I11 check)
3. Analyze targets:
   - Identify dead code (unreferenced symbols)
   - Identify formatting violations
   - Identify deprecated pattern usage (from Specify flagged list)
   - Identify spec convention mismatches (from EntityGraph canonical names)
4. For each identified item: classify COSMETIC|ADDITIVE|BREAKING
   - BREAKING: halt and report — do not apply
5. Apply COSMETIC and ADDITIVE changes
6. Write before/after diff to `.wabblespec/receipts/clean-diff-<timestamp>.md`
7. Write Clean receipt

## STM Pipeline integration (receipt artifacts)

Clean applies the STM pipeline to receipt artifacts and code comments when processing them. STM is NOT applied to production code logic — surface-level cleanup only.

Configuration: `modules/l1/clean/rules/stm-config.json`

**Default active transforms for Clean:**
- `receipt_mode` — strips first-person language from receipt artifacts; capitalizes status tokens (pass→PASS, fail→FAIL, warn→WARN)
- `direct_mode` — removes sycophantic preambles from generated code comments and doc strings

STM transforms are classified as COSMETIC — they do not change semantics, only surface presentation of receipt text and comments.

**STM receipt field appended to Clean receipt:**
```json
{
  "stm_applied": ["receipt_mode", "direct_mode"],
  "char_count_before": 840,
  "char_count_after": 812,
  "reduction_pct": 3.3
}
```

STM only runs when scope includes receipt artifacts or code comment targets. STM does not activate on production code logic regardless of scope declaration.

## Output contract

Writes a receipt to `.wabblespec/receipts/` on successful completion. Receipt includes `stm_applied` field when STM transforms were applied.

## What not to do

- Do not self-scope — never begin without a declared scope
- Do not apply BREAKING changes — halt and route them
- Do not touch `.wabblespec/` — product code only
- Do not modify test assertions
- Do not introduce abstractions or structural changes — surface-level only
- Do not rename across package/module boundaries without Migrate
