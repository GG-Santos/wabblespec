# Polish — Diff Policy

Polish diff is mandatory. Polish never overwrites an artifact without a diff record.

## Diff location

`.wabblespec/state/receipts/polish-diff-<timestamp>.md`

Timestamp format: `YYYYMMDDTHHMMSS`

## Diff format

```markdown
# Polish Diff — <artifact-path>
**timestamp:** ISO 8601
**passes_run:** [1, 2, 3, 4]
**register:** <active Homowabian register>

## Pass 1: Register enforcement
- [LINE or SECTION]: <what changed> — <reason>

## Pass 2: Redundancy removal
- [LINE or SECTION]: <what removed> — <reason>

## Pass 3: Structural consistency
- [LINE or SECTION]: <what fixed> — <reason>

## Pass 4: Spec compliance (flags only)
- [LINE or SECTION]: <violation description> — NOT CHANGED, human review required
```

If a pass produces zero changes, include the pass heading with `No changes.`

## No changes at all

If all four passes produce zero changes, write the diff with `No changes.` under each pass heading. Still write the receipt. Do not skip the diff.
