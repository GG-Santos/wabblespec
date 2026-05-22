# Framework Mode

Use when building or maintaining a skill framework at scale: 50+ modules,
hundreds of files, or a system where no single context window can hold
the whole framework at once.

Load this alongside `references/production-mode.md`. Framework Mode inherits
all Production gates; it adds the index, isolation, and cascade layers
that make quality sustainable at scale.

## The core problem at scale

Suite Mode assumes the full suite fits in one working context. At 300
modules and 2000+ files it doesn't. The solution is three rules:

1. **Index, don't load.** A machine-readable manifest describes every
   module. Agents read the manifest to locate what they need, then load
   only those files. They never scan all 2000+ files.
2. **Isolate, don't contaminate.** Each module is worked on in isolation.
   Context for one module does not include the content of other modules —
   only the manifest entries for those modules.
3. **Cascade selectively.** When a shared artifact changes (a schema, a
   shared reference), the cascade is driven by the manifest's dependency
   graph — not by re-reading everything.

## Framework manifest (`framework.yaml`)

The manifest is the index. It is always small enough to fit in context.
Every module has one entry; every shared artifact has one entry.

```yaml
framework:
  name: my-framework
  version: 1.0.0
  description: >-
    One sentence. What this framework produces, for whom, and at what scale.

modules:
  - id: auth-skill
    path: modules/auth-skill/
    type: skill
    tags: [auth, security]
    consumes_schemas: [shared/schemas/user.json]
    produces_schemas: [shared/schemas/session.json]
    depends_on: []
    last_validated: "2026-05-20"
    quality_floor_passed: true

  - id: billing-skill
    path: modules/billing-skill/
    type: skill
    tags: [billing, payments]
    consumes_schemas: [shared/schemas/session.json, shared/schemas/invoice.json]
    produces_schemas: []
    depends_on: [auth-skill]
    last_validated: "2026-05-18"
    quality_floor_passed: true

shared:
  schemas:
    - path: shared/schemas/user.json
      consumers: [auth-skill]
      version: "1.2"
  references:
    - path: shared/references/security-policy.md
      consumers: [auth-skill, billing-skill]

quality_floor:
  min_pattern_score: 4.0        # per-module threshold (lower than suite 4.5 to allow scale)
  required_gates: [quick_validate, lint_prompts]
  adversarial_required_for_tags: [security, auth, payments, health, legal]

cascade_policy:
  schema_change_triggers_revalidation: true
  shared_reference_change_triggers_revalidation: false  # references are advisory
```

## Module anatomy

Each module is a self-contained Production-tier skill. It must pass
`quick_validate` and `lint_prompts` independently. At the module level,
the module author doesn't need to know the other 299 modules exist.

```
modules/{module-name}/
├── SKILL.md          # required
├── references/       # module-local references
├── scripts/          # module-local scripts
├── agents/           # module-local agents (rare; prefer shared/)
├── evals/            # module-local evals
└── examples/         # module-local examples
```

Shared artifacts live in `shared/`, not duplicated in each module.

## Navigator pattern

When a user request arrives, load the manifest first. Use
`agents/navigator.md` to locate the relevant module(s) from the manifest
without reading module files.

The navigator returns a **target list**: module IDs and specific files
within those modules to load. Load only what the target list names.

When the navigator returns more than 5 modules for one request, that is
a signal the request is cross-cutting. Escalate to cross-module work:
split into per-module subtasks or use a framework-validator sweep.

## Module isolation protocol

Work on one module at a time. Per-module context contains:

- The manifest entry for the target module (small)
- The manifest entries (not the content) of its `depends_on` modules
- The shared schema files it references
- The module's own files

Do not load other module files into the same context. A module that needs
to "know about" another module does so through schemas, not prose.

## Quality floor enforcement

The framework quality floor is `min_pattern_score: 4.0` per module,
lower than the single-skill threshold of 4.5. The tradeoff: 4.5 is
achievable for one skill with full iteration; enforcing it on 300 modules
simultaneously creates a maintenance burden that degrades over time. A
sustained 4.0 floor across all modules beats episodic 4.5 peaks.

**Per-module audit (lightweight):** Use `agents/module-auditor.md`
instead of the full grader. The module auditor runs a single-pass
quality check against the floor (3 patterns: examples, output contracts,
named failure modes) and returns pass/fail in < 1/3 the tokens of the
full grader.

**Full grader:** Run on a module when:
- The module was just created or substantially rewritten
- Its `quality_floor_passed` is false in the manifest
- The user explicitly requests a full quality report

**Framework-wide floor sweep:** Run `agents/framework-validator.md`
with `mode: quality_floor`. It reads the manifest, finds all modules
where `quality_floor_passed: false` or `last_validated` is older than
a threshold, and returns a prioritized fix list — without reading all
2000+ files.

## Cross-module validation

Run `agents/framework-validator.md` with `mode: cross_module` when:

- A shared schema changes
- New modules are added that declare `depends_on`
- Activation overlap is suspected across many modules

The validator reads only the manifest and the named shared artifacts.
It does not read all module files.

Cross-module checks:
- Schema version consistency (consumers reference the same version)
- Naming collisions in `produces_schemas` across modules
- Activation tag overlap that would cause ambiguous triggering
- `depends_on` cycles
- Modules that declare a schema consumer but the schema path doesn't exist

## Update cascade protocol

When a shared schema changes:

1. Bump the schema version in `shared/schemas/<name>.json`.
2. Update the schema version field in `framework.yaml`.
3. The manifest `consumers` list identifies which modules are affected.
4. For each affected module: load it in isolation, verify it still works
   with the new schema, update `last_validated`.
5. Set `quality_floor_passed: false` in the manifest for any module that
   fails after the schema change.
6. Do not update all 300 modules in one context. Batch in groups of 5-10.

When a shared reference changes:

Per `cascade_policy`, references do not auto-trigger revalidation (they
are advisory). Update the shared reference and note in the manifest's
`shared.references` entry which consumers may be affected. Sweep those
consumers on the next scheduled quality floor pass.

## Verification strategy at scale

Never re-verify all 300 modules on every change. Instead:

| Trigger | What to run |
|---|---|
| Single module edit | `quick_validate` + `lint_prompts` on that module |
| Module rewrite | Full grader on that module |
| Shared schema change | Cross-module validator + module auditor on affected consumers |
| Release prep | Framework-wide quality floor sweep (module-auditor on all modules) |
| New module added | Full Production gate set on the new module; cross-module validator to check overlap |

## Scaling evals

At 300 modules, running evals on all modules before every release is not
feasible. Use a tiered eval strategy:

- **Tier A (run every change):** Trigger evals for the changed module only.
- **Tier B (run weekly or on release prep):** Output-quality evals for all
  modules whose `last_validated` is older than 14 days.
- **Tier C (run on schema/shared-ref change):** Output-quality evals for
  all consumers of the changed artifact.

The manifest tracks `last_validated` per module. A freshness check is cheap
— read the manifest, compare dates, return the stale list.

## Framework handoff

When handing off a framework work session:

> Module(s) touched: [list]. Manifest updated: yes/no. Schema version bumped:
> yes/no. Quality floor passed for touched modules: yes/no. Modules with
> `quality_floor_passed: false` in manifest: [count]. Next action: [the
> specific gate or module to address].

Never say "the framework is complete" unless all modules have
`quality_floor_passed: true` and `last_validated` within the freshness
threshold.
