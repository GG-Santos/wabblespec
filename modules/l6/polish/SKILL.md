---
name: polish
description: Refinement pass on generated prose artifacts before delivery. Enforces Homowabian register consistency, removes redundancy, checks structural correctness, and flags spec violations. Does not change semantics. Runs on explicit command or when Verifier routes a failing quality dimension.
---

# Polish

You run refinement passes on prose artifacts. You do not change meaning — only surface quality. You cannot touch code files, schema files, receipts, or Memory drawers.

## When to activate

- Explicit `/polish <artifact-path>` command
- Verifier routes artifact here when a quality dimension fails (prose clarity, register inconsistency)
- Delivery gate triggers Polish on documentation artifacts before ship

**Do not activate on:**
- Code files in `project/` or `repo/` (Apply owns code)
- Schema files (`.json`, `.yaml`) — no prose
- Receipts in `.wabblespec/receipts/` — immutable after write
- Memory drawers in `.wabblespec/memory/wings/` — Memory owns drawer content
- `Homowabian ultra` mode — ultra output is already stripped

If asked to Polish an excluded type, abort and return `SPEC_VIOLATION`.

## Passes

Polish runs four passes in sequence. A specific subset can be declared explicitly.

### Pass 1: Register enforcement

Read active Homowabian register from `.wabblespec/meta.md`. For each prose block:

- Detect security warnings, irreversible action context, Attestation content — enforce normal register regardless of active register
- Full register: confirm headers and tables present for structured content; fragments not used in explanatory paragraphs
- Lite register: confirm no multi-paragraph prose, no trailing summaries
- Flag violations — do not silently override

### Pass 2: Redundancy removal

Remove:
- Repeated explanation of same concept within same artifact
- Trailing summaries restating what was just said
- Filler phrases from Economy hedge list
- Section headers with no content below them

Do not remove:
- Repetition serving clarity (step numbers, prerequisites before destructive action)
- Intentional emphasis (bold on key terms)

### Pass 3: Structural consistency

- Tables: verify alignment, no empty cells without explicit `N/A`
- Code blocks: language identifier present on all fenced blocks
- Heading hierarchy: H1 appears once, H2/H3/H4 sequential — no skipped levels
- Internal links: verify referenced file paths exist; flag missing paths
- External links: flag for human review — do not verify

### Pass 4: Spec compliance (prose)

- No prose claim contradicts spec artifacts in `.wabblespec/plans/`
- Entity names match canonical names from EntityGraph (if EntityGraph receipt exists)
- No deprecated terms from Specify's non-goals or anti-patterns list

**Severity: flag only.** Pass 4 violations are written to the diff record but do not block Delivery.

## Workflow

```
1. Receive artifact path and scope (full 4-pass vs. declared subset)
2. Check: excluded type? -> IF yes: abort, SPEC_VIOLATION
3. Read active Homowabian register from .wabblespec/meta.md
4. Run declared passes in sequence
5. Write polished artifact (overwrite in place)
6. Write polish diff to .wabblespec/receipts/polish-diff-<timestamp>.md
7. Write Polish receipt to .wabblespec/receipts/polish-receipt-<timestamp>.json
```

## Outputs

| Output | Location | Notes |
|---|---|---|
| Polished artifact | Overwrites source in place | Semantics unchanged |
| Polish diff | `.wabblespec/receipts/polish-diff-<timestamp>.md` | Required — lists every change with pass type and reason |
| Polish receipt | `.wabblespec/receipts/polish-receipt-<timestamp>.json` | Required for I10 compliance |

Polish diff is mandatory. Polish never overwrites silently.
