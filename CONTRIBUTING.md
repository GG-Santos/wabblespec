# Contributing to WabbleSpec

Detailed contributor guide: [`.wabblespec/engine/docs/core/contributing.md`](.wabblespec/engine/docs/core/contributing.md). This file is a quick-start summary of the rules that matter most.

## Ground rules (the 12 invariants)

All work must respect the invariants in [`.wabblespec/engine/shared/references/invariants.md`](.wabblespec/engine/shared/references/invariants.md). The ones contributors hit most often:

- **I1 — spec is the single source of truth.** No execution outside a locked spec.
- **I6 — runtime is vendor-neutral.** No model names anywhere in framework files; use capability descriptors (`code-generation`, `analysis`, `synthesis`, `long-context`).
- **I10 — receipts are operational artifacts.** Every non-trivial step writes a receipt; implied completion is prohibited.
- **I11 — framework and product never mix.** `.wabblespec/` is framework space; never write to it from product-space tasks.

## Adding or changing a module

1. Modules live under `.wabblespec/engine/modules/<layer>/<module>/` with a `SKILL.md` and `skill-rules.json`.
2. `SKILL.md` frontmatter needs `name` and `description`; include the standard sections (*What this skill does*, *When to use*, *Output contract*). Tool references use `~~capability` placeholders, not provider names.
3. Register the module in [`.wabblespec/wabblespec.yaml`](.wabblespec/wabblespec.yaml).
4. Prefer **reference routing** over inline duplication: route a topic to its reference doc instead of copying content.

## Before you commit

Run the framework's own gates — both must pass:

```bash
python .wabblespec/engine/shared/scripts/validate-graph.py        # registry integrity, 0 violations
python .wabblespec/engine/shared/scripts/quality-floor-check.py   # all modules pass both gates
```

## State vs. versioned files

`.wabblespec/state/` is **machine-local runtime state** (receipts, memory drawers, plans, session data) and is gitignored — do not expect it to be versioned. Everything under `.wabblespec/engine/` (modules, scripts, schemas, references, hooks) **is** versioned and is the framework itself.

## Receipts

Every non-trivial task produces a receipt chain: Research → Plan → Execution → Verifier → Archive. Use `.wabblespec/engine/shared/scripts/receipt-writer.py` (schema-enforced) rather than hand-authoring receipts.
