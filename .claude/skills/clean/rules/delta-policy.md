# Delta Policy — Clean

## Classify before applying

Every identified change is classified before any edit is made. No changes are applied without classification.

## Classification table

| Delta type | Definition | Action |
|---|---|---|
| COSMETIC | No behavior change, no API surface change | Apply — write to diff record |
| ADDITIVE | Extends interface (e.g. canonical rename that adds new symbol) | Apply — write to diff record |
| BREAKING | Could break consumers (removes symbols, changes signatures, renames exported identifiers) | Halt — do not apply |

## Renames

All renames are ADDITIVE minimum. A rename that removes an exported identifier without maintaining the old name under deprecation is BREAKING — halt and route to Executor with a Specify delta request.

Exception: renaming a purely internal (unexported, unreferenced outside module) identifier is COSMETIC if static analysis confirms no external reference exists.

## Dead code removal

Dead code removal is COSMETIC only if the symbol is provably unreferenced:
- No imports of the symbol found in declared scope
- No dynamic reference patterns that could resolve to the symbol
- No test assertions referencing the symbol

If any doubt exists about reachability, classify as BREAKING and halt.

## BREAKING halt behavior

When a BREAKING change is identified:
1. Do not apply the change
2. Record the change in the receipt as `breaking_halted`
3. Report to Executor with a Specify delta request
4. Continue processing remaining items in scope (a BREAKING halt does not stop the entire clean session)

## Diff record

Every applied change (COSMETIC or ADDITIVE) appears in the before/after diff written to `.wabblespec/state/receipts/clean-diff-<timestamp>.md`. The diff record is mandatory — Clean does not make silent changes.
