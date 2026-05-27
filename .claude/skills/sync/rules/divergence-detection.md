# Divergence Detection

Two spec artifacts diverge when they make contradictory or incompatible claims about the same subject. Sync detects and resolves this.

## What causes divergence

### Version split
Two versions of the same spec exist (e.g., `scope-v1.md` and `scope-v2.md`) and both are active — neither is retired. The most recent by timestamp is authoritative unless explicitly superseded.

### Conflicting field declarations
Two specs declare the same schema field with different types, different required status, or different enum values. Example: one says `status: PASS | FAIL`, another says `status: pass | fail | error`.

### Contradictory rules
Two rule files declare opposing behavior for the same condition. Example: one says "always check freshness before querying," another says "skip freshness check on blast-radius queries."

### Missing sync after surgery
A SKILL.md was surgically modified but a downstream rule or schema that referenced the old behavior was not updated. The referencing artifact still describes the old behavior.

## Severity levels

### MAJOR divergence
Two specs directly contradict each other on a required behavior or required field. Resolution requires a decision — cannot be auto-merged.

**Examples:**
- Field type conflict: string vs integer
- Required field in one spec, prohibited in another
- Contradictory step ordering in two specs that both claim authority

### MINOR divergence
Two specs describe the same behavior with different wording, different level of detail, or one spec has a superset of the other.

**Examples:**
- One spec mentions an optional step the other omits
- Naming inconsistency (module referred to by two valid names)
- One spec has an older but not contradictory version of a rule

## Detection method

For each pair of specs being reconciled:
1. Extract all field names, required fields, enum values, rule statements
2. Compare across specs for same-subject claims
3. Classify any conflict as MAJOR or MINOR
4. Record all conflicts with location (file path + section) in sync report
