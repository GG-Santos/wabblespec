---
name: polish
description: Refinement pass on generated prose artifacts before delivery. Enforces Homowabian register consistency, removes redundancy, checks structural correctness, and flags spec violations. Does not change semantics. Runs on explicit command or when Verifier routes a failing quality dimension.
---

# Polish

You run refinement passes on prose artifacts. You do not change meaning — only surface quality. You cannot touch code files, schema files, receipts, or Memory drawers.

## What this skill does

Refinement pass on generated prose artifacts before delivery. Enforces Homowabian register consistency, removes redundancy, checks structural correctness, and flags spec violations. Does not change semantics. Runs on explicit command or when Verifier routes a failing quality dimension.

## When to use

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

Polish runs four core passes in sequence, plus two optional passes. A specific subset can be declared explicitly.

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

### Pass 5: Proofread (optional)

Delegates to the Proofread module. Checks readability, factual accuracy, and internal consistency. Findings are surfaced in the diff; verdict propagated to the Polish receipt. Does not block Delivery.

Activates when: caller declares `--proofread` flag, OR artifact content type is `technical-doc | marketing-copy | legal-doc | blog-post`.

### Pass 6: Markdown formatting (optional)

Delegates to the Markdown module. Enforces Obsidian/agentskills format: frontmatter, wikilinks, callout syntax. Auto-applied; non-destructive.

Activates when: caller declares `--markdown` flag, OR artifact target is an Obsidian vault path.

## Workflow

```
1. Receive artifact path, scope (full vs. declared subset), and flags (--proofread, --markdown)
2. Check: excluded type? -> IF yes: abort, SPEC_VIOLATION
3. Read active Homowabian register from .wabblespec/meta.md
4. Run declared passes in sequence (Passes 1–4 always; 5 if --proofread or content type match; 6 if --markdown or Obsidian path)
5. Write polished artifact (overwrite in place)
6. Write polish diff to .wabblespec/receipts/polish-diff-<timestamp>.md
7. Write Polish receipt to .wabblespec/receipts/polish-receipt-<timestamp>.json
```

## Pass 7: STM Pipeline (integrated)

The STM (Sequential Text Module) pipeline runs after Pass 4 (Spec compliance) and before Proofread (Pass 5). It applies pure-function text transforms in sequence. Each transform is independently togglable via `rules/stm-config.json`.

Configuration file: `modules/l6/polish/rules/stm-config.json`

**Default active transforms for Polish:**
- `hedge_reducer` — removes hedging phrases ("I think", "perhaps", "maybe", "I believe", "it seems", "might be", "could be", "arguably", "to some extent")
- `direct_mode` — removes sycophantic preambles ("Sure,", "Of course,", "Certainly,", "Absolutely,", "Great question", "I'd be happy to")

**Available but inactive by default:**
- `spec_mode` — normalizes modal verbs to EARS syntax (might→SHOULD, will→SHALL); enable with `--spec-mode`
- `receipt_mode` — strips first-person from receipts, capitalizes PASS/FAIL/WARN; owned by Clean for receipt artifacts
- `casual_mode` — replaces formal connectors (However→But, Utilize→Use, In order to→To); enable with `--casual`

### STM receipt field

Polish receipt includes:
```json
{
  "stm_applied": ["hedge_reducer", "direct_mode"],
  "char_count_before": 1420,
  "char_count_after": 1389,
  "reduction_pct": 2.2
}
```

### STM benchmark gate

Fixture set: 77 cases (26 hedge_reducer, 21 direct_mode, 30 spec_mode + receipt_mode).
Threshold: 100% precision and recall (deterministic regex modules).
30 negative cases required — cases that must NOT be transformed.
Run: `python .wabblespec/engine/shared/scripts/stm-pipeline.py --test --fixture-dir modules/l6/polish/fixtures`

## Outputs

| Output | Location | Notes |
|---|---|---|
| Polished artifact | Overwrites source in place | Semantics unchanged |
| Polish diff | `.wabblespec/receipts/polish-diff-<timestamp>.md` | Required — lists every change with pass type and reason |
| Polish receipt | `.wabblespec/receipts/polish-receipt-<timestamp>.json` | Required for I10 compliance |

Polish receipt includes `stm_applied`, `char_count_before`, `char_count_after`, `reduction_pct` when STM ran.

Polish diff is mandatory. Polish never overwrites silently.
